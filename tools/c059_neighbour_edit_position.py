#!/usr/bin/env python3
"""C059 (F-NEIGH step 2): WHERE in the word does the local one-glyph change happen? For every focal token (>= 3 units)
whose nearest one-glyph neighbour lies among the 10 preceding tokens (C058 definition), the change is classed by unit
position: INITIAL (first unit), FINAL (last unit), MEDIAL (other); for insertions/deletions the position is taken in the
longer word. Excess profile: share_c = (obs_c - null_c) / (obs_tot - null_tot), null = mean over 100 within-115-token-chunk
shuffles (C058 null). A text is scored only if its total excess has z >= 3 against the null spread.
Gates: position recovery on natural halves with copy-with-mutation planted at Q = 0.03 only at the first unit (20 reps)
or only at the last unit (20 reps); recovered if the target share > 0.6; bar >= 16/20 each.
Pre-registered in case-file/C059-neighbour-edit-position.md. Seed 5959.
Run: timeout 600 python3 tools/c059_neighbour_edit_position.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c058_edit_neighbours as E
import c055_burstiness as C
import c003_position_rigidity as T
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate

SEED, NHALF, W, NSH, NGH, QP, MINLEN = 5959, 15000, 10, 100, 20, 0.03, 3
CLS = ('INITIAL', 'MEDIAL', 'FINAL')

def edit_class(a, b):
    if len(a) == len(b):
        j = next(i for i in range(len(a)) if a[i] != b[i]); L = len(a)
    else:
        lo, sh = (a, b) if len(a) > len(b) else (b, a); L = len(lo)
        j = next((i for i in range(len(sh)) if lo[i] != sh[i]), len(sh))
        # insertion/deletion inside a run of identical units is ambiguous; the first mismatching position is used
    return 0 if j == 0 else 2 if j == L - 1 else 1

def counts(ids, types, keys, V, lens, cache):
    n = len(ids); lag = np.zeros(n, int)
    for k in range(1, W + 1):
        h = np.zeros(n, bool); h[k:] = np.isin(ids[k:].astype(np.int64) * V + ids[:-k], keys)
        lag[(lag == 0) & h] = k
    foc = np.where((lag > 0) & (lens[ids] >= MINLEN))[0]; c = np.zeros(3)
    for i in foc:
        key = (ids[i], ids[i - lag[i]])
        if key not in cache: cache[key] = edit_class(types[key[0]], types[key[1]])
        c[cache[key]] += 1
    return c

def profile(toks, rng):
    types = sorted(set(toks)); voc = {t: i for i, t in enumerate(types)}; V = len(types)
    ids = np.array([voc[t] for t in toks]); keys = E.nbr_keys(types); lens = np.array([len(t) for t in types]); cache = {}
    obs = counts(ids, types, keys, V, lens, cache)
    nul = np.array([counts(E.chunk_perm(ids, rng), types, keys, V, lens, cache) for _ in range(NSH)])
    ex = obs - nul.mean(0); tot = ex.sum(); sd = nul.sum(1).std()
    z = float(tot / sd) if sd > 0 else 0.0
    r = dict(obs=obs.tolist(), null=nul.mean(0).tolist(), excess=ex.tolist(), z=z, scored=bool(z >= 3))
    if r['scored']: r['share'] = dict(zip(CLS, (ex / tot).tolist()))
    return r

def plant_at(toks, pos, rng, alpha):
    t = [toks[j] for j in rng.permutation(len(toks))]
    for i in rng.choice(np.arange(5, len(t)), int(QP * len(t)), replace=False):
        src = t[i - int(rng.integers(1, 6))]
        if len(src) < 3: continue
        j = 0 if pos == 'INITIAL' else len(src) - 1; new = alpha[int(rng.integers(len(alpha)))]
        if new == src[j]: continue
        t[i] = src[:j] + (new,) + src[j + 1:]
    return t

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); natt = E.nat_units(); names = list(natt)
    R = dict(seed=SEED, QP=QP, NSH=NSH); G = {}
    for pos in ('INITIAL', 'FINAL'):
        ok = 0; sh = []
        for i in range(NGH):
            b = natt[names[(i + 4) % len(names)]][:NHALF]; r = profile(plant_at(b, pos, rng, E.alphabet(b)), rng)
            s = r.get('share', {}).get(pos, 0.0); sh.append(s); ok += s > 0.6
        G[pos] = dict(recovered=f'{ok}/{NGH}', median_share=float(np.median(sh)), ok=bool(ok >= 16))
        print('gate', pos, G[pos], round(time.time() - t0, 1), flush=True)
    G['ok'] = all(G[p]['ok'] for p in ('INITIAL', 'FINAL')); R['gates'] = G
    out = {}
    for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        pl, _, _ = ivtff_pages_lang(f); v = [tuple(T.units(w)) for _, l in pl for w in l]
        out[k] = [profile(v[h * NHALF:(h + 1) * NHALF], rng) for h in (0, 1)]; print(k, [(round(y['z'], 1), y.get('share')) for y in out[k]], flush=True)
    for k, t in natt.items():
        hs = (0, 1) if len(t) >= 2 * NHALF else (0,)
        out[k] = [profile(t[h * NHALF:(h + 1) * NHALF], rng) for h in hs]; print(k, [(round(y['z'], 1), y.get('share')) for y in out[k]], round(time.time() - t0, 1), flush=True)
    gen = {}
    for s in E.GSEEDS:
        Lg = generate({'text.lines_to_create': 3400}, s); t = [tuple(T.units(w)) for w in C.flat(Lg)] if Lg else []
        if len(t) < 2 * NHALF: gen[s] = dict(ok=False, n=len(t)); continue
        gen[s] = dict(ok=True, halves=[profile(t[h * NHALF:(h + 1) * NHALF], rng) for h in (0, 1)])
        print('gen', s, [(round(y['z'], 1), y.get('share')) for y in gen[s]['halves']], round(time.time() - t0, 1), flush=True)
    R['texts'] = out; R['generator'] = gen
    vo = [y for k in ('ZL3b', 'IT2a') for y in out[k]]; gv = [y for s in gen if gen[s]['ok'] for y in gen[s]['halves'] if y['scored']]
    def place(vals, ref):
        lo, hi = min(ref), max(ref)
        return ('ABOVE' if all(v > hi for v in vals) else 'BELOW' if all(v < lo for v in vals) else
                'INSIDE' if all(lo <= v <= hi for v in vals) else 'STRADDLE'), [lo, hi]
    if not G['ok'] or not all(y['scored'] for y in vo) or len(gv) < 6: Vd = dict(H1='NOT TESTABLE')
    else:
        pc = {c: place([y['share'][c] for y in vo], [y['share'][c] for y in gv]) for c in CLS}
        pl_ = [pc[c][0] for c in CLS]
        h1 = 'MATCH' if all(p == 'INSIDE' for p in pl_) else 'DIFFERENT' if any(p in ('ABOVE', 'BELOW') for p in pl_) else 'PARTIAL'
        Vd = dict(H1=h1, per_class={c: dict(place=pc[c][0], generator_range=pc[c][1], voynich=[y['share'][c] for y in vo]) for c in CLS})
    R['verdict'] = Vd; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C059_results.json', 'w'), indent=1, default=float); print(Vd, R['runtime_s'])

if __name__ == '__main__': main()
