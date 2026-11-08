#!/usr/bin/env python3
"""C063 (F-NEIGH step 4): fresh-seed / per-Currier-language replication of the two C060 POST-HOC observations:
 (a) the manuscript's share of the C060 excess table that is insertion/deletion of unit 'ch' ('+|ch') is LOWER than the
     Timm-Schinner generator's; (b) its share of insertion/deletion of 'q' ('+|q') is HIGHER.
Subsets: {ZL3b, IT2a} x {Currier A, B} (page $L), 4 subsets. For each, the generator is run on FRESH seeds (6301-6360, not
used before; first NG=40 texts with enough tokens) and its first n_s tokens (n_s = the subset's token count, capped at
NMAX) give a size-matched share. Test per subset: p_ch = (1 + #gen share_ch <= V_ch)/(NG+1); p_q = (1 + #gen share_q >= V_q)/(NG+1).
8 tests, BH at 0.05. The hypotheses were SUGGESTED BY C060 DATA; only this fresh-seed/subset replication counts.
Gate (estimator): natural texts at subset size, planted single-unit insertions (Q 0.03, rank-3 letter) -> unit share > 0.5 in >= 16/20;
unplanted controls -> that unit's share < 0.2 in >= 18/20; plus a leave-one-out check of the rank test on generator runs.
Excess table = C060 `excess` (100 shuffles in 115-token chunks). Pre-registered in case-file/C063-ch-q-replication.md. Seed 6363.
Run: timeout 600 python3 tools/c063_ch_q_replication.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c058_edit_neighbours as E
import c055_burstiness as C
import c003_position_rigidity as T
import c060_swap_table as S
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate

SEED, NG, NMAX, NMIN, NGT, QP = 6363, 40, 15000, 5000, 20, 0.03
GS = list(range(6301, 6361)); FILES = (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt'))

def subsets():
    out = {}
    for k, f in FILES:
        pl, lang, _ = ivtff_pages_lang(f)
        for L in 'AB':
            v = [tuple(T.units(w)) for p, l in pl if lang.get(p) == L for w in l]; out[f'{k}_{L}'] = v
    return out

def gen_job(args):
    s, sizes = args; rng = np.random.default_rng(SEED * 1000 + s)
    Lg = generate({'text.lines_to_create': 3400}, s); t = [tuple(T.units(w)) for w in C.flat(Lg)] if Lg else []
    if len(t) < max(sizes.values()): return s, None
    return s, {k: S.excess(t[:n], rng) for k, n in sizes.items()}

def plant_ins(toks, rng, unit):
    t = [toks[j] for j in rng.permutation(len(toks))]
    for i in rng.choice(np.arange(5, len(t)), int(QP * len(t)), replace=False):
        src = t[i - int(rng.integers(1, 6))]
        if len(src) < 3: continue
        j = int(rng.integers(len(src) + 1)); t[i] = src[:j] + (unit,) + src[j:]
    return t

def gate_job(args):
    i, name, n = args; rng = np.random.default_rng(SEED + 17 * i); natt = E.nat_units(); b = natt[name][:n]
    u = [x for x, _ in Counter(c for w in b for c in w).most_common(3)][2]
    ex1 = S.excess(plant_ins(b, rng, u), rng); ex0 = S.excess(b, rng)
    return dict(text=name, unit=u, planted=ex1.get('+|' + u, 0.0), control=ex0.get('+|' + u, 0.0))

def main():
    t0 = time.time(); vs = subsets(); R = dict(seed=SEED, files=[f for _, f in FILES], gen_seeds_tried=GS)
    sizes = {k: min(len(v), NMAX) for k, v in vs.items()}; R['sizes'] = {k: len(v) for k, v in vs.items()}
    testable = {k for k, n in sizes.items() if n >= NMIN}; sizes = {k: sizes[k] for k in testable}
    rng = np.random.default_rng(SEED); natt = E.nat_units(); names = list(natt)
    with Pool(8) as P:
        gj = P.map(gate_job, [(i, names[(i + 4) % len(names)], sizes[sorted(sizes)[i % len(sizes)]]) for i in range(NGT)])
        print('gate jobs', round(time.time() - t0, 1), flush=True)
        gen = {}
        res = P.map(gen_job, [(s, sizes) for s in GS], chunksize=1)
    for s, r in res:
        if r is not None and len(gen) < NG: gen[s] = r
    print('gen runs', len(gen), round(time.time() - t0, 1), flush=True)
    okp = sum(g['planted'] > 0.5 for g in gj); okc = sum(g['control'] < 0.2 for g in gj)
    R['gate'] = dict(plant_recovered=f'{okp}/{NGT}', control_clean=f'{okc}/{NGT}', reps=gj)
    gate_ok = okp >= 16 and okc >= 18
    rows = []; vo = {}
    for k in sorted(sizes):
        v = vs[k][:sizes[k]]; ex = S.excess(v, rng); vo[k] = ex
        for lab, key, sign in (('ch', '+|ch', -1), ('q', '+|q', 1)):
            gv = np.array([g[k].get(key, 0.0) for g in gen.values()]); x = ex.get(key, 0.0)
            p = (1 + np.sum(gv <= x)) / (len(gv) + 1) if sign < 0 else (1 + np.sum(gv >= x)) / (len(gv) + 1)
            # leave-one-out calibration of the same rank test on generator runs (exchangeable -> mean p ~ uniform)
            fp = float(np.mean([((1 + np.sum(np.delete(gv, j) <= gv[j])) / len(gv) <= 0.05) if sign < 0 else
                                ((1 + np.sum(np.delete(gv, j) >= gv[j])) / len(gv) <= 0.05) for j in range(len(gv))]))
            rows.append(dict(subset=k, n=sizes[k], unit=lab, voynich=x, gen_min=float(gv.min()), gen_med=float(np.median(gv)),
                             gen_max=float(gv.max()), p=float(p), loo_fpr=fp,
                             passes_rule=bool(x < gv.min()) if sign < 0 else bool(x > gv.max())))
    ps = np.array([r['p'] for r in rows]); o = np.argsort(ps); m = len(ps); thr = 0.05 * np.arange(1, m + 1) / m
    k = max([i + 1 for i in range(m) if ps[o[i]] <= thr[i]], default=0); rej = set(o[:k].tolist())
    for i, r in enumerate(rows): r['BH_reject'] = bool(i in rej)
    R['rows'] = rows; R['n_gen'] = len(gen); V = {}
    for u in ('ch', 'q'):
        rr = [r for r in rows if r['unit'] == u]; nrej = sum(r['BH_reject'] and r['passes_rule'] for r in rr)
        V[u] = 'NOT TESTABLE' if (not gate_ok or len(gen) < NG or not rr) else ('CONFIRMED' if nrej == len(rr) else 'PARTIAL' if nrej else 'NOT CONFIRMED')
        V[u + '_n'] = f'{nrej}/{len(rr)}'
    R['verdict'] = V; R['gate_ok'] = gate_ok; R['runtime_s'] = round(time.time() - t0, 1)
    R['voynich_top'] = {k: sorted(v.items(), key=lambda x: -x[1])[:5] for k, v in vo.items()}
    json.dump(R, open('analysis/C063_results.json', 'w'), indent=1, default=float)
    for r in rows: print({a: (round(b, 4) if isinstance(b, float) else b) for a, b in r.items()})
    print(V, R['gate']['plant_recovered'], R['gate']['control_clean'], R['runtime_s'])

if __name__ == '__main__': main()
