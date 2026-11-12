#!/usr/bin/env python3
"""C110 (F-VC step 3): can any setting in the FIXED C083 grid of the Timm-Schinner generator reach the manuscript's
neighbour alternation beyond slots (C109 E_slot 0.208-0.225)?
Statistic: C109's E_slot (Sukhotin re-fitted per shuffle, slot-preserving null N2), NSH 100 per half, imported unchanged.
Grid: C083's 65 cells (tools/c083_generator_grid.py::grid), 4,600 lines per run (v2 amendment), common seeds 11744-11746 (6 halves/cell).
Bar (fixed from the PUBLISHED C109 Voynich values, Kryptos's review): B = min(Voynich E_slot) - 2*SE, SE = sd(4 halves, ddof 1)/2.
Per cell (usable iff >= 4 halves): one-sided one-sample t vs B in each direction; Holm across usable cells, alpha 0.05, per
direction. REACHES = up rejected; BELOW = down rejected; else UNRESOLVED. Grid maximum is descriptive only.
Feasible = C083 surface rule (mean over usable runs of mwl, ttr, h2, R within +-15% of the C005 reference).
H1: any feasible REACHES -> REACHED; REACHES only in infeasible cells -> REACHED ONLY WITH SURFACE LOSS; every usable cell
BELOW -> NOT REACHED (within this grid); else UNRESOLVED.  Fewer than 33 usable cells -> NOT TESTABLE.
Gate GR (rule calibration, fresh shuffles): positive panel (6 voweled halves, C109 E 0.211-0.226) must be REACHES and
negative panel (default generator, seeds 11744-11746) must be BELOW, each at the strictest Holm level alpha/m. Fail -> NOT TESTABLE.
Sukhotin regime per half: 'E' iff EVA 'e' is in the fitted vowel class, else 'N'; flip fraction = share of usable cells with
mixed regimes (Kryptos's request).  Minimal detectable excess (descriptive) from the pooled within-cell sd.
Seeds: generator 11744-11746, null rng 11747 (derived per task); next free 11748.
Pre-registered in case-file/C110-grid-slot-null.md.  Run: timeout 600 python3 tools/c110_grid_slot_null.py
- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from multiprocessing import Pool
import numpy as np
import math

def _betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1; c = 1.0; d = 1 - qab * x / qap; d = 1 / (d if abs(d) > 1e-300 else 1e-300); h = d
    for m in range(1, 300):
        m2 = 2 * m; aa = m * (b - m) * x / ((qam + m2) * (a + m2)); d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c; c = c if abs(c) > 1e-300 else 1e-300; h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2)); d = 1 + aa * d; d = 1 / (d if abs(d) > 1e-300 else 1e-300)
        c = 1 + aa / c; c = c if abs(c) > 1e-300 else 1e-300; de = d * c; h *= de
        if abs(de - 1) < 1e-14: break
    return h

def _betai(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    return bt * _betacf(a, b, x) / a if x < (a + 1) / (a + b + 2) else 1 - bt * _betacf(b, a, 1 - x) / b

class SS:
    """Student t (no scipy on the box): sf/cdf via the regularized incomplete beta; isf by bisection."""
    class t:
        @staticmethod
        def sf(t, df):
            tail = 0.5 * _betai(df / 2, 0.5, df / (df + t * t)); return tail if t > 0 else 1 - tail
        @staticmethod
        def cdf(t, df): return 1 - SS.t.sf(t, df)
        @staticmethod
        def isf(q, df):
            lo, hi = 0.0, 1e4
            for _ in range(200):
                mid = (lo + hi) / 2
                if SS.t.sf(mid, df) > q: lo = mid
                else: hi = mid
            return (lo + hi) / 2
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c051_context_spelling_ab as B
import c004_generator_sweep as G
import c083_generator_grid as C
from c108_sukhotin_alternation import flat, chars, halves, NHALF
from c109_sukhotin_slot_null import test

GSEEDS, NSEED, GLINES, NSH, ALPHA = [11744, 11745, 11746], 11747, 4600, 100, 0.05  # v2: 4600 lines (v1 3400 left 111/195 runs short)
POS = [('Latin_Caesar', 0), ('Latin_Descartes', 0), ('Finnish_Kivi', 0), ('Finnish_Kivi', 1),
       ('Spanish_Cervantes', 0), ('Spanish_Cervantes', 1)]

def bar():
    c = json.load(open('analysis/C109_results.json'))['verdict']['voynich_E_slot']
    return min(c) - 2 * float(np.std(c, ddof=1)) / 2, c

def regime(V): return 'E' if 'e' in V else 'N'

def run(args):
    ci, cfg, s = args
    Lg = G.generate(cfg, s); fl = G.flat(Lg or [])
    if not Lg or sum(map(len, Lg)) < 2 * NHALF: return ci, s, None, None
    surf = G.stats(fl[:6000]) if len(fl) >= 6000 else None
    rng = np.random.default_rng([NSEED, ci + 1, s]); hs = []  # v2: ci+1 (v1 crashed on ci=-1)
    for h in halves(Lg):
        r = test([tuple(T.units(w)) for w in flat(h)], rng, NSH); hs.append(dict(E=r['E'], p=r['p'], V=''.join(r['V'])))
    return ci, s, hs, surf

def ttests(vals, b):
    v = np.array(vals); n = len(v); m = v.mean(); sd = v.std(ddof=1)
    if sd == 0: return float(m > b) * 0 + (0.0 if m > b else 1.0), (0.0 if m < b else 1.0), m, sd
    t = (m - b) / (sd / np.sqrt(n)); return float(SS.t.sf(t, n - 1)), float(SS.t.cdf(t, n - 1)), m, sd

def holm(ps, alpha=ALPHA):
    o = np.argsort(ps); m = len(ps); rej = [False] * m
    for r, i in enumerate(o):
        if ps[i] <= alpha / (m - r): rej[i] = True
        else: break
    return rej

def main(cells=None, smoke=False):
    t0 = time.time(); allc = C.grid(); cells = cells if cells is not None else list(range(len(allc)))
    B0, vv = bar(); print('bar', round(B0, 4), vv, flush=True)
    tasks = []
    for ci in cells:
        cfg = C.tocfg(allc[ci]); cfg['text.lines_to_create'] = GLINES
        for s in GSEEDS: tasks.append((ci, cfg, s))
    for s in GSEEDS: tasks.append((-1, {'text.lines_to_create': GLINES}, s))   # negative panel: default generator
    res = {}
    with Pool(8) as P:
        for ci, s, hs, surf in P.imap_unordered(run, tasks):
            res.setdefault(ci, []).append(dict(seed=s, halves=hs, surf=surf))
            print('cell', ci, s, None if hs is None else [(h['E'], h['V']) for h in hs], round(time.time() - t0, 1), flush=True)
    nat = B.nat_texts(); rng = np.random.default_rng([NSEED, 999])
    pos = [test(chars(flat(halves(nat[k])[i])), rng, NSH) for k, i in POS]
    posE = [y['E'] for y in pos]; print('pos', posE, flush=True)
    cellrep = {}
    for ci in cells:
        runs = res.get(ci, []); hs = [h for r in runs if r['halves'] for h in r['halves']]
        sf = [r['surf'] for r in runs if r['surf']]
        ms = {k: float(np.mean([x[k] for x in sf])) for k in C.SURF} if sf else None
        rep = dict(cell=allc[ci], n_halves=len(hs), E=[h['E'] for h in hs], regimes=''.join(regime(h['V']) for h in hs),
                   V=[h['V'] for h in hs], surf=ms, feasible=bool(ms and C.like(ms)), usable=len(hs) >= 4)
        if rep['usable']:
            pu, pd, m, sd = ttests(rep['E'], B0); rep.update(p_up=pu, p_down=pd, mean=round(m, 4), sd=round(sd, 4))
        cellrep[ci] = rep
    U = [ci for ci in cells if cellrep[ci]['usable']]; m = len(U)
    ru = holm([cellrep[c]['p_up'] for c in U]) if m else []; rd = holm([cellrep[c]['p_down'] for c in U]) if m else []
    for c, a, b in zip(U, ru, rd): cellrep[c]['label'] = 'REACHES' if a else 'BELOW' if b else 'UNRESOLVED'
    negE = [h['E'] for r in res.get(-1, []) if r['halves'] for h in r['halves']]
    pu, _, pm, psd = ttests(posE, B0); _, nd, nm, nsd = ttests(negE, B0) if len(negE) >= 4 else (1, 1, None, None)
    lvl = ALPHA / max(m, 1)
    GR = dict(level=lvl, pos_E=posE, pos_p_up=pu, pos_ok=bool(pu <= lvl), neg_E=negE, neg_p_down=nd, neg_ok=bool(nd <= lvl))
    GR['ok'] = GR['pos_ok'] and GR['neg_ok']
    lab = {c: cellrep[c]['label'] for c in U}
    reach = [c for c in U if lab[c] == 'REACHES']; reachF = [c for c in reach if cellrep[c]['feasible']]
    if not GR['ok'] or m < 33: H1 = 'NOT TESTABLE'
    elif reachF: H1 = 'REACHED'
    elif reach: H1 = 'REACHED ONLY WITH SURFACE LOSS'
    elif all(lab[c] == 'BELOW' for c in U): H1 = 'NOT REACHED (within this grid)'
    else: H1 = 'UNRESOLVED'
    sds = [cellrep[c]['sd'] for c in U]; nh = int(np.median([cellrep[c]['n_halves'] for c in U])) if U else 0
    psd_ = float(np.sqrt(np.mean(np.square(sds)))) if sds else None
    mde = psd_ * SS.t.isf(lvl, nh - 1) / np.sqrt(nh) if sds else None
    flips = [c for c in U if len(set(cellrep[c]['regimes'])) > 1]
    allE = [(e, c) for c in U for e in cellrep[c]['E']]
    D = dict(bar=B0, voynich=vv, n_usable=m, counts={k: sum(1 for c in U if lab[c] == k) for k in ('REACHES', 'BELOW', 'UNRESOLVED')},
             reach_cells=reach, reach_feasible=reachF, n_feasible=sum(cellrep[c]['feasible'] for c in U),
             grid_max_cell_mean=max(((cellrep[c]['mean'], c) for c in U), default=None), grid_max_half=max(allE, default=None),
             grid_max_cell_mean_feasible=max(((cellrep[c]['mean'], c) for c in U if cellrep[c]['feasible']), default=None),
             flip_fraction=f'{len(flips)}/{m}', share_halves_E=round(float(np.mean([r == 'E' for c in U for r in cellrep[c]['regimes']])), 3) if U else None,
             max_E_regime_E=max((e for c in U for e, r in zip(cellrep[c]['E'], cellrep[c]['regimes']) if r == 'E'), default=None),
             max_E_regime_N=max((e for c in U for e, r in zip(cellrep[c]['E'], cellrep[c]['regimes']) if r == 'N'), default=None),
             pooled_sd=psd_, mde_above_bar=mde)
    out = dict(seeds=dict(gen=GSEEDS, null=NSEED, next_free=11748), NSH=NSH, GR=GR, H1=H1, descriptive=D,
               cells={str(c): cellrep[c] for c in cells}, negative_runs=res.get(-1), runtime_s=round(time.time() - t0, 1))
    fn = 'analysis/C110_smoke.json' if smoke else 'analysis/C110_results.json'
    json.dump(out, open(fn, 'w'), indent=1, default=float); print('H1', H1, 'GR', {k: v for k, v in GR.items() if 'E' not in k}, D, out['runtime_s'])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'smoke':
        # tool check only: one cell, one seed path exercised; disclosed in the case file
        r = run((0, dict(C.tocfg(C.grid()[0]), **{'text.lines_to_create': GLINES}), 1)); print('smoke run ok', r[2] is not None, r[3] is not None)
        print('t check (df5: sf(2.015)~0.05, sf(4.032)~0.005)', round(SS.t.sf(2.015,5),4), round(SS.t.sf(4.032,5),4), round(SS.t.isf(0.05,5),3)); print('holm', holm([0.001, 0.02, 0.04, 0.5]), 'ttest', ttests([0.22, 0.21, 0.23, 0.215], 0.2)[:2]); print('bar', bar())
    else: main()
