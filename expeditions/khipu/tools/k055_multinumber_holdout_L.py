#!/usr/bin/env python3
"""K055 - R5 multi-number-cord sensitivity of the FROZEN K034/K037 held-out L
confirmations (README line 1).

Pre-registered here and in case-file/K055-multinumber-holdout-L.md BEFORE any
confirmation p-value, FPR or power number was computed.

Usage (run from expeditions/khipu):
  python3 tools/k055_multinumber_holdout_L.py khipu.db --smoke
      G0 fixture + a synthetic toy (no real-data p-value).
  python3 tools/k055_multinumber_holdout_L.py khipu.db
      G0, then confirmation (R=20 000), G1 FPR, G2 power; write analysis/k055_results.json.

QUESTION. Do the four frozen held-out L confirmations survive the same K008
multi-number (R5) mask?
  1. KH0322 / UR086  — K034, L=8, p=0.0014
  2. KH0420 / UR182  — K034, L=8, p=0.00020
  3. KH0502 / UR266  — K037, L=3, p=0.01465
  4. KH0511 / UR273B — K037, L=3, p=0.00195

This is a sensitivity rerun of frozen confirmation tests, not a redesign and not
a new discovery scan. The statistic L, the confirmation alpha_i = 0.025 and the
named targets are frozen. Decision does not consult any BH list or D5w ranking.
Do NOT switch to Bonferroni x4.

STATISTIC L. Longest within-group exact-sum window. L = max k in {2,...,12} such
that some pendant with value >= 10 equals the sum of k consecutive neighbours
entirely inside the same group, with >= 2 nonzero summands (K034/K037 valid_masks).

R5 CORD (K007/K008). >= 2 knot clusters with a single decimal place, and those
places, read in knot_cluster.ORDINAL order, are not strictly decreasing.
Expected count in the DB: 3069 (fixture gate).

MASK (K008, structure-preserving). An R5 pendant keeps its position but is never
a sum target and never part of a summand block. Null permutes only non-R5 values
among non-R5 positions; group ids stay put.

p = (1 + #{null draws with L >= L_obs}) / (1 + R), R = 20 000 masked permutations.

DECISION (per name, frozen K034/K037 rule at the original confirmation alpha):
  survives / still confirmed  iff masked p <= 0.025 and the FPR gate passes
  no longer established       iff masked p > 0.025 and plant power >= 0.5
  not testable                iff masked p > 0.025 and power < 0.5,
                              OR the khipu cannot place a masked L
A name that cannot be scored under the mask is not testable, not lost.

OVERALL (written before any run):
  1. All four survive -> the holdout confirmations are robust to the mask (ROBUST)
  2. A proper subset survive -> PARTIAL (name who drops and why)
  3. None survive and all are testable -> none remain established (NONE_ESTABLISHED)
  4. FPR gate fails -> EXCLUDED (no confirmation claimed)
  5. None survive and at least one is not testable -> report each name; do not
     claim the set is established or that all are lost (NONE_SURVIVE_SOME_UNTESTABLE)

GATES.
  G0 fixture (stop on failure): DB hash matches manifest; 3 069 R5 cords; four
     named targets load; with an empty mask the masked code reproduces each
     name's published unmasked L (KH0322 L=8, KH0420 L=8, KH0502 L=3,
     KH0511 L=3); R5-free named khipus (KH0322 has 0 R5) reproduce L under the
     real mask too.
  G1 FPR (seed 5555): 200 random multi-group pop khipus (>= 2 groups of size >= 4)
     other than the four named. For each, one masked-within-khipu permutation is
     a null "observed"; its L p-value vs R_fpr = 5 000 fresh masked permutations.
     FPR = fraction with p <= 0.025. Pass iff FPR <= 0.08. Report binomial
     P(X >= x | n=200, 0.05).
  G2 power (seed 5554): per named khipu, N = 200 plants: masked-permute, then
     plant one within-group exact sum of length k = 6 inside a group of size >= 8,
     restricted so target and summands are all non-R5. Fallback k = 5 in a group
     of size >= 7 if needed, still all non-R5. Each plant scored with R_pow = 5 000
     nested masked permutations. Power = fraction with p <= 0.025. Required >= 0.5
     for a negative to be readable. If a named khipu cannot place the plant,
     report and skip that name for G2 (do not silently lower the bar).

SEEDS (distinct from K034 3430-3433, K037 3730-3733, K053 5353-5355, K054 5454-5455):
  5550 KH0322 confirm, 5551 KH0420 confirm, 5552 KH0502 confirm,
  5553 KH0511 confirm, 5554 power, 5555 FPR.

Same-data caveat: reanalysis of the same pinned corpus, not an independent
replication. No decipherment is claimed.
"""
import sqlite3, sys, json, time, os, hashlib
import numpy as np
from collections import defaultdict
from math import lgamma, log, exp

t0 = time.time()
DB = sys.argv[1]
SMOKE = '--smoke' in sys.argv or (len(sys.argv) > 2 and sys.argv[2] == 'fixture')
SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
TARGETS = ('KH0322', 'KH0420', 'KH0502', 'KH0511')
PUBLISHED_L = dict(KH0322=8, KH0420=8, KH0502=3, KH0511=3)
PUBLISHED_P = dict(KH0322=0.0014, KH0420=0.00020, KH0502=0.01465, KH0511=0.00195)
PUBLISHED_SOURCE = dict(KH0322='K034', KH0420='K034', KH0502='K037', KH0511='K037')
R_CONF = 200 if SMOKE else 20000
R_FPR = 100 if SMOKE else 5000
R_POW = 100 if SMOKE else 5000
N_FPR = 20 if SMOKE else 200
N_POW = 20 if SMOKE else 200
ALPHA = 0.025
SEEDS = dict(KH0322=5550, KH0420=5551, KH0502=5552, KH0511=5553, power=5554, fpr=5555)
OUT = 'analysis/k055_results.json'
CK = 'analysis/k055_checkpoint.json'
CHUNK = 400

c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute(
    "select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
okr_to_id = {okr: kid for kid, (okr, _) in names.items()}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None:
        val[cid] += int(v)

# --- R5 definition, copied verbatim from K008 / K053 / K054 ---
def place(v):
    p = 0
    while v % 10 == 0:
        v //= 10
        p += 1
    return p
clplaces = defaultdict(set)
clcord = {}
for cid, cl, t, v in c.execute("select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
    t = (t or '').strip()
    if t in ('S', 'L', 'E') and v:
        clplaces[cl].add(place(int(v)) if t == 'S' else 0)
    clcord[cl] = cid
ordn = {r[0]: r[1] for r in c.execute("select CLUSTER_ID, ORDINAL from knot_cluster")}
bycord = defaultdict(dict)
for cl, pl in clplaces.items():
    if len(pl) == 1 and ordn.get(cl) is not None:
        bycord[clcord[cl]][ordn[cl]] = next(iter(pl))
R5 = set()
for cd, d in bycord.items():
    s = [d[o] for o in sorted(d)]
    if len(s) >= 2 and not all(a > b for a, b in zip(s, s[1:])):
        R5.add(cd)

kh = defaultdict(list)
for khid, cid, cl in c.execute(
        "select KHIPU_ID, CORD_ID, CLUSTER_ID from cord "
        "where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups:
        continue
    kh[khid].append((cid, cl, val.get(cid, 0)))

data = {}
for khid, cords in kh.items():
    v = np.array([x[2] for x in cords], np.int64)
    if (v > 0).sum() < 10:
        continue
    gids = np.empty(len(cords), np.int32)
    gi, last, sizes = -1, object(), []
    for i, (_, cl, _) in enumerate(cords):
        if cl != last:
            gi += 1
            last = cl
            sizes.append(0)
        gids[i] = gi
        sizes[-1] += 1
    bad = np.array([x[0] in R5 for x in cords])
    n4 = sum(1 for s in sizes if s >= 4)
    data[khid] = dict(v=v, gids=gids, sizes=sizes, n4=n4, n_groups=len(sizes),
                      okr=names[khid][0], inv=names[khid][1], bad=bad)

pop_ids = [kid for kid, d in data.items() if d['n4'] >= 2]
named = {}
for okr in TARGETS:
    kid = okr_to_id.get(okr)
    if kid is None or kid not in data:
        raise SystemExit(f'missing target {okr}')
    named[okr] = kid


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


def longest_L_batch_masked(V, gids, vr, vl, bad):
    """V: (B, n) int64. R5 never a target; any block containing an R5 is invalid.
    With an all-False mask this is identical to K034/K037 unmasked L."""
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64)
    P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64)
    NZ[:, 1:] = np.cumsum(V > 0, 1)
    BD = np.zeros(n + 1, np.int64)
    BD[1:] = np.cumsum(bad.astype(np.int64))
    idx = np.arange(n)
    tgt = (V >= 10) & ~bad[None, :]
    L = np.zeros(B, np.int32)
    for k in range(2, 13):
        hk = np.zeros((B, n), bool)
        i = idx[idx + k < n]
        i = i[vr[k][i]]
        if len(i):
            ok = (BD[i + k + 1] - BD[i + 1]) == 0
            hk[:, i] |= ((P[:, i + k + 1] - P[:, i + 1]) == V[:, i]) & (
                (NZ[:, i + k + 1] - NZ[:, i + 1]) >= 2) & ok
        i = idx[idx - k >= 0]
        i = i[vl[k][i]]
        if len(i):
            ok = (BD[i] - BD[i - k]) == 0
            hk[:, i] |= ((P[:, i] - P[:, i - k]) == V[:, i]) & (
                (NZ[:, i] - NZ[:, i - k]) >= 2) & ok
        hk &= tgt
        L = np.where(hk.any(1), np.maximum(L, k), L)
    return L


def longest_L_unmasked(V, gids, vr, vl):
    return longest_L_batch_masked(V, gids, vr, vl, np.zeros(len(gids), bool))


def can_place_masked_L(gids, bad):
    """True if at least one masked k>=2 window (target + summands all non-R5, same group) exists."""
    n = len(gids)
    vr, vl = valid_masks(gids)
    BD = np.zeros(n + 1, np.int64)
    BD[1:] = np.cumsum(bad.astype(np.int64))
    for k in range(2, 13):
        for i in range(n):
            if bad[i]:
                continue
            if i + k < n and vr[k][i] and (BD[i + k + 1] - BD[i + 1]) == 0:
                return True
            if i - k >= 0 and vl[k][i] and (BD[i] - BD[i - k]) == 0:
                return True
    return False


def hit_detail_masked(v, gids, vr, vl, bad):
    """Single-sequence descriptive: masked L, n_hits, n_groups_hit, max-k groups, LOO L."""
    V = v[None]
    n = len(v)
    P = np.zeros((1, n + 1), np.int64)
    P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((1, n + 1), np.int64)
    NZ[:, 1:] = np.cumsum(V > 0, 1)
    BD = np.zeros(n + 1, np.int64)
    BD[1:] = np.cumsum(bad.astype(np.int64))
    idx = np.arange(n)
    tgt = (V >= 10) & ~bad[None, :]
    hit = np.zeros(n, bool)
    k_at = np.zeros(n, np.int32)
    L = 0
    for k in range(2, 13):
        hk = np.zeros(n, bool)
        i = idx[idx + k < n]
        i = i[vr[k][i]]
        if len(i):
            ok = (BD[i + k + 1] - BD[i + 1]) == 0
            m = ((P[0, i + k + 1] - P[0, i + 1]) == V[0, i]) & (
                (NZ[0, i + k + 1] - NZ[0, i + 1]) >= 2) & ok & tgt[0, i]
            hk[i] |= m
        i = idx[idx - k >= 0]
        i = i[vl[k][i]]
        if len(i):
            ok = (BD[i] - BD[i - k]) == 0
            m = ((P[0, i] - P[0, i - k]) == V[0, i]) & (
                (NZ[0, i] - NZ[0, i - k]) >= 2) & ok & tgt[0, i]
            hk[i] |= m
        hit |= hk
        if hk.any():
            L = max(L, k)
            k_at[hk] = np.maximum(k_at[hk], k)
    ng = int(gids.max()) + 1
    gsize = np.bincount(gids, minlength=ng)
    ghit = np.bincount(gids, weights=hit.astype(float), minlength=ng).astype(int)
    n_gh = int(((gsize >= 4) & (ghit > 0)).sum())
    max_groups = sorted({int(gids[i]) for i in range(n) if k_at[i] == L and L > 0})
    loo_L = None
    if max_groups:
        v2 = v.copy()
        for g in max_groups:
            v2[gids == g] = 0
        loo_L = int(longest_L_batch_masked(v2[None], gids, vr, vl, bad)[0])
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


def permmask(rng, v, bad, B):
    """K054 N1: permute only non-R5 values among non-R5 positions."""
    free = np.where(~bad)[0]
    out = np.tile(v, (B, 1))
    if len(free):
        out[:, free] = v[free][rng.random((B, len(free))).argsort(1)]
    return out


def plant_L6_masked(rng, v, gids, bad):
    """Masked-permute, then plant one within-group exact sum of length 6
    (fallback 5) with target and summands all non-R5.
    Returns (planted_array, k_used) or (None, None) if no legal block exists."""
    pl = permmask(rng, v, bad, 1)[0].copy()
    ranges = group_ranges(gids)
    for k_want in (6, 5):
        ch = []
        for a, b in ranges:
            if (b - a) < k_want + 2:
                continue
            max_st = b - k_want - 1
            for st in range(a, max_st + 1):
                if not bad[st:st + 1 + k_want].any():
                    ch.append(st)
        if not ch:
            continue
        st = ch[int(rng.integers(0, len(ch)))]
        sl = slice(st + 1, st + 1 + k_want)
        blk = pl[sl].copy()
        if (blk > 0).sum() < 2:
            blk[:] = np.maximum(blk, rng.integers(1, 30, size=len(blk)))
        s = int(blk.sum())
        if s < 10:
            blk[0] += 10 - s
            s = int(blk.sum())
        pl[sl] = blk
        pl[st] = s
        return pl, k_want
    return None, None


def can_plant_structurally(gids, bad):
    """True if some group can host a k=6 (size>=8) or k=5 (size>=7) all-non-R5 plant."""
    ranges = group_ranges(gids)
    for k_want in (6, 5):
        for a, b in ranges:
            if (b - a) < k_want + 2:
                continue
            max_st = b - k_want - 1
            for st in range(a, max_st + 1):
                if not bad[st:st + 1 + k_want].any():
                    return True
    return False


def null_Ls_masked(rng, v, gids, vr, vl, bad, R, chunk=CHUNK):
    out = np.empty(R, np.int32)
    left, pos = R, 0
    while left > 0:
        m = min(chunk, left)
        V = permmask(rng, v, bad, m)
        out[pos:pos + m] = longest_L_batch_masked(V, gids, vr, vl, bad)
        pos += m
        left -= m
    return out


# ---------------- G0 fixture ----------------
h = hashlib.sha256(open(DB, 'rb').read()).hexdigest()
empty_ok = {}
r5free_ok = {}
target_load = {}
for okr in TARGETS:
    kid = named[okr]
    d = data[kid]
    v, gids, bad = d['v'], d['gids'], d['bad']
    vr, vl = valid_masks(gids)
    L_empty = int(longest_L_unmasked(v[None], gids, vr, vl)[0])
    empty_ok[okr] = (L_empty == PUBLISHED_L[okr])
    n_r5 = int(bad.sum())
    target_load[okr] = dict(
        khipu_id=int(kid), okr=okr, inv=d['inv'],
        n_pend=int(len(v)), n_groups=int(d['n_groups']),
        n4=int(d['n4']), n_r5=n_r5,
        n_unmasked_nonzero=int(((v > 0) & ~bad).sum()),
        can_place_masked_L=bool(can_place_masked_L(gids, bad)),
        can_plant=bool(can_plant_structurally(gids, bad)),
        L_empty_mask=L_empty,
        published_L=PUBLISHED_L[okr],
        empty_mask_matches_published=empty_ok[okr],
    )
    if n_r5 == 0:
        L_real = int(longest_L_batch_masked(v[None], gids, vr, vl, bad)[0])
        r5free_ok[okr] = (L_real == PUBLISHED_L[okr])
        target_load[okr]['L_real_mask'] = L_real
        target_load[okr]['real_mask_matches_published'] = r5free_ok[okr]

g0 = dict(
    sha256=h, sha_ok=h == SHA,
    n_r5=len(R5), r5_ok=len(R5) == 3069,
    n_eligible=len(data), n_pop=len(pop_ids),
    targets_loaded=all(o in named for o in TARGETS),
    empty_mask_L= {o: target_load[o]['L_empty_mask'] for o in TARGETS},
    empty_mask_reproduces_published=all(empty_ok.values()),
    r5free_named=[o for o in TARGETS if data[named[o]]['bad'].sum() == 0],
    r5free_real_mask_reproduces=all(r5free_ok.values()) if r5free_ok else False,
    r5free_detail=r5free_ok,
    targets=target_load,
)
g0['pass'] = bool(
    g0['sha_ok'] and g0['r5_ok'] and g0['targets_loaded']
    and g0['empty_mask_reproduces_published']
    and g0['r5free_real_mask_reproduces']
)
print('G0', json.dumps({k: g0[k] for k in g0 if k != 'targets'}, default=int), flush=True)
print('G0_targets', json.dumps(target_load, default=int), flush=True)
if not g0['pass']:
    sys.exit('G0 fixture failed - stop')

if SMOKE:
    # synthetic smoke of the masked L machinery (no real-data p-value)
    r = np.random.default_rng(0)
    v = r.integers(0, 40, 24).astype(np.int64)
    gids = np.array([0] * 8 + [1] * 8 + [2] * 8, np.int32)
    b = np.zeros(24, bool)
    b[[2, 22]] = True  # R5 in groups 0 and 2, away from the plant in group 1
    vr, vl = valid_masks(gids)
    # plant a visible within-group right-sum: target at 8, k=6 summands at 9..14 (group 1 = 8..15)
    blk = np.maximum(v[9:15], 1)
    s = int(blk.sum())
    if s < 10:
        blk[0] += 10 - s
        s = int(blk.sum())
    v[9:15] = blk
    v[8] = s
    L_see = int(longest_L_batch_masked(v[None], gids, vr, vl, b)[0])
    b2 = b.copy()
    b2[9] = True  # mark first summand R5: the planted window must vanish
    L_hide = int(longest_L_batch_masked(v[None], gids, vr, vl, b2)[0])
    print('smoke toy planted_k6_L', L_see, 'R5-in-block_L', L_hide,
          'see_ge_6', L_see >= 6, 'hide_lt_see', L_hide < L_see, flush=True)
    if L_see < 6:
        sys.exit('smoke toy failed: planted k=6 window not seen')
    print(json.dumps(dict(mode='smoke', G0_pass=g0['pass'], secs=round(time.time() - t0, 1)),
                     default=int), flush=True)
    sys.exit(0)


# ---------------- confirmation ----------------
conf = {}
for okr in TARGETS:
    kid = named[okr]
    d = data[kid]
    v, gids, bad = d['v'], d['gids'], d['bad']
    vr, vl = valid_masks(gids)
    scorable = can_place_masked_L(gids, bad)
    L_unmasked = int(longest_L_unmasked(v[None], gids, vr, vl)[0])
    detail = hit_detail_masked(v, gids, vr, vl, bad) if scorable else dict(
        L=None, n_hits=0, n_groups_hit=0, n_eligible_groups=int((np.bincount(gids) >= 4).sum()),
        max_k_groups=[], loo_L_after_zeroing_max_groups=None)
    if scorable:
        rng = np.random.default_rng(SEEDS[okr])
        null_L = null_Ls_masked(rng, v, gids, vr, vl, bad, R_CONF)
        p = p_from_nulls(detail['L'], null_L)
        crit = int(np.quantile(null_L, 1 - ALPHA, method='higher'))
        tail = float((null_L >= crit).mean())
        null_mean = float(null_L.mean())
        null_p95 = float(np.percentile(null_L, 95))
        null_p99 = float(np.percentile(null_L, 99))
        null_max = int(null_L.max())
    else:
        p = None
        crit = tail = null_mean = null_p95 = null_p99 = null_max = None
    conf[okr] = dict(
        khipu_id=int(kid), okr=okr, inv=d['inv'], n_pend=int(len(v)),
        n_groups=int(d['n_groups']), n_r5=int(bad.sum()),
        n_unmasked_nonzero=int(((v > 0) & ~bad).sum()),
        scorable=scorable, L_unmasked=L_unmasked, L_masked=detail['L'],
        published_L=PUBLISHED_L[okr], published_p=PUBLISHED_P[okr],
        published_source=PUBLISHED_SOURCE[okr],
        detail=detail, p=p,
        null_mean=null_mean, null_p95=null_p95, null_p99=null_p99,
        null_max=null_max, crit_alpha=crit, null_tail_at_crit=tail,
        R=R_CONF, seed=SEEDS[okr],
    )
    print('CONF', okr, 'L_unmasked', L_unmasked, 'L_masked', detail['L'],
          'n_r5', int(bad.sum()), 'p', p, 'scorable', scorable,
          round(time.time() - t0, 1), flush=True)
    os.makedirs('analysis', exist_ok=True)
    json.dump(dict(phase='confirmation', done=list(conf), G0=g0),
              open(CK, 'w'), indent=1, default=float)


# ---------------- FPR gate ----------------
rng_f = np.random.default_rng(SEEDS['fpr'])
candidates = [kid for kid in pop_ids if kid not in named.values()]
rng_f.shuffle(candidates)
pick = candidates[:N_FPR]
fpr_hits = 0
fpr_rows = []
for kid in pick:
    d = data[kid]
    v, gids, bad = d['v'], d['gids'], d['bad']
    vr, vl = valid_masks(gids)
    x = permmask(rng_f, v, bad, 1)[0]
    L_obs = int(longest_L_batch_masked(x[None], gids, vr, vl, bad)[0])
    null_L = null_Ls_masked(rng_f, x, gids, vr, vl, bad, R_FPR)
    p = p_from_nulls(L_obs, null_L)
    hit = p <= ALPHA
    fpr_hits += int(hit)
    fpr_rows.append(dict(okr=d['okr'], inv=d['inv'], L=L_obs, p=p, hit=bool(hit)))
    if len(fpr_rows) % 50 == 0:
        print('FPR', len(fpr_rows), round(time.time() - t0, 1), flush=True)
fpr = fpr_hits / max(1, len(pick))
fpr_gate = fpr <= 0.08
fpr_block = dict(n=len(pick), hits=fpr_hits, fpr=fpr, gate_pass=bool(fpr_gate),
                 gate_threshold=0.08,
                 binom_p_above_0_05=binom_tail(fpr_hits, len(pick), 0.05),
                 seed=SEEDS['fpr'], R=R_FPR)
print('FPR', fpr, 'hits', fpr_hits, '/', len(pick), 'gate', fpr_gate,
      'binom', fpr_block['binom_p_above_0_05'], flush=True)
json.dump(dict(phase='fpr', confirmation=conf, fpr=fpr_block, G0=g0),
          open(CK, 'w'), indent=1, default=float)


# ---------------- Power ----------------
rng_p = np.random.default_rng(SEEDS['power'])
power = {}
for okr in TARGETS:
    kid = named[okr]
    d = data[kid]
    v, gids, bad = d['v'], d['gids'], d['bad']
    vr, vl = valid_masks(gids)
    if not can_plant_structurally(gids, bad):
        power[okr] = dict(n_plants=0, skipped=N_POW, detected=0, power=None,
                          R=R_POW, skipped_g2=True,
                          reason='cannot place a non-R5 k=6 (or fallback k=5) plant')
        print('POW', okr, 'SKIP cannot place plant', round(time.time() - t0, 1), flush=True)
        continue
    ok = 0
    attempted = 0
    skipped = 0
    ks = []
    for _ in range(N_POW):
        pl, k_used = plant_L6_masked(rng_p, v, gids, bad)
        if pl is None:
            skipped += 1
            continue
        attempted += 1
        ks.append(k_used)
        L_obs = int(longest_L_batch_masked(pl[None], gids, vr, vl, bad)[0])
        null_L = null_Ls_masked(rng_p, pl, gids, vr, vl, bad, R_POW)
        p = p_from_nulls(L_obs, null_L)
        if p <= ALPHA:
            ok += 1
    pow_rate = ok / attempted if attempted else None
    power[okr] = dict(n_plants=attempted, skipped=skipped, detected=ok,
                      power=pow_rate, R=R_POW, skipped_g2=False,
                      k_used_counts={str(k): ks.count(k) for k in sorted(set(ks))})
    print('POW', okr, pow_rate, 'det', ok, '/', attempted, 'skip', skipped,
          round(time.time() - t0, 1), flush=True)
json.dump(dict(phase='power', confirmation=conf, fpr=fpr_block, power=power, G0=g0),
          open(CK, 'w'), indent=1, default=float)


# ---------------- decisions ----------------
per = {}
for okr in TARGETS:
    rec = conf[okr]
    pw = power[okr]['power']
    if not rec['scorable']:
        verdict = 'not_testable'
        why = 'cannot place a masked L'
    elif not fpr_gate:
        verdict = 'excluded_by_fpr_gate'
        why = 'FPR gate failed'
    elif rec['p'] <= ALPHA:
        verdict = 'survives'
        why = f"masked p={rec['p']:.5g} <= {ALPHA}"
    elif pw is None:
        verdict = 'not_testable'
        why = 'masked p > 0.025 and G2 plant could not be placed (power unread)'
    elif pw >= 0.5:
        verdict = 'no_longer_established'
        why = f"masked p={rec['p']:.5g} > {ALPHA} and power={pw:.3f} >= 0.5"
    else:
        verdict = 'not_testable'
        why = f"masked p={rec['p']:.5g} > {ALPHA} and power={pw:.3f} < 0.5"
    per[okr] = dict(p_orig=PUBLISHED_P[okr], p_masked=rec['p'],
                    L_orig=PUBLISHED_L[okr], L_unmasked=rec['L_unmasked'],
                    L_masked=rec['L_masked'], n_r5=rec['n_r5'],
                    power=pw, verdict=verdict, why=why,
                    scorable=rec['scorable'])

n_surv = sum(1 for o in TARGETS if per[o]['verdict'] == 'survives')
n_nt = sum(1 for o in TARGETS if per[o]['verdict'] == 'not_testable')
n_drop = sum(1 for o in TARGETS if per[o]['verdict'] == 'no_longer_established')
if not fpr_gate:
    overall = 'EXCLUDED'
elif n_surv == 4:
    overall = 'ROBUST'
elif n_surv >= 1:
    overall = 'PARTIAL'
elif n_drop + n_surv + n_nt == 4 and n_nt == 0:
    overall = 'NONE_ESTABLISHED'
else:
    overall = 'NONE_SURVIVE_SOME_UNTESTABLE'

res = dict(
    design=dict(statistic='masked_longest_within_group_exact_sum_window_L',
                alpha_per_khipu=ALPHA, bonferroni=None,
                note='sensitivity of frozen tests; original confirmation alpha_i=0.025 kept; not a new four-way discovery',
                R_CONF=R_CONF, R_FPR=R_FPR, R_POW=R_POW,
                N_FPR=N_FPR, N_POW=N_POW,
                plant='masked-permute then one within-group exact sum k=6 (fallback k=5), all non-R5',
                seeds=SEEDS, smoke=SMOKE,
                mask='K008 structure-preserving R5',
                published_L=PUBLISHED_L, published_p=PUBLISHED_P),
    G0=g0,
    confirmation=conf,
    fpr=fpr_block,
    power=power,
    per_khipu=per,
    overall=overall,
    n_survive=n_surv, n_no_longer_established=n_drop, n_not_testable=n_nt,
    secs=round(time.time() - t0, 1),
)
os.makedirs('analysis', exist_ok=True)
json.dump(res, open(OUT, 'w'), indent=1, default=float)
print(json.dumps(dict(overall=overall, per_khipu=per, fpr=res['fpr'],
                      power={o: power[o].get('power') for o in TARGETS},
                      secs=res['secs']), indent=1), flush=True)
