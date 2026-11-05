#!/usr/bin/env python3
"""C007: rebuilt line-pair metrics (M1 distinct recurring pairs, M1w weighted excess sum max(0,k-1)) with a
distributed planted control. Reuses C006 texts/samplers. Usage: python3 tools/c007_line_pairs_rebuilt.py"""
import os, sys, json, random
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c006_line_pairs_edges as c6

NP, NS = 50, 20

def pair_counts(lines, ok):
    seen = Counter()
    for l in lines:
        ws = sorted({w for w in l if w in ok})
        for a in range(len(ws)):
            for b in range(a + 1, len(ws)): seen[(ws[a], ws[b])] += 1
    return sum(1 for v in seen.values() if v >= 2), sum(v - 1 for v in seen.values() if v >= 2)

def metrics(lines, t, rng, z=False):
    ok = {w for l in lines for w in l if len(t(w)) >= 2}
    obs = np.array(pair_counts(lines, ok), float)
    null = np.array([pair_counts(c6.shuffle_across(lines, rng), ok) for _ in range(NP)], float)
    r = obs / null.mean(0)
    if z: return r, (obs - null.mean(0)) / (null.std(0) + 1e-12)
    return r

def plant_distributed(lines, rng):
    types = sorted({w for l in lines for w in l}); part = {a: rng.choice(types) for a in types}
    out = [list(l) for l in lines]
    for l in out:
        if len(l) >= 2 and rng.random() < 0.2: l[rng.randrange(1, len(l))] = part[l[0]]
    return out

def plant_single(lines, rng):
    out = [list(l) for l in lines]
    for i in rng.sample(range(len(out)), 60): out[i] = out[i] + ['xa', 'xb']
    return out

def ci(x):
    x = np.array(x); return [dict(mean=float(x[:, j].mean()), lo=float(np.percentile(x[:, j], 0.5)),
                                  hi=float(np.percentile(x[:, j], 99.5))) for j in range(x.shape[1])]

def measure(args):
    name, lines, kind = args; t = c6.tok(kind); rng = random.Random(66)
    S = [c6.sample(lines, rng) for _ in range(NS)]
    m = ci([metrics(s, t, rng) for s in S]); return name, dict(M1=m[0], M1w=m[1])

def controls(args):
    name, lines, kind = args; t = c6.tok(kind); rng = random.Random(77)
    fp = np.array([metrics(c6.shuffle_across(c6.sample(lines, rng), rng), t, rng, z=True)[1] > 2.58 for _ in range(40)])
    out = dict(fp_M1=float(fp[:, 0].mean()), fp_M1w=float(fp[:, 1].mean()))
    if name == 'V':
        base, dist, single = [], [], []
        for _ in range(NS):
            s = c6.shuffle_across(c6.sample(lines, rng), rng)
            base.append(metrics(s, t, rng)); dist.append(metrics(plant_distributed(s, rng), t, rng))
            single.append(metrics(plant_single(s, rng), t, rng))
        b, d, sg = ci(base), ci(dist), ci(single)
        for j, m in enumerate(('M1', 'M1w')):
            out[m] = dict(base=b[j], distributed=d[j], single=sg[j],
                          distributed_pass=d[j]['lo'] > b[j]['hi'], single_pass=sg[j]['lo'] > b[j]['hi'])
    return name, out

if __name__ == '__main__':
    T = c6.texts()
    with Pool(8) as p:
        res = dict(p.map(measure, [(k, v[0], v[1]) for k, v in T.items()]))
        ctl = dict(p.map(controls, [(k, T[k][0], T[k][1]) for k in ('V', 'LA')]))
    usable = {m: ctl['V'][m]['distributed_pass'] and max(ctl['V']['fp_' + m], ctl['LA']['fp_' + m]) <= 0.05 for m in ('M1', 'M1w')}
    ov = lambda a, b: not (a['hi'] < b['lo'] or b['hi'] < a['lo'])
    looks = {}
    for m in ('M1', 'M1w'):
        if not usable[m]: continue
        looks[f'V_above_null/{m}'] = res['V'][m]['lo'] > 1
        for c in ('G*', 'G0', 'VF-LA', 'VF-IT'):
            looks[f'{c}/{m}'] = 'consistent' if ov(res[c][m], res['V'][m]) else (
                'differs (higher)' if res[c][m]['lo'] > res['V'][m]['hi'] else 'differs (lower)')
    out = dict(results=res, controls=ctl, usable=usable, looks=looks)
    json.dump(out, open('analysis/C007_results.json', 'w'), indent=1)
    print(json.dumps(out, indent=1))
