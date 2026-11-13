#!/usr/bin/env python3
"""C111 (new approach family F-HMM, step 1): do two independent blind 'two-class' finders agree on the manuscript's glyphs?
A 2-state hidden Markov model (Baum-Welch, words as separate sequences, 10 random restarts, best log-likelihood kept) assigns
each glyph type to the state that holds most of its posterior mass. Sukhotin's algorithm (C108, unchanged) gives a second
partition. Statistic AGR = token-weighted share of glyph tokens (types with >= MINTOK tokens) whose HMM state matches their
Sukhotin class, best of the two label matchings (0.5..1).
Null (primary, N-TYPE): permute the Sukhotin labels among the kept glyph types (class sizes kept), NPERM 10000;
p = (1 + #{AGR_null >= AGR}) / (1 + NPERM). Its calibration against frequency-driven agreement is checked by gate G2 (iid text).
Sensitivity (N-BLOCK4, frequency-blocked): sort types by token count, cut into consecutive blocks of 4, permute labels only inside
blocks; its exact floor (prod over blocks of 1/C(|b|, #V in b)) is printed, because it can be above alpha/4 by construction.
Pre-registered in case-file/C111-hmm-sukhotin-convergence.md. Seeds 11748 (main), 11749-11752 (generator); next free 11753.
Run: timeout 600 python3 tools/c111_hmm_sukhotin_convergence.py   - Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c051_context_spelling_ab as B
from c047_pair_currier_split import ivtff_pages_lang
from c004_generator_sweep import generate
from c108_sukhotin_alternation import encode, alt, flat, chars, halves, VOWELS, NHALF, shuffle_within

SEED, NPERM, NG, ALPHA, MINTOK, BLOCK = 11748, 10000, 20, 0.05, 20, 4
NRESTART, NITER, TOL = 8, 150, 1e-6
GSEEDS, GLINES = [11749, 11750, 11751, 11752], 3400
PLANT_SHUF = 0.80        # G3: share of words within-word shuffled in a voweled half (heavy dilution; 0.50 gave AGR 1.0 in the smoke)

def pad(ids, wid):
    W = int(wid[-1]) + 1; lens = np.bincount(wid, minlength=W); L = int(lens.max())
    pos = np.arange(len(ids)) - np.repeat(np.cumsum(lens) - lens, lens)
    X = np.zeros((W, L), np.int64); M = np.zeros((W, L), bool); X[wid, pos] = ids; M[wid, pos] = True
    return X, M

def fit_hmm(X, M, S, rng):
    W, L = X.shape; pi = rng.dirichlet([1, 1]); A = rng.dirichlet([1, 1], 2); Bm = rng.dirichlet(np.ones(S), 2)
    last = -np.inf
    for it in range(NITER):
        al = np.zeros((W, L, 2)); c = np.ones((W, L))
        a = pi[None] * Bm[:, X[:, 0]].T; c[:, 0] = a.sum(1); al[:, 0] = a / c[:, :1]
        for t in range(1, L):
            a = (al[:, t - 1] @ A) * Bm[:, X[:, t]].T; s = a.sum(1); m = M[:, t]
            c[m, t] = s[m]; al[m, t] = a[m] / s[m, None]; al[~m, t] = al[~m, t - 1]
        be = np.ones((W, L, 2)); xi = np.zeros((2, 2))
        for t in range(L - 2, -1, -1):
            m = M[:, t + 1]; e = Bm[:, X[:, t + 1]].T * be[:, t + 1]
            b = (e @ A.T) / c[:, t + 1:t + 2]; be[m, t] = b[m]
            xi += np.einsum('wi,ij,wj->ij', al[m, t], A, e[m] / c[m, t + 1:t + 2])
        ll = float(np.log(c[M]).sum()); g = al * be; g = g / g.sum(2, keepdims=True)
        pi = g[:, 0].mean(0); A = xi / xi.sum(1, keepdims=True)
        Bn = np.zeros((2, S)); np.add.at(Bn.T, X[M], g[M]); Bm = (Bn + 1e-12) / (Bn + 1e-12).sum(1, keepdims=True)
        if ll - last < TOL * abs(ll): break
        last = ll
    G = np.zeros((S, 2)); np.add.at(G, X[M], g[M])
    return ll, G, A, it + 1

def hmm_labels(words, rng):
    ids, wid, inv = encode(words); S = len(inv); X, M = pad(ids, wid); best = None; labs = []
    for r in range(NRESTART):
        ll, G, A, it = fit_hmm(X, M, S, rng); h = G.argmax(1); labs.append(h)
        if best is None or ll > best[0]: best = (ll, G, A, it, h)
    n = np.bincount(ids, minlength=S); keep = n >= MINTOK; hb = best[4]
    stab = float(np.mean([max(np.mean(l[keep] == hb[keep]), np.mean(l[keep] != hb[keep])) >= 0.999 for l in labs]))
    return ids, wid, inv, n, keep, best, stab

def agr(h, V, n):
    a = float((n * (h == V)).sum() / n.sum()); return max(a, 1 - a)

def type_null(h, V, n, rng, nperm=NPERM):
    Vp = np.take_along_axis(np.tile(V, (nperm, 1)), np.argsort(rng.random((nperm, len(V))), 1), 1)
    a = ((Vp == h[None]) * n[None]).sum(1) / n.sum(); return np.maximum(a, 1 - a)

def block_floor(V, n):
    from math import comb
    order = np.argsort(-n, kind='stable'); V = V[order]; f = 1.0
    for i in range(0, len(V), BLOCK): b = V[i:i + BLOCK]; f /= comb(len(b), int(b.sum()))
    return f

def block_null(h, V, n, rng, nperm=NPERM):
    order = np.argsort(-n, kind='stable'); h, V, n = h[order], V[order], n[order]; K = len(n)
    blocks = [np.arange(i, min(i + BLOCK, K)) for i in range(0, K, BLOCK)]
    Vp = np.tile(V, (nperm, 1))
    for b in blocks:
        if len(b) > 1: Vp[:, b] = np.take_along_axis(Vp[:, b], np.argsort(rng.random((nperm, len(b))), 1), 1)
    a = ((Vp == h[None]) * n[None]).sum(1) / n.sum(); return np.maximum(a, 1 - a)

def test(words, rng, nperm=NPERM, truth=None):
    ids, wid, inv, n, keep, best, stab = hmm_labels(words, rng); S = len(inv)
    _, V = alt(ids, wid, S); h = best[4]
    a = agr(h[keep], V[keep], n[keep]); null = type_null(h[keep], V[keep], n[keep], rng, nperm)
    nb = block_null(h[keep], V[keep], n[keep], rng, nperm)
    cls = lambda lab: sorted(inv[i] for i in np.where(keep & (lab == lab[int(np.argmax(np.where(keep, n, -1)))]))[0])
    out = dict(AGR=round(a, 4), null_mean=round(float(null.mean()), 4), null_sd=round(float(null.std()), 4),
               p=(1 + int((null >= a).sum())) / (1 + nperm),
               p_block4=(1 + int((nb >= a).sum())) / (1 + nperm), block4_floor=block_floor(V[keep], n[keep]), ntypes=int(keep.sum()), nsym=S, ntok=int(n[keep].sum()),
               restart_stability=round(stab, 2), hmm_iters=best[3], hmm_A=np.round(best[2], 3).tolist(),
               hmm_class_of_top=cls(h), sukhotin_V=sorted(inv[i] for i in np.where(keep & V)[0]))
    if truth is not None:
        tv = np.array([u in truth for u in inv]); out['HMM_vs_true_vowels'] = round(agr(h[keep], tv[keep], n[keep]), 4)
        out['Sukhotin_vs_true_vowels'] = round(agr(V[keep], tv[keep], n[keep]), 4)
    return out

def iid_words(words, rng):
    """G2: keep word lengths, draw every unit iid from the half's unit distribution (no structure: both partitions noise)"""
    u = [x for w in words for x in w]; d = rng.permutation(len(u)); out = []; p = 0
    for w in words: out.append(tuple(u[j] for j in d[p:p + len(w)])); p += len(w)
    return out

def partial_shuffle(words, rng, q):
    return [tuple(rng.permutation(w)) if rng.random() < q else w for w in words]

def place(vals, ref):
    lo, hi = min(ref), max(ref)
    return ('ABOVE' if all(v > hi for v in vals) else 'BELOW' if all(v < lo for v in vals) else
            'INSIDE' if all(lo <= v <= hi for v in vals) else 'STRADDLE'), [lo, hi]

def _run(task):
    idx, name, words, nperm, truth = task
    return idx, name, test(words, np.random.default_rng(np.random.SeedSequence([SEED, idx])), nperm, truth)

def main():
    """all inputs are built first from rng(SEED); every test then gets its own rng SeedSequence([SEED, task index])"""
    from multiprocessing import Pool
    t0 = time.time(); rng = np.random.default_rng(SEED); nat = B.nat_texts()
    for k in ('Latin_Caesar', 'Italian_Dante', 'Spanish_Cervantes'): nat[k + '_devowel'] = [l for l in T.devowel(nat[k]) if len(l) >= 3]
    voweled = list(VOWELS); abjad = [k for k in nat if k.startswith('Hebrew') or k.endswith('_devowel')]
    R = dict(seed=SEED, NHALF=NHALF, NPERM=NPERM, NG=NG, alpha=ALPHA, MINTOK=MINTOK, BLOCK=BLOCK, NRESTART=NRESTART,
             NITER=NITER, TOL=TOL, plant_shuf=PLANT_SHUF, gseeds=GSEEDS, glines=GLINES)
    tasks = []
    for i in range(NG):
        k = voweled[i % len(voweled)]; H = halves(nat[k]); words = chars(flat(H[(i // len(voweled)) % len(H)]))
        tasks.append((len(tasks), f'G2|{k}', iid_words(words, rng), 2000, None))
        tasks.append((len(tasks), f'G3|{k}', partial_shuffle(words, rng, PLANT_SHUF), 2000, None))
    for k in nat:
        tr = set(VOWELS[k]) if k in VOWELS else None
        for h, L in enumerate(halves(nat[k])): tasks.append((len(tasks), f'T|{k}|{h}', chars(flat(L)), NPERM, tr))
    for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        pl, lang, _ = ivtff_pages_lang(f); lines = [l for p, l in pl]
        for h, L in enumerate(halves(lines)): tasks.append((len(tasks), f'T|{k}|{h}', [tuple(T.units(w)) for w in flat(L)], NPERM, None))
    gen = {}
    for s in GSEEDS:
        L = generate({'text.lines_to_create': GLINES}, s); n = sum(map(len, L)) if L else 0
        gen[s] = dict(ok=bool(L) and n >= 2 * NHALF, n=n, halves=[])
        if gen[s]['ok']:
            for h, Hh in enumerate(halves(L)): tasks.append((len(tasks), f'GEN|{s}|{h}', [tuple(T.units(w)) for w in flat(Hh)], NPERM, None))
    print('tasks', len(tasks), round(time.time() - t0, 1), flush=True)
    res = {}
    with Pool(8) as P:
        for idx, name, r in P.imap_unordered(_run, tasks):
            res[idx] = (name, r); print(idx, name, r['AGR'], r['p'], r['restart_stability'], round(time.time() - t0, 1), flush=True)
    res = [res[i] for i in range(len(tasks))]
    g2 = [r for n_, r in res if n_.startswith('G2')]; g3 = [r for n_, r in res if n_.startswith('G3')]
    fp = sum(r['p'] < ALPHA for r in g2); pw = sum(r['p'] < ALPHA for r in g3)
    out = {}
    for n_, r in res:
        if n_.startswith('T|'): out.setdefault(n_.split('|')[1], []).append(r)
        if n_.startswith('GEN|'): gen[int(n_.split('|')[1])]['halves'].append(r)
    vp = [y['p'] for k in voweled for y in out[k]]
    G = dict(G1_voweled_converge=f'{sum(p < ALPHA for p in vp)}/{len(vp)}', G2_fpr=f'{fp}/{NG}', G3_power=f'{pw}/{NG}',
             G2_detail=[(r['AGR'], r['p']) for r in g2], G3_detail=[(r['AGR'], r['p']) for r in g3])
    G['ok'] = bool(sum(p < ALPHA for p in vp) >= 0.9 * len(vp) and fp <= 2 and pw >= 16)
    R['gates'] = G; print({k: v for k, v in G.items() if 'detail' not in k}, flush=True)
    R['texts'] = out; R['generator'] = gen
    vo = [y for k in ('ZL3b', 'IT2a') for y in out[k]]; vv = [y['AGR'] for y in vo]
    nv = [y['AGR'] for k in voweled for y in out[k]]; na = [y['AGR'] for k in abjad for y in out[k]]
    genv = [y['AGR'] for s_ in gen if gen[s_]['ok'] for y in gen[s_]['halves']]
    if not G['ok']: V = dict(H1='NOT TESTABLE', H2='NOT TESTABLE', H3='NOT TESTABLE')
    else:
        sg = [y['p'] < ALPHA / 4 for y in vo]
        V = dict(H1='CONVERGE' if all(sg) else 'NO CONVERGENCE' if not any(sg) else 'SPLIT')
        V['H2'], V['voweled_range'] = place(vv, nv); V['abjad_place'], V['abjad_range'] = place(vv, na)
        V['H3'], V['generator_range'] = place(vv, genv) if len(genv) >= 6 else ('NOT TESTABLE', None)
    V['voynich_AGR'] = vv; V['voynich_p'] = [y['p'] for y in vo]; V['voynich_p_block4'] = [y['p_block4'] for y in vo]
    V['voynich_block4_floor'] = [y['block4_floor'] for y in vo]
    R['verdict'] = V; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C111_results.json', 'w'), indent=1, default=float); print(V, R['runtime_s'])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'smoke':
        rng = np.random.default_rng(1); nat = B.nat_texts(); t0 = time.time()
        w = chars(flat(halves(nat['Latin_Caesar'])[0]))
        print('smoke Latin Caesar h1', test(w, rng, 2000, truth=set('aeiouy')), round(time.time() - t0, 1))
        print('smoke iid', test(iid_words(w, rng), rng, 2000), round(time.time() - t0, 1))
        print('smoke plant', test(partial_shuffle(w, rng, PLANT_SHUF), rng, 2000), round(time.time() - t0, 1))
    else: main()
