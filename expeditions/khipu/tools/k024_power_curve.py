#!/usr/bin/env python3
"""K024 disclosed add-on (not pre-registered; cannot change the verdict): planted power for 3, 5 and 8 planted parents
(100 control corpora each, K = 1000), to say how strong a deeper-level habit would have to be to be seen."""
import json, numpy as np
src = open('tools/k024_deeper_subsidiary_sums.py').read().split('res = dict(')[0]
exec(src.replace('20261109', '20261110'))
allp = [(ui, j) for ui, u in enumerate(units) for j in range(len(u['pv']))]; out = {}
for npl in (3, 5, 8):
    pw = 0
    for t in range(100):
        svs = [perm(u['sv'], 1)[0].copy() for u in units]; pvs = [u['pv'].copy() for u in units]
        for k in rng.choice(len(allp), npl, replace=False):
            ui, j = allp[k]; ix = np.where(units[ui]['M'][:, j] == 1)[0]; s = svs[ui]
            if (s[ix] > 0).sum() < 2: s[ix[:2]] = np.maximum(s[ix[:2]], rng.integers(1, 30, 2))
            if s[ix].sum() < 10: s[ix[0]] += 10 - s[ix].sum()
            pvs[ui][j] = s[ix].sum()
        pw += corpus_test(units, 1000, svs=svs, pvs=pvs)[2] <= 0.01
    out[npl] = pw / 100; print(npl, pw / 100, flush=True)
json.dump(dict(power_by_planted=out, n_eligible=len(allp)), open('analysis/k024_power_curve.json', 'w'), indent=1)
