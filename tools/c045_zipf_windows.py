#!/usr/bin/env python3
"""C045 (F-ZIPF step 2): Zipf slope with a window-spread interval that never duplicates tokens (fixes C044's biased
block bootstrap), plus word-length CV against vowelless (devowelled) controls. Pre-registered in
case-file/C045-zipf-windows.md. Seed 4545.
Run: timeout 600 python3 tools/c045_zipf_windows.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c030_line_edge_glyphs as L
from c044_word_length_zipf import zipf, cv, lengths, plant_flat, plant_len

SEED, N, M, NW, NGW, NGATE = 4545, 15000, 7500, 20, 6, 40
C = 'data/corpora/'

def wstats(words, tok, rng, fn):
    """20 random contiguous M-token windows inside the first N tokens (no duplication): median, 2.5/97.5 percentiles"""
    w = words[:N]; v = []
    for _ in range(NW):
        s0 = int(rng.integers(0, len(w) - M + 1)); v.append(fn(w[s0:s0 + M], tok))
    return float(np.median(v)), np.percentile(v, [2.5, 97.5]).tolist()

ZF = lambda ws, tok: zipf(ws)
CF = lambda ws, tok: cv(lengths(ws, tok))

def outside(iv, lo, hi): return bool(iv[1] < lo or iv[0] > hi)
def below(iv, lo): return bool(iv[1] < lo)

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED)
    G = lambda f: [w for l in T.gutenberg(C + f) for w in l]
    nat = {'Latin_Caesar': G('pg218.txt'), 'Latin_Descartes': G('pg23306.txt'), 'Italian_Dante': G('pg1012.txt'),
           'Italian_Machiavelli': G('pg56498.txt'), 'Spanish_Cervantes': G('pg2000.txt'),
           'Hebrew_Genesis': [w for l in T.hebrew(C + 'Gen.xml') for w in l], 'Hebrew_Exodus': [w for l in T.hebrew(C + 'Exod.xml') for w in l]}
    vowl = {f'{k}_vowelless': [w for l in T.devowel(T.gutenberg(C + f)) for w in l]
            for k, f in [('Latin_Caesar', 'pg218.txt'), ('Italian_Dante', 'pg1012.txt'), ('Spanish_Cervantes', 'pg2000.txt')]}
    voy = {'Voynich_ZL3b': [w for ws, _ in L.ivtff_paragraphs('data/ZL3b-n.txt') for w in ws],
           'Voynich_IT2a': [w for ws, _ in L.ivtff_paragraphs('data/IT2a-n.txt') for w in ws]}
    R = dict(N=N, M=M, windows=NW, seed=SEED, texts={})
    for k, w in {**nat, **vowl}.items():
        zm, zi = wstats(w, None, rng, ZF); cm, ci = wstats(w, None, rng, CF)
        R['texts'][k] = dict(n=min(len(w), N), zipf_med=zm, zipf_iv=zi, cv_med=cm, cv_iv=ci)
        print(k, round(zm, 3), [round(x, 3) for x in zi], round(cm, 3), [round(x, 3) for x in ci], flush=True)
    rz = lambda ex=None: (min(R['texts'][k]['zipf_med'] for k in nat if k != ex), max(R['texts'][k]['zipf_med'] for k in nat if k != ex))
    zr = rz(); vr = (min(R['texts'][k]['cv_med'] for k in vowl), max(R['texts'][k]['cv_med'] for k in vowl))
    R['natural_zipf_range'] = zr; R['vowelless_cv_range'] = vr
    # gates before any Voynich number
    f = n = 0
    for k, w in nat.items():
        lo, hi = rz(k)
        for _ in range(NGW):
            s0 = int(rng.integers(0, max(1, len(w) - 12000))); sub = w[s0:s0 + 12000]
            f += outside(wstats(sub, None, rng, ZF)[1], lo, hi); n += 1
    d = nat['Italian_Dante']; p = 0; pz = []
    for _ in range(NGATE):
        s0 = int(rng.integers(0, len(d) - N)); m, iv = wstats(plant_flat(d[s0:s0 + N], rng), None, rng, ZF); pz.append(m); p += outside(iv, *zr)
    gz = f <= 4 and p >= 32
    # H1b gate: vowelless-range call. FPR: vowelless windows vs the other two vowelless; power: Dante halved-sd plant vs vowelless min
    fv = nv = 0
    for k, w in vowl.items():
        lo = min(R['texts'][j]['cv_med'] for j in vowl if j != k)
        for _ in range(14):
            s0 = int(rng.integers(0, max(1, len(w) - 12000))); fv += below(wstats(w[s0:s0 + 12000], None, rng, CF)[1], lo); nv += 1
    pv = sum(below(wstats(plant_len(d[s0:s0 + N], rng, 0.3), None, rng, CF)[1], vr[0]) for s0 in rng.integers(0, len(d) - N, NGATE))
    gv = fv <= 4 and pv >= 32
    R['gates'] = dict(fpr_H1=f'{f}/{n}', power_H1=f'{p}/{NGATE}', ok_H1=gz, plant_zipf_mean=float(np.mean(pz)),
                      fpr_H2=f'{fv}/{nv}', power_H2=f'{pv}/{NGATE}', ok_H2=gv)
    print('gates', R['gates'], round(time.time() - t0, 1), 's', flush=True)
    V = {}
    for k, w in voy.items():
        zm, zi = wstats(w, T.units, rng, ZF); cm, ci = wstats(w, T.units, rng, CF)
        R['texts'][k] = dict(n=min(len(w), N), zipf_med=zm, zipf_iv=zi, cv_med=cm, cv_iv=ci)
        V[k] = dict(zipf_out=outside(zi, *zr), cv_below_vowelless=below(ci, vr[0]),
                    cv_pos_vowelless='below' if cm < vr[0] else ('above' if cm > vr[1] else 'inside'))
        print(k, R['texts'][k], flush=True)
    z, i2 = V['Voynich_ZL3b'], V['Voynich_IT2a']
    def verdict(key, ok, yes, no):
        if not ok: return 'NOT TESTABLE'
        return yes if z[key] and i2[key] else (no if not z[key] and not i2[key] else 'SPLIT: not replicated')
    R['verdicts'] = dict(H1=verdict('zipf_out', gz, 'OUTSIDE NATURAL', 'INSIDE NATURAL'),
                         H2=verdict('cv_below_vowelless', gv, 'NARROWER THAN VOWELLESS', 'NOT NARROWER THAN VOWELLESS'), per_text=V)
    R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C045_results.json', 'w'), indent=1, default=float)
    print(json.dumps(R['verdicts'])); print('runtime', R['runtime_s'])

if __name__ == '__main__': main()
