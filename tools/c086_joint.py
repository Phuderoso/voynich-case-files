#!/usr/bin/env python3
"""C086 (F-TOPIC x F-AFFIX follow-up, JOINT test): within a FIXED grid of Timm-Schinner generator settings, does any cell
keep BOTH the C004/C005 surface statistics (+-15%) AND the manuscript's page-topic gain X (C084) in both windows,
and does that hold on held-out seeds?
Grid (fixed in advance, 2^7 = 128 cells + 2 control cells = 130):
  sourceChooser {page, position} x add_remove {20, 60} x replace {50, 100} x combine_split {30, 0}
  x canFollow {curveline, none} x suggestions {top, none} x lines_per_page {29, 12}; all other settings default
  (initial line f103v.P.9; cell 0 is therefore the all-default configuration, a built-in duplicate of cell 129).
  Cell 128 = C005 selected configuration (known: surface-feasible, topics low; C083/C084).  Cell 129 = all defaults
  (known: topics present, surface-infeasible; C083/C084).  The jar has no 'probability of same-page copying' switch;
  'page' and 'position' are its two topic-capable source choosers ('random' cells were C083's 13 feasible ones and the
  C005 representative lost topics in C084), so the grid spans the knobs that can raise variety under page copying.
Training: every cell on seeds 11391-11393, 3,600 lines.  Surface = C004 stats on the first 6,000 words; cell
surface-feasible iff the 3-run mean of each of mwl, TTR, h2, R is within +-15% of the C005 reference.
Topic X (C084 statistic, PLSA K 8, odd->even lines, line-reassignment null, R_TRAIN = 9) on pseudo-pages cut to the
ZL page-size sequences of W1 (f1r-f79v) and W2 (f86v6-f116r): computed ONLY for surface-feasible cells and the two
control cells (compute budget, disclosed).  Topic band per window = [0.85 x min, 1.15 x max] of the two
transcriptions' multi-init means from the design step (analysis/C086_design.json: 8 PLSA inits each, R 9, non-registered
seeds; the single-init C084 values sat in the upper tail of the init spread, see the C084 audit note):
W1 [0.3911, 0.5372], W2 [0.1841, 0.2542].  Cell jointly feasible iff
surface-feasible and the 3-run mean X inside the band in BOTH windows.
Selection: the jointly feasible cell with the smallest worst relative deviation over the 6 numbers (4 surface stats vs
reference, 2 X means vs the manuscript mean of the window); ties -> lower index.
Confirmation (single test): selected cell on reference seeds 11394-11413 (R 19), held-out runs 11414-11423 (R 19).
Manuscript call per measurement (C084 rule): ABOVE iff X - 2 sd_null > max(ref), BELOW iff X + 2 sd_null < min(ref),
INSIDE iff in [min, max], else NOT CALLED; manuscript X = design multi-init mean, sd = its init-to-init SD.
H1 branches:
  no surface-feasible cell                      -> NOT TESTABLE (grid cannot keep the surface)
  surface-feasible cells but none jointly       -> NOT REACHED IN THIS GRID; two-sided grid extremes reported (I-107/
       I-117): per window the min and max training X over surface-feasible cells (UNDERSHOOT if max < band, OVERSHOOT
       if min > band, BRACKETED otherwise); boundary cells B1 (surface-feasible, smallest topic deviation) and B2
       (topic-feasible in both windows, smallest surface deviation, if any) each re-run on 10 fresh seeds 11424-11443
       to check the infeasibility is not a 3-seed fluke (CONFIRMED / NOT CONFIRMED).
  jointly feasible, confirmation: 20-run means still feasible AND all 4 manuscript calls INSIDE -> REACHED JOINTLY;
       means no longer feasible -> NOT CONFIRMED ON HELD-OUT (training fluke); means feasible but any manuscript call
       ABOVE/BELOW -> NOT REACHED (manuscript outside the cell's run range: ABOVE = overshoot by the manuscript,
       BELOW = cell overshoots); otherwise NOT CALLED.
Gates (fail -> NOT TESTABLE): K1 known answers: cell 128 surface-feasible and below the W1 band, cell 129 surface-
infeasible; K2 positive control: IT2a manuscript text through the same pipeline (surface on its first 6,000 words,
X = mean of 3 PLSA inits on its real W1/W2 pages, R 9, seeds 8686*10+20..25) is jointly feasible (I-119 pass rate
0.94 by resampling the design repeats); F FPR: 5 line-reassigned generator texts (cells 129 x3 / 128 x2 training runs, lines permuted before paging, R 19), p <= 0.05 in <= 1/5 per window; (confirmation only)
G3 <= 2/10 held-out runs called ABOVE/BELOW per window; G4 >= 18/20 reference runs usable.
Multiplicity: one confirmatory test; the training grid is reported by its extremes only (no per-cell p).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time, itertools
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ[_v] = '1'
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c004_generator_sweep as G
import c005_targeted_search as C5
import c003_position_rigidity as c3
import c084_page_topics as T

SEED = 8686
TRAIN, REF, HOLD, BOUND = range(11391, 11394), range(11394, 11414), range(11414, 11424), range(11424, 11444)
SURF = {'mwl': 4.56641, 'ttr': 0.3535733333333333, 'h2': 2.249330242292793, 'R': 0.4871370421623037}
TOL = 0.15
MS = {'W1': {}, 'W2': {}}
R_TRAIN, R_CONF = 9, 19
NLINES = 3600

def load_ms():
    r = json.load(open('analysis/C086_design.json'))['ms_repeats']
    for w in ('W1', 'W2'):
        for t in ('ZL3b', 'IT2a'):
            x = r[f'{t}_{w}']; MS[w][t] = (x['mean'], x['sd'])
    return {w: [0.85 * min(v[0] for v in MS[w].values()), 1.15 * max(v[0] for v in MS[w].values())] for w in MS}

def grid():
    cells = []
    for sc, ar, rp, cs, cf, sg, lp in itertools.product(['page', 'position'], [20, 60], [50, 100], [30, 0],
                                                        ['curveline', 'none'], ['top', 'none'], [29, 12]):
        cells.append({'method.sourceChooser': sc, 'method.morph.add_remove.probability': ar,
                      'method.morph.replace.probability': rp, 'method.morph.combine_split.probability': cs,
                      'method.canFollow': cf, 'method.suggestions': sg, 'text.lines_per_page': lp})
    cells.append(dict(json.load(open('analysis/C005_confirm.json'))['A']['selected']))  # 128
    cells.append({})  # 129 defaults
    return cells

def tocfg(c):
    c = dict(c)
    if 'text.initial_line' in c: c['text.initial_line'] = C5.LINES[c['text.initial_line']]
    c['text.lines_to_create'] = NLINES; return c

def surf_ok(st): return all(abs(st[k] - SURF[k]) <= TOL * SURF[k] for k in SURF)

def gen(args):
    ci, cell, s = args
    L = G.generate(tocfg(cell), s); fl = G.flat(L or [])
    if len(fl) < 6000: return ci, s, None, None
    return ci, s, L, G.stats(fl[:6000])

def xjob(args):
    name, pages, R, seed = args
    return T.test((name, pages, R, seed))

def ms_pages():
    win, pZ, _, _ = T.ms_windows('data/ZL3b-n.txt'); winI, pI, _, _ = T.ms_windows('data/IT2a-n.txt')
    sizes = {w: [sum(map(len, pZ[p])) for p in win[w]] for w in win}
    return sizes, {w: [pI[p] for p in winI[w]] for w in winI}

def xjobs_for(tag, L, sizes, R, base):
    out = []
    for w in ('W1', 'W2'):
        pg = T.cut(L, sizes[w])
        if pg is None: return None
        out.append((f'{tag}_{w}', pg, R, base + (0 if w == 'W1' else 1)))
    return out

def summarise(cells, gens, X, band, seeds):
    S = []
    for ci in range(len(cells)):
        rs = [gens.get((ci, s)) for s in seeds]
        d = dict(cell=ci, cfg=cells[ci], usable=all(r is not None for r in rs))
        if d['usable']:
            d['surf_mean'] = {k: float(np.mean([r[k] for r in rs])) for k in SURF}
            d['surf_runs'] = rs; d['surface_feasible'] = surf_ok(d['surf_mean'])
            d['surf_dev'] = max(abs(d['surf_mean'][k] / SURF[k] - 1) for k in SURF)
        else: d['surface_feasible'] = False
        xs = {w: [X.get(f'c{ci}_s{s}_{w}') for s in seeds] for w in ('W1', 'W2')}
        if all(v is not None for w in xs for v in xs[w]):
            d['X_runs'] = xs; d['X_mean'] = {w: float(np.mean(xs[w])) for w in xs}
            d['topic_feasible'] = all(band[w][0] <= d['X_mean'][w] <= band[w][1] for w in xs)
            msm = {w: float(np.mean([v[0] for v in MS[w].values()])) for w in MS}
            d['topic_dev'] = max(abs(d['X_mean'][w] / msm[w] - 1) for w in xs)
        d['joint'] = bool(d['surface_feasible'] and d.get('topic_feasible'))
        S.append(d)
    return S

def call(x, sd, lo, hi):
    if x - 2 * sd > hi: return 'ABOVE'
    if x + 2 * sd < lo: return 'BELOW'
    if lo <= x <= hi: return 'INSIDE'
    return 'NOT CALLED'

def main(smoke=False):
    t0 = time.time(); band = load_ms(); cells = grid(); sizes, pIT = ms_pages()
    out = dict(seed=SEED, band=band, ms=MS, n_cells=len(cells), R_train=R_TRAIN, R_conf=R_CONF)
    seeds = [11999] if smoke else list(TRAIN)
    idx = [0, 1, 64, 65, 128, 129] if smoke else range(len(cells))
    with Pool(8) as pool:
        # positive control K2 (IT2a manuscript) runs alongside generation
        it_words = G.flat(c3.voynich('data/IT2a-n.txt'))[:6000]
        k2_surf = G.stats(it_words)
        k2j = pool.map_async(xjob, [(f'K2_IT2a_{w}_{j}', pIT[w], R_TRAIN, SEED * 10 + 20 + 3 * i + j) for i, w in enumerate(('W1', 'W2')) for j in range(3)])
        GR = pool.map(gen, [(ci, cells[ci], s) for ci in idx for s in seeds], chunksize=1)
        print('generation done', round(time.time() - t0, 1), flush=True)
        gens = {(ci, s): st for ci, s, L, st in GR}; texts = {(ci, s): L for ci, s, L, st in GR}
        pre = summarise(cells, gens, {}, band, seeds)
        todo = [d['cell'] for d in pre if d['cell'] in idx and (d['surface_feasible'] or d['cell'] in (128, 129))]
        jobs, k = [], 0
        for ci in todo:
            for s in seeds:
                js = xjobs_for(f'c{ci}_s{s}', texts[(ci, s)], sizes, R_TRAIN, SEED * 100 + 2 * k); k += 1
                if js: jobs += js
        fp_src = [(129, s) for s in seeds] + [(128, s) for s in seeds][:2] if not smoke else [(129, 11999)]
        for i, key in enumerate(fp_src):
            L = texts.get(key)
            if not L: continue
            L = [L[j] for j in np.random.default_rng([SEED, 5, i]).permutation(len(L))]
            js = xjobs_for(f'FP{i}', L, sizes, R_CONF, SEED * 1000 + 2 * i)
            if js: jobs += js
        print('topic jobs', len(jobs), 'cells', todo, flush=True)
        XR = dict(pool.map(xjob, jobs, chunksize=1))
        K2 = dict(k2j.get())
        print('topics done', round(time.time() - t0, 1), flush=True)
        X = {n: r['X'] for n, r in XR.items()}
        S = summarise(cells, gens, X, band, seeds)
        S = [d for d in S if d['cell'] in idx]
        k1 = {'c128_C005_surface_feasible': S[-2]['surface_feasible'], 'c128_W1_below_band': S[-2].get('X_mean', {}).get('W1', 9) < band['W1'][0],
              'c129_default_surface_infeasible': not S[-1]['surface_feasible']}
        k2x = {w: float(np.mean([K2[f'K2_IT2a_{w}_{j}']['X'] for j in range(3)])) for w in ('W1', 'W2')}
        k2 = dict(surface=k2_surf, surface_feasible=surf_ok(k2_surf), X=k2x,
                  topic_feasible=all(band[w][0] <= k2x[w] <= band[w][1] for w in k2x))
        fp = {w: [XR[n]['p'] for n in XR if n.startswith('FP') and n.endswith(w)] for w in ('W1', 'W2')}
        gF = all(sum(p <= 0.05 for p in fp[w]) <= 1 and len(fp[w]) == 5 for w in fp)
        gK1 = all(k1.values()); gK2 = k2['surface_feasible'] and k2['topic_feasible']
        out.update(train=S, train_X_raw=XR, K1=k1, K2=k2, K2_raw=K2, FP=fp,
                   gates=dict(K1=gK1, K2=gK2, F=gF), train_runtime_s=round(time.time() - t0, 1))
        grid_cells = [d for d in S if d['cell'] < 128]
        sf = [d for d in grid_cells if d['surface_feasible']]
        jt = [d for d in grid_cells if d['joint']]
        out['n_surface_feasible'] = len(sf); out['n_joint'] = len(jt)
        ext = {}
        for w in ('W1', 'W2'):
            xs = [d['X_mean'][w] for d in sf if 'X_mean' in d]
            if xs:
                lo, hi = min(xs), max(xs)
                ext[w] = dict(min=lo, max=hi, band=band[w],
                              side='UNDERSHOOT' if hi < band[w][0] else 'OVERSHOOT' if lo > band[w][1] else 'BRACKETED',
                              single_run_max=max(v for d in sf for v in d['X_runs'][w]))
        out['grid_extremes'] = ext
        for d in S:
            print(d['cell'], d['cfg'] if d['cell'] < 128 else ('C005' if d['cell'] == 128 else 'default'),
                  {k: round(v, 3) for k, v in d.get('surf_mean', {}).items()}, d['surface_feasible'],
                  {k: round(v, 3) for k, v in d.get('X_mean', {}).items()}, d['joint'], flush=True)
        print('K1', k1, 'K2', k2, 'FP', fp, flush=True); print('extremes', ext, flush=True)
        if smoke:
            print('smoke runtime', round(time.time() - t0, 1)); return
        json.dump(out, open('analysis/C086_train.json', 'w'), indent=1)
        if not (gK1 and gK2 and gF):
            out['H1'] = 'NOT TESTABLE (gate)'
        elif not sf:
            out['H1'] = 'NOT TESTABLE (no surface-feasible cell in the grid)'
        elif not jt:
            out['H1'] = 'NOT REACHED IN THIS GRID'
            b1 = min([d for d in sf if 'topic_dev' in d], key=lambda d: (d['topic_dev'], d['cell']))
            tf = [d for d in grid_cells if d.get('topic_feasible')]
            b2 = min(tf, key=lambda d: (d['surf_dev'], d['cell'])) if tf else None
            bjobs = [(b1['cell'], cells[b1['cell']], s) for s in BOUND[:10]]
            if b2: bjobs += [(b2['cell'], cells[b2['cell']], s) for s in BOUND[10:]]
            BG = pool.map(gen, bjobs, chunksize=1)
            xj = []
            for i, (ci, s, L, st) in enumerate(BG):
                js = xjobs_for(f'B_c{ci}_s{s}', L or [], sizes, R_TRAIN, SEED * 10000 + 2 * i)
                if js: xj += js
            BX = dict(pool.map(xjob, xj, chunksize=1))
            bd = {}
            for tag, b, sl in (('B1', b1, BOUND[:10]), ('B2', b2, BOUND[10:])):
                if b is None: bd[tag] = None; continue
                st = [st for ci, s, L, st in BG if ci == b['cell'] and s in sl and st]
                sm = {k: float(np.mean([r[k] for r in st])) for k in SURF}
                xm = {w: float(np.mean([BX[n]['X'] for n in BX if n.startswith(f"B_c{b['cell']}_") and n.endswith(w)
                                        and int(n.split('_s')[1].split('_')[0]) in sl])) for w in ('W1', 'W2')}
                jf = surf_ok(sm) and all(band[w][0] <= xm[w] <= band[w][1] for w in xm)
                bd[tag] = dict(cell=b['cell'], n_runs=len(st), surf_mean=sm, X_mean=xm, surface_feasible=surf_ok(sm),
                               topic_feasible=all(band[w][0] <= xm[w] <= band[w][1] for w in xm),
                               infeasibility=('CONFIRMED' if not jf else 'NOT CONFIRMED'))
            out['boundary'] = bd; out['boundary_raw'] = BX
        else:
            msm = {w: float(np.mean([v[0] for v in MS[w].values()])) for w in MS}
            win = min(jt, key=lambda d: (max(d['surf_dev'], d['topic_dev']), d['cell']))
            out['selected'] = win['cell']
            CG = pool.map(gen, [(win['cell'], cells[win['cell']], s) for s in list(REF) + list(HOLD)], chunksize=1)
            xj = []
            for i, (ci, s, L, st) in enumerate(CG):
                js = xjobs_for(f"{'ref' if s in REF else 'hold'}_s{s}", L or [], sizes, R_CONF, SEED * 20000 + 2 * i)
                if js: xj += js
            CX = dict(pool.map(xjob, xj, chunksize=1))
            refst = [st for ci, s, L, st in CG if s in REF and st]
            sm = {k: float(np.mean([r[k] for r in refst])) for k in SURF}
            H = {}
            for w in ('W1', 'W2'):
                ref = [CX[n]['X'] for n in CX if n.startswith('ref') and n.endswith(w)]
                hold = {n: call(CX[n]['X'], CX[n]['null_sd'], min(ref), max(ref)) for n in CX if n.startswith('hold') and n.endswith(w)}
                H[w] = dict(ref=ref, ref_range=[min(ref), max(ref)], ref_mean=float(np.mean(ref)), n_ref=len(ref),
                            hold_calls=hold, hold_out=sum(c in ('ABOVE', 'BELOW') for c in hold.values()),
                            ms_calls={t: call(MS[w][t][0], MS[w][t][1], min(ref), max(ref)) for t in MS[w]})
            g3 = all(H[w]['hold_out'] <= 2 and len(H[w]['hold_calls']) == 10 for w in H)
            g4 = all(H[w]['n_ref'] >= 18 for w in H) and len(refst) >= 18
            feas = surf_ok(sm) and all(band[w][0] <= H[w]['ref_mean'] <= band[w][1] for w in H)
            calls = [H[w]['ms_calls'][t] for w in H for t in H[w]['ms_calls']]
            if not (g3 and g4): H1 = 'NOT TESTABLE (gate)'
            elif not feas: H1 = 'NOT CONFIRMED ON HELD-OUT'
            elif all(c == 'INSIDE' for c in calls): H1 = 'REACHED JOINTLY'
            elif any(c in ('ABOVE', 'BELOW') for c in calls): H1 = 'NOT REACHED (' + '/'.join(calls) + ')'
            else: H1 = 'NOT CALLED (' + '/'.join(calls) + ')'
            out.update(H1=H1, confirm=H, confirm_surface=sm, confirm_feasible=feas, confirm_raw=CX,
                       gates={**out['gates'], 'G3': g3, 'G4': g4})
    out['runtime_s'] = round(time.time() - t0, 1)
    json.dump(out, open('analysis/C086_results.json', 'w'), indent=1, default=str)
    print('H1', out['H1']); print('gates', out['gates'])
    if 'boundary' in out: print('boundary', json.dumps(out['boundary']))
    if 'confirm' in out: print('confirm', {w: (out['confirm'][w]['ref_range'], out['confirm'][w]['ms_calls'], out['confirm'][w]['hold_out']) for w in out['confirm']}, out['confirm_surface'])
    print('runtime', out['runtime_s'])

if __name__ == '__main__':
    main(smoke='smoke' in sys.argv)
