#!/usr/bin/env python3
"""K015 - close-match detector: sorted 3-cord window symbols, longest aligned run + Poisson p + BH; run-preserving null; swapped plants; Urton & Chu (2015) positive controls. Pre-registered in case-file/K015-close-match-windows.md.
Usage: python3 tools/k015_close_match_windows.py data/khipu.db"""
import sqlite3, json, sys, time, math, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); c = sqlite3.connect(sys.argv[1]); rng = np.random.default_rng(20151105); NNULL, NPLANT, CAP = 40, 200, 300
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

def bh(P, ALPHA=0.05):
    items = sorted(P.items(), key=lambda kv: kv[1]); k = 0
    for r, (key, p) in enumerate(items, 1):
        if p <= r * ALPHA / M: k = r
    return {key for key, p in items[:k]}



WID = {}
def win(s):
    out = np.zeros(max(len(s) - 2, 1), np.int64)
    for i in range(len(s) - 2):
        a, b, c = int(s[i]), int(s[i + 1]), int(s[i + 2])
        if a > 0 and b > 0 and c > 0: out[i] = WID.setdefault(tuple(sorted((a, b, c))), len(WID) + 1)
    return out
def run(raw):
    W = [win(x) for x in raw]; return pvals(W, longest(W))
anyd, small = 0, 0
for r in range(NNULL):
    P = run([runperm(k) for k in range(N)]); D = bh(P); anyd += bool(D); small += sum(p < 0.01 for p in P.values())
    if r % 10 == 9: print('null', r + 1, anyd, round(time.time() - t0, 1), flush=True)
calA, calB = anyd / NNULL, small / (NNULL * M); calibrated = bool(calA <= 0.15 and calB <= 0.02)
print('calibration', calA, calB, calibrated, flush=True)
def swapped(x):
    x = x.copy(); i = 0
    while i < len(x) - 1:
        if rng.random() < 0.3: x[i], x[i + 1] = x[i + 1], x[i]; i += 2
        else: i += 1
    return x
power = {}
for Lp in (10, 16):
    rec = []
    for t in range(100):
        Sx = [runperm(k) for k in range(N)]
        while True:
            a, b = (int(x) for x in rng.choice(N, 2, replace=False)); sa = Sx[a]
            st = [i for i in range(len(sa) - Lp + 1) if (sa[i:i + Lp] > 0).sum() >= Lp - 1]
            if st and len(Sx[b]) >= Lp + 2: break
        i = int(rng.choice(st)); j = int(rng.integers(0, len(Sx[b]) - Lp + 1)); Sx[b] = Sx[b].copy(); Sx[b][j:j + Lp] = swapped(sa[i:i + Lp])
        D = bh(run(Sx)); rec.append((min(a, b), max(a, b)) in D)
    power[Lp] = float(np.mean(rec)); print('power', Lp, power[Lp], round(time.time() - t0, 1), flush=True)
W = [win(x) for x in seqs]; best = longest(W); P = pvals(W, best); D = bh(P)
pos = {k: i for i, k in enumerate(ids)}; ctrl = {}
for x, y in ((1000608, 1000597), (1000609, 1000598)):
    if x in pos and y in pos:
        k = (min(pos[x], pos[y]), max(pos[x], pos[y])); ctrl['%d-%d' % (x, y)] = dict(p=P.get(k, 1.0), L=best.get(k, (0,))[0], discovery=k in D)
    else: ctrl['%d-%d' % (x, y)] = 'not in analysed set'
rows = [dict(a=ids[a], b=ids[b], L_windows=best[(a, b)][0], p=P[(a, b)]) for a, b in sorted(D, key=lambda k: P[k])]
summ = dict(N=N, M=M, null_any=calA, null_share_p_lt_001=calB, calibrated=calibrated, power_swapped=power, controls=ctrl,
            real_discoveries=len(rows), seconds=round(time.time() - t0, 1))
json.dump(dict(summary=summ, discoveries=rows), open('analysis/k015_results.json', 'w'), indent=1)
print(json.dumps(summ, indent=1)); [print(r) for r in rows]
