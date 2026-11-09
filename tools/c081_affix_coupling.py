#!/usr/bin/env python3
"""C081 (NEW FAMILY F-AFFIX, the two ends of a word): how strongly does a word's first symbol constrain its last symbol,
once word length is held fixed, and is the manuscript inside the range of natural languages and of the Timm-Schinner
generator?  Symbols: Voynich = C003 glyph units; natural texts = letters (texts and loaders exactly as C077).
Tokens: the first N = 15,000 word tokens; only tokens with >= 3 symbols enter.  Strata by length {3, 4, 5, 6, >=7}.
Statistic K = [I(first; last | stratum) - E_null] / H(last | stratum)  (plug-in, bits), where E_null = mean of
I(first; last | stratum) over 50 shuffles of the last symbol among tokens of the same stratum (bias correction).
95% CI: block bootstrap (20 contiguous blocks, B = 1000) of the plug-in K with the full-sample E_null (approximation,
disclosed).  Range rule, LOO gate and generator rule exactly as C077 (OUTSIDE / INSIDE NATURAL / NOT CALLED; gate
<= 1/9 natural texts called OUTSIDE by the other 8; generator 10 default runs, fresh seeds 11201-11210, 2,500 lines).
Known-answer control (required for the natural verdict): Latin_Caesar with its last symbols shuffled within strata has
K = 0 by construction; it must be called OUTSIDE NATURAL against the 9 natural texts, else the natural verdict is NOT
TESTABLE (no power to see a missing coupling).  Seed 8181.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c077_direction as D
SEED, NBLK, B, NNULL = 8181, 20, 1000, 50
GSEEDS = range(11201, 11211)

def strat(n): return min(n, 7) - 3

def cmi(F, L, S):
    """I(F;L|S) and H(L|S) in bits from integer arrays."""
    I = H = 0.0; n = len(S)
    for s in np.unique(S):
        m = S == s; ns = m.sum(); f, l = F[m], L[m]
        j = Counter(zip(f.tolist(), l.tolist())); cf = Counter(f.tolist()); cl = Counter(l.tolist())
        for (a, b), c in j.items(): I += c / n * np.log2(c * ns / (cf[a] * cl[b]))
        for c in cl.values(): H -= c / n * np.log2(c / ns)
    return I, H

def arrays(words):
    ws = [w for w in words if len(w) >= 3]; sym = {}
    F = np.array([sym.setdefault(w[0], len(sym)) for w in ws]); L = np.array([sym.setdefault(w[-1], len(sym)) for w in ws])
    S = np.array([strat(len(w)) for w in ws]); return F, L, S

def shuffle_last(F, L, S, rng):
    L2 = L.copy()
    for s in np.unique(S):
        i = np.where(S == s)[0]; L2[i] = L[rng.permutation(i)]
    return L2

def analyse(name, words, boot=True):
    rng = np.random.default_rng([SEED, sum(map(ord, name))]); F, L, S = arrays(words)
    I, H = cmi(F, L, S); En = float(np.mean([cmi(F, shuffle_last(F, L, S, rng), S)[0] for _ in range(NNULL)]))
    out = dict(n_tokens=int(len(S)), I=float(I), E_null=En, H_last=float(H), K=float((I - En) / H))
    if boot:
        e = np.linspace(0, len(S), NBLK + 1).astype(int); bl = [np.arange(e[b], e[b + 1]) for b in range(NBLK)]; bs = []
        for _ in range(B):
            idx = np.concatenate([bl[j] for j in rng.integers(NBLK, size=NBLK)]); i2, h2 = cmi(F[idx], L[idx], S[idx])
            bs.append((i2 - En) / h2)
        out['ci'] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    return name, out

def decoupled(words, rng):
    ws = [w for w in words if len(w) >= 3]; S = np.array([strat(len(w)) for w in ws]); out = [list(w) for w in ws]
    for s in np.unique(S):
        i = np.where(S == s)[0]; p = rng.permutation(i)
        lasts = [ws[j][-1] for j in p]
        for j, x in zip(i, lasts): out[j][-1] = x
    return out

def gen_job(s):
    import c004_generator_sweep as G
    Lg = G.generate({'text.lines_to_create': 2500}, s)
    ws = [D.T.units(w) for l in (Lg or []) for w in l][:D.N]
    return (f'gen_{s}', None) if len(ws) < D.N else analyse(f'gen_{s}', ws, boot=False)

def main():
    t0 = time.time()
    texts = {n: D.seqs_nat(*v) for n, v in D.NAT.items()}
    voy = {'Voynich_ZL3b': D.seqs_voy('data/ZL3b-n.txt'), 'Voynich_IT2a': D.seqs_voy('data/IT2a-n.txt')}
    ctrl = {'CONTROL_Caesar_decoupled': decoupled(texts['Latin_Caesar'], np.random.default_rng([SEED, 1]))}
    with Pool(8) as pool:
        gj = pool.map_async(gen_job, list(GSEEDS), chunksize=1)
        R = dict(pool.starmap(analyse, list(texts.items()) + list(voy.items()) + list(ctrl.items())))
        G = {n: r for n, r in gj.get() if r}
    nat = list(D.NAT); fp = 0
    for n in nat:
        o = [R[m]['K'] for m in nat if m != n]; fp += D.call(R[n]['ci'], R[n]['K'], min(o), max(o)) == 'OUTSIDE NATURAL'
    lo, hi = min(R[m]['K'] for m in nat), max(R[m]['K'] for m in nat)
    c = R['CONTROL_Caesar_decoupled']; ctrl_call = D.call(c['ci'], c['K'], lo, hi); ctrl_ok = ctrl_call == 'OUTSIDE NATURAL'
    gate = dict(loo_outside=fp, pass_=fp <= 1, control=ctrl_call, control_ok=ctrl_ok)
    ga = [g['K'] for g in G.values()]; ver = {}
    for v in voy:
        ci, x = R[v]['ci'], R[v]['K']
        gv = ('ABOVE GENERATOR' if ci[0] > max(ga) else 'BELOW GENERATOR' if ci[1] < min(ga) else 'INSIDE GENERATOR RANGE' if min(ga) <= x <= max(ga) else 'NOT CALLED') if len(ga) >= 8 else 'NOT TESTABLE'
        ver[v] = dict(natural=D.call(ci, x, lo, hi) if gate['pass_'] and ctrl_ok else 'NOT TESTABLE', natural_range=[lo, hi],
                      generator=gv, generator_range=[min(ga), max(ga)] if ga else None, K=x, ci=ci)
    out = dict(seed=SEED, N=D.N, results=R, generator=G, gate=gate, verdict=ver, n_generator=len(G), runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C081_results.json', 'w'), indent=1)
    print('gate', gate)
    for n, r in list(R.items()) + list(G.items()): print(n, r['n_tokens'], round(r['I'], 4), round(r['E_null'], 4), round(r['H_last'], 3), round(r['K'], 4), [round(v, 4) for v in r.get('ci', [])])
    for k, v in ver.items(): print(k, json.dumps(v))
    print('runtime', out['runtime_s'])

if __name__ == '__main__':
    main()
