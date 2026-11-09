#!/usr/bin/env python3
"""C094 design aid (references only, descriptive, NOT a test): G2 power of the C093 one-edit copying plant against the 20
pooled generator runs as the planted share F grows, at K = 2,000 / 3,000 / 4,000, so that C095 can pre-register a plant
strength (or a different reference) BEFORE seeing anything. Seed 9494 (plants), generator seeds 11474-11493.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c093_edit_graph as E
import c003_position_rigidity as T
FS, KS, GS = (0.10, 0.15, 0.20, 0.30), (2000, 3000, 4000), list(range(11474, 11494))
def job(s):
    import c004_generator_sweep as G
    ws = [tuple(T.units(w)) for l in (G.generate({'text.lines_to_create': 8000}, s) or []) for w in l]
    out = {'ref': {k: E.measure(ws, k)['RHO'] for k in KS}}
    for F in FS:
        pw = E.plant(ws, np.random.default_rng([9494, s]), F); out[F] = {k: E.measure(pw, k)['RHO'] for k in KS}
    return s, out
if __name__ == '__main__':
    with Pool(8) as p: R = dict(p.map(job, GS))
    res = {}
    for k in KS:
        for F in FS:
            pw = sum(E.pt(R[s][F][k], [R[o]['ref'][k] for o in GS if o != s]) < 0.05 for s in GS)
            sh = float(np.mean([R[s][F][k] - R[s]['ref'][k] for s in GS])); res[f'K{k}_F{F}'] = dict(power=f'{pw}/20', shift=sh)
            print(k, F, f'{pw}/20', round(sh, 4))
    json.dump(res, open(sys.argv[1], 'w'), indent=1)
