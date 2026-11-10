#!/usr/bin/env python3
"""C102 POST HOC (descriptive only, not registered, no verdict): two cheap probes of what carries C102's persistence.
(a) D recomputed with pairs of IDENTICAL adjacent words dropped (same drop applied inside each null draw), R = 200;
(b) mean interior word length by position 2..7 (a smooth within-line drift would also make adjacent lengths persist).
Seed 11650. Run: timeout 300 python tools/c102_posthoc.py analysis/C102_posthoc.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import parse, FILES
from c003_position_rigidity import units
rng = np.random.default_rng(11650); out = {}
for k, f in FILES:
    for L in 'AB':
        W = [l['words'][1:-1] for l in parse(f) if l['L'] == L]
        def r_noid(lines):
            a = []; b = []
            for x in lines:
                for i in range(len(x) - 1):
                    if x[i] != x[i + 1]: a.append(len(units(x[i]))); b.append(len(units(x[i + 1])))
            return float(np.corrcoef(a, b)[0, 1])
        ident = sum(x[i] == x[i + 1] for x in W for i in range(len(x) - 1)); pairs = sum(len(x) - 1 for x in W)
        obs = r_noid(W); nl = np.array([r_noid([list(rng.permutation(x)) for x in W]) for _ in range(200)])
        pos = {p: float(np.mean([len(units(x[p - 2])) for x in W if len(x) > p - 2])) for p in range(2, 8)}
        out[f'{k}|{L}'] = dict(identical_pairs=int(ident), pairs=int(pairs), r_noid=obs, null_mean=float(nl.mean()),
                              D_noid=float(obs - nl.mean()), z=float((obs - nl.mean()) / nl.std()), mean_len_by_pos=pos)
        print(k, L, out[f'{k}|{L}'], flush=True)
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else 'analysis/C102_posthoc.json', 'w'), indent=1)
