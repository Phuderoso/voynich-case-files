#!/usr/bin/env python3
# Run from the repo root: timeout 300 python3 tools/c066_posthoc_ceiling.py  (20 s). -- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)
# C066 post-hoc, exploratory (NOT pre-registered): raw O rates in 10 of the reference generator runs (seeds 7701-7710),
# and O at a stricter neighbour threshold (>= 10 tokens outside the home section) for manuscript, generator and natural texts.
import sys, json; sys.path.insert(0, 'tools')
import numpy as np, c066_cross_section_neighbours as X
out = {}
def rates(docs, lab, thr):
    c = X.Corpus(docs); d = c.D(lab, True)
    if thr != 2:
        lab = np.asarray(lab); ns = 4
        Cs = np.bincount(lab[c.td] * c.V + c.tt, minlength=ns * c.V).reshape(ns, c.V).astype(float); h = Cs.argmax(0); O = np.zeros(c.V, bool)
        for s in range(ns):
            Xs = (c.f - Cs[s]) >= thr; Y = np.zeros(c.V, bool); Y[c.er[Xs[c.ec]]] = True; O[h == s] = Y[h == s]
        D = X.dstat(d['_st'], d['_keep'], d['_diag'], O)
        return dict(D=float(D), O_diag=float(O[d['_diag']].mean()), O_other=float(O[d['_keep'] & ~d['_diag']].mean()), n_diag=int(d['_diag'].sum()))
    return dict(D=float(d['D']), O_diag=float(d['O_diag']), O_other=float(d['O_other']), n_diag=int(d['n_diag']))
V = {k: X.voynich(f) for k, f in X.FILES}
N = sum(len(d) for d in V['ZL3b'][1]); sh = np.array([sum(len(d) for d, l in zip(V['ZL3b'][1], V['ZL3b'][2]) if l == s) for s in range(4)]) / N
for thr in (2, 10):
    out[thr] = {}
    for k in V: out[thr][k] = rates(V[k][1], V[k][2], thr)
    g = []
    for s in range(7701, 7711):
        t = [tuple(X.T.units(w)) for w in X.C.flat(X.generate({'text.lines_to_create': X.LINES}, s))][:N]; docs, lab = X.blocks(t, sh); g.append(rates(docs, lab, thr))
    out[thr]['gen'] = {a: (min(x[a] for x in g), max(x[a] for x in g)) for a in g[0]}
    nat = X.E.nat_units(); nr = [rates(*X.blocks(t[:min(len(t), N)], sh), thr) for t in nat.values()]
    out[thr]['nat'] = {a: (min(x[a] for x in nr), max(x[a] for x in nr)) for a in nr[0]}
    print(thr, json.dumps(out[thr]), flush=True)
json.dump(out, open('analysis/C066_posthoc.json', 'w'), indent=1)
