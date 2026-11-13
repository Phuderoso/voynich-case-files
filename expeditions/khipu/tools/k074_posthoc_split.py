#!/usr/bin/env python3
"""K074 post hoc (disclosed, after the registered run): where does the P3 boundary (H1) change come from?
Splits P3 (all KFG khipus with a sum cord, primary coding) into khipus also in the OKR vs KFG-only, and into the 10 OKR BH
names vs the rest. Same K021 engine (loaded from tools/k074_kfg_sum_cord_colour.py up to its population block), R 20 000.
Seed 6427; next free 6428. Descriptive only: no verdict of K074 changes."""
import sys
src = open('tools/k074_kfg_sum_cord_colour.py').read().split('out = {}')[0]
src = src.replace("OUT = 'analysis/k074_smoke.json' if SMOKE else 'analysis/k074_results.json'", "OUT = 'analysis/k074_posthoc_split.json'")
src = src.replace('SEED = 6426; NEXT_FREE = 6427', 'SEED = 6427; NEXT_FREE = 6428')
exec(src)
okr_names = {v for v in okrname.values() if v}
us = make_units(kfg, c_prim, lambda n: n)
res['posthoc'] = {lab: run(sel, lab) for lab, sel in (
    ('in_okr', [u for u in us if u['name'] in okr_names]), ('kfg_only', [u for u in us if u['name'] not in okr_names]),
    ('not_okr_bh', [u for u in us if u['name'] not in okr_bh]))}
for a, b in res['posthoc'].items(): print(a, {x: b[x] for x in ('n_khipus', 'n_sum', 'T1', 'T1_null_mean', 'p1', 'power_H1', 'calib_fpr_H1', 'T2', 'T2_null_mean', 'p2')})
dump()
