#!/usr/bin/env python3
"""K025 - whole-group sums: a pendant (value >= 10) equal to the sum of the whole adjacent cord group (>= 2 cords,
>= 2 nonzero). Pre-registered in case-file/K025 (commit 85389cf3). Null: permute pendant values within khipu."""
import sqlite3, json, time, numpy as np
from collections import defaultdict
t0 = time.time(); c = sqlite3.connect('../khipu.db'); rng = np.random.default_rng(20261111); R = 20000; NC = 200
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
kh = defaultdict(list)
for khid, cid, cl in c.execute("select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: kh[khid].append((val.get(cid, 0), cl))
def groups_of(cl):
    g = []; last = object()
    for i, x in enumerate(cl):
        if x != last: g.append([i, i + 1]); last = x
        else: g[-1][1] = i + 1
    return [(s, e) for s, e in g]
def prep(cl, n):
    pairs = []  # (pendant index, s, e)
    for s, e in groups_of(cl):
        if e - s < 2: continue
        if s - 1 >= 0: pairs.append((s - 1, s, e))
        if e < n: pairs.append((e, s, e))
    return np.array(pairs, np.int64).reshape(-1, 3)
def G(V, pr):  # V (B,n)
    if len(pr) == 0: return np.zeros(V.shape[0], np.int64)
    B, n = V.shape; P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    Z = np.zeros((B, n + 1), np.int64); Z[:, 1:] = np.cumsum(V > 0, 1)
    i, s, e = pr[:, 0], pr[:, 1], pr[:, 2]; vi = V[:, i]
    hit = (vi >= 10) & (vi == P[:, e] - P[:, s]) & ((Z[:, e] - Z[:, s]) >= 2)
    H = np.zeros((B, n), bool)
    for k in range(len(pr)): H[:, i[k]] |= hit[:, k]
    return H.sum(1)
def perm(v, B): return v[np.argsort(rng.random((B, len(v))), 1)]
def pv(o, nl): return float((1 + (nl >= o).sum()) / (1 + len(nl)))
def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps); o = np.argsort(ps); ok = ps[o] <= q * np.arange(1, m + 1) / m
    kk = np.max(np.where(ok)[0]) + 1 if ok.any() else 0; s = np.zeros(m, bool); s[o[:kk]] = True; return s
def plant(v, pr):
    x = rng.permutation(v).copy(); i, s, e = pr[rng.integers(len(pr))]
    blk = x[s:e]
    if (blk > 0).sum() < 2: blk[:2] = np.maximum(blk[:2], rng.integers(1, 30, 2))
    if blk.sum() < 10: blk[0] += 10 - blk.sum()
    x[s:e] = blk; x[i] = blk.sum(); return x
res = dict(seed=20261111, R=R, primary={}, secondary={})
byokr = {names[k][0]: k for k in kh}
for okr in ('KH0359', 'KH0405'):
    k = byokr[okr]; v = np.array([x[0] for x in kh[k]], np.int64); pr = prep([x[1] for x in kh[k]], len(v))
    o = int(G(v[None], pr)[0]); nl = G(perm(v, R), pr); p = pv(o, nl)
    cal = sum(pv(int(G(rng.permutation(v)[None], pr)[0]), nl) <= 0.025 for _ in range(NC)) / NC
    pw = sum(pv(int(G(plant(v, pr)[None], pr)[0]), nl) <= 0.025 for _ in range(NC)) / NC
    res['primary'][okr] = dict(inv=names[k][1], n_pend=len(v), n_groups=len(groups_of([x[1] for x in kh[k]])), n_candidate_pairs=len(pr),
                               G=o, null_mean=float(nl.mean()), p=p, calib_fpr=cal, power_1planted=pw,
                               verdict='supported' if p <= 0.025 else 'not supported' if pw >= 0.5 else 'not testable')
print(json.dumps(res['primary'], indent=1), round(time.time() - t0, 1), flush=True)
rows = []; tot_o = 0; tot_n = np.zeros(5000, np.int64); cal_p = []
for k, cords in kh.items():
    cl = [x[1] for x in cords]
    if len(groups_of(cl)) < 4: continue
    v = np.array([x[0] for x in cords], np.int64); pr = prep(cl, len(v))
    if len(pr) == 0 or (v >= 10).sum() == 0: continue
    o = int(G(v[None], pr)[0]); nl = G(perm(v, 5000), pr); tot_o += o; tot_n += nl
    cal_p.append(pv(int(G(rng.permutation(v)[None], pr)[0]), nl))
    rows.append(dict(okr=names[k][0], inv=names[k][1], G=o, null_mean=float(nl.mean()), p=pv(o, nl)))
sig = bh([r['p'] for r in rows])
for r, s in zip(rows, sig): r['bh'] = bool(s)
res['secondary'] = dict(n_khipus=len(rows), R_per_khipu=5000, G_total=tot_o, null_total_mean=float(tot_n.mean()), p_corpus=pv(tot_o, tot_n),
                        n_bh=int(sig.sum()), calib_bh_false=int(bh(cal_p).sum()), calib_fpr_05=float(np.mean(np.array(cal_p) <= 0.05)),
                        bh_khipus=[r for r in rows if r['bh']], top=sorted(rows, key=lambda r: r['p'])[:12])
res['runtime_s'] = round(time.time() - t0, 1)
json.dump(res, open('analysis/k025_results.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in res['secondary'].items() if k != 'top'}, indent=1)); print(res['runtime_s'])
for r in res['secondary']['top']: print(r)
