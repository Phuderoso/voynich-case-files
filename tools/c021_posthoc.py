"""C021 post-hoc (exploratory, NOT pre-registered): is the Look-B signal just bound adjacency?
(1) Look B without each quire's central bifolium (whose two leaves are bound-adjacent).
(2) Look B restricted to conjugate pairs whose leaves are >= 3 folios apart in bound order.
(3) Adjacency check: bound-adjacent non-conjugate pairs vs other non-conjugate pairs, same B strata, null = random
    choice of the same number of eligible non-conjugate pairs."""
import sys, os, random, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c021_bifolium_vocab as T
from collections import Counter
rng = random.Random(21099)
keep, meta, words = T.leaves()
cnt = Counter(w for f in keep for w in words[f]); vocab = sorted(w for w, c in cnt.items() if c >= 5)
S = T.simmat(keep, words, vocab); q, conj, elig = T.structure(keep, meta, 'B')
R = {}
for name, mind in (('no_central', 2), ('apart_ge3', 3)):
    sub = {p for p in conj if abs(keep[p[0]] - keep[p[1]]) >= mind}
    # drop the removed pairs' leaves from both sides so the null re-pairs only among the remaining structure
    drop = {a for p in conj - sub for a in p}
    e2 = elig.copy(); e2[list(drop), :] = False; e2[:, list(drop)] = False
    q2 = {Q: [a for a in idx if a not in drop] for Q, idx in q.items()}
    obs, p = T.test(S, q2, sub, e2, rng)
    R[name] = {'n_pairs': len(sub), 'n_eligible': int(sum(e2[a, b] for a, b in sub)), 'S_obs': float(obs), 'p': float(p)}
adj = [(a, b) for a in range(len(keep)) for b in range(a + 1, len(keep)) if elig[a, b] and (a, b) not in conj and abs(keep[a] - keep[b]) == 1]
oth = [(a, b) for a in range(len(keep)) for b in range(a + 1, len(keep)) if elig[a, b] and (a, b) not in conj and abs(keep[a] - keep[b]) > 1]
allp = adj + oth; obs = np.mean([S[p] for p in adj]) - np.mean([S[p] for p in oth])
null = []
for _ in range(4000):
    rng.shuffle(allp); A, O = allp[:len(adj)], allp[len(adj):]
    null.append(np.mean([S[p] for p in A]) - np.mean([S[p] for p in O]))
R['adjacent_nonconj'] = {'n_adj': len(adj), 'n_other': len(oth), 'S_obs': float(obs), 'p': float((1 + sum(x >= obs for x in null)) / 4001)}
print(json.dumps(R, indent=1)); json.dump(R, open('analysis/C021_posthoc.json', 'w'), indent=1)
