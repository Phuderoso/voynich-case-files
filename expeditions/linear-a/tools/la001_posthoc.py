#!/usr/bin/env python3
"""LA001 post-hoc (disclosed after the run; no verdict change): exact enumeration of the stratified
permutation null for E, and a power curve over the number of planted balances k. Pimpolha Voynich, do Phuderoso."""
import json, itertools, numpy as np, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from la001_kuro_totals import build, stratum, perm_test
_, dec = build()
S = np.array([sum(s['entries']) for s in dec]); T = np.array([s['total'] for s in dec]); n = len(T)
st = np.array([stratum(t) for t in T]); E0 = int(np.sum(S == T))
groups = [list(np.where(st == g)[0]) for g in np.unique(st)]
dist = {}; tot = 0
for combo in itertools.product(*[list(itertools.permutations(g)) for g in groups]):
    Tp = T.copy()
    for g, p in zip(groups, combo): Tp[g] = T[list(p)]
    e = int(np.sum(S == Tp)); dist[e] = dist.get(e, 0) + 1; tot += 1
p_exact = sum(v for k, v in dist.items() if k >= E0) / tot
rng = np.random.default_rng(2002); curve = {}
for k in (3, 4, 5, 6):
    hit = 0
    for _ in range(200):
        Tn = T[rng.permutation(n)].copy(); pick = rng.choice(n, k, replace=False); Tn[pick] = S[pick]
        _, _, pe, _ = perm_test(S, Tn, np.array([stratum(t) for t in Tn]), rng, 2000); hit += pe <= 0.05
    curve[k] = hit / 200
out = dict(E_obs=E0, n_perms=tot, null_dist=dict(sorted(dist.items())), p_exact=p_exact, power_curve_H1=curve, seed=2002)
json.dump(out, open('la001_posthoc.json', 'w'), indent=1); print(out)
