#!/usr/bin/env python3
"""C102 (NEW FAMILY F-RHYTHM step 1): do the lengths of neighbouring words inside a Voynich line co-vary?
Natural languages tend to alternate short (function) and long (content) words; a copy-and-modify generator copies
neighbours, which could make adjacent lengths persist. Nothing in C001-C101 measured this.
Lines: C070 parser verbatim (paragraph loci, no '<->', all words [a-z]+, >= 5 words). Word length = EVA glyph units
(C003 units(): ch, sh, cth, ckh, cph, cfh count as one). INTERIOR words only (positions 2..n-1; word 1 and the last word
excluded because line edges are known to be special).
Statistic r = pooled Pearson correlation of (len_i, len_i+1) over all adjacent interior pairs. Null: interior words
permuted within each line (line multisets, hence line-level length heterogeneity, kept). D = r - mean(null).
p two-sided = (1 + #|r* - m| >= |r - m|)/(R + 1), R = 2000, seed 11624.
H1 (Holm over 4): {Currier A, Currier B} x {IT2a, ZL3b}. Verdict per language: DETECTED-ALTERNATING (D<0) or
   DETECTED-PERSISTENT (D>0) if both transcriptions reject with the same sign; PARTIAL if one; NOT DETECTED if none.
Plants (applied to a pseudo replicate = real lines with interior words shuffled): with probability q per line,
   NEG = interior reordered long/short alternately (sorted desc, taken from both ends); POS = interior sorted by length.
Design (seed 11621, before gates): q = smallest of {0.02,0.05,0.10,0.20} with p<=0.05 AND correct sign in >=9/10
   design replicates for both plants in all 4 subsets (RG = 300). No q passes -> all NOT TESTABLE. Gates (seed 11622, 20 fresh replicates per subset): FPR p<=0.05 in <=2/20;
   power NEG and POS (correct sign) >= 16/20 each. A failed gate -> that subset NOT TESTABLE. Broken-meter check
   (Kryptos I-224): the null mean must differ between the two plants' replicates in the right direction.
H2 (generator reference, seeds 11630-11649, default Timm-Schinner config, 1,500 lines, lines >= 5 words; 20 valid runs):
   D of manuscript Currier B (each transcription) vs the 20 generator D. INSIDE range -> 'generator-compatible on this
   statistic'; OUTSIDE -> 'generator-excluded on this statistic' (two-sided rank p = min(1, 2*(1+min(#gen<=D, #gen>=D))/(n+1)), reported).
Descriptive: natural-language panel (letters), running text cut into pseudo-lines whose word counts are drawn from the
   IT2a Currier-B line-length distribution (seed 11623), first 2,000 lines; full-line r (edges included) for the manuscript.
Audit C101: recompute H1 full ratio and T3 (top-3 pages removed) for both transcriptions; must equal published values.
Run: timeout 600 python tools/c102_word_length_rhythm.py analysis/C102_results.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import parse, FILES
from c003_position_rigidity import units, gutenberg, hebrew

DSEED, GSEED, CSEED, SEED, GENS = 11621, 11622, 11623, 11624, range(11630, 11650)
R, RG, NG, ALPHA, QS = 2000, 300, 20, 0.05, (0.02, 0.05, 0.10, 0.20)
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

class Lines:
    """interior lengths of each line, flattened, with line ids, for fast within-line permutation."""
    def __init__(self, L):
        self.L = [np.array(x, float) for x in L if len(x) >= 3]
        self.gid = np.concatenate([np.full(len(x), i) for i, x in enumerate(self.L)])
        self.x = np.concatenate(self.L)
        last = np.r_[self.gid[1:] != self.gid[:-1], True]; self.pair = ~last  # i paired with i+1 in same line
    def r(self, x):
        a, b = x[:-1][self.pair[:-1]], x[1:][self.pair[:-1]]
        return float(np.corrcoef(a, b)[0, 1])
    def perm(self, rng):
        o = np.lexsort((rng.random(len(self.x)), self.gid)); return self.x[o]
    def null(self, rng, r): return np.array([self.r(self.perm(rng)) for _ in range(r)])

def lens_interior(lines, tok=units): return [[len(tok(w)) for w in l[1:-1]] for l in lines]

def test(Lo, rng, r):
    obs = Lo.r(Lo.x); nl = Lo.null(rng, r); m = nl.mean()
    p = (1 + (np.abs(nl - m) >= abs(obs - m)).sum()) / (r + 1)
    return dict(r=obs, null_mean=float(m), null_sd=float(nl.std()), D=float(obs - m), z=float((obs - m) / nl.std()), p=float(p))

def plant(L, rng, q, kind):
    out = []
    for x in L:
        x = list(x)
        if rng.random() < q:
            s = sorted(x, reverse=True)
            if kind == 'POS': x = s
            else:
                x = []; i, j = 0, len(s) - 1
                while i <= j:
                    x.append(s[i]); i += 1
                    if i <= j: x.append(s[j]); j -= 1
        out.append(x)
    return out

def pseudo(Lo, rng): return [list(rng.permutation(x)) for x in Lo.L]

def gate(Lo, rng, q, ng=NG):
    fp = neg = pos = 0; dn = []; dp = []
    for _ in range(ng):
        S = pseudo(Lo, rng)
        t = test(Lines(S), rng, RG); fp += t['p'] <= ALPHA
        t = test(Lines(plant(S, rng, q, 'NEG')), rng, RG); neg += t['p'] <= ALPHA and t['D'] < 0; dn.append(t['D'])
        t = test(Lines(plant(S, rng, q, 'POS')), rng, RG); pos += t['p'] <= ALPHA and t['D'] > 0; dp.append(t['D'])
    return dict(FPR=int(fp), NEG=int(neg), POS=int(pos), D_neg_mean=float(np.mean(dn)), D_pos_mean=float(np.mean(dp)))

def holm(ps):
    k = sorted(ps, key=ps.get); out, run = {}, 0
    for i, key in enumerate(k): run = max(run, min(1, ps[key] * (len(k) - i))); out[key] = run
    return out

def main():
    outp = sys.argv[1] if len(sys.argv) > 1 else 'analysis/C102_results.json'
    res = dict(cycle='C102', seeds=dict(design=DSEED, gates=GSEED, chunk=CSEED, test=SEED, gen=[GENS[0], GENS[-1]]))
    P = {k: parse(f) for k, f in FILES}
    sub = {f'{k}|{L}': Lines(lens_interior([l['words'] for l in P[k] if l['L'] == L])) for k, _ in FILES for L in 'AB'}
    res['n'] = {s: dict(lines=len(v.L), pairs=int(v.pair[:-1].sum())) for s, v in sub.items()}; log('n', res['n'])
    # design
    rng = np.random.default_rng(DSEED); qd = None; des = {}
    for q in QS:
        ok = True; des[q] = {}
        for s, Lo in sub.items():
            g = gate(Lo, rng, q, ng=10); des[q][s] = g; ok &= g['NEG'] >= 9 and g['POS'] >= 9
        log('design q', q, des[q])
        if ok: qd = q; break
    res['design'] = dict(q=qd, table={str(k): v for k, v in des.items()})
    # gates
    rng = np.random.default_rng(GSEED); G = {}
    for s, Lo in sub.items():
        g = gate(Lo, rng, qd if qd else QS[-1]); g['ok'] = bool(qd and g['FPR'] <= 2 and g['NEG'] >= 16 and g['POS'] >= 16
                                                      and g['D_neg_mean'] < 0 < g['D_pos_mean']); G[s] = g
    res['gates'] = G; log('gates', G)
    # H1
    rng = np.random.default_rng(SEED); H = {s: test(Lo, rng, R) for s, Lo in sub.items()}
    ph = holm({s: h['p'] for s, h in H.items()})
    for s in H: H[s]['p_holm'] = ph[s]
    res['H1'] = H; log('H1', H)
    ver = {}
    for L in 'AB':
        ks = [f'{k}|{L}' for k, _ in FILES]
        if not all(G[k]['ok'] for k in ks): ver[L] = 'NOT TESTABLE'; continue
        rej = [k for k in ks if H[k]['p_holm'] <= ALPHA]; sg = {np.sign(H[k]['D']) for k in rej}
        if len(rej) == 2 and len(sg) == 1: ver[L] = 'DETECTED-' + ('ALTERNATING' if sg == {-1.0} else 'PERSISTENT')
        elif rej: ver[L] = 'PARTIAL'
        else: ver[L] = 'NOT DETECTED'
    res['verdict_H1'] = ver
    # full-line descriptive
    rng = np.random.default_rng(SEED + 100)
    res['full_line'] = {f'{k}|{L}': test(Lines([[len(units(w)) for w in l['words']] for l in P[k] if l['L'] == L]), rng, 500)
                        for k, _ in FILES for L in 'AB'}
    # H2 generator
    from c004_generator_sweep import generate
    gen = []; rng = np.random.default_rng(SEED + 200)
    for s in GENS:
        Lg = generate({'text.lines_to_create': 1500}, s)
        if not Lg: continue
        Lg = [l for l in Lg if len(l) >= 5]; t = test(Lines(lens_interior(Lg)), rng, 500); t['seed'] = s; gen.append(t)
    gD = np.array([g['D'] for g in gen]); H2 = {}
    for k, _ in FILES:
        d = H[f'{k}|B']['D']; lo, hi = int((gD <= d).sum()), int((gD >= d).sum())
        H2[k] = dict(D=d, gen_min=float(gD.min()), gen_max=float(gD.max()), gen_mean=float(gD.mean()),
                     rank_p=float(min(1, 2 * (1 + min(lo, hi)) / (len(gD) + 1))),
                     reading='generator-compatible on this statistic' if gD.min() <= d <= gD.max() else 'generator-excluded on this statistic')
    res['H2'] = dict(n_runs=len(gen), runs=gen, B=H2); log('H2', H2)
    # natural-language panel
    rng = np.random.default_rng(CSEED); ll = np.array([len(l['words']) for l in P['IT2a'] if l['L'] == 'B'])
    def chunk(lines):
        w = [x for l in lines for x in l]; out, i = [], 0
        while i < len(w) and len(out) < 2000:
            n = int(rng.choice(ll)); out.append(w[i:i + n]); i += n
        return [l for l in out if len(l) >= 5]
    C = 'data/corpora/'; NL = {}
    for name, lines in (('Latin Caesar', gutenberg(C + 'pg218.txt')), ('Latin Descartes', gutenberg(C + 'pg23306.txt')),
                        ('Italian Dante', gutenberg(C + 'pg1012.txt')), ('Spanish Cervantes', gutenberg(C + 'pg2000.txt')),
                        ('Finnish Kalevala', gutenberg(C + 'pg7000.txt')), ('Finnish Kivi', gutenberg(C + 'pg11940.txt')),
                        ('Hebrew Genesis', hebrew(C + 'Gen.xml'))):
        NL[name] = test(Lines(lens_interior(chunk(lines), tok=list)), rng, 500)
    res['natural_language'] = NL; log('NL', {k: round(v['D'], 4) for k, v in NL.items()})
    # audit C101
    import c101_neal_keys_pages as c101
    A = {}
    for k, f in FILES:
        lines = [l for l in parse(f) if l['Q'] == 'T' and l['top']]
        F = c101.fl(lines, c101.CLS['pf']); a, e = c101.AE1(F); pg = np.array([l['page'] for l in lines]); up = sorted(set(pg))
        t3, drop = c101.T3(F, pg, up); A[k] = dict(full_ratio=float(a.sum() / e.sum()), T3=float(t3), dropped=drop)
    pub = {'IT2a': (1.3447115589691347, 1.2921060792569352), 'ZL3b': (1.3047246173592428, 1.2569236135333102)}
    res['audit_C101'] = dict(values=A, exact=all(abs(A[k]['full_ratio'] - pub[k][0]) < 1e-12 and abs(A[k]['T3'] - pub[k][1]) < 1e-12 for k in A))
    log('audit', res['audit_C101'])
    res['elapsed_s'] = round(time.time() - T0, 1)
    json.dump(res, open(outp, 'w'), indent=1, default=float); log('verdict', ver, 'H2', {k: v['reading'] for k, v in H2.items()})

if __name__ == '__main__':
    main()
