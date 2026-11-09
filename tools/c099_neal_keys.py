#!/usr/bin/env python3
"""C099 (NEW FAMILY F-KEY: within-line co-location of a word class; external claim test): do words containing the
single-leg gallows p/f ('p/f-words') sit next to each other on paragraph top lines more often than chance?
Claim under test: P. Neal ('Neal keys'), as quantified by N. Pelling, Cipher Mysteries, 2026-11-04 ('Voynich Q20: Neal
Keys update'): on top (Tiltman) lines, non-paragraph-initial p/f-words are adjacent 5.4% vs 2.7% expected; the behaviour
is said to be tied to top lines.
Lines: C070 parser verbatim (paragraph loci, no '<->', clean words, >= 5 words); top line = starts with '<%>'.
Word 1 excluded (paragraph-initial anomaly). p/f-word = contains 'p' or 'f'.
Statistic A = number of adjacent (i, i+1) pairs of p/f-words at positions 2..n, summed over lines; ratio = A / E[A].
Null: within every line, words 2..n permuted; R = 4000; p = (1 + #A* >= A)/(R + 1) (one-sided, clustering).
Tests (Holm over 6): {S1 Q20 top lines, S2 top lines outside Q20, S3 non-top lines (all quires)} x {IT2a, ZL3b}.
Robustness (own Holm over 2): R1 all top lines with a POSITION-PRESERVING null (permute separately within the first and
second half of positions 2..n), so a shared preference for early or late slots cannot create adjacency.
Gates per test (seed 9999; 20 pseudo replicates = the subset's own lines with words 2..n shuffled):
  FPR p <= 0.05 in <= 2/20.  Power: same pseudo lines; each line with >= 2 p/f-words and no adjacent p/f pair, with
  probability q = 0.80, has one p/f-word swapped into a slot next to another -> p <= 0.05 in >= 16/20.
  q fixed by a rehearsal on SHUFFLED IT2a top lines only (out/C099_rehearsal_log.txt): q 0.80 gives a planted ratio of
  about 1.5, half the claimed excess (Pelling: 5.4% vs 2.7%, ratio 2.0). Cells smaller than top lines may lack power.
  A failed gate -> that test NOT TESTABLE.
Verdict per subset: REPLICATED if both transcriptions reject (Holm); PARTIAL if one; NOT DETECTED if none (gates pass).
Registered reading: S1 and S2 REPLICATED, S3 NOT DETECTED -> 'top-line specific clustering' (Pelling's claim holds);
  S3 REPLICATED too -> clustering is general, not a top-line feature ('largely true throughout', also Pelling).
Descriptive (no verdict): the same ratio for k-words and t-words on top lines; left key ending in -dy and right key
starting o-/qo- in adjacent p/f pairs vs all p/f-words; counts. The generator is not used (it has no paragraphs).
Run: timeout 600 python tools/c099_neal_keys.py analysis/C099_results.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import parse, FILES

SEED, R, NG, Q, ALPHA = 9999, 4000, 20, 0.80, 0.05

def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0] * len(ps); run = 0
    for k, i in enumerate(o): run = max(run, min(1, (len(ps) - k) * ps[i])); adj[i] = run
    return adj

def flags(lines, f):   # positions 2..n, grouped by length into matrices (vectorised permutations)
    G = {}
    for l in lines: G.setdefault(len(l['words']) - 1, []).append([f(w) for w in l['words'][1:]])
    return {n: np.array(v, bool) for n, v in G.items()}

def adj(F): return int(sum((X[:, :-1] & X[:, 1:]).sum() for X in F.values()))

def blocks(n, halves): return [(0, n)] if not halves else [(0, n // 2), (n // 2, n)]

def perm(F, rng, halves=False):
    out = {}
    for n, X in F.items():
        Y = X.copy()
        for a, b in blocks(n, halves):
            if b - a > 1:
                o = np.argsort(rng.random((len(Y), b - a)), axis=1); Y[:, a:b] = np.take_along_axis(Y[:, a:b], o, axis=1)
        out[n] = Y
    return out

def test(F, rng, halves=False):
    obs = adj(F); null = np.array([adj(perm(F, rng, halves)) for _ in range(R)])
    return dict(A=obs, E=float(null.mean()), ratio=float(obs / null.mean()) if null.mean() else None,
                p=float((1 + (null >= obs).sum()) / (R + 1)), slots=int(sum(X.size for X in F.values())), pf=int(sum(X.sum() for X in F.values())))

def plant(F, rng):
    out = {}
    for n, X in F.items():
        Y = X.copy()
        for y in Y:
            idx = np.flatnonzero(y)
            if len(idx) >= 2 and not (y[:-1] & y[1:]).any() and rng.random() < Q:
                a = int(idx[0]); tgt = a + 1 if a + 1 < len(y) else a - 1
                b = int(idx[1]); y[tgt], y[b] = y[b], y[tgt]
        out[n] = Y
    return out

def gate(F, rng, halves=False):
    fp = pw = 0; Rg = 400
    for _ in range(NG):
        P = perm(F, rng)
        for G_, isp in ((P, False), (plant(P, rng), True)):
            obs = adj(G_); null = np.array([adj(perm(G_, rng, halves)) for _ in range(Rg)])
            p = (1 + (null >= obs).sum()) / (Rg + 1)
            if p <= ALPHA: pw += isp; fp += (not isp)
    return dict(FPR=f'{fp}/{NG}', power=f'{pw}/{NG}', ok=fp <= 2 and pw >= 16)

def pf(w): return 'p' in w or 'f' in w

def main(outp):
    t0 = time.time(); rng = np.random.default_rng(SEED); out = dict(seed=SEED, R=R, q=Q, cells={}, robust={}, descriptive={})
    for tn, path in FILES:
        L = parse(path)
        S = {'S1_Q20_top': [l for l in L if l['top'] and l['Q'] == 'T'],
             'S2_top_outside_Q20': [l for l in L if l['top'] and l['Q'] != 'T'],
             'S3_nontop_all': [l for l in L if not l['top']]}
        for s, lines in S.items():
            F = flags(lines, pf); r = test(F, rng); r.update(lines=len(lines), gate=gate(F, rng)); out['cells'][f'{s}|{tn}'] = r
        top = [l for l in L if l['top']]; F = flags(top, pf)
        r = test(F, rng, halves=True); r.update(lines=len(top), gate=gate(F, rng, halves=True)); out['robust'][f'R1_top_all|{tn}'] = r
        d = {}
        for nm, f in (('k', lambda w: 'k' in w), ('t', lambda w: 't' in w)):
            Fk = flags(top, f); d[f'{nm}_words_top'] = {k: v for k, v in test(Fk, rng).items()}
        lk = rk = npair = 0; dy_all = oq_all = n_all = 0
        for l in top:
            ws = l['words'][1:]
            for i, w in enumerate(ws):
                if pf(w): n_all += 1; dy_all += w.endswith('dy'); oq_all += w.startswith(('o', 'qo'))
                if i + 1 < len(ws) and pf(w) and pf(ws[i + 1]): npair += 1; lk += w.endswith('dy'); rk += ws[i + 1].startswith(('o', 'qo'))
        d['pairs'] = dict(n=npair, left_dy=lk / npair if npair else None, right_o_qo=rk / npair if npair else None,
                          all_pf_dy=dy_all / n_all, all_pf_o_qo=oq_all / n_all, n_pf=n_all)
        out['descriptive'][tn] = d
        print(tn, 'done', round(time.time() - t0, 1), flush=True)
    keys = list(out['cells']); ok = [k for k in keys if out['cells'][k]['gate']['ok']]
    for k, a in zip(ok, holm([out['cells'][k]['p'] for k in ok])): out['cells'][k]['p_holm'] = a
    rk_ = [k for k in out['robust'] if out['robust'][k]['gate']['ok']]
    for k, a in zip(rk_, holm([out['robust'][k]['p'] for k in rk_])): out['robust'][k]['p_holm'] = a
    verdict = {}
    for s in ('S1_Q20_top', 'S2_top_outside_Q20', 'S3_nontop_all'):
        cs = [out['cells'][f'{s}|{tn}'] for tn, _ in FILES]
        if not all(c['gate']['ok'] for c in cs): verdict[s] = 'NOT TESTABLE' if not any(c['gate']['ok'] for c in cs) else 'PARTIAL GATE (one transcription)'
        rej = sum(c.get('p_holm', 1) < ALPHA for c in cs)
        if all(c['gate']['ok'] for c in cs): verdict[s] = 'REPLICATED' if rej == 2 else 'PARTIAL' if rej == 1 else 'NOT DETECTED'
        elif rej: verdict[s] += f' ({rej} rejects among gated)'
    rs = list(out['robust'].values())
    verdict['R1_position_preserving'] = ('NOT TESTABLE' if not all(r['gate']['ok'] for r in rs) else
                                         'HOLDS' if all(r.get('p_holm', 1) < ALPHA for r in rs) else 'PARTIAL' if any(r.get('p_holm', 1) < ALPHA for r in rs) else 'DOES NOT HOLD')
    out['verdict'] = verdict; out['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(out, open(outp, 'w'), indent=1, default=str)
    for k in ('cells', 'robust', 'descriptive', 'verdict', 'elapsed_s'): print(k, json.dumps(out[k], default=str))

if __name__ == '__main__':
    main(sys.argv[1])
