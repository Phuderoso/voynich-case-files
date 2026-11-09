#!/usr/bin/env python3
"""C073 (F-LINE step 7): word-2 sh boost with a matched baseline (previous word's ending), after C072's disclosed design flaw.
Slots = positions 2..n-2 of paragraph lines with >= 5 clean words (C070 parse). Each slot has a class c = 1 if the previous word
ends in 'y' else 0, and a flag = slot word is sh-initial.
D_m = sum_c (N2_c/N2) * (sh share at word 2 in class c - sh share at mid slots 3..n-2 in class c).
Null: conditional permutation of flags among slots of the same line AND the same class (word 1 and last two words untouched,
class labels fixed). Exact per-stratum Bernoulli shortcut as in C070, R = 4000, one-sided.
Tests: {Q20, Currier A, Currier B outside Q20} x {IT2a, ZL} = 6, Holm alpha 0.05. Gates: FPR <= 2/20 on within-stratum
shuffles, power >= 16/20 with a 10% within-stratum planted swap. Verdict per subset: REPLICATED (both), PARTIAL, NOT DETECTED,
NOT TESTABLE.
Generator: 40 default Timm-Schinner runs (seeds 10701-10740, 1,500 lines). ABOVE GENERATOR if the manuscript's B-outside-Q20
D_m exceeds every run in both transcriptions (rank p 1/41 = 0.024); generator FPR on 20 runs (10801-10820) reported.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c070_word2_sh as W
from c004_generator_sweep import generate

SEED, R, NG, Q, ALPHA = 7373, 4000, 20, 0.10, 0.05
SUBS = ('Q20', 'A', 'B_noQ20')

def build(word_lines):
    """per line: flags (positions 2..n-2) and classes"""
    out = []
    for ws in word_lines:
        sl = range(1, len(ws) - 2)
        out.append((np.array([ws[i].startswith('sh') for i in sl], bool), np.array([ws[i - 1].endswith('y') for i in sl], int)))
    return out

def stat(X):
    a = np.zeros(2); n2 = np.zeros(2); m = np.zeros(2); nm = np.zeros(2)
    for f, c in X:
        a[c[0]] += f[0]; n2[c[0]] += 1
        np.add.at(m, c[1:], f[1:]); np.add.at(nm, c[1:], 1)
    ok = (n2 > 0) & (nm > 0)
    return float(sum(n2[k] / n2[ok].sum() * (a[k] / n2[k] - m[k] / nm[k]) for k in range(2) if ok[k]))

def perm_test(X, rng):
    obs = stat(X)
    n2 = np.zeros(2); nm = np.zeros(2); mfix = np.zeros(2); probs, cls, ks = [], [], []
    for f, c in X:
        c0 = c[0]; n2[c0] += 1; np.add.at(nm, c[1:], 1)
        same = c == c0; k = int(f[same].sum()); n = int(same.sum())
        mfix += np.bincount(c[1:][~same[1:]], weights=f[1:][~same[1:]], minlength=2)
        probs.append(k / n); cls.append(c0); ks.append(k)
    probs, cls, ks = np.array(probs), np.array(cls), np.array(ks)
    ok = (n2 > 0) & (nm > 0); null = np.empty(R)
    for r in range(R):
        w2 = rng.random(len(probs)) < probs; s = 0.0
        for k in range(2):
            if not ok[k]: continue
            sel = cls == k; A = w2[sel].sum(); M = mfix[k] + (ks[sel] - w2[sel]).sum()
            s += n2[k] / n2[ok].sum() * (A / n2[k] - M / nm[k])
        null[r] = s
    return obs, float((1 + (null >= obs).sum()) / (R + 1))

def shuffled(X, rng):
    out = []
    for f, c in X:
        g = f.copy()
        for k in (0, 1):
            idx = np.flatnonzero(c == k); g[idx] = rng.permutation(g[idx])
        out.append((g, c))
    return out

def plant(X, rng):
    out = []
    for f, c in X:
        g = f.copy()
        if not g[0] and rng.random() < Q:
            cand = np.flatnonzero((c == c[0]) & g)
            cand = cand[cand > 0]
            if len(cand): g[0] = True; g[cand[rng.integers(len(cand))]] = False
        out.append((g, c))
    return out

def gate(X, seed):
    fp = pw = 0
    for i in range(NG):
        rng = np.random.default_rng(seed * 100 + i); S = shuffled(X, rng)
        fp += perm_test(S, rng)[1] <= ALPHA; pw += perm_test(plant(S, rng), rng)[1] <= ALPHA
    return int(fp), int(pw)

def test_job(a):
    k, sub = a; lines = W.subsets(W.parse(dict(W.FILES)[k]))[sub]; X = build([l['words'] for l in lines])
    d, p = perm_test(X, np.random.default_rng(SEED + SUBS.index(sub)))
    fp, pw = gate(X, SEED + 10 * SUBS.index(sub) + (0 if k == 'IT2a' else 5))
    return k, sub, dict(n_lines=len(X), D_m=d, p=p, fpr=fp, power=pw, gate=fp <= 2 and pw >= 16)

def gen_job(s):
    Lg = generate({'text.lines_to_create': 1500}, s)
    X = build([l for l in (Lg or []) if len(l) >= 5])
    if len(X) < 1000: return s, None, None
    p = perm_test(X, np.random.default_rng(s))[1] if s >= 10801 else None
    return s, stat(X), p

def main():
    t0 = time.time()
    with Pool(8) as pool:
        gj = pool.map_async(gen_job, list(range(10701, 10741)) + list(range(10801, 10821)), chunksize=1)
        T = {f'{k}_{s}': r for k, s, r in pool.map(test_job, [(k, s) for k, _ in W.FILES for s in SUBS], chunksize=1)}
        print('tests', json.dumps(T), flush=True)
        GR = gj.get()
    names = [t for t in T if T[t]['gate']]; ps = [T[t]['p'] for t in names]
    o = np.argsort(ps); rej, stop = {}, False
    for r, i in enumerate(o):
        ok = (not stop) and ps[i] <= ALPHA / (len(ps) - r); rej[names[i]] = bool(ok); stop = stop or not ok
    ver = {}
    for s in SUBS:
        if not all(T[f'{k}_{s}']['gate'] for k, _ in W.FILES): ver[s] = 'NOT TESTABLE'; continue
        m = sum(rej.get(f'{k}_{s}', False) for k, _ in W.FILES); ver[s] = 'REPLICATED' if m == 2 else 'PARTIAL' if m == 1 else 'NOT DETECTED'
    ref = [d for s, d, p in GR if s <= 10740 and d is not None]
    fpr = [p for s, d, p in GR if s >= 10801 and p is not None]
    above = {k: dict(D_m=T[f'{k}_B_noQ20']['D_m'], n_gen_ge=sum(x >= T[f'{k}_B_noQ20']['D_m'] for x in ref),
                     rank_p=(1 + sum(x >= T[f'{k}_B_noQ20']['D_m'] for x in ref)) / (len(ref) + 1)) for k, _ in W.FILES}
    gv = dict(n_ref=len(ref), ref_min=min(ref), ref_max=max(ref), ref_mean=float(np.mean(ref)), above=above,
              gen_fpr=f'{sum(p <= ALPHA for p in fpr)}/{len(fpr)}',
              verdict='ABOVE GENERATOR' if all(v['n_gen_ge'] == 0 for v in above.values()) and len(ref) >= 30 else 'NOT ABOVE')
    out = dict(seed=SEED, tests=T, holm=rej, verdict=ver, generator=gv, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C073_results.json', 'w'), indent=1)
    for k in ('holm', 'verdict', 'generator', 'runtime_s'): print(k, json.dumps(out[k]))

if __name__ == '__main__':
    main()
