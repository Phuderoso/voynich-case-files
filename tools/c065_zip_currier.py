#!/usr/bin/env python3
"""C065 (F-ZIP step 2, confirmatory, generator-referenced): do the manuscript's order gain S3 (C064), hapax share S2 and Heaps
exponent S1 differ from the Timm-Schinner generator INSIDE each Currier language, at N = 5,000 tokens?
Windows (8): {ZL3b, IT2a} x {Currier A, Currier B} x {first 5,000, last 5,000 tokens of that language's paragraph text, page order}
 (A ~10.6-10.8k tokens, B ~22.5k, so first/last are disjoint; ZL and IT2a share pages, so they are not independent).
Statistics at N = 5,000: S1 Heaps slope of log V on log N at N = 500,1000,2000,3000,5000; S2 hapax share; S3 order gain
 1 - xz(text)/mean xz(5 word shuffles) (lzma preset 9), exactly as C064 but N = 5,000.
Reference: default generator, 3,400 lines, FRESH seeds 6501-6600, first 80 with >= 5,000 tokens (first 5,000 tokens each).
Test: two-sided rank p = (1 + #ref with |r - med| >= |v - med|)/(n_ref + 1) (floor 1/81 = 0.0123). BH at q = 0.05 over ALL gated tests
 (<= 3 statistics x 8 windows = 24).
Gates per statistic (from the generator itself): held-out default seeds 6601-6640 (first 20 long enough):
 (a) FPR: unplanted held-out runs with p <= 0.05 must be <= 2/20;
 (b) power >= 16/20 on the same runs, p <= 0.05 in the planted direction: S3 partial shuffle (20% of token positions permuted among
     themselves) -> lower; S1, S2 inflation (5% of tokens -> fresh unique types) -> higher.
Decision per statistic: CONFIRMED-DIFFERENT if all 8 windows BH-rejected on the same side; PARTIAL (state which language/windows) if 1-7;
 NO DIFFERENCE SHOWN if 0 (powered); NOT TESTABLE if a gate fails.
Secondary (descriptive range rule, no p): 3 alternative generator settings, 20 runs each (seeds 6701-6730 / 6801-6830 / 6901-6930,
 first 20 long enough): G1 sourceChooser=random, G2 sourceChooser=position, G3 morph.reuse_last.probability=0; per setting and
 statistic, all 8 windows inside its range = COVERS, else the count inside. Natural (12 texts as C064, first 5,000 tokens): LOO gate
 <= 3/12 outside; INSIDE / OUTSIDE-side / STRADDLE per statistic over the 8 windows.
Seed 6565. Pre-registered in case-file/C065-zip-currier.md. Run: timeout 600 python3 tools/c065_zip_currier.py
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, json, time, lzma, zlib
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c058_edit_neighbours as E
import c055_burstiness as C
import c003_position_rigidity as T
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate

SEED, N, NREF, NHO, NALT, NSHUF = 6565, 5000, 80, 20, 20, 5
GRID = [500, 1000, 2000, 3000, 5000]
FILES = (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt'))
SETS = {'ref': ({}, range(6501, 6601), NREF), 'ho': ({}, range(6601, 6641), NHO),
        'G1': ({'method.sourceChooser': 'random'}, range(6701, 6731), NALT),
        'G2': ({'method.sourceChooser': 'position'}, range(6801, 6831), NALT),
        'G3': ({'method.morph.reuse_last.probability': 0}, range(6901, 6931), NALT)}
SS = ('S1', 'S2', 'S3'); ALPHA, Q = 0.05, 0.05

def stats(toks, rng):
    toks = toks[:N]; cnt = {}
    for w in toks: cnt[w] = cnt.get(w, 0) + 1
    V = [len(set(toks[:n])) for n in GRID]
    b = float(np.polyfit(np.log(GRID), np.log(V), 1)[0])
    hap = float(sum(1 for c in cnt.values() if c == 1) / len(cnt))
    s = [''.join(w) for w in toks]
    z = lambda ws: len(lzma.compress(' '.join(ws).encode(), preset=9))
    z0 = z(s); zs = np.mean([z([s[j] for j in rng.permutation(len(s))]) for _ in range(NSHUF)])
    return dict(S1=b, S2=hap, S3=float(1 - z0 / zs))

def vwindows():
    out, n = {}, {}
    for k, f in FILES:
        pl, lang, _ = ivtff_pages_lang(f)
        for L in 'AB':
            t = [tuple(T.units(w)) for p, l in pl if lang.get(p) == L for w in l]
            n[f'{k}_{L}'] = len(t); assert len(t) >= 2 * N
            out[f'{k}_{L}_first'] = t[:N]; out[f'{k}_{L}_last'] = t[-N:]
    return out, n

def partial_shuffle(t, rng, frac=0.2):
    t = list(t); idx = rng.choice(len(t), int(frac * len(t)), replace=False); perm = rng.permutation(idx)
    vals = [t[j] for j in perm]
    for i, v in zip(idx, vals): t[i] = v
    return t

def inflate(t, rng, frac=0.05):
    t = list(t)
    for c, i in enumerate(rng.choice(len(t), int(frac * len(t)), replace=False)): t[i] = t[i] + (f'#{c}',)
    return t

def gen_job(a):
    name, s = a; cfg = dict(SETS[name][0]); cfg['text.lines_to_create'] = 3400
    Lg = generate(cfg, s); t = [tuple(T.units(w)) for w in C.flat(Lg)] if Lg else []
    if len(t) < N: return name, s, None
    rng = np.random.default_rng(SEED * 10000 + s); t = t[:N]
    r = dict(plain=stats(t, rng))
    if name == 'ho': r['shuf'] = stats(partial_shuffle(t, rng), rng); r['infl'] = stats(inflate(t, rng), rng)
    return name, s, r

def nat_job(a):
    k, t = a; return k, stats(t[:N], np.random.default_rng(SEED + zlib.crc32(k.encode()) % 1000))

def rank_p(v, ref):
    ref = np.asarray(ref); m = float(np.median(ref)); return float((1 + np.sum(np.abs(ref - m) >= abs(v - m))) / (len(ref) + 1))

def bh(ps, q):
    ps = np.asarray(ps); m = len(ps); o = np.argsort(ps); ok = ps[o] <= q * np.arange(1, m + 1) / m
    k = np.max(np.where(ok)[0]) + 1 if ok.any() else 0; rej = np.zeros(m, bool); rej[o[:k]] = True; return rej

def cls(vals, lo, hi):
    side = ['below' if v < lo else 'above' if v > hi else 'inside' for v in vals]
    if all(s == 'inside' for s in side): return 'INSIDE'
    if len(set(side)) == 1: return 'OUTSIDE-' + side[0].upper()
    return 'STRADDLE'

def main():
    t0 = time.time(); vw, vn = vwindows()
    natt = {k: v for k, v in E.nat_units().items() if len(v) >= N}; names = list(natt)
    R = dict(seed=SEED, N=N, files=[f for _, f in FILES], voynich_tokens=vn, nat=names)
    jobs = [(nm, s) for nm in SETS for s in SETS[nm][1]]
    with Pool(8) as P:
        nat = dict(P.map(nat_job, [(k, natt[k]) for k in names]))
        res = P.map(gen_job, jobs, chunksize=1)
    print('gen done', round(time.time() - t0, 1), flush=True)
    G = {}
    for nm in SETS:
        ok = [(s, r) for n2, s, r in sorted(res, key=lambda x: x[1]) if n2 == nm and r is not None]
        G[nm] = dict(ok[:SETS[nm][2]])
    R['gen_seeds_used'] = {nm: list(G[nm]) for nm in G}
    rng = np.random.default_rng(SEED); voy = {k: stats(vw[k], rng) for k in vw}
    ref = {s: [r['plain'][s] for r in G['ref'].values()] for s in SS}
    # gates
    gate, gd = {}, {}
    for s in SS:
        fp = sum(rank_p(r['plain'][s], ref[s]) <= ALPHA for r in G['ho'].values())
        pk = 'shuf' if s == 'S3' else 'infl'; med = float(np.median(ref[s]))
        sign = (lambda v: v < med) if s == 'S3' else (lambda v: v > med)
        pw = sum(rank_p(r[pk][s], ref[s]) <= ALPHA and sign(r[pk][s]) for r in G['ho'].values())
        shift = float(np.median([r[pk][s] - r['plain'][s] for r in G['ho'].values()]))
        gd[s] = dict(fpr=fp / len(G['ho']), fp=fp, power=pw, n_ho=len(G['ho']), plant=pk, median_plant_shift=shift)
        gate[s] = len(G['ref']) >= NREF and len(G['ho']) >= NHO and fp <= 2 and pw >= 16
    R['gates'] = gd; R['gate_pass'] = gate
    # primary tests
    tests = [(s, w) for s in SS if gate[s] for w in voy]
    ps = [rank_p(voy[w][s], ref[s]) for s, w in tests]; rej = bh(ps, Q) if tests else []
    T_ = {}
    for (s, w), p, r in zip(tests, ps, rej):
        med = float(np.median(ref[s])); T_[f'{s}|{w}'] = dict(v=voy[w][s], p=p, bh_reject=bool(r), side='below' if voy[w][s] < med else 'above')
    R['tests'] = T_
    V = {}
    for s in SS:
        if not gate[s]: V[s] = 'NOT TESTABLE'; continue
        rr = [T_[f'{s}|{w}'] for w in voy]; k = sum(x['bh_reject'] for x in rr); sides = {x['side'] for x in rr if x['bh_reject']}
        if k == len(rr) and len(sides) == 1: V[s] = 'CONFIRMED-DIFFERENT-' + sides.pop().upper()
        elif k == 0: V[s] = 'NO DIFFERENCE SHOWN'
        else: V[s] = f'PARTIAL {k}/8: ' + ', '.join(w + ':' + T_[f"{s}|{w}"]['side'] for w in voy if T_[f'{s}|{w}']['bh_reject'])
    R['verdict'] = V
    R['ref_range'] = {s: (min(ref[s]), float(np.median(ref[s])), max(ref[s])) for s in SS}
    # secondary: alt settings + natural
    alt = {}
    for nm in ('G1', 'G2', 'G3'):
        alt[nm] = {}
        for s in SS:
            a = [r['plain'][s] for r in G[nm].values()]
            if len(a) < NALT: alt[nm][s] = dict(n=len(a), status='too few runs'); continue
            ins = sum(min(a) <= voy[w][s] <= max(a) for w in voy)
            alt[nm][s] = dict(n=len(a), range=(min(a), float(np.median(a)), max(a)), inside=ins, status='COVERS' if ins == len(voy) else f'{ins}/8 inside')
    R['alt'] = alt
    nr = {s: (min(v[s] for v in nat.values()), max(v[s] for v in nat.values())) for s in SS}
    loo = {s: sum((nat[k][s] < min(nat[j][s] for j in nat if j != k)) or (nat[k][s] > max(nat[j][s] for j in nat if j != k)) for k in nat) for s in SS}
    R['natural'] = dict(stats=nat, range=nr, loo_outside=loo,
                        verdict={s: (cls([voy[w][s] for w in voy], *nr[s]) if loo[s] <= 3 else 'NOT TESTABLE') for s in SS},
                        by_lang={s: {L: cls([voy[w][s] for w in voy if f'_{L}_' in w], *nr[s]) for L in 'AB'} for s in SS})
    R['voynich'] = voy; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C065_results.json', 'w'), indent=1, default=float)
    print('tokens', vn); print('ref range', R['ref_range']); print('gates', gd, gate)
    for w, v in voy.items(): print(w, {a: round(b, 4) for a, b in v.items()})
    for k, v in T_.items(): print(k, round(v['v'], 4), v['p'], v['bh_reject'], v['side'])
    print('VERDICT', V); print('ALT', json.dumps(alt, default=float)); print('NAT', nr, loo, R['natural']['verdict'], R['natural']['by_lang'])
    print('runtime', R['runtime_s'])

if __name__ == '__main__': main()
