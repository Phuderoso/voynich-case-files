#!/usr/bin/env python3
"""C131 (NEW FAMILY F-DIAL step 1): are there pages whose vocabulary is a genuine MIXTURE of Currier A and Currier B,
beyond what line-level resampling inside the page's own language x section stratum produces?
See case-file/C131-intermediate-pages.md (the pre-registration) for the full rule; this docstring is a summary.
DATA. C070 parser (P loci, lines >= 5 clean words; tools/c070_word2_sh.parse), ZL3b primary, IT2a replication (descriptive).
 Currier language $L and section $I from the ZL3b page headers for BOTH transcriptions (as C122). Pages without $L: EXCLUDED.
INSTRUMENT. Per page i, profiles P_A, P_B = add-0.5 unigram word-type distributions of all A / all B retained lines with
 page i (and, for pseudo / planted pages, every donor page) removed. lam_i = argmax over lam in {0,.01,..,1} of
 sum_tokens log((1-lam) P_A(w) + lam P_B(w)). d_i = distance from the page's own pole: lam (A pages), 1 - lam (B pages).
NULL N-RUN. Pseudo-page of exactly n_i CONSECUTIVE tokens: whole lines from a uniformly random start line among the OTHER pages of the
 same (L, I) stratum, continuing through the next pages of the stratum (file order, circular, page i skipped; last line
 truncated); donor pages removed from the profiles. R = 200 per page. (Pilot: a scattered-line pool null over-flagged real
 control pages, 19/134 Latin; see case file.)
 p_i = (1 + #{null d >= d_i}) / (R + 1)  (floor 1/201).
PLANT. Page i with round(f * n_lines) of its lines replaced by random whole lines of the OTHER language (same section if that
 section has >= 3 other-language pages, else other-language herbal); foreign donor pages removed from profiles; scored against
 page i's own null. f = 0.5 (gate), 0.25 (descriptive); 20 plants per page per f.
GLOBAL. T_L = # informative pages of language L with p_i <= 0.05; null T from pseudo-manuscripts (replicate r of every page,
 ranked among that page's other R - 1 replicates); rank p and normal-approximation p printed side by side; Holm over {A, B}.
CONTROLS (discrete two-source texts, structure check of the null): Caesar(A)/Descartes(B), Machiavelli(A)/Dante(B),
 Exodus(A)/Genesis(B), each recut into the ZL3b page/line template, strata = contiguous blocks of the template's strata.
Run: python3 tools/c131_intermediate_pages.py struct | run
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import sys, os, re, json, time, math
import numpy as np
from collections import defaultdict, OrderedDict
sys.path.insert(0, os.path.dirname(__file__))
from c070_word2_sh import parse
from c123_mi_para_block import headers
from c003_position_rigidity import gutenberg, hebrew

SEED_NULL, SEED_PLANT, SEED_CNULL, SEED_CPLANT = 11900, 11901, 11902, 11903     # 11904-11909 reserved
R, NPL, FS, ALPHA, ALPHA_PAGE, NMIN, MINPAGES, SMOOTH = 200, 20, (0.5, 0.25), 0.05, 0.05, 40, 4, 0.5
GRID = np.linspace(0, 1, 101)
FILES = [('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')]
CTRL = [('Latin Caesar/Descartes', 'pg218.txt', 'pg23306.txt'), ('Italian Machiavelli/Dante', 'pg56498.txt', 'pg1012.txt'),
        ('Hebrew Exodus/Genesis', 'Exod.xml', 'Gen.xml')]
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)
ZH = headers('data/ZL3b-n.txt')

def ms_pages(path):
    """OrderedDict page -> dict(L, I, lines)"""
    P = OrderedDict()
    for l in parse(path):
        h = ZH.get(l['page'], {})
        P.setdefault(l['page'], dict(L=h.get('L'), I=h.get('I'), lines=[]))['lines'].append(l['words'])
    return P

def ctrl_pages(tmpl, fa, fb):
    """recut text A into the A pages of the template and text B into the B pages (consecutive words, same line lengths)."""
    C = 'data/corpora/'
    def words(f): return [x for l in (hebrew(C + f) if f.endswith('.xml') else gutenberg(C + f)) for x in l]
    W = {'A': words(fa), 'B': words(fb)}; pos = {'A': 0, 'B': 0}; P = OrderedDict()
    for pg, d in tmpl.items():
        L = d['L']
        if L not in ('A', 'B'): continue
        lines = []
        for ln in d['lines']:
            k = len(ln); s = W[L][pos[L]:pos[L] + k]
            if len(s) < k: break
            lines.append(s); pos[L] += k
        if lines: P[pg] = dict(L=L, I=d['I'], lines=lines)
    return P, {k: (pos[k], len(W[k])) for k in 'AB'}

class Inst:
    def __init__(self, P):
        self.P = P; self.names = [p for p in P if P[p]['L'] in ('A', 'B')]
        self.idx = {p: i for i, p in enumerate(self.names)}
        voc = {}
        for p in self.names:
            for ln in P[p]['lines']:
                for w in ln: voc.setdefault(w, len(voc))
        self.voc = voc; self.V = len(voc) + 1
        self.M = np.zeros((len(self.names), self.V), np.int32)
        for i, p in enumerate(self.names):
            for ln in P[p]['lines']:
                for w in ln: self.M[i, voc[w]] += 1
        self.lang = np.array([P[p]['L'] for p in self.names]); self.n = self.M.sum(1)
        self.CL = {L: self.M[self.lang == L].sum(0) for L in 'AB'}; self.NL = {L: int(self.n[self.lang == L].sum()) for L in 'AB'}
        self.strat = defaultdict(list)
        for p in self.names: self.strat[(P[p]['L'], P[p]['I'])].append(p)
    def ids(self, words): return np.array([self.voc[w] for w in words], np.int64)
    def lam(self, tok, excl):
        ex = np.array(sorted(excl), np.int64); pr = {}
        for L in 'AB':
            e = ex[self.lang[ex] == L] if len(ex) else ex
            c = self.CL[L][tok] - (self.M[e][:, tok].sum(0) if len(e) else 0); n = self.NL[L] - (int(self.n[e].sum()) if len(e) else 0)
            pr[L] = (c + SMOOTH) / (n + SMOOTH * self.V)
        ll = np.log((1 - GRID)[:, None] * pr['A'][None, :] + GRID[:, None] * pr['B'][None, :]).sum(1)
        return float(GRID[int(np.argmax(ll))])
    def d(self, lam, L): return lam if L == 'A' else 1.0 - lam
    def status(self, p):
        L, I = self.P[p]['L'], self.P[p]['I']; ntok = int(self.n[self.idx[p]])
        if len(self.strat[(L, I)]) < MINPAGES: return 'NOT TESTABLE (stratum < 4 pages)'
        if ntok < NMIN: return 'NOT TESTABLE (< 40 tokens)'
        pool = sum(int(self.n[self.idx[q]]) for q in self.strat[(L, I)] if q != p)
        if pool < ntok: return 'NOT TESTABLE (pool too small)'
        return 'INFORMATIVE'
    def pseudo(self, p, rng):
        """N-RUN: n_i consecutive tokens (whole lines, last truncated) from a uniformly random start line among the OTHER pages of the
        stratum, continuing through the following pages of the stratum in file order (circular, page i skipped)."""
        L, I = self.P[p]['L'], self.P[p]['I']; need = int(self.n[self.idx[p]])
        seq = [q for q in self.strat[(L, I)] if q != p]
        flat = [(q, ln) for q in seq for ln in self.P[q]['lines']]
        j = int(rng.integers(len(flat))); out, don = [], set()
        while len(out) < need:
            q, ln = flat[j % len(flat)]; out.extend(ln[:need - len(out)]); don.add(self.idx[q]); j += 1
        return self.ids(out), don | {self.idx[p]}
    def foreign_pool(self, p):
        L, I = self.P[p]['L'], self.P[p]['I']; o = 'B' if L == 'A' else 'A'
        fp = self.strat.get((o, I), [])
        if len(fp) < 3: fp = self.strat.get((o, 'H'), [])
        return [(q, ln) for q in fp for ln in self.P[q]['lines']]
    def plant(self, p, f, rng):
        lines = self.P[p]['lines']; k = int(round(f * len(lines))); pool = self.foreign_pool(p)
        rep = set(rng.choice(len(lines), size=k, replace=False).tolist()) if k else set(); out, don = [], {self.idx[p]}
        for li, ln in enumerate(lines):
            if li in rep:
                q, fl = pool[int(rng.integers(len(pool)))]; out.extend(fl); don.add(self.idx[q])
            else: out.extend(ln)
        return self.ids(out), don

def run_set(P, tag, seed_null, seed_plant, ti, plants=True):
    I = Inst(P); res = OrderedDict(); NULL = {}
    for pi, p in enumerate(I.names):
        L = I.P[p]['L']; st = I.status(p); i = I.idx[p]
        tok = I.ids([w for ln in I.P[p]['lines'] for w in ln]); lam = I.lam(tok, {i}); d0 = I.d(lam, L)
        r = dict(L=L, I=I.P[p]['I'], ntok=int(I.n[i]), nlines=len(I.P[p]['lines']), status=st, lam=lam, d=d0)
        if st == 'INFORMATIVE':
            rng = np.random.default_rng([seed_null, ti, pi]); nd = []
            for _ in range(R):
                t, ex = I.pseudo(p, rng); nd.append(I.d(I.lam(t, ex), L))
            nd = np.array(nd); NULL[p] = nd
            r['p'] = float((1 + (nd >= d0 - 1e-12).sum()) / (R + 1)); r['null_d_mean'] = float(nd.mean()); r['null_d_q95'] = float(np.quantile(nd, 0.95))
            if plants:
                for fi, f in enumerate(FS):
                    rng2 = np.random.default_rng([seed_plant, ti, pi, fi]); hit = 0; dd = []
                    for _ in range(NPL):
                        t, ex = I.plant(p, f, rng2); dp = I.d(I.lam(t, ex), L); dd.append(dp)
                        hit += (1 + (nd >= dp - 1e-12).sum()) / (R + 1) <= ALPHA_PAGE
                    r[f'plant_{f}'] = dict(hits=int(hit), n=NPL, d_mean=float(np.mean(dd)))
        res[p] = r
    return I, res, NULL

def global_T(res, NULL, L):
    pages = [p for p, r in res.items() if r['status'] == 'INFORMATIVE' and r['L'] == L]
    T = sum(res[p]['p'] <= ALPHA_PAGE for p in pages)
    if not pages: return dict(n_inf=0)
    Tn = np.zeros(R, int)
    for p in pages:
        nd = NULL[p]
        for r in range(R):
            pr = (1 + (np.delete(nd, r) >= nd[r] - 1e-12).sum()) / R
            Tn[r] += pr <= ALPHA_PAGE
    rank_p = float((1 + (Tn >= T).sum()) / (R + 1)); mu, sd = float(Tn.mean()), float(Tn.std(ddof=1))
    norm_p = float(0.5 * math.erfc((T - mu) / (sd * math.sqrt(2)))) if sd > 0 else (0.0 if T > mu else 1.0)
    return dict(n_inf=len(pages), T=int(T), null_T_mean=mu, null_T_sd=sd, null_T_max=int(Tn.max()), rank_p=rank_p, norm_p=norm_p,
                share=T / len(pages))

def bh(ps, q):
    o = np.argsort(ps); m = len(ps); k = 0
    for j, idx in enumerate(o, 1):
        if ps[idx] <= q * j / m: k = j
    return set(o[:k].tolist())

def wilson(k, n):
    if n == 0: return (0, 1)
    z = 1.96; ph = k / n; den = 1 + z * z / n; c = (ph + z * z / (2 * n)) / den; h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return (max(0, c - h), min(1, c + h))

def summarise(res, NULL):
    S = dict(strata={}, global_={}, power={}, pages={})
    for p, r in res.items():
        k = f"{r['L']}-{r['I']}"; s = S['strata'].setdefault(k, defaultdict(int)); s['pages'] += 1; s[r['status']] += 1
    for L in 'AB':
        S['global_'][L] = global_T(res, NULL, L)
        inf = [p for p, r in res.items() if r['status'] == 'INFORMATIVE' and r['L'] == L]
        for f in FS:
            key = f'plant_{f}'
            if inf and key in res[inf[0]]:
                h = sum(res[p][key]['hits'] for p in inf); n = sum(res[p][key]['n'] for p in inf)
                S['power'][f'{L}_{f}'] = dict(hits=h, n=n, rate=h / n, pages_ge16=sum(res[p][key]['hits'] >= 16 for p in inf), n_pages=len(inf))
        ps = np.array([res[p]['p'] for p in inf]); dis = bh(ps, 0.10) if len(ps) else set()
        for j, p in enumerate(inf):
            r = res[p]
            if j in dis: cls = 'INTERMEDIATE (BH q 0.10)'
            elif 'plant_0.5' in r and r['plant_0.5']['hits'] >= 16: cls = 'EXCLUDED (mixture f 0.5 ruled out)'
            elif 'plant_0.5' in r: cls = 'NOT TESTABLE (page power < 16/20)'
            else: cls = 'no plants'
            r['class'] = cls
        lam_inf = [res[p]['lam'] for p in inf]
        S['global_'][L]['lam_mid_share'] = float(np.mean([0.25 <= x <= 0.75 for x in lam_inf])) if inf else None
        S['global_'][L]['mean_d'] = float(np.mean([res[p]['d'] for p in inf])) if inf else None
        S['global_'][L]['mean_null_d'] = float(np.mean([res[p]['null_d_mean'] for p in inf])) if inf else None
    for p, r in res.items():
        if 'class' not in r: r['class'] = r['status'] if r['status'] != 'INFORMATIVE' else r.get('class')
    return S

def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0] * len(ps); run = 0
    for k, i in enumerate(o):
        run = max(run, min(1, (len(ps) - k) * ps[i])); adj[i] = run
    return adj

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'struct'
    tmpl = ms_pages(FILES[0][1])
    if mode == 'struct':
        for t, f in FILES:
            P = ms_pages(f); I = Inst(P); c = defaultdict(lambda: defaultdict(int))
            for p in I.names: c[f"{P[p]['L']}-{P[p]['I']}"][I.status(p)] += 1
            excl = [p for p in P if P[p]['L'] not in ('A', 'B')]
            print(t, 'tokens A/B', I.NL, 'V', I.V, 'excluded (no $L):', len(excl), excl)
            for k in sorted(c): print('  ', k, dict(c[k]))
        for name, fa, fb in CTRL:
            P, use = ctrl_pages(tmpl, fa, fb); print(name, 'words used/available', use, 'pages', len(P))
        return
    out = dict(seeds=dict(null=SEED_NULL, plant=SEED_PLANT, cnull=SEED_CNULL, cplant=SEED_CPLANT), R=R, NPL=NPL, FS=FS, NMIN=NMIN,
               files={t: f for t, f in FILES}, manuscript={}, controls={})
    for ti, (t, f) in enumerate(FILES):
        log('manuscript', t); I, res, NULL = run_set(ms_pages(f), t, SEED_NULL, SEED_PLANT, ti)
        S = summarise(res, NULL); out['manuscript'][t] = dict(summary=S, pages=res); log(t, json.dumps(S['global_']), json.dumps(S['power']))
        json.dump(out, open('analysis/C131_results.json', 'w'), indent=1, default=float)
    for ci, (name, fa, fb) in enumerate(CTRL):
        log('control', name); P, use = ctrl_pages(tmpl, fa, fb)
        I, res, NULL = run_set(P, name, SEED_CNULL, SEED_CPLANT, ci, plants=True)
        S = summarise(res, NULL); inf = [p for p, r in res.items() if r['status'] == 'INFORMATIVE']
        k = sum(res[p]['p'] <= ALPHA_PAGE for p in inf)
        S['fpr'] = dict(flagged=k, n=len(inf), share=k / max(1, len(inf)), wilson=wilson(k, len(inf)), gate_ok=bool(k / max(1, len(inf)) <= 0.10))
        S['words_used'] = use; out['controls'][name] = dict(summary=S, pages=res); log(name, json.dumps(S['fpr']), json.dumps(S['global_']), json.dumps(S['power']))
        json.dump(out, open('analysis/C131_results.json', 'w'), indent=1, default=float)
    # gates and verdict (ZL3b primary)
    Z = out['manuscript']['ZL3b']['summary']
    g_fpr = all(out['controls'][n]['summary']['fpr']['gate_ok'] for n, _, _ in CTRL)
    g_pow = {L: Z['power'][f'{L}_0.5']['rate'] >= 0.80 for L in 'AB'}
    raw = [Z['global_'][L]['rank_p'] for L in 'AB']; adj = holm(raw)
    V = {}
    for j, L in enumerate('AB'):
        if not (g_fpr and g_pow[L]): V[L] = 'NOT TESTABLE (gates)'
        elif adj[j] <= ALPHA: V[L] = 'EXCESS INTERMEDIATE PAGES'
        else: V[L] = 'NO EXCESS (discrete at f 0.5 resolution)'
    out['verdict'] = dict(G_FPR=g_fpr, G_POW=g_pow, rank_p=raw, holm=adj, verdict=V)
    json.dump(out, open('analysis/C131_results.json', 'w'), indent=1, default=float); log('VERDICT', json.dumps(out['verdict']))

if __name__ == '__main__': main()
