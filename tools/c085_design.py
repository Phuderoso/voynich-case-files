#!/usr/bin/env python3
"""C085 design step (I-119 gate self-calibration, after Kryptos): BEFORE any C085 run, simulate the pre-registered TOST
rule and gates on exchangeable draws, using only PRECISION numbers already published (never the manuscript's K value):
  sd_ms = mean half-sample sd_d of the two manuscript transcriptions in C082 (0.0083); sd_hold = median sd_d of C082
  held-out generator runs (their within-run spread); sd_gen_run = between-run SD of K of the C005 configuration itself,
  measured here on 35 SPENT seeds 11286-11320 (used in C084 for topic statistics only, never for K; design data, not
  reused for any test).  A first draft used C083's winner-cell SD (0.0057, wrong configuration); the smoke run on the
  reserved seed 11999 (K 0.133) showed the C005 configuration may vary more, so the SD is measured on its own runs.
Margin menu {0.010, 0.015, 0.020, 0.025, 0.030}; chosen margin = smallest with simulated power >= 0.80 for a manuscript-
like text whose true K equals the generator mean, subject to the substantive cap Delta <= 0.033 (half the C083 training
gap between the default-like cell 0, K 0.170, and the C005 cell 64, K 0.103). Normal approximation; seed 8585.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import json, numpy as np
r82 = json.load(open('analysis/C082_results.json'))
sd_ms = float(np.mean([r82['results'][v]['sd_d'] for v in ('Voynich_ZL3b', 'Voynich_IT2a')]))
sd_hold = float(np.median([v['sd_d'] for v in r82['holdout'].values()]))
import os, sys
for v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS'): os.environ[v] = '1'
sys.path.insert(0, os.path.dirname(__file__))
from multiprocessing import Pool
import c085_equivalence as E
def kjob(s):
    Lg = E.G.generate(E.c005cfg(), s); ws = [E.D.T.units(w) for w in E.G.flat(Lg or [])][:E.D.N]
    return s, (E.analyse(f'design_{s}', ws, boot=False)[1]['K'] if len(ws) >= E.D.N else None)
if __name__ != '__main__': raise SystemExit
with Pool(7) as pool: DK = dict(pool.map(kjob, range(11286, 11321)))
ks = np.array([k for k in DK.values() if k is not None]); sd_gen = float(ks.std(ddof=1))
json.dump(dict(design_seeds=list(range(11286, 11321)), K=DK, sd=sd_gen, mean=float(ks.mean())), open('analysis/C085_design.json', 'w'), indent=1)
print(f'design runs {len(ks)}/35 usable; between-run SD {sd_gen:.4f}; range {ks.min():.4f}-{ks.max():.4f} (mean not used by the rule: {ks.mean():.4f})')
NREF, Z = 40, 1.645; se = sd_gen / np.sqrt(NREF)
rng = np.random.default_rng(8585); M = 200000
def rate(sd_x, delta, true_d):
    d = true_d + rng.normal(0, sd_x, M) + rng.normal(0, se, M)       # estimate of K_X - mean_gen
    lo, hi = d - Z * sd_x - Z * se, d + Z * sd_x + Z * se
    eq = (lo >= -delta) & (hi <= delta); beyond = (hi < -delta) | (lo > delta)
    return float(eq.mean()), float(beyond.mean())
print(f'sd_ms {sd_ms:.4f}  sd_hold {sd_hold:.4f}  sd_gen_between_runs {sd_gen:.4f}  se_mean(40) {se:.4f}')
print('margin  P(EQUIV|ms-like,d=0)  P(EQUIV|held-out gen,d~N(0,sd_gen))  P(BEYOND|held-out)  P(EQUIV|d=0.05)  P(BEYOND|d=0.05)')
choice = None
for delta in (0.010, 0.015, 0.020, 0.025, 0.030):
    pe, _ = rate(sd_ms, delta, 0.0)
    hd = rng.normal(0, sd_gen, M); dd = hd + rng.normal(0, se, M)   # a held-out run: its own K deviates by between-run spread
    lo, hi = dd - Z * sd_hold - Z * se, dd + Z * sd_hold + Z * se
    he = float(((lo >= -delta) & (hi <= delta)).mean()); hb = float(((hi < -delta) | (lo > delta)).mean())
    fe, fb = rate(sd_hold, delta, 0.05)
    print(f'{delta:.3f}   {pe:.3f}                 {he:.3f}                                {hb:.4f}              {fe:.4f}          {fb:.3f}')
    if choice is None and pe >= 0.80 and delta <= 0.033: choice = delta
print('CHOSEN MARGIN', choice)
from math import comb
p = rate(sd_ms, choice, 0.0)[0]
print('P(both transcriptions EQUIV | d=0), assuming independence (lower bound-ish):', round(p * p, 3))
