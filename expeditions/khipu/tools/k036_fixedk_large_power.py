#!/usr/bin/env python3
"""K036 - Fixed-K=10000 F1 scan (Primary A) and large-only BH power curve
m in {4,6,8} (Primary B). Pre-registered in case-file/K036-fixedk-large-power.md.
Scoring and pooled exchangeable min-p copied from K033/K035; Monte Carlo is
fixed K=10000 (no adaptive cut). D5w only (F1 family).
Usage: python3 tools/k036_fixedk_large_power.py khipu.db [--smoke]
"""
import sqlite3, sys, json, time
import numpy as np
from collections import defaultdict
from math import lgamma, log, exp, sqrt

t0 = time.time()
DB = sys.argv[1]
SMOKE = '--smoke' in sys.argv
K = 10000  # fixed; no adaptive cut
Q = 0.05
CHUNK = 1000
SEEDS = dict(scan=3630, null=3631, power=3632)
R_NULL = 5
MS = (4, 6, 8)  # large-only
WALL = 560
# Published F1 lists for overlap report (not used in decisions)
K033_F1 = {
    "KH0322/UR086", "KH0395/UR155", "KH0420/UR182", "KH0428/UR190",
    "KH0491/UR255", "KH0492/UR256", "KH0504/UR267B", "KH0506/UR269",
    "KH0507/UR270", "KH0513/UR274B", "KH0514/UR275",
}
K035_F1 = {
    "KH0322/UR086", "KH0395/UR155", "KH0428/UR190", "KH0478/UR242",
    "KH0491/UR255", "KH0492/UR256", "KH0504/UR267B", "KH0506/UR269",
    "KH0507/UR270", "KH0513/UR274B", "KH0514/UR275",
}

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
                      R_null=R_NULL, seeds=SEEDS, K=K, MS=MS)), flush=True)

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


def scores_w(V, gids):
    """D5w only (within-group), same formula as K033/K035 scores(..., within=True)."""
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64)
    P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64)
    NZ[:, 1:] = np.cumsum(V > 0, 1)
    idx = np.arange(n)
    big = V >= 10
    w = np.where(big, np.log10(np.maximum(V.astype(np.float64), 1)), 0.0)
    W = np.zeros((B, 11))
    vr, vl = valid_masks(gids)
    for k in range(2, 13):
        hk = np.zeros((B, n), bool)
        i = idx[idx + k < n]
        i = i[vr[k][i]]
        if len(i):
            hk[:, i] |= ((P[:, i + k + 1] - P[:, i + 1]) == V[:, i]) & (
                (NZ[:, i + k + 1] - NZ[:, i + 1]) >= 2)
        i = idx[idx - k >= 0]
        i = i[vl[k][i]]
        if len(i):
            hk[:, i] |= ((P[:, i] - P[:, i - k]) == V[:, i]) & (
                (NZ[:, i] - NZ[:, i - k]) >= 2)
        hk &= big
        W[:, k - 2] = (w * hk).sum(1)
    return W


def colrank_p(N, x):
    Ns = np.sort(N, 0)
    KK = N.shape[0]
    return np.stack([(KK - np.searchsorted(Ns[:, j], x[:, j] - 1e-9, 'left')) / KK
                     for j in range(N.shape[1])], 1)


def null_scores_w(rng, x, gids, KK):
    out = []
    left = KK
    while left > 0:
        m = min(CHUNK, left)
        V = np.array([rng.permutation(x) for _ in range(m)])
        out.append(scores_w(V, gids))
        left -= m
    return np.vstack(out)


def minp_pooled_detail(No, Nn):
    """Return (p, count, denom) under pooled exchangeable min-p (K033)."""
    A = np.vstack([No, Nn])
    live = A.max(0) > 0
    if not live.any():
        return 1.0, int(A.shape[0]), int(A.shape[0])
    A = A[:, live]
    pa = colrank_p(A, A).min(1)
    cnt = int((pa <= pa[0] + 1e-12).sum())
    denom = int(A.shape[0])
    return float(cnt / denom), cnt, denom


def fixed_p(rng, x, gids):
    Wow = scores_w(x[None], gids)
    n5w = null_scores_w(rng, x, gids, K)
    p, cnt, denom = minp_pooled_detail(Wow, n5w)
    se = sqrt(p * (1.0 - p) / denom) if 0 < p < 1 else 0.0
    return p, cnt, denom, se


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
    """Identical to K035 plant_within_m."""
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
        p, cnt, denom, se = fixed_p(rng, x, gids)
        rows.append(dict(khipu_id=khid, okr=names[khid][0], inv=names[khid][1], n_pend=len(v),
                         stratum=stratum[khid], p_D5w=p, cnt=cnt, denom=denom, se=se))
        if (j + 1) % 50 == 0:
            print(label, j + 1, round(time.time() - ts, 1), 's', flush=True)
    print(label, 'done', round(time.time() - ts, 1), 's', flush=True)
    return rows


def fam_hits(rows):
    f1 = [r for r in rows if r['khipu_id'] in pop_ids]
    s1 = bh([r['p_D5w'] for r in f1])
    return dict(F1=[f1[i]['okr'] + '/' + f1[i]['inv'] for i in np.nonzero(s1)[0]])


lab = lambda r: r['okr'] + '/' + r['inv']

# Stage 1: real scan (fixed K)
real = run_scan(SEEDS['scan'], (lambda rng, v: rng.permutation(v)) if SMOKE else (lambda rng, v: v), 'scan')
real_h = fam_hits(real)
print('real F1', len(real_h['F1']), real_h['F1'], flush=True)

# Checkpoint after scan
ckpt = dict(stage='scan_done', secs=round(time.time() - t0, 1), F1=real_h['F1'])
json.dump(ckpt, open('analysis/k036_checkpoint.json', 'w'), indent=1)

# Stage 2: 5 null corpora
null_reps = []
for r in range(R_NULL):
    if time.time() - t0 > WALL:
        print('null wall before corpus', r, flush=True)
        break
    rows = run_scan(SEEDS['null'] * 10 + r, lambda rng, v: rng.permutation(v), f'null{r}')
    h = fam_hits(rows)
    null_reps.append(dict(rows=rows, hits=h))
    print(f'null{r}', {k: len(v) for k, v in h.items()}, flush=True)

fpr = {}
for s in ('large', 'pop'):
    ps_ = [row['p_D5w'] for rep in null_reps for row in rep['rows']
           if (s == 'pop' and row['khipu_id'] in pop_ids) or row['stratum'] == s]
    x = int(sum(p <= 0.05 for p in ps_))
    n = len(ps_)
    bu = binom_upper(x, n) if n else float('nan')
    fpr[s] = dict(n=n, x=x, fpr=round(x / n, 4) if n else None,
                  binom_p_above=bu, gate_pass=bool(n and bu >= 0.05))
# also report other strata descriptively
for s in STRATA:
    if s == 'large':
        continue
    ps_ = [row['p_D5w'] for rep in null_reps for row in rep['rows'] if row['stratum'] == s]
    x = int(sum(p <= 0.05 for p in ps_))
    n = len(ps_)
    bu = binom_upper(x, n) if n else float('nan')
    fpr[s] = dict(n=n, x=x, fpr=round(x / n, 4) if n else None,
                  binom_p_above=bu, gate_pass=bool(n and bu >= 0.05))
bh_calib = {'F1': [len(rep['hits']['F1']) for rep in null_reps]}
bh_gate = {'F1': int(sum(h > 0 for h in bh_calib['F1'])) <= 1}
print('FPR', {s: fpr[s]['fpr'] for s in fpr}, '\nBH calib', bh_calib, '\ngate', bh_gate, flush=True)

gate_F1 = bool(bh_gate['F1'] and fpr['pop']['gate_pass'] and fpr['large']['gate_pass']
               and len(null_reps) == R_NULL)


def bh_insert(pmap, khid, p):
    keys = list(pmap)
    arr = np.array([p if k == khid else pmap[k] for k in keys])
    return bool(bh(arr)[keys.index(khid)])


real_F1 = {r['khipu_id']: r['p_D5w'] for r in real if r['khipu_id'] in pop_ids}

# Overlap vs K033 / K035
f1_set = set(real_h['F1'])
overlap = dict(
    n_F1=len(f1_set),
    shared_K033=sorted(f1_set & K033_F1),
    shared_K035=sorted(f1_set & K035_F1),
    only_K036=sorted(f1_set - K033_F1 - K035_F1),
    only_K033=sorted(K033_F1 - f1_set),
    only_K035=sorted(K035_F1 - f1_set),
    in_K033_not_K035=sorted((K033_F1 - K035_F1) & f1_set),  # recovered from K033 side of swap
    in_K035_not_K033=sorted((K035_F1 - K033_F1) & f1_set),
    candidates_new=sorted(f1_set - K033_F1 - K035_F1),  # flag only; no holdout this cycle
)

# Stage 3: large-only power by m
rng = np.random.default_rng(SEEDS['power'])
power_rows, j, capped = [], -1, False
ts = time.time()
large_data = [(i, d) for i, d in enumerate(data) if stratum[d[0]] == 'large']
for j, (idx, (khid, v, gids, n4, ng)) in enumerate(large_data):
    for m in MS:
        x, specs = plant_within_m(rng, v, gids, m)
        if x is None:
            continue
        p, cnt, denom, se = fixed_p(rng, x, gids)
        row = dict(khipu_id=khid, stratum='large', m=m, specs=specs, p_D5w=p,
                   cnt=cnt, denom=denom, se=se,
                   bh_F1=bh_insert(real_F1, khid, p))
        power_rows.append(row)
    if (j + 1) % 20 == 0:
        print('power', j + 1, '/', len(large_data), round(time.time() - t0, 1), flush=True)
    if time.time() - t0 > WALL:
        capped = True
        print('power checkpoint: wall cap at large khipu', j + 1, flush=True)
        break
power_reached = j + 1


def mean(rr, k):
    return round(float(np.mean([r[k] for r in rr])), 4) if rr else None


power = {'large': {}}
for m in MS:
    rr = [r for r in power_rows if r['m'] == m]
    power['large'][m] = dict(
        n=len(rr),
        p05=round(float(np.mean([r['p_D5w'] <= 0.05 for r in rr])), 4) if rr else None,
        bh_F1=mean(rr, 'bh_F1'))

ok = [m for m in MS if power['large'][m]['n'] >= 30 and (power['large'][m]['bh_F1'] or 0) >= 0.5]
mstar_large = min(ok) if ok else None
if not gate_F1:
    verdict = 'excluded'
elif mstar_large is not None:
    verdict = f'silence readable against >= {mstar_large} within-group sums in large'
else:
    verdict = 'not improved / not testable at m in {4,6,8} for large'

# Boundary detail for swapped names of interest
boundary = {}
for name in sorted(K033_F1 | K035_F1 | f1_set):
    for r in real:
        if lab(r) == name:
            boundary[name] = dict(p=r['p_D5w'], cnt=r['cnt'], denom=r['denom'], se=round(r['se'], 6),
                                  stratum=r['stratum'], in_F1=name in f1_set)
            break

res = dict(
    n_eligible=len(data), n_pop=len(pop), thirds=[float(t1), float(t2)],
    counts={s: sum(1 for v in stratum.values() if v == s) for s in STRATA},
    design=dict(K=K, adaptive=False, q=Q, seeds=SEEDS, R_null=R_NULL, MS=list(MS), wall=WALL,
                p_construction='pooled_exchangeable (K033)', scope='D5w_F1_only'),
    real=dict(hits=real_h, overlap=overlap, boundary=boundary),
    calibration=dict(fpr=fpr, bh_hits_per_null_corpus=bh_calib, bh_gate_pass=bh_gate,
                     n_null_corpora=len(null_reps),
                     null_hit_lists=[rep['hits'] for rep in null_reps]),
    power=power, power_khipus_reached=power_reached, power_capped=capped,
    decision=dict(gate_F1=gate_F1, m_star_large=mstar_large, verdict=verdict,
                  reference_list_adopted=bool(gate_F1)),
    rows=real, power_rows=power_rows, secs=round(time.time() - t0, 1))
out = 'analysis/k036_smoke.json' if SMOKE else 'analysis/k036_results.json'
json.dump(res, open(out, 'w'), indent=1, default=float)
print(json.dumps(dict(F1=real_h['F1'], overlap=overlap, power=power,
                      decision=res['decision'], secs=res['secs']), indent=1, default=float))
print('secs', res['secs'], flush=True)
