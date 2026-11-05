#!/usr/bin/env python3
"""C012: homophonic-substitution hill-climbing solver against a Latin 4-gram model; planted Latin ciphers (blind), meaningless
nulls (generator, iid glyph text) set the bar; Voynich ZL 3b samples. Usage: python3 tools/c012_solver_bar.py"""
import os, sys, json, random
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3, c004_generator_sweep as c4, c005_targeted_search as c5

NW, RESTARTS, ITERS, A = 1500, 20, 15000, 27  # run 2 used 4 restarts: planted 8/10 (disclosed)
flat = lambda L: [w for l in L for w in l]

def lm():
    la = flat(c3.gutenberg('data/corpora/pg218.txt')); la = la[:len(la) // 2]
    s = np.array([26] + [x for w in la for x in [ord(ch) - 97 for ch in w] + [26]])
    q = ((s[:-3] * A + s[1:-2]) * A + s[2:-1]) * A + s[3:]
    c = np.bincount(q, minlength=A ** 4).astype(float)
    # joint 4-gram log-probability with a floor for unseen 4-grams (standard quadgram fitness). Run 1 used conditional
    # P(c4|c1c2c3) with add-0.5, which scored unseen contexts as uniform and failed the planted gate (disclosed).
    return np.log10(np.where(c > 0, c, 0.01) / c.sum())

def encode(words):  # words -> list of symbol-id lists
    syms = {}; out = [[syms.setdefault(u, len(syms)) for u in w] for w in words]; return out, len(syms)

def stream(words_ids):
    s = [-1]
    for w in words_ids: s += w + [-1]
    return np.array(s)

def score(st, m, T):
    p = np.where(st < 0, 26, m[np.maximum(st, 0)])
    q = ((p[:-3] * A + p[1:-2]) * A + p[2:-1]) * A + p[3:]; return T[q].mean()

def solve(args):
    words_ids, n, seed, T = args
    rng = np.random.default_rng(seed); st = stream(words_ids); best = (-1e9, None)
    for r in range(RESTARTS):
        m = rng.integers(0, 26, n); s = score(st, m, T)
        for _ in range(ITERS):
            i = rng.integers(n); old = m[i]; m[i] = rng.integers(26)
            t = score(st, m, T)
            if t >= s: s = t
            else: m[i] = old
        if s > best[0]: best = (s, m.copy())
    return best

def plain_score(words, T):
    return score(stream([[ord(c) - 97 for c in w] for w in words]), np.arange(26), T)

if __name__ == '__main__':
    T = lm(); rng = random.Random(12)
    LEX = set(flat(c3.gutenberg('data/corpora/pg218.txt')))  # post-hoc descriptive: Latin word-type list (Caesar, whole text)
    de = flat(c3.gutenberg('data/corpora/pg23306.txt')); V = flat(c3.voynich())
    jobs, meta = [], []
    top8 = [c for c, _ in Counter(''.join(de)).most_common(8)]
    for k in range(5):
        s0 = rng.randrange(len(de) - NW); pw = de[s0:s0 + NW]
        for kind in ('P1', 'P2'):
            truth, ids = [], []
            sym = {}
            for w in pw:
                wi = []
                for ch in w:
                    key = (ch, rng.randrange(2)) if (kind == 'P2' and ch in top8) else (ch, 0)
                    wi.append(sym.setdefault(key, len(sym))); truth.append(key[0])
                ids.append(wi)
            inv = {v: k_[0] for k_, v in sym.items()}
            jobs.append((ids, len(sym), 100 + len(jobs), T)); meta.append(dict(kind=kind, k=k, inv=inv, plain=pw))
    cfg = c5.tocfg(json.load(open('analysis/C005_confirm.json'))['A']['selected'])
    cV = Counter(u for w in V for u in c3.units(w)); us, ps = zip(*cV.items()); ps = np.array(ps) / sum(ps)
    lens = [len(c3.units(w)) for w in V]
    for name, c, seeds in (('G0', {}, range(1, 6)), ('G*', cfg, range(6001, 6006))):
        for sd in seeds:
            w = flat(c4.generate(c, sd))[:NW]; ids, n = encode([c3.units(x) for x in w])
            jobs.append((ids, n, 100 + len(jobs), T)); meta.append(dict(kind='null-' + name, k=sd, units=[c3.units(x) for x in w]))
    for sd in range(5):
        r = np.random.default_rng(500 + sd); ws = [list(r.choice(us, size=random.Random(sd * 7919 + i).choice(lens), p=ps)) for i in range(NW)]
        ids, n = encode(ws); jobs.append((ids, n, 100 + len(jobs), T)); meta.append(dict(kind='null-iid', k=sd, units=ws))
    for k in range(5):
        s0 = rng.randrange(len(V) - NW); ws = [c3.units(x) for x in V[s0:s0 + NW]]
        ids, n = encode(ws); jobs.append((ids, n, 100 + len(jobs), T)); meta.append(dict(kind='Voynich', k=s0, units=ws))
    with Pool(8) as p: res = p.map(solve, jobs)
    rows = []
    for (ids, n, sd, _), md, (s, m) in zip(jobs, meta, res):
        row = dict(kind=md['kind'], k=md['k'], n_symbols=n, S=float(s))
        dec = [''.join(chr(97 + m[i]) for i in w) for w in ids]
        if md['kind'] in ('P1', 'P2'):
            tr = ''.join(md['plain']); dc = ''.join(dec); row['accuracy'] = float(np.mean([a == b for a, b in zip(tr, dc)]))
        row['excerpt'] = ' '.join(dec[:25])
        # post-hoc, descriptive only (added after the pre-registered run): share of decoded tokens of length >= 3 that are
        # Latin words in Caesar's vocabulary, and number of distinct such words
        lw = [d for d in dec if len(d) >= 3]; hit = [d for d in lw if d in LEX]
        row['lex_rate'] = len(hit) / max(1, len(lw)); row['lex_types'] = len(set(hit)); rows.append(row)
    plantok = sum(r.get('accuracy', 0) >= 0.8 for r in rows if r['kind'] in ('P1', 'P2'))
    nullS = [r['S'] for r in rows if r['kind'].startswith('null')]; bar = max(nullS)
    vS = [r['S'] for r in rows if r['kind'] == 'Voynich']
    ceiling = float(np.mean([plain_score(de[i:i + NW], T) for i in (0, len(de) // 3, 2 * len(de) // 3)]))
    verdict = ('not testable' if plantok < 9 else
               'manuscript shows more Latin than meaningless text' if np.median(vS) > bar else
               'no more Latin than meaningless text under this solver')
    out = dict(planted_ok=f'{plantok}/10', bar=bar, null_S=dict(min=min(nullS), median=float(np.median(nullS)), max=bar),
               voynich_S=vS, voynich_median=float(np.median(vS)), plain_latin_ceiling=ceiling,
               planted_S=[r['S'] for r in rows if r['kind'] in ('P1', 'P2')], verdict=verdict, runs=rows)
    json.dump(out, open('analysis/C012_results.json', 'w'), indent=1)
    for r in rows: print(r['kind'], r['k'], r['n_symbols'], round(r['S'], 3), r.get('accuracy'), r['excerpt'][:70])
    print({k: v for k, v in out.items() if k != 'runs'})
