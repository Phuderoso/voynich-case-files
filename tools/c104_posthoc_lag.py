#!/usr/bin/env python3
"""C104 post hoc (NOT registered; disclosed as a correction to the C104 reading rule). The registered H1a pair (last kept
word of line i, first kept word of line i+1) skips three dropped words (last word of i, words 1 and 2 of i+1), so in
running text it is a LAG-4 pair, not an adjacent one. The fair layout-only comparator is the within-line lag-k
persistence. Here: interior words (C102: positions 2..n-1, lines >= 5 words) and C103 kept words (3..n-1, lines >= 6);
pooled Pearson r of (len_j, len_j+k) inside lines vs within-line permutation null, k = 1..4, R = 500, seed 11697.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import parse, FILES
from c003_position_rigidity import units
rng = np.random.default_rng(11697); R = 500; out = {}
def rk(L, k):
    a = np.concatenate([x[:-k] for x in L if len(x) > k]); b = np.concatenate([x[k:] for x in L if len(x) > k]); return float(np.corrcoef(a, b)[0, 1]), len(a)
for name, f in FILES:
    P = parse(f)
    for Lg in 'AB':
        for tag, sl, mn in (('interior2..n-1', slice(1, -1), 5), ('kept3..n-1', slice(2, -1), 6)):
            L = [np.array([len(units(w)) for w in l['words'][sl]], float) for l in P if l['L'] == Lg and len(l['words']) >= mn]
            for k in range(1, 5):
                obs, n = rk(L, k); nl = np.array([rk([rng.permutation(x) for x in L], k)[0] for _ in range(R)])
                m = nl.mean(); p = (1 + (np.abs(nl - m) >= abs(obs - m)).sum()) / (R + 1)
                out[f'{name}|{Lg}|{tag}|lag{k}'] = dict(r=obs, pairs=n, D=float(obs - m), sd=float(nl.std()), p=float(p))
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else 'analysis/C104_posthoc_lag.json', 'w'), indent=1)
for k, v in out.items(): print(k, round(v['D'], 4), round(v['sd'], 4), v['pairs'], round(v['p'], 4))
