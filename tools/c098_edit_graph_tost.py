#!/usr/bin/env python3
"""C098 (F-NET step 5): EQUIVALENCE test (TOST). Is the manuscript's frequency-neighbour link RHO at K 4,000
(ZL3b / IT2a, C093 instrument verbatim, C094 stream) EQUIVALENT to what C097's winning surface-keeping generator
setting produces?  C097 could only test DIFFERENCE and its one-direction plant gate failed; equivalence needs its own,
direction-free calibration (lesson from C097: the copy-plant LOWERS RHO on this host).
HOST (fixed by C097, not re-selected): C083 grid cell 37 = sourceChooser random, combine_split 30, add_remove 20,
  use_word_final_substitutions false, canFollow curveline, initial_line f103r.1; 8,000 lines per run.
BATCHES (fresh, blind): N3 = seeds 11579-11598, N4 = 11599-11618 (20 runs each); next free generator seed 11619.
TEST: prediction-type TOST for one new text vs a batch of n runs: d = x - mean, SE = sd*sqrt(1+1/n), df n-1;
  p_TOST = max(P(T >= (d+delta)/SE), P(T <= (d-delta)/SE)).  Holm over the 2 transcriptions, per batch, per margin.
MARGINS (fixed in advance): delta1 = 0.054 (the manuscript's lead over the DEFAULT generator, C095; 'as close to cell 37 as
  the default is far'); delta2 = 0.027 (half of it, the stricter claim).
GATES per batch and margin, computed on generator runs only, BEFORE the manuscript is measured:
  G0 reach >= 19/20.
  GE1 false equivalence at the boundary: each held-out run h shifted by +delta and by -delta, TOST vs the other runs;
      equivalence calls must be <= 3/40 (nominal 5%).
  GE2 equivalence power: each unshifted held-out run vs the other runs; equivalence calls >= 19/20.
  A margin passes only if all gates pass in BOTH batches, else that margin is NOT TESTABLE.
VERDICT per runnable margin: EQUIVALENT iff Holm p_TOST < 0.05 for both transcriptions in both batches;
  in one batch only -> NOT REPLICATED (no call); otherwise NOT SHOWN EQUIVALENT (inconclusive; NOT 'different').
DESCRIPTIVE (no verdict): two-sided difference p (C093 pt), manuscript rank within each batch, copy-plant F 0.20 mean
  shift and |shift| on this host (seed 9898), and the share of C095's 40 default-generator runs that the delta1 TOST
  would call equivalent to cell 37 (a known-different real-text check; reported, not gated).
READING (registered): EQUIVALENT at delta1 -> the C093/C095 RHO departure is reachable by a surface-keeping setting of the
  generator, so RHO no longer separates the manuscript from the Timm-Schinner hypothesis (F-NET H3 closed as a
  discriminator); at delta2 as well -> a strong match.  Not shown -> the question stays open at this power.
Run: OMP_NUM_THREADS=1 timeout 600 python tools/c098_edit_graph_tost.py run analysis/C098_results.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time, math
from multiprocessing import Pool
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.dirname(__file__))
import c093_edit_graph as E
import c003_position_rigidity as T
import c083_generator_grid as GG
import c004_generator_sweep as G
from c094_edit_graph_step2 import stream

SEED, LINES, F, K, ALPHA = 9898, 8000, 0.20, 4000, 0.05
N3 = list(range(11579, 11599)); N4 = list(range(11599, 11619))
DELTAS = {'delta1': 0.054, 'delta2': 0.027}
CELL = {'method.sourceChooser': 'random', 'method.morph.combine_split.probability': 30,
        'method.morph.add_remove.probability': 20, 'method.morph.use_word_final_substitutions': 'false',
        'method.canFollow': 'curveline', 'text.initial_line': 'f103r.1'}
C095 = os.path.join(os.path.dirname(__file__), '..', 'analysis', 'C095_results.json')
E.SEED = SEED

def cfg(c):
    c = dict(c); c['text.initial_line'] = GG.C5.LINES[c['text.initial_line']]; c['text.lines_to_create'] = LINES; return c

def job(s):
    fl = G.flat(G.generate(cfg(CELL), s) or [])
    surf = G.stats(fl[:6000]) if len(fl) >= 6000 else None
    ws = [tuple(T.units(w)) for w in fl]
    r = dict(seed=s, ntokens=len(ws), surf=surf, ref=E.measure(ws, K) if ws else None)
    if ws: r['plant'] = E.measure(E.plant(ws, np.random.default_rng([SEED, s]), F), K)
    return r

def tost(x, ref, delta):
    ref = np.asarray(ref, float); n = len(ref); se = ref.std(ddof=1) * math.sqrt(1 + 1 / n); d = x - ref.mean()
    return float(max(stats.t.sf((d + delta) / se, n - 1), stats.t.cdf((d - delta) / se, n - 1)))

def gates(x, delta):
    names = list(x)
    if len(names) < 19: return dict(reached=len(names), ok=False, why='G0')
    fe = sum(tost(x[h] + sg * delta, [x[o] for o in names if o != h], delta) < ALPHA for h in names for sg in (1, -1))
    pw = sum(tost(x[h], [x[o] for o in names if o != h], delta) < ALPHA for h in names)
    why = 'GE1' if fe > 3 else 'GE2' if pw < 19 else ''
    return dict(reached=f'{len(names)}/20', false_equiv=f'{fe}/{2 * len(names)}', equiv_power=f'{pw}/{len(names)}', ok=why == '', why=why)

def main(mode, outp):
    t0 = time.time()
    with Pool(8) as pool: R = pool.map(job, N3 + N4, chunksize=1)
    print('generation done', round(time.time() - t0, 1), flush=True)
    ok = {r['seed']: r for r in R if r['ref'] and r['surf']}
    B = {'N3': {s: ok[s]['ref']['RHO'] for s in N3 if s in ok}, 'N4': {s: ok[s]['ref']['RHO'] for s in N4 if s in ok}}
    surf = {k: float(np.mean([r['surf'][k] for r in ok.values()])) for k in GG.SURF}
    batch = {b: dict(n=len(v), mean=float(np.mean(list(v.values()))), sd=float(np.std(list(v.values()), ddof=1)),
                     lo=float(min(v.values())), hi=float(max(v.values()))) for b, v in B.items()}
    pl = [ok[s]['plant']['RHO'] - ok[s]['ref']['RHO'] for s in ok if ok[s].get('plant')]
    G_ = {m: {b: gates(B[b], d) for b in B} for m, d in DELTAS.items()}
    runnable = {m: all(g['ok'] for g in G_[m].values()) for m in G_}
    d95 = json.load(open(C095)); dflt = [v['ref']['4000']['RHO'] for v in d95['refs'].values() if v.get('ref') and v['ref'].get('4000')]
    allx = list(B['N3'].values()) + list(B['N4'].values())
    dflt_eq = sum(tost(x, allx, DELTAS['delta1']) < ALPHA for x in dflt)
    out = dict(seed=SEED, mode=mode, cell=CELL, batch=batch, surface=surf, surface_like=bool(GG.like(surf)),
               plant=dict(F=F, mean_shift=float(np.mean(pl)), mean_abs_shift=float(np.mean(np.abs(pl))), n=len(pl)),
               gates=G_, runnable=runnable, default_runs_called_equiv_delta1=f'{dflt_eq}/{len(dflt)}',
               default_mean=float(np.mean(dflt)), runs={str(s): dict(ref=ok[s]['ref']['RHO'], plant=ok[s]['plant']['RHO']) for s in ok})
    if mode == 'run':
        V = {tn: E.measure(stream(p, None), K)['RHO'] for tn, p in E.VPATH.items()}
        desc = {b: {tn: dict(x=x, gap=float(x - batch[b]['mean']), p_diff=E.pt(x, list(B[b].values())),
                             rank=int(sum(v < x for v in B[b].values()))) for tn, x in V.items()} for b in B}
        tests, verdict = {}, {}
        for m, d in DELTAS.items():
            if not runnable[m]: verdict[m] = 'NOT TESTABLE (gate ' + ','.join(f"{b}:{g['why']}" for b, g in G_[m].items() if not g['ok']) + ')'; continue
            tests[m] = {}
            for b in B:
                ts = [dict(t=tn, p_tost=tost(x, list(B[b].values()), d)) for tn, x in V.items()]
                for t, a in zip(ts, E.holm([t['p_tost'] for t in ts])): t['p_holm'] = a
                tests[m][b] = ts
            rej = [all(t['p_holm'] < ALPHA for t in tests[m][b]) for b in B]
            verdict[m] = 'EQUIVALENT' if all(rej) else 'NOT REPLICATED (no call)' if any(rej) else 'NOT SHOWN EQUIVALENT (inconclusive)'
        out.update(voynich=V, descriptive=desc, tests=tests, verdict=verdict)
    out['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(out, open(outp, 'w'), indent=1, default=str)
    for k in ('batch', 'surface', 'surface_like', 'plant', 'gates', 'runnable', 'default_runs_called_equiv_delta1', 'default_mean',
              'voynich', 'descriptive', 'tests', 'verdict', 'elapsed_s'):
        if k in out: print(k, json.dumps(out[k], default=str))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
