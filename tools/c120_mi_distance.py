#!/usr/bin/env python3
"""C120 (NEW FAMILY F-MID step 1): glyph mutual information at a distance, beyond the word.
Prior work: Ebeling & Poeschel 1994 (long-range letter correlations); Lin & Tegmark 2017 (MI decay in language);
Montemurro & Zanette 2013 (word-level keyword clustering in the Voynich MS). Nothing in C001-C119 measured MI(d).
Question: inside a page, does the order of Voynich words carry glyph-level information at distances of 16-256 glyph
steps (about 3 words to a few lines) beyond what the page's own word multiset carries? How does the size of that
excess compare with natural texts and with the Timm-Schinner self-citation generator, at matched size and page cut?
Stream: C070 parser verbatim (paragraph loci, no '<->', words [a-z]+, lines >= 5 words). Page = folio-side id. Per page,
 words in reading order, each word = its EVA units (C003 units()) followed by one separator symbol '_'. Pairs (i, i+d) are
 counted only inside a page. MI(d) = plug-in mutual information (bits) of the joint symbol counts at lag d.
Lags D = (16, 24, 32, 48, 64, 96, 128, 192, 256). Statistic M = sum_d MI(d).
Null N-PAGE: words permuted within their page (page multiset and unit length of every page kept; units inside words kept).
 E = M - mean(M*) ; z = E / sd(M*) ; p one-sided = (1 + #M* >= M)/(R + 1), R = 1000 (floor 1/1001).
H1 (Holm over 4, alpha 0.05): {Currier A, Currier B} x {ZL3b, IT2a}. Verdict per language: DETECTED if both
 transcriptions reject; PARTIAL if one; NOT DETECTED if none (gates pass); NOT TESTABLE if a gate fails.
Gates per test (seed 11810, stream i = default_rng([11810, i]) for i over ZL3b A, ZL3b B, IT2a A, IT2a B, run in parallel; 20 pseudo replicates; R_g = 200): pseudo = the stratum's pages with words shuffled within the
 page and re-cut into the original line word counts. G-FPR: p <= 0.05 in <= 2/20. G-POW: self-citation plant on the
 pseudo replicate: for every line after a page's first line, with probability q = 0.25, the word at a random position j is
 replaced by a copy of the previous line's word at position min(j, len-1); p <= 0.05 in >= 16/20. Planted direction is
 upward and M is a sum statistic (Kryptos lesson c200), so a planted excess can show.
H2 (descriptive, pre-declared reading; seed 11811 for nulls, R = 200): ZL3b Currier B against a panel cut to the same
 word count and the same page word-count sequence: Latin Caesar, Latin Descartes, Italian Dante, Spanish Cervantes,
 Italian Machiavelli, Finnish Kivi, Finnish Kalevala (Gutenberg, C003 gutenberg()), Hebrew Genesis+Exodus consonantal
 (C003 hebrew()), and 5 default Timm-Schinner runs (seeds 11812-11816, 4,000 lines requested, first N words).
 Reported per text: E (bits), z, E per lag. Reading of Voynich-B E: 'inside natural range' / 'above natural max' /
 'below natural min'; same against the generator range. Alphabet sizes differ (EVA units vs letters), so E is a size and
 alphabet-dependent quantity: H2 is descriptive, never a verdict.
Run: timeout 600 python tools/c120_mi_distance.py analysis/C120_results.json
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import parse, FILES
from c003_position_rigidity import units, gutenberg, hebrew

SEED, GSEED, PSEED, GENS = 11809, 11810, 11811, range(11812, 11817)
LAGS = (16, 24, 32, 48, 64, 96, 128, 192, 256)
R, RG, NG, Q, ALPHA = 1000, 200, 20, 0.25, 0.05
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

class Stream:
    """pages: list of pages, each a list of lines, each a list of words."""
    def __init__(self, pages, tok=units):
        self.pages = pages
        vocab, words, pg = {'_': 0}, [], []
        for k, p in enumerate(pages):
            for l in p:
                for w in l:
                    u = [vocab.setdefault(x, len(vocab)) for x in tok(w)] + [0]
                    words.append(np.array(u, np.int32)); pg.append(k)
        self.K = len(vocab); self.pg = np.array(pg)
        self.L = np.array([len(w) for w in words]); self.S = np.r_[0, np.cumsum(self.L)[:-1]]
        self.x = np.concatenate(words); self.n = len(self.x); self.nw = len(words)
        upg = np.repeat(self.pg, self.L)
        self.masks = {d: np.nonzero(upg[:-d] == upg[d:])[0] for d in LAGS}
    def mi(self, x):
        out = []
        for d in LAGS:
            a = self.masks[d]
            if len(a) == 0: out.append(0.0); continue
            c = np.bincount(x[a] * self.K + x[a + d], minlength=self.K * self.K).reshape(self.K, self.K).astype(float)
            n = c.sum(); px = c.sum(1) / n; py = c.sum(0) / n; nz = c > 0; pj = c[nz] / n
            out.append(float((pj * np.log2(pj / np.outer(px, py)[nz])).sum()))
        return np.array(out)
    def perm(self, rng):
        o = np.lexsort((rng.random(self.nw), self.pg)); Lo = self.L[o]
        ns = np.r_[0, np.cumsum(Lo)[:-1]]
        idx = np.arange(self.n) - np.repeat(ns, Lo) + np.repeat(self.S[o], Lo)
        return self.x[idx]
    def test(self, rng, r):
        m = self.mi(self.x); nul = np.array([self.mi(self.perm(rng)) for _ in range(r)])
        M, Ms = m.sum(), nul.sum(1)
        return dict(M=float(M), null_mean=float(Ms.mean()), null_sd=float(Ms.std(ddof=1)), E=float(M - Ms.mean()),
                    z=float((M - Ms.mean()) / Ms.std(ddof=1)), p=float((1 + (Ms >= M).sum()) / (r + 1)),
                    E_lag={str(d): float(m[i] - nul[:, i].mean()) for i, d in enumerate(LAGS)},
                    units=int(self.n), words=int(self.nw), pages=len(self.pages), K=int(self.K))

def strata(path):
    pages, order = {}, []
    for l in parse(path):
        if l['L'] not in ('A', 'B'): continue
        key = (l['L'], l['page'])
        if key not in pages: pages[key] = []; order.append(key)
        pages[key].append(l['words'])
    return {L: [pages[k] for k in order if k[0] == L] for L in ('A', 'B')}

def pseudo(pages, rng):
    out = []
    for p in pages:
        w = [x for l in p for x in l]; w = [w[i] for i in rng.permutation(len(w))]; q, i = [], 0
        for l in p: q.append(w[i:i + len(l)]); i += len(l)
        out.append(q)
    return out

def plant(pages, rng, q=Q):
    out = []
    for p in pages:
        new = [list(p[0])]
        for l in p[1:]:
            l = list(l)
            if rng.random() < q:
                j = int(rng.integers(len(l))); prev = new[-1]; l[j] = prev[min(j, len(prev) - 1)]
            new.append(l)
        out.append(new)
    return out

def gate(pages, rng):
    fp = pw = 0
    for _ in range(NG):
        ps = pseudo(pages, rng)
        fp += Stream(ps).test(rng, RG)['p'] <= ALPHA
        pw += Stream(plant(ps, rng)).test(rng, RG)['p'] <= ALPHA
    return dict(fpr=int(fp), power=int(pw), pass_=bool(fp <= 2 and pw >= 16))

def gate_job(a):
    i, L, t, pages = a
    return f'{L}_{t}', gate(pages, np.random.default_rng([GSEED, i]))

def holm(ps):
    k = sorted(ps, key=ps.get); m = len(k); out, stop = {}, False
    for i, key in enumerate(k):
        if not stop and ps[key] <= ALPHA / (m - i): out[key] = True
        else: stop = True; out[key] = False
    return out

def recut(words, template):
    """cut a running word list into pages/lines following the template's line word counts; stop when words run out."""
    out, i = [], 0
    for p in template:
        q = []
        for l in p:
            if i + len(l) > len(words): return out
            q.append(words[i:i + len(l)]); i += len(l)
        out.append(q)
    return out

def main():
    outp = sys.argv[1] if len(sys.argv) > 1 else 'analysis/C120_results.json'
    stage = sys.argv[2] if len(sys.argv) > 2 else 'all'
    res = dict(cycle='C120', seeds=dict(main=SEED, gates=GSEED, panel=PSEED, gen=list(GENS)), lags=LAGS, R=R, RG=RG, q=Q)
    S = {t: strata(f) for t, f in FILES}
    jobs = [(i, L, t, S[t][L]) for i, (t, L) in enumerate((t, L) for t in ('ZL3b', 'IT2a') for L in ('A', 'B'))]
    with Pool(4) as P: G = P.map(gate_job, jobs)
    res['gates'] = {k: v for k, v in G}; log('gates', res['gates'])
    rng = np.random.default_rng(SEED); res['H1'] = {}
    for t in ('ZL3b', 'IT2a'):
        for L in ('A', 'B'):
            res['H1'][f'{L}_{t}'] = Stream(S[t][L]).test(rng, R); log('H1', L, t, {k: res['H1'][f'{L}_{t}'][k] for k in ('E', 'z', 'p', 'units')})
    rej = holm({k: v['p'] for k, v in res['H1'].items()}); res['holm'] = rej; ver = {}
    for L in ('A', 'B'):
        ks = [f'{L}_ZL3b', f'{L}_IT2a']
        if not all(res['gates'][k]['pass_'] for k in ks): ver[L] = 'NOT TESTABLE'
        else:
            n = sum(rej[k] for k in ks); ver[L] = 'DETECTED' if n == 2 else 'PARTIAL' if n == 1 else 'NOT DETECTED'
    res['verdict_H1'] = ver; log('verdict', ver)
    tmpl = S['ZL3b']['B']; NB = sum(len(l) for p in tmpl for l in p)
    rng = np.random.default_rng(PSEED); panel = {}
    C = 'data/corpora/'
    nat = [('Latin Caesar', 'pg218.txt'), ('Latin Descartes', 'pg23306.txt'), ('Italian Dante', 'pg1012.txt'),
           ('Spanish Cervantes', 'pg2000.txt'), ('Italian Machiavelli', 'pg56498.txt'), ('Finnish Kivi', 'pg11940.txt'),
           ('Finnish Kalevala', 'pg7000.txt')]
    for name, fn in nat:
        w = [x for l in gutenberg(C + fn) for x in l]
        panel[name] = Stream(recut(w, tmpl), tok=list).test(rng, 200); log('panel', name, panel[name]['E'], panel[name]['z'])
    hw = [x for l in hebrew(C + 'Gen.xml') + hebrew(C + 'Exod.xml') for x in l]
    panel['Hebrew Gen+Exod'] = Stream(recut(hw, tmpl), tok=list).test(rng, 200); log('panel heb', panel['Hebrew Gen+Exod']['E'])
    from c004_generator_sweep import generate
    for s in GENS:
        g = generate({'text.lines_to_create': 4000}, s)
        if not g: panel[f'TS gen {s}'] = None; continue
        w = [x for l in g for x in l]
        panel[f'TS gen {s}'] = Stream(recut(w, tmpl)).test(rng, 200); log('gen', s, panel[f'TS gen {s}']['E'])
    res['panel'] = panel; res['NB_words'] = int(NB)
    V = res['H1']['B_ZL3b']['E']
    natE = [panel[n]['E'] for n, _ in nat] + [panel['Hebrew Gen+Exod']['E']]
    genE = [v['E'] for k, v in panel.items() if k.startswith('TS gen') and v]
    rd = lambda xs: ('inside' if min(xs) <= V <= max(xs) else 'above max' if V > max(xs) else 'below min') if xs else 'n/a'
    res['H2_reading'] = dict(voynich_B_E=V, natural=rd(natE), natural_range=[min(natE), max(natE)],
                             generator=rd(genE), generator_range=[min(genE), max(genE)] if genE else None)
    res['elapsed_s'] = round(time.time() - T0, 1)
    json.dump(res, open(outp, 'w'), indent=1, default=float); log('H2', res['H2_reading'])

if __name__ == '__main__':
    main()
