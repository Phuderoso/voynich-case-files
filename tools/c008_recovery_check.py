#!/usr/bin/env python3
"""C008 post-hoc recovery check (declared after the main run): apply rules S and G at p=1 with table T to Voynich itself
after shuffling word order within lines (coupling destroyed). How much of C = 0.204 does each rule restore?"""
import os, sys, json, random
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3, c006_line_pairs_edges as c6, c008_cross_word_rules as c8
T, T0, m = c8.tables(); V = c3.voynich(); rng = random.Random(88); out = {}
for name in ('shuffled', 'S', 'G', 'G_lastunit_marginal_note'):
    if name.endswith('note'): continue
    vals = []
    for k in range(10):
        s = c6.shuffle_within(c6.sample(V, rng), rng)
        if name != 'shuffled': s = c8.apply(s, name, 1.0, T, m, 1000 + k)
        vals.append(c6.M2(s, c3.units, rng))
    out[name] = dict(mean=float(np.mean(vals)), lo=float(np.min(vals)), hi=float(np.max(vals))); print(name, out[name])
json.dump(out, open('analysis/C008_recovery_check.json', 'w'), indent=1)
