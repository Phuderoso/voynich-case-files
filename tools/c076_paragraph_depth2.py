#!/usr/bin/env python3
"""C076 (F-PARA step 2): C071's paragraph-floor test with a CALIBRATED, direction-neutral plant, plus H2 (does the top-line
body still differ once every interior word containing a p/f gallows is removed?).
Data, paragraphs, interior words (positions 3..n-2), classes (T, S, M, Lst), JSD statistic and within-paragraph line-order
null: exactly as C071 (tools/c071_paragraph_depth.py, imported).
Plant: per replicate a target unit U is drawn uniformly from units whose pooled interior share in the subset is in
[0.02, 0.10] (H2: p/f units excluded); in class-X lines each interior word is replaced with probability q by a word drawn
uniformly from the subset's interior tokens containing U (H2: tokens without p/f units).
Design phase (no manuscript statistic computed): IT2a only, X = T, A and B, 10 pseudo replicates per q in
QGRID, gate R = 200, seed 7676*10+1; q* = smallest q with planted p<=0.05 in >=9/10 for both A and B (else max of grid).
Main: H1 = {T,S,Lst} x {A,B} x {IT2a,ZL} (12), H2 = T(no p/f words) x {A,B} x {IT2a,ZL} (4); Holm over 16; R = 1000;
gates per test 20 pseudo replicates, FPR <= 2/20, power >= 16/20 at q*; seed 7676.
Verdicts per (hypothesis, language): DIFFERENT / PARTIAL / NOT DETECTED / NOT TESTABLE (as C071).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c071_paragraph_depth as C
SEED, R, RG, NG, NGD, ALPHA = 7676, 1000, 200, 20, 10, 0.05
QGRID = (0.04, 0.06, 0.08, 0.12, 0.16, 0.24)
PF = {'p', 'f', 'cph', 'cfh'}
FILES = dict(C.FILES)

def has_pf(w): return any(u in PF for u in C.T3.units(w))

def subset(k, lang, nopf=False):
    ps = [p for p in C.parse(FILES[k]) if p['L'] == lang]
    if nopf:  # remove interior words containing p/f units (keep edges so interior positions stay defined)
        ps = [dict(p, lines=[ws[:2] + [w for w in ws[2:-2] if not has_pf(w)] + ws[-2:] if len(ws) > 4 else ws for ws in p['lines']]) for p in ps]
    return ps

def stat_x(P, x, order=None): return C.stat(P, order)[x]

def ptest(P, x, rng, r):
    obs = stat_x(P, x); null = [stat_x(P, x, [rng.permutation(len(l)) for l in P]) for _ in range(r)]
    return obs, float((1 + sum(v >= obs for v in null)) / (r + 1))

def plant(shuf, x, q, rng, nopf):
    toks = [w for p in shuf for ws in p['lines'] for w in ws[2:-2]]
    uc = Counter(u for w in toks for u in C.T3.units(w)); tot = sum(uc.values())
    cand = sorted(u for u, c in uc.items() if 0.02 <= c / tot <= 0.10 and not (nopf and u in PF))
    U = cand[rng.integers(len(cand))]; pool = [w for w in toks if U in C.T3.units(w)]
    out = []
    for p in shuf:
        L = []
        for c, ws in zip(C.classes(len(p['lines'])), p['lines']):
            if c == x and len(ws) > 4: ws = ws[:2] + [pool[rng.integers(len(pool))] if rng.random() < q else w for w in ws[2:-2]] + ws[-2:]
            L.append(ws)
        out.append(L)
    return [[C.counts(C.interior(ws)) for ws in L] for L in out], U

def shuffled(ps, rng): return [dict(p, lines=[p['lines'][j] for j in rng.permutation(len(p['lines']))]) for p in ps]

def design_job(a):
    lang, qi, i = a; rng = np.random.default_rng(SEED * 10 + 1 + 100000 * qi + 1000 * i + (0 if lang == 'A' else 500))
    sh = shuffled(subset('IT2a', lang), rng); Pp, U = plant(sh, 'T', QGRID[qi], rng, False)
    obs, p = ptest(Pp, 'T', rng, RG); return lang, qi, i, p, obs, U

def gate_job(a):
    k, lang, h, i, q = a; nopf = h == 'H2'; xs = ('T',) if nopf else C.CLS
    rng = np.random.default_rng(SEED * 1000 + i + (0 if k == 'IT2a' else 500) + (0 if lang == 'A' else 250) + (0 if h == 'H1' else 2000))
    sh = shuffled(subset(k, lang, nopf), rng); P0 = C.build(sh); res = {}
    for x in xs:
        fp = ptest(P0, x, rng, RG)[1]; Pp, U = plant(sh, x, q, rng, nopf); pobs, pp = ptest(Pp, x, rng, RG)
        res[x] = (fp, pp, pobs)
    return k, lang, h, i, res

def main_job(a):
    k, lang, h = a; nopf = h == 'H2'; xs = ('T',) if nopf else C.CLS; ps = subset(k, lang, nopf); P = C.build(ps)
    rng = np.random.default_rng(SEED + (0 if k == 'IT2a' else 1) + (0 if lang == 'A' else 2) + (0 if h == 'H1' else 4))
    tests = {x: dict(zip(('JSD', 'p'), ptest(P, x, rng, R))) for x in xs}
    agg = {c: Counter() for c in ('T', 'S', 'M', 'Lst')}
    for p in ps:
        for c, ws in zip(C.classes(len(p['lines'])), p['lines']): agg[c].update(C.counts(C.interior(ws)))
    desc = {}
    for x in xs:
        tx, tm = sum(agg[x].values()), sum(agg['M'].values())
        d = sorted(((agg[x][u] / tx - agg['M'][u] / tm, u) for u in set(agg[x]) | set(agg['M'])), key=lambda z: -abs(z[0]))[:5]
        desc[x] = dict(top_units=[(u, round(v, 4)) for v, u in d], n_units=tx, n_units_M=tm)
    return k, lang, h, dict(n_paras=len(ps), tests=tests, desc=desc)

def main():
    t0 = time.time(); out = dict(seed=SEED, R=R, QGRID=QGRID)
    with Pool(8) as pool:
        D = pool.map(design_job, [(l, qi, i) for l in ('A', 'B') for qi in range(len(QGRID)) for i in range(NGD)], chunksize=1)
        des = {}
        for l, qi, i, p, obs, U in D:
            d = des.setdefault(f'{l}_{QGRID[qi]}', dict(hits=0, jsd=[], units=[])); d['hits'] += p <= ALPHA; d['jsd'].append(obs); d['units'].append(U)
        for d in des.values(): d['median_planted_JSD'] = float(np.median(d['jsd'])); del d['jsd']
        ok = [q for q in QGRID if all(des[f'{l}_{q}']['hits'] >= 9 for l in ('A', 'B'))]
        qs = ok[0] if ok else QGRID[-1]; out.update(design=des, q_star=qs, design_s=round(time.time() - t0, 1))
        print('design', json.dumps(des), 'q*', qs, flush=True)
        jobs = [(k, l, h) for k in FILES for l in ('A', 'B') for h in ('H1', 'H2')]
        gj = pool.map_async(gate_job, [j + (i, qs) for j in jobs for i in range(NG)], chunksize=1)
        M = {f'{k}_{l}_{h}': r for k, l, h, r in pool.map(main_job, jobs)}
        print('main', json.dumps(M), flush=True)
        G = {}
        for k, l, h, i, res in gj.get():
            for x, (fp, pp, pobs) in res.items():
                g = G.setdefault(f'{k}_{l}_{h}_{x}', dict(fp=0, pw=0, pj=[])); g['fp'] += fp <= ALPHA; g['pw'] += pp <= ALPHA; g['pj'].append(pobs)
    for g in G.values(): g['pass'] = g['fp'] <= 2 and g['pw'] >= 16; g['median_planted_JSD'] = float(np.median(g['pj'])); del g['pj']
    names = [n for n in G if G[n]['pass']]
    ps = [M['_'.join(n.split('_')[:3])]['tests'][n.split('_')[3]]['p'] for n in names]
    o = np.argsort(ps); rej, stop = {}, False
    for r, i in enumerate(o):
        okk = (not stop) and ps[i] <= ALPHA / (len(ps) - r); rej[names[i]] = bool(okk); stop = stop or not okk
    ver = {}
    for h, xs in (('H1', C.CLS), ('H2', ('T',))):
        for l in ('A', 'B'):
            for x in xs:
                ns = [f'{k}_{l}_{h}_{x}' for k in FILES]
                if not all(G[n]['pass'] for n in ns): ver[f'{h}_{l}_{x}'] = 'NOT TESTABLE'; continue
                m = sum(rej.get(n, False) for n in ns); ver[f'{h}_{l}_{x}'] = 'DIFFERENT' if m == 2 else 'PARTIAL' if m == 1 else 'NOT DETECTED'
    out.update(main=M, gates=G, holm=rej, n_holm=len(names), verdict=ver, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C076_results.json', 'w'), indent=1)
    for k in ('gates', 'holm', 'verdict', 'runtime_s'): print(k, json.dumps(out[k]))

if __name__ == '__main__':
    main()
