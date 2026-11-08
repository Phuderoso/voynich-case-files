#!/usr/bin/env python3
"""K038 - Fixed-K=10000 BH-level F1 power for the small and mid strata, m in {2,3,4}
(K036's large-only design extended). Pre-registered in case-file/K038-fixedk-smallmid-power.md.
D5w scoring, plant_within_m, pooled exchangeable min-p, BH q=0.05, K=10000, CHUNK=1000,
valid_masks and strata are copied unchanged from tools/k036_fixedk_large_power.py.
The real F1 p-map and the calibration are INHERITED from analysis/k036_results.json
(not recomputed): no real scan, no null corpora this cycle. Power seed 3832 only.
Usage: python3 tools/k038_fixedk_smallmid_power.py khipu.db [--smoke]
"""
import sqlite3, sys, json, time, os
import numpy as np
from collections import defaultdict
from math import lgamma, log, exp, sqrt

t0 = time.time()
DB = sys.argv[1]
SMOKE = '--smoke' in sys.argv
K = 10000  # fixed; no adaptive cut (as K036)
Q = 0.05
CHUNK = 1000
SEEDS = dict(power=3832)
MS = (2, 3, 4)
POWER_STRATA = ('small', 'mid')
WALL = 520
K036_JSON = 'analysis/k036_results.json'
OUT = 'analysis/k038_smoke.json' if SMOKE else 'analysis/k038_results.json'
CKPT = 'analysis/k038_smoke_checkpoint.json' if SMOKE else 'analysis/k038_checkpoint.json'


def stop_excluded(reason):
    res = dict(decision=dict(excluded=True, reason=reason, verdicts={s: 'excluded' for s in POWER_STRATA}),
               secs=round(time.time() - t0, 1))
    json.dump(res, open(OUT, 'w'), indent=1)
    print('EXCLUDED:', reason, flush=True)
    sys.exit(0)


# --- Rule 1: inherit K036 p-map and calibration, or stop ---
if not os.path.exists(K036_JSON):
    stop_excluded('k036_results.json missing')
try:
    k036 = json.load(open(K036_JSON))
except Exception as e:  # noqa
    stop_excluded(f'k036_results.json unreadable: {e}')
if k036.get('decision', {}).get('gate_F1') is not True:
    stop_excluded('K036 gate_F1 is not true')
k036_rows = k036.get('rows') or []
if not k036_rows:
    stop_excluded('K036 rows missing')

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

# Strata on the FULL eligible set (identical to K031-K036); smoke subsamples afterwards.
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

# Consistency check against K036 (same data, same strata) before using its p-map
k036_strata = {r['khipu_id']: r['stratum'] for r in k036_rows}
consistency = dict(
    n_eligible_match=len(data) == k036.get('n_eligible'),
    n_pop_match=len(pop) == k036.get('n_pop'),
    thirds_match=bool(np.allclose([t1, t2], k036.get('thirds', [0, 0]))),
    strata_match=all(k036_strata.get(d[0]) == stratum[d[0]] for d in data) and len(k036_strata) == len(data),
)
if not all(consistency.values()):
    stop_excluded(f'data/strata do not match K036: {consistency}')

real_F1 = {r['khipu_id']: r['p_D5w'] for r in k036_rows if r['khipu_id'] in pop_ids}
if len(real_F1) != len(pop_ids):
    stop_excluded('K036 p-map does not cover pop')
cal = k036['calibration']
inherited_calibration = dict(
    source=K036_JSON + ' (K036, prereg b7d7bf1, results c5f34d8); NOT recomputed in K038',
    gate_F1=k036['decision']['gate_F1'],
    fpr={s: cal['fpr'][s] for s in cal['fpr']},
    bh_hits_per_null_corpus=cal['bh_hits_per_null_corpus'],
    bh_gate_pass=cal['bh_gate_pass'],
    n_null_corpora=cal['n_null_corpora'],
    k036_seeds=k036['design']['seeds'],
    real_F1_hits=k036['real']['hits']['F1'],
    k036_power_large=k036['power']['large'],
    k036_m_star_large=k036['decision']['m_star_large'],
)

work = {s: [d for d in data if stratum[d[0]] == s] for s in POWER_STRATA}
if SMOKE:
    work = {s: work[s][::11] for s in POWER_STRATA}
# Interleave small and mid (data order) so a wall cap leaves both strata partially covered.
order = []
for i in range(max(len(work[s]) for s in POWER_STRATA)):
    for s in POWER_STRATA:
        if i < len(work[s]):
            order.append((s, work[s][i]))

print(json.dumps(dict(n_eligible=len(data), n_pop=len(pop), thirds=[float(t1), float(t2)],
                      counts={s: sum(1 for v in stratum.values() if v == s) for s in STRATA},
                      work={s: len(work[s]) for s in POWER_STRATA}, seeds=SEEDS, K=K, MS=MS,
                      consistency=consistency, smoke=SMOKE)), flush=True)

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



def bh_insert(pmap, khid, p):
    keys = list(pmap)
    arr = np.array([p if k == khid else pmap[k] for k in keys])
    return bool(bh(arr)[keys.index(khid)])

rng = np.random.default_rng(SEEDS['power'])
power_rows, capped = [], False
reached = {s: 0 for s in POWER_STRATA}


def summarize():
    power = {}
    for s in POWER_STRATA:
        power[s] = {}
        for m in MS:
            rr = [r for r in power_rows if r['stratum'] == s and r['m'] == m]
            power[s][m] = dict(
                n=len(rr),
                p05=round(float(np.mean([r['p_D5w'] <= 0.05 for r in rr])), 4) if rr else None,
                bh_F1=round(float(np.mean([r['bh_F1'] for r in rr])), 4) if rr else None)
    return power


for j, (s, (khid, v, gids, n4, ng)) in enumerate(order):
    for m in MS:
        x, specs = plant_within_m(rng, v, gids, m)
        if x is None:
            continue
        p, cnt, denom, se = fixed_p(rng, x, gids)
        power_rows.append(dict(khipu_id=khid, okr=names[khid][0], inv=names[khid][1], n_pend=len(v),
                               stratum=s, m=m, specs=specs, p_D5w=p, cnt=cnt, denom=denom, se=se,
                               bh_F1=bh_insert(real_F1, khid, p)))
    reached[s] += 1
    if (j + 1) % 20 == 0:
        print('power', j + 1, '/', len(order), reached, round(time.time() - t0, 1), flush=True)
        json.dump(dict(stage='power', secs=round(time.time() - t0, 1), reached=reached,
                       power=summarize()), open(CKPT, 'w'), indent=1, default=float)
    if time.time() - t0 > WALL:
        capped = True
        print('power wall cap after', j + 1, 'khipus', reached, flush=True)
        break

power = summarize()
mstar, verdicts = {}, {}
for s in POWER_STRATA:
    ok = [m for m in MS if power[s][m]['n'] >= 30 and (power[s][m]['bh_F1'] or 0) >= 0.5]
    mstar[s] = min(ok) if ok else None
    verdicts[s] = (f'silence readable against >= {mstar[s]} within-group sums in {s}' if mstar[s] is not None
                   else f'not testable at m in {{2,3,4}} for {s}')

K035_REF = dict(small=dict(m_star=4, bh_power={'1': 0.10, '2': 0.28, '3': 0.49, '4': 0.59}),
                mid=dict(m_star=3, fragile=True, bh_power={'1': 0.04, '2': 0.19, '3': 0.50, '4': 0.49}))
vs_k035 = {}
for s in POWER_STRATA:
    a, b = K035_REF[s]['m_star'], mstar[s]
    vs_k035[s] = ('confirms' if b == a else 'unreads (not testable at m<=4)' if b is None
                  else f'shifts ({a} -> {b})')

res = dict(
    n_eligible=len(data), n_pop=len(pop), thirds=[float(t1), float(t2)],
    counts={s: sum(1 for v in stratum.values() if v == s) for s in STRATA},
    design=dict(K=K, adaptive=False, q=Q, seeds=SEEDS, MS=list(MS), strata=list(POWER_STRATA), wall=WALL,
                p_construction='pooled_exchangeable (K033)', scope='D5w_F1_only_power',
                p_map='inherited from K036 real scan (seed 3630), not recomputed',
                bh_level='plant p inserted in place of the khipu real p in K036 F1 family (pop 378)',
                interleaved=True, smoke=SMOKE),
    consistency_with_K036=consistency,
    inherited_calibration=inherited_calibration,
    power=power, power_khipus_reached=reached, power_khipus_total={s: len(work[s]) for s in POWER_STRATA},
    power_capped=capped,
    m_star_small=mstar['small'], m_star_mid=mstar['mid'],
    decision=dict(excluded=False, gate_F1_inherited=True, m_star=mstar, verdicts=verdicts,
                  k035_reference=K035_REF, vs_k035=vs_k035),
    power_rows=power_rows, secs=round(time.time() - t0, 1))
json.dump(res, open(OUT, 'w'), indent=1, default=float)
print(json.dumps(dict(power=power, reached=reached, capped=capped, decision=res['decision'],
                      secs=res['secs']), indent=1, default=float))
print('secs', res['secs'], flush=True)
