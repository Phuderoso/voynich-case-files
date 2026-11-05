#!/usr/bin/env python3
"""C008: cross-word rules (S: local reordering, G: first-glyph rewriting) on C005's matched generator output, driven by the
Voynich table T(first unit | previous last unit) or a decoupled control table T0. Usage: python3 tools/c008_cross_word_rules.py"""
import os, sys, json, random
from collections import Counter, defaultdict
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3, c004_generator_sweep as c4, c005_targeted_search as c5, c006_line_pairs_edges as c6

U = c3.units; NW = 6000; PS = [0, 0.25, 0.5, 0.75, 1.0]; WIN = 30

def tables():
    pair = defaultdict(Counter); marg = Counter()
    for l in c3.voynich():
        for a, b in zip(l, l[1:]): pair[U(a)[-1]][U(b)[0]] += 1; marg[U(b)[0]] += 1
    T = {a: (list(c.keys()), np.array(list(c.values()), float) / sum(c.values())) for a, c in pair.items()}
    m = (list(marg.keys()), np.array(list(marg.values()), float) / sum(marg.values()))
    return T, {a: m for a in T}, m

def draw(tab, fallback, last, rng):
    k, p = tab.get(last, fallback); return k[int(np.searchsorted(np.cumsum(p), rng.random() * p.sum()))]

def apply(lines, rule, p, tab, fb, seed):
    rng = random.Random(seed); flat = [w for l in lines for w in l]; out = []; i = 0
    lens = [len(l) for l in lines]
    for L in lens:
        line = []
        for j in range(L):
            if j > 0 and rng.random() < p:
                f = draw(tab, fb, U(line[-1])[-1], rng)
                if rule == 'S':
                    for k in range(i, min(i + WIN, len(flat))):
                        if U(flat[k])[0] == f: flat[i], flat[k] = flat[k], flat[i]; break
                else:
                    u = U(flat[i]); flat[i] = f + ''.join(u[1:])
            line.append(flat[i]); i += 1
        out.append(line)
    return out

def head(lines):
    out, n = [], 0
    for l in lines:
        if n >= NW: break
        out.append(l); n += len(l)
    return out

def job(args):
    seed, cfg = args; T, T0, m = tables(); lines = head(c4.generate(cfg, seed)); res = {}
    for tname, tab in (('T', T), ('T0', T0)):
        for rule in ('S', 'G'):
            for p in PS:
                if tname == 'T0' and p == 0: continue
                L = apply(lines, rule, p, tab, m, seed)
                st = c4.stats([w for l in L for w in l]); st['C'] = c6.M2(L, U, random.Random(seed))
                res[f'{tname}/{rule}/{p}'] = st
    return seed, res

if __name__ == '__main__':
    c5.REF = c5.ref(); ref = c5.REF
    cfg = c5.tocfg(json.load(open('analysis/C005_confirm.json'))['A']['selected'])
    with Pool(10) as pool: runs = dict(pool.map(job, [(s, cfg) for s in range(6001, 6011)]))
    keys = list(runs[6001].keys())
    summ = {k: {s: float(np.mean([runs[x][k][s] for x in runs])) for s in ('R', 'mwl', 'ttr', 'h2', 'C')} for k in keys}
    for k in keys: summ[k]['C_lo'], summ[k]['C_hi'] = [float(x) for x in np.percentile([runs[x][k]['C'] for x in runs], [0.5, 99.5])]
    base = summ['T/S/0']
    ctrl_neg = all(base['C_lo'] <= summ[f'T0/{r}/{p}']['C'] <= base['C_hi'] for r in 'SG' for p in PS[1:])
    ctrl_dose = {r: summ[f'T/{r}/1.0']['C'] > summ[f'T/{r}/0']['C'] for r in 'SG'}
    match = lambda s: all(abs(s[k] - ref[k]) <= 0.15 * ref[k] for k in ('mwl', 'ttr', 'h2', 'R'))
    verdict = {}
    for r in 'SG':
        inC = [p for p in PS[1:] if 0.145 <= summ[f'T/{r}/{p}']['C'] <= 0.281]
        ok = [p for p in inC if match(summ[f'T/{r}/{p}'])]
        verdict[r] = ('not testable' if not (ctrl_neg and ctrl_dose[r]) else 'reaches' if ok else
                      'reaches only by breaking the match' if inC else 'does not reach')
    out = dict(reference=ref, summary=summ, controls=dict(negative_T0=ctrl_neg, dose=ctrl_dose), verdict=verdict, per_seed=runs)
    json.dump(out, open('analysis/C008_results.json', 'w'), indent=1)
    for k in keys: print(k, {a: round(b, 3) for a, b in summ[k].items()})
    print(out['controls'], verdict)
