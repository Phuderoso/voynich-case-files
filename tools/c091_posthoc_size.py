"""C091 post hoc, DESCRIPTIVE ONLY (not registered): (a) Voynich Q when the type sample is cut to the generator's type
counts (random subsets of types, 200 draws per size, seed 9192); (b) Q vs type count across the 10 generator runs;
(c) the largest Voynich anagram families. -- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c077_direction as D, c091_anagram_families as A
R = json.load(open('out/C091_results.json')); rng = np.random.default_rng(9192)
gq = [(v['ref']['ntypes'], v['ref']['Q']) for v in R['generator'].values()]
print('generator ntypes vs Q, r =', round(float(np.corrcoef(*zip(*gq))[0, 1]), 3))
for path in ('data/ZL3b-n.txt', 'data/IT2a-n.txt'):
    ty = A.types_of(D.seqs_voy(path))
    for n in (2139, 2500, 2778):
        qs = []
        for _ in range(200):
            sub = [ty[i] for i in rng.choice(len(ty), n, replace=False)]; fam = Counter(tuple(sorted(t)) for t in sub)
            qs.append(np.mean([fam[tuple(sorted(t))] >= 2 for t in sub]))
        print(path, 'types', n, 'Q mean', round(float(np.mean(qs)), 4), 'range', round(float(min(qs)), 4), round(float(max(qs)), 4))
    fam = defaultdict(list)
    for t in ty: fam[tuple(sorted(t))].append(''.join(t))
    big = sorted(fam.values(), key=len, reverse=True)[:5]
    for b in big: print('  family', len(b), b)
