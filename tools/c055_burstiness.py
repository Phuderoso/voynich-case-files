#!/usr/bin/env python3
"""C055 (new family F-BURST, word burstiness): do mid-frequency word types clump into some stretches of text and
vanish from others (as topical words do in natural prose), and is the manuscript's clumping natural-like or
generator-like? Each text: two disjoint halves of 15,000 tokens in reading order, cut into 115-token chunks (130).
Eligible types: 15-150 occurrences in the half. Statistic B = mean over eligible types of log(var/mean) of their
per-chunk counts. Null: global token shuffle inside the half (200x); excess D = B - mean(null B); p by rank.
Gates: FPR on shuffled natural halves, power on a planted clumping. Controls: 9 natural + 3 devowelled texts,
Timm-Schinner generator (5 seeds, default settings). Pre-registered in case-file/C055-burstiness.md. Seed 5555.
Run: timeout 600 python3 tools/c055_burstiness.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c051_context_spelling_ab as B
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate

SEED, NHALF, CH, NSH, NG, ALPHA, LO, HI, MINT = 5555, 15000, 115, 200, 20, 0.05, 15, 150, 30
GSEEDS, GLINES, PT, PM, PC = [551, 552, 553, 554, 555], 3400, 0.20, 0.30, 0.10

def stat(ids, nt):
    nc = len(ids) // CH; ids = ids[:nc * CH]
    tot = np.bincount(ids, minlength=nt); el = np.where((tot >= LO) & (tot <= HI))[0]
    if len(el) < MINT: return None, len(el)
    M = np.bincount(ids * nc + np.repeat(np.arange(nc), CH), minlength=nt * nc).reshape(nt, nc)[el]
    m = M.mean(1); v = M.var(1)
    return float(np.mean(np.log(np.maximum(v, 1e-9) / m))), len(el)

def test(toks, rng):
    voc = {w: i for i, w in enumerate(sorted(set(toks)))}; ids = np.array([voc[w] for w in toks]); nt = len(voc)
    b, ne = stat(ids, nt)
    if b is None: return dict(B=None, n_types=ne, verdict='NOT TESTABLE')
    nl = np.array([stat(rng.permutation(ids), nt)[0] for _ in range(NSH)])
    return dict(B=b, null=float(nl.mean()), D=float(b - nl.mean()), p=float((1 + (nl >= b).sum()) / (NSH + 1)), n_types=ne)

def plant(toks, rng):
    """shuffled half; for PT of eligible types, move PM of their tokens into a random PC of chunks (swap places)"""
    t = list(rng.permutation(np.array(toks, dtype=object))); n = len(t) // CH * CH; t = t[:n]; nc = n // CH
    from collections import Counter
    c = Counter(t); el = [w for w, k in c.items() if LO <= k <= HI]
    for w in rng.choice(el, int(PT * len(el)), replace=False) if el else []:
        hot = rng.choice(nc, max(1, int(PC * nc)), replace=False)
        pos = [i for i, x in enumerate(t) if x == w and i // CH not in set(hot)]
        for i in rng.choice(pos, int(PM * len(pos)), replace=False) if pos else []:
            j = int(hot[rng.integers(len(hot))] * CH + rng.integers(CH)); t[i], t[j] = t[j], t[i]
    return t

def flat(lines): return [w for l in lines for w in l]

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); nat = B.nat_texts()
    for k in ('Latin_Caesar', 'Italian_Dante', 'Spanish_Cervantes'): nat[k + '_devowel'] = [l for l in T.devowel(nat[k]) if len(l) >= 3]
    R = dict(seed=SEED, NHALF=NHALF, CH=CH, NSH=NSH, band=[LO, HI], plant=dict(types=PT, moved=PM, chunks=PC), gseeds=GSEEDS)
    natt = {k: flat(v) for k, v in nat.items()}; names = [k for k in nat if not k.endswith('_devowel')]
    fp = pw = 0
    for i in range(NG):
        a = natt[names[i % len(names)]][:NHALF]; fp += test(list(rng.permutation(np.array(a, dtype=object))), rng)['p'] < ALPHA
        b = natt[names[(i + 4) % len(names)]][NHALF:2 * NHALF]; pw += test(plant(b, rng), rng)['p'] < ALPHA
    G = dict(fpr=f'{fp}/{NG}', power=f'{pw}/{NG}', ok=bool(fp <= 2 and pw >= 14)); R['gates'] = G; print('gates', G, round(time.time() - t0, 1), flush=True)
    out = {}
    for k, t in natt.items():
        out[k] = [test(t[h * NHALF:(h + 1) * NHALF], rng) for h in (0, 1)]; print(k, [(round(y['B'], 3), round(y['D'], 3), y['p'], y['n_types']) for y in out[k]], flush=True)
    for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        pl, _, _ = ivtff_pages_lang(f); t = ['.'.join(T.units(w)) for _, l in pl for w in l]
        out[k] = [test(t[h * NHALF:(h + 1) * NHALF], rng) for h in (0, 1)]; print(k, [(round(y['B'], 3), round(y['D'], 3), y['p'], y['n_types']) for y in out[k]], flush=True)
    gen = {}
    for s in GSEEDS:
        L = generate({'text.lines_to_create': GLINES}, s); t = flat(L) if L else []
        if len(t) < 2 * NHALF: gen[s] = dict(ok=False, n=len(t)); continue
        gen[s] = dict(ok=True, n=len(t), halves=[test(t[h * NHALF:(h + 1) * NHALF], rng) for h in (0, 1)])
        print('gen', s, [(round(y['B'], 3), round(y['D'], 3), y['p']) for y in gen[s]['halves']], round(time.time() - t0, 1), flush=True)
    R['texts'] = out; R['generator'] = gen
    vo = [y for k in ('ZL3b', 'IT2a') for y in out[k]]
    def place(vals, ref):
        lo, hi = min(ref), max(ref)
        return ('ABOVE' if all(v > hi for v in vals) else 'BELOW' if all(v < lo for v in vals) else
                'INSIDE' if all(lo <= v <= hi for v in vals) else 'STRADDLE'), [lo, hi]
    if not G['ok'] or any(y['B'] is None for y in vo): V = dict(H1='NOT TESTABLE', H2='NOT TESTABLE', H3='NOT TESTABLE')
    else:
        s = [y['p'] < ALPHA / 4 for y in vo]; h1 = 'EXCESS' if all(s) else 'NO EXCESS' if not any(s) else 'SPLIT'
        vv = [y['D'] for y in vo]; natv = [y['D'] for k in nat for y in out[k] if y['B'] is not None]
        genv = [y['D'] for s_ in gen if gen[s_]['ok'] for y in gen[s_]['halves'] if y['B'] is not None]
        h2 = place(vv, natv); h3 = place(vv, genv) if len(genv) >= 6 else ('NOT TESTABLE', None)
        V = dict(H1=h1, H2=h2[0], natural_range=h2[1], H3=h3[0], generator_range=h3[1])
    R['verdict'] = V; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C055_results.json', 'w'), indent=1, default=float); print(V, R['runtime_s'])

if __name__ == '__main__': main()
