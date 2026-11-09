#!/usr/bin/env python3
"""C095 (F-NET step 3): pre-registered RE-GATE of the C093/C094 edit-graph statistic RHO against the default
Timm-Schinner generator, with the plant strength fixed IN ADVANCE by the effect of interest and with batch stability built in.
Instrument = C093 verbatim (tools/c093_edit_graph.py: prefix of the first K distinct types in token order, edge = Levenshtein 1
over units, RHO = Spearman(frequency inside the prefix, degree), one-edit copying plant, predictive t, MDE80, Holm).
Manuscript streams = C094's stream() (paragraph loci, the C091-C094 filter, page order): ALL, Currier A ($L=A), Currier B ($L=B).
PLANT STRENGTH (fixed before any C095 number was seen): effect of interest DELTA = 0.054 (Zhang & Sheng's gap, fixed in C093).
  Rule: the smallest F on C094's design grid (0.10, 0.15, 0.20, 0.30) whose mean |RHO shift| on C094's 20 pooled runs
  (seeds 11474-11493, independent of every C095 batch) is >= 0.95*DELTA = 0.0513 at BOTH K 3,000 and K 4,000.
  C094 curve: F 0.15 -> 0.0485 / 0.0492 (fails); F 0.20 -> 0.0533 / 0.0530 (passes) => F = 0.20.
REFERENCES: two independent brand-new batches of 20 default generator runs (8,000 lines):
  N1 = seeds 11494-11513 (primary), N2 = seeds 11514-11533 (stability batch). Next free generator seed 11534. Plant seed 9595.
CELLS: W3 = RHO(ALL, K 3,000); W4 = RHO(ALL, K 4,000) (= C093 H3 replication on blind references); B4 = RHO(Currier B, K 4,000);
  A3 = RHO(Currier A, K 3,000), included only if its gate holds (same rule as every cell).
GATES (C093's, plant F 0.20), each evaluated SEPARATELY on N1 and on N2: G0 reach >= 19/20; G1 leave-one-out false calls
  at raw p < 0.05 <= 1/20; G2 planted power >= 19/20; DOA 0.054 > MDE80. A cell is RUNNABLE only if it passes on BOTH batches;
  otherwise NOT RUN, LOW-POWER (NOT TESTABLE). Batch stability (reported for every K): sd(N1)/sd(N2), Brown-Forsythe
  (median-centred Levene) p and Welch-t p of the means, descriptive.
TESTS (only if >= 1 cell runnable): x vs N1 -> family 1 (Holm over runnable cells x {ZL3b, IT2a}); x vs N2 -> family 2 (own Holm).
  HIGHER / LOWER only if Holm < 0.05 for both transcriptions in BOTH families, same direction; Holm < 0.05 in one family
  only -> NOT REPLICATED (no call); otherwise NOT DIFFERENT at this power.
CLOSING RULE: no runnable cell -> F-NET generator line CLOSED (NOT TESTABLE); C093 H3 -> UNCONFIRMED.
  W4 not runnable, or W4 not HIGHER in both families -> C093 H3 -> UNCONFIRMED. W4 HIGHER in both -> C093 H3 REPLICATED.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from multiprocessing import Pool
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.dirname(__file__))
import c093_edit_graph as E
import c003_position_rigidity as T
from c094_edit_graph_step2 import stream

SEED, LINES, F = 9595, 8000, 0.20
KS = (3000, 4000)
N1 = list(range(11494, 11514)); N2 = list(range(11514, 11534))
E.SEED = SEED
VPATH = E.VPATH
CELLS = {'W3': ('ALL', 3000), 'W4': ('ALL', 4000), 'B4': ('B', 4000), 'A3': ('A', 3000)}

def job(s):
    import c004_generator_sweep as G
    rng = np.random.default_rng([SEED, s])
    ws = [tuple(T.units(w)) for l in (G.generate({'text.lines_to_create': LINES}, s) or []) for w in l]
    pw = E.plant(ws, rng, F)
    return f'gen_{s}', dict(ntokens=len(ws), ref={k: E.measure(ws, k) for k in KS}, plant={k: E.measure(pw, k) for k in KS})

def at(R, k): return {m: dict(ref=v['ref'][k], plant=v['plant'][k]) for m, v in R.items()}

def main(mode):
    t0 = time.time()
    with Pool(8) as p: R = dict(p.map(job, N1 + N2))
    b1 = [f'gen_{s}' for s in N1]; b2 = [f'gen_{s}' for s in N2]
    G = {(b, k): E.gate(at(R, k), names, 'RHO') for b, names in (('N1', b1), ('N2', b2)) for k in KS}
    stab = {}
    for k in KS:
        x1 = [R[m]['ref'][k]['RHO'] for m in b1]; x2 = [R[m]['ref'][k]['RHO'] for m in b2]
        stab[f'K{k}'] = dict(sd_N1=float(np.std(x1, ddof=1)), sd_N2=float(np.std(x2, ddof=1)),
                             sd_ratio=float(np.std(x1, ddof=1) / np.std(x2, ddof=1)), mean_N1=float(np.mean(x1)),
                             mean_N2=float(np.mean(x2)), BF_p=float(stats.levene(x1, x2, center='median').pvalue),
                             welch_p=float(stats.ttest_ind(x1, x2, equal_var=False).pvalue))
    runnable = [c for c, (L, k) in CELLS.items() if G[('N1', k)]['ok'] and G[('N2', k)]['ok']]
    out = dict(seed=SEED, mode=mode, F=F, KS=KS, lines=LINES, N1=N1, N2=N2, refs=R,
               gates={f'{b}_K{k}': g for (b, k), g in G.items()}, stability=stab, cells=CELLS, runnable=runnable)
    if mode == 'run' and not runnable: out['note'] = 'no cell passed its gate on both batches: manuscript NOT measured'
    if mode == 'run' and runnable:
        V = {}
        for tn, pth in VPATH.items():
            for L in ('ALL', 'A', 'B'):
                ws = stream(pth, None if L == 'ALL' else L)
                for k in KS: V[f'{tn}_{L}_K{k}'] = dict(ntokens=len(ws), ntypes=len(set(ws)), **(E.measure(ws, k) or {}))
        # descriptive identity check against C093's published values (C093 parse, K 4,000)
        V['C093_parse_K4000'] = {tn: E.measure([tuple(w) for w in E.D.seqs_voy(p)], 4000)['RHO'] for tn, p in VPATH.items()}
        fam = {}
        for b, names in (('N1', b1), ('N2', b2)):
            tests = []
            for c, (L, k) in CELLS.items():
                ref = [R[m]['ref'][k]['RHO'] for m in names]
                for tn in VPATH:
                    if c not in runnable:
                        tests.append(dict(cell=f'{c}_{tn}', status='NOT RUN, LOW-POWER')); continue
                    x = V[f'{tn}_{L}_K{k}']['RHO']
                    tests.append(dict(cell=f'{c}_{tn}', status='run', x=x, p=E.pt(x, ref), gap=float(x - np.mean(ref)),
                                      gap_over_MDE=float((x - np.mean(ref)) / G[(b, k)]['MDE80']),
                                      above_all=bool(x > max(ref)), below_all=bool(x < min(ref))))
            run = [t for t in tests if t['status'] == 'run']
            for t, a in zip(run, E.holm([t['p'] for t in run])): t['p_holm'] = a
            fam[b] = tests
        verdict = {}
        for c in CELLS:
            if c not in runnable: verdict[c] = 'NOT RUN, LOW-POWER (NOT TESTABLE)'; continue
            sig = {b: [t for t in fam[b] if t['cell'].startswith(c + '_')] for b in fam}
            rej = {b: all(t['p_holm'] < 0.05 for t in sig[b]) for b in sig}
            dirs = {np.sign(t['gap']) for b in sig for t in sig[b]}
            if all(rej.values()) and len(dirs) == 1: verdict[c] = 'HIGHER' if dirs.pop() > 0 else 'LOWER'
            elif any(rej.values()): verdict[c] = 'NOT REPLICATED (no call)'
            else: verdict[c] = 'NOT DIFFERENT at this power'
        out.update(voynich=V, tests=fam, verdict=verdict)
    if mode == 'run':
        w4 = out.get('verdict', {}).get('W4')
        out['closing'] = dict(fnet_generator_line='CLOSED (NOT TESTABLE)' if not runnable else 'open',
                              C093_H3='REPLICATED' if w4 == 'HIGHER' else 'UNCONFIRMED')
    out['elapsed_s'] = time.time() - t0
    return out

if __name__ == '__main__':
    o = main(sys.argv[1]); json.dump(o, open(sys.argv[2], 'w'), indent=1, default=str)
    r = lambda d: {a: (round(b, 4) if isinstance(b, float) else b) for a, b in d.items()} if d else None
    for m, v in o['refs'].items():
        for k in KS: print(m, k, v['ntokens'], 'ref', round(v['ref'][k]['RHO'], 4), 'plant', round(v['plant'][k]['RHO'], 4))
    for h, g in o['gates'].items(): print(h, r(g))
    for h, g in o['stability'].items(): print('stability', h, r(g))
    print('runnable', o['runnable'], o.get('note', ''))
    if 'voynich' in o:
        for k, v in o['voynich'].items(): print('voynich', k, r(v) if isinstance(v, dict) else v)
        for b, ts in o['tests'].items():
            for t in ts: print(b, r(t))
        print('verdict', o['verdict'])
    if 'closing' in o: print('closing', o['closing'])
    print('elapsed', round(o['elapsed_s'], 1))
