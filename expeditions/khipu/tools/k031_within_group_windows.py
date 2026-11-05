#!/usr/bin/env python3
"""K031 - D5 vs D5w (within-group windows) on large multi-group khipus.
Pre-registered in case-file/K031-within-group-windows.md.
Usage: python3 tools/k031_within_group_windows.py khipu.db
"""
import sqlite3, sys, json, time, math
import numpy as np
from collections import defaultdict
from math import comb

t0 = time.time()
DB = sys.argv[1]
KMAX = 12
TCAP = 270  # seconds per stage

c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute(
    "select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None:
        val[cid] += int(v)
kh = defaultdict(list)  # list of (cluster_id, value)
for khid, cid, cl in c.execute(
        "select KHIPU_ID, CORD_ID, CLUSTER_ID from cord "
        "where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups:
        continue
    kh[khid].append((cl, val.get(cid, 0)))

data = []  # (khid, values ndarray, gids ndarray, n_groups_ge4)
for khid, cords in kh.items():
    v = np.array([x[1] for x in cords], np.int64)
    if (v > 0).sum() < 10:
        continue
    # consecutive same CLUSTER_ID -> group index 0..G-1
    gids = np.empty(len(cords), np.int32)
    gi = -1
    last = object()
    sizes = []
    for i, (cl, _) in enumerate(cords):
        if cl != last:
            gi += 1
            last = cl
            sizes.append(0)
        gids[i] = gi
        sizes[-1] += 1
    n_ge4 = sum(1 for s in sizes if s >= 4)
    data.append((khid, v, gids, n_ge4, len(sizes)))

# Primary population: >=2 groups of size >=4; largest third by pendant count
pop = [(k, v, g, n4, ng) for k, v, g, n4, ng in data if n4 >= 2]
pop_sizes = np.array([len(v) for _, v, _, _, _ in pop])
t1, t2 = np.quantile(pop_sizes, [1 / 3, 2 / 3]) if len(pop) else (0, 0)
large_ids = {k for k, v, _, _, _ in pop if len(v) > t2}
mid_ids = {k for k, v, _, _, _ in pop if t1 < len(v) <= t2}
small_ids = {k for k, v, _, _, _ in pop if len(v) <= t1}
print(json.dumps(dict(
    n_eligible=len(data), n_pop=len(pop), n_large=len(large_ids),
    size_thirds=[float(t1), float(t2)],
)), flush=True)


def window_ok(gids, i, k, right):
    """True iff anchor i and its k-window share one group id."""
    g = gids[i]
    if right:
        if i + k >= len(gids):
            return False
        return bool(np.all(gids[i: i + k + 1] == g))
    else:
        if i - k < 0:
            return False
        return bool(np.all(gids[i - k: i + 1] == g))


def scores(V, gids=None, within=False):
    """V (B,n) -> (B,11) per-k log10-weighted hit scores. If within, require same group."""
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64)
    P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64)
    NZ[:, 1:] = np.cumsum(V > 0, 1)
    idx = np.arange(n)
    big = V >= 10
    w = np.where(big, np.log10(np.maximum(V.astype(np.float64), 1)), 0.0)
    W = np.zeros((B, 11))
    # precompute valid anchors per k,side when within
    valid_r = valid_l = None
    if within:
        valid_r = [None] * 13
        valid_l = [None] * 13
        for k in range(2, 13):
            vr = np.array([window_ok(gids, i, k, True) for i in range(n)], bool)
            vl = np.array([window_ok(gids, i, k, False) for i in range(n)], bool)
            valid_r[k] = vr
            valid_l[k] = vl
    for k in range(2, 13):
        hk = np.zeros((B, n), bool)
        i = idx[idx + k < n]
        if within:
            i = i[valid_r[k][i]]
        if len(i):
            hk[:, i] |= ((P[:, i + k + 1] - P[:, i + 1]) == V[:, i]) & (
                (NZ[:, i + k + 1] - NZ[:, i + 1]) >= 2)
        i = idx[idx - k >= 0]
        if within:
            i = i[valid_l[k][i]]
        if len(i):
            hk[:, i] |= ((P[:, i] - P[:, i - k]) == V[:, i]) & (
                (NZ[:, i] - NZ[:, i - k]) >= 2)
        hk &= big
        W[:, k - 2] = (w * hk).sum(1)
    return W


def colrank_p(N, x):
    Ns = np.sort(N, 0)
    K = N.shape[0]
    return np.stack([
        (K - np.searchsorted(Ns[:, j], x[:, j] - 1e-9, 'left')) / K
        for j in range(N.shape[1])
    ], 1)


def pvals_pair(obs_V, null_V, gids):
    """Return dict D5, D5w p-values; shared null draws; gids fixed."""
    Wo = scores(obs_V[None], within=False)
    Wn = scores(null_V, within=False)
    Wow = scores(obs_V[None], gids=gids, within=True)
    Wnw = scores(null_V, gids=gids, within=True)
    K = len(null_V)
    out = {}
    for name, No, Nn in (('D5', Wo, Wn), ('D5w', Wow, Wnw)):
        live = (Nn.max(0) > 0) | (No[0] > 0)
        if not live.any():
            out[name] = 1.0
            continue
        Nn2, No2 = Nn[:, live], No[:, live]
        pn = colrank_p(Nn2, Nn2).min(1)
        po = colrank_p(Nn2, No2).min(1)[0]
        out[name] = (1 + (pn <= po + 1e-12).sum()) / (1 + K)
    return out


def perm(rng, v, B):
    return np.array([rng.permutation(v) for _ in range(B)])


def group_ranges(gids):
    n = len(gids)
    ranges = []
    i = 0
    while i < n:
        j = i
        while j < n and gids[j] == gids[i]:
            j += 1
        ranges.append((i, j))
        i = j
    return ranges


def plant_unrestricted(rng, v, spec):
    """K003 plant code, unchanged (spec 'A' or 'B')."""
    pl = rng.permutation(v).copy()
    n = len(pl)
    for _ in range(2):
        k = 3 if spec == 'A' else int(rng.integers(2, 11))
        if n < k + 2:
            return None
        right = spec == 'A' or rng.random() < 0.5
        st = int(rng.integers(0, n - k)) if right else int(rng.integers(k, n))
        sl = slice(st + 1, st + 1 + k) if right else slice(st - k, st)
        blk = pl[sl]
        if (blk > 0).sum() < 2:
            blk[:] = np.maximum(blk, rng.integers(1, 30, len(blk)))
        s = int(blk.sum())
        if s < 10:
            blk[0] += 10 - s
            s = int(blk.sum())
        pl[sl] = blk
        pl[st] = s
    return pl


def plant_within(rng, v, gids, spec):
    """Two within-group planted sum cords. spec 'A_within' (k=3) or 'B_within'."""
    pl = rng.permutation(v).copy()
    ranges = group_ranges(gids)
    for _ in range(2):
        if spec == 'A_within':
            k_choices = [(a, b, 3) for a, b in ranges if (b - a) >= 3 + 2]
        else:
            k_choices = []
            for a, b in ranges:
                glen = b - a
                kmax = min(10, glen - 1)
                for k in range(2, kmax + 1):
                    if glen >= k + 2:
                        k_choices.append((a, b, k))
        if not k_choices:
            return None
        a, b, k = k_choices[int(rng.integers(0, len(k_choices)))]
        right = True if spec == 'A_within' else (rng.random() < 0.5)
        if right:
            # st in [a, b-k-1]
            st = int(rng.integers(a, b - k))
            sl = slice(st + 1, st + 1 + k)
        else:
            st = int(rng.integers(a + k, b))
            sl = slice(st - k, st)
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


def mcnemar(a_hits, b_hits):
    """Exact two-sided McNemar; a_hits/b_hits boolean arrays of equal length."""
    a = np.asarray(a_hits, bool)
    b = np.asarray(b_hits, bool)
    n10 = int((a & ~b).sum())
    n01 = int((~a & b).sum())
    nd = n10 + n01
    if nd == 0:
        return 1.0, n10, n01
    p = min(1.0, 2 * sum(comb(nd, i) for i in range(min(n10, n01) + 1)) / (2 ** nd))
    return p, n10, n01


def rate(lst):
    return float(np.mean([p <= 0.05 for p in lst])) if lst else float('nan')


def stage(seed, K):
    rng = np.random.default_rng(seed)
    # rec[det][lab] -> list of (khid, p)
    rec = {d: defaultdict(list) for d in ('D5', 'D5w')}
    ts = time.time()
    done = 0
    for khid, v, gids, n4, ng in data:
        tests = [('calib', rng.permutation(v))]
        for lab, fn, arg in (
            ('A_within', plant_within, 'A_within'),
            ('B_within', plant_within, 'B_within'),
            ('A', plant_unrestricted, 'A'),
            ('B', plant_unrestricted, 'B'),
        ):
            if lab.endswith('within'):
                x = fn(rng, v, gids, arg)
            else:
                if len(v) < 20:
                    x = None
                else:
                    x = fn(rng, v, arg)
            tests.append((lab, x))
        nulls_cache = {}
        for lab, x in tests:
            if x is None:
                continue
            # shared null draws for this observed sequence
            key = id(x)
            if key not in nulls_cache:
                nulls_cache[key] = perm(rng, x, K)
            p = pvals_pair(x, nulls_cache[key], gids)
            for d in ('D5', 'D5w'):
                rec[d][lab].append((khid, p[d]))
        done += 1
        if done % 50 == 0:
            print('seed', seed, 'khipu', done, round(time.time() - t0, 1), flush=True)
        if time.time() - ts > TCAP:
            print('time cap at', done, flush=True)
            break
    return rec, done


def summarise(rec, done):
    out = {}
    for d, labs in rec.items():
        out[d] = {}
        for lab, pairs in labs.items():
            ps = [p for _, p in pairs]
            out[d][lab] = dict(n=len(ps), rate_p05=round(rate(ps), 4))
            # stratum splits for primary population
            for tag, idset in (('large', large_ids), ('mid', mid_ids),
                               ('small', small_ids), ('pop', large_ids | mid_ids | small_ids)):
                sub = [p for kid, p in pairs if kid in idset]
                out[d][f'{lab}_{tag}'] = dict(n=len(sub), rate_p05=round(rate(sub), 4))
    out['khipus_reached'] = done
    return out


print('dev starting', flush=True)
dev_rec, ndev = stage(3130, 300)
dev = summarise(dev_rec, ndev)
print('dev', json.dumps({d: {k: v for k, v in labs.items() if not k.endswith(('_large', '_mid', '_small', '_pop'))}
                         for d, labs in dev.items() if d in ('D5', 'D5w')}, indent=1), flush=True)

print('eval starting', flush=True)
ev_rec, nev = stage(3131, 500)
ev = summarise(ev_rec, nev)

# Primary decision on large stratum, A_within + B_within pooled McNemar
def hits(rec, det, lab, idset):
    return np.array([p <= 0.05 for kid, p in rec[det][lab] if kid in idset], bool)

a_w = np.concatenate([hits(ev_rec, 'D5w', 'A_within', large_ids),
                      hits(ev_rec, 'D5w', 'B_within', large_ids)])
b_w = np.concatenate([hits(ev_rec, 'D5', 'A_within', large_ids),
                      hits(ev_rec, 'D5', 'B_within', large_ids)])
# align lengths: both built from same plant list order
# rebuild paired from shared keys
def paired_hits(rec, lab, idset):
    d5 = {kid: p for kid, p in rec['D5'][lab] if kid in idset}
    d5w = {kid: p for kid, p in rec['D5w'][lab] if kid in idset}
    keys = sorted(set(d5) & set(d5w))
    return (np.array([d5w[k] <= 0.05 for k in keys], bool),
            np.array([d5[k] <= 0.05 for k in keys], bool), keys)

aw, a5, _ = paired_hits(ev_rec, 'A_within', large_ids)
bw, b5, _ = paired_hits(ev_rec, 'B_within', large_ids)
d5w_hits = np.concatenate([aw, bw])
d5_hits = np.concatenate([a5, b5])
mc, n10, n01 = mcnemar(d5w_hits, d5_hits)

mean_d5w = (ev['D5w']['A_within_large']['rate_p05'] + ev['D5w']['B_within_large']['rate_p05']) / 2
mean_d5 = (ev['D5']['A_within_large']['rate_p05'] + ev['D5']['B_within_large']['rate_p05']) / 2
gain = mean_d5w - mean_d5
fpr_d5w = ev['D5w']['calib_large']['rate_p05']
adopted = bool(fpr_d5w <= 0.05 and gain >= 0.03 and mc < 0.05)
k003_bar = bool(
    ev['D5w']['A_within_large']['rate_p05'] >= 0.80
    and ev['D5w']['B_within_large']['rate_p05'] >= 0.60)

res = dict(
    n_eligible=len(data),
    n_pop=len(pop),
    n_large=len(large_ids),
    size_thirds=[float(t1), float(t2)],
    dev=dev,
    eval=ev,
    primary=dict(
        stratum='largest_third_of_pop',
        fpr_D5w=fpr_d5w,
        fpr_D5=ev['D5']['calib_large']['rate_p05'],
        A_within_D5w=ev['D5w']['A_within_large']['rate_p05'],
        B_within_D5w=ev['D5w']['B_within_large']['rate_p05'],
        A_within_D5=ev['D5']['A_within_large']['rate_p05'],
        B_within_D5=ev['D5']['B_within_large']['rate_p05'],
        mean_D5w=round(mean_d5w, 4),
        mean_D5=round(mean_d5, 4),
        gain=round(gain, 4),
        d5w_only=n10,
        d5_only=n01,
        mcnemar_p=mc,
        adopted=adopted,
        k003_bar_met=k003_bar,
        n_A=int(len(aw)),
        n_B=int(len(bw)),
    ),
    secs=round(time.time() - t0, 1),
)
json.dump(res, open('analysis/k031_results.json', 'w'), indent=1, default=float)
print(json.dumps(res['primary'], indent=1, default=float))
print('secs', res['secs'], 'adopted', adopted, flush=True)
