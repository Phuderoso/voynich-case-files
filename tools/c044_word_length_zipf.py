#!/usr/bin/env python3
"""C044 (new family F-ZIPF, step 1): word-length dispersion and Zipf rank-frequency slope.
H1: is the coefficient of variation (sd/mean) of Voynich word-token length (EVA glyph units) below the range of
7 natural-language texts at matched length (first N = 15,000 tokens)? H2: is the Zipf slope (least squares of
log10 freq on log10 rank, ranks 1-500) outside the natural range? Leave-one-out FPR gates and planted power gates
run before any Voynich number. Pre-registered in case-file/C044-word-length-zipf.md. Seed 4444.
Run: timeout 600 python3 tools/c044_word_length_zipf.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c030_line_edge_glyphs as L

SEED, N, NBLK, NBOOT, NGW, NGATE, RMAX = 4444, 15000, 20, 200, 6, 40, 500
C = 'data/corpora/'

def lengths(words, tok):
    return np.array([len(tok(w)) if tok else len(w) for w in words], dtype=float)

def cv(l): return float(l.std() / l.mean())

def zipf(words):
    f = np.array(sorted(Counter(words).values(), reverse=True), dtype=float)[:RMAX]
    r = np.arange(1, len(f) + 1); return float(np.polyfit(np.log10(r), np.log10(f), 1)[0])

def boot(vals_fn, items, rng):
    edges = np.linspace(0, len(items), NBLK + 1).astype(int); blocks = [items[edges[b]:edges[b + 1]] for b in range(NBLK)]
    out = []
    for _ in range(NBOOT):
        pick = rng.integers(0, NBLK, NBLK)
        out.append(vals_fn([x for b in pick for x in blocks[b]]))
    return np.percentile(out, [2.5, 97.5]).tolist()

def low_call(x, ci, lo): return bool(x < lo and ci[1] < lo)
def out_call(x, ci, lo, hi): return bool((x < lo and ci[1] < lo) or (x > hi and ci[0] > hi))

def measure(words, tok, rng, ci=True):
    l = lengths(words, tok); m = dict(n=len(words), mean_len=float(l.mean()), sd_len=float(l.std()), cv=cv(l),
        skew=float(((l - l.mean()) ** 3).mean() / l.std() ** 3), zipf=zipf(words), types=len(set(words)),
        len_hist={int(k): int(v) for k, v in sorted(Counter(l.astype(int)).items())})
    if ci:
        m['cv_ci95'] = boot(lambda ls: cv(np.array(ls)), list(l), rng)
        m['zipf_ci95'] = boot(zipf, list(words), rng)
    return m

def plant_len(words, rng, shrink=0.5):
    """concatenate the letters, re-cut into words whose lengths come from a normal with the same mean and shrink*sd"""
    s = ''.join(words); l = lengths(words, None); out, i = [], 0
    while i < len(s) and len(out) < len(words):
        k = max(1, int(round(rng.normal(l.mean(), shrink * l.std())))); out.append(s[i:i + k]); i += k
    return out

def plant_flat(words, rng, p=0.5):
    voc = sorted(set(words)); return [voc[rng.integers(len(voc))] if rng.random() < p else w for w in words]

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED)
    nat = {'Latin_Caesar': [w for l in T.gutenberg(C + 'pg218.txt') for w in l],
           'Latin_Descartes': [w for l in T.gutenberg(C + 'pg23306.txt') for w in l],
           'Italian_Dante': [w for l in T.gutenberg(C + 'pg1012.txt') for w in l],
           'Italian_Machiavelli': [w for l in T.gutenberg(C + 'pg56498.txt') for w in l],
           'Spanish_Cervantes': [w for l in T.gutenberg(C + 'pg2000.txt') for w in l],
           'Hebrew_Genesis': [w for l in T.hebrew(C + 'Gen.xml') for w in l],
           'Hebrew_Exodus': [w for l in T.hebrew(C + 'Exod.xml') for w in l]}
    voy = {'Voynich_ZL3b': [w for ws, _ in L.ivtff_paragraphs('data/ZL3b-n.txt') for w in ws],
           'Voynich_IT2a': [w for ws, _ in L.ivtff_paragraphs('data/IT2a-n.txt') for w in ws]}
    gens = {'Generator_base': [w for ws, _ in L.generator() for w in ws]}
    try:
        import c004_generator_sweep as G
        cfg = dict(json.load(open('analysis/C005_confirm.json'))['A']['selected'], **{'text.lines_to_create': 2400})
        raw = G.generate(cfg, SEED); gens['Generator_C005matched'] = [w for l in (raw or []) for w in l]
    except Exception as e:
        print('C005 generator unavailable:', e)
    R = dict(N=N, seed=SEED, primary_tokenization='Voynich and generators: EVA glyph units (c003.units); natural: letters; '
             'commas read as word spaces (c030.ivtff_paragraphs)', zipf_ranks=f'1-{RMAX}', texts={})
    # ---- 1. natural range
    for k, w in nat.items():
        R['texts'][k] = measure(w[:N], None, rng); print(k, {x: round(y, 3) for x, y in R['texts'][k].items() if isinstance(y, float)}, round(time.time() - t0, 1), 's', flush=True)
    rng_ = lambda key, ex=None: (min(R['texts'][k][key] for k in nat if k != ex), max(R['texts'][k][key] for k in nat if k != ex))
    cvr, zr = rng_('cv'), rng_('zipf'); R['natural_range'] = dict(cv=cvr, zipf=zr)
    # ---- 2. gates, before any Voynich number
    f1 = f2 = n = 0
    for k, w in nat.items():
        lo1, _ = rng_('cv', k); lo2, hi2 = rng_('zipf', k)
        for _ in range(NGW):
            s0 = int(rng.integers(0, max(1, len(w) - N))); ww = w[s0:s0 + N]; m = measure(ww, None, rng)
            f1 += low_call(m['cv'], m['cv_ci95'], lo1); f2 += out_call(m['zipf'], m['zipf_ci95'], lo2, hi2); n += 1
    d = nat['Italian_Dante']; p1 = p2 = 0; pc, pz = [], []
    for _ in range(NGATE):
        s0 = int(rng.integers(0, len(d) - N)); ww = d[s0:s0 + N]
        m = measure(plant_len(ww, rng), None, rng); pc.append(m['cv']); p1 += low_call(m['cv'], m['cv_ci95'], cvr[0])
        m = measure(plant_flat(ww, rng), None, rng); pz.append(m['zipf']); p2 += out_call(m['zipf'], m['zipf_ci95'], *zr)
    g1 = f1 <= 4 and p1 >= 32; g2 = f2 <= 4 and p2 >= 32
    R['gates'] = dict(fpr_H1=f'{f1}/{n}', power_H1=f'{p1}/{NGATE}', ok_H1=g1, plant_cv_mean=float(np.mean(pc)),
                      fpr_H2=f'{f2}/{n}', power_H2=f'{p2}/{NGATE}', ok_H2=g2, plant_zipf_mean=float(np.mean(pz)))
    print('gates', R['gates'], round(time.time() - t0, 1), 's', flush=True)
    # ---- 3. tested texts
    for k, w in {**voy, **gens}.items():
        if len(w) < 1000: R['texts'][k] = dict(error='missing'); continue
        R['texts'][k] = measure(w[:N], T.units, rng); print(k, {x: round(y, 3) for x, y in R['texts'][k].items() if isinstance(y, float)}, flush=True)
    V = {}
    for k in list(voy) + list(gens):
        t = R['texts'].get(k, {})
        if 'cv' not in t: V[k] = 'missing'; continue
        V[k] = dict(cv_low=low_call(t['cv'], t['cv_ci95'], cvr[0]), zipf_out=out_call(t['zipf'], t['zipf_ci95'], *zr),
                    cv_pos='below' if t['cv'] < cvr[0] else ('above' if t['cv'] > cvr[1] else 'inside'),
                    zipf_pos='below' if t['zipf'] < zr[0] else ('above' if t['zipf'] > zr[1] else 'inside'))
    z, i2 = V['Voynich_ZL3b'], V['Voynich_IT2a']
    def verdict(key, ok, yes):
        if not ok: return 'NOT TESTABLE'
        if z[key] and i2[key]: return yes
        if not z[key] and not i2[key]: return 'INSIDE NATURAL' if z[key.split('_')[0] + '_pos'] == i2[key.split('_')[0] + '_pos'] == 'inside' else 'NOT CALLED (outside point range, CI overlaps)'
        return 'SPLIT (ZL and IT2a disagree): not replicated'
    R['verdicts'] = dict(H1=verdict('cv_low', g1, 'UNUSUALLY LOW'), H2=verdict('zipf_out', g2, 'OUTSIDE NATURAL'), per_text=V)
    # ---- 4. descriptive: raw EVA characters
    R['descriptive'] = {f'{k}|raw_EVA_chars': measure(w[:N], None, rng, ci=False) for k, w in voy.items()}
    R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C044_results.json', 'w'), indent=1, default=float)
    print(json.dumps(R['verdicts'], default=str)); print('runtime', R['runtime_s'])

if __name__ == '__main__': main()
