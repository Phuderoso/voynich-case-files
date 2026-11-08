#!/usr/bin/env python3
"""C052 (new family F-REP, adjacent repetition): how often is a word followed, in the same line, by itself (R0) or by a
word one glyph-unit edit away (R1)? Excess X = observed / expected under a within-page token shuffle (lines keep their
lengths; Voynich pages from IVTFF, natural text pseudo-pages of ~115 tokens). Compared with 9 natural + 3 devowelled
controls and the Timm-Schinner generator (5 seeds) at matched N = 15,000 tokens (two disjoint halves per text).
Pre-registered in case-file/C052-adjacent-repetition.md. Seed 5252.
Run: timeout 600 python3 tools/c052_adjacent_repetition.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c049_context_spelling as E
import c051_context_spelling_ab as B
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate

SEED, NHALF, NSH, NG, ALPHA, PAGE, PLANT = 5252, 15000, 100, 20, 0.05, 115, 0.03
GSEEDS, GLINES = [521, 522, 523, 524, 525], 3400
_L1 = {}

def one_edit(a, b):
    k = (a, b) if a <= b else (b, a)
    v = _L1.get(k)
    if v is None: v = _L1[k] = (abs(len(a) - len(b)) <= 1 and E.lev(a, b) == 1)
    return v

def counts(pl):
    r0 = r1 = n = 0
    for _, l in pl:
        for x, y in zip(l, l[1:]):
            n += 1
            if x == y: r0 += 1
            elif one_edit(x, y): r1 += 1
    return r0, r1, n

def shuffle_pages(pl, rng):
    by, order = {}, []
    for p, l in pl:
        if p not in by: by[p] = []; order.append(p)
        by[p].append(l)
    out = []
    for p in order:
        toks = [w for l in by[p] for w in l]; rng.shuffle(toks); i = 0
        for l in by[p]: out.append((p, toks[i:i + len(l)])); i += len(l)
    return out

def test(pl, rng):
    o = counts(pl); nl = np.array([counts(shuffle_pages(pl, rng))[:2] for _ in range(NSH)])
    res = {}
    for k, nm in enumerate(('R0', 'R1')):
        e = nl[:, k].mean(); res[nm] = dict(obs=int(o[k]), exp=float(e), X=float(o[k] / e) if e > 0 else None,
                                         rate=float(o[k] / o[2]), p=float((1 + (nl[:, k] >= o[k]).sum()) / (NSH + 1)))
    return res

def as_units(pl): return [(p, [tuple(T.units(w)) for w in l]) for p, l in pl]
def as_chars(pl): return [(p, [tuple(w) for w in l]) for p, l in pl]

def take_pages(pl, start, n):
    out, t, seen = [], 0, 0
    for p, l in pl:
        if seen < start: seen += len(l); continue
        if t >= n: break
        out.append((p, l)); t += len(l)
    return out

def plant(pl, rng, frac=PLANT):
    """after a fraction frac of in-line positions, the next word is replaced by a copy of the current one (exact) or,
    with probability 1/2, by a copy with one unit changed"""
    letters = sorted({c for _, l in pl for w in l for c in w}); out = []
    for p, l in pl:
        l = list(l)
        for i in range(len(l) - 1):
            if rng.random() < frac:
                w = l[i]
                if rng.random() < 0.5 and len(w) > 1:
                    k = int(rng.integers(len(w))); w = w[:k] + (str(rng.choice(letters)),) + w[k + 1:]
                l[i + 1] = w
        out.append((p, l))
    return out

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); nat = B.nat_texts()
    for k in ('Latin_Caesar', 'Italian_Dante', 'Spanish_Cervantes'): nat[k + '_devowel'] = [l for l in T.devowel(nat[k]) if len(l) >= 3]
    R = dict(seed=SEED, NHALF=NHALF, NSH=NSH, plant=PLANT, gseeds=GSEEDS)
    natpl = {k: as_chars(B.pseudo_pages(v, 0, 2 * NHALF + 500)) for k, v in nat.items()}
    names = [k for k in nat if not k.endswith('_devowel')]
    # gates: FPR on page-shuffled natural text (null true), power on planted natural text
    fp = [0, 0]; pw = [0, 0]
    for i in range(NG):
        pl = take_pages(natpl[names[i % len(names)]], 0, NHALF); r = test(shuffle_pages(pl, rng), rng)
        pl2 = take_pages(natpl[names[(i + 4) % len(names)]], NHALF, NHALF); r2 = test(plant(pl2, rng), rng)
        for k, nm in enumerate(('R0', 'R1')): fp[k] += r[nm]['p'] < ALPHA; pw[k] += r2[nm]['p'] < ALPHA
        print('gate', i, fp, pw, round(time.time() - t0, 1), flush=True)
    G = {nm: dict(fpr=f'{fp[k]}/{NG}', power=f'{pw[k]}/{NG}', ok=bool(fp[k] <= 2 and pw[k] >= 14)) for k, nm in enumerate(('R0', 'R1'))}
    R['gates'] = G; print(G, flush=True)
    out = {}
    for k, pl in natpl.items():
        out[k] = [test(take_pages(pl, h * NHALF, NHALF), rng) for h in (0, 1)]
        print(k, [(y['R0']['X'], y['R1']['X']) for y in out[k]], round(time.time() - t0, 1), flush=True)
    for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        pl, lang, _ = ivtff_pages_lang(f); pl = as_units(pl)
        out[k] = [test(take_pages(pl, h * NHALF, NHALF), rng) for h in (0, 1)]
        print(k, [(y['R0']['X'], y['R0']['p'], y['R1']['X'], y['R1']['p']) for y in out[k]], round(time.time() - t0, 1), flush=True)
    gen = {}
    for s in GSEEDS:
        L = generate({'text.lines_to_create': GLINES}, s); n = sum(map(len, L)) if L else 0
        if not L or n < 2 * NHALF: gen[s] = dict(ok=False, n=n); continue
        pl = as_units(B.pseudo_pages(L, 0, 2 * NHALF + 500))
        gen[s] = dict(ok=True, n=n, halves=[test(take_pages(pl, h * NHALF, NHALF), rng) for h in (0, 1)])
        print('gen', s, [(y['R0']['X'], y['R1']['X']) for y in gen[s]['halves']], round(time.time() - t0, 1), flush=True)
    R['texts'] = out; R['generator'] = gen
    vo = [y for k in ('ZL3b', 'IT2a') for y in out[k]]
    def place(vals, ref):
        lo, hi = min(ref), max(ref)
        return ('ABOVE' if all(v > hi for v in vals) else 'BELOW' if all(v < lo for v in vals) else
                'INSIDE' if all(lo <= v <= hi for v in vals) else 'STRADDLE'), [lo, hi]
    V = {}
    for nm in ('R0', 'R1'):
        if not G[nm]['ok']: V[nm] = dict(H1='NOT TESTABLE', H2='NOT TESTABLE', H3='NOT TESTABLE'); continue
        s = [y[nm]['p'] < ALPHA / 4 for y in vo]
        h1 = 'EXCESS' if all(s) else 'NO EXCESS' if not any(s) else 'SPLIT'
        vv = [y[nm]['X'] for y in vo]; natv = [y[nm]['X'] for k in nat for y in out[k]]
        genv = [y[nm]['X'] for s_ in gen if gen[s_]['ok'] for y in gen[s_]['halves']]
        h2 = place(vv, natv); h3 = place(vv, genv) if len(genv) >= 6 else ('NOT TESTABLE', None)
        V[nm] = dict(H1=h1, H2=h2[0], natural_range=h2[1], H3=h3[0], generator_range=h3[1])
    R['verdict'] = V; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C052_results.json', 'w'), indent=1, default=float); print(V, R['runtime_s'])

if __name__ == '__main__': main()
