#!/usr/bin/env python3
"""C034 (new family F-SEG, segmentation): are the transcribed Voynich spaces 'Harris boundaries', i.e. places where the
next glyph becomes hard to predict, as word boundaries are in natural language? Compared with 7 natural texts and the
Timm-Schinner generator. Pre-registered in case-file/C034-harris-boundaries.md. Seed 3434.
Run: timeout 600 python3 tools/c034_harris_boundaries.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time, math
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c030_line_edge_glyphs as L
import c027_word_length_binomial as W

SEED, K, NU, NPERM, NBLK, NBOOT, ALPHA = 3434, 2, 40000, 200, 20, 200, 0.05
C = 'data/corpora/'

def words_of(lines): return [w for l in lines for w in l]

def stream(words, tok):
    s, b = [], []
    for w in words:
        u = tok(w) if tok else list(w)
        if not u: continue
        b.append(len(s)); s.extend(u)
        if len(s) >= NU: break
    s = s[:NU]; isb = np.zeros(len(s), bool); isb[[x for x in b if 0 < x < len(s)]] = True
    return s, isb, [len(tok(w)) if tok else len(w) for w in words]

def ent(c):
    n = sum(c.values()); return -sum(v / n * math.log2(v / n) for v in c.values())

def scores(s):
    """gap i (between s[i-1] and s[i]), i = K..len-K: H(next | K left) + H(prev | K right)"""
    nxt, prv = defaultdict(Counter), defaultdict(Counter)
    for i in range(K, len(s)): nxt[tuple(s[i - K:i])][s[i]] += 1
    for i in range(0, len(s) - K): prv[tuple(s[i + 1:i + 1 + K])][s[i]] += 1
    hn = {k: ent(v) for k, v in nxt.items()}; hp = {k: ent(v) for k, v in prv.items()}
    sc = np.full(len(s), np.nan)
    for i in range(K, len(s) - K + 1):
        sc[i] = hn[tuple(s[i - K:i])] + hp[tuple(s[i:i + K])]
    return sc

def rankdata(x):
    """midranks (ties averaged), numpy only"""
    u, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    upper = np.cumsum(cnt); return ((upper - cnt + 1 + upper) / 2)[inv]

def auc(sc, lab):
    m = ~np.isnan(sc); return auc_r(rankdata(sc[m]), m, lab)

def auc_r(ranks, m, lab):
    """AUC with precomputed midranks of the valid scores (labels change, scores do not)"""
    y = lab[m]; n1 = y.sum(); n0 = len(y) - n1
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

def null_labels(n, lengths, rng):
    """random segmentation with the same word-length distribution (lengths drawn by shuffling the text's own)"""
    L_ = np.array(lengths); lab = np.zeros(n, bool); pos = 0
    while True:
        for l in rng.permutation(L_):
            pos += int(l)
            if pos >= n: return lab
            lab[pos] = True

def block_boot(sc, lab, rng):
    n = len(sc); edges = np.linspace(0, n, NBLK + 1).astype(int); out = []
    for _ in range(NBOOT):
        idx = np.concatenate([np.arange(edges[b], edges[b + 1]) for b in rng.integers(0, NBLK, NBLK)])
        out.append(auc(sc[idx], lab[idx]))
    return np.percentile(out, [2.5, 97.5]).tolist()

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED)
    corp = {'Voynich_ZL3b': ([ws for ws, _ in L.ivtff_paragraphs('data/ZL3b-n.txt')], T.units),
            'Voynich_IT2a': ([ws for ws, _ in L.ivtff_paragraphs('data/IT2a-n.txt')], T.units),
            'Generator_TimmSchinner': ([ws for ws, _ in L.generator()], T.units),
            'Latin_Caesar': (T.gutenberg(C + 'pg218.txt'), None), 'Latin_Descartes': (T.gutenberg(C + 'pg23306.txt'), None),
            'Italian_Dante': (T.gutenberg(C + 'pg1012.txt'), None), 'Italian_Machiavelli': (T.gutenberg(C + 'pg56498.txt'), None),
            'Spanish_Cervantes': (T.gutenberg(C + 'pg2000.txt'), None),
            'Hebrew_Genesis': (T.hebrew(C + 'Gen.xml'), None), 'Hebrew_Exodus': (T.hebrew(C + 'Exod.xml'), None)}
    R = dict(K=K, units=NU, nperm=NPERM, seed=SEED); tested = ['Voynich_ZL3b', 'Voynich_IT2a', 'Generator_TimmSchinner']
    nat = [k for k in corp if k not in tested]; a_test = ALPHA / len(tested)
    for k, (lines, tok) in corp.items():
        s, lab, lens = stream(words_of(lines), tok); sc = scores(s); a = auc(sc, lab); m = ~np.isnan(sc); rk = rankdata(sc[m])
        nulls = np.array([auc_r(rk, m, null_labels(len(s), lens, rng)) for _ in range(NPERM)])
        p = float((1 + (nulls >= a).sum()) / (NPERM + 1))
        # FPR gate: 40 null segmentations, each tested against 50 fresh null draws at the family alpha
        fp = 0
        for _ in range(40):
            a0 = auc_r(rk, m, null_labels(len(s), lens, rng))
            ref = nulls[rng.choice(NPERM, 50, replace=False)]
            fp += (1 + (ref >= a0).sum()) / 51 < max(a_test, 1 / 51)
        R[k] = dict(units=len(s), alphabet=len(set(s)), boundaries=int(lab.sum()), auc=a, null_mean=float(nulls.mean()),
                    null_max=float(nulls.max()), p=p, fpr=fp / 40, ci95=block_boot(sc, lab, rng))
        print(k, {x: (round(y, 4) if isinstance(y, float) else y) for x, y in R[k].items()}, round(time.time() - t0, 1), 's', flush=True)
    power = sum(R[k]['p'] < a_test for k in nat); fpr_ok = all(R[k]['fpr'] <= 0.1 for k in corp)
    R['gates'] = dict(natural_detected=f'{power}/{len(nat)}', fpr_ok=fpr_ok, passed=power == len(nat) and fpr_ok)
    nat_lo = min(R[k]['ci95'][0] for k in nat); nat_hi = max(R[k]['ci95'][1] for k in nat)
    for k in tested:
        q1 = 'NOT TESTABLE' if not R['gates']['passed'] else ('BOUNDARIES' if R[k]['p'] < a_test else 'NOT BOUNDARIES')
        lo, hi = R[k]['ci95']
        q2 = 'ABOVE natural range' if lo > nat_hi else ('BELOW natural range' if hi < nat_lo else 'WITHIN natural range')
        R[k]['q1'] = q1; R[k]['q2'] = q2
    R['natural_ci_envelope'] = [nat_lo, nat_hi]; R['seconds'] = round(time.time() - t0, 1)
    print(json.dumps({k: (R[k].get('q1'), R[k].get('q2')) for k in tested}), R['gates'], R['natural_ci_envelope'])
    json.dump(R, open('analysis/C034_results.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
