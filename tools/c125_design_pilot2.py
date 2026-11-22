#!/usr/bin/env python3
"""C125 DESIGN PILOT part 2 (controls only, no manuscript glyph or word statistic). Additive line-pair overlap instrument:
O(d) = mean over same-page line pairs (i, i+d) of |types(i) & types(i+d)| / sqrt(|types(i)| |types(i+d)|), d = 1..8.
Shows the distance profile each plant produces (C124 drift plant DR(lam), C121 copy plant) on 2 controls recut into the CB ZL3b
template, and the observed-arrangement DiD on this additive scale: D_front = O_F(1) - O_F(2) on internal block boundaries,
D_int = same contrast inside blocks (2->3 minus 1->3), DiD = D_front - D_int. Seed 11861 (next free 11862).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c124_mi_flip as C4
from c120_mi_distance import recut
from c121_mi_calibrated import plant, controls
import c123_mi_para_block as C3
SEED, NREP = 11861, 20
def ov(a, b):
    a, b = set(a), set(b)
    return len(a & b) / np.sqrt(len(a) * len(b)) if a and b else np.nan
def profile(pages):
    O = {d: [] for d in range(1, 9)}; F1, F2, I1, I2 = [], [], [], []
    for p in pages:
        for d in O:
            O[d] += [ov(p[i], p[i + d]) for i in range(len(p) - d)]
        h, bs, t = C3.blocks_of(len(p), 0); nb = len(bs)
        for s in range(1, nb - 2):
            b0, b1 = bs[s], bs[s + 1]
            F1.append(ov(p[b0 + 3], p[b1])); F2.append(ov(p[b0 + 2], p[b1])); I1.append(ov(p[b0 + 2], p[b0 + 3])); I2.append(ov(p[b0 + 1], p[b0 + 3]))
    m = lambda v: float(np.nanmean(v))
    Df = m(F1) - m(F2); Di = m(I1) - m(I2)
    return dict(O={d: m(v) for d, v in O.items()}, Df=Df, Di=Di, DiD=Df - Di, n_boundaries=len(F1))
CONDS = [('none', None), ('DR0.35', ('dr', 0.35)), ('DR0.75', ('dr', 0.75)), ('DR1.0', ('dr', 1.0)), ('copy1.0x4', ('cp', (1.0, 4))), ('copy1.0x99', ('cp', (1.0, 99)))]
D = C3.pages_of('data/ZL3b-n.txt', 'CB'); pages, pids = C3.split_pp(D)
ctl = [c for c in controls() if c[0] in ('Latin Caesar', 'Spanish Cervantes')]; out = {}
for ci, (name, words, eva) in enumerate(ctl):
    base = recut(words, pages)
    for k, (cn, kind) in enumerate(CONDS):
        rs = []
        for r in range(NREP):
            rng = np.random.default_rng([SEED, ci, k, r]); ps = C4.pseudo_flip(base, rng)
            if kind and kind[0] == 'dr': ps = C4.plant_drift(ps, rng, kind[1])
            if kind and kind[0] == 'cp': ps = plant(ps, rng, *kind[1])
            rs.append(profile(ps))
        O = {d: float(np.mean([x['O'][d] for x in rs])) for d in range(1, 9)}
        did = [x['DiD'] for x in rs]
        out[f'{name} | {cn}'] = dict(O=O, O1_minus_O2=O[1] - O[2], O2_minus_O8=O[2] - O[8], DiD_mean=float(np.mean(did)), DiD_sd=float(np.std(did, ddof=1)),
                                     DiD_z_of_mean=float(np.mean(did) / (np.std(did, ddof=1) / np.sqrt(NREP))), n_boundaries=rs[0]['n_boundaries'])
        o = out[f'{name} | {cn}']
        print(f"{name:18s} {cn:10s} O1 {O[1]:.4f} O2 {O[2]:.4f} O4 {O[4]:.4f} O8 {O[8]:.4f} | O1-O2 {o['O1_minus_O2']:+.4f} O2-O8 {o['O2_minus_O8']:+.4f} | DiD {o['DiD_mean']:+.4f} (sd {o['DiD_sd']:.4f}, z {o['DiD_z_of_mean']:+.2f}) nb {o['n_boundaries']}", flush=True)
json.dump(dict(seed=SEED, NREP=NREP, summary=out), open('analysis/C125_design_pilot2.json', 'w'), indent=1)
