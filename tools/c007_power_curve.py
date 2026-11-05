#!/usr/bin/env python3
"""C007 post-hoc power curve (declared after the pre-registered plant failed; exploratory, not a verdict):
distributed plant at line rates 0.2/0.5/1.0, 10 samples each, on across-line-shuffled Voynich."""
import os, sys, json, random
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c006_line_pairs_edges as c6, c007_line_pairs_rebuilt as c7, c003_position_rigidity as c3

def plant(lines, rng, rate):
    types = sorted({w for l in lines for w in l}); part = {a: rng.choice(types) for a in types}
    out = [list(l) for l in lines]
    for l in out:
        if len(l) >= 2 and rng.random() < rate: l[rng.randrange(1, len(l))] = part[l[0]]
    return out

def job(rate):
    V = c3.voynich(); rng = random.Random(int(rate * 100) + 5)
    r = [c7.metrics(plant(c6.shuffle_across(c6.sample(V, rng), rng), rng, rate), c3.units, rng) for _ in range(10)]
    r = np.array(r); return rate, dict(M1=[float(x) for x in np.percentile(r[:, 0], [0.5, 50, 99.5])],
                                       M1w=[float(x) for x in np.percentile(r[:, 1], [0.5, 50, 99.5])])

if __name__ == '__main__':
    with Pool(3) as p: out = dict(p.map(job, [0.2, 0.5, 1.0]))
    json.dump(out, open('analysis/C007_power_curve.json', 'w'), indent=1); print(json.dumps(out))
