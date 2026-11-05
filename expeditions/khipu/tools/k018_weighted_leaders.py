#!/usr/bin/env python3
"""K018 - information-weighted group-leader LCS over all pairs; leader-order shuffle max-statistic null; held-out calibration; planted ordered copies. Pre-registered in case-file/K018-weighted-leaders.md.
Usage: python3 tools/k018_weighted_leaders.py data/khipu.db  (compiles tools/k016_wlcs.c with gcc)"""
import sqlite3, json, sys, time, math, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); c = sqlite3.connect(sys.argv[1]); rng = np.random.default_rng(20181105); NNULL, NPLANT, CAP = 40, 200, 300
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
meta = {r[0]: dict(okr=r[1] or '', inv=r[2] or '', museum=(r[3] or '').strip(), mnum=(r[4] or '').strip())
        for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM, MUSEUM_NAME, MUSEUM_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
# --- R5 cords (K007 definition) ---
def place_(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
clpl = defaultdict(set); clcd = {}
for cid_, cl_, t_, v_ in c.execute("select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
    t_ = (t_ or '').strip()
    if t_ in ('S', 'L', 'E') and v_: clpl[cl_].add(place_(int(v_)) if t_ == 'S' else 0)
    clcd[cl_] = cid_
ordn_ = {r[0]: r[1] for r in c.execute("select CLUSTER_ID, ORDINAL from knot_cluster")}
bc_ = defaultdict(dict)
for cl_, pl_ in clpl.items():
    if len(pl_) == 1 and ordn_.get(cl_) is not None: bc_[clcd[cl_]][ordn_[cl_]] = next(iter(pl_))
R5 = {cd for cd, d in bc_.items() if len(d) >= 2 and not all(a > b for a, b in zip([d[o] for o in sorted(d)], [d[o] for o in sorted(d)][1:]))}
print('R5 cords', len(R5), flush=True)
from math import comb, factorial
from itertools import combinations
kh = defaultdict(list); grp = defaultdict(list)
for khid, cid, cl in c.execute("select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups: continue
    v = 0 if cid in R5 else val.get(cid, 0); kh[khid].append(v)
    if not grp[khid] or grp[khid][-1][0] != cl: grp[khid].append([cl, []])
    grp[khid][-1][1].append(v)
ids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]; N = len(ids); M = N * (N - 1) // 2
def leaders(k): return [g[1][0] for g in grp[k] if len(g[1]) >= 5 and g[1][0] > 0]
LD = {k: leaders(k) for k in ids}
def lcs(a, b):
    d = [0] * (len(b) + 1)
    for x in a:
        p = 0
        for j, y in enumerate(b):
            t = d[j + 1]; d[j + 1] = p + 1 if x == y else max(d[j + 1], d[j]); p = t
    return d[-1]
byokr = {meta[k]['okr']: k for k in ids}
import ctypes, subprocess, os
SO = '/tmp/k018_wlcs.so'; subprocess.run(['gcc', '-O3', '-shared', '-fPIC', '-o', SO, os.path.join(os.path.dirname(__file__), 'k016_wlcs.c')], check=True)
lib = ctypes.CDLL(SO); dp = ctypes.POINTER(ctypes.c_double); ip = ctypes.POINTER(ctypes.c_int); lp = ctypes.POINTER(ctypes.c_longlong)
lf = Counter(x for k in ids for x in LD[k]); lt = sum(lf.values()); WL = {v: -math.log2(n / lt) for v, n in lf.items()}
print('leaders', lt, 'distinct', len(lf), flush=True)
def allW(S):
    L = np.array([len(s) for s in S], np.int32); off = np.concatenate([[0], np.cumsum(L)[:-1]]).astype(np.int32)
    v = np.array([x for s in S for x in s], np.int64); w = np.array([WL[int(x)] for x in v], np.float64); out = np.zeros(M)
    lib.wlcs_all(N, off.ctypes.data_as(ip), L.ctypes.data_as(ip), v.ctypes.data_as(lp), w.ctypes.data_as(dp), out.ctypes.data_as(dp)); return out
base = [list(LD[k]) for k in ids]
def nullc(): return [list(rng.permutation(s)) if len(s) > 1 else list(s) for s in base]
AI, BI = np.triu_indices(N, 1)
def pidx(a, b):
    a, b = min(a, b), max(a, b); return a * N - a * (a + 1) // 2 + (b - a - 1)
obs = allW(base)
mx = []
for r in range(100):
    mx.append(allW(nullc()).max())
    if r % 25 == 24: print(' null', r + 1, round(time.time() - t0), flush=True)
TW = float(np.percentile(mx, 95)); print('T_W', TW, flush=True)
held = [int((allW(nullc()) > TW).any()) for _ in range(20)]; calib = sum(held) <= 3; print('held', sum(held), flush=True)
elig = [i for i in range(N) if len(base[i]) >= 12]; found = 0
for t in range(50):
    a, b = rng.choice(elig, 2, replace=False); S = [list(s) for s in base]
    ia = np.sort(rng.choice(len(S[a]), 10, replace=False)); ib = np.sort(rng.choice(len(S[b]), 10, replace=False))
    for x, y in zip(ia, ib): S[b][y] = S[a][x]
    found += int(allW(S)[pidx(a, b)] > TW)
print('plants', found, round(time.time() - t0), flush=True)
known = {frozenset(p) for p in [('KH0240','KH0496'),('KH0362','KH0049'),('KH0128','KH0137'),('KH0140','KH0483'),('KH0305','KH0301'),('KH0304','KH0303')]}
disc = sorted([(float(obs[p]), meta[ids[AI[p]]]['okr'], meta[ids[BI[p]]]['okr'], len(base[AI[p]]), len(base[BI[p]])) for p in np.flatnonzero(obs > TW)], reverse=True)
named = {}
for a, b in [('KH0097', 'KH0586'), ('KH0192', 'KH0470')]:
    w_ = float(obs[pidx(ids.index(byokr[a]), ids.index(byokr[b]))]); named[f'{a}/{b}'] = dict(W=w_, CONFIRMED=bool(calib and w_ > TW))
res = dict(T_W=TW, null_max=dict(min=float(min(mx)), median=float(np.median(mx)), max=float(max(mx))), heldout_with_discovery=sum(held), calibrated=calib,
           plants_found=found, plants=50, named=named, n_disc=len(disc), discoveries=[dict(W=d[0], A=d[1], B=d[2], nA=d[3], nB=d[4], known=frozenset(d[1:3]) in known) for d in disc[:40]],
           sec=round(time.time() - t0, 1))
json.dump(res, open('analysis/k018_results.json', 'w'), indent=1); print(json.dumps(res)[:4000])
