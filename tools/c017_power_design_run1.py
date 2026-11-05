#!/usr/bin/env python3
"""C017 DESIGN STEP (run and published before the pre-registration of the verdict test).
Planted power of the page-level permutation tests (A-vs-B contrast; heterogeneity among drawing-element classes),
computed ONLY from pseudo-labels drawn from running text. Real labels enter only through their count per
(page, class) unit. No feature of any real label word is computed here.
Output: analysis/C017_power_design.json.  Usage: timeout 600 python3 tools/c017_power_design.py"""
import json, time, sys
import numpy as np
sys.path.insert(0, 'tools')
from c017_common import Design, plant, FILES, FEATURES, A_CLASSES
from c016_common import Planter

ALPHA = 0.0035          # 0.05 / 14 (max 5 contrast x 2 + 2 heterogeneity x 2), fixed in advance
R = 9999; REPS = 100
GRID = {f: [0.10, 0.20, 0.30, 0.40] for f in FEATURES}; GRID['len'] = [0.4, 0.8, 1.2, 1.6]
TAU = {f: 0.10 for f in FEATURES}; TAU['len'] = 0.5
HET_FEATS = ['o_init', 'q_init']
OUT = 'analysis/C017_power_design_run1_superseded.json'  # run 1 (superseded); originally wrote analysis/C017_power_design.json, renamed afterwards

def main():
    t0 = time.time(); res = {'alpha': ALPHA, 'R': R, 'reps': REPS, 'grid': GRID, 'tau_design': TAU, 'datasets': {}}
    for di, name in enumerate(['ZL', 'IT']):
        D = Design(FILES[name], R, 17000 + di); P = Planter(D.pool)
        d = {'inventory': D.inventory(), 'contrast': {}, 'hetero': {}}
        print(name, d['inventory'], flush=True)
        A = D.g == 1
        for fi, f in enumerate(FEATURES):
            rng = np.random.default_rng(17100 + 10 * di + fi)
            # unplanted at tau_design: FPR and residual-heterogeneity reference
            ps, hs = [], []
            for _ in range(200):
                uw = plant(D, P, D.pseudo(rng), f, A, 0.0, TAU[f], rng); e = D.excess(uw, f)
                ps.append(D.contrast_test(e)[1]); hs.append(D.resid_sd(e))
            cell = {'fpr_tau': {'at_0.05': float(np.mean(np.array(ps) <= 0.05)), 'at_alpha': float(np.mean(np.array(ps) <= ALPHA))},
                    'resid_sd_tau_p95': float(np.percentile(hs, 95)), 'resid_sd_tau_median': float(np.median(hs)), 'power': {}}
            for tau in (0.0, TAU[f]):
                for delta in GRID[f]:
                    row = {}
                    for sgn, lab in ((1, 'up'), (-1, 'down')):
                        hits = 0
                        for _ in range(REPS):
                            uw = plant(D, P, D.pseudo(rng), f, A, sgn * delta, tau, rng)
                            _, p, dr = D.contrast_test(D.excess(uw, f))
                            hits += (p <= ALPHA and dr == ('A>B' if sgn > 0 else 'A<B'))
                        row[lab] = hits / REPS
                    cell['power'][f'tau={tau}|delta={delta}'] = row
            ok = [dl for dl in GRID[f] if min(cell['power'][f'tau={TAU[f]}|delta={dl}'].values()) >= 0.9]
            cell['delta_star'] = ok[0] if ok else None
            d['contrast'][f] = cell
            print(f'[{time.time()-t0:6.1f}s] {name} contrast {f} d*={cell["delta_star"]} fpr={cell["fpr_tau"]} {cell["power"]}', flush=True)
            json.dump(res | {'datasets': res['datasets'] | {name: d}}, open(OUT, 'w'), indent=1)
        # heterogeneity among drawing-element classes: plant on BIO units
        tgt = np.array([c == 'BIO' for c in D.cls])
        for fi, f in enumerate(HET_FEATS):
            rng = np.random.default_rng(17500 + 10 * di + fi)
            ps = [D.hetero_test(D.excess(plant(D, P, D.pseudo(rng), f, tgt, 0.0, TAU[f], rng), f))[1] for _ in range(200)]
            cell = {'fpr_tau': {'at_0.05': float(np.mean(np.array(ps) <= 0.05)), 'at_alpha': float(np.mean(np.array(ps) <= ALPHA))}, 'power': {}}
            for delta in GRID[f]:
                row = {}
                for sgn, lab in ((1, 'up'), (-1, 'down')):
                    hits = sum(D.hetero_test(D.excess(plant(D, P, D.pseudo(rng), f, tgt, sgn * delta, TAU[f], rng), f))[1] <= ALPHA
                               for _ in range(REPS))
                    row[lab] = hits / REPS
                cell['power'][f'tau={TAU[f]}|delta={delta}'] = row
            ok = [dl for dl in GRID[f] if min(cell['power'][f'tau={TAU[f]}|delta={dl}'].values()) >= 0.9]
            cell['delta_star'] = ok[0] if ok else None
            d['hetero'][f] = cell
            print(f'[{time.time()-t0:6.1f}s] {name} hetero {f} d*={cell["delta_star"]} fpr={cell["fpr_tau"]} {cell["power"]}', flush=True)
        res['datasets'][name] = d; res['elapsed_s'] = round(time.time() - t0, 1)
        json.dump(res, open(OUT, 'w'), indent=1)
    print('done', res['elapsed_s'])

if __name__ == '__main__':
    main()
