#!/usr/bin/env python3
"""C041 (new family F-ENT, step 1): conditional glyph entropy h2 = H(X_{i+1}|X_i), in bits (log2).
Is the Voynich glyph stream's h2 below the range of 7 natural-language texts at matched length (first N = 50,000
symbols), and where does the Timm-Schinner self-citation generator sit? Within-word shuffle null, planted gates,
block-bootstrap robustness. Pre-registered in case-file/C041-conditional-entropy-h2.md. Seed 4141.
Run: timeout 600 python3 tools/c041_conditional_entropy.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time, math
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c030_line_edge_glyphs as L

SEED, N, NNULL, NBLK, NBOOT, NGATE, PCOPY = 4141, 50000, 200, 20, 200, 40, 0.6
SP = '_'          # word-space token (kept: one '_' after every word)
C = 'data/corpora/'

def stream(words, tok, space=True, n=N):
    s, wid = [], []
    for k, w in enumerate(words):
        u = tok(w) if tok else list(w)
        if not u: continue
        s.extend(u); wid.extend([k] * len(u))
        if space: s.append(SP); wid.append(-1)
        if len(s) >= n + 100000: break
    return s, wid

def encode(s):
    voc = {}; return np.array([voc.setdefault(x, len(voc)) for x in s], dtype=np.int64), voc

def H(counts):
    c = counts[counts > 0].astype(float); p = c / c.sum(); return float(-(p * np.log2(p)).sum())

def big_counts(a, A):
    return np.bincount(a[:-1] * A + a[1:], minlength=A * A)

def h_from_big(bc, A):
    """h2 = H(pair) - H(first of pair)"""
    return H(bc) - H(bc.reshape(A, A).sum(1))

def metrics(a, A):
    bc = big_counts(a, A); alph = int((np.bincount(a, minlength=A) > 0).sum())
    h1 = H(np.bincount(a, minlength=A)); h2 = h_from_big(bc, A)
    return dict(h1=h1, h2=h2, A=alph, h2_norm=h2 / math.log2(alph))

def wshuffle(a, wid, rng):
    """permute glyphs inside each word; spaces (wid -1) keep their own unique slot"""
    w = wid.copy(); sp = w < 0; w[sp] = -(np.arange(sp.sum()) + 1)  # unique id per space, order kept
    # order key: word position (first index of each word id) then random
    _, first = np.unique(w, return_index=True); pos = np.empty(len(w), np.int64)
    u, inv = np.unique(w, return_inverse=True); pos = first[inv]
    o = np.lexsort((rng.random(len(w)), pos)); return a[o]

def boot_ci(a, A, rng, norm=False):
    edges = np.linspace(0, len(a), NBLK + 1).astype(int)
    blk = [big_counts(a[edges[b]:edges[b + 1]], A) for b in range(NBLK)]
    al = int((np.bincount(a, minlength=A) > 0).sum()); out = []
    for _ in range(NBOOT):
        bc = sum(blk[b] for b in rng.integers(0, NBLK, NBLK)); h = h_from_big(bc, A)
        out.append(h / math.log2(al) if norm else h)
    return np.percentile(out, [2.5, 97.5]).tolist()

def prep(words, tok, space=True, n=N):
    s, wid = stream(words, tok, space); s, wid = s[:n], np.array(wid[:n]); a, voc = encode(s); return a, wid, len(voc)

def plant_copy(a, wid, rng, p=PCOPY):
    """Voynich-like low-h2 plant: draw a random successor map f (one preferred follower per symbol); inside each word,
    every glyph after the first is replaced, with prob p, by f(previous, already rewritten glyph) (never by the space)"""
    A = int(a.max()) + 1; f = rng.integers(0, A, A); sp = a[np.nonzero(wid < 0)[0][0]]
    b = a.copy(); same = np.zeros(len(a), bool); same[1:] = (wid[1:] == wid[:-1]) & (wid[1:] >= 0)
    for i in np.nonzero(same & (rng.random(len(a)) < p))[0]:
        nx = f[b[i - 1]]; b[i] = nx if nx != sp else b[i]
    return b

def low_call(h2, ci_hi, nat_min):
    return bool(h2 < nat_min and ci_hi < nat_min)

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED)
    gens = {'Generator_base': [w for ws, _ in L.generator() for w in ws]}
    try:
        import c004_generator_sweep as G
        cfg = dict(json.load(open('analysis/C005_confirm.json'))['A']['selected'], **{'text.lines_to_create': 2400})
        raw = G.generate(cfg, SEED); gens['Generator_C005matched'] = [w for l in (raw or []) for w in l]
    except Exception as e:
        print('C005 generator unavailable:', e)
    voy = {'Voynich_ZL3b': [w for ws, _ in L.ivtff_paragraphs('data/ZL3b-n.txt') for w in ws],
           'Voynich_IT2a': [w for ws, _ in L.ivtff_paragraphs('data/IT2a-n.txt') for w in ws]}
    nat = {'Latin_Caesar': [w for l in T.gutenberg(C + 'pg218.txt') for w in l],
           'Latin_Descartes': [w for l in T.gutenberg(C + 'pg23306.txt') for w in l],
           'Italian_Dante': [w for l in T.gutenberg(C + 'pg1012.txt') for w in l],
           'Italian_Machiavelli': [w for l in T.gutenberg(C + 'pg56498.txt') for w in l],
           'Spanish_Cervantes': [w for l in T.gutenberg(C + 'pg2000.txt') for w in l],
           'Hebrew_Genesis': [w for l in T.hebrew(C + 'Gen.xml') for w in l],
           'Hebrew_Exodus': [w for l in T.hebrew(C + 'Exod.xml') for w in l]}
    tok = {k: T.units for k in list(voy) + list(gens)}
    R = dict(N=N, seed=SEED, log='log2 (bits)', primary_tokenization='EVA glyph units (c003.units: cth ckh cph cfh ch sh single), '
             'commas read as word spaces (c030.ivtff_paragraphs), one space token after every word', texts={})
    # ---- 1. natural texts first: range, own nulls
    def measure(k, words):
        a, wid, A = prep(words, tok.get(k)); m = metrics(a, A)
        nl = np.array([metrics(wshuffle(a, wid, rng), A)['h2'] for _ in range(NNULL)])
        m.update(n=int(len(a)), null_mean=float(nl.mean()), null_sd=float(nl.std()),
                 p_low=float((1 + (nl <= m['h2']).sum()) / (NNULL + 1)),
                 ci95=boot_ci(a, A, rng), ci95_norm=boot_ci(a, A, rng, norm=True))
        R['texts'][k] = m; print(k, {x: (round(y, 4) if isinstance(y, float) else y) for x, y in m.items() if x not in ('ci95', 'ci95_norm')}, round(time.time() - t0, 1), 's', flush=True)
    for k, w in nat.items(): measure(k, w)
    nmin = min(R['texts'][k]['h2'] for k in nat); nmax = max(R['texts'][k]['h2'] for k in nat)
    qmin = min(R['texts'][k]['h2_norm'] for k in nat); qmax = max(R['texts'][k]['h2_norm'] for k in nat)
    R['natural_range'] = dict(h2=[nmin, nmax], h2_norm=[qmin, qmax])
    # leave-one-out spread check (descriptive): is any natural text "low" against the other six?
    R['natural_loo_low'] = {k: low_call(R['texts'][k]['h2'], R['texts'][k]['ci95'][1], min(R['texts'][j]['h2'] for j in nat if j != k)) for k in nat}
    # ---- 2. gates on Caesar (natural only), before any Voynich number
    ca, cwid, cA = prep(nat['Latin_Caesar'], None, n=10 ** 9); fp = pw = 0; fpn = pwn = 0; ph = []
    for g in range(NGATE):
        s0 = int(rng.integers(0, len(ca) - N)); a = ca[s0:s0 + N]; wid = cwid[s0:s0 + N]
        sh = wshuffle(a, wid, rng); m = metrics(sh, cA)
        fp += low_call(m['h2'], boot_ci(sh, cA, rng)[1], nmin); fpn += low_call(m['h2_norm'], boot_ci(sh, cA, rng, True)[1], qmin)
        pl = plant_copy(a, wid, rng); m = metrics(pl, cA); ph.append(m['h2'])
        pw += low_call(m['h2'], boot_ci(pl, cA, rng)[1], nmin); pwn += low_call(m['h2_norm'], boot_ci(pl, cA, rng, True)[1], qmin)
    gate_ok = fp <= 4 and pw >= 32; gate2_ok = fpn <= 4 and pwn >= 32
    R['gates'] = dict(fpr=f'{fp}/{NGATE}', power=f'{pw}/{NGATE}', ok=gate_ok, fpr_norm=f'{fpn}/{NGATE}', power_norm=f'{pwn}/{NGATE}',
                      ok_norm=gate2_ok, plant_h2_mean=float(np.mean(ph)), caesar_symbols=int(len(ca)))
    print('gates', R['gates'], round(time.time() - t0, 1), 's', flush=True)
    # ---- 3. tested texts
    for k, w in {**voy, **gens}.items():
        if len(w) < 1000: R['texts'][k] = dict(error='missing'); continue
        measure(k, w)
    def pos(x, r): return 'inside' if r[0] <= x <= r[1] else ('above' if x > r[1] else 'below')
    V = {}
    for k in list(voy) + list(gens):
        t = R['texts'].get(k, {})
        if 'h2' not in t: V[k] = 'missing'; continue
        V[k] = dict(h2_vs_natural=pos(t['h2'], [nmin, nmax]), h2_norm_vs_natural=pos(t['h2_norm'], [qmin, qmax]),
                    robust_low=low_call(t['h2'], t['ci95'][1], nmin), robust_low_norm=low_call(t['h2_norm'], t['ci95_norm'][1], qmin))
    z, i2 = V['Voynich_ZL3b'], V['Voynich_IT2a']
    def verdict(key, ok):
        if not ok: return 'NOT TESTABLE'
        if z[key] and i2[key]: return 'UNUSUALLY LOW'
        if not z[key] and not i2[key]:
            return 'INSIDE NATURAL' if all(V[x][('h2_norm' if 'norm' in key else 'h2') + '_vs_natural'] == 'inside' for x in voy) else 'NOT LOW (outside range on the high side or mixed)'
        return 'SPLIT (ZL and IT2a disagree): not replicated'
    R['verdicts'] = dict(H1=verdict('robust_low', gate_ok), H2=verdict('robust_low_norm', gate2_ok), per_text=V)
    # ---- 4. descriptive: secondary tokenizations
    D = {}
    for k, w in voy.items():
        for lab, tk, spc in [('raw_EVA_chars', None, True), ('units_no_space', T.units, False)]:
            a, wid, A = prep(w, tk, spc); D[f'{k}|{lab}'] = metrics(a, A)
    for k, w in nat.items():
        a, wid, A = prep(w, None, False); D[f'{k}|no_space'] = metrics(a, A)
    for k, f in [('Latin_Caesar', 'pg218.txt'), ('Italian_Dante', 'pg1012.txt')]:
        a, wid, A = prep([x for l in T.devowel(T.gutenberg(C + f)) for x in l], None); D[f'{k}|vowelless'] = metrics(a, A)
    R['descriptive'] = D; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C041_results.json', 'w'), indent=1, default=float)
    print(json.dumps(R['verdicts'], default=str)); print('runtime', R['runtime_s'])

if __name__ == '__main__': main()
