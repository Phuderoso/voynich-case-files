#!/usr/bin/env python3
"""C090 (NEW FAMILY F-ANAG, the anagram / alphagram premise, Hauer & Kondrak 2016): is there ONE fixed ordering of the
glyph units under which Voynich words are written in sorted order (alphagrams), as the strongest anagram reading needs?
Units: Voynich = C003 glyph units; natural texts = letters. Sample: distinct word types of length 3-8 units among the
first N = 15,000 word tokens. M(order) = share of types whose adjacent distinct-symbol pairs all rise in the order
(repeats allowed). M* = best M over orders (insertion local search, 6 starts: 1 mean-position start + 5 random).
Null: every type's symbols shuffled inside the word (K = 10 copies), M* re-optimised; A = (M* - mean M*_shuf)/(1 - mean).
A = 1: perfect alphagram text; A ~ 0: word-internal order no more 'sortable' than random arrangement.
References: 9 natural texts (C077 set); 9 DEGRADED ALPHAGRAM plants (each natural text sorted by a hidden random order,
then 10% of types get one random adjacent transposition: copy/transcription noise); 10 fresh default Timm-Schinner
generator runs (seeds 11444-11453, 2,500 lines).
Tests, per transcription (ZL 3b, IT2a), predictive-t p against a reference set (x - mean)/(sd*sqrt(1+1/n)), df n-1:
 H1 ALPHAGRAM EXCLUDED: one-sided, Voynich A below the degraded-alphagram plants.
 H3 vs GENERATOR:       two-sided, Voynich A differs from the 10 generator runs.
 H2 ABOVE NATURAL (range rule, changed in rehearsal before the push: the predictive-t version failed its FPR gate 2/9
    because the two Hebrew texts sit apart): ABOVE NATURAL if A > max of the 9 natural values in both transcriptions;
    false-call rate of this rule on exchangeable draws is 1/9 by construction (no p-value, so outside Holm).
Holm over 4 (H1, H3 x 2 transcriptions), alpha 0.05; a call needs both transcriptions.
Gates (rehearsed before the pre-registration push, I-119; real Voynich never touched in rehearsal, I-116):
 G0 full alphagram plants (no noise) A >= 0.95 in 9/9.
 G1 FPR, leave-one-out inside each reference set at raw p < 0.05: H1 plants, H2 naturals, H3 generator runs <= 1/n.
 G2 power: H1 = unsorted naturals vs plants called EXCLUDED >= 8/9;  H2 = each natural with a fraction F2 of its types
    sorted (hidden order) vs the other 8 unplanted, detected >= 8/9;  H3 = each generator run with F3 of types sorted vs
    the other 9 unplanted, detected >= 8/10.  A hypothesis whose gate fails is NOT TESTABLE (descriptive only).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time, math
from multiprocessing import Pool
import numpy as np
from scipy import sparse, stats
sys.path.insert(0, os.path.dirname(__file__))
import c077_direction as D

SEED, N, K, STARTS, NOISE = 9090, 15000, 10, 6, 0.10
F2, F3 = float(os.environ.get('F2', 0.25)), float(os.environ.get('F3', 0.25))
GSEEDS = list(range(11444, 11454))
ALPHA = 0.05

def types_of(words):
    seen, out = set(), []
    for w in words[:N]:
        t = tuple(w)
        if 3 <= len(t) <= 8 and t not in seen: seen.add(t); out.append(t)
    return out

def build(types):
    syms = sorted({s for t in types for s in t}); ix = {s: i for i, s in enumerate(syms)}; S = len(syms)
    rows, cols = [], []
    for r, t in enumerate(types):
        for a, b in zip(t, t[1:]):
            if a != b: rows.append(r); cols.append(ix[a] * S + ix[b])
    Bm = sparse.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(types), S * S))
    Bm.data[:] = 1.0
    return syms, ix, Bm

def score(Bm, rank, S):
    v = (rank[:, None] > rank[None, :]).astype(float).ravel()
    return float(np.mean((Bm @ v) == 0))

def optimise(types, rng):
    syms, ix, Bm = build(types); S = len(syms)
    pos = np.zeros(S); cnt = np.zeros(S)
    for t in types:
        for j, s in enumerate(t): pos[ix[s]] += j / max(1, len(t) - 1); cnt[ix[s]] += 1
    starts = [list(np.argsort(pos / np.maximum(cnt, 1)))] + [list(rng.permutation(S)) for _ in range(STARTS - 1)]
    best = -1
    for order in starts:
        rank = np.empty(S); rank[order] = np.arange(S); cur = score(Bm, rank, S)
        for _ in range(30):
            improved = False
            for s in range(S):
                o = [x for x in order if x != s]; bm, bo = cur, None
                for p in range(S):
                    cand = o[:p] + [s] + o[p:]; r2 = np.empty(S); r2[cand] = np.arange(S); m = score(Bm, r2, S)
                    if m > bm + 1e-12: bm, bo = m, cand
                if bo is not None: order, cur, improved = bo, bm, True
            if not improved: break
        best = max(best, cur)
    return best

def A_of(types, seed):
    rng = np.random.default_rng(seed)
    m = optimise(types, rng)
    ms = [optimise([tuple(rng.permutation(list(t))) for t in types], rng) for _ in range(K)]
    mu = float(np.mean(ms))
    return dict(M=m, Mshuf=mu, Mshuf_sd=float(np.std(ms, ddof=1)), A=(m - mu) / (1 - mu), ntypes=len(types))

def sort_types(types, rng, frac, noise=0.0):
    syms = sorted({s for t in types for s in t}); hidden = {s: r for r, s in enumerate(rng.permutation(len(syms)))}
    hid = {s: hidden[i] for i, s in enumerate(syms)}
    pick = rng.random(len(types)) < frac; out = []
    for t, p in zip(types, pick):
        t = tuple(sorted(t, key=lambda s: hid[s])) if p else t
        if noise and rng.random() < noise:
            j = rng.integers(len(t) - 1); t = t[:j] + (t[j + 1], t[j]) + t[j + 2:]
        out.append(t)
    return out

def gen_types(s):
    import c004_generator_sweep as G
    Lg = G.generate({'text.lines_to_create': 2500}, s)
    ws = [D.T.units(w) for l in (Lg or []) for w in l][:N]
    return types_of(ws) if len(ws) >= N else None

def job(spec):
    kind, name, s = spec; rng = np.random.default_rng([SEED, s])
    if kind == 'nat': ty = types_of(D.seqs_nat(*D.NAT[name]))
    elif kind == 'gen':
        ty = gen_types(s)
        if ty is None: return (kind, name, None)
    elif kind == 'voy': ty = types_of(D.seqs_voy(name))
    if kind in ('nat', 'gen'):
        out = {'ref': A_of(ty, [SEED, s, 0])}
        f = F2 if kind == 'nat' else F3
        out['partial'] = A_of(sort_types(ty, rng, f), [SEED, s, 1])
        if kind == 'nat':
            out['full'] = A_of(sort_types(ty, rng, 1.0), [SEED, s, 2])
            out['degraded'] = A_of(sort_types(ty, rng, 1.0, NOISE), [SEED, s, 3])
        return (kind, name, out)
    return (kind, name, {'ref': A_of(ty, [SEED, s, 0])})

def pt(x, ref, side):
    ref = np.asarray(ref, float); n = len(ref); t = (x - ref.mean()) / (ref.std(ddof=1) * math.sqrt(1 + 1 / n))
    if side == 'below': return float(stats.t.cdf(t, n - 1))
    if side == 'above': return float(stats.t.sf(t, n - 1))
    return float(2 * stats.t.sf(abs(t), n - 1))

def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0] * len(ps); run = 0
    for k, i in enumerate(o): run = max(run, min(1, (len(ps) - k) * ps[i])); adj[i] = run
    return adj

def main(mode):
    t0 = time.time()
    specs = [('nat', n, 100 + i) for i, n in enumerate(D.NAT)] + [('gen', f'gen_{s}', s) for s in GSEEDS]
    if mode == 'run': specs += [('voy', 'data/ZL3b-n.txt', 1), ('voy', 'data/IT2a-n.txt', 2)]
    with Pool(8) as p: res = p.map(job, specs)
    R = {n: o for k, n, o in res}
    nat = [n for n in D.NAT]; gen = [f'gen_{s}' for s in GSEEDS if R.get(f'gen_{s}')]
    An = {n: R[n]['ref']['A'] for n in nat}; Ad = {n: R[n]['degraded']['A'] for n in nat}
    Af = {n: R[n]['full']['A'] for n in nat}; Ag = {g: R[g]['ref']['A'] for g in gen}
    g0 = sum(Af[n] >= 0.95 for n in nat)
    fpr1 = sum(pt(Ad[n], [Ad[m] for m in nat if m != n], 'below') < ALPHA for n in nat)
    fpr2t = sum(pt(An[n], [An[m] for m in nat if m != n], 'above') < ALPHA for n in nat)
    fpr2 = sum(An[n] > max(An[m] for m in nat if m != n) for n in nat)
    fpr3 = sum(pt(Ag[g], [Ag[h] for h in gen if h != g], 'two') < ALPHA for g in gen)
    pow1 = sum(pt(An[n], list(Ad.values()), 'below') < ALPHA for n in nat)
    pow2 = sum(R[n]['partial']['A'] > max(An[m] for m in nat if m != n) for n in nat)
    pow3 = sum(pt(R[g]['partial']['A'], [Ag[h] for h in gen if h != g], 'two') < ALPHA for g in gen)
    sh2 = float(np.mean([R[n]['partial']['A'] - An[n] for n in nat])); sh3 = float(np.mean([R[g]['partial']['A'] - Ag[g] for g in gen]))
    def mde(ref, side):
        ref = np.asarray(ref); n = len(ref); s = ref.std(ddof=1) * math.sqrt(1 + 1 / n)
        q = stats.t.ppf(1 - (ALPHA if side != 'two' else ALPHA / 2), n - 1); return float((q + stats.norm.ppf(0.8)) * s)
    gates = dict(G0=f'{g0}/9', FPR_H1=f'{fpr1}/9', FPR_H2_predictive_t_dropped=f'{fpr2t}/9', FPR_H2_range=f'{fpr2}/9', FPR_H3=f'{fpr3}/{len(gen)}',
                 POW_H1=f'{pow1}/9', POW_H2_range=f'{pow2}/9', POW_H3=f'{pow3}/{len(gen)}',
                 shift_H2=sh2, MDE80_H2=mde(list(An.values()), 'above'), shift_H3=sh3, MDE80_H3=mde(list(Ag.values()), 'two'),
                 gap_H1=float(np.mean(list(Ad.values())) - np.mean(list(An.values()))), MDE80_H1=mde(list(Ad.values()), 'below'))
    ok = dict(H1=g0 == 9 and fpr1 <= 1 and pow1 >= 8, H2=g0 == 9 and fpr2 <= 1 and pow2 >= 8,
              H3=g0 == 9 and fpr3 <= 1 and pow3 >= 8 and len(gen) >= 8)
    out = dict(seed=SEED, mode=mode, N=N, K=K, STARTS=STARTS, NOISE=NOISE, F2=F2, F3=F3, gates=gates, testable=ok,
               naturals={n: R[n] for n in nat}, generator={g: R[g] for g in gen},
               summary=dict(nat=An, degraded=Ad, full=Af, gen=Ag))
    if mode == 'run':
        V = {'ZL3b': R['data/ZL3b-n.txt']['ref'], 'IT2a': R['data/IT2a-n.txt']['ref']}
        ps, keys = [], []
        for tname, v in V.items():
            a = v['A']
            for h, ref, side in (('H1', list(Ad.values()), 'below'), ('H3', list(Ag.values()), 'two')):
                ps.append(pt(a, ref, side)); keys.append((tname, h))
        adj = holm(ps)
        out['H2_range'] = {t: dict(A=v['A'], max_nat=max(An.values()), above=v['A'] > max(An.values()),
                           p_pred_t_descriptive=pt(v['A'], list(An.values()), 'above')) for t, v in V.items()}
        out['voynich'] = V; out['tests'] = [dict(transcription=t, H=h, p=p, p_holm=q) for (t, h), p, q in zip(keys, ps, adj)]
    out['elapsed_s'] = time.time() - t0
    return out

if __name__ == '__main__':
    mode = sys.argv[1]; o = main(mode)
    json.dump(o, open(sys.argv[2], 'w'), indent=1, default=str)
    print(json.dumps({k: o[k] for k in ('gates', 'testable', 'elapsed_s')}, indent=1))
    for k, v in o['summary'].items(): print(k, {a: round(b, 3) for a, b in v.items()})
    if mode == 'run':
        print('voynich', {t: {k: round(x, 4) for k, x in v.items()} for t, v in o['voynich'].items()})
        for t in o['tests']: print(t)
        print('H2 range', o['H2_range'])
