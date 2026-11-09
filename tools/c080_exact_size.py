#!/usr/bin/env python3
"""C080 (F-PARA audit, step 2): exact-size check of the C078 length-matched permutation test with known-answer controls.
Fresh true-null replicates (seed 8080, never used before): (a) line-shuffled real paragraphs, Currier B, word sets W0 and
W2, IT2a and ZL 3b, 300 replicates each (1,200); (b) a fully synthetic corpus: lines drawn i.i.d. with replacement from the
ZL/B/W0 line pool into the observed paragraph shapes, 200 replicates.  Each replicate: C078 test with RG = 200
permutations -> p = (1+b)/201, attainable size at alpha 0.05 = 10/201.
H1 (primary, pooled a+b, n = 1,400): one-sided exact binomial test of #(p <= 10/201) against 10/201 -> INFLATED if
p_binom <= 0.05, else CALIBRATED.  Known-answer control (required): on the same replicates the rule p <= 13/201 has exact
size 13/201 = 6.47% under a valid test (the size C078+C079 suggested); it must be flagged INFLATED against 10/201 by the
same binomial test, else H1 is NOT TESTABLE.  Analytic power of that control is reported.
Near-tie check: for every replicate, count permuted statistics within 1e-9 (absolute) of the observed one.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from math import lgamma, log, exp, sqrt
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c078_paragraph_lenmatched as E
SEED, RG, NA, NB = 8080, 200, 300, 200
A0, A1 = 10 / 201, 13 / 201

def bsf(x, n, p):
    return float(min(1.0, sum(exp(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * log(p) + (n - i) * log(1 - p)) for i in range(x, n + 1))))

def test(ps, rng):
    P = E.build(ps); obs = E.stat(P); null = np.array([E.stat(P, [rng.permutation(len(l)) for l in P]) for _ in range(RG)])
    return int((null >= obs).sum()), int((np.abs(null - obs) <= 1e-9).sum())

def job_a(a):
    k, ws, i = a
    rng = np.random.default_rng([SEED, i, 0 if k == 'IT2a' else 1, int(ws[1])])
    return 'a', f'{k}_B_{ws}', *test(E.shuffled(E.subset(k, 'B', ws), rng), rng)

def job_b(i):
    rng = np.random.default_rng([SEED, i, 77]); ps = E.subset('ZL3b', 'B', 'W0')
    pool = [l for p in ps for l in p['lines']]
    syn = [dict(p, lines=[pool[rng.integers(len(pool))] for _ in p['lines']]) for p in ps]
    return 'b', 'SYN_ZL3b_B_W0', *test(syn, rng)

def main():
    t0 = time.time()
    with Pool(8) as pool:
        rb = pool.map_async(job_b, range(NB))
        ra = pool.map(job_a, [(k, w, i) for k in E.FILES for w in ('W0', 'W2') for i in range(NA)], chunksize=4)
        res = ra + rb.get()
    json.dump(res, open('analysis/C080_raw.json', 'w'))
    p = np.array([(1 + b) / (RG + 1) for _, _, b, _ in res]); n = len(p)
    x0 = int((p <= A0 + 1e-12).sum()); x1 = int((p <= A1 + 1e-12).sum())
    pb0, pb1 = bsf(x0, n, A0), bsf(x1, n, A0)
    xc = int(next(k for k in range(n + 1) if bsf(k, n, A0) <= 0.05)); power = bsf(xc, n, A1)
    per = {}
    for part, c, b, t in res:
        d = per.setdefault(c, dict(n=0, rej=0, near_ties=0)); d['n'] += 1; d['rej'] += (1 + b) / (RG + 1) <= A0 + 1e-12; d['near_ties'] += t
    ctrl = pb1 <= 0.05
    verdict = 'NOT TESTABLE' if not ctrl else 'INFLATED' if pb0 <= 0.05 else 'CALIBRATED'
    out = dict(seed=SEED, RG=RG, n=n, H1=dict(rejections=x0, rate=x0 / n, size=A0, binom_p=pb0),
               control=dict(rule='p <= 13/201', rejections=x1, rate=x1 / n, binom_p_vs_10_201=pb1, detected=ctrl,
                            critical_count=xc, analytic_power=power),
               per_config=per, total_near_ties=sum(t for *_, t in res), verdict=verdict, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C080_results.json', 'w'), indent=1); print(json.dumps(out, indent=1))

if __name__ == '__main__':
    main()
