#!/usr/bin/env python3
"""C101 (F-KEY step 3): (H1) is the Quire-20 p/f top-line clustering (C099/C100) carried by a few pages?
(H2) is the t-/k-word clustering seen on Currier-B top lines a TOP-LINE property, or do such words cluster as much
on ordinary (non-top) paragraph lines?
Lines: C070 parser verbatim (tools/c070_word2_sh.py parse); top line = starts with '<%>'; positions 2..n only (word 1
excluded) on every line; p/f-word = contains 'p' or 'f'; t-word contains 't'; k-word contains 'k'. Q20 = $Q=T.
Exact expectation under within-line permutation: E = k(k-1)/m per line (m slots, k flagged words); ratio = sum A / sum E.
H1 (own family; Holm over 2 transcriptions not needed: verdict needs both): T3 = ratio of Q20 top lines AFTER removing
   the 3 pages with the largest excess (A - E). Null: words 2..n shuffled within each line, THEN the same top-3 removal
   applied to the shuffled data (so the selection is inside the null). R = 2000, one-sided p.
   Reading: ROBUST (not carried by <=3 pages) if p <= 0.05 in both transcriptions; FRAGILE if neither; PARTIAL if one.
   Gates (20 replicates, seed 11620): FPR shuffled lines p<=0.05 in <=2/20; power = shuffled + C099 plant (q 0.80)
   on ALL Q20 top lines -> >=16/20; concentration control = shuffled + plant (q 1.0) only on 3 random Q20 pages
   -> must be called NOT robust (p>0.05) in >=16/20. Any failed gate -> NOT TESTABLE.
   Descriptive: per-page excess table, leave-one-page-out ratio range.
H2 (Holm over 4 = {t, k} x {IT2a, ZL3b}): Currier-B paragraph lines (all quires). T = ratio(top) - ratio(non-top).
   Null: the 'top' label permuted among lines WITHIN each page (counts per page fixed), R = 4000, one-sided.
   Gates (seed 11620): FPR = all lines shuffled within line, <=2/20; power = shuffled + plant (q 0.80, t- or k-words)
   on top lines only, >=16/20. Reading per word class: TOP-LINE LAW if both transcriptions reject (Holm);
   GENERAL (not top-specific) if neither and gates pass; PARTIAL if one.
   Descriptive: ratio of each class on top vs non-top lines in B, Q20 and A; within-line-null z for non-top lines.
Audit: recompute C100 descriptive A/E for Q20 p/f, B-other p/f, Q20 t (must equal published values).
Run: timeout 600 python tools/c101_neal_keys_pages.py analysis/C101_results.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import parse, FILES

SEED, GSEED, R1, R2, RG, NG, ALPHA = 11619, 11620, 2000, 4000, 300, 20, 0.05
CLS = {'pf': lambda w: 'p' in w or 'f' in w, 't': lambda w: 't' in w, 'k': lambda w: 'k' in w}

def fl(lines, f): return [np.array([f(x) for x in l['words'][1:]], bool) for l in lines]

def AE1(F):
    A = np.array([int((x[:-1] & x[1:]).sum()) for x in F], float)
    E = np.array([x.sum() * (x.sum() - 1) / len(x) for x in F], float); return A, E

def shuf(F, rng): return [rng.permutation(x) for x in F]

def plant(F, rng, q, mask=None):
    out = []
    for i, x in enumerate(F):
        x = x.copy(); idx = np.flatnonzero(x)
        if (mask is None or mask[i]) and len(idx) >= 2 and not (x[:-1] & x[1:]).any() and rng.random() < q:
            a, b = idx[0], idx[1]; t = a + 1 if a + 1 < len(x) else a - 1; x[t], x[b] = x[b], x[t]
        out.append(x)
    return out

# ---------- H1
def T3(F, pg, upages):
    A, E = AE1(F); ex = np.array([A[pg == p].sum() - E[pg == p].sum() for p in upages])
    drop = set(np.array(upages)[np.argsort(-ex)[:3]]); keep = np.array([p not in drop for p in pg])
    return A[keep].sum() / E[keep].sum(), sorted(drop)

def test1(F, pg, upages, rng, r):
    obs, drop = T3(F, pg, upages); null = np.array([T3(shuf(F, rng), pg, upages)[0] for _ in range(r)])
    return float(obs), drop, float((1 + (null >= obs).sum()) / (r + 1))

def gates1(F, pg, upages, rng):
    fp = pw = cc = 0
    for _ in range(NG):
        S = shuf(F, rng)
        fp += test1(S, pg, upages, rng, RG)[2] <= ALPHA
        pw += test1(plant(S, rng, 0.80), pg, upages, rng, RG)[2] <= ALPHA
        three = set(rng.choice(upages, 3, replace=False)); m = np.array([p in three for p in pg])
        cc += test1(plant(S, rng, 1.0, m), pg, upages, rng, RG)[2] > ALPHA
    return dict(FPR=f'{fp}/{NG}', power=f'{pw}/{NG}', concentration_called_fragile=f'{cc}/{NG}',
                ok=fp <= 2 and pw >= 16 and cc >= 16)

# ---------- H2
def T2(A, E, top):
    return A[top].sum() / E[top].sum() - A[~top].sum() / E[~top].sum()

def test2(F, top, groups, rng, r):
    A, E = AE1(F); obs = T2(A, E, top); null = np.empty(r)
    for i in range(r):
        lab = top.copy()
        for g in groups: lab[g] = top[g][rng.permutation(len(g))]
        null[i] = T2(A, E, lab)
    return float(obs), float((1 + (null >= obs).sum()) / (r + 1))

def gates2(F, top, groups, rng):
    fp = pw = 0
    for _ in range(NG):
        S = shuf(F, rng)
        fp += test2(S, top, groups, rng, RG)[1] <= ALPHA
        pw += test2(plant(S, rng, 0.80, top), top, groups, rng, RG)[1] <= ALPHA
    return dict(FPR=f'{fp}/{NG}', power=f'{pw}/{NG}', ok=fp <= 2 and pw >= 16)

def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0] * len(ps); run = 0
    for k, i in enumerate(o): run = max(run, min(1, (len(ps) - k) * ps[i])); adj[i] = run
    return adj

def rat(F):
    A, E = AE1(F); return dict(lines=len(F), A=int(A.sum()), E=round(float(E.sum()), 4), ratio=round(float(A.sum() / E.sum()), 4))

def main(outp):
    t0 = time.time(); rng = np.random.default_rng(SEED); grng = np.random.default_rng(GSEED)
    out = dict(seed=SEED, gate_seed=GSEED, R1=R1, R2=R2, H1={}, H2={}, descriptive={}, audit_C100={})
    for tn, path in FILES:
        L = parse(path); top = [l for l in L if l['top']]
        q20 = [l for l in top if l['Q'] == 'T']; Fq = fl(q20, CLS['pf']); pg = np.array([l['page'] for l in q20])
        up = sorted(set(pg))
        # audit C100
        out['audit_C100'][tn] = dict(Q20_pf=rat(Fq), B_other_pf=rat(fl([l for l in top if l['Q'] != 'T' and l['L'] == 'B'], CLS['pf'])),
                                     Q20_t=rat(fl(q20, CLS['t'])))
        # H1
        obs, drop, p = test1(Fq, pg, up, rng, R1)
        A, E = AE1(Fq)
        per = sorted([(p_, int(A[pg == p_].sum()), round(float(E[pg == p_].sum()), 2), int((pg == p_).sum())) for p_ in up],
                     key=lambda r: -(r[1] - r[2]))
        loo = [float(A[pg != p_].sum() / E[pg != p_].sum()) for p_ in up]
        out['H1'][tn] = dict(pages=len(up), full_ratio=float(A.sum() / E.sum()), T3=obs, dropped=drop, p=p,
                             gate=gates1(Fq, pg, up, grng), loo_min=min(loo), loo_max=max(loo), per_page_top8=per[:8])
        print(tn, 'H1 done', round(time.time() - t0, 1), flush=True)
        # H2: Currier B paragraph lines
        B = [l for l in L if l['L'] == 'B']; topB = np.array([l['top'] for l in B]); pgB = np.array([l['page'] for l in B])
        groups = [np.flatnonzero(pgB == p_) for p_ in sorted(set(pgB))]
        for c in ('t', 'k'):
            F = fl(B, CLS[c]); T, p = test2(F, topB, groups, rng, R2)
            out['H2'][f'{c}|{tn}'] = dict(T=T, p=p, gate=gates2(F, topB, groups, grng))
        d = {}
        for c in CLS:
            for name, sel in (('B_top', [l for l in B if l['top']]), ('B_nontop', [l for l in B if not l['top']]),
                              ('Q20_top', q20), ('Q20_nontop', [l for l in L if l['Q'] == 'T' and not l['top']]),
                              ('A_top', [l for l in L if l['L'] == 'A' and l['top']]), ('A_nontop', [l for l in L if l['L'] == 'A' and not l['top']])):
                d[f'{c}|{name}'] = rat(fl(sel, CLS[c]))
        out['descriptive'][tn] = d
        print(tn, 'H2 done', round(time.time() - t0, 1), flush=True)
    # verdicts
    v = {}
    cs = [out['H1'][tn] for tn, _ in FILES]
    if not all(c['gate']['ok'] for c in cs): v['H1'] = 'NOT TESTABLE'
    else:
        rej = sum(c['p'] <= ALPHA for c in cs); v['H1'] = 'ROBUST (not carried by <=3 pages)' if rej == 2 else 'PARTIAL' if rej == 1 else 'FRAGILE'
    ks = [k for k in out['H2'] if out['H2'][k]['gate']['ok']]
    for k, a in zip(ks, holm([out['H2'][k]['p'] for k in ks])): out['H2'][k]['p_holm'] = a
    for c in ('t', 'k'):
        cs = [out['H2'][f'{c}|{tn}'] for tn, _ in FILES]
        if not all(x['gate']['ok'] for x in cs): v[f'H2_{c}'] = 'NOT TESTABLE'
        else:
            rej = sum(x['p_holm'] < ALPHA for x in cs)
            v[f'H2_{c}'] = 'TOP-LINE LAW' if rej == 2 else 'PARTIAL' if rej == 1 else 'NOT TOP-SPECIFIC (not detected)'
    out['verdict'] = v; out['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(out, open(outp, 'w'), indent=1, default=str)
    for k in ('H1', 'H2', 'audit_C100', 'verdict', 'elapsed_s'): print(k, json.dumps(out[k], default=str))

if __name__ == '__main__':
    main(sys.argv[1])
