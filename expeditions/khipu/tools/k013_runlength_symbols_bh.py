#!/usr/bin/env python3
"""K013 - run-length-aware symbols (value, run length), per-pair longest-match chance probability + BH. Pre-registered in case-file/K013-runlength-symbols-bh.md.
Usage: python3 tools/k013_runlength_symbols_bh.py data/khipu.db"""
import sqlite3, json, sys, time, math, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); c = sqlite3.connect(sys.argv[1]); rng = np.random.default_rng(20131105); NNULL, NPLANT, CAP = 40, 200, 300
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
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: kh[khid].append(0 if cid in R5 else val.get(cid, 0))
ids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]; seqs = [np.array(kh[k], np.int64) for k in ids]
freq = Counter(int(x) for s in seqs for x in s if x > 0); tot = sum(freq.values()); ginfo = {v: -math.log2(n / tot) for v, n in freq.items()}
lnn = [math.log2(len(s)) for s in seqs]
def runs(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; return np.split(s, b)
RUNS = [runs(s) for s in seqs]
def runperm(k):
    r = RUNS[k]; o = rng.permutation(len(r)); return np.concatenate([r[i] for i in o])
def collapse(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; st = np.concatenate([[0], b]); ln = np.diff(np.concatenate([st, [len(s)]]))
    v = s[st]; assert ln.max() < 1000
    return np.where(v > 0, v * 1000 + ln, 0), ln
N = len(seqs); M = N * (N - 1) // 2; print('khipus', N, 'pairs', M, flush=True)

def longest(S):
    """longest aligned block of equal non-zero values per pair, from shared 3-value seeds"""
    idx = defaultdict(list)
    for a, s in enumerate(S):
        for i in range(len(s) - 2):
            if s[i] > 0 and s[i + 1] > 0 and s[i + 2] > 0: idx[(s[i], s[i + 1], s[i + 2])].append((a, i))
    best = {}
    for g, occ in idx.items():
        if len(occ) > CAP or len(occ) < 2: continue
        for x in range(len(occ)):
            a, i = occ[x]
            for y in range(x + 1, len(occ)):
                b, j = occ[y]
                if a == b: continue
                sa, sb = S[a], S[b]
                if i > 0 and j > 0 and sa[i - 1] == sb[j - 1] and sa[i - 1] > 0: continue
                L = 3
                while i + L < len(sa) and j + L < len(sb) and sa[i + L] == sb[j + L] and sa[i + L] > 0: L += 1
                key = (a, b) if a < b else (b, a); ia, ib = (i, j) if a < b else (j, i)
                if L > best.get(key, (0,))[0]: best[key] = (L, ia, ib)
    return best

def pvals(S, best):
    P = {}
    dist = [Counter(int(x) for x in s) for s in S]
    for (a, b), (L, i, j) in best.items():
        na, nb = len(S[a]), len(S[b]); da, db = dist[a], dist[b]
        q = sum((k / na) * (db[v] / nb) for v, k in da.items() if v > 0 and v in db)
        lam = (1 - q) * q ** L * (na - L + 1) * (nb - L + 1)
        P[(a, b)] = -math.expm1(-lam)
    return P

def bh(P):
    items = sorted(P.items(), key=lambda kv: kv[1]); k = 0
    for r, (key, p) in enumerate(items, 1):
        if p <= r * 0.05 / M: k = r
    return {key for key, p in items[:k]}

anydisc, small, ndisc = 0, 0, []
for r in range(NNULL):
    Sx = [collapse(runperm(k))[0] for k in range(N)]; P = pvals(Sx, longest(Sx)); D = bh(P)
    anydisc += bool(D); ndisc.append(len(D)); small += sum(p < 0.01 for p in P.values())
    if r % 10 == 9: print('null', r + 1, anydisc, round(time.time() - t0, 1), flush=True)
calA = anydisc / NNULL; calB = small / (NNULL * M)
rec, plP = [], []
for t in range(NPLANT):
    Sx = [runperm(k) for k in range(N)]
    while True:
        a, b = (int(x) for x in rng.choice(N, 2, replace=False)); sa = Sx[a]
        st = [i for i in range(len(sa) - 5) if (sa[i:i + 6] > 0).sum() >= 5]
        if st and len(Sx[b]) >= 8: break
    i = int(rng.choice(st)); j = int(rng.integers(0, len(Sx[b]) - 5)); Sx[b] = Sx[b].copy(); Sx[b][j:j + 6] = sa[i:i + 6]
    Sx = [collapse(x)[0] for x in Sx]
    P = pvals(Sx, longest(Sx)); D = bh(P); k = (min(a, b), max(a, b)); rec.append(k in D); plP.append(P.get(k, 1.0))
    if t % 50 == 49: print('plant', t + 1, round(float(np.mean(rec)), 3), round(time.time() - t0, 1), flush=True)
CL = [collapse(x) for x in seqs]; cs = [x[0] for x in CL]
best = longest(cs); P = pvals(cs, best); D = bh(P)
rows = []
for key in sorted(D, key=lambda k: P[k]):
    a, b = key; L, i, j = best[key]; A, B = meta[ids[a]], meta[ids[b]]
    rows.append(dict(a=A['okr'], a_inv=A['inv'], b=B['okr'], b_inv=B['inv'], L=L, p=P[key], block=[int(x) // 1000 for x in cs[a][i:i + L]], runlen_a=[int(x) for x in CL[a][1][i:i + L]], runlen_b=[int(x) for x in CL[b][1][j:j + L]],
                     runlen_agree=bool((CL[a][1][i:i + L] == CL[b][1][j:j + L]).all()),
                     a_museum=A['museum'] + ' ' + A['mnum'], b_museum=B['museum'] + ' ' + B['mnum']))
summ = dict(N=N, M=M, null_corpora=NNULL, null_any_discovery=calA, null_mean_discoveries=float(np.mean(ndisc)),
            null_share_p_lt_001=calB, calibrated=bool(calA <= 0.15 and calB <= 0.02), planted=NPLANT,
            planted_power=float(np.mean(rec)), planted_median_p=float(np.median(plP)), real_blocks=len(best),
            real_discoveries=len(rows), real_runlen_agree=sum(r['runlen_agree'] for r in rows), seconds=round(time.time() - t0, 1))
json.dump(dict(summary=summ, null_discoveries=ndisc, planted_p=plP, discoveries=rows), open('analysis/k013_results.json', 'w'), indent=1)
print(json.dumps(summ, indent=1))
for r in rows: print(r['a'], r['a_inv'], r['b'], r['b_inv'], r['L'], '%.2e' % r['p'], r['runlen_agree'], r['a_museum'], '|', r['b_museum'], r['block'][:10])
