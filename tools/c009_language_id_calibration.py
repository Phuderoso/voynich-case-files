#!/usr/bin/env python3
"""C009: sorted-unigram-profile language ID (simplified Hauer-Kondrak stage), planted substitution ciphers, generator
noise bar, Voynich. Usage: python3 tools/c009_language_id_calibration.py"""
import os, sys, json, random
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as c3, c004_generator_sweep as c4, c005_targeted_search as c5

K, NW, NS = 30, 6000, 20

def profile(words, tok):
    c = Counter(u for w in words for u in tok(w)); v = np.array(sorted(c.values(), reverse=True)[:K], float)
    v = v / v.sum(); return np.pad(v, (0, K - len(v)))

def flat(lines): return [w for l in lines for w in l]

def ident(p, refs):
    d = sorted((float(np.abs(p - r).sum()), k) for k, r in refs.items())
    return d[0][1], (d[1][0] - d[0][0]) / d[0][0]

def samples(words, rng, n=NS):
    return [words[s:s + NW] for s in (rng.randrange(0, max(1, len(words) - NW)) for _ in range(n))]

def substitute(words, rng):
    al = sorted({ch for w in words for ch in w}); sh = al[:]; rng.shuffle(sh)
    pool = [chr(0x4e00 + i) for i in range(len(al))]; m = dict(zip(al, [pool[al.index(x)] for x in sh]))
    return [''.join(m[ch] for ch in w) for w in words]

if __name__ == '__main__':
    rng = random.Random(99)
    la = flat(c3.gutenberg('data/corpora/pg218.txt'))
    texts = {'Latin': la, 'Italian': flat(c3.gutenberg('data/corpora/pg1012.txt')),
             'Spanish': flat(c3.gutenberg('data/corpora/pg2000.txt')), 'Hebrew': flat(c3.hebrew('data/corpora/Gen.xml')),
             'Latin-vowelless': [w for w in (''.join(ch for ch in x if ch not in 'aeiou') for x in la) if w]}
    refs = {k: profile(v[:len(v) // 2], list) for k, v in texts.items()}
    planted = []
    tests = {k: v[len(v) // 2:] for k, v in texts.items()}
    tests['Latin (Descartes)'] = flat(c3.gutenberg('data/corpora/pg23306.txt'))
    for k, v in tests.items():
        truth = 'Latin' if k.startswith('Latin (') else k
        for s in samples(v, rng):
            lang, m = ident(profile(substitute(s, rng), list), refs); planted.append(dict(text=k, truth=truth, got=lang, margin=m))
    acc = float(np.mean([p['truth'] == p['got'] for p in planted]))
    cfg = c5.tocfg(json.load(open('analysis/C005_confirm.json'))['A']['selected'])
    gen = []
    for name, c, seeds in (('G0', {}, range(1, 11)), ('G*', cfg, range(6001, 6011))):
        for sd in seeds:
            w = flat(c4.generate(c, sd))
            for s in samples(w, rng, 2):
                lang, m = ident(profile(s, c3.units), refs); gen.append(dict(text=name, got=lang, margin=m))
    B = float(np.percentile([g['margin'] for g in gen], 99))
    def run(words, tok):
        r = [ident(profile(s, tok), refs) for s in samples(words, rng)]
        return dict(assigned=dict(Counter(x[0] for x in r)), margin_median=float(np.median([x[1] for x in r])),
                    margins=[x[1] for x in r])
    V = flat(c3.voynich())
    vres = run(V, c3.units)
    desc = {'V_raw_EVA_chars': run(V, list), 'V_Currier_A': run(flat(c3.voynich(lang='A')), c3.units),
            'V_Currier_B': run(flat(c3.voynich(lang='B')), c3.units)}
    verdict = ('not testable' if acc < 0.8 else
               'more confident than generator noise' if vres['margin_median'] > B else
               'no more confident than meaningless text')
    out = dict(planted_accuracy=acc, planted_by_text={k: float(np.mean([p['truth'] == p['got'] for p in planted if p['text'] == k])) for k in tests},
               planted_margin_median=float(np.median([p['margin'] for p in planted if p['truth'] == p['got']])),
               generator_assigned=dict(Counter(g['got'] for g in gen)), generator_margins=[g['margin'] for g in gen],
               bar_B=B, voynich=vres, descriptive=desc, verdict=verdict, planted=planted)
    json.dump(out, open('analysis/C009_results.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ('planted', 'generator_margins')}, indent=1)[:3000])
