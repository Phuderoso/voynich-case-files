#!/usr/bin/env python3
"""C062 — F-LABEL step 2 (repair of C061): is a label word more likely to occur in its own page's running text than
FREQUENCY-MATCHED decoy words from the same section?  Each label w (>= 3 units) on page p, section s, with section running-text
count f_w >= 1, is compared with the decoy bin B(w) = distinct words of s's running text with the same count bin
(exact 1,2,3,4; then 5-8, 9-16, 17-32, ...), w excluded. Page size, page vocabulary and label count are held fixed because
labels and decoys are scored on the same page.
H1: T1 = sum_w [ h_own(w) - mean_{d in B(w)} h_own(d) ].
H2 (page-specific vs drift): T2 = sum_w [ c(w) - mean_d c(d) ], c = h_own - mean over bound neighbours (prev/next section page).
Null: each label replaced by a uniform draw from its bin (20000 draws); one-sided p; alpha 0.025 each; ZL 3b primary, IT2a replication.
Gates (same model as the null): FPR = 200 fake-label sets, each label drawn from its bin; power = same but each label slot,
with prob 0.10, is drawn from the bin words present on its own page (when any). Bars FPR <= 0.05, power >= 0.80.
Labels with f_w = 0 (never in the section's text) cannot be scored and are counted separately (descriptive).
Pre-registered in case-file/C062-label-decoys.md. Seed 6262.   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c061_labels_in_text as L
import c003_position_rigidity as T

SEED, NNULL, NREP, ALPHA, QPLANT = 6262, 20000, 200, 0.025, 0.10

def binof(f): return f if f <= 4 else 4 + int(np.ceil(np.log2(f))) - 2

def build(path):
    sect, tp, lp, txt, lab = L.parse(path); vocs = {p: set(txt[p]) for p in tp}; items = []; unscored = 0
    for p in lp:
        s = sect[p]; sec = [q for q in tp if sect[q] == s]; k = sec.index(p); nb = [sec[x] for x in (k - 1, k + 1) if 0 <= x < len(sec)]
        cnt = Counter(w for q in sec for w in txt[q] if len(T.units(w)) >= 3); bins = {}
        for w, f in cnt.items(): bins.setdefault(binof(f), []).append(w)
        for w in sorted(lab[p]):
            if cnt.get(w, 0) == 0: unscored += 1; continue
            B = [d for d in bins[binof(cnt[w])] if d != w]
            if not B: unscored += 1; continue
            ho = np.array([d in vocs[p] for d in B], float)
            hn = np.array([np.mean([d in vocs[q] for q in nb]) if nb else 0.0 for d in B])
            wo = float(w in vocs[p]); wn = float(np.mean([w in vocs[q] for q in nb])) if nb else 0.0
            items.append(dict(page=p, w=w, B=B, ho=ho, c=ho - hn, wo=wo, wc=wo - wn, has_nb=bool(nb)))
    return items, unscored

def stats(items, choice=None):
    """choice: None = real labels; else list of indices into each bin (fake labels)."""
    t1 = t2 = 0.0
    for i, it in enumerate(items):
        o, c = (it['wo'], it['wc']) if choice is None else (it['ho'][choice[i]], it['c'][choice[i]])
        t1 += o - it['ho'].mean(); t2 += c - it['c'].mean()
    return t1, t2

def null(items, rng):
    n1 = np.zeros(NNULL); n2 = np.zeros(NNULL)
    for it in items:
        j = rng.integers(len(it['B']), size=NNULL); n1 += it['ho'][j] - it['ho'].mean(); n2 += it['c'][j] - it['c'].mean()
    return n1, n2

def pval(x, n): return float((1 + (n >= x - 1e-12).sum()) / (len(n) + 1))

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); R = dict(seed=SEED)
    items, uns = build('data/ZL3b-n.txt'); n1, n2 = null(items, rng); g = {}
    for mode in ('fpr', 'power'):
        r1 = r2 = 0
        for _ in range(NREP):
            ch = []
            for it in items:
                pos = np.where(it['ho'] > 0)[0]
                ch.append(int(rng.choice(pos)) if mode == 'power' and len(pos) and rng.random() < QPLANT else int(rng.integers(len(it['B']))))
            a, b = stats(items, ch); r1 += pval(a, n1) <= ALPHA; r2 += pval(b, n2) <= ALPHA
        g[mode] = dict(H1=r1 / NREP, H2=r2 / NREP); print(mode, g[mode], round(time.time() - t0, 1), flush=True)
    g['ok_H1'] = bool(g['fpr']['H1'] <= 0.05 and g['power']['H1'] >= 0.8); g['ok_H2'] = bool(g['fpr']['H2'] <= 0.05 and g['power']['H2'] >= 0.8)
    R['gates'] = g
    for name, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        it, un = build(f); m1, m2 = null(it, rng); a, b = stats(it)
        R[name] = dict(n_scored=len(it), n_unscored=un, T1=a, p_H1=pval(a, m1), T2=b, p_H2=pval(b, m2),
                       own_hits=int(sum(x['wo'] for x in it)), decoy_expected=float(sum(x['ho'].mean() for x in it)),
                       hit_words=sorted(f"{x['page']}:{x['w']}" for x in it if x['wo']))
        print(name, {k: v for k, v in R[name].items() if k != 'hit_words'}, round(time.time() - t0, 1), flush=True)
    z = R['ZL3b']
    R['verdict'] = dict(H1='NOT TESTABLE' if not g['ok_H1'] else ('EXCESS' if z['p_H1'] <= ALPHA else 'NO EXCESS'),
                        H2='NOT TESTABLE' if not g['ok_H2'] else ('PAGE-SPECIFIC' if z['p_H2'] <= ALPHA else 'NOT PAGE-SPECIFIC'))
    R['runtime_s'] = round(time.time() - t0, 1); json.dump(R, open('analysis/C062_results.json', 'w'), indent=1, default=float)
    print(R['verdict'], R['runtime_s'])

if __name__ == '__main__': main()
