#!/usr/bin/env python3
"""C064 (NEW family F-ZIP, vocabulary growth and compressibility): at N = 15,000 tokens, three statistics per text:
 S1 Heaps exponent beta = slope of log V(N) on log N at N = 1000, 2000, 4000, 8000, 15000 (V = distinct word types in the first N tokens);
 S2 hapax share = (types seen once)/(types) at N = 15000;
 S3 order gain G = 1 - xz(text)/mean xz(5 word-order shuffles of the same text) (lzma preset 9, words joined by one space; bytes of the
    glyph-unit strings), i.e. how much the word ORDER (not the vocabulary) helps a dictionary compressor.
Reference sets: 12 natural (9 + 3 devowelled; as C051/C058), Timm-Schinner generator (default settings, FRESH seeds 6401-6460, first 40 long
enough), Voynich ZL3b and IT2a (paragraph text as C047), first 15,000 tokens AND last 15,000 tokens (two disjoint halves).
Gates: (a) leave-one-out: each natural text vs the other 11 -> outside-range rate per statistic must be <= 3/12; (b) planted power: vocabulary
inflation (10% of tokens -> fresh unique types) must push S1 and S2 above the natural max and word-order destruction (global shuffle) must push
S3 below the natural min in >= 16/20 plants each; deflation plant (types of rank > 100 merged into 50 pooled types) must push S2 below natural min >= 16/20.
Decision per statistic: OUTSIDE NATURAL if both transcriptions and both halves lie strictly outside the 12-text natural range on the same side;
INSIDE if all 4 lie inside; else STRADDLE. Same classification against the generator's 40-run range (H2). 3 statistics x 2 references = 6 verdicts,
no p-value is claimed from a 12-text range, so no multiplicity correction is needed (rules are range-based, stated before the run); the
generator rank p = (1+#gen beyond Voynich)/(41) is reported descriptively. Seed 6464. Pre-registered in case-file/C064-vocab-growth.md.
Run: timeout 600 python3 tools/c064_vocab_growth.py   -- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time, lzma, zlib
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c058_edit_neighbours as E
import c055_burstiness as C
import c003_position_rigidity as T
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate

SEED, N, NG, NGT = 6464, 15000, 40, 20
GRID = [1000, 2000, 4000, 8000, 15000]; GS = list(range(6401, 6461)); NSHUF = 5
FILES = (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt'))

def stats(toks, rng):
    seen, v = set(), []; cnt = {}
    for i, w in enumerate(toks[:N]):
        cnt[w] = cnt.get(w, 0) + 1
    V = []
    for n in GRID: V.append(len(set(toks[:n])))
    b = float(np.polyfit(np.log(GRID), np.log(V), 1)[0])
    hap = float(sum(1 for c in cnt.values() if c == 1) / len(cnt))
    s = [''.join(w) for w in toks[:N]]
    z = lambda ws: len(lzma.compress(' '.join(ws).encode(), preset=9))
    z0 = z(s); zs = np.mean([z([s[j] for j in rng.permutation(len(s))]) for _ in range(NSHUF)])
    return dict(S1=b, S2=hap, S3=float(1 - z0 / zs))

def vtoks():
    out = {}
    for k, f in FILES:
        pl, _, _ = ivtff_pages_lang(f); t = [tuple(T.units(w)) for p, l in pl for w in l]
        out[k + '_first'] = t[:N]; out[k + '_last'] = t[-N:]; out[k + '_n'] = len(t)
    return out

def gen_job(a):
    s = a; rng = np.random.default_rng(SEED * 1000 + s)
    Lg = generate({'text.lines_to_create': 3400}, s); t = [tuple(T.units(w)) for w in C.flat(Lg)] if Lg else []
    if len(t) < N: return s, None
    return s, stats(t, rng)

def nat_job(a):
    k, t = a; return k, stats(t[:N], np.random.default_rng(SEED + zlib.crc32(k.encode()) % 1000))

def inflate(t, rng):
    t = list(t)
    for c, i in enumerate(rng.choice(len(t), int(0.1 * len(t)), replace=False)): t[i] = t[i] + (f'#{c}',)
    return t

def deflate(t, rng):
    from collections import Counter
    rk = {w: r for r, (w, _) in enumerate(Counter(t).most_common())}
    pool = {}; out = []
    for w in t:
        if rk[w] > 100:
            if w not in pool: pool[w] = ('~', str(int(rng.integers(50))))
            out.append(pool[w])
        else: out.append(w)
    return out

def plant_job(a):
    i, name, t, kind = a; rng = np.random.default_rng(SEED + 31 * i); t = t[:N]
    if kind == 'inflate': t2 = inflate(t, rng)
    elif kind == 'deflate': t2 = deflate(t, rng)
    else: t2 = [t[j] for j in rng.permutation(len(t))]
    return dict(kind=kind, text=name, **stats(t2, rng))

def main():
    t0 = time.time(); vt = vtoks(); natt = {k: v for k, v in E.nat_units().items() if len(v) >= N}; names = list(natt)
    R = dict(seed=SEED, files=[f for _, f in FILES], nat=names, voynich_tokens={k: v for k, v in vt.items() if k.endswith('_n')})
    with Pool(8) as P:
        nat = dict(P.map(nat_job, [(k, natt[k]) for k in names]))
        print('nat', round(time.time() - t0, 1), flush=True)
        res = P.map(gen_job, GS, chunksize=1)
        print('gen', round(time.time() - t0, 1), flush=True)
        jobs = [(i, names[i % len(names)], natt[names[i % len(names)]], kind) for kind in ('inflate', 'deflate', 'shuffle') for i in range(NGT)]
        pl = P.map(plant_job, jobs)
    gen = {s: r for s, r in res if r is not None}; gen = dict(list(gen.items())[:NG])
    rng = np.random.default_rng(SEED); voy = {k: stats(vt[k], rng) for k in vt if not k.endswith('_n')}
    SS = ('S1', 'S2', 'S3'); R['natural'] = nat; R['voynich'] = voy; R['n_gen'] = len(gen); R['gen_seeds_used'] = list(gen)
    rng_n = {s: (min(v[s] for v in nat.values()), max(v[s] for v in nat.values())) for s in SS}
    # gate (a): leave-one-out outside-range counts
    loo = {s: sum((nat[k][s] < min(nat[j][s] for j in nat if j != k)) or (nat[k][s] > max(nat[j][s] for j in nat if j != k)) for k in nat) for s in SS}
    # gate (b): plants
    lo = {s: rng_n[s][0] for s in SS}; hi = {s: rng_n[s][1] for s in SS}
    pw = dict(infl_S1=sum(p['S1'] > hi['S1'] for p in pl if p['kind'] == 'inflate'), infl_S2=sum(p['S2'] > hi['S2'] for p in pl if p['kind'] == 'inflate'),
              defl_S2=sum(p['S2'] < lo['S2'] for p in pl if p['kind'] == 'deflate'), shuf_S3=sum(p['S3'] < lo['S3'] for p in pl if p['kind'] == 'shuffle'))
    R['gate'] = dict(loo_outside=loo, power=pw, natural_range=rng_n, plants=pl)
    gate = {'S1': loo['S1'] <= 3 and pw['infl_S1'] >= 16, 'S2': loo['S2'] <= 3 and pw['infl_S2'] >= 16 and pw['defl_S2'] >= 16, 'S3': loo['S3'] <= 3 and pw['shuf_S3'] >= 16}
    R['gate_pass'] = gate
    def cls(vals, ref_lo, ref_hi):
        side = ['below' if v < ref_lo else 'above' if v > ref_hi else 'inside' for v in vals]
        if all(s == 'inside' for s in side): return 'INSIDE'
        if len(set(side)) == 1: return 'OUTSIDE-' + side[0].upper()
        return 'STRADDLE'
    G = {s: (min(g[s] for g in gen.values()), float(np.median([g[s] for g in gen.values()])), max(g[s] for g in gen.values())) for s in SS}
    R['gen_range'] = G; V = {}
    for s in SS:
        vals = [voy[k][s] for k in voy]
        a = cls(vals, *rng_n[s]); b = cls(vals, G[s][0], G[s][2])
        V[s] = dict(natural=a if gate[s] else 'NOT TESTABLE', generator=b if (gate[s] and len(gen) >= NG) else 'NOT TESTABLE', voynich=dict(zip(voy, vals)),
                    gen_rank_p={k: float((1 + sum(abs(g[s] - float(np.median([x[s] for x in gen.values()]))) >= abs(voy[k][s] - float(np.median([x[s] for x in gen.values()]))) for g in gen.values())) / (len(gen) + 1)) for k in voy})
    R['verdict'] = V; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C064_results.json', 'w'), indent=1, default=float)
    print('natural range', rng_n); print('gen range', G); print('LOO', loo, 'power', pw, 'gate', gate)
    for k, v in voy.items(): print(k, {a: round(b, 4) for a, b in v.items()})
    for s in SS: print(s, V[s]['natural'], V[s]['generator'])
    print(R['runtime_s'])

if __name__ == '__main__': main()
