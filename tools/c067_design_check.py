# C067 design check, generator only (spent seeds 7711-7740), no manuscript statistic. Run from repo root: timeout 600 python3 tools/c067_design_check.py -- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)
# C067 design check on SPENT generator seeds 7711-7740 only (no manuscript statistic): spread of S10, plant shifts
import sys, json; sys.path.insert(0,'tools'); import numpy as np, c067_cross_threshold10 as Y, c066_cross_section_neighbours as X
from multiprocessing import Pool
Ns={'ZL3b':30771}; sh=np.array([11349,6152,2056,11214])/30771
def job(s):
    t=[tuple(X.T.units(w)) for w in X.C.flat(X.generate({'text.lines_to_create':X.LINES},s))]
    if len(t)<30771: return None
    docs,lab=X.blocks(t[:30771],sh); rng=np.random.default_rng(s); r=Y.stats(X.Corpus(docs),lab)
    out=dict(S=r['S'],n=r['n_diag'])
    for f in (0.10,0.15):
        pd,k=Y.connect_plant(docs,lab,rng,f); out[f'c{f}']=Y.stats(X.Corpus(pd),lab)['S']
    out['iso']=Y.stats(X.Corpus(Y.iso_plant(docs,lab,rng)),lab)['S']; return out
with Pool(8) as P: R=[r for r in P.map(job, range(7711,7741)) if r]
S=np.array([r['S'] for r in R]); print(len(R),'S',S.min(),np.median(S),S.max(), 'sd',S.std())
for k in ('c0.1','c0.15','iso'): d=np.array([r[k]-r['S'] for r in R]); print(k,'shift',np.median(d), 'planted', np.sort([r[k] for r in R])[[0,len(R)//2,-1]])
