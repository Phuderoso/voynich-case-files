#!/usr/bin/env python3
"""C091 (F-ANAG step 2, the UNSORTED anagram reading, Hauer & Kondrak 2016): do Voynich word types form anagram families
(different types written with the same multiset of glyph units) at the rate a freely-anagrammed text would show?
Units: Voynich = C003 glyph units; natural texts = letters. Sample: distinct word types of 3-8 units among the first
N = 15,000 word tokens (same sample rule as C090).
Statistic Q = share of those types whose unit multiset is shared with at least one OTHER type in the sample.
No search / optimiser is involved (Q is an exact count), so no optimiser-effort audit is needed.
References: 9 natural texts (C077 set); 9 FREE-SCRAMBLE plants (every token of each natural text has its letters put in a
fresh random order, independently per occurrence: the unsorted anagram cipher); 10 fresh default Timm-Schinner generator
runs (seeds 11454-11463, 2,500 lines; next generator seed 11464).
Tests per transcription (ZL 3b, IT2a); predictive-t p = t of (x - mean)/(sd*sqrt(1+1/n)), df n-1:
 H1 FREE ANAGRAM EXCLUDED: one-sided, Voynich Q below the 9 free-scramble plants.
 H3 vs GENERATOR: two-sided, Voynich Q differs from the 10 generator runs.
 H2 vs NATURAL: rule set by H2MODE (fixed in rehearsal BEFORE the pre-registration push, see case file):
   't'     two-sided predictive-t vs the 9 naturals, inside Holm;
   'below' range rule: BELOW NATURAL iff Q < min of the 9 naturals in both transcriptions (false-call rate 1/9 by
           construction, outside Holm).
Holm over the predictive-t tests, alpha 0.05; a call needs both transcriptions.
Gates (rehearsed before the push, references only; Voynich untouched in rehearsal):
 G1 FPR, leave-one-out inside each reference set at raw p < 0.05: <= 1/n.
 G2 power: H1 = unscrambled naturals vs plants called EXCLUDED >= 8/9; H2 't' = each natural with F2 of tokens freely
    scrambled vs the other 8 unplanted >= 8/9, H2 'below' = each natural with F2 of types alphagrammed (hidden order)
    below min of the other 8 >= 8/9; H3 = each generator run with F3 of tokens freely scrambled vs the other 9 >= 8/10.
 A hypothesis whose gate fails is NOT TESTABLE (descriptive only).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time, math
from collections import Counter, defaultdict
from multiprocessing import Pool
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.dirname(__file__))
import c077_direction as D

SEED, N = 9191, 15000
F2, F3 = float(os.environ.get('F2', 0.25)), float(os.environ.get('F3', 0.10))
H2MODE = os.environ.get('H2MODE', 't')  # fixed to 't' after rehearsal (below-range power 1/9 = dead on arrival)
GSEEDS = list(range(11454, 11464))
ALPHA = 0.05

def types_of(words):
    seen, out = set(), []
    for w in words[:N]:
        t = tuple(w)
        if 3 <= len(t) <= 8 and t not in seen: seen.add(t); out.append(t)
    return out

def Q_of(words):
    ty = types_of(words); fam = Counter(tuple(sorted(t)) for t in ty)
    q = sum(fam[tuple(sorted(t))] >= 2 for t in ty) / len(ty)
    return dict(Q=q, ntypes=len(ty), nclasses=len(fam), nfam2=sum(v >= 2 for v in fam.values()),
                maxfam=max(fam.values()))

def scramble_tokens(words, rng, frac):
    return [tuple(rng.permutation(list(w))) if (len(w) > 1 and rng.random() < frac) else tuple(w) for w in words[:N]]

def alphagram_types(words, rng, frac):
    syms = sorted({s for w in words[:N] for s in w}); hid = {s: r for s, r in zip(syms, rng.permutation(len(syms)))}
    pick = {}; out = []
    for w in words[:N]:
        t = tuple(w)
        if t not in pick: pick[t] = rng.random() < frac
        out.append(tuple(sorted(t, key=lambda s: hid[s])) if pick[t] else t)
    return out

def gen_words(s):
    import c004_generator_sweep as G
    Lg = G.generate({'text.lines_to_create': 2500}, s)
    ws = [D.T.units(w) for l in (Lg or []) for w in l][:N]
    return ws if len(ws) >= N else None

def job(spec):
    kind, name, s = spec; rng = np.random.default_rng([SEED, s])
    if kind == 'nat': ws = D.seqs_nat(*D.NAT[name])
    elif kind == 'gen':
        ws = gen_words(s)
        if ws is None: return (kind, name, None)
    else: ws = D.seqs_voy(name)
    out = {'ref': Q_of(ws)}
    if kind == 'nat':
        out['free'] = Q_of(scramble_tokens(ws, rng, 1.0))
        out['partial_scramble'] = Q_of(scramble_tokens(ws, rng, F2))
        out['partial_alphagram'] = Q_of(alphagram_types(ws, rng, F2))
    elif kind == 'gen':
        out['partial_scramble'] = Q_of(scramble_tokens(ws, rng, F3))
        out['free_descriptive'] = Q_of(scramble_tokens(ws, rng, 1.0))  # unit-alphabet free-scramble, descriptive only
    return (kind, name, out)

def pt(x, ref, side):
    ref = np.asarray(ref, float); n = len(ref); t = (x - ref.mean()) / (ref.std(ddof=1) * math.sqrt(1 + 1 / n))
    if side == 'below': return float(stats.t.cdf(t, n - 1))
    if side == 'above': return float(stats.t.sf(t, n - 1))
    return float(2 * stats.t.sf(abs(t), n - 1))

def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0] * len(ps); run = 0
    for k, i in enumerate(o): run = max(run, min(1, (len(ps) - k) * ps[i])); adj[i] = run
    return adj

def mde(ref, side):
    ref = np.asarray(ref); n = len(ref); s = ref.std(ddof=1) * math.sqrt(1 + 1 / n)
    q = stats.t.ppf(1 - (ALPHA if side != 'two' else ALPHA / 2), n - 1); return float((q + stats.norm.ppf(0.8)) * s)

def main(mode):
    t0 = time.time()
    specs = [('nat', n, 100 + i) for i, n in enumerate(D.NAT)] + [('gen', f'gen_{s}', s) for s in GSEEDS]
    if mode == 'run': specs += [('voy', 'data/ZL3b-n.txt', 1), ('voy', 'data/IT2a-n.txt', 2)]
    with Pool(8) as p: res = p.map(job, specs)
    R = {n: o for k, n, o in res}
    nat = list(D.NAT); gen = [f'gen_{s}' for s in GSEEDS if R.get(f'gen_{s}')]
    Qn = {n: R[n]['ref']['Q'] for n in nat}; Qf = {n: R[n]['free']['Q'] for n in nat}; Qg = {g: R[g]['ref']['Q'] for g in gen}
    fpr1 = sum(pt(Qf[n], [Qf[m] for m in nat if m != n], 'below') < ALPHA for n in nat)
    fpr2t = sum(pt(Qn[n], [Qn[m] for m in nat if m != n], 'two') < ALPHA for n in nat)
    fpr2b = sum(Qn[n] < min(Qn[m] for m in nat if m != n) for n in nat)
    fpr3 = sum(pt(Qg[g], [Qg[h] for h in gen if h != g], 'two') < ALPHA for g in gen)
    pow1 = sum(pt(Qn[n], list(Qf.values()), 'below') < ALPHA for n in nat)
    pow2t = sum(pt(R[n]['partial_scramble']['Q'], [Qn[m] for m in nat if m != n], 'two') < ALPHA for n in nat)
    pow2b = sum(R[n]['partial_alphagram']['Q'] < min(Qn[m] for m in nat if m != n) for n in nat)
    pow3 = sum(pt(R[g]['partial_scramble']['Q'], [Qg[h] for h in gen if h != g], 'two') < ALPHA for g in gen)
    sh2t = float(np.mean([R[n]['partial_scramble']['Q'] - Qn[n] for n in nat]))
    sh2b = float(np.mean([R[n]['partial_alphagram']['Q'] - Qn[n] for n in nat]))
    sh3 = float(np.mean([R[g]['partial_scramble']['Q'] - Qg[g] for g in gen]))
    gates = dict(FPR_H1=f'{fpr1}/9', FPR_H2_t=f'{fpr2t}/9', FPR_H2_below_range=f'{fpr2b}/9', FPR_H3=f'{fpr3}/{len(gen)}',
                 POW_H1=f'{pow1}/9', POW_H2_t=f'{pow2t}/9', POW_H2_below_range=f'{pow2b}/9', POW_H3=f'{pow3}/{len(gen)}',
                 gap_H1=float(np.mean(list(Qf.values())) - np.mean(list(Qn.values()))), MDE80_H1=mde(list(Qf.values()), 'below'),
                 shift_H2_t=sh2t, shift_H2_below=sh2b, MDE80_H2_t=mde(list(Qn.values()), 'two'),
                 shift_H3=sh3, MDE80_H3=mde(list(Qg.values()), 'two'))
    ok = dict(H1=fpr1 <= 1 and pow1 >= 8,
              H2=(fpr2t <= 1 and pow2t >= 8) if H2MODE == 't' else (fpr2b <= 1 and pow2b >= 8),
              H3=fpr3 <= 1 and pow3 >= 8 and len(gen) >= 8)
    out = dict(seed=SEED, mode=mode, N=N, F2=F2, F3=F3, H2MODE=H2MODE, gates=gates, testable=ok,
               naturals={n: R[n] for n in nat}, generator={g: R[g] for g in gen},
               summary=dict(nat=Qn, free=Qf, gen=Qg))
    if mode == 'run':
        V = {'ZL3b': R['data/ZL3b-n.txt']['ref'], 'IT2a': R['data/IT2a-n.txt']['ref']}
        ps, keys = [], []
        for tname, v in V.items():
            q = v['Q']; hs = [('H1', list(Qf.values()), 'below'), ('H3', list(Qg.values()), 'two')]
            if H2MODE == 't': hs.append(('H2', list(Qn.values()), 'two'))
            for h, ref, side in hs: ps.append(pt(q, ref, side)); keys.append((tname, h))
        adj = holm(ps)
        out['H2_range'] = {t: dict(Q=v['Q'], min_nat=min(Qn.values()), max_nat=max(Qn.values()),
                           below=v['Q'] < min(Qn.values())) for t, v in V.items()}
        out['voynich'] = V; out['tests'] = [dict(transcription=t, H=h, p=p, p_holm=q) for (t, h), p, q in zip(keys, ps, adj)]
    out['elapsed_s'] = time.time() - t0
    return out

if __name__ == '__main__':
    mode = sys.argv[1]; o = main(mode)
    json.dump(o, open(sys.argv[2], 'w'), indent=1, default=str)
    print(json.dumps({k: o[k] for k in ('gates', 'testable', 'elapsed_s')}, indent=1))
    for k, v in o['summary'].items(): print(k, {a: round(b, 4) for a, b in v.items()})
    for n in o['naturals']: print(n, {k: round(x['Q'], 4) for k, x in o['naturals'][n].items()})
    for g in o['generator']: print(g, {k: round(x['Q'], 4) for k, x in o['generator'][g].items()}, o['generator'][g]['ref']['ntypes'])
    if mode == 'run':
        print('voynich', o['voynich'])
        for t in o['tests']: print(t)
        print('H2 range', o['H2_range'])
