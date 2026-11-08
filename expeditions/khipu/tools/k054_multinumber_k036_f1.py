#!/usr/bin/env python3
"""K054 - R5 multi-number-cord sensitivity of the FROZEN K036 F1 / D5w reference list (README line 1).
Pre-registered here and in case-file/K054-multinumber-k036-f1.md BEFORE any gate or corpus number was computed.
Usage (run from expeditions/khipu):  python3 tools/k054_multinumber_k036_f1.py /workspace/khipu/khipu.db {fixture|all}
  fixture = hash / R5-count / eligible-set / score-reproduction checks only (no gate, no corpus p-value).
  all     = fixture, then gates (seed 5454), masked F1 corpus (seed 5455), summary.
  Each phase is checkpointed in analysis/k054_checkpoint.json; a rerun resumes finished phases unchanged.

QUESTION. Do the published K036 F1 names (frozen D5w, fixed K = 10 000, pooled exchangeable min-p, BH q = 0.05
over pop = 378, 14 names) survive when R5 multi-number cords are masked as in K008? Does any new BH name appear?

DATA. OKR khipu.db @ 4039ca5 (sha256 607913034a0f...c4db), level-1 pendants in CORD_ORDINAL order, duplicate-flagged
khipus removed, cord value = sum of knot values, groups = runs of consecutive pendants sharing CLUSTER_ID (as
K031–K036). Eligible = >= 10 nonzero pendants (457). F1 universe = pop = >= 2 groups of size >= 4 (378), identical
to K036. A pop khipu is TESTABLE if it keeps >= 10 nonzero UNMASKED pendants; otherwise NOT TESTABLE (not lost).
BH is over the testable subset of that same F1 family (not over S0, and not over a redesigned universe).

R5 CORD (K007/K008). >= 2 knot clusters with a single decimal place, and those places, read in knot_cluster.ORDINAL
order, are not strictly decreasing. Expected count in the DB: 3069 (fixture gate).

MASK (K008, structure-preserving). An R5 pendant keeps its position but is never a sum target and never part of a
summand block (any k-block containing an R5 position is invalid). Null N1 = within-khipu permutation of the non-R5
values among the non-R5 positions; group ids stay put (same layout K036 kept). Everything else is frozen: D5w =
per-k log10-weighted within-group exact-sum hits, k = 2..12, target >= 10, block with >= 2 nonzero summands,
windows wholly inside one CLUSTER_ID group; p = pooled exchangeable min-p (K033/K036: stack observed + K null
score-rows, live columns only, p = (# rows whose min-p <= observed min-p) / (K+1)); fixed K = 10 000, no adaptive
cut. No detector redesign; no new holdout is invented.

CORPUS PROCEDURE (as K036 F1, with the mask). For every testable pop khipu: fixed K = 10 000; BH-FDR q = 0.05 over
all testable khipus. Seed 5455. Khipus without any R5 pendant are recomputed with the new seed too (same data, same
statistic, fresh null).

GATES (seed 5454; K = 10 000, the frozen detector's own budget — not the K = 1000 K053 used for D2/D5, and not a
looser bar):
  G0 fixture (stop on failure): DB hash; R5 count == 3069; eligible == 457 and pop == K036's 378 ids; published
     K036 F1 list loads as the 14 reference names; with an all-False mask the masked D5w scores reproduce K036's
     unmasked scores_w for every eligible khipu; with the real mask, R5-free eligible khipus reproduce unmasked
     scores_w.
  G1 calibration FPR: for each testable khipu one masked shuffle treated as real; rate of p <= 0.05. Gate: rate
     <= 0.05 (K053 G1 and K036's alpha = 0.05 FPR; a single-corpus rate cap, not a looser binomial). If G1 fails,
     H1 (survival) and H2 (new candidates) are NOT TESTABLE. Also reported: number of BH flags on the calibration
     p's.
  G2 planted recovery at the adopted corpus_m* = 6 (K039; K036 large m* = 6): on a masked shuffle of each testable
     khipu, six within-group exact-sum windows are inserted with K036's plant_within_m fill rules (A_within /
     B_within with probability 1/2), restricted so target and summands are all non-R5 and contiguous inside one
     group (a block the masked detector can see). Khipus that cannot place all six are skipped (reported). Power =
     rate of p <= 0.05 (K053 G2 metric). Binary gate: power >= 0.50, evaluated only if n_planted >= 30 (K036's
     n >= 30 rule). Failing G2 does not block reporting; it marks the detector UNDERPOWERED. The unmasked K036
     large p<=0.05 rate at m = 6 was 0.9516 and K039's corpus BH-level power was 0.7056; 0.50 is the adopted bar,
     not a lowered one.

DECISION RULES. A published K036 F1 name SURVIVES if BH-significant under masked D5w. A name that drops is NO
LONGER ESTABLISHED (masking cut or weakened the signal, or a BH-boundary Monte-Carlo move), not excluded. Fewer
than 10 nonzero unmasked pendants: NOT TESTABLE. A BH name absent from the original 14 is a NEW CANDIDATE,
reported but not claimed (same-data sensitivity). Same-data caveat: reanalysis of the same pinned corpus, not an
independent replication. No new structure is claimed unless it beats the pre-registered BH rule after gates pass.

SEEDS. 5454 (gates), 5455 (corpus). 5456 is unused (one frozen detector, two phases). Distinct from K053
(5353–5355) and K036 (3630–3632).
"""
import sqlite3, sys, json, time, os, hashlib
import numpy as np
from collections import defaultdict
from math import sqrt

DB, MODE = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'fixture')
SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
CK = 'analysis/k054_checkpoint.json'
OUT = 'analysis/k054_results.json'
K036_PATH = 'analysis/k036_results.json'
SEED_G, SEED_SCAN = 5454, 5455
K = 10000
Q = 0.05
CHUNK = 1000
MINP = 10
M_PLANT = 6
K036_F1 = [
    "KH0322/UR086", "KH0395/UR155", "KH0420/UR182", "KH0428/UR190",
    "KH0478/UR242", "KH0491/UR255", "KH0492/UR256", "KH0502/UR266",
    "KH0504/UR267B", "KH0506/UR269", "KH0507/UR270", "KH0511/UR273B",
    "KH0513/UR274B", "KH0514/UR275",
]
t0 = time.time()
c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute(
    "select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None:
        val[cid] += int(v)

# --- R5 definition, copied verbatim from K008 / K053 ---
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

data = []  # eligible: >= 10 nonzero pendants (unmasked), with groups and R5 mask
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
    data.append((khid, v, gids, sum(1 for s in sizes if s >= 4), bad))

k036 = json.load(open(K036_PATH))
k036_rows = {r['khipu_id']: r for r in k036['rows']}
pop = [d for d in data if d[3] >= 2]
pop_ids = {d[0] for d in pop}
k036_pop_ids = {r['khipu_id'] for r in k036['rows'] if r['stratum'] != 'S0'}
lab = lambda khid: names[khid][0] + '/' + names[khid][1]
testable = [(k, v, g, n4, b) for k, v, g, n4, b in pop if ((v > 0) & ~b).sum() >= MINP]

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
    """Unmasked D5w, copied from K036 (for the G0 reproduction check)."""
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


def scores_w_masked(V, gids, bad):
    """D5w within-group AND R5-masked: R5 never target; any block containing an R5 is invalid."""
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64)
    P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64)
    NZ[:, 1:] = np.cumsum(V > 0, 1)
    BD = np.zeros(n + 1, np.int64)
    BD[1:] = np.cumsum(bad)
    idx = np.arange(n)
    tgt = (V >= 10) & ~bad[None, :]
    w = np.where(tgt, np.log10(np.maximum(V.astype(np.float64), 1)), 0.0)
    W = np.zeros((B, 11))
    vr, vl = valid_masks(gids)
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
        W[:, k - 2] = (w * hk).sum(1)
    return W


def colrank_p(N, x):
    Ns = np.sort(N, 0)
    KK = N.shape[0]
    return np.stack([(KK - np.searchsorted(Ns[:, j], x[:, j] - 1e-9, 'left')) / KK
                     for j in range(N.shape[1])], 1)


def minp_pooled_detail(No, Nn):
    """Return (p, count, denom) under pooled exchangeable min-p (K033/K036)."""
    A = np.vstack([No, Nn])
    live = A.max(0) > 0
    if not live.any():
        return 1.0, int(A.shape[0]), int(A.shape[0])
    A = A[:, live]
    pa = colrank_p(A, A).min(1)
    cnt = int((pa <= pa[0] + 1e-12).sum())
    denom = int(A.shape[0])
    return float(cnt / denom), cnt, denom


def permmask(rng, v, bad, B):
    free = np.where(~bad)[0]
    out = np.tile(v, (B, 1))
    if len(free):
        out[:, free] = v[free][rng.random((B, len(free))).argsort(1)]
    return out


def null_scores_masked(rng, x, gids, bad, KK):
    out = []
    left = KK
    while left > 0:
        m = min(CHUNK, left)
        V = permmask(rng, x, bad, m)
        out.append(scores_w_masked(V, gids, bad))
        left -= m
    return np.vstack(out)


def masked_p(rng, x, gids, bad):
    Wow = scores_w_masked(x[None], gids, bad)
    n5w = null_scores_masked(rng, x, gids, bad, K)
    p, cnt, denom = minp_pooled_detail(Wow, n5w)
    se = sqrt(p * (1.0 - p) / denom) if 0 < p < 1 else 0.0
    return p, cnt, denom, se, float(Wow.sum())


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


def plant_within_m_masked(rng, v, gids, bad, m):
    """K036 plant_within_m on a masked shuffle, only on non-R5 windows the detector can see."""
    pl = permmask(rng, v, bad, 1)[0]
    ranges = group_ranges(gids)
    specs = []
    for _ in range(m):
        spec = 'A_within' if rng.random() < 0.5 else 'B_within'
        specs.append(spec)
        ch = []
        if spec == 'A_within':
            for a, b in ranges:
                if (b - a) < 5:
                    continue
                k = 3
                for st in range(a, b - k):
                    if not bad[st:st + 1 + k].any():
                        ch.append((st, k, True))
        else:
            for a, b in ranges:
                for k in range(2, min(10, b - a - 1) + 1):
                    if b - a < k + 2:
                        continue
                    for st in range(a, b - k):
                        if not bad[st:st + 1 + k].any():
                            ch.append((st, k, True))
                    for st in range(a + k, b):
                        if not bad[st - k:st + 1].any():
                            ch.append((st, k, False))
        if not ch:
            return None, specs
        st, k, right = ch[int(rng.integers(0, len(ch)))]
        if right:
            _fill(rng, pl, slice(st + 1, st + 1 + k), st)
        else:
            _fill(rng, pl, slice(st - k, st), st)
    return pl, specs


# ---------------- G0 fixture ----------------
h = hashlib.sha256(open(DB, 'rb').read()).hexdigest()
rep_empty = rep_r5free = 0
n0 = 0
empty_bad_cache = {}
for khid, v, gids, n4, b in data:
    Wu = scores_w(v[None], gids)
    We = scores_w_masked(v[None], gids, np.zeros(len(v), bool))
    rep_empty += int(np.allclose(Wu, We))
    if not b.any():
        n0 += 1
        Wm = scores_w_masked(v[None], gids, b)
        rep_r5free += int(np.allclose(Wu, Wm))

f1_loaded = list(k036.get('real', {}).get('hits', {}).get('F1') or [])
g0 = dict(
    sha256=h, sha_ok=h == SHA,
    n_r5=len(R5), r5_ok=len(R5) == 3069,
    n_eligible=len(data), eligible_ok=len(data) == 457 and set(k036_rows) == {d[0] for d in data},
    n_pop=len(pop), pop_ok=len(pop) == 378 and pop_ids == k036_pop_ids,
    f1_ref=K036_F1, f1_loaded_ok=f1_loaded == K036_F1,
    scores_empty_mask_reproduces=f'{rep_empty}/{len(data)}',
    scores_zero_r5_reproduces=f'{rep_r5free}/{n0}',
    n_r5free_eligible=n0,
    n_with_r5_pop=int(sum(b.any() for _, _, _, _, b in pop)),
    n_testable=len(testable),
    n_not_testable=len(pop) - len(testable),
    not_testable=[lab(k) for k, v, g, n4, b in pop if ((v > 0) & ~b).sum() < MINP],
)
g0['pass'] = bool(
    g0['sha_ok'] and g0['r5_ok'] and g0['eligible_ok'] and g0['pop_ok'] and g0['f1_loaded_ok']
    and rep_empty == len(data) and rep_r5free == n0
)
print('G0', json.dumps({k: g0[k] for k in g0 if k not in ('not_testable', 'f1_ref')}), flush=True)
if not g0['pass']:
    sys.exit('G0 fixture failed - stop')

if MODE == 'fixture':
    # synthetic smoke of the masked D5w machinery (no real-data p-value)
    r = np.random.default_rng(0)
    v = r.integers(0, 40, 24).astype(np.int64)
    gids = np.array([0] * 8 + [1] * 8 + [2] * 8, np.int32)
    b = np.zeros(24, bool)
    b[[2, 14]] = True
    # plant a visible within-group right-sum at index 8 (group 1), window 9:12, all non-R5
    blk = np.maximum(v[9:12], 1)
    s = int(blk.sum())
    if s < 10:
        blk[0] += 10 - s
        s = int(blk.sum())
    v[9:12] = blk
    v[8] = s
    W = scores_w_masked(v[None], gids, b)
    # same plant but mark the first summand R5: the hit must vanish at that window
    b2 = b.copy()
    b2[9] = True
    W2 = scores_w_masked(v[None], gids, b2)
    print('smoke toy W>0 at k', list(np.where(W[0] > 0)[0] + 2),
          'stat', round(float(W.sum()), 3),
          'R5-in-block stat', round(float(W2.sum()), 3), flush=True)
    sys.exit(0)

ck = json.load(open(CK)) if os.path.exists(CK) else {}

def save():
    json.dump(ck, open(CK, 'w'), indent=1)

ck['G0'] = g0

# ---------------- G1/G2 gates ----------------
if 'gates' not in ck:
    rng = np.random.default_rng(SEED_G)
    cal, pw, skipped = [], [], []
    ts = time.time()
    for j, (khid, v, gids, n4, b) in enumerate(testable):
        x = permmask(rng, v, b, 1)[0]
        p, cnt, denom, se, stat = masked_p(rng, x, gids, b)
        cal.append(p)
        planted, specs = plant_within_m_masked(rng, v, gids, b, M_PLANT)
        if planted is None:
            skipped.append(lab(khid))
        else:
            p2, cnt2, denom2, se2, stat2 = masked_p(rng, planted, gids, b)
            pw.append(p2)
        if (j + 1) % 25 == 0:
            print('gates', j + 1, '/', len(testable), round(time.time() - ts, 1), 's', flush=True)
    cal = np.asarray(cal)
    pw = np.asarray(pw)
    G = dict(
        seed=SEED_G, K=K, m_plant=M_PLANT,
        calib_n=int(len(cal)),
        fpr=float(np.mean(cal <= 0.05)) if len(cal) else None,
        calib_bh_flags=int(bh(cal).sum()) if len(cal) else 0,
        plant_n=int(len(pw)),
        plant_skipped_no_window=skipped,
        power=float(np.mean(pw <= 0.05)) if len(pw) else None,
    )
    G['G1'] = bool(G['fpr'] is not None and G['fpr'] <= 0.05)
    G['G2'] = bool(G['plant_n'] >= 30 and G['power'] is not None and G['power'] >= 0.50)
    G['G2_evaluable'] = bool(G['plant_n'] >= 30)
    G['seconds'] = round(time.time() - t0, 1)
    ck['gates'] = G
    save()
print('gates', json.dumps({k: ck['gates'][k] for k in ck['gates'] if k != 'plant_skipped_no_window'}),
      flush=True)
print('gates skipped', ck['gates']['plant_skipped_no_window'], flush=True)

# ---------------- corpus scan ----------------
if 'F1' not in ck:
    rng = np.random.default_rng(SEED_SCAN)
    rows = []
    ts = time.time()
    for j, (khid, v, gids, n4, b) in enumerate(testable):
        p, cnt, denom, se, stat_m = masked_p(rng, v, gids, b)
        stat_u = float(scores_w(v[None], gids).sum())
        orig = k036_rows[khid]
        rows.append(dict(
            khipu_id=khid, okr=names[khid][0], inv=names[khid][1],
            n_pend=len(v), n_r5=int(b.sum()),
            n_unmasked_nz=int(((v > 0) & ~b).sum()),
            stratum=orig['stratum'],
            stat_D5w_unmasked=stat_u, stat_D5w_masked=stat_m,
            p=p, cnt=cnt, denom=denom, se=se,
            p_orig=orig['p_D5w'], cnt_orig=orig['cnt'],
        ))
        if (j + 1) % 25 == 0:
            print('scan', j + 1, '/', len(testable), round(time.time() - ts, 1), 's', flush=True)
    sig = bh([r['p'] for r in rows])
    for r, s in zip(rows, sig):
        r['bh_sig'] = bool(s)
    ck['F1'] = dict(seed=SEED_SCAN, K=K, rows=rows, seconds=round(time.time() - ts, 1))
    save()
print('F1 done', ck['F1']['seconds'], flush=True)

# ---------------- summary ----------------
rows = {r['khipu_id']: r for r in ck['F1']['rows']}
old = set()
old_ids = {}
for name in K036_F1:
    okr, inv = name.split('/')
    found = None
    for khid, (o, i) in names.items():
        if o == okr and i == inv:
            found = khid
            break
    if found is None:
        raise SystemExit('missing K036 name ' + name)
    old.add(found)
    old_ids[found] = name
new = {k for k, r in rows.items() if r['bh_sig']}
fate = {}
for k in sorted(old, key=lambda k: names[k][0]):
    if k not in rows:
        fate[old_ids[k]] = 'not testable'
    else:
        fate[old_ids[k]] = 'survives' if rows[k]['bh_sig'] else 'no longer established'
detail = []
for k in sorted(old, key=lambda k: names[k][0]):
    name = old_ids[k]
    r = rows.get(k)
    detail.append(dict(
        name=name,
        n_r5=None if r is None else r['n_r5'],
        stratum=None if r is None else r['stratum'],
        stat_unmasked=None if r is None else r['stat_D5w_unmasked'],
        stat_masked=None if r is None else r['stat_D5w_masked'],
        p_orig=k036_rows[k]['p_D5w'],
        p_masked=None if r is None else r['p'],
        cnt_masked=None if r is None else r['cnt'],
        fate=fate[name],
    ))
ps = [r['p'] for r in ck['F1']['rows']]
o = np.argsort(ps)
m = len(ps)
thr = Q * np.arange(1, m + 1) / m
ok = np.asarray(ps)[o] <= thr
kk = int(np.max(np.where(ok)[0]) + 1) if ok.any() else 0
bar = float(thr[kk - 1]) if kk else None
G = ck['gates']
gate_ok = G['G1']
summary = dict(
    detector='D5w_F1',
    n_tested=len(rows),
    n_bh=len(new),
    orig_n_bh=len(old),
    bh_bar_at_rank=bar,
    bh_rank=kk,
    survive=sum(v == 'survives' for v in fate.values()),
    lost=sum(v == 'no longer established' for v in fate.values()),
    not_testable=sum(v == 'not testable' for v in fate.values()),
    new_candidates=sorted(lab(k) for k in new - old),
    gate_G1=gate_ok,
    gate_G2=G['G2'],
    verdict=('H1/H2 NOT TESTABLE (G1 failed)' if not gate_ok else
             ('UNDERPOWERED (G2 failed)' if not G['G2'] else 'gates pass')),
    names=detail,
)
out = dict(
    cycle='K054',
    db=f'OKR khipu.db @ 4039ca5 sha256 {h}',
    design=dict(K=K, q=Q, seeds=dict(gates=SEED_G, scan=SEED_SCAN, unused=5456),
                m_plant=M_PLANT, p_construction='pooled_exchangeable (K033/K036)',
                mask='K008 structure-preserving R5',
                family='K036 F1 pop, testable after mask',
                same_data_caveat=True),
    G0=ck['G0'],
    gates=ck['gates'],
    summary=summary,
    rows=ck['F1']['rows'],
    seconds_total_this_run=round(time.time() - t0, 1),
)
json.dump(out, open(OUT, 'w'), indent=1, default=str)
print(json.dumps({k: summary[k] for k in summary if k != 'names'}, indent=1))
for r in detail:
    print('F1', r)
print('seconds', round(time.time() - t0, 1), flush=True)
