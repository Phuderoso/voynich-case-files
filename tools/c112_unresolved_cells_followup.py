#!/usr/bin/env python3
"""C112 (F-VC step 4): confirmatory follow-up on the 14 C110 cells left UNRESOLVED (grid of the Timm-Schinner copying
generator under C109's slot null). Design agreed in advance with Kryptos (12 Nov 2026): per-cell n fixed from the C110 pooled
sd 0.029 with the MDE printed, and a regime-stratified secondary in which a cell can only be rated REACHES if its 'E' (vowel)
regime also reaches.
Statistic: C109 E_slot (imported unchanged via C110's run()), NSH 100 per half, 4,600 lines, first 30,000 tokens = 2 halves.
Unit (primary): the SEED (mean of its two halves), n = 20 seeds per cell (11753-11772); halves of one run are not independent.
Bar B = 0.1996 (C110, from the published C109 Voynich values). One-sided one-sample t vs B per direction, Holm over the 14
cells at alpha 0.05 per direction: REACHES / BELOW / UNRESOLVED.
Secondary (regime): halves whose Sukhotin vowel class contains EVA 'e' ('E', as all four Voynich halves); per cell with >= 6
E halves, one-sided t of the E halves vs B per direction, Holm over testable cells. Final REACHES = primary REACHES and
E-regime REACHES. Flip fraction printed.
H1 (the 14 cells): every cell BELOW -> NOT REACHED (with C110's 51 BELOW: whole C083 grid NOT REACHED); any feasible final
REACHES -> REACHED; final REACHES only in infeasible cells -> REACHED ONLY WITH SURFACE LOSS; else UNRESOLVED (k of 14).
Gates (fail -> NOT TESTABLE): G-NEG the default generator on the same 20 seeds must be BELOW at alpha/14;
G-SHIFT for each cell, its own 20 seed means recentred to B+0.03 must test above at alpha/14 and recentred to B-0.03 below
at alpha/14, in >= 13 of 14 cells each (certifies the rule at the agreed MDE 0.03 with the observed scatter).
Seeds: generator 11753-11772, null rng 11773 (derived per task); 11774 reserved for the Kryptos plant side-task; next free 11775.
Pre-registered in case-file/C112-unresolved-cells-followup.md. Run: timeout 600 python3 tools/c112_unresolved_cells_followup.py
- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c110_grid_slot_null as X
import c083_generator_grid as C
import c004_generator_sweep as G

CELLS = [1, 2, 7, 9, 10, 14, 16, 21, 25, 27, 31, 40, 48, 49]
GSEEDS = list(range(11753, 11773)); X.NSEED = 11773; GLINES = 4600; ALPHA = 0.05; SHIFT = 0.03; POOLED_SD = 0.029

def mde(n=20, m=14, sd=POOLED_SD, power_z=0.8):
    lvl = ALPHA / m; t1 = X.SS.t.isf(lvl, n - 1); t2 = X.SS.t.isf(1 - power_z, n - 1)
    return dict(level=lvl, t_crit=t1, mde50=t1 * sd / np.sqrt(n), mde80=(t1 + t2) * sd / np.sqrt(n))

def main(smoke=False):
    t0 = time.time(); allc = C.grid(); B0, vv = X.bar(); print('bar', round(B0, 4), 'mde', mde(), flush=True)
    cells = CELLS[:1] if smoke else CELLS; seeds = [1, 2, 3, 4] if smoke else GSEEDS  # smoke: unregistered seeds only
    tasks = []
    for ci in cells:
        cfg = C.tocfg(allc[ci]); cfg['text.lines_to_create'] = GLINES
        tasks += [(ci, cfg, s) for s in seeds]
    tasks += [(-1, {'text.lines_to_create': GLINES}, s) for s in seeds]
    res = {}
    with Pool(8) as P:
        for ci, s, hs, surf in P.imap_unordered(X.run, tasks):
            res.setdefault(ci, []).append(dict(seed=s, halves=hs, surf=surf))
            print('cell', ci, s, None if hs is None else [(round(h['E'], 4), h['V']) for h in hs], round(time.time() - t0, 1), flush=True)
    rep = {}
    for ci in cells + [-1]:
        runs = sorted(res.get(ci, []), key=lambda r: r['seed']); ok = [r for r in runs if r['halves'] and len(r['halves']) == 2]
        sm = [float(np.mean([h['E'] for h in r['halves']])) for r in ok]
        hE = [h['E'] for r in ok for h in r['halves']]; rg = ''.join(X.regime(h['V']) for r in ok for h in r['halves'])
        sf = [r['surf'] for r in runs if r['surf']]; ms = {k: float(np.mean([x[k] for x in sf])) for k in C.SURF} if sf else None
        d = dict(n_seeds=len(sm), seed_means=sm, halves=hE, regimes=rg, surf=ms, feasible=bool(ms and C.like(ms)) if ci >= 0 else None,
                 half_sd=float(np.std(hE, ddof=1)) if len(hE) > 1 else None)
        if len(sm) >= 4:
            pu, pd, m, sd = X.ttests(sm, B0); d.update(p_up=pu, p_down=pd, mean=m, sd_seed=sd)
        eh = [e for e, r in zip(hE, rg) if r == 'E']; d['n_E'] = len(eh)
        if len(eh) >= 6:
            pu, pd, m, sd = X.ttests(eh, B0); d.update(E_p_up=pu, E_p_down=pd, E_mean=m, E_sd=sd)
        if len(sm) >= 4 and ci >= 0:
            a = np.array(sm); c = a - a.mean()
            d['shift_up_p'] = X.ttests(list(c + B0 + SHIFT), B0)[0]; d['shift_down_p'] = X.ttests(list(c + B0 - SHIFT), B0)[1]
        rep[ci] = d
    U = [c for c in cells if 'p_up' in rep[c]]; m = len(U); lvl = ALPHA / len(cells)
    ru = X.holm([rep[c]['p_up'] for c in U]); rd = X.holm([rep[c]['p_down'] for c in U])
    for c, a, b in zip(U, ru, rd): rep[c]['label'] = 'REACHES' if a else 'BELOW' if b else 'UNRESOLVED'
    UE = [c for c in U if 'E_p_up' in rep[c]]
    eu = X.holm([rep[c]['E_p_up'] for c in UE]) if UE else []; ed = X.holm([rep[c]['E_p_down'] for c in UE]) if UE else []
    for c in U: rep[c]['E_label'] = 'NOT TESTABLE (<6 E halves)'
    for c, a, b in zip(UE, eu, ed): rep[c]['E_label'] = 'REACHES' if a else 'BELOW' if b else 'UNRESOLVED'
    for c in U: rep[c]['final'] = 'REACHES' if rep[c]['label'] == 'REACHES' and rep[c]['E_label'] == 'REACHES' else ('REACHES (pooled only; E regime does not)' if rep[c]['label'] == 'REACHES' else rep[c]['label'])
    neg = rep[-1]; gneg = bool(neg.get('p_down', 1) <= lvl)
    nsu = sum(rep[c]['shift_up_p'] <= lvl for c in U); nsd = sum(rep[c]['shift_down_p'] <= lvl for c in U)
    gs = nsu >= 13 and nsd >= 13 and m == len(cells)
    GT = dict(level=lvl, G_NEG=dict(mean=neg.get('mean'), p_down=neg.get('p_down'), ok=gneg), G_SHIFT=dict(up=f'{nsu}/{m}', down=f'{nsd}/{m}', ok=gs))
    fin = {c: rep[c]['final'] for c in U}; reach = [c for c in U if fin[c] == 'REACHES']; reachF = [c for c in reach if rep[c]['feasible']]
    if not (gneg and gs) or m < len(cells): H1 = 'NOT TESTABLE'
    elif reachF: H1 = 'REACHED'
    elif reach: H1 = 'REACHED ONLY WITH SURFACE LOSS'
    elif all(fin[c] == 'BELOW' for c in U): H1 = 'NOT REACHED (all 14 BELOW; with C110 all 65 cells of the C083 grid BELOW)'
    else: H1 = f'UNRESOLVED ({sum(fin[c] != "BELOW" for c in U)} of {m} not BELOW)'
    sds = [rep[c]['sd_seed'] for c in U]; psd = float(np.sqrt(np.mean(np.square(sds)))) if sds else None
    D = dict(bar=B0, counts={k: sum(1 for c in U if rep[c]['label'] == k) for k in ('REACHES', 'BELOW', 'UNRESOLVED')},
             E_counts={k: sum(1 for c in U if rep[c]['E_label'] == k) for k in ('REACHES', 'BELOW', 'UNRESOLVED', 'NOT TESTABLE (<6 E halves)')},
             flip_fraction=f"{sum(len(set(rep[c]['regimes'])) > 1 for c in U)}/{m}", share_E=round(float(np.mean([r == 'E' for c in U for r in rep[c]['regimes']])), 3),
             max_cell_mean=max(((rep[c]['mean'], c) for c in U), default=None), max_half=max(((e, c) for c in U for e in rep[c]['halves']), default=None),
             halves_at_or_above_bar=f"{sum(e >= B0 for c in U for e in rep[c]['halves'])}/{sum(len(rep[c]['halves']) for c in U)}",
             pooled_seed_sd=psd, realized_mde=mde(sd=psd) if psd else None, n_feasible=sum(bool(rep[c]['feasible']) for c in U))
    out = dict(seeds=dict(gen=GSEEDS, null=11773, reserved_side_task=11774, next_free=11775), NSH=X.NSH, prereg_mde=mde(), gates=GT, H1=H1,
               descriptive=D, cells={str(c): rep[c] for c in cells}, negative=neg, runtime_s=round(time.time() - t0, 1))
    fn = '/workspace/voynich/c112/C112_smoke.json' if smoke else 'analysis/C112_results.json'
    json.dump(out, open(fn, 'w'), indent=1, default=float)
    print('H1', H1, 'gates', GT, D, out['runtime_s'], flush=True)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'mde': print(mde())
    else: main(smoke=len(sys.argv) > 1 and sys.argv[1] == 'smoke')
