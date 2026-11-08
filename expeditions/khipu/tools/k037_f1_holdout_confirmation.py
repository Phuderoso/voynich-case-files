#!/usr/bin/env python3
"""K037 - held-out confirmation of KH0502/UR266 and KH0511/UR273B via longest
within-group exact-sum window L. Pre-registered in
case-file/K037-f1-holdout-confirmation.md
(K034 design copied; only targets, seeds and output path changed).
Usage: python3 tools/k037_f1_holdout_confirmation.py khipu.db [--smoke]
"""
import sqlite3, sys, json, time
import numpy as np
from collections import defaultdict
from math import lgamma, log, exp

t0 = time.time()
DB = sys.argv[1]
SMOKE = '--smoke' in sys.argv
TARGETS = ('KH0502', 'KH0511')  # OKR_NUM
R_CONF = 200 if SMOKE else 20000
R_FPR = 100 if SMOKE else 5000
R_POW = 100 if SMOKE else 5000
N_FPR = 20 if SMOKE else 200
N_POW = 20 if SMOKE else 200
ALPHA = 0.025
SEEDS = dict(KH0502=3730, KH0511=3731, power=3732, fpr=3733)

c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute(
    "select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
okr_to_id = {okr: kid for kid, (okr, _) in names.items()}
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

data = {}
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
    n4 = sum(1 for s in sizes if s >= 4)
    data[khid] = dict(v=v, gids=gids, sizes=sizes, n4=n4, n_groups=len(sizes),
                      okr=names[khid][0], inv=names[khid][1])

pop_ids = [kid for kid, d in data.items() if d['n4'] >= 2]
named = {}
for okr in TARGETS:
    kid = okr_to_id.get(okr)
    if kid is None or kid not in data:
        raise SystemExit(f'missing target {okr}')
    named[okr] = kid
print(json.dumps(dict(n_eligible=len(data), n_pop=len(pop_ids),
                      targets={o: dict(khipu_id=named[o], **{k: (int(data[named[o]][k]) if k in ('n4', 'n_groups')
                                                                else data[named[o]][k])
                                                             for k in ('okr', 'inv', 'n4', 'n_groups')} ,
                                      n_pend=len(data[named[o]]['v']), sizes=data[named[o]]['sizes'])
                               for o in TARGETS},
                      seeds=SEEDS, R_CONF=R_CONF, R_FPR=R_FPR, R_POW=R_POW,
                      N_FPR=N_FPR, N_POW=N_POW, alpha=ALPHA)), flush=True)


def valid_masks(gids):
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
    return vr, vl


def longest_L_batch(V, gids, vr, vl):
    """V: (B, n) int64. Returns (B,) max within-group exact-sum window length (0 if none)."""
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64)
    P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64)
    NZ[:, 1:] = np.cumsum(V > 0, 1)
    idx = np.arange(n)
    big = V >= 10
    L = np.zeros(B, np.int32)
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
        L = np.where(hk.any(1), np.maximum(L, k), L)
    return L


def hit_detail(v, gids, vr, vl):
    """Single-sequence descriptive: L, n_hits, n_groups_hit, hit-group ids, LOO L."""
    V = v[None]
    n = len(v)
    P = np.zeros((1, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((1, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    idx = np.arange(n); big = V >= 10
    hit = np.zeros(n, bool); k_at = np.zeros(n, np.int32); L = 0
    for k in range(2, 13):
        hk = np.zeros(n, bool)
        i = idx[idx + k < n]; i = i[vr[k][i]]
        if len(i):
            m = ((P[0, i + k + 1] - P[0, i + 1]) == V[0, i]) & (
                (NZ[0, i + k + 1] - NZ[0, i + 1]) >= 2) & big[0, i]
            hk[i] |= m
        i = idx[idx - k >= 0]; i = i[vl[k][i]]
        if len(i):
            m = ((P[0, i] - P[0, i - k]) == V[0, i]) & (
                (NZ[0, i] - NZ[0, i - k]) >= 2) & big[0, i]
            hk[i] |= m
        hit |= hk
        if hk.any():
            L = max(L, k)
            k_at[hk] = np.maximum(k_at[hk], k)
    ng = int(gids.max()) + 1
    gsize = np.bincount(gids, minlength=ng)
    ghit = np.bincount(gids, weights=hit.astype(float), minlength=ng).astype(int)
    n_gh = int(((gsize >= 4) & (ghit > 0)).sum())
    # groups carrying the max-k hit
    max_groups = sorted({int(gids[i]) for i in range(n) if k_at[i] == L and L > 0})
    loo_L = None
    if max_groups:
        v2 = v.copy()
        for g in max_groups:
            v2[gids == g] = 0
        loo_L = int(longest_L_batch(v2[None], gids, vr, vl)[0])
    return dict(L=int(L), n_hits=int(hit.sum()), n_groups_hit=n_gh,
                n_eligible_groups=int((gsize >= 4).sum()),
                max_k_groups=max_groups, loo_L_after_zeroing_max_groups=loo_L)


def p_from_nulls(L_obs, null_L):
    return float((1 + int((null_L >= L_obs).sum())) / (1 + len(null_L)))


def binom_tail(x, n, a=0.05):
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


def plant_L6(rng, v, gids):
    """Plant one within-group exact sum of length 6 (fallback 5). Returns new array or None."""
    pl = rng.permutation(v).copy()
    ranges = group_ranges(gids)
    for k_want in (6, 5):
        ch = [(a, b) for a, b in ranges if (b - a) >= k_want + 2]
        if not ch:
            continue
        a, b = ch[int(rng.integers(0, len(ch)))]
        # place total at left of a k-block inside [a,b)
        # choose start of total so total + k neighbours fit
        # right-summing: total at st, summands st+1..st+k
        max_st = b - k_want - 1
        if max_st < a:
            continue
        st = int(rng.integers(a, max_st + 1))
        sl = slice(st + 1, st + 1 + k_want)
        blk = pl[sl].copy()
        if (blk > 0).sum() < 2:
            blk[:] = np.maximum(blk, rng.integers(1, 30, len(blk)))
        s = int(blk.sum())
        if s < 10:
            blk[0] += 10 - s
            s = int(blk.sum())
        pl[sl] = blk
        pl[st] = s
        return pl
    return None


def null_Ls(rng, v, gids, vr, vl, R, chunk=500):
    out = np.empty(R, np.int32)
    left, pos = R, 0
    while left > 0:
        m = min(chunk, left)
        V = np.array([rng.permutation(v) for _ in range(m)])
        out[pos:pos + m] = longest_L_batch(V, gids, vr, vl)
        pos += m
        left -= m
    return out


# ---------- confirmation ----------
conf = {}
for okr in TARGETS:
    kid = named[okr]
    d = data[kid]
    v, gids = d['v'], d['gids']
    vr, vl = valid_masks(gids)
    detail = hit_detail(v, gids, vr, vl)
    rng = np.random.default_rng(SEEDS[okr])
    null_L = null_Ls(rng, v, gids, vr, vl, R_CONF)
    p = p_from_nulls(detail['L'], null_L)
    # exchangeable tail at critical value for α=0.025
    crit = int(np.quantile(null_L, 1 - ALPHA, method='higher')) if hasattr(np, 'quantile') else int(np.percentile(null_L, 100 * (1 - ALPHA)))
    # fraction of nulls with L >= crit (descriptive calibration on this structure)
    tail = float((null_L >= crit).mean())
    conf[okr] = dict(khipu_id=kid, okr=okr, inv=d['inv'], n_pend=len(v),
                     n_groups=d['n_groups'], sizes=d['sizes'],
                     detail=detail, L_obs=detail['L'], p=p,
                     null_mean=float(null_L.mean()), null_p95=float(np.percentile(null_L, 95)),
                     null_p99=float(np.percentile(null_L, 99)),
                     null_max=int(null_L.max()), crit_alpha=crit, null_tail_at_crit=tail,
                     R=R_CONF, seed=SEEDS[okr])
    print('CONF', okr, 'L', detail['L'], 'p', p, 'crit', crit, 'tail', round(tail, 4),
          round(time.time() - t0, 1), flush=True)

# ---------- FPR gate ----------
rng_f = np.random.default_rng(SEEDS['fpr'])
candidates = [kid for kid in pop_ids if kid not in named.values()]
rng_f.shuffle(candidates)
pick = candidates[:N_FPR]
fpr_hits = 0
fpr_rows = []
for kid in pick:
    d = data[kid]
    v, gids = d['v'], d['gids']
    vr, vl = valid_masks(gids)
    # one null "observed"
    x = rng_f.permutation(v)
    L_obs = int(longest_L_batch(x[None], gids, vr, vl)[0])
    null_L = null_Ls(rng_f, x, gids, vr, vl, R_FPR)
    p = p_from_nulls(L_obs, null_L)
    hit = p <= ALPHA
    fpr_hits += int(hit)
    fpr_rows.append(dict(okr=d['okr'], inv=d['inv'], L=L_obs, p=p, hit=hit))
    if len(fpr_rows) % 50 == 0:
        print('FPR', len(fpr_rows), round(time.time() - t0, 1), flush=True)
fpr = fpr_hits / max(1, len(pick))
fpr_gate = fpr <= 0.08
print('FPR', fpr, 'hits', fpr_hits, '/', len(pick), 'gate', fpr_gate,
      'binom', binom_tail(fpr_hits, len(pick), 0.05), flush=True)

# ---------- Power ----------
rng_p = np.random.default_rng(SEEDS['power'])
power = {}
for okr in TARGETS:
    kid = named[okr]
    d = data[kid]
    v, gids = d['v'], d['gids']
    vr, vl = valid_masks(gids)
    ok = 0
    attempted = 0
    skipped = 0
    for _ in range(N_POW):
        pl = plant_L6(rng_p, v, gids)
        if pl is None:
            skipped += 1
            continue
        attempted += 1
        L_obs = int(longest_L_batch(pl[None], gids, vr, vl)[0])
        null_L = null_Ls(rng_p, pl, gids, vr, vl, R_POW)
        p = p_from_nulls(L_obs, null_L)
        if p <= ALPHA:
            ok += 1
    pow_rate = ok / attempted if attempted else float('nan')
    power[okr] = dict(n_plants=attempted, skipped=skipped, detected=ok,
                      power=pow_rate, R=R_POW)
    print('POW', okr, pow_rate, 'det', ok, '/', attempted, 'skip', skipped,
          round(time.time() - t0, 1), flush=True)

# ---------- decisions ----------
per = {}
for okr in TARGETS:
    p = conf[okr]['p']
    pw = power[okr]['power']
    if not fpr_gate:
        verdict = 'excluded_by_fpr_gate'
    elif p <= ALPHA:
        verdict = 'confirmed'
    elif pw >= 0.5:
        verdict = 'not_confirmed'
    else:
        verdict = 'not_testable'
    per[okr] = dict(p=p, L=conf[okr]['L_obs'], power=pw, verdict=verdict)

n_conf = sum(1 for o in TARGETS if per[o]['verdict'] == 'confirmed')
n_nt = sum(1 for o in TARGETS if per[o]['verdict'] == 'not_testable')
n_nc = sum(1 for o in TARGETS if per[o]['verdict'] == 'not_confirmed')
if not fpr_gate:
    overall = 'EXCLUDED'
elif n_conf == 2:
    overall = 'CONFIRMED'
elif n_conf == 1:
    overall = 'PARTIAL'
elif n_nc == 2:
    overall = 'NOT_CONFIRMED'
else:
    overall = 'NOT_TESTABLE'

res = dict(
    design=dict(statistic='longest_within_group_exact_sum_window_L',
                alpha_per_khipu=ALPHA, bonferroni=2, R_CONF=R_CONF,
                R_FPR=R_FPR, R_POW=R_POW, N_FPR=N_FPR, N_POW=N_POW,
                plant='one within-group exact sum k=6 (fallback k=5)',
                seeds=SEEDS, smoke=SMOKE),
    confirmation=conf,
    fpr=dict(n=len(pick), hits=fpr_hits, fpr=fpr, gate_pass=fpr_gate,
             gate_threshold=0.08, binom_p_above_0_05=binom_tail(fpr_hits, len(pick), 0.05)),
    power=power,
    per_khipu=per,
    overall=overall,
    secs=round(time.time() - t0, 1),
)
out_path = 'analysis/k037_results.json'
json.dump(res, open(out_path, 'w'), indent=1, default=float)
print(json.dumps(dict(overall=overall, per_khipu=per, fpr=res['fpr'],
                      power={o: power[o]['power'] for o in TARGETS},
                      secs=res['secs']), indent=1), flush=True)
