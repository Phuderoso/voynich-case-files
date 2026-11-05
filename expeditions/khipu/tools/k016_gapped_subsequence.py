#!/usr/bin/env python3
"""K016 - weighted LCS of non-zero value sequences (S1) and its normalised form (S2); run-preserving max-statistic null; held-out calibration; gapped plants; Urton & Chu (2015) controls. Pre-registered in case-file/K016-gapped-subsequence.md.
Usage: python3 tools/k016_gapped_subsequence.py data/khipu.db  (compiles tools/k016_wlcs.c with gcc)"""
import sqlite3, json, sys, time, math, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); c = sqlite3.connect(sys.argv[1]); rng = np.random.default_rng(20161105); NNULL, NPLANT, CAP = 40, 200, 300
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


import ctypes, subprocess, os
SO = '/tmp/k016_wlcs.so'; subprocess.run(['gcc', '-O3', '-shared', '-fPIC', '-o', SO, os.path.join(os.path.dirname(__file__), 'k016_wlcs.c')], check=True)
lib = ctypes.CDLL(SO); dp = ctypes.POINTER(ctypes.c_double); ip = ctypes.POINTER(ctypes.c_int); lp = ctypes.POINTER(ctypes.c_longlong)
W = {v: -math.log2(n / tot) for v, n in freq.items()}
def nz(s): return s[s > 0]
def scores(S):
    S = [nz(s) for s in S]; L = np.array([len(s) for s in S], np.int32); off = np.concatenate([[0], np.cumsum(L)[:-1]]).astype(np.int32)
    v = np.concatenate(S).astype(np.int64); w = np.array([W.get(int(x), max(W.values())) for x in v], np.float64); out = np.zeros(M)
    lib.wlcs_all(N, off.ctypes.data_as(ip), L.ctypes.data_as(ip), v.ctypes.data_as(lp), w.ctypes.data_as(dp), out.ctypes.data_as(dp))
    tw = np.array([w[o:o + l].sum() for o, l in zip(off, L)]); a, b = np.triu_indices(N, 1)
    return out, out / np.sqrt(tw[a] * tw[b])
AI, BI = np.triu_indices(N, 1)
def pidx(a, b):
    a, b = min(a, b), max(a, b); return a * N - a * (a + 1) // 2 + (b - a - 1)
m1, m2 = [], []
for r in range(100):
    s1, s2 = scores([runperm(k) for k in range(N)]); m1.append(s1.max()); m2.append(s2.max())
    if r % 20 == 19: print('null', r + 1, round(time.time() - t0, 1), flush=True)
T1, T2 = float(np.quantile(m1, 0.975)), float(np.quantile(m2, 0.975)); print('thresholds', T1, T2, flush=True)
hold = 0
for r in range(20):
    s1, s2 = scores([runperm(k) for k in range(N)]); hold += bool((s1 > T1).any() or (s2 > T2).any())
calA = hold / 20; calibrated = calA <= 0.15; print('held-out any', hold, calibrated, flush=True)
rec = []
for t in range(50):
    Sx = [runperm(k) for k in range(N)]
    while True:
        a, b = (int(x) for x in rng.choice(N, 2, replace=False)); A, B = nz(Sx[a]), nz(Sx[b])
        if len(A) >= 12 and len(B) >= 24: break
    i = int(rng.integers(0, len(A) - 11)); j = int(rng.integers(0, len(B) - 23)); B = B.copy(); B[j:j + 24:2] = A[i:i + 12]
    Sx[b] = B; Sx[a] = A
    s1, s2 = scores(Sx); p = pidx(a, b); rec.append(bool(s1[p] > T1 or s2[p] > T2))
power = float(np.mean(rec)); print('power', power, round(time.time() - t0, 1), flush=True)
s1, s2 = scores(seqs); hit = np.flatnonzero((s1 > T1) | (s2 > T2)); pos = {k: i for i, k in enumerate(ids)}
def info(x, y):
    if x not in pos or y not in pos: return 'not in analysed set'
    p = pidx(pos[x], pos[y]); return dict(S1=float(s1[p]), S2=float(s2[p]), discovery=bool(s1[p] > T1 or s2[p] > T2))
ctrl = {'UR267A-UR255': info(1000608, 1000597), 'UR267B-UR256': info(1000609, 1000598)}
known = {'KH0362-KH0049': info(1000323, 1000565), 'KH0128-KH0137': info(1000063, 1000079), 'KH0140-KH0483': info(1000082, 1000558),
         'KH0304-KH0303': info(1000260, 1000261), 'KH0305-KH0301': info(1000262, 1000263)}
rows = sorted([dict(a=meta[ids[AI[p]]]['okr'] + ' ' + meta[ids[AI[p]]]['inv'], b=meta[ids[BI[p]]]['okr'] + ' ' + meta[ids[BI[p]]]['inv'],
                    a_museum=meta[ids[AI[p]]]['museum'], b_museum=meta[ids[BI[p]]]['museum'], S1=float(s1[p]), S2=float(s2[p]),
                    by=('S1' if s1[p] > T1 else '') + ('S2' if s2[p] > T2 else '')) for p in hit], key=lambda r: -r['S1'])
summ = dict(N=N, M=M, T1=T1, T2=T2, heldout_any=calA, calibrated=bool(calibrated), power_gapped12=power, controls=ctrl, known_pairs=known,
            real_discoveries=len(rows), seconds=round(time.time() - t0, 1))
json.dump(dict(summary=summ, discoveries=rows), open('analysis/k016_results.json', 'w'), indent=1)
print(json.dumps(summ, indent=1)); [print(r) for r in rows]
