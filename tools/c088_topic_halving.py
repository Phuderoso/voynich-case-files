#!/usr/bin/env python3
"""C088 (F-TOPIC step 2): does the C084 W1 -> W2 drop in page topicality (X 0.55 -> 0.21, ZL 3b) survive when
Currier language and page size are held fixed?
Units: pages of the C084 windows (W1 f1r-f79v, W2 f86v6-f116r; >= 40 paragraph tokens), each TRUNCATED to its first
lines until >= T = 80 tokens (pages that never reach 80 are dropped).  Strata: Currier A and Currier B ($L in ZL 3b /
IT2a headers), tested separately.  X(set) = G - mean G over R_IN = 4 line-reassignment draws inside the set
(C084's PLSA K 8, EPS 0.1, 150 iterations; odd lines fit, even lines scored).
Statistic: D = X(W1 pages of the stratum) - X(W2 pages of the stratum).
Null (covariate-matched, structure-preserving): window labels permuted among the pages of the SAME stratum (group sizes
kept; every page keeps its lines and its truncation), R_PERM = 199; two-sided p = min(1, 2 min(p_hi, p_lo)), floor 0.01.
Family: {A, B} x {ZL 3b, IT2a} = 4 tests, Holm 0.05.
Gates (ZL 3b only, on the real pooled pages of each stratum, random pseudo-labels with the real group sizes):
  FPR  : 5 pseudo-label replicates per stratum (R_PERM 99): false calls at p <= 0.05 <= 1/10 overall.
  PLANT: 5 replicates per stratum (R_PERM 199): in the pseudo-'W2' group a fraction F_PLANT = 0.3 of the lines of each
         page is swapped with lines of other pseudo-'W2' pages (expected own-page share ~0.7^2 ~ half the topical gain);
         detection = D > 0 and p <= 0.0125 (first Holm step); pass >= 4/5 in each stratum, else that stratum NOT TESTABLE.
Descriptive only: truncated windows with both languages pooled, X with R_IN 19 (no test).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'): os.environ[_v] = '1'
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c084_page_topics import ms_windows, plsa_gain, reassign, holm

SEED, T, R_IN, R_PERM, R_GATE_FPR, F_PLANT = 8888, 80, 4, 199, 99, 0.3
N_FPR, N_PLANT, ALPHA1 = 5, 5, 0.0125

def trunc(p):
    out, t = [], 0
    for l in p:
        out.append(l); t += len(l)
        if t >= T: return out
    return None

def xval(pages, seed, r_in=R_IN):
    rng = np.random.default_rng([seed, 1])
    g = plsa_gain(pages, np.random.default_rng([seed, 0]))
    nl = [plsa_gain(reassign(pages, rng), np.random.default_rng([seed, 2, i])) for i in range(r_in)]
    return g - float(np.mean(nl))

def delta(args):
    tid, k, pages, lab, seed = args  # lab: boolean array, True = 'W1'
    a = [p for p, b in zip(pages, lab) if b]; b = [p for p, x in zip(pages, lab) if not x]
    return tid, k, xval(a, seed * 3 + 1) - xval(b, seed * 3 + 2)

def dilute(pages, lab, rng, f):
    """swap a fraction f of the lines of every pseudo-W2 page with lines of other pseudo-W2 pages (pool permutation)"""
    idx = [i for i, x in enumerate(lab) if not x]
    slots = [(i, j) for i in idx for j in range(len(pages[i])) if rng.random() < f]
    out = [list(p) for p in pages]
    src = [pages[i][j] for i, j in slots]; perm = rng.permutation(len(src))
    for (i, j), s in zip(slots, perm): out[i][j] = src[s]
    return out

def strata(path):
    win, pages, lang, sect = ms_windows(path); S = {}
    for L in 'AB':
        ps, lab, names = [], [], []
        for w in ('W1', 'W2'):
            for p in win[w]:
                if lang.get(p) != L: continue
                tp = trunc(pages[p])
                if tp: ps.append(tp); lab.append(w == 'W1'); names.append(p)
        S[L] = (ps, np.array(lab), names)
    pooled = {w: [trunc(pages[p]) for p in win[w] if trunc(pages[p])] for w in win}
    return S, pooled

def main():
    t0 = time.time(); out = dict(seed=SEED, T=T, R_IN=R_IN, R_PERM=R_PERM, F_PLANT=F_PLANT)
    SZ, poolZ = strata('data/ZL3b-n.txt'); SI, poolI = strata('data/IT2a-n.txt')
    jobs, tests = [], {}
    def add(tid, pages, lab, R, rng, s0):
        tests[tid] = dict(n_W1=int(lab.sum()), n_W2=int((~lab).sum()), R=R)
        jobs.append((tid, -1, pages, lab, s0))
        for k in range(R): jobs.append((tid, k, pages, rng.permutation(lab), s0 + 1000 + k))
    rng = np.random.default_rng(SEED)
    for tr, S in (('ZL3b', SZ), ('IT2a', SI)):
        for L in 'AB':
            ps, lab, names = S[L]; add(f'{tr}_{L}', ps, lab, R_PERM, rng, SEED * 100 + len(tests) * 10000)
            out.setdefault('pages', {})[f'{tr}_{L}'] = dict(W1=[n for n, b in zip(names, lab) if b], W2=[n for n, b in zip(names, lab) if not b])
    for L in 'AB':
        ps, lab, _ = SZ[L]
        for i in range(N_FPR):
            pl = rng.permutation(lab); add(f'fpr_{L}_{i}', ps, pl, R_GATE_FPR, rng, SEED * 100 + len(tests) * 10000)
        for i in range(N_PLANT):
            pl = rng.permutation(lab); dp = dilute(ps, pl, rng, F_PLANT)
            add(f'plant_{L}_{i}', dp, pl, R_PERM, rng, SEED * 100 + len(tests) * 10000)
    print('jobs', len(jobs), flush=True)
    with Pool(8) as pool:
        desc = pool.starmap(xval, [(poolZ[w], SEED + 7 + i, 19) for i, w in enumerate(('W1', 'W2'))] +
                            [(poolI[w], SEED + 9 + i, 19) for i, w in enumerate(('W1', 'W2'))])
        res = {}
        for n, (tid, k, d) in enumerate(pool.imap_unordered(delta, jobs, chunksize=4)):
            res.setdefault(tid, {})[k] = d
            if n % 2000 == 0: print('done', n, round(time.time() - t0, 1), flush=True)
    for tid, r in res.items():
        obs = r[-1]; nl = np.array([r[k] for k in range(tests[tid]['R'])]); R = len(nl)
        phi = (1 + (nl >= obs).sum()) / (R + 1); plo = (1 + (nl <= obs).sum()) / (R + 1)
        tests[tid].update(D=float(obs), null_mean=float(nl.mean()), null_sd=float(nl.std(ddof=1)),
                          p=float(min(1.0, 2 * min(phi, plo))))
    out['descriptive_pooled_truncated'] = dict(ZL3b=dict(W1=desc[0], W2=desc[1]), IT2a=dict(W1=desc[2], W2=desc[3]))
    main4 = ['ZL3b_A', 'IT2a_A', 'ZL3b_B', 'IT2a_B']; rej = holm([tests[m]['p'] for m in main4])
    for m, r_ in zip(main4, rej): tests[m]['holm_reject'] = bool(r_)
    fp = sum(tests[t]['p'] <= 0.05 for t in tests if t.startswith('fpr_'))
    pw = {L: sum(tests[t]['D'] > 0 and tests[t]['p'] <= ALPHA1 for t in tests if t.startswith(f'plant_{L}_')) for L in 'AB'}
    g_fpr = fp <= 1; g_pw = {L: pw[L] >= 4 for L in 'AB'}
    verdict = {}
    for L in 'AB':
        z, i = tests[f'ZL3b_{L}'], tests[f'IT2a_{L}']
        if not (g_fpr and g_pw[L]): verdict[L] = 'NOT TESTABLE (gate)'
        elif z['holm_reject'] and i['holm_reject'] and z['D'] > 0 and i['D'] > 0: verdict[L] = 'DETECTED (W1 > W2 within language)'
        elif z['holm_reject'] and i['holm_reject'] and z['D'] < 0 and i['D'] < 0: verdict[L] = 'DETECTED REVERSED (W2 > W1)'
        elif z['holm_reject'] or i['holm_reject']: verdict[L] = 'SPLIT (transcription-dependent)'
        else: verdict[L] = 'NOT DETECTED'
    out.update(tests=tests, gates=dict(FPR=f'{fp}/{2 * N_FPR}', FPR_pass=g_fpr, plant={L: f'{pw[L]}/{N_PLANT}' for L in 'AB'},
               plant_pass=g_pw), verdict=verdict, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C088_results.json', 'w'), indent=1)
    for t in tests: print(t, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in tests[t].items()})
    print('descriptive', out['descriptive_pooled_truncated'])
    print('gates', out['gates']); print('verdict', verdict); print('runtime', out['runtime_s'])

if __name__ == '__main__':
    main()
