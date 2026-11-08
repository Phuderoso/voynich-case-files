#!/usr/bin/env python3
"""C060 (F-NEIGH step 3): WHICH glyph units are swapped in the local one-glyph changes, and is the manuscript's swap
table generator-like? For each focal token (>= 3 units) with its nearest one-glyph neighbour among the 10 preceding
tokens (C058/C059 definition), the change is labelled: substitution -> unordered unit pair {u,v}; insertion/deletion
-> ('+', unit). Excess table = clip(obs - mean null, 0) over the C058 null (100 shuffles inside 115-token chunks),
normalised. Distance = Jensen-Shannon divergence (bits) over the union of labels.
H1: VG = JSD(each Voynich half, each generator half); GG = JSD between generator halves of DIFFERENT seeds.
GENERATOR-LIKE if median VG <= 95th percentile of GG; DIFFERENT if median VG > max GG; INTERMEDIATE otherwise.
Gate: natural halves with copy-with-mutation planted (Q 0.03) using ONE fixed swap (its two most frequent letters);
recovered if that pair has the largest excess share and share > 0.3; bar >= 16/20.
Pre-registered in case-file/C060-swap-table.md. Seed 6060.
Run: timeout 600 python3 tools/c060_swap_table.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c058_edit_neighbours as E
import c055_burstiness as C
import c003_position_rigidity as T
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate

SEED, NHALF, W, NSH, NGT, QP, MINLEN = 6060, 15000, 10, 100, 20, 0.03, 3

def label(a, b):
    if len(a) == len(b):
        j = next(i for i in range(len(a)) if a[i] != b[i]); return tuple(sorted((a[j], b[j])))
    lo, sh = (a, b) if len(a) > len(b) else (b, a)
    j = next((i for i in range(len(sh)) if lo[i] != sh[i]), len(sh)); return ('+', lo[j])

def table(ids, types, keys, V, lens, cache):
    n = len(ids); lag = np.zeros(n, int)
    for k in range(1, W + 1):
        h = np.zeros(n, bool); h[k:] = np.isin(ids[k:].astype(np.int64) * V + ids[:-k], keys); lag[(lag == 0) & h] = k
    c = Counter()
    for i in np.where((lag > 0) & (lens[ids] >= MINLEN))[0]:
        key = (ids[i], ids[i - lag[i]])
        if key not in cache: cache[key] = label(types[key[0]], types[key[1]])
        c[cache[key]] += 1
    return c

def excess(toks, rng):
    types = sorted(set(toks)); voc = {t: i for i, t in enumerate(types)}; V = len(types)
    ids = np.array([voc[t] for t in toks]); keys = E.nbr_keys(types); lens = np.array([len(t) for t in types]); cache = {}
    obs = table(ids, types, keys, V, lens, cache); nul = Counter()
    for _ in range(NSH): nul.update(table(E.chunk_perm(ids, rng), types, keys, V, lens, cache))
    ex = {k: max(0.0, obs[k] - nul[k] / NSH) for k in set(obs) | set(nul)}; tot = sum(ex.values())
    return {'|'.join(k): v / tot for k, v in ex.items() if v > 0} if tot > 0 else {}

def jsd(p, q):
    ks = set(p) | set(q); a = np.array([p.get(k, 0) for k in ks]); b = np.array([q.get(k, 0) for k in ks]); m = (a + b) / 2
    f = lambda x: np.sum(x[x > 0] * np.log2(x[x > 0] / m[x > 0]))
    return float((f(a) + f(b)) / 2)

def plant_swap(toks, rng):
    t = [toks[j] for j in rng.permutation(len(toks))]
    u, v = [x for x, _ in Counter(c for w in toks for c in w).most_common(2)]
    for i in rng.choice(np.arange(5, len(t)), int(QP * len(t)), replace=False):
        src = t[i - int(rng.integers(1, 6))]; pos = [j for j, c in enumerate(src) if c in (u, v)]
        if len(src) < 3 or not pos: continue
        j = pos[int(rng.integers(len(pos)))]; t[i] = src[:j] + ((v if src[j] == u else u),) + src[j + 1:]
    return t, '|'.join(sorted((u, v)))

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); natt = E.nat_units(); names = list(natt); R = dict(seed=SEED)
    ok = 0; gl = []
    for i in range(NGT):
        b = natt[names[(i + 4) % len(names)]][:NHALF]; pt, tgt = plant_swap(b, rng); ex = excess(pt, rng)
        top = max(ex, key=ex.get) if ex else None; s = ex.get(tgt, 0.0); hit = bool(top == tgt and s > 0.3); ok += hit
        gl.append(dict(text=names[(i + 4) % len(names)], target=tgt, share=s, top=top))
    G = dict(recovered=f'{ok}/{NGT}', ok=bool(ok >= 16), reps=gl); R['gate'] = G; print('gate', G['recovered'], round(time.time() - t0, 1), flush=True)
    vo = {}
    for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        pl, _, _ = ivtff_pages_lang(f); v = [tuple(T.units(w)) for _, l in pl for w in l]
        for h in (0, 1): vo[f'{k}_h{h + 1}'] = excess(v[h * NHALF:(h + 1) * NHALF], rng)
    print('voynich done', round(time.time() - t0, 1), flush=True)
    ge = {}
    for s in E.GSEEDS:
        Lg = generate({'text.lines_to_create': 3400}, s); t = [tuple(T.units(w)) for w in C.flat(Lg)] if Lg else []
        if len(t) < 2 * NHALF: continue
        for h in (0, 1): ge[f'{s}_h{h + 1}'] = excess(t[h * NHALF:(h + 1) * NHALF], rng)
        print('gen', s, round(time.time() - t0, 1), flush=True)
    VG = [jsd(vo[a], ge[b]) for a in vo for b in ge]
    GG = [jsd(ge[a], ge[b]) for a in ge for b in ge if a < b and a.split('_')[0] != b.split('_')[0]]
    VV = {'ZL_h1_h2': jsd(vo['ZL3b_h1'], vo['ZL3b_h2']), 'IT_h1_h2': jsd(vo['IT2a_h1'], vo['IT2a_h2']),
          'ZL_IT_h1': jsd(vo['ZL3b_h1'], vo['IT2a_h1']), 'ZL_IT_h2': jsd(vo['ZL3b_h2'], vo['IT2a_h2'])}
    R.update(voynich=vo, generator=ge, VG=VG, GG=GG, VV=VV)
    if not G['ok'] or len(ge) < 6: Vd = dict(H1='NOT TESTABLE')
    else:
        mv, q95, mx = float(np.median(VG)), float(np.percentile(GG, 95)), float(max(GG))
        Vd = dict(H1='GENERATOR-LIKE' if mv <= q95 else 'DIFFERENT' if mv > mx else 'INTERMEDIATE', median_VG=mv,
                  GG_q95=q95, GG_max=mx, GG_median=float(np.median(GG)))
    def top(d, n=8): return sorted(d.items(), key=lambda x: -x[1])[:n]
    pv = {}; [pv.__setitem__(k, pv.get(k, 0) + x / 4) for d in vo.values() for k, x in d.items()]
    pg = {}; [pg.__setitem__(k, pg.get(k, 0) + x / len(ge)) for d in ge.values() for k, x in d.items()]
    R['top_voynich'] = top(pv); R['top_generator'] = top(pg)
    R['verdict'] = Vd; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C060_results.json', 'w'), indent=1, default=float)
    print(Vd, VV, '\nV', R['top_voynich'], '\nG', R['top_generator'], R['runtime_s'])

if __name__ == '__main__': main()
