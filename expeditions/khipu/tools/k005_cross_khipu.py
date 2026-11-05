#!/usr/bin/env python3
"""K005 - cross-khipu shared value runs with max-statistic FWER control. Pre-registered in case-file/K005-cross-khipu-matches.md.
Usage: python3 tools/k005_cross_khipu.py data/khipu.db"""
import sqlite3, json, sys, time, math, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); c = sqlite3.connect(sys.argv[1]); rng = np.random.default_rng(10010)
R, CAP = 200, 300
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
meta = {r[0]: dict(okr=r[1] or '', inv=r[2] or '', museum=(r[3] or '').strip(), mnum=(r[4] or '').strip(), prov=r[5] or '')
        for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM, MUSEUM_NAME, MUSEUM_NUM, PROVENANCE from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: kh[khid].append(val.get(cid, 0))
ids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]; seqs = [np.array(kh[k], np.int64) for k in ids]
freq = Counter(int(x) for s in seqs for x in s if x > 0); tot = sum(freq.values())
info = {v: -math.log2(n / tot) for v, n in freq.items()}

def pairstats(S, want=None):
    """S: list of sequences. Returns dict (a,b)->(I, start_a, start_b, length) for best shared block; want = restrict to one pair."""
    idx = defaultdict(list)
    for a, s in enumerate(S):
        if want and a not in want: continue
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
                if i > 0 and j > 0 and sa[i - 1] == sb[j - 1] and sa[i - 1] > 0: continue  # not maximal-left; counted from earlier seed
                L = 3
                while i + L < len(sa) and j + L < len(sb) and sa[i + L] == sb[j + L] and sa[i + L] > 0: L += 1
                I = sum(info.get(int(v), 20.0) for v in sa[i:i + L]); key = (a, b) if a < b else (b, a)
                if I > best.get(key, (0,))[0]: best[key] = (I, i, j, L) if a < b else (I, j, i, L)
    return best

obs = pairstats(seqs); print('observed pairs with a shared block:', len(obs), round(time.time() - t0, 1), flush=True)
maxes = []
for r in range(R):
    S = [rng.permutation(s) for s in seqs]; b = pairstats(S); maxes.append(max((v[0] for v in b.values()), default=0.0))
    if r % 50 == 49: print('replicate', r + 1, round(time.time() - t0, 1), flush=True)
maxes = np.array(maxes); T = float(np.quantile(maxes, 0.95)); T150 = float(np.quantile(maxes[:150], 0.95))
calib = float((maxes[150:] > T150).mean())
# planted control
rec = []; plI = []
for t in range(100):
    S = [rng.permutation(s) for s in seqs]
    while True:
        a, b = rng.choice(len(S), 2, replace=False); sa = S[a]
        st = [i for i in range(len(sa) - 5) if (sa[i:i + 6] > 0).sum() >= 5]
        if st and len(S[b]) >= 8: break
    i = int(rng.choice(st)); j = int(rng.integers(0, len(S[b]) - 6 + 1)); S[b] = S[b].copy(); S[b][j:j + 6] = sa[i:i + 6]
    I = pairstats(S, want={int(a), int(b)}).get((min(a, b), max(a, b)), (0,))[0]; rec.append(I > T); plI.append(I)
rows = []
for (a, b), (I, i, j, L) in obs.items():
    if I <= T: continue
    A, B = meta[ids[a]], meta[ids[b]]; nz = min((seqs[a] > 0).sum(), (seqs[b] > 0).sum())
    same_mus = bool(A['mnum'] and A['mnum'] == B['mnum'] and A['museum'] == B['museum'])
    cls = 'probable duplicate record' if (same_mus or L >= nz / 2) else 'inter-khipu match'
    rows.append(dict(a=A['okr'], a_inv=A['inv'], b=B['okr'], b_inv=B['inv'], I_bits=round(I, 2), block_len=L, start_a=int(i), start_b=int(j),
                     block=[int(v) for v in seqs[a][i:i + L]], p_adj=(1 + int((maxes >= I).sum())) / (1 + R),
                     same_museum_number=same_mus, a_museum=A['museum'] + ' ' + A['mnum'], b_museum=B['museum'] + ' ' + B['mnum'],
                     a_prov=A['prov'], b_prov=B['prov'], shorter_nonzero=int(nz), cls=cls))
rows.sort(key=lambda r: -r['I_bits'])
summ = dict(n_khipus=len(ids), n_pairs=len(ids) * (len(ids) - 1) // 2, pairs_with_block=len(obs), R=R, threshold_bits=round(T, 2),
            null_max_median=round(float(np.median(maxes)), 2), calib_exceed_rate_last50=calib, planted_recovery=float(np.mean(rec)),
            planted_I_median=round(float(np.median(plI)), 2), n_significant=len(rows),
            n_duplicate=sum(r['cls'] == 'probable duplicate record' for r in rows), n_inter=sum(r['cls'] == 'inter-khipu match' for r in rows),
            seconds=round(time.time() - t0, 1))
json.dump(dict(summary=summ, null_maxes=maxes.round(3).tolist(), significant=rows), open('analysis/k005_results.json', 'w'), indent=1)
print(json.dumps(summ, indent=1))
for r in rows: print(r['a'], r['a_inv'], r['b'], r['b_inv'], r['I_bits'], r['block_len'], r['p_adj'], r['cls'], r['a_museum'], '|', r['b_museum'], r['block'][:12])
