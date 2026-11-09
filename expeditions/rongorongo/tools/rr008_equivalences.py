"""RR008 step 1 - learn sign-substitution equivalences from the H/P/Q copies ONLY (training set, never the 25 test pairs).
Rule (fixed before any test statistic): align each training pair of head-sign sequences with difflib SequenceMatcher
(autojunk off); record every 1-for-1 'replace' opcode flanked on both sides by 'equal' blocks of >= 3 signs, with both
signs legible and different. Training pairs: Hr-Pr, Hr-Qr, Pr-Qr, Hv-Pv, Hv-Qv, Pv-Qv. Equivalence classes = connected
components (union-find) of the recorded pairs. Usage: python3 rr008_equivalences.py corpus.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, difflib
from collections import Counter
sys.path.insert(0, '.')
import rr005_fuzzy_isolation  # head_norm
import rr001_isolation as R1
TRAIN = [('Hr', 'Pr'), ('Hr', 'Qr'), ('Pr', 'Qr'), ('Hv', 'Pv'), ('Hv', 'Qv'), ('Pv', 'Qv')]

def learn(corpus):
    seqs = {s: R1.side_seq(corpus, s) for p in TRAIN for s in p}
    key = lambda t: t if not isinstance(t, tuple) else 'ILL'
    subs = Counter(); per = {}
    for a, b in TRAIN:
        x = [key(t) for t in seqs[a]]; y = [key(t) for t in seqs[b]]
        ops = difflib.SequenceMatcher(None, x, y, autojunk=False).get_opcodes(); n = 0
        for k in range(1, len(ops) - 1):
            tag, i1, i2, j1, j2 = ops[k]
            if tag == 'replace' and i2 - i1 == 1 and j2 - j1 == 1 and ops[k-1][0] == 'equal' and ops[k+1][0] == 'equal' \
               and ops[k-1][2] - ops[k-1][1] >= 3 and ops[k+1][2] - ops[k+1][1] >= 3:
                s, t = x[i1], y[j1]
                if 'ILL' not in (s, t) and s != t: subs[tuple(sorted((s, t)))] += 1; n += 1
        per[f'{a}-{b}'] = n
    parent = {}
    def f(u):
        parent.setdefault(u, u)
        while parent[u] != u: parent[u] = parent[parent[u]]; u = parent[u]
        return u
    for (s, t) in subs: parent[f(s)] = f(t)
    classes = {}
    for u in list(parent): classes.setdefault(f(u), set()).add(u)
    cmap = {u: min(cl) for cl in classes.values() for u in cl}
    return subs, per, cmap, sorted((sorted(cl) for cl in classes.values()), key=len, reverse=True)

if __name__ == '__main__':
    subs, per, cmap, classes = learn(json.load(open(sys.argv[1])))
    json.dump(dict(per_training_pair=per, substitutions={f'{a}~{b}': n for (a, b), n in subs.most_common()},
                   classes=classes, map=cmap), open(sys.argv[2], 'w'), indent=1)
    print(per); print(subs.most_common(40)); print([c for c in classes][:10], len(classes))
