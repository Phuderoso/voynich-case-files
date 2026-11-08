#!/usr/bin/env python3
"""C067 (F-CROSS step 2): CONFIRMATORY test of the C066 post-hoc lead (the hypothesis was SUGGESTED BY C066 DATA; the manuscript
values at this threshold were already seen in C066's post-hoc file, so only the generator seeds below are fresh data).
Definitions as C066 (tools/c066_cross_section_neighbours.py): paragraph text of pages with $I in {H,B,P,S}; glyph units (C003);
types with f >= 4; home section h(w) = argmax; diagnostic if exact binomial upper tail < 0.001.
NEW fixed threshold: O10(w) = 1 if some other type v at glyph-unit Levenshtein distance 1 has >= 10 tokens OUTSIDE h(w).
Primary statistics: S10 = mean O10 over diagnostic types; D10 = stratum-matched difference O10(diag) - O10(non-diag) (C066 strata).
Primary tests (BH q = 0.05 over the 4 tests that pass their gates):
 T1/T2 S10 (ZL 3b / IT2a) vs 40 default Timm-Schinner runs (4,200 lines, FRESH seeds 8201-8260, first 40 long enough), cut to the
   transcription's token count, 4 consecutive pseudo-sections with the manuscript's section token shares. Two-sided rank p
   (floor 1/41). Gates on 20 held-out runs (FRESH seeds 8301-8330, first 20 long enough): FPR (p <= 0.05) <= 2/20;
   power >= 16/20 for the CONNECTION plant (the direction predicted by the C066 lead): for diagnostic types with O10 = 0,
   chosen at random, up to CONN_FRAC x n_diag of them, 10 random tokens outside the home section are replaced by w + marker (a new
   one-glyph neighbour with 10 outside tokens), success = p <= 0.05 and above the reference median. The ISOLATION plant (15% of
   diagnostic types renamed with a unique marker, all tokens) is reported as a downward power check (not a gate).
 T3/T4 D10 (ZL 3b / IT2a) vs 2,000 permutations of the diagnostic label among types WITHIN C066 strata (home section x frequency
   bin x length bin), two-sided. This null permutes type labels, not page labels, so a plant on the diagnostic types cannot be
   absorbed (the C066 HB flaw: page relabelling within Currier x hand barely moves pages, because section ~ stratum).
   Gates on ZL 3b: FPR — 20 random pseudo-diagnostic sets (same per-stratum counts, drawn from all types in the stratum), each vs
   500 permutations: p <= 0.05 in <= 2/20; power — 20 isolation plants (15% of true diagnostic types), each vs 500 permutations:
   p <= 0.05 and D below the null mean in >= 16/20.
Verdicts: gate fails -> NOT TESTABLE (not excluded); gate passes, BH-rejected -> ABOVE / BELOW; not rejected -> NO DIFFERENCE SHOWN.
Secondary (descriptive, no BH): natural texts with >= 29,000 tokens (C058 set; 8 texts), cut to min(len, N), same 4-block split;
 LOO outside-range <= 3 -> INSIDE / OUTSIDE-ABOVE/BELOW (these texts were also seen in the C066 post-hoc: not fresh).
 Threshold sensitivity (5, 20) for manuscript and generator reference, descriptive. D10 vs generator, descriptive.
Seed 6767. Pre-registered in case-file/C067-cross-threshold10.md. Run from repo root: timeout 600 python3 tools/c067_cross_threshold10.py
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c066_cross_section_neighbours as X

SEED = 6767; THR = 10; CONN_FRAC = 0.12; ISO = 0.15
NREF, NHO, NG, NPERM, NPERM_G = 40, 20, 20, 2000, 500
REF_SEEDS, HO_SEEDS = range(8201, 8261), range(8301, 8331)
NAT_MIN = 29000; SENS = (5, 20)

def stats(c, lab, thr=THR, detail=False):
    """S10, D10 and arrays for one corpus (c = X.Corpus) and labels"""
    d = c.D(lab, True); lab = np.asarray(lab); ns = 4
    Cs = np.bincount(lab[c.td] * c.V + c.tt, minlength=ns * c.V).reshape(ns, c.V).astype(float); h = Cs.argmax(0); O = np.zeros(c.V, bool)
    for s in range(ns):
        Xs = (c.f - Cs[s]) >= thr; Y = np.zeros(c.V, bool); Y[c.er[Xs[c.ec]]] = True; O[h == s] = Y[h == s]
    diag, keep, st = d['_diag'], d['_keep'], d['_st']
    S = float(O[diag].mean()) if diag.any() else float('nan'); D = float(X.dstat(st, keep, diag, O))
    r = dict(S=S, D=D, n_diag=int(diag.sum()), O_other=float(O[keep & ~diag].mean()))
    if detail: r.update(_O=O, _diag=diag, _keep=keep, _st=st, _h=h, _Cs=Cs)
    return r

def perm_p(st, keep, diag, O, rng, n):
    obs = X.dstat(st, keep, diag, O); ks = np.where(keep)[0]; groups = [ks[st[ks] == k] for k in np.unique(st[ks])]; nl = np.empty(n)
    for i in range(n):
        dg = diag.copy()
        for m in groups: dg[m] = rng.permutation(diag[m])
        nl[i] = X.dstat(st, keep, dg, O)
    mu = nl.mean(); return float(obs), float(mu), float((1 + np.sum(np.abs(nl - mu) >= abs(obs - mu))) / (n + 1))

def connect_plant(docs, lab, rng, frac=CONN_FRAC):
    """raise S10: for random diagnostic types with O10 = 0, replace 10 random outside-home tokens by w + marker"""
    c = X.Corpus(docs); r = stats(c, lab, detail=True); lab = np.asarray(lab)
    cand = np.where(r['_diag'] & ~r['_O'])[0]; k = min(len(cand), int(round(frac * r['n_diag'])))
    docs = [list(d) for d in docs]; pos = [(i, j) for i, d in enumerate(docs) for j in range(len(d))]; used = set()
    for t in rng.choice(cand, k, replace=False) if k else []:
        w = c.types[t]; hs = r['_h'][t]; outside = [p for p in pos if lab[p[0]] != hs and p not in used]
        for q in rng.choice(len(outside), 10, replace=False):
            i, j = outside[q]; used.add((i, j)); docs[i][j] = w + ('+',)
    return docs, k

def iso_plant(docs, lab, rng, frac=ISO):
    return X.plant(docs, lab, rng, frac)

def gen_job(a):
    s, Ns, shares = a; Lg = X.generate({'text.lines_to_create': X.LINES}, s)
    t = [tuple(X.T.units(w)) for w in X.C.flat(Lg)] if Lg else []
    if len(t) < max(Ns.values()): return s, None
    rng = np.random.default_rng(SEED * 10000 + s); r = {}
    for k, N in Ns.items():
        docs, lab = X.blocks(t[:N], shares); c = X.Corpus(docs); r[k] = dict(plain=stats(c, lab))
        r[k]['sens'] = {str(th): stats(c, lab, th)['S'] for th in SENS}
        if s in HO_SEEDS:
            pd, kk = connect_plant(docs, lab, rng); r[k]['conn'] = stats(X.Corpus(pd), lab); r[k]['conn_k'] = kk
            r[k]['iso'] = stats(X.Corpus(iso_plant(docs, lab, rng)), lab)
    return s, r

def dgate_job(a):
    kind, i, docs, lab = a; rng = np.random.default_rng(SEED + 1000 * (kind == 'pw') + i)
    if kind == 'pw': docs = iso_plant(docs, lab, rng)
    r = stats(X.Corpus(docs), lab, detail=True); diag = r['_diag']
    if kind == 'fp':  # random pseudo-diagnostic set with the same per-stratum counts
        st, keep = r['_st'], r['_keep']; dg = np.zeros_like(diag)
        for k in np.unique(st[keep]):
            m = np.where(keep & (st == k))[0]; n = int(diag[m].sum())
            if n: dg[rng.choice(m, n, replace=False)] = True
        diag = dg
    obs, mu, p = perm_p(r['_st'], r['_keep'], diag, r['_O'], rng, NPERM_G)
    return kind, i, dict(obs=obs, null_mean=mu, p=p)

def main():
    t0 = time.time(); R = dict(seed=SEED, threshold=THR, files=[f for _, f in X.FILES]); V = {}
    for k, f in X.FILES:
        ps, docs, lab, strata = X.voynich(f); n = np.array([sum(len(d) for d, l in zip(docs, lab) if l == s) for s in range(4)])
        V[k] = dict(docs=docs, lab=lab, N=int(n.sum()), sect_tokens=n.tolist(), pages=len(ps))
    shares = np.array(V['ZL3b']['sect_tokens']) / V['ZL3b']['N']; Ns = {k: V[k]['N'] for k in V}
    R['voynich_tokens'] = {k: dict(N=V[k]['N'], by_section=dict(zip(X.SECTS, V[k]['sect_tokens'])), pages=V[k]['pages']) for k in V}
    gjobs = [(s, Ns, shares) for s in list(REF_SEEDS) + list(HO_SEEDS)]
    djobs = [(kind, i, V['ZL3b']['docs'], V['ZL3b']['lab']) for kind in ('fp', 'pw') for i in range(NG)]
    with Pool(8) as P:
        ga = P.map_async(gen_job, gjobs, chunksize=1); dg = P.map(dgate_job, djobs, chunksize=1); gres = ga.get()
    print('pool done', round(time.time() - t0, 1), flush=True)
    G = {s: r for s, r in sorted(gres) if r is not None}
    ref = [s for s in REF_SEEDS if s in G][:NREF]; ho = [s for s in HO_SEEDS if s in G][:NHO]; R['gen_seeds_used'] = dict(ref=ref, ho=ho)
    gates = {}
    for k in V:
        refk = [G[s][k]['plain']['S'] for s in ref]; med = float(np.median(refk))
        fp = sum(X.rank_p(G[s][k]['plain']['S'], refk) <= 0.05 for s in ho)
        pw = sum(X.rank_p(G[s][k]['conn']['S'], refk) <= 0.05 and G[s][k]['conn']['S'] > med for s in ho)
        pwd = sum(X.rank_p(G[s][k]['iso']['S'], refk) <= 0.05 and G[s][k]['iso']['S'] < med for s in ho)
        gates[f'T_S10_{k}'] = dict(fp=fp, power_conn=pw, power_iso=pwd, n_ref=len(ref), n_ho=len(ho), ref_range=(min(refk), med, max(refk)),
                                   conn_shift_median=float(np.median([G[s][k]['conn']['S'] - G[s][k]['plain']['S'] for s in ho])),
                                   conn_k_median=float(np.median([G[s][k]['conn_k'] for s in ho])),
                                   passed=len(ref) >= NREF and len(ho) >= NHO and fp <= 2 and pw >= 16)
    fpD = sum(r['p'] <= 0.05 for kind, i, r in dg if kind == 'fp'); pwD = sum(r['p'] <= 0.05 and r['obs'] < r['null_mean'] for kind, i, r in dg if kind == 'pw')
    gD = dict(fp=fpD, power=pwD, n=NG, plant_D_median=float(np.median([r['obs'] for kind, i, r in dg if kind == 'pw'])),
              passed=fpD <= 2 and pwD >= 16, note='gates measured on ZL 3b, applied to both transcriptions')
    gates['T_D10_ZL3b'] = gD; gates['T_D10_IT2a'] = gD; R['gates'] = gates
    print('GATES', json.dumps(gates, default=float), flush=True)
    # manuscript (computed only after all gates above are fixed)
    rng = np.random.default_rng(SEED); vs = {}; tests = []
    for k in V:
        c = X.Corpus(V[k]['docs']); r = stats(c, V[k]['lab'], detail=True)
        obs, mu, p = perm_p(r['_st'], r['_keep'], r['_diag'], r['_O'], rng, NPERM)
        vs[k] = dict(S10=r['S'], D10=r['D'], n_diag=r['n_diag'], O10_other=r['O_other'], D10_null_mean=mu, D10_perm_p=p,
                     sens={str(th): stats(c, V[k]['lab'], th)['S'] for th in SENS})
        refk = [G[s][k]['plain']['S'] for s in ref]
        tests.append((f'T_S10_{k}', r['S'], X.rank_p(r['S'], refk), float(np.median(refk))))
        tests.append((f'T_D10_{k}', r['D'], p, mu))
        vs[k]['gen_D10_range'] = (min(G[s][k]['plain']['D'] for s in ref), float(np.median([G[s][k]['plain']['D'] for s in ref])), max(G[s][k]['plain']['D'] for s in ref))
        vs[k]['gen_sens_range'] = {str(th): (min(G[s][k]['sens'][str(th)] for s in ref), max(G[s][k]['sens'][str(th)] for s in ref)) for th in SENS}
    R['voynich'] = vs
    gt = [t for t in tests if gates[t[0]]['passed']]; rej = X.bh([t[2] for t in gt]) if gt else []
    TT = {t[0]: dict(v=t[1], p=t[2], centre=t[3], side='above' if t[1] > t[3] else 'below', gate=gates[t[0]]['passed']) for t in tests}
    for t, rj in zip(gt, rej): TT[t[0]]['bh_reject'] = bool(rj)
    for x in TT.values(): x['verdict'] = 'NOT TESTABLE' if not x['gate'] else (x['side'].upper() if x['bh_reject'] else 'NO DIFFERENCE SHOWN')
    R['tests'] = TT
    nat = X.E.nat_units(); natS, dropped = {}, []
    for name, t in nat.items():
        if len(t) < NAT_MIN: dropped.append((name, len(t))); continue
        n_ = min(len(t), min(Ns.values())); docs, lab = X.blocks(t[:n_], shares); r = stats(X.Corpus(docs), lab)
        natS[name] = dict(N=n_, **r)
    vals = {a: b['S'] for a, b in natS.items()}; lo, hi = min(vals.values()), max(vals.values())
    loo = sum((vals[a] < min(vals[b] for b in vals if b != a)) or (vals[a] > max(vals[b] for b in vals if b != a)) for a in vals)
    cl = {k: ('BELOW' if vs[k]['S10'] < lo else 'ABOVE' if vs[k]['S10'] > hi else 'INSIDE') for k in V}
    R['natural'] = dict(S=natS, dropped=dropped, range=(lo, hi), loo_outside=loo, n=len(vals),
                        verdict=({k: (c if c == 'INSIDE' else 'OUTSIDE-' + c) for k, c in cl.items()} if loo <= 3 else 'NOT TESTABLE'))
    R['generator_detail'] = {str(s): G[s] for s in ref + ho}; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C067_results.json', 'w'), indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else float(o))
    print('tokens', R['voynich_tokens'])
    for k in vs: print('VOY', k, json.dumps(vs[k], default=float))
    print('TESTS', json.dumps(TT, default=float)); print('NAT', json.dumps({a: b for a, b in R['natural'].items() if a != 'S'}, default=float))
    print('NAT_S', {a: round(b['S'], 3) for a, b in natS.items()}); print('runtime', R['runtime_s'])

if __name__ == '__main__': main()
