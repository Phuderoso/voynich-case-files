#!/usr/bin/env python3
"""C086 design step (before the pre-registration push; I-119 gate self-calibration after Kryptos; spent/non-registered
seeds only).  (1) Init-to-init spread of the manuscript's own topic gain X: the C084 statistic re-measured on ZL 3b and
IT2a, W1/W2, with R = 9 null reassignments and 8 non-registered seeds (9086xx) -> sets the topic band.
(2) Exchangeable-draw rates on the SPENT C084 generator runs (C005 config, 30 runs, seeds 11286-11315):
  P(a run is INSIDE the min-max range of 20 others), P(called ABOVE/BELOW with the 2-sd margin), held-out gate pass rate.
(3) Three-run-mean noise of X and surface from the same spent runs (band / +-15% rule false-call rates).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ[_v] = '1'
from multiprocessing import Pool
from math import comb
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c084_page_topics as T

def main():
    winZ, pZ, _, _ = T.ms_windows('data/ZL3b-n.txt'); winI, pI, _, _ = T.ms_windows('data/IT2a-n.txt')
    jobs = [(f'{t}_{w}_{i}', [P[p] for p in W[w]], 9, 908600 + 10 * i + k)
            for i in range(8) for k, (t, P, W) in enumerate((('ZL3b', pZ, winZ), ('IT2a', pI, winI))) for w in ('W1', 'W2')]
    with Pool(8) as pool: R = dict(pool.map(T.test, jobs, chunksize=1))
    out = {'ms_repeats': {}}
    for t in ('ZL3b', 'IT2a'):
        for w in ('W1', 'W2'):
            xs = [R[f'{t}_{w}_{i}']['X'] for i in range(8)]
            out['ms_repeats'][f'{t}_{w}'] = dict(X=xs, mean=float(np.mean(xs)), sd=float(np.std(xs, ddof=1)), min=min(xs), max=max(xs))
            print(t, w, [round(x, 3) for x in xs], 'mean', round(np.mean(xs), 3), 'sd', round(np.std(xs, ddof=1), 3))
    c84 = json.load(open('analysis/C084_results.json'))['runs']
    sim = {}
    for w in ('W1', 'W2'):
        runs = [(c84[n]['X'], c84[n]['null_sd']) for n in c84 if (n.startswith('gen_ref_') or n.startswith('gen_hold_')) and n.endswith(w)]
        inside = abc = 0; rng = np.random.default_rng(8686); trials = 4000
        xs = np.array([r[0] for r in runs])
        for _ in range(trials):
            idx = rng.permutation(len(runs)); x, sd = runs[idx[0]]; ref = xs[idx[1:21]]
            if ref.min() <= x <= ref.max(): inside += 1
            if x - 2 * sd > ref.max() or x + 2 * sd < ref.min(): abc += 1
        p_out = abc / trials
        g3 = sum(comb(10, k) * p_out ** k * (1 - p_out) ** (10 - k) for k in range(3))
        sim[w] = dict(n_runs=len(runs), between_run_sd=float(xs.std(ddof=1)), three_run_mean_sd=float(xs.std(ddof=1) / np.sqrt(3)),
                      p_inside=inside / trials, p_called_out=p_out, G3_pass=g3)
        print(w, sim[w])
    out['exchangeable'] = sim
    tr = json.load(open('analysis/C083_train.json'))['cells']
    c64 = [c for c in tr if c['cell'] == 64][0]
    out['c083_c005_surface_runs'] = c64.get('surf_mean')
    json.dump(out, open('analysis/C086_design.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
