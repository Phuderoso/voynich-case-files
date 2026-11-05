#!/usr/bin/env python3
"""C003 sensitivity (exploratory, added after main run): (a) the authors' own published self-citation sample (G0,
TorstenTimm/SelfCitationTextgenerator executable/generate/generated_text.txt, default config, seed 19);
(b) rare glyph types (< 0.5 % of tokens) merged into one symbol, to check that alphabet-size differences don't drive R."""
import sys, re, json, random
from collections import Counter
sys.path.insert(0, 'tools'); import c003_position_rigidity as c
C = 'data/corpora/'
G0 = [l for l in ([re.findall(r'[a-z]+', x) for x in open(C + 'ts_generated_text.txt') if not x.startswith('#')]) if l]
T = {'V': (c.voynich(), None), 'G0_timm_schinner_sample': (G0, None), 'HE': (c.hebrew(C + 'Gen.xml'), list),
     'IT_dante': (c.gutenberg(C + 'pg1012.txt'), list), 'LA_caesar': (c.gutenberg(C + 'pg218.txt'), list)}
out = {}
for k, (L, tk) in T.items():
    base = (lambda w: list(w)) if tk else c.units
    out[k] = c.boot(L, random.Random(7), tok=base)
    f = Counter(g for l in L for w in l for g in base(w)); n = sum(f.values())
    keep = {g for g, v in f.items() if v / n >= 0.005}
    out[k + '_rare_merged'] = c.boot(L, random.Random(7), tok=lambda w: [g if g in keep else '#' for g in base(w)])
    out[k + '_rare_merged']['alphabet'] = len(keep) + 1
    print(k, round(out[k]['R_mean'], 3), round(out[k]['R_lo'], 3), round(out[k]['R_hi'], 3), '| merged',
          round(out[k + '_rare_merged']['R_mean'], 3), out[k + '_rare_merged']['alphabet'], flush=True)
json.dump(out, open('analysis/C003_sensitivity.json', 'w'), indent=1)
