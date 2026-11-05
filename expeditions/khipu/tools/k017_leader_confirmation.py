#!/usr/bin/env python3
"""K017 - group-leader LCS confirmation of KH0097/KH0586 (pre-registered in case-file/K017-paris-lima-confirmation.md).
Usage: python3 tools/k017_leader_confirmation.py data/khipu.db  (compiles tools/k016_wlcs.c with gcc)"""
import sqlite3, json, sys, time, math, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); c = sqlite3.connect(sys.argv[1]); rng = np.random.default_rng(20171105); NNULL, NPLANT, CAP = 40, 200, 300
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
A, B = LD[byokr['KH0097']], LD[byokr['KH0586']]; Tobs = lcs(A, B)
print('A', A); print('B', B); print('T_obs', Tobs, flush=True)
# test 1: Monte Carlo permutations of B
Bn = np.array(B); mc = 0; R = 10**6
lens = []
for r in range(R):
    if r and r % 200000 == 0: print(' mc', r, mc, round(time.time() - t0), flush=True)
    if lcs(A, list(rng.permutation(Bn))) >= Tobs: mc += 1
# conservative exact union bound for multisets: sum over |J|=T positions of permuted B and |I|=T subsequences of A
cnt = Counter(B); n = len(B)
def rec(i, depth, used, prob):
    if depth == Tobs: return prob
    s = 0.0
    for k in range(i, len(A) - (Tobs - depth) + 1):
        v = A[k]; r_ = cnt[v] - used.get(v, 0)
        if r_ <= 0: continue
        used[v] = used.get(v, 0) + 1; s += rec(k + 1, depth + 1, used, prob * r_ / (n - depth)); used[v] -= 1
    return s
pbound = comb(n, Tobs) * rec(0, 0, {}, 1.0)
# test 2: corpus null, all pairs
allT = []; t1 = time.time()
for i in range(N):
    a = LD[ids[i]]
    for j in range(i + 1, N): allT.append((lcs(a, LD[ids[j]]), meta[ids[i]]['okr'], meta[ids[j]]['okr']))
allT.sort(reverse=True); print('all pairs', len(allT), round(time.time() - t1), 's', flush=True)
known = {frozenset(p) for p in [('KH0240','KH0496'),('KH0362','KH0049'),('KH0128','KH0137'),('KH0140','KH0483'),('KH0305','KH0301'),('KH0304','KH0303'),('KH0503','KH0491'),('KH0504','KH0492')]}
above = [x for x in allT if x[0] >= Tobs and frozenset(x[1:]) != frozenset(('KH0097', 'KH0586')) and frozenset(x[1:]) not in known]
ctrl = {f'{a}/{b}': lcs(LD[byokr[a]], LD[byokr[b]]) for a, b in [('KH0503','KH0491'),('KH0504','KH0492')]}
neg = [lcs(A, list(rng.permutation(np.array(A)))) for _ in range(1000)]
res = dict(A=A, B=B, T_obs=Tobs, n_B=n, mc_hits=mc, mc_R=R, p_union_bound=pbound, p_bonf=pbound * M, M=M,
           top10=allT[:10], unknown_pairs_ge_Tobs=above[:20], n_unknown_ge_Tobs=len(above), controls=ctrl,
           neg_selfshuffle=dict(mean=float(np.mean(neg)), max=int(max(neg))), sec=round(time.time() - t0, 1))
res['CONFIRMED'] = bool(res['p_bonf'] < 0.01 and len(above) == 0)
json.dump(res, open('analysis/k017_results.json', 'w'), indent=1, default=str); print(json.dumps(res, default=str)[:3000])
