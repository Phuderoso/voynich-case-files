#!/usr/bin/env python3
# Run from the repo root: timeout 300 python3 tools/c065_posthoc_s2_settings.py  -- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
# C065 post-hoc, exploratory (NOT pre-registered): hapax share S2 at N=5000 across a few generator settings, 10 runs each, seeds 7001+.
import sys, json; sys.path.insert(0, 'tools')
from multiprocessing import Pool
import c055_burstiness as C, c003_position_rigidity as T
from c004_generator_sweep import generate
N = 5000
SET = {'P1 suggestions.probability=0': {'method.suggestions.probability': 0},
       'P2 suggestions=none': {'method.suggestions': 'none'},
       'P3 canFollow.error_rate=10': {'method.canFollow.error_rate': 10},
       'P4 replace.probability=100': {'method.morph.replace.probability': 100},
       'P5 add_remove.probability=80': {'method.morph.add_remove.probability': 80},
       'P6 canFollow=none': {'method.canFollow': 'none'}}
def job(a):
    i, k, s = a; cfg = dict(SET[k]); cfg['text.lines_to_create'] = 3400
    L = generate(cfg, s); t = [tuple(T.units(w)) for w in C.flat(L)] if L else []
    if len(t) < N: return k, None
    t = t[:N]; c = {}
    for w in t: c[w] = c.get(w, 0) + 1
    return k, sum(v == 1 for v in c.values()) / len(c)
jobs = [(i, k, 7001 + 100 * i + j) for i, k in enumerate(SET) for j in range(10)]
with Pool(8) as P: r = P.map(job, jobs, chunksize=1)
out = {k: sorted(v for kk, v in r if kk == k and v is not None) for k in SET}
for k, v in out.items(): print(k, len(v), round(min(v), 3) if v else None, round(max(v), 3) if v else None)
json.dump(dict(seeds='7001+100*i+j, j<10', N=N, s2=out), open('analysis/C065_posthoc_S2_settings.json', 'w'), indent=1)
