#!/usr/bin/env python3
"""K006 - cross-khipu shared runs, run-preserving null, composition-aware score. Pre-registered in case-file/K006-run-preserving-cross-khipu.md.
Usage: python3 tools/k006_run_null.py data/khipu.db"""
import sqlite3, json, sys, time, math, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); c = sqlite3.connect(sys.argv[1]); rng = np.random.default_rng(20020); R, CAP = 200, 300
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
meta = {r[0]: dict(okr=r[1] or '', inv=r[2] or '', museum=(r[3] or '').strip(), mnum=(r[4] or '').strip())
        for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM, MUSEUM_NAME, MUSEUM_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: kh[khid].append(val.get(cid, 0))
ids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]; seqs = [np.array(kh[k], np.int64) for k in ids]
freq = Counter(int(x) for s in seqs for x in s if x > 0); tot = sum(freq.values()); ginfo = {v: -math.log2(n / tot) for v, n in freq.items()}
# within-khipu log-probabilities (fixed from real data; the null keeps each multiset)
lp = []
for s in seqs:
    cn = Counter(int(x) for x in s); lp.append({v: -math.log2(k / len(s)) for v, k in cn.items()})
lnn = [math.log2(len(s)) for s in seqs]
def runs(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; return np.split(s, b)
RUNS = [runs(s) for s in seqs]
def runperm(k):
    r = RUNS[k]; o = rng.permutation(len(r)); return np.concatenate([r[i] for i in o])

def pairstats(S, want=None):
    # within-khipu frequencies of the corpus being scored (equal to the real multisets under the null;
    # for planted corpora they include the planted values) - fix after a KeyError crash in the first run
    lp = {}
    for k in (want if want else range(len(S))):
        cn = Counter(int(x) for x in S[k]); lp[k] = {v: -math.log2(m / len(S[k])) for v, m in cn.items()}
    idx = defaultdict(list)
    for a, s in enumerate(S):
        if want and a not in want: continue
        for i in range(len(s) - 2):
            if s[i] > 0 and s[i + 1] > 0 and s[i + 2] > 0: idx[(s[i], s[i + 1], s[i + 2])].append((a, i))
    bS, bI = {}, {}
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
                blk = [int(v) for v in sa[i:i + L]]
                Sc = sum(lp[a][v] + lp[b][v] for v in blk) - lnn[a] - lnn[b]
                I = sum(ginfo.get(v, 20.0) for v in blk)
                key = (a, b) if a < b else (b, a); ia, ib = (i, j) if a < b else (j, i)
                if Sc > bS.get(key, (-1e9,))[0]: bS[key] = (Sc, ia, ib, L)
                if I > bI.get(key, (0,))[0]: bI[key] = (I, ia, ib, L)
    return bS, bI

oS, oI = pairstats(seqs); print('pairs with block', len(oS), round(time.time() - t0, 1), flush=True)
mS, mI = [], []
for r in range(R):
    Sx = [runperm(k) for k in range(len(seqs))]; a, b = pairstats(Sx)
    mS.append(max((v[0] for v in a.values()), default=0)); mI.append(max((v[0] for v in b.values()), default=0))
    if r % 50 == 49: print('rep', r + 1, round(time.time() - t0, 1), flush=True)
mS, mI = np.array(mS), np.array(mI); TS, TI = float(np.quantile(mS, .95)), float(np.quantile(mI, .95))
calS = float((mS[150:] > np.quantile(mS[:150], .95)).mean()); calI = float((mI[150:] > np.quantile(mI[:150], .95)).mean())
rec, recI, plS = [], [], []
for t in range(100):
    Sx = [runperm(k) for k in range(len(seqs))]
    while True:
        a, b = (int(x) for x in rng.choice(len(Sx), 2, replace=False)); sa = Sx[a]
        st = [i for i in range(len(sa) - 5) if (sa[i:i + 6] > 0).sum() >= 5]
        if st and len(Sx[b]) >= 8: break
    i = int(rng.choice(st)); j = int(rng.integers(0, len(Sx[b]) - 5)); Sx[b] = Sx[b].copy(); Sx[b][j:j + 6] = sa[i:i + 6]
    ps, pi = pairstats(Sx, want={a, b}); k = (min(a, b), max(a, b))
    s = ps.get(k, (-1e9,))[0]; rec.append(s > TS); recI.append(pi.get(k, (0,))[0] > TI); plS.append(s)
def table(obs, T, mx):
    rows = []
    for (a, b), (v, i, j, L) in obs.items():
        if v <= T: continue
        A, B = meta[ids[a]], meta[ids[b]]; nz = min((seqs[a] > 0).sum(), (seqs[b] > 0).sum())
        same = bool(A['mnum'] and A['mnum'] == B['mnum'] and A['museum'] == B['museum'])
        rows.append(dict(a=A['okr'], a_inv=A['inv'], b=B['okr'], b_inv=B['inv'], score=round(v, 2), block_len=L,
                         block=[int(x) for x in seqs[a][i:i + L]], p_adj=(1 + int((mx >= v).sum())) / (1 + R),
                         a_museum=A['museum'] + ' ' + A['mnum'], b_museum=B['museum'] + ' ' + B['mnum'],
                         cls='probable duplicate record' if (same or L >= nz / 2) else 'inter-khipu match'))
    return sorted(rows, key=lambda r: -r['score'])
rS, rI = table(oS, TS, mS), table(oI, TI, mI)
summ = dict(R=R, T_S=round(TS, 2), T_I=round(TI, 2), calib_S=calS, calib_I=calI, planted_recovery_S=float(np.mean(rec)),
            planted_recovery_I=float(np.mean(recI)), planted_S_median=round(float(np.median(plS)), 2),
            n_sig_S=len(rS), n_sig_I=len(rI), seconds=round(time.time() - t0, 1))
json.dump(dict(summary=summ, null_max_S=mS.round(3).tolist(), null_max_I=mI.round(3).tolist(), significant_S=rS, significant_I=rI),
          open('analysis/k006_results.json', 'w'), indent=1)
print(json.dumps(summ, indent=1))
for name, rr in (('S', rS), ('I', rI)):
    for r in rr: print(name, r['a'], r['a_inv'], r['b'], r['b_inv'], r['score'], r['block_len'], r['p_adj'], r['cls'], r['a_museum'], '|', r['b_museum'], r['block'][:10])
