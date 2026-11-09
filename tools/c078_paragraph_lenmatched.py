#!/usr/bin/env python3
"""C078 (F-PARA step 3): is C076's top-line body difference a word-length side effect, and does it survive removing all
gallows words?  Data, paragraphs, interior words (positions 3..n-2), within-paragraph line-order null, plant (random
mid-frequency unit, q* = 0.24 fixed by C076's design phase) as C076 (imports tools/c076_paragraph_depth2.py, c071).
Statistic (length-matched): interior words are split into length strata by glyph units {1-3, 4, 5, 6, >=7}; within each
stratum s, JSD_s = JSD(unit counts of top-line words in s, unit counts of middle-line words in s); LM = sum_s w_s JSD_s
with w_s = share of top-line interior words in s (weights from the observed labelling, recomputed for every permutation).
Word sets: W0 all interior words; W1 without words containing p/f units (p f cph cfh, as C076 H2); W2 without words
containing any gallows unit (p f t k cth ckh cph cfh).
Tests: {W0, W1, W2} x {Currier A, Currier B} x {IT2a, ZL} = 12, Holm alpha 0.05; R = 1000; gates per test 20 pseudo
replicates (lines pre-permuted within paragraph), FPR <= 2/20, power >= 16/20 at q* with the plant pool restricted to the
word set; seed 7878. Verdicts per (word set, language): DIFFERENT / PARTIAL / NOT DETECTED / NOT TESTABLE.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c071_paragraph_depth as C
SEED, R, RG, NG, ALPHA, Q = 7878, 1000, 200, 20, 0.05, 0.24
FILES = dict(C.FILES)
EXCL = {'W0': set(), 'W1': {'p', 'f', 'cph', 'cfh'}, 'W2': {'p', 'f', 't', 'k', 'cth', 'ckh', 'cph', 'cfh'}}

def stratum(n): return 0 if n <= 3 else min(n, 7) - 3

def keep(w, ex): return not any(u in ex for u in C.T3.units(w))

def subset(k, lang, ws):
    ex = EXCL[ws]; ps = [p for p in C.parse(FILES[k]) if p['L'] == lang]
    return [dict(p, lines=[l[:2] + [w for w in l[2:-2] if keep(w, ex)] + l[-2:] if len(l) > 4 else l for l in p['lines']]) for p in ps]

def build(ps):
    """per paragraph: per line: list of 5 stratum Counters."""
    out = []
    for p in ps:
        L = []
        for l in p['lines']:
            st = [Counter() for _ in range(5)]
            for u in C.interior(l): st[stratum(len(u))].update(u)
            L.append((st, Counter(stratum(len(u)) for u in C.interior(l))))
        out.append(L)
    return out

def stat(P, order=None):
    T = [Counter() for _ in range(5)]; M = [Counter() for _ in range(5)]; nw = Counter()
    for i, lines in enumerate(P):
        lab = C.classes(len(lines)); idx = order[i] if order is not None else range(len(lines))
        for c, j in zip(lab, idx):
            st, n = lines[j]
            if c == 'T':
                nw.update(n)
                for s in range(5): T[s].update(st[s])
            elif c == 'M':
                for s in range(5): M[s].update(st[s])
    tot = sum(nw.values())
    return float(sum(nw[s] / tot * C.jsd(T[s], M[s]) for s in range(5) if nw[s])) if tot else 0.0

def ptest(P, rng, r):
    obs = stat(P); null = [stat(P, [rng.permutation(len(l)) for l in P]) for _ in range(r)]
    return obs, float((1 + sum(v >= obs for v in null)) / (r + 1))

def shuffled(ps, rng): return [dict(p, lines=[p['lines'][j] for j in rng.permutation(len(p['lines']))]) for p in ps]

def plant(sh, rng, ex):
    toks = [w for p in sh for l in p['lines'] for w in l[2:-2]]
    uc = Counter(u for w in toks for u in C.T3.units(w)); tot = sum(uc.values())
    cand = sorted(u for u, c in uc.items() if 0.02 <= c / tot <= 0.10 and u not in ex)
    U = cand[rng.integers(len(cand))]; pool = [w for w in toks if U in C.T3.units(w)]
    out = []
    for p in sh:
        L = []
        for c, l in zip(C.classes(len(p['lines'])), p['lines']):
            if c == 'T' and len(l) > 4: l = l[:2] + [pool[rng.integers(len(pool))] if rng.random() < Q else w for w in l[2:-2]] + l[-2:]
            L.append(l)
        out.append(dict(p, lines=L))
    return out

def gate_job(a):
    k, lang, ws, i = a
    rng = np.random.default_rng(SEED * 1000 + i + (0 if k == 'IT2a' else 500) + (0 if lang == 'A' else 250) + 3000 * int(ws[1]))
    sh = shuffled(subset(k, lang, ws), rng)
    fp = ptest(build(sh), rng, RG)[1]; pobs, pp = ptest(build(plant(sh, rng, EXCL[ws])), rng, RG)
    return k, lang, ws, fp, pp, pobs

def main_job(a):
    k, lang, ws = a; ps = subset(k, lang, ws)
    rng = np.random.default_rng(SEED + (0 if k == 'IT2a' else 1) + (0 if lang == 'A' else 2) + 4 * int(ws[1]))
    obs, p = ptest(build(ps), rng, R)
    # descriptive: unmatched JSD (C071 statistic) on the same word set, and length shares
    P1 = C.build(ps); un = C.stat(P1)['T']
    lt, lm = Counter(), Counter()
    for q in ps:
        for c, l in zip(C.classes(len(q['lines'])), q['lines']):
            for u in C.interior(l): (lt if c == 'T' else lm if c == 'M' else Counter())[stratum(len(u))] += 1
    return k, lang, ws, dict(LM=obs, p=p, unmatched_JSD=un, n_T_words=sum(lt.values()), n_M_words=sum(lm.values()),
                             len_share_T=[round(lt[s] / max(1, sum(lt.values())), 3) for s in range(5)],
                             len_share_M=[round(lm[s] / max(1, sum(lm.values())), 3) for s in range(5)])

def main():
    t0 = time.time(); jobs = [(k, l, w) for k in FILES for l in ('A', 'B') for w in EXCL]
    with Pool(8) as pool:
        gj = pool.map_async(gate_job, [j + (i,) for j in jobs for i in range(NG)], chunksize=2)
        M = {'_'.join(j[:3]): j[3] for j in pool.map(main_job, jobs)}
        print('main', json.dumps(M), flush=True)
        G = {}
        for k, l, w, fp, pp, pobs in gj.get():
            g = G.setdefault(f'{k}_{l}_{w}', dict(fp=0, pw=0, pj=[])); g['fp'] += fp <= ALPHA; g['pw'] += pp <= ALPHA; g['pj'].append(pobs)
    for g in G.values(): g['pass'] = g['fp'] <= 2 and g['pw'] >= 16; g['median_planted_LM'] = float(np.median(g['pj'])); del g['pj']
    names = [n for n in G if G[n]['pass']]; ps = [M[n]['p'] for n in names]
    o = np.argsort(ps); rej, stop = {}, False
    for r, i in enumerate(o):
        ok = (not stop) and ps[i] <= ALPHA / (len(ps) - r); rej[names[i]] = bool(ok); stop = stop or not ok
    ver = {}
    for w in EXCL:
        for l in ('A', 'B'):
            ns = [f'{k}_{l}_{w}' for k in FILES]
            if not all(G[n]['pass'] for n in ns): ver[f'{w}_{l}'] = 'NOT TESTABLE'; continue
            m = sum(rej.get(n, False) for n in ns); ver[f'{w}_{l}'] = 'DIFFERENT' if m == 2 else 'PARTIAL' if m == 1 else 'NOT DETECTED'
    out = dict(seed=SEED, R=R, Q=Q, main=M, gates=G, holm=rej, n_holm=len(names), verdict=ver, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C078_results.json', 'w'), indent=1)
    for k in ('gates', 'holm', 'verdict', 'runtime_s'): print(k, json.dumps(out[k]))

if __name__ == '__main__':
    main()
