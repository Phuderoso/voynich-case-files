#!/usr/bin/env python3
"""C069 (F-VERT step 2, confirmatory test of the C068 post-hoc lead; hypothesis suggested by C068 data).
Is the manuscript's vertical alignment excess Dc (C068 statistic, same code) BELOW the Timm-Schinner generator's default
(sourceChooser=page, same_position_probability=28) and ABOVE the same generator with same_position_probability=0?
Generator texts are size-matched to the manuscript: 2,784 lines in 29-line pages (96 pages, 2,688 pairs) instead of C068's 1,200.
References (fresh seeds): default 9401-9520, spp0 9601-9720 (first 100 valid runs each).
H1 (per transcription): p1 = (1 + #{default ref Dc <= V}) / 101.  H2: p2 = (1 + #{spp0 ref Dc >= V}) / 101.
Holm over 4 (H1, H2 x ZL, IT2a), alpha 0.05.  V = Dc delta with the C068 procedure and seed 6868 (C068 values recomputed).
Gates (held-out fresh seeds as pseudo-manuscripts): default 9801-9830, spp0 9901-9930 (first 20 valid each).
 H1 FPR: held-out default runs, p1 <= 0.05 in <= 2/20; H1 power: held-out spp0 runs, p1 <= 0.05 in >= 16/20.
 H2 FPR: held-out spp0 runs, p2 <= 0.05 in <= 2/20; H2 power: held-out default runs, p2 <= 0.05 in >= 16/20.
Decision: H1/H2 each SUPPORTED (both transcriptions reject after Holm), PARTIAL (one), NOT DETECTED (none, gates pass),
NOT TESTABLE (a gate fails). BETWEEN-SETTINGS if H1 and H2 both SUPPORTED.
Descriptive dose curve (no p claims): spp in {7, 14, 21}, seeds 10001-10015, 10101-10115, 10201-10215 (first 10 valid each);
median Dc per spp with 0 and 28 from the references; spp where the median curve crosses V by linear interpolation.
Note: generator texts use one page group (no Currier language/section), as in C068 descriptive runs.
Run: timeout 600 python3 tools/c069_vert_dose.py   (design: python3 tools/c069_vert_dose.py design -> timing on seed 1 only)
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c068_vertical_alignment as V
import c003_position_rigidity as T
from c004_generator_sweep import generate

SEED, NLINES, ALPHA = 6868, 2784, 0.05
SET = {'default': {}, 'spp0': {'method.sourceChooser.same_position_probability': 0},
       'spp7': {'method.sourceChooser.same_position_probability': 7}, 'spp14': {'method.sourceChooser.same_position_probability': 14},
       'spp21': {'method.sourceChooser.same_position_probability': 21}}
GROUPS = {'ref_default': ('default', range(9401, 9521), 100), 'ref_spp0': ('spp0', range(9601, 9721), 100),
          'ho_default': ('default', range(9801, 9831), 20), 'ho_spp0': ('spp0', range(9901, 9931), 20),
          'dose7': ('spp7', range(10001, 10016), 10), 'dose14': ('spp14', range(10101, 10116), 10), 'dose21': ('spp21', range(10201, 10216), 10)}

def dc_only(lines, pairs, rng):
    Ac, Af, N = V.table(lines, pairs, rng)
    a0, n0 = Ac[:, 0].sum(), N[:, 0].sum(); ar, nr = Ac[:, 1:].sum(), N[:, 1:].sum()
    return float(a0 / max(n0, 1) - ar / max(nr, 1)), int(len(Ac))

def gen_job(a):
    g, setting, s = a; cfg = dict(SET[setting]); cfg['text.lines_to_create'] = NLINES + 600
    Lg = generate(cfg, s)
    if not Lg: return g, s, None
    rows = [l for l in Lg if len(l) >= 3]
    if len(rows) < NLINES: return g, s, None
    lines, pairs = V.block_text(rows[:NLINES], T.units)
    return g, s, dc_only(lines, pairs, np.random.default_rng(SEED * 10 + s))

def holm(ps):
    o = np.argsort(ps); m = len(ps); rej = [False] * m
    for r, i in enumerate(o):
        if ps[i] <= ALPHA / (m - r): rej[i] = True
        else: break
    return rej

def main():
    t0 = time.time()
    if len(sys.argv) > 1 and sys.argv[1] == 'design':
        r = gen_job(('design', 'default', 1)); print('DESIGN timing only', r[2] is not None, round(time.time() - t0, 1)); return
    with Pool(8) as pool:
        jobs = [(g, st, s) for g, (st, seeds, _) in GROUPS.items() for s in seeds]
        gj = pool.map_async(gen_job, jobs, chunksize=1)
        Vd = {}
        for k, f in V.FILES:
            lines, pairs = V.parse_voynich(f); d = V.both(lines, pairs, np.random.default_rng(SEED))['Dc']
            Vd[k] = dict(delta=d['delta'], lines=d['lines']); print(k, Vd[k], flush=True)
        res = gj.get()
    G = {}
    for g, s, r in sorted(res, key=lambda x: (x[0], x[1])):
        if r is not None and len(G.setdefault(g, {})) < GROUPS[g][2]: G[g][s] = r
    ref = {g: np.array([v[0] for v in G[g].values()]) for g in G}
    n = {g: len(G[g]) for g in G}; print('valid runs', n, flush=True)
    p1 = lambda v: float((1 + (ref['ref_default'] <= v).sum()) / (len(ref['ref_default']) + 1))
    p2 = lambda v: float((1 + (ref['ref_spp0'] >= v).sum()) / (len(ref['ref_spp0']) + 1))
    gates = dict(H1_fpr=int(sum(p1(v) <= ALPHA for v in ref['ho_default'])), H1_power=int(sum(p1(v) <= ALPHA for v in ref['ho_spp0'])),
                 H2_fpr=int(sum(p2(v) <= ALPHA for v in ref['ho_spp0'])), H2_power=int(sum(p2(v) <= ALPHA for v in ref['ho_default'])))
    ok = dict(H1=gates['H1_fpr'] <= 2 and gates['H1_power'] >= 16 and n['ref_default'] == 100 and n['ho_default'] == 20 and n['ho_spp0'] == 20,
              H2=gates['H2_fpr'] <= 2 and gates['H2_power'] >= 16 and n['ref_spp0'] == 100 and n['ho_default'] == 20 and n['ho_spp0'] == 20)
    P = {f'{h}_{k}': (p1 if h == 'H1' else p2)(Vd[k]['delta']) for h in ('H1', 'H2') for k, _ in V.FILES}
    tests = [t for t in P if ok[t[:2]]]; rej = holm([P[t] for t in tests]); Hm = dict(zip(tests, map(bool, rej)))
    def verdict(h):
        if not ok[h]: return 'NOT TESTABLE'
        m = sum(Hm.get(f'{h}_{k}', False) for k, _ in V.FILES); return 'SUPPORTED' if m == 2 else 'PARTIAL' if m == 1 else 'NOT DETECTED'
    ver = {h: verdict(h) for h in ('H1', 'H2')}
    if ver['H1'] == ver['H2'] == 'SUPPORTED': ver['overall'] = 'BETWEEN-SETTINGS'
    summ = {g: dict(n=len(v), min=float(v.min()), q25=float(np.percentile(v, 25)), median=float(np.median(v)), q75=float(np.percentile(v, 75)), max=float(v.max()))
            for g, v in ref.items()}
    xs = [0, 7, 14, 21, 28]; ys = [summ['ref_spp0']['median'], summ['dose7']['median'], summ['dose14']['median'], summ['dose21']['median'], summ['ref_default']['median']]
    cross = {}
    for k in Vd:
        v = Vd[k]['delta']; c = None
        for i in range(4):
            if (ys[i] - v) * (ys[i + 1] - v) <= 0 and ys[i] != ys[i + 1]: c = xs[i] + (v - ys[i]) / (ys[i + 1] - ys[i]) * 7; break
        cross[k] = c
    out = dict(seed=SEED, nlines=NLINES, voynich=Vd, valid=n, seeds_used={g: sorted(G[g]) for g in G}, ref_values={g: [float(x) for x in ref[g]] for g in ref},
               summary=summ, gates=gates, gate_ok=ok, p=P, holm=Hm, verdict=ver, dose=dict(spp=xs, median=ys, crossing=cross), runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C069_results.json', 'w'), indent=1)
    for k in ('voynich', 'summary', 'gates', 'gate_ok', 'p', 'holm', 'verdict', 'dose', 'runtime_s'): print(k, json.dumps(out[k]))

if __name__ == '__main__':
    main()
