#!/usr/bin/env python3
"""K019 - cord-level check of K018 leader correspondences: non-leader within-group LCS vs random-partner-group null. Pre-registered in case-file/K019-cord-level-check.md.
Usage: python3 tools/k019_cord_level.py data/khipu.db  (compiles tools/k016_wlcs.c with gcc)"""
import sqlite3, json, sys, time, math, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); c = sqlite3.connect(sys.argv[1]); rng = np.random.default_rng(20191105); NNULL, NPLANT, CAP = 40, 200, 300
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
lf = Counter(x for k in ids for x in LD[k]); lt = sum(lf.values()); WL = {v: -math.log2(n / lt) for v, n in lf.items()}
cid_of = defaultdict(list)
for khid, cid, cl in c.execute("select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if not cid_of[khid] or cid_of[khid][-1][0] != cl: cid_of[khid].append([cl, []])
    cid_of[khid][-1][1].append(cid)
col = {}
for cid, cc in c.execute("select CORD_ID, FULL_COLOR from ascher_cord_color where PCORD_FLAG=0 or PCORD_FLAG is null"):
    col.setdefault(cid, (cc or '').strip())
def lgroups(k):
    return [(g[1], cid_of[k][i][1]) for i, g in enumerate(grp[k]) if len(g[1]) >= 5 and g[1][0] > 0]
def walign(a, b):
    n, m = len(a), len(b); D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = max(D[i-1][j], D[i][j-1], D[i-1][j-1] + WL[a[i-1]] if a[i-1] == b[j-1] else -1)
    i, j, pr = n, m, []
    while i and j:
        if a[i-1] == b[j-1] and abs(D[i][j] - (D[i-1][j-1] + WL[a[i-1]])) < 1e-9: pr.append((i-1, j-1)); i -= 1; j -= 1
        elif D[i-1][j] >= D[i][j-1]: i -= 1
        else: j -= 1
    return pr[::-1]
res = {}; R = 10000
for a, b in [('KH0097', 'KH0586'), ('KH0192', 'KH0470'), ('KH0192', 'KH0469')]:
    GA, GB = lgroups(byokr[a]), lgroups(byokr[b]); pr = walign([g[0][0] for g in GA], [g[0][0] for g in GB])
    V = [lcs(GA[i][0][1:], GB[j][0][1:]) for i, j in pr]; obs = sum(V)
    pos_eq = sum(x == y for i, j in pr for x, y in zip(GA[i][0][1:], GB[j][0][1:])); pos_n = sum(min(len(GA[i][0]), len(GB[j][0])) - 1 for i, j in pr)
    ceq = cn = 0
    for i, j in pr:
        for x, y in zip(GA[i][1], GB[j][1]):
            if x in col and y in col: cn += 1; ceq += col[x] == col[y]
    others = {j: [i2 for i2 in range(len(GA)) if i2 != i] for i, j in pr}
    cache = {}
    def V_(i2, j):
        if (i2, j) not in cache: cache[(i2, j)] = lcs(GA[i2][0][1:], GB[j][0][1:])
        return cache[(i2, j)]
    ge = 0; nulls = []
    for r in range(R):
        s = sum(V_(int(rng.choice(others[j])), j) for i, j in pr); nulls.append(s); ge += s >= obs
    p = (1 + ge) / (R + 1)
    res[f'{a}/{b}'] = dict(matched_groups=len(pr), pairs=[(i, j) for i, j in pr], V=V, V_tot=obs, null_mean=float(np.mean(nulls)), null_max=int(max(nulls)), p=p,
        CONFIRMED=bool(p < 0.01 / 3), nonleader_cords_in_matched_groups_A=sum(len(GA[i][0]) - 1 for i, j in pr), B=sum(len(GB[j][0]) - 1 for i, j in pr),
        same_position_equal=f'{pos_eq}/{pos_n}', colour_equal_same_position=f'{ceq}/{cn}', cords_total=dict(A=len(kh[byokr[a]]), B=len(kh[byokr[b]])))
    print(a, b, json.dumps(res[f'{a}/{b}']), round(time.time() - t0), flush=True)
json.dump(dict(results=res, R=R, sec=round(time.time() - t0, 1)), open('analysis/k019_results.json', 'w'), indent=1)
