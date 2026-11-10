#!/usr/bin/env python3
"""C103 (F-RHYTHM step 2): (H1) can any configuration in the FIXED C083 65-cell Timm-Schinner grid reproduce the
manuscript's adjacent interior word-length persistence D (C102: Currier B +0.076 IT2a / +0.084 ZL3b) while keeping the
C004/C005 surface statistics?  (H2) does C102's persistence survive dropping word 2 as well (position control)?
Statistic D exactly as C102 (tools/c102_word_length_rhythm.py, imported): interior words, EVA glyph units, pooled Pearson
r of adjacent lengths minus the mean of a within-line permutation null.
H1 grid = C083 grid (2^6 = 64 cells + C005 selected = 65), 2,500 lines, lines >= 5 words. Training: every cell on seeds
11651-11655, D with R = 200 null draws; surface (mwl, ttr, h2, R on first 6,000 words) within +-15% of the C005 reference
= feasible (C083 rule, all 5 runs usable). Winner = feasible cell with the HIGHEST mean training D (ties -> lower index).
Grid-extreme reported: max over feasible cells of mean D and of single-run D (and over ALL cells, descriptive).
Confirmation: winner on 20 fresh seeds 11656-11675 (reference, R = 500), 10 held-out runs 11676-11685 (FPR gate),
5 plant hosts 11686-11690 (C102 POS plant at q = 0.10 on the host's lines; power gate).
Call per transcription: ABOVE iff manuscript D > max(ref); INSIDE iff in [min, max]; BELOW iff < min.
H1: both ABOVE -> ROBUST DEPARTURE (within this grid); both INSIDE with held-out surface still feasible -> REACHED;
   both INSIDE with surface lost -> REACHED ONLY WITH SURFACE LOSS; otherwise NOT CALLED. No feasible cell -> NOT TESTABLE.
Gates (fail -> NOT TESTABLE): G1 <= 2/10 held-out outside [min,max]; G2 >= 4/5 plants ABOVE; G3 >= 18/20 ref usable.
H2: interior = positions 3..n-1 (words 1, 2 and last dropped), lines >= 6 words; within-line permutation null, R = 2,000,
   seed 11691; Holm over {A,B} x {IT2a, ZL3b}; C102 decision rule. Gates (seed 11692, 20 replicates, RG = 300, q = 0.20
   fixed from C102's design): FPR <= 2/20, NEG and POS power >= 16/20, broken-meter check (mean D NEG < 0 < POS).
Audit C102: recompute H1 (seed 11624, R 2,000) - D must equal the published JSON values to 1e-12.
Run: timeout 600 python tools/c103_rhythm_grid.py analysis/C103_results.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c102_word_length_rhythm as W
import c083_generator_grid as C83
import c004_generator_sweep as G
from c070_word2_sh import parse, FILES
from c003_position_rigidity import units

TRAIN, REF, HOLD, PLANT = range(11651, 11656), range(11656, 11676), range(11676, 11686), range(11686, 11691)
H2SEED, H2GATE, QP, QH2 = 11691, 11692, 0.10, 0.20
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

def run(args):
    ci, cell, s, mode = args
    Lg = G.generate(C83.tocfg(cell), s)
    if not Lg: return (ci, s, mode, None)
    fl = G.flat(Lg)
    if len(fl) < 6000: return (ci, s, mode, None)
    surf = G.stats(fl[:6000])
    L5 = [l for l in Lg if len(l) >= 5]
    rng = np.random.default_rng([s, ci, {'train': 0, 'ref': 1, 'hold': 2, 'plant': 3}[mode]])
    Lo = W.Lines(W.lens_interior(L5))
    if mode == 'plant': Lo = W.Lines(W.plant(Lo.L, rng, QP, 'POS'))
    t = W.test(Lo, rng, 200 if mode == 'train' else 500)
    return (ci, s, mode, dict(D=t['D'], r=t['r'], surf=surf, lines=len(L5)))

def h2_lines(P, k, L): return W.Lines([[len(units(w)) for w in l['words'][2:-1]] for l in P[k] if l['L'] == L and len(l['words']) >= 6])

def main(smoke=False):
    outp = sys.argv[1] if len(sys.argv) > 1 and not smoke else '/tmp/C103_smoke.json'
    res = dict(cycle='C103', seeds=dict(train=[11651, 11655], ref=[11656, 11675], hold=[11676, 11685], plant=[11686, 11690],
                                        h2=H2SEED, h2_gates=H2GATE), next_free_seed=11693)
    P = {k: parse(f) for k, f in FILES}
    # audit C102
    sub = {f'{k}|{L}': W.Lines(W.lens_interior([l['words'] for l in P[k] if l['L'] == L])) for k, _ in FILES for L in 'AB'}
    pub = json.load(open('analysis/C102_results.json'))['H1']
    rng = np.random.default_rng(11624); A = {s: W.test(Lo, rng, 2000 if not smoke else 50) for s, Lo in sub.items()}
    res['audit_C102'] = dict(values={s: A[s]['D'] for s in A}, exact=all(abs(A[s]['D'] - pub[s]['D']) < 1e-12 for s in A))
    log('audit', res['audit_C102']); MD = {k: A[f'{k}|B']['D'] for k, _ in FILES}
    # H1 grid
    cells = C83.grid(); idx = range(len(cells)) if not smoke else [len(cells) - 1, 0]
    trs = list(TRAIN) if not smoke else [11999]
    with Pool(8) as pool:
        TR = pool.map(run, [(i, cells[i], s, 'train') for i in idx for s in trs], chunksize=1)
        log('training done')
        per = {}
        for ci, s, m, r in TR: per.setdefault(ci, []).append(r)
        summ = []
        for ci, rs in sorted(per.items()):
            ok = all(r is not None for r in rs) and len(rs) == len(trs); d = dict(cell=ci, cfg=cells[ci], usable=ok)
            if ok:
                d['D_runs'] = [r['D'] for r in rs]; d['D_mean'] = float(np.mean(d['D_runs'])); d['D_max'] = max(d['D_runs'])
                d['surf_mean'] = {k: float(np.mean([r['surf'][k] for r in rs])) for k in C83.SURF}; d['feasible'] = C83.like(d['surf_mean'])
            else: d['feasible'] = False
            summ.append(d)
        res['train'] = summ; feas = [d for d in summ if d['feasible']]; us = [d for d in summ if d['usable']]
        res['grid_extreme'] = dict(n_cells=len(summ), n_usable=len(us), n_feasible=len(feas),
            max_feasible_D_mean=max([d['D_mean'] for d in feas], default=None),
            max_feasible_single_run=max([d['D_max'] for d in feas], default=None),
            max_all_D_mean=max([d['D_mean'] for d in us], default=None), max_all_single_run=max([d['D_max'] for d in us], default=None),
            n_feasible_cells_any_run_ge_IT2a=sum(d['D_max'] >= MD['IT2a'] for d in feas),
            n_all_cells_any_run_ge_IT2a=sum(d['D_max'] >= MD['IT2a'] for d in us))
        log('grid', res['grid_extreme'])
        if not feas: res['H1'] = 'NOT TESTABLE (no feasible cell)'
        else:
            win = max(feas, key=lambda d: (d['D_mean'], -d['cell'])); res['winner'] = dict(cell=win['cell'], cfg=win['cfg'], D_mean=win['D_mean'])
            log('winner', res['winner'])
            if smoke: refs = list(REF)[:2]; holds = list(HOLD)[:1]; plants = list(PLANT)[:1]
            else: refs, holds, plants = list(REF), list(HOLD), list(PLANT)
            CR = pool.map(run, [(win['cell'], cells[win['cell']], s, m) for m, rr in (('ref', refs), ('hold', holds), ('plant', plants)) for s in rr], chunksize=1)
            ref = {s: r for ci, s, m, r in CR if m == 'ref' and r}; hold = {s: r for ci, s, m, r in CR if m == 'hold' and r}
            pl = {s: r for ci, s, m, r in CR if m == 'plant' and r}
            ga = [r['D'] for r in ref.values()]; lo, hi = min(ga), max(ga)
            call = lambda d: 'ABOVE' if d > hi else ('BELOW' if d < lo else 'INSIDE')
            hc = {s: call(r['D']) for s, r in hold.items()}; pc = {s: call(r['D']) for s, r in pl.items()}
            g1n = sum(c != 'INSIDE' for c in hc.values()); g2n = sum(c == 'ABOVE' for c in pc.values())
            gates = dict(G1=f'{g1n}/{len(hold)}', G1_pass=g1n <= 2 and len(hold) == len(holds), G2=f'{g2n}/{len(pl)}',
                         G2_pass=g2n >= 0.8 * len(plants), G3=f'{len(ref)}/{len(refs)}', G3_pass=len(ref) >= 0.9 * len(refs))
            surf = {k: float(np.mean([r['surf'][k] for r in ref.values()])) for k in C83.SURF}; sok = C83.like(surf)
            ver = {k: dict(D=MD[k], call=call(MD[k]), n_ref_ge=sum(g >= MD[k] for g in ga)) for k in MD}
            cs = [v['call'] for v in ver.values()]
            if not all(gates[g] for g in ('G1_pass', 'G2_pass', 'G3_pass')): H1 = 'NOT TESTABLE (gate)'
            elif all(c == 'ABOVE' for c in cs): H1 = 'ROBUST DEPARTURE (within this grid)'
            elif all(c == 'INSIDE' for c in cs): H1 = 'REACHED' if sok else 'REACHED ONLY WITH SURFACE LOSS'
            else: H1 = 'NOT CALLED (' + ' / '.join(cs) + ')'
            res.update(reference={str(s): r for s, r in ref.items()}, ref_range=[lo, hi], ref_mean=float(np.mean(ga)),
                       ref_sd=float(np.std(ga, ddof=1)) if len(ga) > 1 else None, holdout={str(s): r for s, r in hold.items()},
                       plants={str(s): r for s, r in pl.items()}, holdout_calls={str(k): v for k, v in hc.items()},
                       plant_calls={str(k): v for k, v in pc.items()}, ref_surface=surf, ref_surface_ok=sok, gates_H1=gates,
                       verdict_H1_detail=ver, H1=H1)
            log('H1', H1, gates, ver, 'ref range', lo, hi)
    # H2 position control
    s2 = {f'{k}|{L}': h2_lines(P, k, L) for k, _ in FILES for L in 'AB'}
    res['H2_n'] = {s: dict(lines=len(v.L), pairs=int(v.pair[:-1].sum())) for s, v in s2.items()}
    rng = np.random.default_rng(H2GATE); Gt = {}
    for s, Lo in s2.items():
        g = W.gate(Lo, rng, QH2, ng=20 if not smoke else 2)
        g['ok'] = bool(g['FPR'] <= 2 and g['NEG'] >= 16 and g['POS'] >= 16 and g['D_neg_mean'] < 0 < g['D_pos_mean']); Gt[s] = g
    res['H2_gates'] = Gt; log('H2 gates', Gt)
    rng = np.random.default_rng(H2SEED); H = {s: W.test(Lo, rng, 2000 if not smoke else 50) for s, Lo in s2.items()}
    ph = W.holm({s: h['p'] for s, h in H.items()})
    for s in H: H[s]['p_holm'] = ph[s]
    ver = {}
    for L in 'AB':
        ks = [f'{k}|{L}' for k, _ in FILES]
        if not all(Gt[k]['ok'] for k in ks): ver[L] = 'NOT TESTABLE'; continue
        rej = [k for k in ks if H[k]['p_holm'] <= 0.05]; sg = {np.sign(H[k]['D']) for k in rej}
        if len(rej) == 2 and len(sg) == 1: ver[L] = 'DETECTED-' + ('ALTERNATING' if sg == {-1.0} else 'PERSISTENT')
        elif rej: ver[L] = 'PARTIAL'
        else: ver[L] = 'NOT DETECTED'
    res['H2'] = H; res['verdict_H2'] = ver; log('H2', H, ver)
    res['elapsed_s'] = round(time.time() - T0, 1)
    json.dump(res, open(outp, 'w'), indent=1, default=float); log('done', res.get('H1'), ver)

if __name__ == '__main__':
    main(smoke='smoke' in sys.argv)
