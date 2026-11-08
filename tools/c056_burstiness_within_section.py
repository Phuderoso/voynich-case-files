#!/usr/bin/env python3
"""C056 (F-BURST step 2): does C055's word clumping survive once section changes are taken out? Same statistic B
as C055 (115-token chunks, types 15-150 per 15,000-token half, mean log var/mean). New null: tokens shuffled only
inside blocks = contiguous runs of the same IVTFF $I section in reading order (D_blk = B - mean null). Controls get
the SAME block lengths as the matching Voynich ZL half (natural texts with one half use ZL half 1), so their long-range
drift is removed in the same way. Stronger gates: 40 replicates. Pre-registered in
case-file/C056-burstiness-within-section.md. Seed 5656.
Run: timeout 600 python3 tools/c056_burstiness_within_section.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c055_burstiness as C
import c003_position_rigidity as T
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate

SEED, NHALF, NSH, NG, ALPHA = 5656, 15000, 200, 40, 0.05
GSEEDS = [551, 552, 553, 554, 555, 556, 557]

def runs(lab):
    r = []
    for c in lab:
        if r and r[-1][0] == c: r[-1][1] += 1
        else: r.append([c, 1])
    return [b for _, b in r]

def bounds(lengths, n):
    e = np.cumsum(lengths); e = e[e < n]; return np.concatenate([[0], e, [n]]).astype(int)

def blk_perm(ids, bd, rng):
    out = ids.copy()
    for a, b in zip(bd[:-1], bd[1:]): out[a:b] = rng.permutation(out[a:b])
    return out

def test(toks, lengths, rng):
    voc = {w: i for i, w in enumerate(sorted(set(toks)))}; ids = np.array([voc[w] for w in toks]); nt = len(voc)
    b, ne = C.stat(ids, nt)
    if b is None: return dict(B=None, n_types=ne)
    bd = bounds(lengths, len(ids))
    nb = np.array([C.stat(blk_perm(ids, bd, rng), nt)[0] for _ in range(NSH)])
    ng = np.array([C.stat(rng.permutation(ids), nt)[0] for _ in range(50)])
    return dict(B=b, D_blk=float(b - nb.mean()), p_blk=float((1 + (nb >= b).sum()) / (NSH + 1)),
                D_glob=float(b - ng.mean()), n_types=ne, n_blocks=len(bd) - 1)

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); nat = C.B.nat_texts()
    for k in ('Latin_Caesar', 'Italian_Dante', 'Spanish_Cervantes'): nat[k + '_devowel'] = [l for l in T.devowel(nat[k]) if len(l) >= 3]
    natt = {k: C.flat(v) for k, v in nat.items()}; names = [k for k in nat if not k.endswith('_devowel')]
    V = {}; L = {}
    for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        pl, _, sect = ivtff_pages_lang(f)
        V[k] = ['.'.join(T.units(w)) for _, l in pl for w in l]; lab = [sect[p] for p, l in pl for w in l]
        L[k] = [runs(lab[h * NHALF:(h + 1) * NHALF]) for h in (0, 1)]
    R = dict(seed=SEED, NHALF=NHALF, NSH=NSH, NG=NG, blocks={k: L[k] for k in L}, gseeds=GSEEDS)
    fp = pw = 0
    for i in range(NG):
        lg = L['ZL3b'][i % 2]
        a = natt[names[i % len(names)]][:NHALF]; fp += test(list(rng.permutation(np.array(a, dtype=object))), lg, rng).get('p_blk', 1) < ALPHA
        b = natt[names[(i + 4) % len(names)]][:NHALF]; pw += test(C.plant(b, rng), lg, rng).get('p_blk', 1) < ALPHA
    G = dict(fpr=f'{fp}/{NG}', power=f'{pw}/{NG}', ok=bool(fp <= 4 and pw >= 28)); R['gates'] = G; print('gates', G, round(time.time() - t0, 1), flush=True)
    out = {}
    for k in ('ZL3b', 'IT2a'):
        out[k] = [test(V[k][h * NHALF:(h + 1) * NHALF], L[k][h], rng) for h in (0, 1)]; print(k, out[k], flush=True)
    for k, t in natt.items():
        hs = (0, 1) if len(t) >= 2 * NHALF else (0,)
        out[k] = [test(t[h * NHALF:(h + 1) * NHALF], L['ZL3b'][h], rng) for h in hs]; print(k, [(round(y['D_glob'], 3), round(y['D_blk'], 3), y['p_blk']) for y in out[k]], flush=True)
    gen = {}
    for s in GSEEDS:
        Lg = generate({'text.lines_to_create': 3400}, s); t = C.flat(Lg) if Lg else []
        if len(t) < 2 * NHALF: gen[s] = dict(ok=False, n=len(t)); print('gen', s, 'short', len(t)); continue
        gen[s] = dict(ok=True, n=len(t), halves=[test(t[h * NHALF:(h + 1) * NHALF], L['ZL3b'][h], rng) for h in (0, 1)])
        print('gen', s, [(round(y['D_glob'], 3), round(y['D_blk'], 3)) for y in gen[s]['halves']], round(time.time() - t0, 1), flush=True)
    R['texts'] = out; R['generator'] = gen
    vo = [y for k in ('ZL3b', 'IT2a') for y in out[k]]
    def place(vals, ref):
        lo, hi = min(ref), max(ref)
        return ('ABOVE' if all(v > hi for v in vals) else 'BELOW' if all(v < lo for v in vals) else
                'INSIDE' if all(lo <= v <= hi for v in vals) else 'STRADDLE'), [lo, hi]
    if not G['ok'] or any(y['B'] is None for y in vo): Vd = dict(H1='NOT TESTABLE', H2='NOT TESTABLE', H3='NOT TESTABLE')
    else:
        s = [y['p_blk'] < ALPHA / 4 for y in vo]; h1 = 'EXCESS' if all(s) else 'NO EXCESS' if not any(s) else 'SPLIT'
        vv = [y['D_blk'] for y in vo]; natv = [y['D_blk'] for k in nat for y in out[k] if y['B'] is not None]
        genv = [y['D_blk'] for s_ in gen if gen[s_]['ok'] for y in gen[s_]['halves'] if y['B'] is not None]
        h2 = place(vv, natv); h3 = place(vv, genv) if len(genv) >= 6 else ('NOT TESTABLE', None)
        Vd = dict(H1=h1, H2=h2[0], natural_range=h2[1], H3=h3[0], generator_range=h3[1])
    R['verdict'] = Vd; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C056_results.json', 'w'), indent=1, default=float); print(Vd, R['runtime_s'])

if __name__ == '__main__': main()
