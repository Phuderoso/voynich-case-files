#!/usr/bin/env python3
"""POST HOC (not preregistered, descriptive): mean STRAT draw max per N level and per window, and the slope per e-fold between successive levels,
to see whether the search-size curve is concave (extreme-value shape), i.e. whether the single b_A of T1 hides a slope that falls with N.
Uses the preregistered tool unchanged; seed 11857 (reserved in PREREG section 6, now used)."""
import numpy as np, math, json
import i342_subsample as t
C = t.load(t.DEF_R, True)
rng = np.random.default_rng(11857)
D = t.draws(C, rng, t.R_POINT)
S = D['design'] == 0
out = []
print('level  meanN  mean_max   (STRAT, all pools equally weighted per draw)')
mm = []; lN = []
for L in t.LEVELS:
    m = S & (D['L'] == L)
    mm.append(D['mx'][m].mean()); lN.append(np.log(D['N'][m]).mean())
    print(L, round(float(D['N'][m].mean()), 1), round(float(mm[-1]), 4), 'draws', int(m.sum()))
print('slope per e-fold between successive levels (differences of the level means; pool mix differs by level because of support, so see the paired version below):')
# paired version: only pools supported at every level
for a, b in zip(t.LEVELS[:-1], t.LEVELS[1:]):
    num = []; 
    for f in range(len(t.FAMS)):
        for w in range(len(t.WINS)):
            ma = S & (D['L'] == a) & (D['fam'] == f) & (D['w'] == w); mb = S & (D['L'] == b) & (D['fam'] == f) & (D['w'] == w)
            if ma.any() and mb.any():
                num.append((D['mx'][mb].mean() - D['mx'][ma].mean()) / (np.log(D['N'][mb]).mean() - np.log(D['N'][ma]).mean()))
    print(f'  {a}->{b}: mean slope {np.mean(num):.4f} over {len(num)} (family,window) pools; range {min(num):.4f}..{max(num):.4f}')
print('mean max by window at each level (all families pooled equally):')
for w, (lo, hi) in enumerate(t.WINS):
    print(f'  nq {lo}-{hi}:', [round(float(D['mx'][S & (D['L'] == L) & (D['w'] == w)].mean()), 3) if (S & (D['L'] == L) & (D['w'] == w)).any() else None for L in t.LEVELS])
