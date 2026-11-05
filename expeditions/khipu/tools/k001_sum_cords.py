#!/usr/bin/env python3
"""K001 - Do adjacent 'sum cords' occur more often than a calibrated null predicts?
Pre-registered in case-file/K001. Input: OKR data/khipu.db (sha256 recorded in data/MANIFEST.md).
Cord value = sum of knot.knot_value_type over the cord's knots (the database's own per-knot decoding).
Statistic S(khipu) = number of level-1 pendants c with value v>=10 such that, for some k in 2..12, the k pendants
immediately to the right of c, or immediately to the left, sum to v and at least 2 of them are nonzero.
Nulls: N1 = permute pendant values within khipu; N2 = permute the order of whole cord groups (keeps within-group order).
p = (1 + #null >= obs) / (1 + K). BH-FDR across khipus at q=0.05.
Controls: (a) calibration: shuffled khipus treated as observed -> false-positive rate at alpha=0.05;
(b) planted: shuffled khipus with 2 planted sum cords (cord := sum of next 3) -> recovery rate."""
import sqlite3, json, sys, numpy as np
from collections import defaultdict
DB = sys.argv[1] if len(sys.argv) > 1 else 'khipu.db'
K = int(sys.argv[2]) if len(sys.argv) > 2 else 500; KMAX = 12; SEED = 20261104; MINP = 10
rng = np.random.default_rng(SEED)
c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
kh = defaultdict(list)
for khid, cid, cl, ordn in c.execute("select KHIPU_ID, CORD_ID, CLUSTER_ID, CORD_ORDINAL from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups: continue
    kh[khid].append((cid, cl, val.get(cid, 0)))

def S_batch(V):  # V: (B, n) int64
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    hit = np.zeros((B, n), bool); idx = np.arange(n)
    for k in range(2, KMAX + 1):
        # right block: c+1 .. c+k
        ok = idx + k < n; i = idx[ok]
        s = P[:, i + k + 1] - P[:, i + 1]; z = NZ[:, i + k + 1] - NZ[:, i + 1]
        hit[:, i] |= (s == V[:, i]) & (z >= 2)
        ok = idx - k >= 0; i = idx[ok]
        s = P[:, i] - P[:, i - k]; z = NZ[:, i] - NZ[:, i - k]
        hit[:, i] |= (s == V[:, i]) & (z >= 2)
    hit &= V >= 10
    return hit.sum(1)

def n1(v, B): return np.array([rng.permutation(v) for _ in range(B)])
def n2(groups, B):
    out = []
    for _ in range(B):
        o = rng.permutation(len(groups)); out.append(np.concatenate([groups[j] for j in o]))
    return np.array(out)
def pval(obs, null): return (1 + (null >= obs).sum()) / (1 + len(null))
def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps); o = np.argsort(ps); thr = q * np.arange(1, m + 1) / m
    passed = ps[o] <= thr; kmax = np.max(np.where(passed)[0]) + 1 if passed.any() else 0
    sig = np.zeros(m, bool); sig[o[:kmax]] = True; return sig

rows = []
for khid, cords in kh.items():
    v = np.array([x[2] for x in cords], np.int64)
    if (v > 0).sum() < MINP: continue
    gi = []; last = object()
    for x in cords:
        if x[1] != last: gi.append([]); last = x[1]
        gi[-1].append(x[2])
    groups = [np.array(g, np.int64) for g in gi]
    obs = int(S_batch(v[None])[0])
    s1 = S_batch(n1(v, K)); p1 = pval(obs, s1)
    p2 = pval(obs, S_batch(n2(groups, K))) if len(groups) >= 4 else None
    # calibration: one shuffled copy as 'observed'
    fake = rng.permutation(v); pc = pval(int(S_batch(fake[None])[0]), S_batch(n1(fake, K)))
    # planted control (needs room)
    pp = None
    if len(v) >= 20:
        pl = rng.permutation(v).copy()
        for st in rng.choice(np.arange(0, len(v) - 4), 2, replace=False):
            blk = pl[st + 1: st + 4]
            if (blk > 0).sum() < 2: blk[:] = np.maximum(blk, rng.integers(1, 30, 3))
            pl[st + 1: st + 4] = blk; pl[st] = blk.sum() if blk.sum() >= 10 else blk.sum() + 10
            if pl[st] != blk.sum(): pl[st + 1] += pl[st] - blk.sum()
        pp = pval(int(S_batch(pl[None])[0]), S_batch(n1(pl, K)))
    rows.append(dict(khipu_id=khid, okr=names[khid][0], inv=names[khid][1], n_pend=len(v), n_nonzero=int((v > 0).sum()),
                     n_groups=len(groups), S_obs=obs, S_null_mean=float(s1.mean()), p_N1=p1, p_N2=p2, p_calib=pc, p_planted=pp))
ps = [r['p_N1'] for r in rows]; sig = bh(ps)
for r, s in zip(rows, sig): r['bh_sig_N1'] = bool(s)
r2 = [r for r in rows if r['p_N2'] is not None]; sig2 = bh([r['p_N2'] for r in r2])
for r, s in zip(r2, sig2): r['bh_sig_N2'] = bool(s)
calib = np.array([r['p_calib'] for r in rows]); plant = np.array([r['p_planted'] for r in rows if r['p_planted'] is not None])
summary = dict(n_khipus=len(rows), K=K, seed=SEED, calib_fpr_05=float((calib <= 0.05).mean()), calib_bh_sig=int(bh(calib).sum()),
               planted_power_05=float((plant <= 0.05).mean()), planted_n=len(plant),
               n_p05_N1=int((np.array(ps) <= 0.05).sum()), n_bh_N1=int(sig.sum()),
               n_tested_N2=len(r2), n_p05_N2=int(sum(r['p_N2'] <= 0.05 for r in r2)), n_bh_N2=int(sig2.sum()),
               total_S_obs=int(sum(r['S_obs'] for r in rows)), total_S_null=float(sum(r['S_null_mean'] for r in rows)))
json.dump(dict(summary=summary, rows=rows), open(f'analysis/k001_results_K{K}.json', 'w'), indent=1)
print(json.dumps(summary, indent=1))
top = sorted(rows, key=lambda r: (r['p_N1'], -r['S_obs']))[:15]
for r in top: print(r['okr'], r['inv'], r['n_pend'], r['S_obs'], round(r['S_null_mean'], 2), r['p_N1'], r['p_N2'])
