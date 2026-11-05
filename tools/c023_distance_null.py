"""C023 (F-COD step 3). Repair of C022 Look D: are conjugate leaves more alike than other leaf pairs of the same quire
that lie at exactly the same bound distance and share hand x language x illustration type?
Cells = (quire, bound distance |folio number difference|) that contain a true conjugate pair eligible under the C021
Look-B strata and at least one other eligible pair. Statistic S = mean sim(conjugates in cells) - mean sim(other pairs
in cells). Null (distance-preserving): in every cell the "conjugate" label is given to a random eligible pair of that
cell (one per true conjugate), 4000 draws; one-sided p. Single look, alpha = 0.05.
Gates as C021: FPR at alpha <= 0.075 on 40 destroyed corpora (leaf words redrawn from the hand x language x
illustration pool); power >= 0.8 on 40 planted corpora (20 % of one conjugate leaf's words from its partner).
Leaves, similarity, redraw and plant reused unchanged from tools/c021_bifolium_vocab.py.
"""
import sys, os, json, random, time
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c021_bifolium_vocab as T
SEED = 23023; ALPHA = 0.05

def cells(keep, meta):
    q, conj, elig = T.structure(keep, meta, 'B')
    qof = {a: Q for Q, idx in q.items() for a in idx}
    cell = defaultdict(lambda: {'conj': [], 'all': []})
    for a in range(len(keep)):
        for b in range(a + 1, len(keep)):
            if elig[a, b] and qof[a] == qof[b]:
                cell[(qof[a], abs(keep[a] - keep[b]))]['all'].append((a, b))
    for p in conj:
        if elig[p]: cell[(qof[p[0]], abs(keep[p[0]] - keep[p[1]]))]['conj'].append(p)
    return {k: v for k, v in cell.items() if v['conj'] and len(v['all']) > len(v['conj'])}

def stat(S, cl, labels):
    c, o = [], []
    for k, v in cl.items():
        lab = set(labels[k])
        for p in v['all']: (c if p in lab else o).append(S[p])
    return np.mean(c) - np.mean(o)

def test(S, cl, rng, nperm=4000):
    obs = stat(S, cl, {k: v['conj'] for k, v in cl.items()})
    null = np.array([stat(S, cl, {k: rng.sample(v['all'], len(v['conj'])) for k, v in cl.items()}) for _ in range(nperm)])
    return float(obs), float((1 + (null >= obs).sum()) / (1 + nperm))

def main():
    t0 = time.time(); rng = random.Random(SEED)
    keep, meta, words = T.leaves()
    cnt = Counter(w for f in keep for w in words[f]); vocab = sorted(w for w, c in cnt.items() if c >= 5)
    cl = cells(keep, meta); _, conj, _ = T.structure(keep, meta, 'B')
    key = lambda m: (m['H'], m['L'], m['I'])
    fp = [test(T.simmat(keep, T.redraw(keep, meta, words, key, rng), vocab), cl, rng, 500)[1] for _ in range(T.NCAL)]
    pw = [test(T.simmat(keep, T.plant(keep, T.redraw(keep, meta, words, key, rng), conj, rng), vocab), cl, rng, 500)[1] for _ in range(T.NCAL)]
    fpr = float(np.mean(np.array(fp) <= ALPHA)); power = float(np.mean(np.array(pw) <= ALPHA))
    obs, p = test(T.simmat(keep, words, vocab), cl, rng)
    ok = fpr <= 0.075 and power >= 0.8
    R = {'n_cells': len(cl), 'n_conj': sum(len(v['conj']) for v in cl.values()),
         'n_other': sum(len(v['all']) - len(v['conj']) for v in cl.values()), 'S_obs': obs, 'p': p,
         'fpr_at_alpha': fpr, 'power_f0.2': power,
         'verdict': 'not testable' if not ok else ('detected' if p <= ALPHA else 'not detected'),
         'seconds': round(time.time() - t0, 1)}
    print(R, flush=True); json.dump(R, open('analysis/C023_results.json', 'w'), indent=1)

if __name__ == '__main__': main()
