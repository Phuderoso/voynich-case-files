#!/usr/bin/env python3
"""C079 (F-PARA audit): is the 20-replicate false-positive gate of C076/C078 calibrated?  C078 saw 20 null firings in 240
gate replicates (8.3% vs nominal 5%).  Here: for each of C078's 12 configurations ({W0,W1,W2} x {A,B} x {IT2a,ZL}) draw
NR = 100 fresh true-null pseudo replicates (lines permuted within paragraph, as C078 gates) and compute the C078
length-matched permutation p (RG = 200).  H1 (primary): pooled null rejection rate at alpha 0.05 over 1200 replicates;
one-sided exact binomial test against 0.05 -> INFLATED if p_binom <= 0.05, else CALIBRATED.  Positive control (must work
or the audit is NOT TESTABLE): a deliberately wrong null that permutes interior *words* among the lines of a paragraph
(ignores line-level clustering) on ZL/B/W0, NR = 100 -> must be INFLATED.  Secondary (descriptive): per-config counts,
chi-square heterogeneity statistic (df 11; critical 19.68 at 0.05), KS of p against U(0,1); the forward rule for 40-replicate gates (FPR <= 4/40) evaluated on these
nulls: P(fail | calibrated) vs 20-replicate rule.  C078 verdicts are not revised by this cycle.  Seed 7979.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from collections import Counter
from multiprocessing import Pool
import numpy as np
from math import lgamma, log, sqrt, exp

def bsf(x, n, p):  # P(X >= x)
    return float(min(1.0, sum(exp(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * log(p) + (n - i) * log(1 - p)) for i in range(x, n + 1))))

def wilson(x, n, z=1.96):
    ph = x / n; d = 1 + z * z / n; c = (ph + z * z / (2 * n)) / d; h = z * sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return [c - h, c + h]

def ks_uniform(v):
    v = np.sort(v); n = len(v); i = np.arange(1, n + 1)
    D = float(max((i / n - v).max(), (v - (i - 1) / n).max())); t = (sqrt(n) + 0.12 + 0.11 / sqrt(n)) * D
    return D, float(min(1.0, max(0.0, 2 * sum((-1)**(j - 1) * exp(-2 * j * j * t * t) for j in range(1, 101)))))
sys.path.insert(0, os.path.dirname(__file__))
import c078_paragraph_lenmatched as E
C = E.C
SEED, NR, RG, ALPHA = 7979, 100, 200, 0.05

def null_job(a):
    k, lang, ws, i = a
    rng = np.random.default_rng([SEED, i, 0 if k == 'IT2a' else 1, 0 if lang == 'A' else 1, int(ws[1])])
    sh = E.shuffled(E.subset(k, lang, ws), rng)
    return k, lang, ws, E.ptest(E.build(sh), rng, RG)[1]

def wordperm(ps, rng):
    out = []
    for p in ps:
        ints = [w for l in p['lines'] if len(l) > 4 for w in l[2:-2]]; rng.shuffle(ints); it = iter(ints)
        out.append(dict(p, lines=[l[:2] + [next(it) for _ in l[2:-2]] + l[-2:] if len(l) > 4 else l for l in p['lines']]))
    return out

def ctrl_job(i):
    rng = np.random.default_rng([SEED, i, 99]); sh = E.shuffled(E.subset('ZL3b', 'B', 'W0'), rng)
    obs = E.stat(E.build(sh)); null = [E.stat(E.build(wordperm(sh, rng))) for _ in range(RG)]
    return float((1 + sum(v >= obs for v in null)) / (RG + 1))

def main():
    t0 = time.time(); cfg = [(k, l, w) for k in E.FILES for l in ('A', 'B') for w in E.EXCL]
    with Pool(8) as pool:
        cj = pool.map_async(ctrl_job, range(NR))
        res = pool.map(null_job, [c + (i,) for c in cfg for i in range(NR)], chunksize=4)
        cp = cj.get()
    json.dump(dict(null=res, control=cp), open('analysis/C079_raw_pvalues.json', 'w'))
    P = {}
    for k, l, w, p in res: P.setdefault(f'{k}_{l}_{w}', []).append(p)
    allp = np.array([p for v in P.values() for p in v]); n = len(allp); x = int((allp <= ALPHA).sum())
    pb = bsf(x, n, ALPHA)
    cx = int(sum(p <= ALPHA for p in cp)); cpb = bsf(cx, NR, ALPHA)
    per = {c: int(sum(p <= ALPHA for p in v)) for c, v in P.items()}
    cnt = np.array(list(per.values()), float); e = cnt.mean(); chi = float(((cnt - e)**2 / e).sum()) if e else None
    D, kp = ks_uniform(allp); rate = x / n
    f20, f40, f20n, f40n = bsf(3, 20, rate), bsf(5, 40, rate), bsf(3, 20, ALPHA), bsf(5, 40, ALPHA)
    ctrl_ok = cpb <= ALPHA
    verdict = 'NOT TESTABLE' if not ctrl_ok else ('INFLATED' if pb <= ALPHA else 'CALIBRATED')
    out = dict(seed=SEED, NR=NR, RG=RG, pooled=dict(n=n, rejections=x, rate=rate, binom_p=pb,
               ci95_wilson=wilson(x, n)), per_config=per,
               heterogeneity_chi2=dict(stat=chi, df=len(cnt) - 1),
               ks_uniform=dict(D=D, p_asymptotic=kp),
               control=dict(rejections=cx, n=NR, binom_p=cpb, passed=ctrl_ok),
               gate_fail_prob=dict(rule20_at_observed=f20, rule40_at_observed=f40, rule20_nominal=f20n, rule40_nominal=f40n),
               verdict=verdict, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C079_results.json', 'w'), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == '__main__':
    main()
