#!/usr/bin/env python3
"""C085 (F-AFFIX step 4, confirmatory EQUIVALENCE): does the surface-matched C005 configuration of the Timm-Schinner
generator reproduce the manuscript's first/last-symbol coupling K within a margin fixed in advance?
Statistic K and half-sample CI exactly as C082 (tools/c082_affix_repaired.py; seed 8585), plus the 5/95 percentiles for
the 90% interval used by TOST.  Configuration = C083 cell 64 (C005 'A' selected config, f103r line-1 seed), 2,500 lines.
Seeds (fresh): reference 11321-11360 (40 runs, K only), held-out 11361-11380 (20 unmodified runs with CI), decoupled
plants 11381-11385 (C005 runs with the last symbol of 70% of tokens shuffled within length strata), default-config
controls 11386-11390 (generator defaults, as C082).  Smoke on seed 11999 only (reserved, I-116).
TOST per text X: d = K_X - m, m = mean of the reference runs, se = sd/sqrt(n_ref);
  90% CI of d = [ci90_lo(X) - m - 1.645 se, ci90_hi(X) - m + 1.645 se].
  EQUIVALENT iff CI within [-DELTA, +DELTA]; BELOW/ABOVE BEYOND MARGIN iff CI entirely below -DELTA / above +DELTA;
  else INCONCLUSIVE.  DELTA = 0.030 chosen in tools/c085_design.py (smallest of a pre-stated menu with simulated
  power >= 0.80, cap 0.033), from precision numbers only.
H1 (both transcriptions, intersection-union, no further correction): both EQUIVALENT -> EQUIVALENT; both BEYOND on the
same side -> EXCLUDED (that side); one EQUIVALENT + one INCONCLUSIVE -> NOT CALLED (equivalence for one transcription
only); one EQUIVALENT + one BEYOND -> TRANSCRIPTION-DEPENDENT (NOT CALLED); anything else -> INCONCLUSIVE.
H2 (secondary): mean surface stats (mwl, ttr, h2, R; first 6,000 words) of the reference runs within +-15% of the C005
reference -> FEASIBILITY CONFIRMED, else FEASIBILITY LOST (then an H1 EQUIVALENT reads 'equivalent only with surface loss').
Secondary reading (no confirmatory weight): C084-style |K_X - m| <= 2 sd_between_runs.
Gates (fail -> H1 NOT TESTABLE): G1 every CI (95% and 90%) contains its point; G2 held-out: EQUIVALENT >= 8/20 and
BEYOND <= 2/20 (bars from the I-119 calibration in tools/c085_design.py: expected EQUIVALENT rate 0.60, BEYOND 0.002); G3a plants: BELOW BEYOND >= 4/5 and EQUIVALENT 0/5; G3b default controls: EQUIVALENT <= 1/5;
G4 >= 36/40 reference runs usable.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import os
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ[v] = '1'
import sys, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c077_direction as D
import c082_affix_repaired as A
import c004_generator_sweep as G
import c005_targeted_search as C5
SEED = A.SEED = 8585
REF, HOLD, PLANT, DEFC = range(11321, 11361), range(11361, 11381), range(11381, 11386), range(11386, 11391)
DELTA, Z, PLANT_F = 0.030, 1.645, 0.70
SURF = {'mwl': 4.56641, 'ttr': 0.3535733333333333, 'h2': 2.249330242292793, 'R': 0.4871370421623037}
TOL = 0.15

def c005cfg():
    c = dict(json.load(open('analysis/C005_confirm.json'))['A']['selected'])
    c['text.initial_line'] = C5.LINES[c['text.initial_line']]; c['text.lines_to_create'] = 2500; return c

def analyse(name, words, boot=True):
    rng = np.random.default_rng([SEED, sum(map(ord, name))]); F, L, S, Al = A.arrays(words)
    K, I, En, H = A.kval(F, L, S, Al, rng, A.NNULL)
    out = dict(n_tokens=int(len(S)), I=float(I), E_null=En, H_last=float(H), K=float(K))
    if boot:
        e = np.linspace(0, len(S), A.NBLK + 1).astype(int); bl = [np.arange(e[b], e[b + 1]) for b in range(A.NBLK)]; d = []
        for _ in range(A.B):
            idx = np.sort(np.concatenate([bl[j] for j in rng.choice(A.NBLK, A.NBLK // 2, replace=False)]))
            d.append(A.kval(F[idx], L[idx], S[idx], Al, rng, A.NNULL_SUB)[0] - K)
        q = np.percentile(d, [2.5, 5, 95, 97.5])
        out.update(ci=[float(K - q[3]), float(K - q[0])], ci90=[float(K - q[2]), float(K - q[1])],
                   median_d=float(np.median(d)), sd_d=float(np.std(d)))
    return name, out

def job(args):
    kind, s = args
    cfg = {'text.lines_to_create': 2500} if kind == 'def' else c005cfg()
    Lg = G.generate(cfg, s); fl = G.flat(Lg or [])
    if len(fl) < 6000: return (kind, s, None)
    surf = G.stats(fl[:6000]); ws = [D.T.units(w) for w in fl][:D.N]
    if len(ws) < D.N: return (kind, s, None)
    if kind == 'ref': _, r = analyse(f'gen_{s}', ws, boot=False)
    elif kind == 'plant': _, r = analyse(f'plant_{s}', A.decoupled(ws, np.random.default_rng([SEED, s]), PLANT_F))
    else: _, r = analyse(f'{kind}_{s}', ws)
    r['surf'] = surf; return (kind, s, r)

def tost(r, m, se):
    lo, hi = r['ci90'][0] - m - Z * se, r['ci90'][1] - m + Z * se
    if lo >= -DELTA and hi <= DELTA: c = 'EQUIVALENT'
    elif hi < -DELTA: c = 'BELOW BEYOND MARGIN'
    elif lo > DELTA: c = 'ABOVE BEYOND MARGIN'
    else: c = 'INCONCLUSIVE'
    return c, [float(lo), float(hi)], float(r['K'] - m)

def like(st): return all(abs(st[k] - SURF[k]) <= TOL * SURF[k] for k in SURF)

def main(smoke=False):
    t0 = time.time()
    jobs = [('hold', 11999), ('ref', 11999)] if smoke else \
        [('hold', s) for s in HOLD] + [('plant', s) for s in PLANT] + [('def', s) for s in DEFC] + [('ref', s) for s in REF]
    with Pool(7) as pool:
        vj = None if smoke else pool.starmap_async(analyse, [('Voynich_ZL3b', D.seqs_voy('data/ZL3b-n.txt')),
                                                              ('Voynich_IT2a', D.seqs_voy('data/IT2a-n.txt'))])
        R = pool.map(job, jobs, chunksize=1)
        V = {} if smoke else dict(vj.get())
    if smoke:
        print('smoke', [(k, s, r and round(r['K'], 4), r and r.get('ci90')) for k, s, r in R], round(time.time() - t0, 1)); return
    grp = {}
    for k, s, r in R: grp.setdefault(k, {})[s] = r
    ref = {s: r for s, r in grp['ref'].items() if r}
    ga = np.array([r['K'] for r in ref.values()]); m, sd = float(ga.mean()), float(ga.std(ddof=1)); se = sd / np.sqrt(len(ga))
    hold = {s: r for s, r in grp['hold'].items() if r}; plant = {s: r for s, r in grp['plant'].items() if r}
    defc = {s: r for s, r in grp['def'].items() if r}
    rows = {**V, **{f'hold_{s}': r for s, r in hold.items()}, **{f'plant_{s}': r for s, r in plant.items()},
            **{f'def_{s}': r for s, r in defc.items()}}
    g1 = all(r['ci'][0] <= r['K'] <= r['ci'][1] and r['ci90'][0] <= r['K'] <= r['ci90'][1] for r in rows.values())
    calls = {n: tost(r, m, se) for n, r in rows.items()}
    hc = [calls[f'hold_{s}'][0] for s in hold]; pc = [calls[f'plant_{s}'][0] for s in plant]; dc = [calls[f'def_{s}'][0] for s in defc]
    g2e = hc.count('EQUIVALENT'); g2b = sum('BEYOND' in c for c in hc); g2 = g2e >= 8 and g2b <= 2 and len(hold) == 20
    g3a = pc.count('BELOW BEYOND MARGIN') >= 4 and pc.count('EQUIVALENT') == 0 and len(plant) == 5
    g3b = dc.count('EQUIVALENT') <= 1 and len(defc) == 5
    g4 = len(ref) >= 36
    surf = {k: float(np.mean([r['surf'][k] for r in ref.values()])) for k in SURF}; surf_ok = like(surf)
    ver = {v: dict(K=V[v]['K'], ci95=V[v]['ci'], ci90=V[v]['ci90'], d=calls[v][2], ci90_d=calls[v][1], call=calls[v][0],
                   two_sd_inside=abs(V[v]['K'] - m) <= 2 * sd, rank_in_ref=int((ga < V[v]['K']).sum())) for v in V}
    cz, ci_ = ver['Voynich_ZL3b']['call'], ver['Voynich_IT2a']['call']; cs = {cz, ci_}
    if not (g1 and g2 and g3a and g3b and g4): H1 = 'NOT TESTABLE (gate)'
    elif cs == {'EQUIVALENT'}: H1 = 'EQUIVALENT' if surf_ok else 'EQUIVALENT ONLY WITH SURFACE LOSS'
    elif len(cs) == 1 and 'BEYOND' in cz: H1 = 'EXCLUDED (' + cz + ')'
    elif 'EQUIVALENT' in cs and 'INCONCLUSIVE' in cs: H1 = 'NOT CALLED (equivalence for one transcription only)'
    elif 'EQUIVALENT' in cs: H1 = 'TRANSCRIPTION-DEPENDENT (NOT CALLED)'
    else: H1 = 'INCONCLUSIVE'
    gates = dict(G1=g1, G2=f'EQ {g2e}/20, BEYOND {g2b}/20', G2_pass=g2, G3a=pc, G3a_pass=g3a, G3b=dc, G3b_pass=g3b,
                 G4=f'{len(ref)}/40', G4_pass=g4)
    out = dict(seed=SEED, delta=DELTA, ref_mean=m, ref_sd=sd, ref_se=se, ref_range=[float(ga.min()), float(ga.max())],
               ref={str(s): r for s, r in ref.items()}, rows=rows, calls={k: list(v) for k, v in calls.items()},
               surface_ref_mean=surf, H2='FEASIBILITY CONFIRMED' if surf_ok else 'FEASIBILITY LOST', gates=gates,
               verdict=ver, H1=H1, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C085_results.json', 'w'), indent=1)
    print('ref n', len(ref), 'mean', round(m, 4), 'sd', round(sd, 4), 'range', round(ga.min(), 4), round(ga.max(), 4))
    for n, c in calls.items(): print(n, round(rows[n]['K'], 4), c[0], [round(x, 4) for x in c[1]])
    print('gates', gates); print('surface', surf, out['H2'])
    for k, v in ver.items(): print(k, json.dumps(v))
    print('H1', H1); print('runtime', out['runtime_s'])

if __name__ == '__main__':
    main(smoke='smoke' in sys.argv)
