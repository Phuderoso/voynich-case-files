#!/usr/bin/env python3
"""C017 COUNTED RUN: do drawing-element labels (BIO, ROS, AZ, PP) differ from free-standing L0 labels in their excess
over their own pages' running text? Page-level ((page, class) unit) permutation null, 5 single features, ZL 3b and IT2a.
Pre-registered in case-file/C017-label-genre-contrast.md (power design: analysis/C017_power_design.json).
Output: analysis/C017_results.json.  Usage: timeout 600 python3 tools/c017_label_genre.py"""
import json, time, sys
import numpy as np
sys.path.insert(0, 'tools')
from c017_common import Design, plant, FILES, FEATURES, A_CLASSES, use_blocked, blocked_perms
from c016_common import Planter, units

ALPHA = 0.0035; R = 9999; GATE_REPS = 100; GATE_MIN = 90; FPR_DRAWS = 1000
FPR_LIM = (0.08, 0.012)
DESIGN = json.load(open('analysis/C017_power_design.json'))
TAU = DESIGN['tau_design']; OUT = 'analysis/C017_results.json'
import os
if os.environ.get('C017_SMOKE'):      # code-path check only: tiny sizes, output to /tmp, never read
    R, GATE_REPS, GATE_MIN, FPR_DRAWS, OUT = 99, 3, 3, 5, '/tmp/c017_smoke.json'

def main():
    t0 = time.time(); res = {'alpha': ALPHA, 'R': R, 'datasets': {}, 'started': time.strftime('%Y-%m-%d %H:%M:%S %Z')}
    for di, name in enumerate(['ZL', 'IT']):
        D = use_blocked(Design(FILES[name], R, 17050 + di), R, 17080 + di); P = Planter(D.pool); A = D.g == 1
        real = D.real_words(); d = {'inventory': D.inventory(), 'looks': {}, 'descriptive': {}}
        for fi, f in enumerate(FEATURES):
            dc = DESIGN['datasets'][name]['contrast'][f]; dstar = dc['delta_star']
            e = D.excess(real, f); obs, p, dr = D.contrast_test(e)
            w = D.k
            lab_mean = {g: float(np.mean([__import__('c016_common').feat(x, f) for ws, gg in zip(real, D.g) if gg == g for x in ws])) for g in (1, 0)}
            exA = float((w[A] * e[A]).sum() / w[A].sum()); exB = float((w[~A] * e[~A]).sum() / w[~A].sum())
            rsd = D.resid_sd(e)
            look = {'delta_star': dstar, 'contrast': obs, 'p': p, 'direction': dr, 'excess_A': exA, 'excess_B': exB,
                    'label_mean_A': lab_mean[1], 'label_mean_B': lab_mean[0], 'resid_sd_real': rsd,
                    'resid_sd_design_p95': dc['resid_sd_tau_p95']}
            # FPR (unplanted, tau_design)
            rng = np.random.default_rng(17800 + 10 * di + fi)
            ps = np.array([D.contrast_test(D.excess(plant(D, P, D.pseudo(rng), f, A, 0.0, TAU[f], rng), f))[1] for _ in range(FPR_DRAWS)])
            look['fpr'] = {'at_0.05': float((ps <= 0.05).mean()), 'at_alpha': float((ps <= ALPHA).mean())}
            fpr_ok = look['fpr']['at_0.05'] <= FPR_LIM[0] and look['fpr']['at_alpha'] <= FPR_LIM[1]
            # gate
            if dstar is None:
                look['gate'] = None; gate_ok = False
            else:
                rng = np.random.default_rng(17600 + 10 * di + fi); g = {}
                for sgn, lab in ((1, 'up'), (-1, 'down')):
                    hits = 0
                    for _ in range(GATE_REPS):
                        _, pp, dd = D.contrast_test(D.excess(plant(D, P, D.pseudo(rng), f, A if sgn > 0 else ~A, dstar, TAU[f], rng), f))
                        hits += (pp <= ALPHA and dd == ('A>B' if sgn > 0 else 'A<B'))
                    g[lab] = int(hits)
                look['gate'] = g; gate_ok = min(g.values()) >= GATE_MIN
            if not gate_ok: v = 'not testable (no design power)' if dstar is None else 'not testable (gate failed)'
            elif not fpr_ok: v = 'withdrawn (false-positive check failed)'
            elif p <= ALPHA: v = f'contrast detected ({dr})'
            elif rsd > dc['resid_sd_tau_p95']: v = 'not testable (heterogeneity above design)'
            else: v = f'no contrast of {dstar} or more detected'
            look['verdict'] = v; d['looks'][f] = look
            print(f'[{time.time()-t0:6.1f}s] {name} {f}: C={obs:+.3f} p={p:.4f} {dr} exA={exA:+.3f} exB={exB:+.3f} rsd={rsd:.3f}/{dc["resid_sd_tau_p95"]:.3f} gate={look["gate"]} fpr={look["fpr"]} -> {v}', flush=True)
            res['datasets'][name] = d; json.dump(res, open(OUT, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
        # ---- descriptive, not counted ----
        desc = {}
        for f in FEATURES:
            e = D.excess(real, f)
            het_obs, het_p = D.hetero_test(e)
            per_class = {}
            for c in A_CLASSES + ('FREE',):
                m = np.array([cc == c for cc in D.cls])
                if m.any(): per_class[c] = {'tokens': int(D.k[m].sum()), 'units': int(m.sum()), 'excess': float((D.k[m] * e[m]).sum() / D.k[m].sum())}
            per_B_unit = {D.units[i][0]: {'k': int(D.k[i]), 'excess': float(e[i])} for i in range(len(D.units)) if D.cls[i] == 'FREE'}
            # leave-one-B-page-out for the two dominant pages
            loo = {}
            for drop in ('f67r2', 'f69r'):
                keep = [i for i in range(len(D.units)) if not (D.cls[i] == 'FREE' and D.units[i][0] == drop)]
                D2 = Design.__new__(Design); D2.__dict__.update(D.__dict__)
                D2.units = [D.units[i] for i in keep]; D2.k = D.k[keep]; D2.g = D.g[keep]; D2.cls = [D.cls[i] for i in keep]
                D2.Gperm = blocked_perms(D2.g, D2.k, R, 17900)
                o, pp, dd = D2.contrast_test(e[keep]); loo[f'drop_{drop}'] = {'contrast': o, 'p': pp, 'direction': dd}
            desc[f] = {'hetero_among_A_classes': {'stat': het_obs, 'p_one_sided': het_p}, 'per_class': per_class,
                       'per_B_unit': per_B_unit, 'leave_one_B_page_out': loo}
        d['descriptive'] = desc
        res['datasets'][name] = d; res['elapsed_s'] = round(time.time() - t0, 1)
        json.dump(res, open(OUT, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    res['finished'] = time.strftime('%Y-%m-%d %H:%M:%S %Z'); json.dump(res, open(OUT, 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
    print('done', res['elapsed_s'])

if __name__ == '__main__':
    main()
