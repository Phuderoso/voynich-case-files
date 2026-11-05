#!/usr/bin/env python3
"""K033 - pooled exchangeable min-p rescan of the D5/D5w corpus with BH-FDR,
5 null corpora for the BH gate, and K003 list re-derivation.
Pre-registered in case-file/K033-pooled-minp-rescan.md.
Scoring identical to K032; only the p-value construction changes (pooled).
Usage: python3 tools/k033_pooled_minp_rescan.py khipu.db [--smoke]
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
SEEDS = dict(scan=3330, null=3331, power=3332)
R_NULL = 5  # pre-registered: ≥ 5; BH gate allows ≤ 1 of 5

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


def plant_within(rng, v, gids, spec):
    pl = rng.permutation(v).copy()
    ranges = group_ranges(gids)
    for _ in range(2):
        if spec == 'A_within':
            ch = [(a, b, 3) for a, b in ranges if (b - a) >= 5]
        else:
            ch = [(a, b, k) for a, b in ranges for k in range(2, min(10, b - a - 1) + 1)
                  if b - a >= k + 2]
        if not ch:
            return None
        a, b, k = ch[int(rng.integers(0, len(ch)))]
        right = True if spec == 'A_within' else (rng.random() < 0.5)
        if right:
            st = int(rng.integers(a, b - k))
            _fill(rng, pl, slice(st + 1, st + 1 + k), st)
        else:
            st = int(rng.integers(a + k, b))
            _fill(rng, pl, slice(st - k, st), st)
    return pl


def plant_unrestricted(rng, v, spec):
    pl = rng.permutation(v).copy()
    n = len(pl)
    if n < 20:
        return None
    for _ in range(2):
        k = 3 if spec == 'A' else int(rng.integers(2, 11))
        if n < k + 2:
            return None
        right = spec == 'A' or rng.random() < 0.5
        st = int(rng.integers(0, n - k)) if right else int(rng.integers(k, n))
        sl = slice(st + 1, st + 1 + k) if right else slice(st - k, st)
        _fill(rng, pl, sl, st)
    return pl


def run_scan(seed, make_x, label, also_asym=False):
    rng = np.random.default_rng(seed)
    rows, ts = [], time.time()
    for j, (khid, v, gids, n4, ng) in enumerate(data):
        x = make_x(rng, v)
        if also_asym:
            p5, p5w, esc, a5, a5w = adaptive_p(rng, x, gids, also_asym=True)
            rows.append(dict(khipu_id=khid, okr=names[khid][0], inv=names[khid][1], n_pend=len(v),
                             n_groups=ng, n_ge4=n4, stratum=stratum[khid],
                             p_D5=p5, p_D5w=p5w, p_D5_asym=a5, p_D5w_asym=a5w, esc=esc))
        else:
            p5, p5w, esc = adaptive_p(rng, x, gids)
            rows.append(dict(khipu_id=khid, okr=names[khid][0], inv=names[khid][1], n_pend=len(v),
                             n_groups=ng, n_ge4=n4, stratum=stratum[khid],
                             p_D5=p5, p_D5w=p5w, esc=esc))
        if (j + 1) % 100 == 0:
            print(label, j + 1, round(time.time() - t0, 1), flush=True)
    print(label, 'done', round(time.time() - ts, 1), 's', flush=True)
    return rows


def families(rows, key_D5='p_D5', key_D5w='p_D5w'):
    f1 = [r for r in rows if r['khipu_id'] in pop_ids]
    s1 = bh([r[key_D5w] for r in f1])
    s2 = bh([r[key_D5] for r in rows])
    s3 = bh([r[key_D5w] for r in rows])
    return f1, s1, s2, s3


# Stage 1: real scan
real = run_scan(SEEDS['scan'],
                (lambda rng, v: rng.permutation(v)) if SMOKE else (lambda rng, v: v),
                'scan', also_asym=True)
f1, s1, s2, s3 = families(real)
hits_F1 = [f1[i]['okr'] + '/' + f1[i]['inv'] for i in np.nonzero(s1)[0]]
hits_F2 = [real[i]['okr'] + '/' + real[i]['inv'] for i in np.nonzero(s2)[0]]
hits_F3 = [real[i]['okr'] + '/' + real[i]['inv'] for i in np.nonzero(s3)[0]]
_, sa1, sa2, _ = families(real, 'p_D5_asym', 'p_D5w_asym')
hits_F1_asym = [f1[i]['okr'] + '/' + f1[i]['inv'] for i in np.nonzero(sa1)[0]]
hits_F2_asym = [real[i]['okr'] + '/' + real[i]['inv'] for i in np.nonzero(sa2)[0]]
print('F1', len(hits_F1), 'F2', len(hits_F2), 'F3', len(hits_F3),
      '| asym F1', len(hits_F1_asym), 'F2', len(hits_F2_asym), flush=True)
if not SMOKE:
    json.dump(dict(stage='scan', hits_F1=hits_F1, hits_F2=hits_F2, rows=real),
              open('analysis/k033_checkpoint_scan.json', 'w'), default=float)

# Stage 2: 5 null corpora
null_reps = []
for r in range(R_NULL):
    rows = run_scan(SEEDS['null'] * 10 + r, lambda rng, v: rng.permutation(v), f'null{r}')
    g1, n1, n2, n3 = families(rows)
    null_reps.append(dict(rows=rows, F1_hits=int(n1.sum()), F2_hits=int(n2.sum()), F3_hits=int(n3.sum()),
                          F1_list=[g1[i]['okr'] + '/' + g1[i]['inv'] for i in np.nonzero(n1)[0]],
                          F2_list=[rows[i]['okr'] + '/' + rows[i]['inv'] for i in np.nonzero(n2)[0]]))
    print(f'null{r} BH F1={int(n1.sum())} F2={int(n2.sum())} F3={int(n3.sum())}', flush=True)
    if not SMOKE:
        slim = [{k: rep[k] for k in ('F1_hits', 'F2_hits', 'F3_hits', 'F1_list', 'F2_list')}
                for rep in null_reps]
        json.dump(dict(stage=f'null{r}', so_far=slim),
                  open('analysis/k033_checkpoint_nulls.json', 'w'), default=float)

fpr = {}
for det in ('D5', 'D5w'):
    fpr[det] = {}
    for s in STRATA + ('pop', 'all'):
        ps_ = [row[f'p_{det}'] for rep in null_reps for row in rep['rows']
               if s == 'all' or (s == 'pop' and row['khipu_id'] in pop_ids) or row['stratum'] == s]
        x = int(sum(p <= 0.05 for p in ps_))
        n = len(ps_)
        bu = binom_upper(x, n) if n else float('nan')
        fpr[det][s] = dict(n=n, x=x, fpr=round(x / n, 4) if n else None, binom_p_above=bu,
                           gate_pass=bool(n and bu >= 0.05))
bh_calib = dict(F1=[rep['F1_hits'] for rep in null_reps],
                F2=[rep['F2_hits'] for rep in null_reps],
                F3=[rep['F3_hits'] for rep in null_reps])
# BH gate: ≤ 1 of 5 null corpora with any discovery
bh_gate = {f: int(sum(h > 0 for h in v)) <= 1 for f, v in bh_calib.items()}
print('FPR', json.dumps({d: {s: fpr[d][s]['fpr'] for s in fpr[d]} for d in fpr}),
      '\nBH calib', bh_calib, 'gate', bh_gate, flush=True)

# Stage 3: power
rng = np.random.default_rng(SEEDS['power'])
real_p_F1 = {r['khipu_id']: r['p_D5w'] for r in f1}
real_p_D5_all = {r['khipu_id']: r['p_D5'] for r in real}
real_p_D5w_all = {r['khipu_id']: r['p_D5w'] for r in real}
real_p_D5_pop = {r['khipu_id']: r['p_D5'] for r in f1}


def bh_insert(pmap, khid, p):
    keys = list(pmap)
    arr = np.array([p if k == khid else pmap[k] for k in keys])
    sig = bh(arr)
    return bool(sig[keys.index(khid)])


power_rows = []
ts = time.time()
j = -1
for j, (khid, v, gids, n4, ng) in enumerate(data):
    for lab in ('A_within', 'B_within', 'A', 'B'):
        x = plant_within(rng, v, gids, lab) if lab.endswith('within') else plant_unrestricted(rng, v, lab)
        if x is None:
            continue
        p5, p5w, esc = adaptive_p(rng, x, gids)
        row = dict(khipu_id=khid, stratum=stratum[khid], plant=lab, p_D5=p5, p_D5w=p5w, esc=esc,
                   bh_D5_all=bh_insert(real_p_D5_all, khid, p5),
                   bh_D5w_all=bh_insert(real_p_D5w_all, khid, p5w))
        if khid in pop_ids:
            row['bh_D5w_pop'] = bh_insert(real_p_F1, khid, p5w)
            row['bh_D5_pop'] = bh_insert(real_p_D5_pop, khid, p5)
        power_rows.append(row)
    if (j + 1) % 50 == 0:
        print('power', j + 1, round(time.time() - t0, 1), flush=True)
    if time.time() - t0 > 560:
        print('power checkpoint: wall cap at khipu', j + 1, flush=True)
        break
power_reached = j + 1
print('power done', round(time.time() - ts, 1), flush=True)


def prate(rows, key):
    return round(float(np.mean([r[key] for r in rows])), 4) if rows else None


power = {}
for s in STRATA + ('pop',):
    power[s] = {}
    for lab in ('A_within', 'B_within', 'A', 'B', 'within'):
        rr = [r for r in power_rows
              if (r['plant'] == lab or (lab == 'within' and r['plant'].endswith('within')))
              and ((s == 'pop' and r['khipu_id'] in pop_ids) or r['stratum'] == s)]
        d = dict(n=len(rr))
        for det in ('D5', 'D5w'):
            d[f'{det}_p05'] = round(float(np.mean([r[f'p_{det}'] <= 0.05 for r in rr])), 4) if rr else None
            d[f'{det}_bh_all'] = prate(rr, f'bh_{det}_all')
            if s != 'S0':
                d[f'{det}_bh_pop'] = prate(rr, f'bh_{det}_pop')
        power[s][lab] = d

rule = {}
for s in STRATA:
    rr = [r for r in power_rows if r['stratum'] == s and r['plant'].endswith('within')]
    a = [r['p_D5w'] <= 0.05 for r in rr]
    b = [r['p_D5'] <= 0.05 for r in rr]
    mc, n10, n01 = mcnemar(a, b)
    gain = float(np.mean(a) - np.mean(b)) if rr else float('nan')
    testable = len(rr) >= 30
    pref = bool(testable and fpr['D5w'][s]['gate_pass'] and gain >= 0.03 and mc < 0.05)
    ru = [r for r in power_rows if r['stratum'] == s and r['plant'] in ('A', 'B')]
    cost = (float(np.mean([r['p_D5'] <= 0.05 for r in ru]) - np.mean([r['p_D5w'] <= 0.05 for r in ru]))
            if ru else float('nan'))
    rule[s] = dict(n_within_plants=len(rr), testable=testable, fpr_gate_D5w=fpr['D5w'][s]['gate_pass'],
                   gain_within=round(gain, 4), d5w_only=n10, d5_only=n01, mcnemar_p=mc,
                   prefer='D5w' if pref else ('not testable' if not testable else 'D5'),
                   unrestricted_cost_D5_minus_D5w=round(cost, 4))

silence = {s: dict(bh_power_within=power[s]['within'].get('D5w_bh_pop' if s != 'S0' else 'D5w_bh_all'),
                   readable=bool((power[s]['within'].get('D5w_bh_pop' if s != 'S0' else 'D5w_bh_all') or 0) >= 0.5))
           for s in STRATA}

k003 = json.load(open('analysis/k003_corpus.json'))
k003_hits = {f"{r['okr']}/{r['inv']}" for r in k003['rows'] if r['bh_sig']}
f2_set, f1_set = set(hits_F2), set(hits_F1)
k003_rederived = sorted(f2_set & k003_hits)
k003_lost = sorted(k003_hits - f2_set)
f2_new = sorted(f2_set - k003_hits)

# Strip bulky null rows from final JSON (keep hit lists + FPR already computed)
null_slim = [{k: rep[k] for k in ('F1_hits', 'F2_hits', 'F3_hits', 'F1_list', 'F2_list')}
             for rep in null_reps]

res = dict(
    n_eligible=len(data), n_pop=len(pop), thirds=[float(t1), float(t2)],
    counts={s: sum(1 for v in stratum.values() if v == s) for s in STRATA},
    design=dict(K0=K0, KTOT=KTOT, ESC=ESC, q=Q, seeds=SEEDS, R_null=R_NULL,
                p_construction='pooled_exchangeable', asym_recorded_on_real_scan=True),
    scan=dict(F1_D5w_pop=hits_F1, F2_D5_all=hits_F2, F3_D5w_all=hits_F3,
              F1_asym_descriptive=hits_F1_asym, F2_asym_descriptive=hits_F2_asym,
              F1_by_stratum={s: sum(1 for h in hits_F1
                                    if next(r['stratum'] for r in real
                                            if r['okr'] + '/' + r['inv'] == h) == s)
                             for s in STRATA},
              F1_new_vs_K003=sorted(f1_set - k003_hits),
              K003_lost_in_F1=sorted((k003_hits & {r['okr'] + '/' + r['inv'] for r in f1}) - f1_set),
              F2_vs_K003_overlap=len(f2_set & k003_hits), K003_n=len(k003_hits),
              K003_rederived=k003_rederived, K003_lost_under_pooled=k003_lost,
              F2_new_vs_K003=f2_new,
              n_escalated=int(sum(r['esc'] for r in real))),
    calibration=dict(fpr=fpr, bh_hits_per_null_corpus=bh_calib, bh_gate_pass=bh_gate,
                     null_slim=null_slim),
    power=power, rule=rule, silence=silence,
    power_khipus_reached=power_reached,
    rows=real, power_rows=power_rows,
    secs=round(time.time() - t0, 1),
)
out = 'analysis/k033_smoke.json' if SMOKE else 'analysis/k033_results.json'
json.dump(res, open(out, 'w'), indent=1, default=float)
summary = {k: res[k] for k in ('scan', 'calibration', 'rule', 'silence')}
# drop bulky bits from printed summary
summary['calibration'] = dict(fpr={d: {s: {kk: fpr[d][s][kk] for kk in ('n', 'x', 'fpr', 'gate_pass')}
                                       for s in fpr[d]} for d in fpr},
                              bh_hits_per_null_corpus=bh_calib, bh_gate_pass=bh_gate)
print(json.dumps(summary, indent=1, default=float))
print('secs', res['secs'], flush=True)
