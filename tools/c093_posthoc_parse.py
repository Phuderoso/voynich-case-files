"""C093 POST HOC, descriptive only (written after the registered run): why does our full-text RHO (0.638) not reproduce
Zhang & Sheng's 0.587? Variants of parse/units, full text, no test. -- Pimpolha Voynich, do Phuderoso (AI)"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from collections import Counter
from scipy import stats
import numpy as np
import c003_position_rigidity as T
from c093_edit_graph import graph_stats
def row(name, ws):
    cnt = Counter(map(tuple, ws)); ty = list(cnt); deg, g = graph_stats(ty)
    r = stats.spearmanr([cnt[t] for t in ty], deg).correlation
    hap = [t for t in ty if cnt[t] >= 2]; idx = [i for i, t in enumerate(ty) if cnt[t] >= 2]
    r2 = stats.spearmanr([cnt[ty[i]] for i in idx], deg[idx]).correlation
    print(f'{name:38s} tokens {len(ws):6d} types {len(ty):5d} RHO {r:.3f} RHO(f>=2) {r2:.3f} near {np.mean(deg>0):.3f} meandeg {deg.mean():.2f} GIANT {g:.3f}')
for tn, p in [('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')]:
    L = T.voynich(p)
    row(tn + ' C003 units (registered parse)', [T.units(w) for l in L for w in l])
    row(tn + ' raw EVA characters', [list(w) for l in L for w in l])
    L2 = T.voynich(p, split_commas=False)
    row(tn + ' uncertain spaces NOT split', [T.units(w) for l in L2 for w in l])
