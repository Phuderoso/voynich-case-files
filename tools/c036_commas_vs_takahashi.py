#!/usr/bin/env python3
"""C036 (F-SEG step 3, bridge to F-TRX): where ZL 3b doubts a gap (comma), does Takahashi IT2a write a space?
And do the C035 Harris scores separate the commas IT2a agrees with from those it doesn't?
Pre-registered in case-file/C036-commas-vs-takahashi.md. Seed 3636.
Run: timeout 600 python3 tools/c036_commas_vs_takahashi.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c034_harris_boundaries as X
import c035_comma_half_boundaries as Y

SEED, NPERM, NREP = 3636, 2000, 40
ALPHA = 0.05 / 3

def loci(path):
    """locus -> (units, gaptypes) for paragraph lines; gaptype per unit: 0 none, 1 space, 2 comma, 3 line start"""
    out = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'<(f\w+\.\d+),([@+=*&~-])(\w+)>\s*(.*)', line.rstrip('\n'))
        if not m or not m.group(3).startswith('P'): continue
        t = m.group(4).replace('<->', '.')
        t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        t = re.sub(r'\s+', '', t); toks = [x for x in re.split(r'([.,]+)', t) if x]
        words = [x for x in toks if not re.fullmatch(r'[.,]+', x)]
        if not words or not all(re.fullmatch(r'[a-z]+', w) for w in words): continue
        u, g, pend = [], [], 3
        for x in toks:
            if re.fullmatch(r'[.,]+', x): pend = 2 if (',' in x and '.' not in x) else 1; continue
            for j, ch in enumerate(T.units(x)): u.append(ch); g.append(pend if j == 0 else 0)
            pend = 1
        out[m.group(1)] = (u, g)
    return out

def strat_perm(lab, cand, y, rng, n):
    """null for rate(y | lab) - rate(y | cand & ~lab): relabel lab within cand, keeping the per-line count of lab.
    lab, cand, y: lists of per-line boolean arrays"""
    obs = rate_diff(lab, cand, y); ge = 0; null = []
    for _ in range(n):
        L = []
        for l, c in zip(lab, cand):
            idx = np.flatnonzero(c); k = int(l.sum()); z = np.zeros_like(l)
            if k: z[rng.choice(idx, k, replace=False)] = True
            L.append(z)
        null.append(rate_diff(L, cand, y))
    null = np.array(null); return obs, null

def rate_diff(lab, cand, y):
    a = sum(int((l & yy).sum()) for l, yy in zip(lab, y)); na = sum(int(l.sum()) for l in lab)
    b = sum(int((c & ~l & yy).sum()) for l, c, yy in zip(lab, cand, y)); nb = sum(int((c & ~l).sum()) for l, c in zip(lab, cand))
    return a / na - b / nb

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED)
    Z, I = loci('data/ZL3b-n.txt'), loci('data/IT2a-n.txt')
    common = sorted(set(Z) & set(I)); same = [k for k in common if Z[k][0] == I[k][0]]
    lines = [(np.array(Z[k][1]), np.array(I[k][1])) for k in same]
    lines = [(z, i) for z, i in lines if (z == 2).any() or True]
    comma = [z == 2 for z, i in lines]; space = [z == 1 for z, i in lines]; none = [z == 0 for z, i in lines]
    itsp = [(i == 1) | (i == 2) for z, i in lines]
    nC = sum(int(c.sum()) for c in comma)
    R = dict(loci_common=len(common), loci_identical_glyphs=len(same), commas=nC,
             spaces=sum(int(s.sum()) for s in space), nongaps=sum(int(n.sum()) for n in none))
    rate = lambda M: sum(int((m & y).sum()) for m, y in zip(M, itsp)) / sum(int(m.sum()) for m in M)
    R['it2a_space_rate'] = dict(at_zl_space=rate(space), at_zl_comma=rate(comma), at_zl_nongap=rate(none))
    print(R, flush=True)
    # A: commas vs non-gaps (IT2a space rate higher at commas?), B: spaces vs commas (higher at spaces?)
    candA = [c | n for c, n in zip(comma, none)]; candB = [c | s for c, s in zip(comma, space)]
    oA, nA = strat_perm(comma, candA, itsp, rng, NPERM); pA = (1 + (nA >= oA).sum()) / (NPERM + 1)
    oB, nB = strat_perm(space, candB, itsp, rng, NPERM); pB = (1 + (nB >= oB).sum()) / (NPERM + 1)
    R['A'] = dict(diff=oA, p=float(pA)); R['B'] = dict(diff=oB, p=float(pB))
    print('A', oA, pA, 'B', oB, pB, round(time.time() - t0, 1), 's', flush=True)
    # gates (200-draw nulls reused): size A fake commas from non-gaps; size B fake commas from spaces; power half/half
    nA2, nB2 = nA[:200], nB[:200]; fa = fb = pa = pb = 0
    def fake(src_lists, k_frac=1.0, mix=None):
        out = []
        for li, (c, s, n) in enumerate(zip(comma, space, none)):
            k = int(c.sum()); z = np.zeros_like(c)
            if mix is None:
                pool = np.flatnonzero(src_lists[li]); k = min(k, len(pool))
                if k: z[rng.choice(pool, k, replace=False)] = True
            else:
                for pool_arr, kk in ((s, (k + 1) // 2), (n, k // 2)):
                    pool = np.flatnonzero(pool_arr & ~z); kk = min(kk, len(pool))
                    if kk: z[rng.choice(pool, kk, replace=False)] = True
            out.append(z)
        return out
    for _ in range(NREP):
        f = fake(none); fa += (1 + (nA2 >= rate_diff(f, [x | n for x, n in zip(f, none)], itsp)).sum()) / 201 < ALPHA
        f = fake(space); fb += (1 + (nB2 >= rate_diff([s & ~x for s, x in zip(space, f)], [s | x for s, x in zip(space, f)], itsp)).sum()) / 201 < ALPHA
        f = fake(None, mix=True)
        pa += (1 + (nA2 >= rate_diff(f, [x | n for x, n in zip(f, none)], itsp)).sum()) / 201 < ALPHA
        pb += (1 + (nB2 >= rate_diff([s & ~x for s, x in zip(space, f)], [s | x for s, x in zip(space, f)], itsp)).sum()) / 201 < ALPHA
    R['gates'] = dict(fpr_A=fa / NREP, fpr_B=fb / NREP, power_A=pa / NREP, power_B=pb / NREP)
    ok = fa <= 4 and fb <= 4 and pa >= 32 and pb >= 32; R['gates']['passed'] = bool(ok)
    # Look 2: C035 Harris score at commas, IT2a-space vs IT2a-no-space (score from the whole ZL stream, as C035)
    s, g = Y.zl_stream(); sc = X.scores(s)
    offs, pos = {}, 0  # map identical loci into the ZL stream by re-walking loci in file order
    order = list(Z.keys()); 
    for k in order: offs[k] = pos; pos += len(Z[k][0])
    assert pos == len(s), (pos, len(s))
    yes, no = [], []
    for k, (z, i) in zip(same, lines):
        for j in np.flatnonzero(z == 2):
            v = sc[offs[k] + j]
            if not np.isnan(v): (yes if (i[j] in (1, 2)) else no).append(v)
    yes, no = np.array(yes), np.array(no); allv = np.concatenate([yes, no]); r = X.rankdata(allv); n1 = len(yes)
    a2 = float((r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * len(no))); ge = 0
    for _ in range(NPERM):
        rr = rng.permutation(r); ge += (rr[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * len(no)) >= a2
    p2 = (1 + ge) / (NPERM + 1); R['look2'] = dict(n_it2a_space=n1, n_it2a_nospace=len(no), auc=a2, p=float(p2))
    sA, sB, s2 = pA < ALPHA, pB < ALPHA, p2 < ALPHA
    R['verdict'] = 'NOT TESTABLE' if not ok else ('HALF (IT2a agrees partly)' if sA and sB else 'SPACE-LIKE' if sA else 'NON-GAP-LIKE' if sB else 'UNRESOLVED')
    R['look2_verdict'] = 'SCORES SEPARATE' if s2 else 'NO SEPARATION'
    R['seconds'] = round(time.time() - t0, 1); print(R['gates'], R['verdict'], R['look2'], R['look2_verdict'], R['seconds'])
    json.dump(R, open('analysis/C036_results.json', 'w'), indent=1, default=float)

if __name__ == '__main__':
    main()
