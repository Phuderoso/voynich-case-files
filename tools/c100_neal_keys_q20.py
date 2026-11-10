#!/usr/bin/env python3
"""C100 (F-KEY step 2): why is the Neal-key clustering of p/f-words (C099) confined to Quire 20 among top lines?
Lines: C070 parser verbatim (tools/c070_word2_sh.py parse); top line = starts with '<%>'; positions 2..n only (word 1
excluded); p/f-word = contains 'p' or 'f'; L = Currier language from the page header, Q == 'T' is Quire 20.
For a line with m slots (positions 2..n) and k flagged words, E[adjacent flagged pairs] under within-line permutation
= k(k-1)/m exactly. Subset ratio = sum A / sum E.
Ha (Holm over 4 with Hc): Q20 top lines vs Currier-B top lines outside Q20. T = ratio(Q20) - ratio(B other).
   Null: the 'Q20' label permuted among the pooled lines (subset sizes fixed), R = 4000, one-sided (Q20 higher).
   Gates (20 pseudo replicates, seed 10000): FPR = all pooled lines with words 2..n shuffled, p <= 0.05 in <= 2/20;
   power = same, plus C099's plant (q 0.80, ratio ~1.5) in the Q20 lines only, p <= 0.05 in >= 16/20 (null R 400).
   Reading: DIFFERENT (Q20 > other B) if both transcriptions reject; NOT DETECTED if neither and gates pass.
Hc (Holm over 4 with Ha): Q20 top lines, adjacency counted only for pairs of DIFFERENT words (repeats like
   'qopchedy qopchedy' removed from the count, in the data and in every null draw). Null: words 2..n permuted
   within line, R = 4000, one-sided. Gates as Ha (plant swaps a p/f-word next to another, q 0.80).
   Reading: SURVIVES if both reject; NOT DETECTED if neither and gates pass.
Hb (own decision, no Holm): Q20 top lines, D = ratio(p/f-words) - ratio(t-words), 95% percentile bootstrap over lines
   (4000 resamples). EXCEEDS if the lower bound > 0 in both transcriptions; NOT SHOWN otherwise.
   Gates: FPR = shuffled lines, lower bound > 0 in <= 2/20; power = shuffled lines + p/f plant, in >= 16/20.
A failed gate -> that test NOT TESTABLE. No generator (it has no paragraphs). Descriptive: line and pair counts,
   ratios of each subset, the number of repeated-word p/f pairs, Currier-A top lines (few; no test).
Run: timeout 600 python tools/c100_neal_keys_q20.py analysis/C100_results.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import parse, FILES

SEED, R, RG, NG, Q, ALPHA, B = 10000, 4000, 400, 20, 0.80, 0.05, 4000
pf = lambda w: 'p' in w or 'f' in w
tw = lambda w: 't' in w

def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0] * len(ps); run = 0
    for k, i in enumerate(o): run = max(run, min(1, (len(ps) - k) * ps[i])); adj[i] = run
    return adj

def body(lines): return [list(l['words'][1:]) for l in lines]

def shuf(W, rng): return [list(rng.permutation(w)) for w in W]

def plant(W, rng):
    out = []
    for w in W:
        w = list(w); idx = [i for i, x in enumerate(w) if pf(x)]
        if len(idx) >= 2 and not any(pf(w[i]) and pf(w[i + 1]) for i in range(len(w) - 1)) and rng.random() < Q:
            a, b = idx[0], idx[1]; t = a + 1 if a + 1 < len(w) else a - 1; w[t], w[b] = w[b], w[t]
        out.append(w)
    return out

def AE(w, f=pf, distinct=False):
    fl = [f(x) for x in w]; m = len(w); k = sum(fl)
    A = sum(fl[i] and fl[i + 1] and (not distinct or w[i] != w[i + 1]) for i in range(m - 1))
    return A, k * (k - 1) / m

def arrays(W, f=pf):
    a = np.array([AE(w, f) for w in W], float); return a[:, 0], a[:, 1]

# --- Ha: label permutation
def Ta(A, E, lab):
    return A[lab].sum() / E[lab].sum() - A[~lab].sum() / E[~lab].sum()

def test_a(Wq, Wo, rng, r=R):
    A, E = arrays(Wq + Wo); lab = np.zeros(len(A), bool); lab[:len(Wq)] = True
    obs = Ta(A, E, lab); null = np.array([Ta(A, E, rng.permutation(lab)) for _ in range(r)])
    return float(obs), float((1 + (null >= obs).sum()) / (r + 1))

# --- Hc: distinct-word adjacency, within-line permutation
def adj_distinct(W): return sum(AE(w, distinct=True)[0] for w in W)

def test_c(W, rng, r=R):
    obs = adj_distinct(W); null = np.array([adj_distinct(shuf(W, rng)) for _ in range(r)])
    return obs, float(null.mean()), float((1 + (null >= obs).sum()) / (r + 1))

# --- Hb: bootstrap
def boot_b(W, rng, b=B):
    Ap, Ep = arrays(W, pf); At, Et = arrays(W, tw); n = len(W)
    D = Ap.sum() / Ep.sum() - At.sum() / Et.sum(); ds = np.empty(b)
    for i in range(b):
        s = rng.integers(0, n, n); ds[i] = Ap[s].sum() / Ep[s].sum() - At[s].sum() / Et[s].sum()
    return float(D), float(np.quantile(ds, 0.025)), float(np.quantile(ds, 0.975))

def gates(kind, Wq, Wo, rng):
    fp = pw = 0
    for _ in range(NG):
        Sq, So = shuf(Wq, rng), shuf(Wo, rng)
        for planted in (False, True):
            Pq = plant(Sq, rng) if planted else Sq
            if kind == 'a': hit = test_a(Pq, So, rng, RG)[1] <= ALPHA
            elif kind == 'c': hit = test_c(Pq, rng, RG)[2] <= ALPHA
            else: hit = boot_b(Pq, rng, 1000)[1] > 0
            pw += planted and hit; fp += (not planted) and hit
    return dict(FPR=f'{fp}/{NG}', power=f'{pw}/{NG}', ok=fp <= 2 and pw >= 16)

def ratio(W, f=pf, distinct=False):
    a = np.array([AE(w, f, distinct) for w in W]); return dict(lines=len(W), A=int(a[:, 0].sum()), E=float(a[:, 1].sum()),
                                                              ratio=float(a[:, 0].sum() / a[:, 1].sum()))

def main(outp):
    t0 = time.time(); rng = np.random.default_rng(SEED); out = dict(seed=SEED, R=R, q=Q, tests={}, descriptive={})
    for tn, path in FILES:
        L = parse(path); top = [l for l in L if l['top']]
        Wq = body([l for l in top if l['Q'] == 'T']); Wo = body([l for l in top if l['Q'] != 'T' and l['L'] == 'B'])
        WA = body([l for l in top if l['L'] == 'A'])
        T, p = test_a(Wq, Wo, rng); out['tests'][f'Ha|{tn}'] = dict(T=T, p=p, gate=gates('a', Wq, Wo, rng))
        obs, E, p = test_c(Wq, rng); out['tests'][f'Hc|{tn}'] = dict(A_distinct=obs, E=E, ratio=obs / E, p=p, gate=gates('c', Wq, Wo, rng))
        D, lo, hi = boot_b(Wq, rng); out['tests'][f'Hb|{tn}'] = dict(D=D, lo=lo, hi=hi, gate=gates('b', Wq, Wo, rng))
        rep = sum(sum(pf(w[i]) and w[i] == w[i + 1] for i in range(len(w) - 1)) for w in Wq)
        out['descriptive'][tn] = dict(Q20_pf=ratio(Wq), B_other_pf=ratio(Wo), A_top_pf=ratio(WA), Q20_t=ratio(Wq, tw),
                                      B_other_t=ratio(Wo, tw), Q20_pf_repeat_pairs=int(rep))
        print(tn, 'done', round(time.time() - t0, 1), flush=True)
    ks = [k for k in out['tests'] if k[:2] in ('Ha', 'Hc') and out['tests'][k]['gate']['ok']]
    for k, a in zip(ks, holm([out['tests'][k]['p'] for k in ks])): out['tests'][k]['p_holm'] = a
    v = {}
    for h, yes in (('Ha', 'DIFFERENT (Q20 > other B)'), ('Hc', 'SURVIVES')):
        cs = [out['tests'][f'{h}|{tn}'] for tn, _ in FILES]
        if not all(c['gate']['ok'] for c in cs): v[h] = 'NOT TESTABLE'
        else:
            rej = sum(c['p_holm'] < ALPHA for c in cs); v[h] = yes if rej == 2 else 'PARTIAL' if rej == 1 else 'NOT DETECTED'
    cs = [out['tests'][f'Hb|{tn}'] for tn, _ in FILES]
    v['Hb'] = 'NOT TESTABLE' if not all(c['gate']['ok'] for c in cs) else 'EXCEEDS' if all(c['lo'] > 0 for c in cs) else 'NOT SHOWN'
    out['verdict'] = v; out['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(out, open(outp, 'w'), indent=1, default=str)
    for k in ('tests', 'descriptive', 'verdict', 'elapsed_s'): print(k, json.dumps(out[k], default=str))

if __name__ == '__main__':
    main(sys.argv[1])
