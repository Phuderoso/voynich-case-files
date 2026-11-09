#!/usr/bin/env python3
"""C068 POST-HOC (not pre-registered, run after the results): per-run Dc deltas of the default and spp0 generator runs
(same seeds and code as the main run), to place the manuscript inside each range. Descriptive only.
Run: python3 tools/c068_posthoc_generator_ranks.py   -- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, json; sys.path.insert(0, 'tools')
from multiprocessing import Pool
import c068_vertical_alignment as V
with Pool(8) as p: res = p.map(V.gen_job, [('default', s) for s in range(9101, 9121)] + [('spp0', s) for s in range(9201, 9221)])
for n in ('default', 'spp0'):
    d = sorted(round(r['Dc']['delta'], 4) for nm, s, r in res if nm == n and r)
    print(n, 'Dc deltas', d, 'below 0.0100:', sum(x < 0.0100 for x in d), 'below 0.0096:', sum(x < 0.0096 for x in d))
