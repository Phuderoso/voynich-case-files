#!/usr/bin/env python3
"""C094 (F-NET step 2): does C093's H3 (manuscript RHO above the default Timm-Schinner generator at K = 4,000 types)
hold at a second size and inside Currier A and Currier B separately? Plus one homogeneous natural reference.
Instrument = C093 verbatim (tools/c093_edit_graph.py: prefix sampling of the first K distinct word types in token order,
edge = Levenshtein 1 over units, RHO = Spearman(type frequency inside the prefix, degree), plant, gate, predictive t, Holm).
Units: Voynich = C003 glyph units (ch, sh, cth, ckh, cph, cfh single); generator = C003 units; Cervantes = letters.
Manuscript streams (paragraph loci only, lines with unreadable words dropped, >= 3 words; the C091-C093 filter):
  ALL = whole paragraph stream, A = pages tagged $L=A, B = pages tagged $L=B (page order).
  Types available: ZL ALL 6,894 / A 3,145 / B 4,717; IT2a ALL 6,908 / A 3,135 / B 4,753.
Registered cells (design v3; v1 and v2 were rehearsed first, on references only, and are disclosed in the case file):
  H3a RHO(ALL, K 2,000) vs generator; H3A RHO(Currier A, K 3,000) vs generator; H3B RHO(Currier B, K 4,000) vs generator;
  H5  RHO(ALL, K 4,000) vs HOMOGENEOUS NATURAL: Don Quijote cut into 10 disjoint contiguous 38,000-token chunks;
  AUD C093 H3 audit: RHO(ALL, K 4,000) vs the 20 pooled generator runs (not blind: the C093 value is public; own Holm).
References: 20 default generator runs = C093's seeds 11474-11483 (regenerated; identical output) + fresh 11484-11493
(8,000 lines; next seed 11494); the 10 Cervantes chunks. Every reference is measured at K = 2,000, 3,000, 4,000.
Gates (C093 verbatim): G0 reach >= n-1; G1 leave-one-out false calls at raw p < 0.05 <= 1 (C093 code); G2 power with planted
one-edit copying (F 0.10 generator, 0.25 Cervantes) detected >= n-1; DOA 0.054 > MDE80. Failing cells: NOT RUN, LOW-POWER.
The manuscript is measured ONLY if at least one cell passes its gate.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c093_edit_graph as E
import c003_position_rigidity as T
from c047_pair_currier_split import ivtff_pages_lang

SEED, LINES = 9494, 8000
KS = (2000, 3000, 4000)          # v2: every reference is measured at all three sizes
E.SEED = SEED
GSEEDS = list(range(11474, 11494))   # v3: C093's 10 runs (11474-11483, regenerated, never used at K 2,000/3,000 or on
                                     # Currier A/B) pooled with 10 fresh runs (11484-11493); next seed 11494
NCHUNK, CHUNK = 10, 38000      # v2: 38,000-token chunks so every chunk reaches 4,000 types
VPATH = E.VPATH

def stream(path, L=None):
    pl, lang, _ = ivtff_pages_lang(path)
    return [tuple(T.units(w)) for p, l in pl if L is None or lang.get(p) == L for w in l]

def job(spec):
    kind, name, s = spec; rng = np.random.default_rng([SEED, s])
    if kind == 'gen':
        import c004_generator_sweep as G
        Lg = G.generate({'text.lines_to_create': LINES}, s); ws = [tuple(T.units(w)) for l in (Lg or []) for w in l]; F = E.FG
    else:
        allw = E.D.seqs_nat(*E.D.NAT['Spanish_Cervantes']); ws = [tuple(w) for w in allw[s * CHUNK:(s + 1) * CHUNK]]; F = E.FN
    pw = E.plant(ws, rng, F)
    return name, dict(ntokens=len(ws), ref={k: E.measure(ws, k) for k in KS}, plant={k: E.measure(pw, k) for k in KS})

def at(R, k): return {m: dict(ref=v['ref'][k], plant=v['plant'][k]) for m, v in R.items()}

def main(mode):
    t0 = time.time()
    specs = [('gen', f'gen_{s}', s) for s in GSEEDS] + [('cerv', f'cerv_{i}', i) for i in range(NCHUNK)]
    with Pool(8) as p: R = dict(p.map(job, specs))
    gen = [f'gen_{s}' for s in GSEEDS]; cerv = [f'cerv_{i}' for i in range(NCHUNK)]
    G = {(r, k): E.gate(at(R, k), names, 'RHO') for r, names in (('gen', gen), ('cerv', cerv)) for k in KS}
    # v2 registered cells: (reference, manuscript stream, K)
    cells = {'H3a': ('gen', 'ALL', 2000), 'H3A': ('gen', 'A', 3000), 'H3B': ('gen', 'B', 4000), 'H5': ('cerv', 'ALL', 4000),
             'AUD': ('gen', 'ALL', 4000)}   # AUD = C093 H3 audit vs 20 pooled runs; NOT blind (C093 value public); own Holm
    out = dict(seed=SEED, mode=mode, KS=KS, lines=LINES, gseeds=GSEEDS, chunks=[NCHUNK, CHUNK], refs=R,
               gates={f'{r}_K{k}': g for (r, k), g in G.items()}, cells=cells)
    out['runnable'] = [h for h, (r, L, k) in cells.items() if G[(r, k)]['ok']]
    if mode == 'run' and not out['runnable']:
        out['note'] = 'no cell passed its gate: manuscript NOT measured'
    if mode == 'run' and out['runnable']:
        V = {}
        for tn, pth in VPATH.items():
            for L in ('ALL', 'A', 'B'):
                ws = stream(pth, None if L == 'ALL' else L)
                for k in KS: V[f'{tn}_{L}_K{k}'] = dict(ntokens=len(ws), ntypes=len(set(ws)), **(E.measure(ws, k) or {}))
        tests = []
        for h, (r, L, k) in cells.items():
            g = G[(r, k)]; names = gen if r == 'gen' else cerv
            ref = [R[m]['ref'][k]['RHO'] for m in names if R[m]['ref'][k] is not None]
            for tn in VPATH:
                if not g['ok']: tests.append(dict(cell=f'{h}_{tn}', status='NOT RUN, LOW-POWER', why=g['why'])); continue
                x = V[f'{tn}_{L}_K{k}']['RHO']
                tests.append(dict(cell=f'{h}_{tn}', status='run', x=x, p=E.pt(x, ref),
                                  z=float((x - np.mean(ref)) / np.std(ref, ddof=1)), gap=float(x - np.mean(ref)),
                                  gap_over_MDE=float((x - np.mean(ref)) / g['MDE80']),
                                  above_all=bool(x > max(ref)), below_all=bool(x < min(ref))))
        run = [t for t in tests if t['status'] == 'run' and not t['cell'].startswith('AUD')]
        aud = [t for t in tests if t['status'] == 'run' and t['cell'].startswith('AUD')]
        for t, a in zip(aud, E.holm([t['p'] for t in aud])): t['p_holm'] = a
        for t, a in zip(run, E.holm([t['p'] for t in run])): t['p_holm'] = a
        out.update(voynich=V, tests=tests)
    out['elapsed_s'] = time.time() - t0
    return out

if __name__ == '__main__':
    o = main(sys.argv[1]); json.dump(o, open(sys.argv[2], 'w'), indent=1, default=str)
    f = lambda d: {k: round(x, 4) for k, x in d.items()} if d else None
    for m, v in o['refs'].items():
        for k in KS: print(m, k, v['ntokens'], 'ref', f(v['ref'][k]), 'plant', f(v['plant'][k]))
    for h, g in o['gates'].items(): print(h, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in g.items()})
    print('runnable', o['runnable'], o.get('note', ''))
    if 'voynich' in o:
        for k, v in o['voynich'].items(): print('voynich', k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()})
        for t in o['tests']: print(t)
    print('elapsed', round(o['elapsed_s'], 1))
