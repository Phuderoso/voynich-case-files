#!/usr/bin/env python3
"""K004 sensitivity check (NOT pre-registered): corpus test with KH0349/UR113 removed. Run from expeditions/khipu/ with data/khipu.db present."""
import runpy, sys, numpy as np
sys.argv = ['x', 'data/khipu.db']
src = open('tools/k004_subsidiary_sums.py').read().split('# (1) corpus test')[0]
g = {}; exec(src, g)
K_, H, permS, pval, rng = g['K_'], g['H'], g['permS'], g['pval'], g['rng']
rng2 = np.random.default_rng(9009)


ids = [d['khid'] for d in K_]
target = [d for d in K_ if g['names'][d['khid']][0] == 'KH0349'][0]['khid']
KC = 10000; o = 0; nt = np.zeros(KC, np.int64); per = []
for d in K_:
    h = int(H(d['sv'][None], d['M'], d['pv'])[0])
    if h: per.append((g['names'][d['khid']][0], g['names'][d['khid']][1], h))
    if d['khid'] == target: continue
    o += h; nt += H(np.array([rng2.permutation(d['sv']) for _ in range(KC)]), d['M'], d['pv'])
print('without KH0349: H', o, 'null mean', nt.mean(), 'max', nt.max(), 'p', (1 + (nt >= o).sum()) / (1 + KC))
print(per)
