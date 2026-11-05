#!/usr/bin/env python3
"""K035 - BH-level power curve by plant count m (primary) and size-stratified BH
(secondary) for the F1 family (D5w on pop, pooled exchangeable min-p, q = 0.05).
Pre-registered in case-file/K035-bh-power-multiplant.md.
Scoring, null, pooled p and adaptive Monte Carlo copied unchanged from K033
(tools/k033_pooled_minp_rescan.py). Only the plant count and the BH partition vary.
Usage: python3 tools/k035_bh_power_multiplant.py khipu.db [--smoke]
"""
import sqlite3, sys, json, time
import numpy as np
from collections import defaultdict
from math import comb, lgamma, log, exp

t0 = time.time()
DB = sys.argv[1]
SMOKE = '--smoke' in sys.argv
K0, KTOT, ESC = 1000, 10000, 0.01
Q = 0.05
CHUNK = 1000
SEEDS = dict(scan=3530, null=3531, power=3532)
R_NULL = 5  # pre-registered: BH gate allows <= 1 of 5 per family
MS = (1, 2, 3, 4)
POPS = ('small', 'mid', 'large')
WALL = 560

c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute(
    "select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None:
        val[cid] += int(v)
kh = defaultdict(list)
for khid, cid, cl in c.execute(
        "select KHIPU_ID, CORD_ID, CLUSTER_ID from cord "
        "where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups:
        continue
    kh[khid].append((cl, val.get(cid, 0)))

data = []
for khid, cords in kh.items():
    v = np.array([x[1] for x in cords], np.int64)
    if (v > 0).sum() < 10:
        continue
    gids = np.empty(len(cords), np.int32)
    gi, last, sizes = -1, object(), []
    for i, (cl, _) in enumerate(cords):
        if cl != last:
            gi += 1
            last = cl
            sizes.append(0)
        gids[i] = gi
        sizes[-1] += 1
    data.append((khid, v, gids, sum(1 for s in sizes if s >= 4), len(sizes)))
if SMOKE:
    data = data[::11]

pop = [d for d in data if d[3] >= 2]
ps = np.array([len(d[1]) for d in pop])
t1, t2 = np.quantile(ps, [1 / 3, 2 / 3])
stratum = {}
for d in data:
    if d[3] < 2:
        stratum[d[0]] = 'S0'
    elif len(d[1]) <= t1:
        stratum[d[0]] = 'small'
    elif len(d[1]) <= t2:
        stratum[d[0]] = 'mid'
    else:
        stratum[d[0]] = 'large'
STRATA = ('S0', 'small', 'mid', 'large')
pop_ids = {d[0] for d in pop}
print(json.dumps(dict(n_eligible=len(data), n_pop=len(pop), thirds=[float(t1), float(t2)],
                      counts={s: sum(1 for v in stratum.values() if v == s) for s in STRATA},
                      R_null=R_NULL, seeds=SEEDS)), flush=True)

_valid_cache = {}


def valid_masks(gids):
    key = gids.tobytes()
    if key in _valid_cache:
        return _valid_cache[key]
    n = len(gids)
    vr, vl = [None] * 13, [None] * 13
    for k in range(2, 13):
        r = np.zeros(n, bool)
        l = np.zeros(n, bool)
        for i in range(n):
            if i + k < n:
                r[i] = bool(np.all(gids[i:i + k + 1] == gids[i]))
            if i - k >= 0:
                l[i] = bool(np.all(gids[i - k:i + 1] == gids[i]))
        vr[k], vl[k] = r, l
    _valid_cache[key] = (vr, vl)
    return vr, vl


def scores(V, gids=None, within=False):
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64)
    P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64)
    NZ[:, 1:] = np.cumsum(V > 0, 1)
    idx = np.arange(n)
    big = V >= 10
    w = np.where(big, np.log10(np.maximum(V.astype(np.float64), 1)), 0.0)
    W = np.zeros((B, 11))
    if within:
        vr, vl = valid_masks(gids)
    for k in range(2, 13):
        hk = np.zeros((B, n), bool)
        i = idx[idx + k < n]
        if within:
            i = i[vr[k][i]]
        if len(i):
            hk[:, i] |= ((P[:, i + k + 1] - P[:, i + 1]) == V[:, i]) & (
                (NZ[:, i + k + 1] - NZ[:, i + 1]) >= 2)
        i = idx[idx - k >= 0]
        if within:
            i = i[vl[k][i]]
        if len(i):
            hk[:, i] |= ((P[:, i] - P[:, i - k]) == V[:, i]) & (
                (NZ[:, i] - NZ[:, i - k]) >= 2)
        hk &= big
        W[:, k - 2] = (w * hk).sum(1)
    return W


def colrank_p(N, x):
    Ns = np.sort(N, 0)
    K = N.shape[0]
    return np.stack([(K - np.searchsorted(Ns[:, j], x[:, j] - 1e-9, 'left')) / K
                     for j in range(N.shape[1])], 1)


def null_scores(rng, x, gids, K):
    a, b = [], []
    left = K
    while left > 0:
        m = min(CHUNK, left)
        V = np.array([rng.permutation(x) for _ in range(m)])
        a.append(scores(V))
        b.append(scores(V, gids, True))
        left -= m
    return np.vstack(a), np.vstack(b)


def minp_asym(No, Nn):
    live = (Nn.max(0) > 0) | (No[0] > 0)
    if not live.any():
        return 1.0
    Nn2, No2 = Nn[:, live], No[:, live]
    pn = colrank_p(Nn2, Nn2).min(1)
    po = colrank_p(Nn2, No2).min(1)[0]
    return float((1 + (pn <= po + 1e-12).sum()) / (1 + len(Nn2)))


def minp_pooled(No, Nn):
    A = np.vstack([No, Nn])
    live = A.max(0) > 0
    if not live.any():
        return 1.0
    A = A[:, live]
    pa = colrank_p(A, A).min(1)
    return float((pa <= pa[0] + 1e-12).sum() / len(A))


def adaptive_p(rng, x, gids, also_asym=False):
    Wo, Wow = scores(x[None]), scores(x[None], gids, True)
    n5, n5w = null_scores(rng, x, gids, K0)
    p5, p5w = minp_pooled(Wo, n5), minp_pooled(Wow, n5w)
    esc = False
    if min(p5, p5w) <= ESC:
        e5, e5w = null_scores(rng, x, gids, KTOT - K0)
        n5, n5w = np.vstack([n5, e5]), np.vstack([n5w, e5w])
        p5, p5w = minp_pooled(Wo, n5), minp_pooled(Wow, n5w)
        esc = True
    if also_asym:
        return p5, p5w, esc, minp_asym(Wo, n5), minp_asym(Wow, n5w)
    return p5, p5w, esc


def bh(pvals, q=Q):
    p = np.asarray(pvals, float)
    m = len(p)
    if m == 0:
        return np.zeros(0, bool)
    o = np.argsort(p)
    thr = q * np.arange(1, m + 1) / m
    ok = p[o] <= thr
    sig = np.zeros(m, bool)
    if ok.any():
        r = np.max(np.nonzero(ok)[0])
        sig[o[:r + 1]] = True
    return sig


def binom_upper(x, n, a=0.05):
    if n == 0:
        return float('nan')
    return float(min(1.0, sum(exp(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1)
                                   + i * log(a) + (n - i) * log(1 - a))
                              for i in range(x, n + 1))))


def mcnemar(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    n10, n01 = int((a & ~b).sum()), int((~a & b).sum())
    nd = n10 + n01
    if nd == 0:
        return 1.0, n10, n01
    return min(1.0, 2 * sum(comb(nd, i) for i in range(min(n10, n01) + 1)) / 2 ** nd), n10, n01


def group_ranges(gids):
    n, out, i = len(gids), [], 0
    while i < n:
        j = i
        while j < n and gids[j] == gids[i]:
            j += 1
        out.append((i, j))
        i = j
    return out


def _fill(rng, pl, sl, st):
    blk = pl[sl].copy()
    if (blk > 0).sum() < 2:
        blk[:] = np.maximum(blk, rng.integers(1, 30, len(blk)))
    s = int(blk.sum())
    if s < 10:
        blk[0] += 10 - s
        s = int(blk.sum())
    pl[sl] = blk
    pl[st] = s



def plant_within_m(rng, v, gids, m):
    """K033 plant_within with the fixed 2 replaced by m; spec A_within/B_within drawn
    per plant with prob 1/2 (K033's pooled 'within' mixed both specs equally)."""
    pl = rng.permutation(v).copy()
    ranges = group_ranges(gids)
    specs = []
    for _ in range(m):
        spec = 'A_within' if rng.random() < 0.5 else 'B_within'
        specs.append(spec)
        if spec == 'A_within':
            ch = [(a, b, 3) for a, b in ranges if (b - a) >= 5]
        else:
            ch = [(a, b, k) for a, b in ranges for k in range(2, min(10, b - a - 1) + 1)
                  if b - a >= k + 2]
        if not ch:
            return None, specs
        a, b, k = ch[int(rng.integers(0, len(ch)))]
        right = True if spec == 'A_within' else (rng.random() < 0.5)
        if right:
            st = int(rng.integers(a, b - k))
            _fill(rng, pl, slice(st + 1, st + 1 + k), st)
        else:
            st = int(rng.integers(a + k, b))
            _fill(rng, pl, slice(st - k, st), st)
    return pl, specs


def run_scan(seed, make_x, label):
    rng = np.random.default_rng(seed)
    rows, ts = [], time.time()
    for j, (khid, v, gids, n4, ng) in enumerate(data):
        x = make_x(rng, v)
        p5, p5w, esc = adaptive_p(rng, x, gids)
        rows.append(dict(khipu_id=khid, okr=names[khid][0], inv=names[khid][1], n_pend=len(v),
                         stratum=stratum[khid], p_D5=p5, p_D5w=p5w, esc=esc))
    print(label, 'done', round(time.time() - ts, 1), 's', flush=True)
    return rows


def fam_hits(rows):
    """F1 pooled (D5w on pop), F1 stratified (BH within small/mid/large), S0 (D5w BH within S0)."""
    f1 = [r for r in rows if r['khipu_id'] in pop_ids]
    s1 = bh([r['p_D5w'] for r in f1])
    out = dict(F1=[f1[i]['okr'] + '/' + f1[i]['inv'] for i in np.nonzero(s1)[0]])
    for s in POPS + ('S0',):
        rr = [r for r in rows if r['stratum'] == s]
        ss = bh([r['p_D5w'] for r in rr])
        out['strat_' + s] = [rr[i]['okr'] + '/' + rr[i]['inv'] for i in np.nonzero(ss)[0]]
    out['F1_strat'] = sorted(sum((out['strat_' + s] for s in POPS), []))
    return out


lab = lambda r: r['okr'] + '/' + r['inv']

# Stage 1: real scan (fresh seed; re-derives F1 under K033's pipeline)
real = run_scan(SEEDS['scan'], (lambda rng, v: rng.permutation(v)) if SMOKE else (lambda rng, v: v), 'scan')
real_h = fam_hits(real)
print('real F1', len(real_h['F1']), 'F1_strat', len(real_h['F1_strat']),
      {s: len(real_h['strat_' + s]) for s in POPS + ('S0',)}, flush=True)

# Stage 2: 5 null corpora (structure-preserving: within-khipu permutation, groups kept)
null_reps = []
for r in range(R_NULL):
    rows = run_scan(SEEDS['null'] * 10 + r, lambda rng, v: rng.permutation(v), f'null{r}')
    h = fam_hits(rows)
    null_reps.append(dict(rows=rows, hits=h))
    print(f'null{r}', {k: len(v) for k, v in h.items()}, flush=True)

fpr = {}
for s in STRATA + ('pop',):
    ps_ = [row['p_D5w'] for rep in null_reps for row in rep['rows']
           if (s == 'pop' and row['khipu_id'] in pop_ids) or row['stratum'] == s]
    x = int(sum(p <= 0.05 for p in ps_))
    n = len(ps_)
    bu = binom_upper(x, n)
    fpr[s] = dict(n=n, x=x, fpr=round(x / n, 4), binom_p_above=bu, gate_pass=bool(bu >= 0.05))
fams = ('F1',) + tuple('strat_' + s for s in POPS + ('S0',))
bh_calib = {f: [len(rep['hits'][f]) for rep in null_reps] for f in fams + ('F1_strat',)}
bh_gate = {f: int(sum(h > 0 for h in v)) <= 1 for f, v in bh_calib.items()}
print('FPR', {s: fpr[s]['fpr'] for s in fpr}, '\nBH calib', bh_calib, '\ngate', bh_gate, flush=True)


def bh_insert(pmap, khid, p):
    keys = list(pmap)
    arr = np.array([p if k == khid else pmap[k] for k in keys])
    return bool(bh(arr)[keys.index(khid)])


real_F1 = {r['khipu_id']: r['p_D5w'] for r in real if r['khipu_id'] in pop_ids}
real_strat = {s: {r['khipu_id']: r['p_D5w'] for r in real if r['stratum'] == s} for s in STRATA}

# Stage 3: power by m (seed 3532), wall cap
rng = np.random.default_rng(SEEDS['power'])
power_rows, j, capped = [], -1, False
ts = time.time()
for j, (khid, v, gids, n4, ng) in enumerate(data):
    s = stratum[khid]
    for m in MS:
        x, specs = plant_within_m(rng, v, gids, m)
        if x is None:
            continue
        p5, p5w, esc = adaptive_p(rng, x, gids)
        row = dict(khipu_id=khid, stratum=s, m=m, specs=specs, p_D5w=p5w, p_D5=p5, esc=esc,
                   bh_strat=bh_insert(real_strat[s], khid, p5w))
        if khid in pop_ids:
            row['bh_F1'] = bh_insert(real_F1, khid, p5w)
        power_rows.append(row)
    if (j + 1) % 50 == 0:
        print('power', j + 1, round(time.time() - t0, 1), flush=True)
    if time.time() - t0 > WALL:
        capped = True
        print('power checkpoint: wall cap at khipu', j + 1, flush=True)
        break
power_reached = j + 1


def mean(rr, k):
    return round(float(np.mean([r[k] for r in rr])), 4) if rr else None


power = {}
for s in STRATA + ('pop',):
    power[s] = {}
    for m in MS:
        rr = [r for r in power_rows if r['m'] == m and
              ((s == 'pop' and r['khipu_id'] in pop_ids) or r['stratum'] == s)]
        d = dict(n=len(rr), p05=round(float(np.mean([r['p_D5w'] <= 0.05 for r in rr])), 4) if rr else None)
        if s != 'S0':
            d['bh_F1'] = mean(rr, 'bh_F1')
        if s != 'pop':
            d['bh_strat'] = mean(rr, 'bh_strat')
        power[s][m] = d

# Decision (pre-registered)
gate_F1 = bh_gate['F1'] and all(fpr[s]['gate_pass'] for s in POPS + ('pop',))
mstar = {}
for s in POPS:
    ok = [m for m in MS if power[s][m]['n'] >= 30 and (power[s][m]['bh_F1'] or 0) >= 0.5]
    mstar[s] = min(ok) if ok else None
silence = {s: dict(m_star_F1=mstar[s],
                   readable=(f'readable against >= {mstar[s]} within-group sums' if (gate_F1 and mstar[s])
                             else 'not testable at m <= 4'),
                   power_m2_F1=power[s][2]['bh_F1'], power_m4_F1=power[s][4]['bh_F1'])
           for s in POPS}
if not gate_F1:
    verdict = 'excluded'
elif any(mstar[s] == 1 or mstar[s] == 2 for s in POPS):
    verdict = 'power raised: silence testable at K033 strength (m<=2) in some stratum'
elif any(mstar.values()):
    verdict = 'silence testable only against stronger effects (m*>2)'
else:
    verdict = 'not improved'
strat_gate = all(bh_gate['strat_' + s] for s in POPS)
diffs = {s: round((power[s][2]['bh_strat'] or 0) - (power[s][2]['bh_F1'] or 0), 4) for s in POPS}
adopt_strat = bool(strat_gate and min(diffs.values()) >= -0.03 and sum(d >= 0.05 for d in diffs.values()) >= 1)
mstar_strat = {s: (min([m for m in MS if (power[s][m]['bh_strat'] or 0) >= 0.5 and power[s][m]['n'] >= 30],
                       default=None)) for s in POPS}

res = dict(
    n_eligible=len(data), n_pop=len(pop), thirds=[float(t1), float(t2)],
    counts={s: sum(1 for v in stratum.values() if v == s) for s in STRATA},
    design=dict(K0=K0, KTOT=KTOT, ESC=ESC, q=Q, seeds=SEEDS, R_null=R_NULL, MS=MS, wall=WALL,
                p_construction='pooled_exchangeable (K033)'),
    real=dict(hits=real_h, n_escalated=int(sum(r['esc'] for r in real))),
    calibration=dict(fpr=fpr, bh_hits_per_null_corpus=bh_calib, bh_gate_pass=bh_gate,
                     null_hit_lists=[rep['hits'] for rep in null_reps]),
    power=power, power_khipus_reached=power_reached, power_capped=capped,
    decision=dict(gate_F1=gate_F1, m_star_F1=mstar, silence=silence, verdict=verdict,
                  strat_gate=strat_gate, strat_minus_F1_at_m2=diffs, adopt_stratified=adopt_strat,
                  m_star_strat=mstar_strat),
    rows=real, power_rows=power_rows, secs=round(time.time() - t0, 1))
out = 'analysis/k035_smoke.json' if SMOKE else 'analysis/k035_results.json'
json.dump(res, open(out, 'w'), indent=1, default=float)
print(json.dumps(dict(power=power, decision=res['decision']), indent=1, default=float))
print('secs', res['secs'], flush=True)
