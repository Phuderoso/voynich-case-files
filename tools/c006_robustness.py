#!/usr/bin/env python3
"""C006 post-hoc robustness (declared after the main run, not a pre-registered look): edge coupling C for Voynich
with commas kept inside words, and by Currier language A/B."""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3, c006_line_pairs_edges as c6
out = {}
for name, kw in (('V_commas_kept', dict(split_commas=False)), ('V_lang_A', dict(lang='A')), ('V_lang_B', dict(lang='B'))):
    L = c3.voynich(**kw); rng = random.Random(66)
    S = [c6.sample(L, rng) for _ in range(c6.NS)]
    out[name] = c6.ci([c6.M2(s, c3.units, rng) for s in S]); print(name, out[name], flush=True)
json.dump(out, open('analysis/C006_robustness.json', 'w'), indent=1)
