#!/usr/bin/env python3
"""C006: line-pair excess P (same word pair on >=2 lines vs across-line word shuffle) and word-edge coupling C
(MI last glyph -> next first glyph minus within-line-shuffle mean) for Voynich, matched/default Timm-Schinner
generator, VC-F verbose ciphers of Latin/Italian and plain Latin/Italian. Usage: python3 tools/c006_line_pairs_edges.py"""
import os, sys, json, math, random
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3, c004_generator_sweep as c4, c005_targeted_search as c5

NS, NP, NW = 20, 50, 6000

def vf_texts():  # replicate C005 vc() code tables exactly (same RNG order)
    r = random.Random(5005); base = [chr(0x41 + i) for i in range(12)]; fin = [chr(0x71 + i) for i in range(4)]
    ini = [chr(0x61 + i) for i in range(4)]; out = {}
    for lang, path in (('VF-LA', 'data/corpora/pg218.txt'), ('VF-IT', 'data/corpora/pg1012.txt')):
        lines = c3.gutenberg(path); letters = sorted({ch for l in lines for w in l for ch in w})
        N = {c: r.choice(base) + r.choice(base) for c in letters}
        F = {c: r.choice(fin) for c in letters}; I = {c: r.choice(ini) for c in letters}
        def enc(w):  # mode 'F' of C005 vc()
            if len(w) == 1: return ''.join(N[c] for c in w)
            return ''.join(N[c][0] + F[c] if i == len(w) - 1 else N[c] for i, c in enumerate(w))
        out[lang] = [[enc(w) for w in l] for l in lines]
    return out

def gen(cfg, seeds):
    L = []
    for s in seeds: L += c4.generate(cfg, s)
    return L

def texts():
    sel = json.load(open('analysis/C005_confirm.json'))['A']['selected']
    T = {'V': (c3.voynich(), 'units'), 'G*': (gen(c5.tocfg(sel), range(6001, 6011)), 'units'),
         'G0': (gen({}, range(1, 11)), 'units')}
    for k, v in vf_texts().items(): T[k] = (v, 'chars')
    T['LA'] = (c3.gutenberg('data/corpora/pg218.txt'), 'chars'); T['IT'] = (c3.gutenberg('data/corpora/pg1012.txt'), 'chars')
    return T

def tok(kind): return c3.units if kind == 'units' else list

def sample(lines, rng):
    i = rng.randrange(len(lines)); out = []; n = 0
    while n < NW:
        l = lines[i % len(lines)]; out.append(list(l)); n += len(l); i += 1
    return out

def pairs_count(lines, ok):
    seen = Counter()
    for l in lines:
        ws = sorted({w for w in l if w in ok})
        for a in range(len(ws)):
            for b in range(a + 1, len(ws)): seen[(ws[a], ws[b])] += 1
    return sum(1 for v in seen.values() if v >= 2)

def shuffle_across(lines, rng):
    flat = [w for l in lines for w in l]; rng.shuffle(flat); out, i = [], 0
    for l in lines: out.append(flat[i:i + len(l)]); i += len(l)
    return out

def shuffle_within(lines, rng): return [rng.sample(l, len(l)) for l in lines]

def edge_mi(lines, t):
    c = Counter()
    for l in lines:
        for a, b in zip(l, l[1:]): c[(t(a)[-1], t(b)[0])] += 1
    n = sum(c.values()); pa, pb = Counter(), Counter()
    for (a, b), k in c.items(): pa[a] += k; pb[b] += k
    return sum(k / n * math.log2(k * n / (pa[a] * pb[b])) for (a, b), k in c.items())

def M1(lines, t, rng, z=False):
    ok = {w for l in lines for w in l if len(t(w)) >= 2}
    obs = pairs_count(lines, ok); null = [pairs_count(shuffle_across(lines, rng), ok) for _ in range(NP)]
    P = obs / np.mean(null)
    return (P, (obs - np.mean(null)) / (np.std(null) + 1e-12)) if z else P

def M2(lines, t, rng, z=False):
    obs = edge_mi(lines, t); null = [edge_mi(shuffle_within(lines, rng), t) for _ in range(NP)]
    C = obs - np.mean(null)
    return (C, C / (np.std(null) + 1e-12)) if z else C

def ci(x): return dict(mean=float(np.mean(x)), lo=float(np.percentile(x, 0.5)), hi=float(np.percentile(x, 99.5)))

def measure(args):
    name, lines, kind = args; t = tok(kind); rng = random.Random(66)
    S = [sample(lines, rng) for _ in range(NS)]
    return name, {'P': ci([M1(s, t, rng) for s in S]), 'C': ci([M2(s, t, rng) for s in S])}

def controls(args):
    name, lines, kind = args; t = tok(kind); rng = random.Random(77); out = {}
    fp1 = sum(M1(shuffle_across(sample(lines, rng), rng), t, rng, z=True)[1] > 2.58 for _ in range(40))
    fp2 = sum(M2(shuffle_within(sample(lines, rng), rng), t, rng, z=True)[1] > 2.58 for _ in range(40))
    out['fp_M1'] = fp1 / 40; out['fp_M2'] = fp2 / 40
    if name == 'V':
        base1, plant1, base2, plant2 = [], [], [], []
        for _ in range(NS):
            s = shuffle_across(sample(lines, rng), rng); base1.append(M1(s, t, rng))
            p = [list(l) for l in s]
            for i in rng.sample(range(len(p)), 60): p[i] = p[i] + ['xa', 'xb']
            plant1.append(M1(p, t, rng))
            s2 = shuffle_within(sample(lines, rng), rng); base2.append(M2(s2, t, rng))
            p2 = [list(l) for l in s2]
            for l in p2:
                for j in range(1, len(l)):
                    if l[j - 1].endswith('y') and rng.random() < 0.3: l[j] = 'q' + ''.join(c3.units(l[j])[1:])
            plant2.append(M2(p2, t, rng))
        out.update(planted_M1=dict(base=ci(base1), planted=ci(plant1)), planted_M2=dict(base=ci(base2), planted=ci(plant2)))
        out['planted_M1_pass'] = out['planted_M1']['planted']['lo'] > out['planted_M1']['base']['hi']
        out['planted_M2_pass'] = out['planted_M2']['planted']['lo'] > out['planted_M2']['base']['hi']
    return name, out

if __name__ == '__main__':
    T = texts()
    with Pool(8) as p:
        res = dict(p.map(measure, [(k, v[0], v[1]) for k, v in T.items()]))
        ctl = dict(p.map(controls, [(k, T[k][0], T[k][1]) for k in ('V', 'LA')]))
    ov = lambda a, b: not (a['hi'] < b['lo'] or b['hi'] < a['lo'])
    looks = {f'{c}/{m}': ('consistent' if ov(res[c][m], res['V'][m]) else
                          ('differs (higher)' if res[c][m]['lo'] > res['V'][m]['hi'] else 'differs (lower)'))
             for c in ('G*', 'G0', 'VF-LA', 'VF-IT') for m in ('P', 'C')}
    out = dict(results=res, controls=ctl, looks=looks, n_words={k: sum(map(len, v[0])) for k, v in T.items()})
    json.dump(out, open('analysis/C006_results.json', 'w'), indent=1)
    print(json.dumps(out, indent=1))
