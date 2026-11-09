#!/usr/bin/env python3
"""C097 (F-NET step 4): can ANY configuration in C083's FIXED grid of the Timm-Schinner generator reach the manuscript's
frequency-neighbour link RHO at K 4,000 types (ZL 0.642 / IT 0.635; default generator ~0.588, C095) while keeping the
C004/C005 surface statistics?  Instrument = C093 verbatim (tools/c093_edit_graph.py, K 4,000), manuscript stream = C094's
stream() (paragraph loci, whole text), exactly as C095 W4.
GRID (fixed in advance, = C083): 2^6 = 64 cells sourceChooser {page, random} x combine_split {30, 0} x add_remove {20, 60}
  x use_word_final_substitutions {true, false} x canFollow {curveline, none} x initial_line {default, f103r.1}
  + the full C005 selected configuration = 65 cells; all other settings default; 8,000 lines per run.
TRAINING: every cell on seeds 11534-11538 (5 common seeds). Feasible cell = 5-run mean of mwl, ttr, h2, R (first 6,000
  words, C004 stats) within +-15% of the C005 whole-manuscript reference AND all 5 runs reach K 4,000 types.
SELECTION: the feasible cell with the HIGHEST mean training RHO (ties -> lower index) = the generator's best shot.
  Grid-extreme reported (Kryptos I-107): max over ALL feasible cells of mean RHO and of single-run RHO, and over all cells.
CONFIRMATION (C095 standard): the winner on two blind batches N1 = 11539-11558, N2 = 11559-11578 (20 runs each);
  next free generator seed 11579. Plant F 0.20 (fixed in C095 by the effect of interest), plant seed 9797.
  Gates per batch (C093): G0 reach >= 19/20; G1 leave-one-out false calls <= 1/20; G2 planted power >= 19/20; DOA 0.054 > MDE80.
  Must pass on BOTH batches, else NOT RUN, LOW-POWER (NOT TESTABLE).
TEST (if runnable): ZL3b and IT2a RHO vs N1 (Holm over 2) and vs N2 (own Holm). HIGHER iff Holm < 0.05 for both
  transcriptions in BOTH batches, same direction; Holm < 0.05 in one batch only -> NOT REPLICATED (no call); otherwise
  NOT DIFFERENT at this power.
READING (registered): HIGHER -> the C093/C095 departure HOLDS against the grid's best shot (within this grid only);
  NOT DIFFERENT -> REACHED within the grid (the gap is within generator settings; C093 H3 becomes 'default-generator only');
  no feasible cell -> NOT TESTABLE (grid cannot keep the surface).
Run: OMP_NUM_THREADS=1 timeout 600 python3 tools/c097_edit_graph_grid.py run analysis/C097_results.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c093_edit_graph as E
import c003_position_rigidity as T
import c083_generator_grid as GG
import c004_generator_sweep as G
from c094_edit_graph_step2 import stream

SEED, LINES, F, K = 9797, 8000, 0.20, 4000
TRAIN = list(range(11534, 11539)); N1 = list(range(11539, 11559)); N2 = list(range(11559, 11579))
E.SEED = SEED

def cfg(c):
    c = dict(c); c['text.initial_line'] = GG.C5.LINES[c['text.initial_line']]; c['text.lines_to_create'] = LINES; return c

def job(args):
    ci, cell, s, plant = args
    Lg = G.generate(cfg(cell), s) or []; fl = G.flat(Lg)
    surf = G.stats(fl[:6000]) if len(fl) >= 6000 else None
    ws = [tuple(T.units(w)) for w in fl]
    r = dict(ci=ci, seed=s, ntokens=len(ws), surf=surf, ref=E.measure(ws, K) if ws else None)
    if plant and ws: r['plant'] = E.measure(E.plant(ws, np.random.default_rng([SEED, s]), F), K)
    return r

def main(mode, outp):
    t0 = time.time(); cells = GG.grid()
    with Pool(8) as pool:
        TR = pool.map(job, [(i, c, s, False) for i, c in enumerate(cells) for s in TRAIN], chunksize=1)
        print('training done', round(time.time() - t0, 1), flush=True)
        summ = []
        for i, c in enumerate(cells):
            rs = [r for r in TR if r['ci'] == i]
            ok = [r for r in rs if r['ref'] and r['surf']]
            rho = [r['ref']['RHO'] for r in ok]
            ms = {k: float(np.mean([r['surf'][k] for r in ok])) for k in GG.SURF} if ok else None
            feas = len(ok) == len(TRAIN) and ms is not None and GG.like(ms)
            summ.append(dict(ci=i, cell=c, n_ok=len(ok), mean_RHO=float(np.mean(rho)) if rho else None,
                             max_RHO=float(max(rho)) if rho else None, surf=ms, feasible=bool(feas)))
        json.dump(dict(training=summ), open(outp + '.train.json', 'w'), indent=1, default=str)
        fe = [s for s in summ if s['feasible']]
        allr = [s for s in summ if s['mean_RHO'] is not None]
        extreme = dict(n_feasible=len(fe),
                       feasible_max_mean=max((s['mean_RHO'] for s in fe), default=None),
                       feasible_max_single=max((s['max_RHO'] for s in fe), default=None),
                       all_max_mean=max((s['mean_RHO'] for s in allr), default=None),
                       all_max_single=max((s['max_RHO'] for s in allr), default=None),
                       default_like_cells=None)
        out = dict(seed=SEED, mode=mode, training=summ, extreme=extreme)
        if not fe:
            out['verdict'] = 'NOT TESTABLE (no feasible cell)'
        else:
            win = sorted(fe, key=lambda s: (-s['mean_RHO'], s['ci']))[0]; out['winner'] = win
            print('winner', win['ci'], win['cell'], round(win['mean_RHO'], 4), flush=True)
            R = pool.map(job, [(win['ci'], win['cell'], s, True) for s in N1 + N2], chunksize=1)
        print('confirmation done', round(time.time() - t0, 1), flush=True)
    if fe:
        Rd = {f'gen_{r["seed"]}': dict(ref=r['ref'], plant=r.get('plant')) for r in R}
        Rd = {m: v for m, v in Rd.items() if v['ref'] and v['plant']}
        b1 = [f'gen_{s}' for s in N1 if f'gen_{s}' in Rd]; b2 = [f'gen_{s}' for s in N2 if f'gen_{s}' in Rd]
        gates = {'N1': E.gate(Rd, b1, 'RHO'), 'N2': E.gate(Rd, b2, 'RHO')}
        for g in gates.values():   # G0 reach counted on the planned 20 runs
            pass
        reach = {'N1': len(b1), 'N2': len(b2)}
        runnable = all(gates[b]['ok'] for b in gates) and min(reach.values()) >= 19
        surfN = {k: float(np.mean([r['surf'][k] for r in R if r['surf']])) for k in GG.SURF}
        out.update(gates=gates, reach=reach, runnable=bool(runnable), winner_surface_confirm=surfN,
                   winner_surface_like=bool(GG.like(surfN)),
                   batch=dict(mean_N1=float(np.mean([Rd[m]['ref']['RHO'] for m in b1])), sd_N1=float(np.std([Rd[m]['ref']['RHO'] for m in b1], ddof=1)),
                              mean_N2=float(np.mean([Rd[m]['ref']['RHO'] for m in b2])), sd_N2=float(np.std([Rd[m]['ref']['RHO'] for m in b2], ddof=1)),
                              max_all=float(max(Rd[m]['ref']['RHO'] for m in b1 + b2))))
        if mode == 'run' and runnable:
            V = {tn: E.measure(stream(p, None), K)['RHO'] for tn, p in E.VPATH.items()}
            fam = {}
            for b, names in (('N1', b1), ('N2', b2)):
                ref = [Rd[m]['ref']['RHO'] for m in names]
                ts = [dict(t=tn, x=x, p=E.pt(x, ref), gap=float(x - np.mean(ref)), gap_over_MDE=float((x - np.mean(ref)) / gates[b]['MDE80']),
                           above_all=bool(x > max(ref))) for tn, x in V.items()]
                for t, a in zip(ts, E.holm([t['p'] for t in ts])): t['p_holm'] = a
                fam[b] = ts
            rej = {b: all(t['p_holm'] < 0.05 for t in fam[b]) for b in fam}
            dirs = {np.sign(t['gap']) for b in fam for t in fam[b]}
            if all(rej.values()) and len(dirs) == 1: v = 'HIGHER' if dirs.pop() > 0 else 'LOWER'
            elif any(rej.values()): v = 'NOT REPLICATED (no call)'
            else: v = 'NOT DIFFERENT at this power'
            out.update(voynich=V, tests=fam, verdict=v,
                       reading={'HIGHER': 'departure HOLDS against the grid best shot (within this grid)',
                                'NOT DIFFERENT at this power': 'REACHED within the grid'}.get(v, 'no call'))
        elif mode == 'run':
            out['verdict'] = 'NOT RUN, LOW-POWER (NOT TESTABLE)'
    out['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(out, open(outp, 'w'), indent=1, default=str)
    for k in ('extreme', 'winner', 'gates', 'reach', 'batch', 'winner_surface_confirm', 'winner_surface_like', 'runnable', 'voynich', 'tests', 'verdict', 'reading', 'elapsed_s'):
        if k in out: print(k, json.dumps(out[k], default=str))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
