#!/usr/bin/env python3
"""C083 (F-AFFIX step 3): can any configuration in a FIXED grid of the Timm-Schinner generator reach the manuscript's
low first/last-symbol coupling K while keeping the C004/C005 surface statistics?  Single confirmatory test on held-out seeds.
Statistic K and repaired CI exactly as C082 (tools/c082_affix_repaired.py, imported; seed changed to 8383).
Grid (fixed in advance, 2^6 = 64 cells + the full C005 selected configuration = 65 cells):
  sourceChooser {page, random} x combine_split {30, 0} x add_remove {20, 60} x use_word_final_substitutions {true, false}
  x canFollow {curveline, none} x initial_line {default f103v.P.9, f103r line 1}; all other settings default.
  (the C005 core switches sourceChooser=random, combine_split=0, canFollow=none, f103r.1 are a grid cell.)
Training: every cell on seeds 11246-11250 (common seeds), 2,500 lines. Per run: K (no CI) and surface stats on the first
6,000 words (C004 stats: mean word length in units, TTR, h2, rigidity R).  Feasible cell = 5-run mean of each of
mwl, ttr, h2, R within +-15% of the C005 whole-manuscript reference (4.566, 0.354, 2.249, 0.487); all 5 runs usable.
Selection rule: the feasible cell with the LOWEST mean training K (ties -> lower cell index) = the generator's best shot.
Confirmation (single test): the winner on 20 fresh seeds 11251-11270 (reference), 10 held-out unmodified runs 11271-11280
(each with CI; false-positive gate), 5 plant hosts 11281-11285 (25% of endings shuffled within strata; power gate).
Per transcription: C082 rule against the winner's 20 reference runs (BELOW iff K < min and CI upper < min; INSIDE iff in
[min, max]; else NOT CALLED).
H1: both BELOW -> ROBUST DEPARTURE (within this grid).  Both INSIDE and the winner's 20-run mean surface stats still
within +-15% -> REACHED.  Both INSIDE but surface lost -> REACHED ONLY WITH SURFACE LOSS (= not reached under the
constraint).  Otherwise NOT CALLED.  No feasible cell -> NOT TESTABLE (grid cannot keep the surface).
Gates (fail -> NOT TESTABLE): G1 every CI contains its point; G2 <= 2/10 held-out called BELOW/ABOVE; G3 >= 4/5 plants
BELOW; G4 >= 18/20 reference runs usable.
Grid multiplicity (borrowed from Kryptos I-107): the training report quotes the grid-extreme statistic (min over ALL
feasible cells of mean K, and of single-run K), never a hand-picked cell; the only p-like number is the held-out rank.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time, itertools
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c077_direction as D
import c082_affix_repaired as A
import c004_generator_sweep as G
import c005_targeted_search as C5
A.SEED = 8383
SEED = 8383
TRAIN, REF, HOLD, PLANT = range(11246, 11251), range(11251, 11271), range(11271, 11281), range(11281, 11286)
SURF = {'mwl': 4.56641, 'ttr': 0.3535733333333333, 'h2': 2.249330242292793, 'R': 0.4871370421623037}
TOL = 0.15
F103R = C5.LINES['f103r.1']

def grid():
    cells = []
    for sc, cs, ar, wf, cf, il in itertools.product(['page', 'random'], [30, 0], [20, 60], ['true', 'false'],
                                                    ['curveline', 'none'], ['default', 'f103r.1']):
        cells.append({'method.sourceChooser': sc, 'method.morph.combine_split.probability': cs,
                      'method.morph.add_remove.probability': ar, 'method.morph.use_word_final_substitutions': wf,
                      'method.canFollow': cf, 'text.initial_line': il})
    c5 = dict(json.load(open('analysis/C005_confirm.json'))['A']['selected']); cells.append(c5)
    return cells

def tocfg(c):
    c = dict(c); c['text.initial_line'] = C5.LINES[c['text.initial_line']]; c['text.lines_to_create'] = 2500; return c

def like(st): return all(abs(st[k] - SURF[k]) <= TOL * SURF[k] for k in SURF)

def run(args):
    ci, cell, s, mode = args
    Lg = G.generate(tocfg(cell), s); fl = G.flat(Lg or [])
    if len(fl) < 6000: return (ci, s, mode, None)
    surf = G.stats(fl[:6000])
    ws = [D.T.units(w) for w in fl][:D.N]
    if len(ws) < D.N: return (ci, s, mode, dict(surf=surf, K=None))
    if mode == 'train': name, r = A.analyse(f't{ci}_{s}', ws, boot=False)
    elif mode == 'ref': name, r = A.analyse(f'gen_{s}', ws, boot=False)
    elif mode == 'hold': name, r = A.analyse(f'hold_{s}', ws, boot=True)
    else: name, r = A.analyse(f'plant_{s}', A.decoupled(ws, np.random.default_rng([SEED, s]), A.PLANT_F), boot=True)
    r['surf'] = surf; return (ci, s, mode, r)

def main(smoke=False):
    t0 = time.time(); cells = grid(); log = {}
    tr_seeds = [11999] if smoke else list(TRAIN)
    idx = range(len(cells)) if not smoke else range(len(cells) - 2, len(cells))
    jobs = [(i, cells[i], s, 'train') for i in idx for s in tr_seeds]
    with Pool(8) as pool:
        voy = {'Voynich_ZL3b': D.seqs_voy('data/ZL3b-n.txt'), 'Voynich_IT2a': D.seqs_voy('data/IT2a-n.txt')}
        vj = pool.starmap_async(A.analyse, list(voy.items()))
        TR = pool.map(run, jobs, chunksize=1)
        print('training done', round(time.time() - t0, 1), flush=True)
        per = {}
        for ci, s, m, r in TR: per.setdefault(ci, []).append(r)
        summ = []
        for ci, rs in sorted(per.items()):
            ok = all(r and r.get('K') is not None for r in rs) and len(rs) == len(tr_seeds)
            d = dict(cell=ci, cfg=cells[ci], usable=ok)
            if ok:
                d['K_mean'] = float(np.mean([r['K'] for r in rs])); d['K_min'] = float(min(r['K'] for r in rs))
                d['K_runs'] = [r['K'] for r in rs]
                d['surf_mean'] = {k: float(np.mean([r['surf'][k] for r in rs])) for k in SURF}
                d['feasible'] = like(d['surf_mean'])
            else: d['feasible'] = False
            summ.append(d)
        feas = [d for d in summ if d['feasible']]
        json.dump(dict(seed=SEED, cells=summ), open('analysis/C083_train.json', 'w'), indent=1)
        V = dict(vj.get())
        if not feas:
            out = dict(H1='NOT TESTABLE (no feasible cell)', n_feasible=0, voynich=V); print(out)
            if not smoke: json.dump(out, open('analysis/C083_results.json', 'w'), indent=1)
            return
        win = min(feas, key=lambda d: (d['K_mean'], d['cell']))
        extreme = dict(min_feasible_K_mean=win['K_mean'], min_feasible_single_run=min(d['K_min'] for d in feas),
                       n_feasible=len(feas), n_cells=len(summ),
                       n_feasible_cells_with_any_run_below_ZL=sum(d['K_min'] <= V['Voynich_ZL3b']['K'] for d in feas),
                       n_feasible_cells_with_any_run_below_IT2a=sum(d['K_min'] <= V['Voynich_IT2a']['K'] for d in feas))
        print('winner', win['cell'], win['cfg'], round(win['K_mean'], 4), extreme, flush=True)
        if smoke: return
        cj = [(win['cell'], cells[win['cell']], s, m) for m, rr in (('ref', REF), ('hold', HOLD), ('plant', PLANT)) for s in rr]
        CR = pool.map(run, cj, chunksize=1)
    ref = {s: r for ci, s, m, r in CR if m == 'ref' and r and r.get('K') is not None}
    hold = {s: r for ci, s, m, r in CR if m == 'hold' and r and r.get('K') is not None}
    plant = {s: r for ci, s, m, r in CR if m == 'plant' and r and r.get('K') is not None}
    ga = [r['K'] for r in ref.values()]; glo, ghi = min(ga), max(ga)
    rows = {**V, **{f'hold_{s}': r for s, r in hold.items()}, **{f'plant_{s}': r for s, r in plant.items()}}
    g1 = all(r['ci'][0] <= r['K'] <= r['ci'][1] for r in rows.values())
    hc = {s: A.gcall(r['ci'], r['K'], glo, ghi) for s, r in hold.items()}
    g2n = sum(c in ('BELOW GENERATOR', 'ABOVE GENERATOR') for c in hc.values()); g2 = g2n <= 2 and len(hold) == 10
    pc = {s: A.gcall(r['ci'], r['K'], glo, ghi) for s, r in plant.items()}
    g3n = sum(c == 'BELOW GENERATOR' for c in pc.values()); g3 = g3n >= 4 and len(plant) == 5
    g4 = len(ref) >= 18
    surf_ho = {k: float(np.mean([r['surf'][k] for r in ref.values()])) for k in SURF}; surf_ok = like(surf_ho)
    ver = {v: dict(K=V[v]['K'], ci=V[v]['ci'], n_ref_below=sum(g < V[v]['K'] for g in ga),
                   call=A.gcall(V[v]['ci'], V[v]['K'], glo, ghi)) for v in V}
    calls = [ver[v]['call'] for v in V]
    if not (g1 and g2 and g3 and g4): H1 = 'NOT TESTABLE (gate)'
    elif all(c == 'BELOW GENERATOR' for c in calls): H1 = 'ROBUST DEPARTURE (within the grid)'
    elif all(c == 'INSIDE GENERATOR RANGE' for c in calls):
        H1 = 'REACHED' if surf_ok else 'REACHED ONLY WITH SURFACE LOSS'
    else: H1 = 'NOT CALLED (' + ' / '.join(calls) + ')'
    gates = dict(G1=g1, G2=f'{g2n}/{len(hold)}', G2_pass=g2, G3=f'{g3n}/{len(plant)}', G3_pass=g3, G4=f'{len(ref)}/20', G4_pass=g4)
    out = dict(seed=SEED, winner=win, grid_extreme=extreme, reference={str(s): r for s, r in ref.items()},
               reference_range=[glo, ghi], reference_mean=float(np.mean(ga)), reference_sd=float(np.std(ga, ddof=1)),
               holdout={str(s): r for s, r in hold.items()}, plants={str(s): r for s, r in plant.items()},
               holdout_calls={str(k): v for k, v in hc.items()}, plant_calls={str(k): v for k, v in pc.items()},
               heldout_surface_mean=surf_ho, heldout_surface_ok=surf_ok, gates=gates, verdict=ver, H1=H1,
               runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C083_results.json', 'w'), indent=1)
    print('ref range', round(glo, 4), round(ghi, 4), 'mean', round(np.mean(ga), 4))
    print('holdout', hc); print('plants', pc); print('gates', gates); print('surface held-out', surf_ho, surf_ok)
    for k, v in ver.items(): print(k, json.dumps(v))
    print('H1', H1); print('runtime', out['runtime_s'])

if __name__ == '__main__':
    main(smoke='smoke' in sys.argv)
