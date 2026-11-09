#!/usr/bin/env python3
"""C082 (F-AFFIX step 2, confirmatory): is the manuscript's first/last-symbol coupling K BELOW the Timm-Schinner
generator?  Statistic K exactly as C081 (same texts, loaders, strata {3,4,5,6,>=7}, E_null = mean of 50 within-stratum
shuffles of the last symbol).  Repaired CI (C081 flaw): half-sample subsampling WITHOUT replacement -- B = 400 draws of
10 of the 20 contiguous blocks; in every draw E_null is recomputed on the drawn half (20 shuffles).  With m = n/2 the
spread of (K_half - K_full) estimates the sampling spread of K_full (finite-population factor 1/m - 1/n = 1/n), so the
95% CI is the basic interval [K - q97.5(d), K - q2.5(d)], d = K_half - K_full.
Generator: 20 reference runs (seeds 11211-11230), 10 held-out unmodified runs (11231-11240, false-positive gate),
5 plant hosts (11241-11245; endings of 25% of tokens shuffled within strata, seed-fixed = positive control).
Rule per text X: BELOW GENERATOR iff K_X < min(reference) [rank p = 1/21 under exchangeability] AND CI_X upper < min;
ABOVE symmetric; INSIDE GENERATOR RANGE if min <= K_X <= max; else NOT CALLED.
H1 (confirmatory) = both transcriptions BELOW (intersection-union, alpha 0.05, no further correction).
Gates: (G1) CI repair valid: point K inside its CI for every CI row (centring |median d| <= 0.25 half-width is
reported descriptively only: the Caesar smoke test showed median d = -0.0047, a residual small-sample bias that the basic
interval moves upward, i.e. conservatively for BELOW); (G2) false positives: <= 2 of 10 held-out runs called BELOW or ABOVE; (G3) power: >= 4 of 5 plants called BELOW.
Any gate failing -> H1 NOT TESTABLE.  H2 (secondary) = C081 natural range rule with repaired CI, LOO gate <= 1/9,
decoupled-Caesar control must be OUTSIDE NATURAL.  Seed 8282.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c077_direction as D
SEED, NBLK, B, NNULL, NNULL_SUB, PLANT_F = 8282, 20, 400, 50, 20, 0.25
REF, HOLD, PLANT = range(11211, 11231), range(11231, 11241), range(11241, 11246)

def strat(n): return min(n, 7) - 3

def cmi(F, L, S, A):
    """I(F;L|S), H(L|S) in bits (plug-in), vectorised; identical to C081's Counter version up to rounding."""
    n = len(S); j = np.bincount((S * A + F) * A + L, minlength=5 * A * A).reshape(5, A, A).astype(float)
    ns = j.sum((1, 2)); cf = j.sum(2); cl = j.sum(1); I = H = 0.0
    for s in range(5):
        if ns[s] == 0: continue
        m = j[s] > 0; e = np.outer(cf[s], cl[s])[m]
        I += (j[s][m] / n * np.log2(j[s][m] * ns[s] / e)).sum()
        c = cl[s][cl[s] > 0]; H -= (c / n * np.log2(c / ns[s])).sum()
    return I, H

def arrays(words):
    ws = [w for w in words if len(w) >= 3]; sym = {}
    F = np.array([sym.setdefault(w[0], len(sym)) for w in ws]); L = np.array([sym.setdefault(w[-1], len(sym)) for w in ws])
    S = np.array([strat(len(w)) for w in ws]); return F, L, S, len(sym)

def shuffle_last(L, S, rng):
    L2 = L.copy()
    for s in np.unique(S):
        i = np.where(S == s)[0]; L2[i] = L[rng.permutation(i)]
    return L2

def kval(F, L, S, A, rng, nnull):
    I, H = cmi(F, L, S, A); En = float(np.mean([cmi(F, shuffle_last(L, S, rng), S, A)[0] for _ in range(nnull)]))
    return (I - En) / H, I, En, H

def analyse(name, words, boot=True):
    rng = np.random.default_rng([SEED, sum(map(ord, name))]); F, L, S, A = arrays(words)
    K, I, En, H = kval(F, L, S, A, rng, NNULL)
    out = dict(n_tokens=int(len(S)), I=float(I), E_null=En, H_last=float(H), K=float(K))
    if boot:
        e = np.linspace(0, len(S), NBLK + 1).astype(int); bl = [np.arange(e[b], e[b + 1]) for b in range(NBLK)]; d = []
        for _ in range(B):
            idx = np.sort(np.concatenate([bl[j] for j in rng.choice(NBLK, NBLK // 2, replace=False)]))
            d.append(kval(F[idx], L[idx], S[idx], A, rng, NNULL_SUB)[0] - K)
        q_lo, q_hi = np.percentile(d, [2.5, 97.5]); ci = [float(K - q_hi), float(K - q_lo)]
        out.update(ci=ci, median_d=float(np.median(d)), sd_d=float(np.std(d)))
    return name, out

def decoupled(words, rng, frac=1.0):
    ws = [w for w in words if len(w) >= 3]; S = np.array([strat(len(w)) for w in ws]); out = [list(w) for w in ws]
    pick = rng.random(len(ws)) < frac
    for s in np.unique(S):
        i = np.where((S == s) & pick)[0]; p = rng.permutation(i)
        lasts = [ws[j][-1] for j in p]
        for j, x in zip(i, lasts): out[j][-1] = x
    return out

def gen_words(s):
    import c004_generator_sweep as G
    Lg = G.generate({'text.lines_to_create': 2500}, s)
    ws = [D.T.units(w) for l in (Lg or []) for w in l][:D.N]
    return ws if len(ws) >= D.N else None

def gen_job(s):
    ws = gen_words(s)
    if ws is None: return (f'gen_{s}', None)
    if s in HOLD: return analyse(f'hold_{s}', ws, boot=True)
    if s in PLANT: return analyse(f'plant_{s}', decoupled(ws, np.random.default_rng([SEED, s]), PLANT_F), boot=True)
    return analyse(f'gen_{s}', ws, boot=False)

def gcall(ci, x, lo, hi):
    if x < lo and ci[1] < lo: return 'BELOW GENERATOR'
    if x > hi and ci[0] > hi: return 'ABOVE GENERATOR'
    return 'INSIDE GENERATOR RANGE' if lo <= x <= hi else 'NOT CALLED'

def main():
    t0 = time.time()
    texts = {n: D.seqs_nat(*v) for n, v in D.NAT.items()}
    voy = {'Voynich_ZL3b': D.seqs_voy('data/ZL3b-n.txt'), 'Voynich_IT2a': D.seqs_voy('data/IT2a-n.txt')}
    ctrl = {'CONTROL_Caesar_decoupled': decoupled(texts['Latin_Caesar'], np.random.default_rng([SEED, 1]))}
    with Pool(8) as pool:
        gj = pool.map_async(gen_job, list(REF) + list(HOLD) + list(PLANT), chunksize=1)
        R = dict(pool.starmap(analyse, list(texts.items()) + list(voy.items()) + list(ctrl.items())))
        Gall = dict(gj.get())
    ref = {k: v for k, v in Gall.items() if k.startswith('gen_') and v}
    hold = {k: v for k, v in Gall.items() if k.startswith('hold_') and v}
    plant = {k: v for k, v in Gall.items() if k.startswith('plant_') and v}
    ga = [g['K'] for g in ref.values()]; glo, ghi = min(ga), max(ga)
    cirows = {**R, **hold, **plant}
    inside = all(r['ci'][0] <= r['K'] <= r['ci'][1] for r in cirows.values())
    centred = sum(abs(r['median_d']) <= 0.25 * (r['ci'][1] - r['ci'][0]) / 2 for r in cirows.values())
    g1 = inside
    hold_calls = {k: gcall(v['ci'], v['K'], glo, ghi) for k, v in hold.items()}
    g2n = sum(c in ('BELOW GENERATOR', 'ABOVE GENERATOR') for c in hold_calls.values()); g2 = g2n <= 2 and len(hold) == 10
    plant_calls = {k: gcall(v['ci'], v['K'], glo, ghi) for k, v in plant.items()}
    g3n = sum(c == 'BELOW GENERATOR' for c in plant_calls.values()); g3 = g3n >= 4 and len(plant) == 5
    enough = len(ref) >= 18
    nat = list(D.NAT); fp = 0
    for n in nat:
        o = [R[m]['K'] for m in nat if m != n]; fp += D.call(R[n]['ci'], R[n]['K'], min(o), max(o)) == 'OUTSIDE NATURAL'
    lo, hi = min(R[m]['K'] for m in nat), max(R[m]['K'] for m in nat)
    c = R['CONTROL_Caesar_decoupled']; ctrl_call = D.call(c['ci'], c['K'], lo, hi); ctrl_ok = ctrl_call == 'OUTSIDE NATURAL'
    gates = dict(G1_ci_valid=g1, G1_all_inside=inside, G1_centred=f'{centred}/{len(cirows)}', G2_holdout_rejections=f'{g2n}/{len(hold)}',
                 G2=g2, G3_plants_below=f'{g3n}/{len(plant)}', G3=g3, n_reference=len(ref), enough_reference=enough,
                 H2_loo_outside=fp, H2_loo_pass=fp <= 1, H2_control=ctrl_call, H2_control_ok=ctrl_ok)
    ver = {}
    for v in voy:
        ci, x = R[v]['ci'], R[v]['K']
        ver[v] = dict(K=x, ci=ci, rank_below=sum(g < x for g in ga), generator_call=gcall(ci, x, glo, ghi),
                      natural=D.call(ci, x, lo, hi) if g1 and fp <= 1 and ctrl_ok else 'NOT TESTABLE')
    if not (g1 and g2 and g3 and enough): H1 = 'NOT TESTABLE'
    elif all(ver[v]['generator_call'] == 'BELOW GENERATOR' for v in voy): H1 = 'BELOW GENERATOR (H1 supported)'
    elif all(ver[v]['generator_call'] == 'INSIDE GENERATOR RANGE' for v in voy): H1 = 'INSIDE GENERATOR RANGE (H1 rejected)'
    else: H1 = 'NOT CALLED (' + ' / '.join(ver[v]['generator_call'] for v in voy) + ')'
    out = dict(seed=SEED, N=D.N, B=B, results=R, reference=ref, holdout=hold, plants=plant, holdout_calls=hold_calls,
               plant_calls=plant_calls, generator_range=[glo, ghi], natural_range=[lo, hi], gates=gates, verdict=ver, H1=H1,
               missing_generator=[k for k, v in Gall.items() if v is None], runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C082_results.json', 'w'), indent=1)
    for n, r in list(R.items()) + list(hold.items()) + list(plant.items()) + list(ref.items()):
        print(n, r['n_tokens'], round(r['K'], 4), [round(v, 4) for v in r.get('ci', [])], round(r.get('median_d', 0), 4))
    print('generator range', round(glo, 4), round(ghi, 4)); print('holdout', hold_calls); print('plants', plant_calls)
    print('gates', gates)
    for k, v in ver.items(): print(k, json.dumps(v))
    print('H1', H1); print('runtime', out['runtime_s'])

if __name__ == '__main__':
    main()
