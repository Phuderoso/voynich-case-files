#!/usr/bin/env python3
"""C066 (new family F-CROSS, step 1): are SECTION-DIAGNOSTIC word types spelling variants of words used in OTHER sections
(vocabulary 'transfer' by small changes, as the self-citation account and Timm & Schinner's single word network suggest), or
lexically separate (as topic words in natural multi-topic texts tend to be)?
Corpus: paragraph text (C047 parser) of pages with $I in {H, B, P, S} (herbal, balneo/biological, pharma, stars); glyph units (C003).
Per type w with frequency f >= 4: home section h(w) = argmax count; diagnostic if binomial upper tail
 P(X >= c_h | f, n_h/N) < 0.001. O(w) = 1 if some other type v at glyph-unit Levenshtein distance 1 has >= 2 tokens OUTSIDE h(w).
Statistic D = stratum-weighted mean of [mean O(diagnostic) - mean O(non-diagnostic)] over strata (home section x frequency bin
 {4-5,6-9,10-19,20-49,50+} x length bin {<=3,4,5,6,>=7 units}), weights = #diagnostic in stratum; strata lacking either group skipped.
 D < 0: diagnostic types are more isolated than matched types; D > 0: more connected to other sections' vocabulary.
Primary tests (BH q = 0.05 over 4):
 HA (generator-referenced) Voynich D (ZL, IT2a) vs 40 default Timm-Schinner runs (4,200 lines, FRESH seeds 7701-7760, first 40
   with enough tokens), each cut to the same token count and split into 4 consecutive pseudo-sections with the manuscript's section
   token shares in manuscript order (H, B, P, S). Two-sided rank p (floor 1/41 = 0.0244).
   Gates on 20 held-out default runs (seeds 7801-7830, first 20 long enough): FPR (p <= 0.05) <= 2/20; power >= 16/20 for the
   ISOLATION plant (15% of that text's diagnostic types, all tokens, get a unique marker glyph -> no neighbours), p <= 0.05 and below median.
 HB (structure-preserving null) Voynich true-section D vs 1,000 relabellings that permute section labels among pages WITHIN
   Currier language x scribal hand ($L x $H) strata (section page counts per stratum kept). Two-sided p = (1+#|null-mean|>=|obs-mean|)/(n+1).
   Gates: FPR — 20 relabelled Voynich texts treated as truth, each vs 200 further relabellings: p <= 0.05 in <= 2/20;
   power — 20 isolation plants (15%) on the true sections, each vs 200 relabellings of the planted text: p <= 0.05 and below in >= 16/20.
Secondary (descriptive): 12 natural texts (C058 set) cut to min(own length, manuscript token count) (texts < 16,000 tokens dropped;
 6 of 12 are shorter than the manuscript, disclosed N-dependence), same 4-block split;
 LOO outside-range <= 3/12, then INSIDE / OUTSIDE-side. Exact within-stratum label-permutation p for D != 0 (2,000 perms), raw rates.
Verdicts: per test BH-rejected -> ABOVE/BELOW; not rejected -> NO DIFFERENCE SHOWN (powered); gate fails -> NOT TESTABLE (not excluded).
Seed 6666. Pre-registered in case-file/C066-cross-section-neighbours.md. Run: timeout 600 python3 tools/c066_cross_section_neighbours.py
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, re, json, time
from multiprocessing import Pool
import numpy as np
from math import lgamma
sys.path.insert(0, os.path.dirname(__file__))
import c058_edit_neighbours as E
import c055_burstiness as C
import c003_position_rigidity as T
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate

SEED = 6666; SECTS = ('H', 'B', 'P', 'S'); PDIAG = 1e-3; FMIN = 4; PLANT = 0.15
NREF, NHO, NPERM_B, NG, NPERM_G, NPERM_L = 40, 20, 1000, 20, 200, 2000
FILES = (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt'))
REF_SEEDS, HO_SEEDS = range(7701, 7761), range(7801, 7831); LINES = 4200
NAT_MIN = 16000; FB = (4, 6, 10, 20, 50); LB = (3, 4, 5, 6)

def neighbours(types):
    """sparse symmetric adjacency, glyph-unit Levenshtein distance exactly 1"""
    idx = {t: i for i, t in enumerate(types)}; rows, cols = [], []
    sub = {}
    for i, t in enumerate(types):
        for j in range(len(t)):
            sub.setdefault((t[:j] + t[j + 1:], j), []).append(i)  # substitution key
            d = t[:j] + t[j + 1:]
            if d in idx: rows.append(i); cols.append(idx[d])     # deletion -> shorter type exists
    for g in sub.values():
        if len(g) > 1:
            for a in g:
                for b in g:
                    if a != b: rows.append(a); cols.append(b)
    e = {(a, b) for a, b in zip(rows, cols)} | {(b, a) for a, b in zip(rows, cols)}
    e = np.array(sorted(e), dtype=np.int64).reshape(-1, 2); return e[:, 0], e[:, 1]

LG = np.array([lgamma(i + 1) for i in range(200001)])

def binom_sf(c, f, p):
    """P(X >= c), X ~ Bin(f, p), exact, vectorised (numpy only)"""
    c = c.astype(np.int64); f = f.astype(np.int64); n = f - c + 1; idx = np.repeat(np.arange(len(f)), n)
    x = c[idx] + (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)); ff = f[idx]; pp = np.clip(p[idx], 1e-300, 1 - 1e-16)
    lt = LG[ff] - LG[x] - LG[ff - x] + x * np.log(pp) + (ff - x) * np.log1p(-pp)
    return np.minimum(1.0, np.bincount(idx, weights=np.exp(lt), minlength=len(f)))

class Corpus:
    """docs = list of (unit-tuple tokens) per page/block; labels give the section of each doc"""
    def __init__(self, docs):
        types = sorted({w for d in docs for w in d}); self.types = types; ix = {t: i for i, t in enumerate(types)}
        r, c = [], []
        for k, d in enumerate(docs):
            for w in d: r.append(k); c.append(ix[w])
        self.td, self.tt = np.array(r), np.array(c); self.V = len(types)
        self.er, self.ec = neighbours(types); self.f = np.bincount(self.tt, minlength=self.V).astype(float)
        L = np.array([len(t) for t in types]); self.lb = np.searchsorted(LB, L, side='left')
        self.fb = np.searchsorted(FB, self.f, side='right') - 1
    def D(self, lab, detail=False):
        lab = np.asarray(lab); ns = len(SECTS)
        Cs = np.bincount(lab[self.td] * self.V + self.tt, minlength=ns * self.V).reshape(ns, self.V).astype(float)
        n = Cs.sum(1); N = n.sum(); keep = self.f >= FMIN; h = Cs.argmax(0); ch = Cs[h, np.arange(self.V)]
        p = np.ones(self.V); p[keep] = binom_sf(ch[keep], self.f[keep], (n[h] / N)[keep]); diag = keep & (p < PDIAG)
        O = np.zeros(self.V, bool)
        for s in range(ns):
            X = (self.f - Cs[s]) >= 2; Y = np.zeros(self.V, bool); Y[self.er[X[self.ec]]] = True; O[h == s] = Y[h == s]
        st = h * 100 + self.fb * 10 + self.lb
        return dstat(st, keep, diag, O, detail)

def dstat(st, keep, diag, O, detail=False):
    num = den = 0.0
    for k in np.unique(st[keep]):
        m = keep & (st == k); a = m & diag; b = m & ~diag
        if a.any() and b.any(): w = a.sum(); num += w * (O[a].mean() - O[b].mean()); den += w
    D = num / den if den else float('nan')
    if not detail: return D
    return dict(D=D, n_types=int(keep.sum()), n_diag=int(diag.sum()), n_diag_matched=int(den),
                O_diag=float(O[diag].mean()) if diag.any() else None, O_other=float(O[keep & ~diag].mean()),
                _st=st, _keep=keep, _diag=diag, _O=O)

def label_perm_p(d, rng, n=NPERM_L):
    st, keep, diag, O = d['_st'], d['_keep'], d['_diag'], d['_O']; obs = d['D']; nl = []
    ks = np.where(keep)[0]
    for _ in range(n):
        dg = diag.copy()
        for k in np.unique(st[ks]):
            m = ks[st[ks] == k]; dg[m] = rng.permutation(diag[m])
        nl.append(dstat(st, keep, dg, O))
    nl = np.array(nl); return float((1 + np.sum(np.abs(nl) >= abs(obs))) / (n + 1))

def plant(docs, lab, rng, frac=PLANT):
    c = Corpus(docs); d = c.D(lab, True); dg = np.where(d['_diag'])[0]
    pick = set(c.types[i] for i in rng.choice(dg, max(1, int(round(frac * len(dg)))), replace=False))
    return [[(w + ('#',)) if w in pick else w for w in doc] for doc in docs]

def relabel(lab, strata, rng):
    out = lab.copy()
    for s in np.unique(strata):
        m = np.where(strata == s)[0]; out[m] = rng.permutation(lab[m])
    return out

def hb_test(docs, lab, strata, rng, n):
    c = Corpus(docs); obs = c.D(lab); nl = np.array([c.D(relabel(lab, strata, rng)) for _ in range(n)]); mu = nl.mean()
    return dict(obs=float(obs), null_mean=float(mu), null_sd=float(nl.std()), p=float((1 + np.sum(np.abs(nl - mu) >= abs(obs - mu))) / (n + 1)))

def voynich(path):
    pl, lang, sect = ivtff_pages_lang(path); hand = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        h = re.match(r'<(f\w+)>\s+<!(.*)>', line)
        if h: m = re.search(r'\$H=(\w)', h.group(2)); hand[h.group(1)] = m.group(1) if m else '?'
    pages = {}
    for p, ws in pl:
        if sect.get(p) in SECTS: pages.setdefault(p, []).extend(tuple(T.units(w)) for w in ws)
    ps = list(pages); docs = [pages[p] for p in ps]; lab = np.array([SECTS.index(sect[p]) for p in ps])
    strata = np.array([f'{lang.get(p)}{hand.get(p)}' for p in ps]); return ps, docs, lab, strata

def blocks(toks, shares):
    cut = np.round(np.cumsum(shares) * len(toks)).astype(int); out, a = [], 0
    for b in cut: out.append(toks[a:b]); a = b
    return out, np.arange(len(SECTS))

def gen_job(a):
    s, Ns, shares = a; Lg = generate({'text.lines_to_create': LINES}, s)
    t = [tuple(T.units(w)) for w in C.flat(Lg)] if Lg else []
    if len(t) < max(Ns): return s, None
    rng = np.random.default_rng(SEED * 10000 + s); r = {}
    for k, N in Ns.items():
        docs, lab = blocks(t[:N], shares); r[k] = dict(plain=Corpus(docs).D(lab))
        if s in HO_SEEDS: r[k]['plant'] = Corpus(plant(docs, lab, rng)).D(lab)
    return s, r

def rank_p(v, ref):
    ref = np.asarray(ref); m = float(np.median(ref)); return float((1 + np.sum(np.abs(ref - m) >= abs(v - m))) / (len(ref) + 1))

def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps); o = np.argsort(ps); ok = ps[o] <= q * np.arange(1, m + 1) / m
    k = np.max(np.where(ok)[0]) + 1 if ok.any() else 0; rej = np.zeros(m, bool); rej[o[:k]] = True; return rej

def hb_gate_job(a):
    kind, i, docs, lab, strata = a; rng = np.random.default_rng(SEED + 1000 * (kind == 'pw') + i)
    if kind == 'fp': L2 = relabel(lab, strata, rng); r = hb_test(docs, L2, strata, rng, NPERM_G)
    else: r = hb_test(plant(docs, lab, rng), lab, strata, rng, NPERM_G)
    return kind, i, r

def main():
    t0 = time.time(); R = dict(seed=SEED, files=[f for _, f in FILES]); V = {}
    for k, f in FILES:
        ps, docs, lab, strata = voynich(f); n = np.array([sum(len(d) for d, l in zip(docs, lab) if l == s) for s in range(4)])
        V[k] = dict(pages=ps, docs=docs, lab=lab, strata=strata, N=int(n.sum()), sect_tokens=n.tolist())
    shares = np.array(V['ZL3b']['sect_tokens']) / V['ZL3b']['N']; Ns = {k: V[k]['N'] for k in V}
    R['voynich_tokens'] = {k: dict(N=V[k]['N'], by_section=dict(zip(SECTS, V[k]['sect_tokens'])), pages=len(V[k]['pages'])) for k in V}
    R['strata'] = {k: {s: {SECTS[x]: int(np.sum((V[k]['strata'] == s) & (V[k]['lab'] == x))) for x in range(4)} for s in np.unique(V[k]['strata'])} for k in V}
    gjobs = [(s, Ns, shares) for s in list(REF_SEEDS) + list(HO_SEEDS)]
    hjobs = [(kind, i, V[k]['docs'], V[k]['lab'], V[k]['strata']) for k in ('ZL3b',) for kind in ('fp', 'pw') for i in range(NG)]
    with Pool(8) as P:
        ga = P.map_async(gen_job, gjobs, chunksize=1); hg = P.map(hb_gate_job, hjobs, chunksize=1); gres = ga.get()
    print('pool done', round(time.time() - t0, 1), flush=True)
    G = {s: r for s, r in sorted(gres) if r is not None}
    ref = [s for s in REF_SEEDS if s in G][:NREF]; ho = [s for s in HO_SEEDS if s in G][:NHO]
    R['gen_seeds_used'] = dict(ref=ref, ho=ho)
    # Voynich statistics
    rng = np.random.default_rng(SEED); vs = {}
    for k in V:
        d = Corpus(V[k]['docs']).D(V[k]['lab'], True); lp = label_perm_p(d, rng)
        vs[k] = {a: b for a, b in d.items() if not a.startswith('_')}; vs[k]['label_perm_p'] = lp
        vs[k]['HB'] = hb_test(V[k]['docs'], V[k]['lab'], V[k]['strata'], rng, NPERM_B)
    R['voynich'] = vs
    # gates
    gates = {}
    for k in V:
        refk = [G[s][k]['plain'] for s in ref]; med = float(np.median(refk))
        fp = sum(rank_p(G[s][k]['plain'], refk) <= 0.05 for s in ho)
        pw = sum(rank_p(G[s][k]['plant'], refk) <= 0.05 and G[s][k]['plant'] < med for s in ho)
        gates[f'HA_{k}'] = dict(fp=fp, power=pw, n_ref=len(ref), n_ho=len(ho), ref_range=(min(refk), med, max(refk)),
                                plant_shift_median=float(np.median([G[s][k]['plant'] - G[s][k]['plain'] for s in ho])),
                                passed=len(ref) >= NREF and len(ho) >= NHO and fp <= 2 and pw >= 16)
    fpB = sum(r['p'] <= 0.05 for kind, i, r in hg if kind == 'fp')
    pwB = sum(r['p'] <= 0.05 and r['obs'] < r['null_mean'] for kind, i, r in hg if kind == 'pw')
    gB = dict(fp=fpB, power=pwB, n=NG, plant_obs_median=float(np.median([r['obs'] for kind, i, r in hg if kind == 'pw'])),
              passed=fpB <= 2 and pwB >= 16, note='gates measured on ZL 3b, applied to both transcriptions')
    gates['HB_ZL3b'] = gB; gates['HB_IT2a'] = gB; R['gates'] = gates
    tests = []
    for k in V:
        refk = [G[s][k]['plain'] for s in ref]
        tests.append((f'HA_{k}', vs[k]['D'], rank_p(vs[k]['D'], refk), float(np.median(refk))))
        tests.append((f'HB_{k}', vs[k]['HB']['obs'], vs[k]['HB']['p'], vs[k]['HB']['null_mean']))
    gt = [t for t in tests if gates[t[0]]['passed']]; rej = bh([t[2] for t in gt]) if gt else []
    TT = {}
    for t in tests: TT[t[0]] = dict(v=t[1], p=t[2], centre=t[3], side='above' if t[1] > t[3] else 'below', gate=gates[t[0]]['passed'])
    for t, r in zip(gt, rej): TT[t[0]]['bh_reject'] = bool(r)
    for k, x in TT.items():
        x['verdict'] = 'NOT TESTABLE' if not x['gate'] else (x['side'].upper() if x['bh_reject'] else 'NO DIFFERENCE SHOWN')
    R['tests'] = TT
    # natural, descriptive
    nat = E.nat_units(); Nn = min(Ns.values()); natD, dropped = {}, []
    for name, t in nat.items():
        if len(t) < NAT_MIN: dropped.append((name, len(t))); continue
        n_ = min(len(t), Nn); docs, lab = blocks(t[:n_], shares); d = Corpus(docs).D(lab, True)
        natD[name] = dict(N=n_, D=d['D'], n_diag=d['n_diag'], O_diag=d['O_diag'], O_other=d['O_other'])
    vals = {a: b['D'] for a, b in natD.items()}
    if vals:
        lo, hi = min(vals.values()), max(vals.values())
        loo = sum((vals[a] < min(vals[b] for b in vals if b != a)) or (vals[a] > max(vals[b] for b in vals if b != a)) for a in vals) if len(vals) > 2 else None
        cl = {k: ('below' if vs[k]['D'] < lo else 'above' if vs[k]['D'] > hi else 'inside') for k in V}
        R['natural'] = dict(N=Nn, D=natD, dropped=dropped, range=(lo, hi), loo_outside=loo, n=len(vals),
                            verdict=({k: ('INSIDE' if c == 'inside' else 'OUTSIDE-' + c.upper()) for k, c in cl.items()} if loo is not None and loo <= max(3, len(vals) // 4) else 'NOT TESTABLE'))
    else: R['natural'] = dict(dropped=dropped, verdict='NOT TESTABLE (no text long enough)')
    R['generator_detail'] = {str(s): G[s] for s in ref + ho}; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C066_results.json', 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else float(o))
    print('tokens', R['voynich_tokens']); print('strata', R['strata'])
    for k in vs: print('VOY', k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in vs[k].items()})
    print('GATES', json.dumps(gates, default=float)); print('TESTS', json.dumps(TT, default=float))
    print('NAT', json.dumps(R['natural'], default=float)); print('runtime', R['runtime_s'])

if __name__ == '__main__': main()
