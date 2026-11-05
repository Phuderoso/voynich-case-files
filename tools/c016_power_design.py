#!/usr/bin/env python3
"""C016 DESIGN STEP (run and published before the pre-registration of the verdict test).
Planted power of a same-page running-text null for single label features, in the two counted datasets, computed
ONLY from pseudo-labels drawn from running text. No feature of any real label word is computed here: the labels
enter only through their count per page (inventory).
Output: analysis/C016_power_design.json
Usage: python3 tools/c016_power_design.py"""
import json, time, sys
import numpy as np
sys.path.insert(0, 'tools')
from c016_common import DATASETS, FEATURES, parse, Sampler, Planter, pval, feat

ALPHA = 0.005          # 0.05 / 10 = Bonferroni over the maximum of 5 features x 2 counted datasets, fixed in advance
R = 9999; REPS = 200
GRID = {'o_init': [0.05, 0.10, 0.15, 0.20, 0.30], 'y_fin': [0.05, 0.10, 0.15, 0.20, 0.30],
        'q_init': [0.05, 0.10, 0.15, 0.20, 0.30], 'gallows': [0.05, 0.10, 0.15, 0.20, 0.30],
        'len': [0.2, 0.4, 0.6, 0.8, 1.0]}
OUT = 'analysis/C016_power_design.json'

def main():
    t0 = time.time(); res = {'alpha': ALPHA, 'R': R, 'reps': REPS, 'grid': GRID, 'datasets': {}}
    for di, name in enumerate(['D1_ZL_heldout', 'D2_IT_C015loci']):
        src, pred = DATASETS[name]
        labels, running, _, _ = parse(src, pred)
        S = Sampler(labels, running); P = Planter(S.pool)
        inv = {'src': src, 'label_tokens': len(labels), 'loci': len({(p, l) for p, l, _ in labels}),
               'pages': {p: k for p, k in sorted(S.pc.items())}, 'pages_pooled': S.pooled_pages,
               'running_tokens_on_label_pages': len(S.pool)}
        rng = np.random.default_rng(16000 + di)
        null = S.null_matrix(rng, R, FEATURES)
        d = {'inventory': inv, 'null_mean': dict(zip(FEATURES, np.round(null.mean(0), 4).tolist())),
             'null_sd': dict(zip(FEATURES, np.round(null.std(0), 4).tolist())), 'power': {}, 'fpr': {}}
        for fi, f in enumerate(FEATURES):
            prng = np.random.default_rng(16100 + 10 * di + fi)
            # FPR: unplanted pseudo-labels
            ps = [pval(np.mean([feat(w, f) for w in S.draw(prng)]), null[:, fi])[0] for _ in range(REPS)]
            d['fpr'][f] = {'at_0.05': float(np.mean(np.array(ps) <= 0.05)), 'at_alpha': float(np.mean(np.array(ps) <= ALPHA))}
            d['power'][f] = {}
            for delta in GRID[f]:
                row = {}
                for sgn, lab in ((1, 'up'), (-1, 'down')):
                    hits = 0
                    for _ in range(REPS):
                        w = P.apply(S.draw(prng), f, sgn * delta, prng)
                        p, dr = pval(np.mean([feat(x, f) for x in w]), null[:, fi])
                        hits += (p <= ALPHA and dr == ('more' if sgn > 0 else 'less'))
                    row[lab] = hits / REPS
                d['power'][f][str(delta)] = row
            ok = [dl for dl in GRID[f] if min(d['power'][f][str(dl)].values()) >= 0.9]
            d.setdefault('delta_star', {})[f] = ok[0] if ok else None
            print(f'[{time.time()-t0:6.1f}s] {name} {f} power={d["power"][f]} delta*={d["delta_star"][f]} fpr={d["fpr"][f]}', flush=True)
        res['datasets'][name] = d
        res['elapsed_s'] = round(time.time() - t0, 1)
        json.dump(res, open(OUT, 'w'), indent=1)
    print(json.dumps({k: {'inventory': {kk: v['inventory'][kk] for kk in ('label_tokens', 'loci', 'pages_pooled', 'running_tokens_on_label_pages')}, 'delta_star': v['delta_star']} for k, v in res['datasets'].items()}, indent=1))

if __name__ == '__main__':
    main()
