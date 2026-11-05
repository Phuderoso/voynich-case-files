#!/usr/bin/env python3
"""K023 disclosed sensitivity (not pre-registered; cannot upgrade the verdict): (a) Monte Carlo stability of p over 5 seeds
x 20 000; (b) drop KH0502 (UR266), the published twin of UR275 (KH0514, in the K021/K022 set), so not fully held out."""
import json, numpy as np
src = open('tools/k022_sum_summand_colour.py').read().split('prim = [it')[0]
exec(src)
ink = {r[0] for r in c.execute("select OKR_NUM from khipu_main where PROVENANCE='Incahuasi'")}
hold = [it for it in items if it['okr'] in ink and it['okr'] not in sigk]
def p_lo(o, nl): return float((1 + (nl <= o + 1e-12).sum()) / (1 + len(nl)))
out = {}
for name, its in (('all_heldout', hold), ('without_KH0502', [it for it in hold if it['okr'] != 'KH0502'])):
    A = sum(it['obs'] for it in its); ps = []
    for s in range(5):
        rng = np.random.default_rng(1000 + s); ps.append(p_lo(A, null_draw(its, R)))
    out[name] = dict(n=len(its), A=A, p_by_seed=ps, p_mean=float(np.mean(ps)))
json.dump(out, open('analysis/k023_sensitivity.json', 'w'), indent=1); print(json.dumps(out, indent=1))
