#!/usr/bin/env python3
"""C092 (F-ANAG step 3): SIZE-MATCHED manuscript-vs-generator test of the anagram-partner share Q.
C091 found Q (share of 3-8-unit word types with an anagram partner) rises with the number of types sampled
(generator r 0.70) and the manuscript had more types than every generator run, so its registered H3 was tilted.
Here the type count is held fixed by PREFIX sampling for every text: Q_K = Q over the first K distinct 3-8-unit word
types met in token order (C003 glyph units; Voynich token stream as in C091).
References: 10 fresh default Timm-Schinner generator runs, seeds 11464-11473 (8,000 lines each so every run can reach the
manuscript's type count; next generator seed 11474).
Cells (two-sided predictive-t, t = (x - mean)/(sd*sqrt(1+1/n)), df n-1):
 H3a  K = the manuscript's own type count in its first 15,000 tokens (ZL 3,667; IT2a 3,735; published in C091) -> the
      manuscript value is C091's registered Q; each generator run is cut at the same K.
 H3b  K0 = 2,000 types (below every C091 generator run) -> manuscript and generator both cut at their first 2,000 types.
Holm over 4 (H3a, H3b x ZL, IT2a), alpha 0.05; a call needs both transcriptions.
Gates per cell (rehearsed BEFORE the pre-registration push on references only, manuscript untouched):
 G0 reach: >= 8 of 10 runs reach K types.  G1 false calls, leave-one-out among the runs at raw p < 0.05: <= 1/10.
 G2 power: each run with 10 % of tokens freely scrambled (fresh letter order per occurrence), cut at K, vs the other 9
    unplanted, detected >= 8/10.  DOA (dead-on-arrival line): C091's post hoc lead |gap| 0.13 must exceed MDE80.
 A cell failing any gate is declared NOT RUN and LOW-POWER (NOT TESTABLE), per Kryptos's rule.
Descriptive audit of C091's post hoc lead (registered here as descriptive only): manuscript prefix-cut Q at the C091
generator type counts 2,139 / 2,500 / 2,778, versus C091's random-subset values 0.21 / 0.24 / 0.26.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time, math
from collections import Counter
from multiprocessing import Pool
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.dirname(__file__))
import c077_direction as D

SEED, NV, LINES, F3, ALPHA, LEAD = 9292, 15000, 8000, 0.10, 0.05, 0.13
GSEEDS = list(range(11464, 11474))
KV = {'ZL3b': 3667, 'IT2a': 3735}; K0 = 2000; AUDK = (2139, 2500, 2778)
VPATH = {'ZL3b': 'data/ZL3b-n.txt', 'IT2a': 'data/IT2a-n.txt'}

def first_types(words, K):
    seen, out = set(), []
    for w in words:
        t = tuple(w)
        if 3 <= len(t) <= 8 and t not in seen:
            seen.add(t); out.append(t)
            if len(out) == K: break
    return out

def Q_types(ty):
    fam = Counter(tuple(sorted(t)) for t in ty)
    return sum(fam[tuple(sorted(t))] >= 2 for t in ty) / len(ty)

def QK(words, K):
    ty = first_types(words, K)
    return (Q_types(ty) if len(ty) == K else None), len(ty)

def scramble(words, rng, frac):
    return [tuple(rng.permutation(list(w))) if (len(w) > 1 and rng.random() < frac) else tuple(w) for w in words]

def gen_job(s):
    import c004_generator_sweep as G
    Lg = G.generate({'text.lines_to_create': LINES}, s)
    ws = [tuple(D.T.units(w)) for l in (Lg or []) for w in l]
    rng = np.random.default_rng([SEED, s]); pl = scramble(ws, rng, F3)
    Ks = sorted(set(list(KV.values()) + [K0]))
    out = {'ntokens': len(ws), 'ntypes_15k': len(first_types(ws[:NV], 10**9))}
    for K in Ks:
        q, n = QK(ws, K); qp, npl = QK(pl, K)
        out[str(K)] = dict(Q=q, reached=n, Q_plant=qp)
    return s, out

def pt(x, ref):
    ref = np.asarray(ref, float); n = len(ref); t = (x - ref.mean()) / (ref.std(ddof=1) * math.sqrt(1 + 1 / n))
    return float(2 * stats.t.sf(abs(t), n - 1))

def mde(ref):
    ref = np.asarray(ref, float); n = len(ref); s = ref.std(ddof=1) * math.sqrt(1 + 1 / n)
    return float((stats.t.ppf(1 - ALPHA / 2, n - 1) + stats.norm.ppf(0.8)) * s)

def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0] * len(ps); run = 0
    for k, i in enumerate(o): run = max(run, min(1, (len(ps) - k) * ps[i])); adj[i] = run
    return adj

def gate(G, K):
    runs = [s for s in GSEEDS if G[s][str(K)]['Q'] is not None]
    q = {s: G[s][str(K)]['Q'] for s in runs}; qp = {s: G[s][str(K)]['Q_plant'] for s in runs if G[s][str(K)]['Q_plant'] is not None}
    if len(runs) < 8: return dict(K=K, reached=len(runs), ok=False, why='G0')
    fpr = sum(pt(q[s], [q[r] for r in runs if r != s]) < ALPHA for s in runs)
    pw = sum(pt(qp[s], [q[r] for r in runs if r != s]) < ALPHA for s in qp)
    m = mde(list(q.values())); sh = float(np.mean([qp[s] - q[s] for s in qp]))
    ok = fpr <= 1 and pw >= 8 and LEAD > m
    return dict(K=K, reached=len(runs), FPR=f'{fpr}/{len(runs)}', POW=f'{pw}/{len(qp)}', MDE80=m, plant_shift=sh,
                shift_over_MDE=sh / m, lead_over_MDE=LEAD / m, mean=float(np.mean(list(q.values()))),
                sd=float(np.std(list(q.values()), ddof=1)), lo=min(q.values()), hi=max(q.values()), ok=ok,
                why='' if ok else ('G1' if fpr > 1 else 'G2' if pw < 8 else 'DOA'))

def main(mode):
    t0 = time.time()
    with Pool(8) as p: G = dict(p.map(gen_job, GSEEDS))
    cells = {'H3a_ZL3b': KV['ZL3b'], 'H3a_IT2a': KV['IT2a'], 'H3b_ZL3b': K0, 'H3b_IT2a': K0}
    gates = {c: gate(G, K) for c, K in cells.items()}
    out = dict(seed=SEED, mode=mode, lines=LINES, F3=F3, gseeds=GSEEDS, KV=KV, K0=K0, generator={str(k): v for k, v in G.items()},
               gates=gates)
    if mode == 'run':
        V, ps, keys, aud = {}, [], [], {}
        for tn, path in VPATH.items():
            ws = [tuple(w) for w in D.seqs_voy(path)]
            nt = len(first_types(ws[:NV], 10**9)); assert nt == KV[tn], (tn, nt)
            V[tn] = {'H3a': QK(ws[:NV], KV[tn])[0], 'H3b': QK(ws, K0)[0]}
            aud[tn] = {str(k): QK(ws, k)[0] for k in AUDK}
        tests = []
        for c, K in cells.items():
            h, tn = c.split('_'); g = gates[c]; ref = [G[s][str(K)]['Q'] for s in GSEEDS if G[s][str(K)]['Q'] is not None]
            if not g['ok']: tests.append(dict(cell=c, status='NOT RUN, LOW-POWER', Q=None)); continue
            x = V[tn][h]; tests.append(dict(cell=c, status='run', Q=x, p=pt(x, ref), z=(x - np.mean(ref)) / np.std(ref, ddof=1)))
        run = [t for t in tests if t['status'] == 'run']
        for t, a in zip(run, holm([t['p'] for t in run])): t['p_holm'] = a
        out.update(voynich=V, tests=tests, audit_c091_prefix=aud)
    out['elapsed_s'] = time.time() - t0
    return out

if __name__ == '__main__':
    o = main(sys.argv[1]); json.dump(o, open(sys.argv[2], 'w'), indent=1, default=str)
    for s, v in o['generator'].items(): print(s, v['ntokens'], v['ntypes_15k'], {k: (round(x['Q'], 4) if x['Q'] else None, round(x['Q_plant'], 4) if x['Q_plant'] else None) for k, x in v.items() if isinstance(x, dict)})
    for c, g in o['gates'].items(): print(c, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in g.items()})
    if o['mode'] == 'run':
        print('voynich', o['voynich']); print('audit prefix', o['audit_c091_prefix'])
        for t in o['tests']: print(t)
    print('elapsed', round(o['elapsed_s'], 1))
