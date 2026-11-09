#!/usr/bin/env python3
"""C074 — NEW FAMILY F-JUNC (word junctions): does the end of a word predict the start of the next one, beyond the page's vocabulary?
Lines: C070 parser (paragraph lines, >= 5 clean words). Interior words = positions 2..n-1 (line-first and line-final words excluded,
because both have known position effects: C032/C033/C070). Pairs = adjacent interior words (i, i+1), 2 <= i, i+1 <= n-1.
Units: c003 glyph units. Final unit of word i -> 8 commonest finals + other; initial unit of word i+1 -> 10 commonest initials + other
(classes fixed per dataset from its own counts).
MI = plug-in mutual information (bits) of the final x initial table. Null: shuffle interior words among interior slots of the same page
(page vocabulary and line lengths kept), R = 200. X = MI_obs - mean(MI_null); ratio = MI_obs / mean(MI_null).
Tests: {Currier A, Currier B} x {IT2a, ZL} = 4, one-sided rank p, Holm alpha 0.05. Gates (20 reps each): FPR <= 2/20 on page-shuffled
text; power >= 16/20 with a planted junction rule (q 0.05: for a pair whose first word has final class f, replace the second word by a
random interior word of the same page whose initial class is target(f), a fixed random map, seed-fixed). Verdict per language:
DETECTED (both transcriptions reject), PARTIAL, NOT DETECTED, NOT TESTABLE.
Generator (descriptive, pre-registered criterion): 20 default Timm-Schinner runs (seeds 10901-10920, 1,500 lines, pseudo-pages of 29
lines, lines >= 5 words); ratio compared with the manuscript's Currier B ratio: INSIDE if the manuscript lies within the run range,
ABOVE / BELOW otherwise (both transcriptions). Seed 7474.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from multiprocessing import Pool
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c070_word2_sh as W
import c003_position_rigidity as T3
from c004_generator_sweep import generate

SEED, R, NG, Q, ALPHA = 7474, 200, 20, 0.05, 0.05
KF, KI = 8, 10

class Data:
    def __init__(self, pages):  # pages: list of list of word lists
        self.pages = pages
        fin = Counter(); ini = Counter()
        for p in pages:
            for ws in p:
                for w in ws[1:-1]:
                    u = T3.units(w); fin[u[-1]] += 1; ini[u[0]] += 1
        self.fmap = {u: i for i, (u, _) in enumerate(fin.most_common(KF))}
        self.imap = {u: i for i, (u, _) in enumerate(ini.most_common(KI))}
        # per page: interior word codes (final class, initial class) and slot structure
        self.P = []
        for p in pages:
            codes, bounds = [], []
            for ws in p:
                inner = ws[1:-1]; s = len(codes)
                for w in inner:
                    u = T3.units(w); codes.append((self.fmap.get(u[-1], KF), self.imap.get(u[0], KI)))
                bounds.append((s, len(codes)))
            self.P.append((np.array(codes, int).reshape(-1, 2), bounds))

def mi_from(P_codes):
    tab = np.zeros((KF + 1, KI + 1))
    for codes, bounds in P_codes:
        for s, e in bounds:
            if e - s >= 2: np.add.at(tab, (codes[s:e - 1, 0], codes[s + 1:e, 1]), 1)
    n = tab.sum(); pxy = tab / n; px = pxy.sum(1, keepdims=True); py = pxy.sum(0, keepdims=True)
    nz = pxy > 0
    return float((pxy[nz] * np.log2(pxy[nz] / (px @ py)[nz])).sum())

def shuffle(P, rng):
    return [(codes[rng.permutation(len(codes))], b) for codes, b in P]

def test(P, rng):
    obs = mi_from(P); null = np.array([mi_from(shuffle(P, rng)) for _ in range(R)])
    return obs, float(null.mean()), float((1 + (null >= obs).sum()) / (R + 1))

def plant(P, rng, target):
    out = []
    for codes, bounds in P:
        c = codes.copy()
        for s, e in bounds:
            for i in range(s, e - 1):
                if rng.random() < Q:
                    want = target[c[i, 0]]; cand = np.flatnonzero(c[:, 1] == want)
                    if len(cand): j = cand[rng.integers(len(cand))]; c[[i + 1, j]] = c[[j, i + 1]]
        out.append((c, bounds))
    return out

def gate(P, seed):
    fp = pw = 0; target = np.random.default_rng(seed).integers(0, KI, KF + 1)
    for g in range(NG):
        rng = np.random.default_rng(seed * 100 + g); S = shuffle(P, rng)
        fp += test(S, rng)[2] <= ALPHA; pw += test(plant(S, rng, target), rng)[2] <= ALPHA
    return int(fp), int(pw)

def ms_pages(path, lang):
    by = {}
    for l in W.parse(path):
        if l['L'] == lang: by.setdefault(l['page'], []).append(l['words'])
    return list(by.values())

def test_job(a):
    k, lang = a; D = Data(ms_pages(dict(W.FILES)[k], lang)); i = ('A', 'B').index(lang) + (0 if k == 'IT2a' else 2)
    obs, nm, p = test(D.P, np.random.default_rng(SEED + i)); fp, pw = gate(D.P, SEED * 10 + i)
    return k, lang, dict(n_pages=len(D.P), n_pairs=sum(max(e - s - 1, 0) for _, b in D.P for s, e in b), MI=obs, MI_null=nm,
                         X=obs - nm, ratio=obs / nm, p=p, fpr=fp, power=pw, gate=fp <= 2 and pw >= 16)

def gen_job(s):
    Lg = [l for l in (generate({'text.lines_to_create': 1500}, s) or []) if len(l) >= 5]
    if len(Lg) < 1000: return s, None
    D = Data([Lg[i:i + 29] for i in range(0, len(Lg), 29)])
    obs, nm, p = test(D.P, np.random.default_rng(s))
    return s, dict(MI=obs, MI_null=nm, ratio=obs / nm, p=p)

def main():
    t0 = time.time()
    with Pool(8) as pool:
        gj = pool.map_async(gen_job, range(10901, 10921), chunksize=1)
        T = {f'{k}_{l}': r for k, l, r in pool.map(test_job, [(k, l) for k, _ in W.FILES for l in ('A', 'B')], chunksize=1)}
        print('tests', json.dumps(T), flush=True)
        G = [r for _, r in gj.get() if r]
    names = [t for t in T if T[t]['gate']]; ps = [T[t]['p'] for t in names]
    o = np.argsort(ps); rej, stop = {}, False
    for r, i in enumerate(o):
        ok = (not stop) and ps[i] <= ALPHA / (len(ps) - r); rej[names[i]] = bool(ok); stop = stop or not ok
    ver = {}
    for l in ('A', 'B'):
        if not all(T[f'{k}_{l}']['gate'] for k, _ in W.FILES): ver[l] = 'NOT TESTABLE'; continue
        m = sum(rej.get(f'{k}_{l}', False) for k, _ in W.FILES); ver[l] = 'DETECTED' if m == 2 else 'PARTIAL' if m == 1 else 'NOT DETECTED'
    rr = [g['ratio'] for g in G]; lo, hi = min(rr), max(rr)
    pos = {k: ('ABOVE' if T[f'{k}_B']['ratio'] > hi else 'BELOW' if T[f'{k}_B']['ratio'] < lo else 'INSIDE') for k, _ in W.FILES}
    gv = dict(n=len(G), ratio_min=lo, ratio_max=hi, ratio_mean=float(np.mean(rr)), MI_min=min(g['MI'] for g in G), MI_max=max(g['MI'] for g in G),
              gen_detect=f"{sum(g['p'] <= ALPHA for g in G)}/{len(G)}", position=pos,
              verdict=pos['IT2a'] if pos['IT2a'] == pos['ZL3b'] else 'SPLIT')
    out = dict(seed=SEED, tests=T, holm=rej, verdict=ver, generator=gv, generator_runs=G, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C074_results.json', 'w'), indent=1)
    for k in ('holm', 'verdict', 'generator', 'runtime_s'): print(k, json.dumps(out[k]))

if __name__ == '__main__':
    main()
