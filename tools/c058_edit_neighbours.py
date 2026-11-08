#!/usr/bin/env python3
"""C058 (new family F-NEIGH, local edit-distance neighbours): Timm & Schinner describe the text as produced by copying
nearby words with small changes. Statistic S = share of focal tokens (>= 3 units) that have at least one token at
edit distance EXACTLY 1 (one unit substituted, inserted or deleted; identical tokens do not count) among the W = 10
preceding tokens. Units: EVA glyph units for Voynich and generator, letters for natural text. Null: tokens shuffled
only INSIDE 115-token chunks (the F-BURST chunk), so chunk-scale clumping (C055-C057) is kept and only short-range
order is destroyed; D = S - mean null S, NSH = 100, p by rank. 15,000-token halves as in C055-C057.
Plant (copy-with-mutation): in a shuffled natural half, a share Q of tokens are replaced by a one-unit substitution of
a token 1-5 places earlier. Design mode (seed 5858) sweeps Q; test mode (seed 5859) runs gates and H1-H3.
Pre-registered in case-file/C058-edit-neighbours.md.
Run: timeout 600 python3 tools/c058_edit_neighbours.py design|test   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c055_burstiness as C
import c003_position_rigidity as T
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate

NHALF, CH, W, NSH, NG, ALPHA, MINLEN = 15000, 115, 10, 100, 40, 0.05, 3
GSEEDS = [551, 552, 553, 554, 555, 556, 557]
QS = [0.01, 0.02, 0.03, 0.05]
Q_CHOSEN = None  # set from the design step before the test is run

def nbr_keys(types):
    """encoded pairs a*V+b of distinct types at edit distance exactly 1"""
    V = len(types); buck = defaultdict(list)
    for i, t in enumerate(types):
        buck[('W',) + t].append((i, 0))
        for j in range(len(t)):
            buck[('S', j) + t[:j] + ('*',) + t[j + 1:]].append((i, 1))
            buck[('W',) + t[:j] + t[j + 1:]].append((i, 2))   # deletion of t equals a whole shorter word
    ks = set()
    for k, lst in buck.items():
        if k[0] == 'S':
            ids = [i for i, _ in lst]
            for a in ids:
                for b in ids:
                    if a != b: ks.add(a * V + b)
        else:
            whole = [i for i, m in lst if m == 0]; dels = [i for i, m in lst if m == 2]
            for a in whole:
                for b in dels:
                    if a != b: ks.add(a * V + b); ks.add(b * V + a)
    return np.array(sorted(ks), dtype=np.int64)

def S(ids, focal, keys, V):
    hit = np.zeros(len(ids), bool)
    for k in range(1, W + 1):
        hit[k:] |= np.isin(ids[k:].astype(np.int64) * V + ids[:-k], keys, assume_unique=False)
    return float(hit[focal].mean())

def chunk_perm(ids, rng):
    out = ids.copy(); n = len(ids)
    for a in range(0, n, CH): out[a:a + CH] = rng.permutation(out[a:a + CH])
    return out

def test(toks, rng):
    """toks: list of tuples of units"""
    types = sorted(set(toks)); voc = {t: i for i, t in enumerate(types)}; V = len(types)
    ids = np.array([voc[t] for t in toks]); keys = nbr_keys(types); lens = np.array([len(t) for t in types])
    s = S(ids, lens[ids] >= MINLEN, keys, V)
    null = []
    for _ in range(NSH):
        p = chunk_perm(ids, rng); null.append(S(p, lens[p] >= MINLEN, keys, V))
    null = np.array(null)
    return dict(S=s, null=float(null.mean()), D=float(s - null.mean()), p=float((1 + (null >= s).sum()) / (NSH + 1)), V=V)

def plant(toks, q, rng, alpha):
    t = [toks[j] for j in rng.permutation(len(toks))]
    for i in rng.choice(np.arange(5, len(t)), int(q * len(t)), replace=False):
        src = t[i - int(rng.integers(1, 6))]
        if len(src) < 2: continue
        j = int(rng.integers(len(src))); new = alpha[int(rng.integers(len(alpha)))]
        if new == src[j]: continue
        t[i] = src[:j] + (new,) + src[j + 1:]
    return t

def nat_units():
    nat = C.B.nat_texts()
    for k in ('Latin_Caesar', 'Italian_Dante', 'Spanish_Cervantes'): nat[k + '_devowel'] = [l for l in T.devowel(nat[k]) if len(l) >= 3]
    return {k: [tuple(w) for w in C.flat(v)] for k, v in nat.items()}

def alphabet(toks): return sorted({u for t in toks for u in t})

def gates(natt, q, rng):
    names = list(natt); fp = pw = 0
    for i in range(NG):
        a = natt[names[i % len(names)]][:NHALF]
        fp += test([a[j] for j in rng.permutation(len(a))], rng)['p'] < ALPHA
        b = natt[names[(i + 4) % len(names)]][:NHALF]
        pw += test(plant(b, q, rng, alphabet(b)), rng)['p'] < ALPHA
    return fp, pw

def design():
    t0 = time.time(); rng = np.random.default_rng(5858); natt = nat_units(); names = list(natt); rows = []
    for q in QS:
        hits = 0; ds = []
        for i in range(NG):
            b = natt[names[(i + 4) % len(names)]][:NHALF]; r = test(plant(b, q, rng, alphabet(b)), rng)
            hits += r['p'] < ALPHA; ds.append(r['D'])
        rows.append(dict(Q=q, power=f'{hits}/{NG}', hits=hits, D_median=float(np.median(ds)))); print(rows[-1], round(time.time() - t0, 1), flush=True)
    ok = [r for r in rows if r['hits'] >= 36]
    R = dict(seed=5858, rows=rows, chosen_Q=ok[0]['Q'] if ok else None, runtime_s=round(time.time() - t0, 1))
    json.dump(R, open('analysis/C058_design.json', 'w'), indent=1); print(R)

def main_test():
    t0 = time.time(); rng = np.random.default_rng(5859); natt = nat_units()
    q = json.load(open('analysis/C058_design.json'))['chosen_Q']; R = dict(seed=5859, Q=q, NSH=NSH, W=W)
    if q is None: R['verdict'] = dict(H1='NOT TESTABLE', H2='NOT TESTABLE', H3='NOT TESTABLE', why='no design Q'); json.dump(R, open('analysis/C058_results.json', 'w'), indent=1); return
    fp, pw = gates(natt, q, rng); G = dict(fpr=f'{fp}/{NG}', power=f'{pw}/{NG}', ok=bool(fp <= 4 and pw >= 32)); R['gates'] = G
    print('gates', G, round(time.time() - t0, 1), flush=True)
    out = {}
    for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        pl, _, _ = ivtff_pages_lang(f); v = [tuple(T.units(w)) for _, l in pl for w in l]
        out[k] = [test(v[h * NHALF:(h + 1) * NHALF], rng) for h in (0, 1)]; print(k, out[k], flush=True)
    for k, t in natt.items():
        hs = (0, 1) if len(t) >= 2 * NHALF else (0,)
        out[k] = [test(t[h * NHALF:(h + 1) * NHALF], rng) for h in hs]; print(k, [(round(y['D'], 4), y['p']) for y in out[k]], round(time.time() - t0, 1), flush=True)
    gen = {}
    for s in GSEEDS:
        Lg = generate({'text.lines_to_create': 3400}, s); t = [tuple(T.units(w)) for w in C.flat(Lg)] if Lg else []
        if len(t) < 2 * NHALF: gen[s] = dict(ok=False, n=len(t)); print('gen', s, 'short', len(t)); continue
        gen[s] = dict(ok=True, n=len(t), halves=[test(t[h * NHALF:(h + 1) * NHALF], rng) for h in (0, 1)])
        print('gen', s, [(round(y['D'], 4), y['p']) for y in gen[s]['halves']], round(time.time() - t0, 1), flush=True)
    R['texts'] = out; R['generator'] = gen
    vo = [y for k in ('ZL3b', 'IT2a') for y in out[k]]
    def place(vals, ref):
        lo, hi = min(ref), max(ref)
        return ('ABOVE' if all(v > hi for v in vals) else 'BELOW' if all(v < lo for v in vals) else
                'INSIDE' if all(lo <= v <= hi for v in vals) else 'STRADDLE'), [lo, hi]
    if not G['ok']: Vd = dict(H1='NOT TESTABLE', H2='NOT TESTABLE', H3='NOT TESTABLE')
    else:
        sig = [y['p'] < ALPHA / 4 for y in vo]; h1 = 'EXCESS' if all(sig) else 'NO EXCESS' if not any(sig) else 'SPLIT'
        vv = [y['D'] for y in vo]; natv = [y['D'] for k in natt for y in out[k]]
        genv = [y['D'] for s_ in gen if gen[s_]['ok'] for y in gen[s_]['halves']]
        h2 = place(vv, natv); h3 = place(vv, genv) if len(genv) >= 6 else ('NOT TESTABLE', None)
        Vd = dict(H1=h1, H2=h2[0], natural_range=h2[1], H3=h3[0], generator_range=h3[1])
    R['verdict'] = Vd; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C058_results.json', 'w'), indent=1, default=float); print(Vd, R['runtime_s'])

if __name__ == '__main__':
    design() if sys.argv[1:] == ['design'] else main_test()
