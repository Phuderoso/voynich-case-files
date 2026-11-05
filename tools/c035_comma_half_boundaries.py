#!/usr/bin/env python3
"""C035 (F-SEG step 2): are ZL's uncertain spaces (commas) 'half-boundaries' on the C034 Harris score?
Pre-registered in case-file/C035-comma-half-boundaries.md. Seed 3535.
Run: timeout 600 python3 tools/c035_comma_half_boundaries.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c034_harris_boundaries as X

SEED, NPERM, NREP, ALPHA = 3535, 1000, 40, 0.05 / 2

def zl_stream(path='data/ZL3b-n.txt'):
    """paragraph lines of ZL; returns unit stream and gap type per position: 0 none, 1 space ('.'), 2 comma (','),
    3 line break (excluded). '<->' read as '.', as in all cycles; lines with unreadable glyphs dropped (C030 rule)."""
    s, g = [], []
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'<(f\w+)\.\d+,([@+=*&~-])(\w+)>\s*(.*)', line.rstrip('\n'))
        if not m or not m.group(3).startswith('P'): continue
        t = m.group(4).replace('<->', '.')
        t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        t = re.sub(r'\s+', '', t)
        toks = re.split(r'([.,]+)', t); words, seps = [], []
        for x in toks:
            if not x: continue
            if re.fullmatch(r'[.,]+', x): seps.append(2 if ',' in x and '.' not in x else 1)
            else: words.append(x); seps.append(None)
        if not words or not all(re.fullmatch(r'[a-z]+', w) for w in words): continue
        first = True; pending = 3
        for x in seps:
            if x is not None: pending = x; continue
            w = words.pop(0); u = T.units(w)
            for j, ch in enumerate(u):
                g.append((3 if first else pending) if j == 0 else 0); s.append(ch); first = False
            pending = 1
    return s, np.array(g)

def auc_groups(rk_all, m, pos_mask, neg_mask):
    """AUC of score: positives vs negatives, from midranks recomputed on the union"""
    sel = (pos_mask | neg_mask)[m]; r = X.rankdata(rk_all[sel]); y = pos_mask[m][sel]
    n1 = y.sum(); n0 = len(y) - n1
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

def ptest(sc, m, pos, neg, rng, plant_pool=None):
    """one-sided p: AUC(pos vs neg) vs relabelling the same number of positives at random within pos|neg"""
    a = auc_groups(sc, m, pos, neg); idx = np.flatnonzero(pos | neg); n = pos.sum(); ge = 0
    for _ in range(NPERM):
        p2 = np.zeros_like(pos); p2[rng.choice(idx, n, replace=False)] = True
        ge += auc_groups(sc, m, p2, (pos | neg) & ~p2) >= a
    return a, (1 + ge) / (NPERM + 1)

def fast_null(sc, m, pos, neg, rng, nperm):
    idx = np.flatnonzero(pos | neg); n = pos.sum(); out = []
    for _ in range(nperm):
        p2 = np.zeros_like(pos); p2[rng.choice(idx, n, replace=False)] = True
        out.append(auc_groups(sc, m, p2, (pos | neg) & ~p2))
    return np.array(out)

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); s, g = zl_stream(); sc = X.scores(s); m = ~np.isnan(sc)
    valid = m & (g != 3); none, space, comma = valid & (g == 0), valid & (g == 1), valid & (g == 2)
    R = dict(units=len(s), gaps_none=int(none.sum()), gaps_space=int(space.sum()), gaps_comma=int(comma.sum()), K=X.K)
    print(R, flush=True)
    aA, pA = ptest(sc, m, comma, none, rng); aB, pB = ptest(sc, m, space, comma, rng)
    R['A_comma_vs_none'] = dict(auc=aA, p=pA); R['B_space_vs_comma'] = dict(auc=aB, p=pB)
    R['space_vs_none_auc'] = auc_groups(sc, m, space, none)
    print('A', aA, pA, 'B', aB, pB, 'space/none', R['space_vs_none_auc'], round(time.time() - t0, 1), 's', flush=True)
    # gates: fake commas = random non-gaps (A size), random spaces (B size), half/half mixture (power A and B)
    nC = int(comma.sum()); iN, iS = np.flatnonzero(none), np.flatnonzero(space)
    nullA = fast_null(sc, m, comma, none, rng, 200); nullB = fast_null(sc, m, space, comma, rng, 200)
    fa = fb = pa = pb = 0
    for _ in range(NREP):
        f = np.zeros_like(comma); f[rng.choice(iN, nC, replace=False)] = True
        fa += (1 + (nullA >= auc_groups(sc, m, f, none & ~f)).sum()) / 201 < ALPHA
        f = np.zeros_like(comma); f[rng.choice(iS, nC, replace=False)] = True
        fb += (1 + (nullB >= auc_groups(sc, m, space & ~f, f)).sum()) / 201 < ALPHA
        f = np.zeros_like(comma); f[rng.choice(iS, nC // 2, replace=False)] = True; f[rng.choice(iN, nC - nC // 2, replace=False)] = True
        pa += (1 + (nullA >= auc_groups(sc, m, f, none & ~f)).sum()) / 201 < ALPHA
        pb += (1 + (nullB >= auc_groups(sc, m, space & ~f, f)).sum()) / 201 < ALPHA
    R['gates'] = dict(fpr_A=fa / NREP, fpr_B=fb / NREP, power_A=pa / NREP, power_B=pb / NREP)
    ok = fa <= 4 and fb <= 4 and pa >= 32 and pb >= 32; R['gates']['passed'] = ok
    sA, sB = pA < ALPHA, pB < ALPHA
    R['verdict'] = 'NOT TESTABLE' if not ok else ('HALF-BOUNDARIES' if sA and sB else 'SPACE-LIKE' if sA and not sB
                                                   else 'NON-BOUNDARIES' if sB and not sA else 'UNRESOLVED')
    R['seconds'] = round(time.time() - t0, 1); print(R['gates'], R['verdict'], R['seconds'], 's')
    json.dump(R, open('analysis/C035_results.json', 'w'), indent=1, default=float)

if __name__ == '__main__':
    main()
