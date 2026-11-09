#!/usr/bin/env python3
"""C086 EXPLORATORY (after the confirmatory run, no confirmatory weight): topic X (R 9) on the training seeds 11391-11393
for three near-miss cells chosen AFTER seeing the surface table: 3 (closest overall surface, page chooser),
102 (closest among TTR-feasible cells, position chooser), 39 (TTR-feasible, page chooser).  Output: analysis/C086_exploratory.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ[_v] = '1'
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c086_joint as J
CELLS = [3, 102, 39]
if __name__ == '__main__':
    cells = J.grid(); sizes, _ = J.ms_pages(); band = J.load_ms()
    with Pool(8) as pool:
        GR = pool.map(J.gen, [(c, cells[c], s) for c in CELLS for s in J.TRAIN], chunksize=1)
        jobs = []
        for i, (c, s, L, st) in enumerate(GR): jobs += J.xjobs_for(f'c{c}_s{s}', L, sizes, 9, 868600000 + 2 * i)
        XR = dict(pool.map(J.xjob, jobs, chunksize=1))
    out = {}
    for c in CELLS:
        out[c] = {w: [XR[f'c{c}_s{s}_{w}']['X'] for s in J.TRAIN] for w in ('W1', 'W2')}
        out[c]['mean'] = {w: float(np.mean(out[c][w])) for w in ('W1', 'W2')}
        print(c, {w: round(v, 3) for w, v in out[c]['mean'].items()}, 'band', band)
    json.dump(out, open('analysis/C086_exploratory.json', 'w'), indent=1)
