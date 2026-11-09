#!/usr/bin/env python3
"""C077 (NEW FAMILY F-DIR, the arrow of the word): is the inside of a Voynich word easier to predict left-to-right or
right-to-left, and is that asymmetry inside the range of natural languages and of the Timm-Schinner generator?
Symbols: Voynich = C003 glyph units; natural texts = letters. Each word = ^ u1 .. un $.
Model: order-k Markov (k = 1, 2, 3), add-0.1 smoothing over the training alphabet (+ '$'), trained on even blocks and
tested on odd blocks and vice versa (20 contiguous blocks of the first N = 15,000 word tokens). Forward = words as read;
backward = each word's units reversed. H = cross-entropy in bits per predicted symbol (units + '$').
A_k = H_backward - H_forward (positive = the word is easier to predict left-to-right).
Primary k = 3 (pre-registered); k = 1, 2 descriptive.  95% CI: block bootstrap of the two-fold per-block log-loss
difference (B = 1000 resamples of 20 blocks).  Range rule: OUTSIDE NATURAL if the manuscript's CI lies entirely outside
[min, max] of the 9 natural point values; INSIDE NATURAL if its point value is inside and CI overlaps; NOT CALLED otherwise.
Gate (FPR, leave-one-out): each natural text vs the other 8 with the same rule; <= 1/9 called OUTSIDE, else NOT TESTABLE.
Sanity (must hold exactly): reversing every word of a text flips the sign of A_k.  Generator: 10 default runs, fresh
seeds 11101-11110, 2,500 lines each, same N; ABOVE/BELOW GENERATOR if the manuscript's CI is entirely above/below all runs.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time, math
from collections import Counter, defaultdict
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c030_line_edge_glyphs as L

SEED, N, NBLK, B, LAM, KS = 7777, 15000, 20, 1000, 0.1, (1, 2, 3)
C = 'data/corpora/'
NAT = {'Latin_Caesar': ('g', 'pg218.txt'), 'Latin_Descartes': ('g', 'pg23306.txt'), 'Italian_Dante': ('g', 'pg1012.txt'),
       'Italian_Machiavelli': ('g', 'pg56498.txt'), 'Spanish_Cervantes': ('g', 'pg2000.txt'), 'Finnish_Kalevala': ('g', 'pg7000.txt'),
       'Finnish_Kivi': ('g', 'pg11940.txt'), 'Hebrew_Genesis': ('h', 'Gen.xml'), 'Hebrew_Exodus': ('h', 'Exod.xml')}
GSEEDS = range(11101, 11111)

def seqs_nat(kind, f):
    lines = T.gutenberg(C + f) if kind == 'g' else T.hebrew(C + f)
    return [list(w) for l in lines for w in l][:N]

def seqs_voy(path): return [T.units(w) for ws, _ in L.ivtff_paragraphs(path) for w in ws][:N]

def block_losses(words, k, rev):
    """per-block total log-loss (bits) and symbol counts, 2-fold even/odd."""
    W = [w[::-1] if rev else w for w in words]
    e = np.linspace(0, len(W), NBLK + 1).astype(int); blocks = [W[e[b]:e[b + 1]] for b in range(NBLK)]
    loss, cnt = np.zeros(NBLK), np.zeros(NBLK)
    for fold in (0, 1):
        ctx, alph = defaultdict(Counter), set(['$'])
        for b in range(NBLK):
            if b % 2 != fold: continue
            for w in blocks[b]:
                s = ['^'] * k + list(w) + ['$']; alph.update(w)
                for i in range(k, len(s)): ctx[tuple(s[i - k:i])][s[i]] += 1
        V = len(alph) + 1  # +1 unseen symbol
        tot = {c: sum(v.values()) for c, v in ctx.items()}
        for b in range(NBLK):
            if b % 2 == fold: continue
            for w in blocks[b]:
                s = ['^'] * k + list(w) + ['$']
                for i in range(k, len(s)):
                    c = tuple(s[i - k:i]); n = ctx[c][s[i]] if c in ctx else 0; t = tot.get(c, 0)
                    loss[b] -= math.log2((n + LAM) / (t + LAM * V)); cnt[b] += 1
    return loss, cnt

def analyse(name, words, boot=True):
    rng = np.random.default_rng(SEED + sum(map(ord, name)))
    out = dict(n_words=len(words), n_symbols=int(sum(len(w) for w in words)))
    for k in KS:
        lf, cf = block_losses(words, k, False); lb, cb = block_losses(words, k, True)
        A = lb.sum() / cb.sum() - lf.sum() / cf.sum()
        r = dict(Hf=float(lf.sum() / cf.sum()), Hb=float(lb.sum() / cb.sum()), A=float(A))
        if boot:
            bs = []
            for _ in range(B):
                i = rng.integers(NBLK, size=NBLK); bs.append(lb[i].sum() / cb[i].sum() - lf[i].sum() / cf[i].sum())
            r['ci'] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        out[f'k{k}'] = r
    return name, out

def gen_job(s):
    import c004_generator_sweep as G
    Lg = G.generate({'text.lines_to_create': 2500}, s)
    ws = [T.units(w) for l in (Lg or []) for w in l][:N]
    if len(ws) < N: return f'gen_{s}', None
    return analyse(f'gen_{s}', ws, boot=False)

def call(ci, x, lo, hi):
    if ci[1] < lo or ci[0] > hi: return 'OUTSIDE NATURAL'
    return 'INSIDE NATURAL' if lo <= x <= hi else 'NOT CALLED'

def main():
    t0 = time.time()
    texts = {n: seqs_nat(*v) for n, v in NAT.items()}
    voy = {'Voynich_ZL3b': seqs_voy('data/ZL3b-n.txt'), 'Voynich_IT2a': seqs_voy('data/IT2a-n.txt')}
    # sanity: reversal flips the sign exactly (Caesar, k=3)
    a1 = analyse('s', texts['Latin_Caesar'], False)[1]['k3']['A']; a2 = analyse('s', [w[::-1] for w in texts['Latin_Caesar']], False)[1]['k3']['A']
    sanity = dict(A=a1, A_reversed=a2, ok=abs(a1 + a2) < 1e-9)
    with Pool(8) as pool:
        gj = pool.map_async(gen_job, list(GSEEDS), chunksize=1)
        R = dict(pool.starmap(analyse, list(texts.items()) + list(voy.items())))
        G = {n: r for n, r in gj.get() if r}
    out = dict(seed=SEED, N=N, sanity=sanity, results=R, generator=G)
    nat = list(NAT)
    gate, ver = {}, {}
    for k in KS:
        key = f'k{k}'
        fp = 0
        for n in nat:
            others = [R[m][key]['A'] for m in nat if m != n]
            fp += call(R[n][key]['ci'], R[n][key]['A'], min(others), max(others)) == 'OUTSIDE NATURAL'
        gate[key] = dict(loo_outside=fp, pass_=fp <= 1)
        lo, hi = min(R[m][key]['A'] for m in nat), max(R[m][key]['A'] for m in nat)
        ga = [g[key]['A'] for g in G.values()]
        for v in voy:
            ci, x = R[v][key]['ci'], R[v][key]['A']
            gv = ('ABOVE GENERATOR' if ci[0] > max(ga) else 'BELOW GENERATOR' if ci[1] < min(ga) else 'INSIDE GENERATOR RANGE' if min(ga) <= x <= max(ga) else 'NOT CALLED') if len(ga) >= 8 else 'NOT TESTABLE'
            ver[f'{v}_{key}'] = dict(natural=call(ci, x, lo, hi) if gate[key]['pass_'] else 'NOT TESTABLE', natural_range=[lo, hi],
                                    generator=gv, generator_range=[min(ga), max(ga)] if ga else None, A=x, ci=ci)
    out.update(gate=gate, verdict=ver, n_generator=len(G), runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C077_results.json', 'w'), indent=1)
    print('sanity', sanity); print('gate', gate)
    for n, r in list(R.items()) + list(G.items()): print(n, {k: (round(r[k]['Hf'], 3), round(r[k]['Hb'], 3), round(r[k]['A'], 4)) for k in ('k1', 'k2', 'k3')})
    for k, v in ver.items(): print(k, json.dumps(v))
    print('runtime', out['runtime_s'])

if __name__ == '__main__':
    main()
