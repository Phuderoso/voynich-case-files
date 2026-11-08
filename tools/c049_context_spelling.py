#!/usr/bin/env python3
"""C049 (new family F-EMB, distributional embeddings): do word types that appear in similar contexts also look alike?
rho = Spearman correlation, over all pairs of the K=200 most frequent types, between context similarity (cosine of
PPMI vectors from +-2 in-line neighbours, 500 context words) and spelling similarity (1 - Levenshtein/max length,
EVA units for Voynich/generator, letters for natural text). Mantel permutation of spellings across types.
Pre-registered in case-file/C049-context-spelling.md. Seed 4949.
Run: timeout 600 python3 tools/c049_context_spelling.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T

SEED, K, NCTX, WIN, NHALF, NPERM, NG, ALPHA = 4949, 200, 500, 2, 15000, 200, 20, 0.05
C = 'data/corpora/'

def take(lines, start, n):
    out, t, seen = [], 0, 0
    for l in lines:
        if seen < start: seen += len(l); continue
        if t >= n: break
        out.append(l); t += len(l)
    return out

def lev(a, b):
    d = np.arange(len(b) + 1)
    for i, x in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            cur = d[j]; d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (x != y)); prev = cur
    return int(d[len(b)])

def rank(x):
    o = np.argsort(x, kind='mergesort'); r = np.empty(len(x)); r[o] = np.arange(len(x)); xs = x[o]
    # average ties
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[i]: j += 1
        if j > i: r[o[i:j + 1]] = (i + j) / 2
        i = j + 1
    return r

def context_sim(lines):
    from collections import Counter
    f = Counter(w for l in lines for w in l); types = [w for w, _ in f.most_common(K)]; ctx = [w for w, _ in f.most_common(NCTX)]
    ti = {w: i for i, w in enumerate(types)}; ci = {w: i for i, w in enumerate(ctx)}; M = np.zeros((K, NCTX))
    for l in lines:
        for i, w in enumerate(l):
            if w not in ti: continue
            for j in range(max(0, i - WIN), min(len(l), i + WIN + 1)):
                if j != i and l[j] in ci: M[ti[w], ci[l[j]]] += 1
    tot = M.sum(); pr = M.sum(1, keepdims=True) / tot; pc = M.sum(0, keepdims=True) / tot
    with np.errstate(divide='ignore', invalid='ignore'):
        P = np.log((M / tot) / (pr * pc)); P[~np.isfinite(P)] = 0; P = np.maximum(P, 0)
    n = np.linalg.norm(P, axis=1, keepdims=True); n[n == 0] = 1; U = P / n; S = U @ U.T
    a, b = np.triu_indices(K, 1); return types, rank(S[a, b])

def spell_mat(sp):
    n = len(sp); S = np.ones((n, n))
    for i in range(n):
        for j in range(i + 1, n): S[i, j] = S[j, i] = 1 - lev(sp[i], sp[j]) / max(len(sp[i]), len(sp[j]))
    return S

def rho(rc, s):
    rs = rank(s); rs = rs - rs.mean(); r = rc - rc.mean(); return float((r @ rs) / np.sqrt((r @ r) * (rs @ rs)))

def mantel(lines, unit, rng, spell=None):
    types, rc = context_sim(lines); sp = [unit(w) for w in types] if spell is None else [spell[w] for w in types]
    SM = spell_mat(sp); a, b = np.triu_indices(len(sp), 1); obs = rho(rc, SM[a, b]); nl = []
    for _ in range(NPERM):
        q = rng.permutation(len(sp)); nl.append(rho(rc, SM[q[a], q[b]]))
    nl = np.array(nl); return dict(rho=obs, null_mean=float(nl.mean()), null_sd=float(nl.std()), p=float((1 + (nl >= obs).sum()) / (NPERM + 1))), types, rc, sp

def recode(lines, rng):
    """bijection type -> random string of the same length over the text's own letters (kills spelling-context link)"""
    letters = sorted({c for l in lines for w in l for c in w}); m, used = {}, set()
    for w in sorted({w for l in lines for w in l}):
        while True:
            s = ''.join(rng.choice(letters, len(w)))
            if s not in used: used.add(s); m[w] = s; break
    return m

def plant(lines, rng, m):
    """power plant: on a recoded text, 25% of the top-K types take the spelling of their nearest context neighbour with one letter changed"""
    types, _ = context_sim(lines); from collections import Counter
    f = Counter(w for l in lines for w in l)
    tot = sum(f.values()); ctx = [w for w, _ in f.most_common(NCTX)]; ci = {w: i for i, w in enumerate(ctx)}; ti = {w: i for i, w in enumerate(types)}
    M = np.zeros((K, NCTX))
    for l in lines:
        for i, w in enumerate(l):
            if w in ti:
                for j in range(max(0, i - WIN), min(len(l), i + WIN + 1)):
                    if j != i and l[j] in ci: M[ti[w], ci[l[j]]] += 1
    n = np.linalg.norm(M, axis=1, keepdims=True); n[n == 0] = 1; S = (M / n) @ (M / n).T; np.fill_diagonal(S, -1)
    letters = sorted({c for s in m.values() for c in s}); m2 = dict(m); used = set(m.values())
    for i in rng.choice(K, K // 4, replace=False):
        src = m[types[int(np.argmax(S[i]))]]
        for _ in range(50):
            k = int(rng.integers(len(src))); s = src[:k] + str(rng.choice(letters)) + src[k + 1:]
            if s not in used: used.add(s); m2[types[i]] = s; break
    return m2

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); R = dict(seed=SEED, K=K, NCTX=NCTX, WIN=WIN, NHALF=NHALF, NPERM=NPERM)
    nat = {'Latin_Caesar': T.gutenberg(C + 'pg218.txt'), 'Latin_Descartes': T.gutenberg(C + 'pg23306.txt'),
           'Italian_Dante': T.gutenberg(C + 'pg1012.txt'), 'Italian_Machiavelli': T.gutenberg(C + 'pg56498.txt'),
           'Spanish_Cervantes': T.gutenberg(C + 'pg2000.txt'), 'Hebrew_Genesis': T.hebrew(C + 'Gen.xml'), 'Hebrew_Exodus': T.hebrew(C + 'Exod.xml')}
    nat = {k: [l for l in v if len(l) >= 3] for k, v in nat.items()}
    letters = list
    # gates: FPR on recoded natural halves, power on planted recodes
    fp = pw = 0; names = list(nat)
    for g in range(NG):
        L = take(nat[names[g % len(names)]], 0, NHALF); m = recode(L, rng)
        fp += mantel(L, None, rng, spell=m)[0]['p'] < ALPHA
        L2 = take(nat[names[(g + 3) % len(names)]], NHALF, NHALF); m2 = plant(L2, rng, recode(L2, rng))
        pw += mantel(L2, None, rng, spell=m2)[0]['p'] < ALPHA
        print('gate', g, fp, pw, round(time.time() - t0, 1), flush=True)
    R['gates'] = dict(fpr=f'{fp}/{NG}', power=f'{pw}/{NG}', ok=bool(fp <= 2 and pw >= 14))
    texts = {k: (v, list) for k, v in nat.items()}
    texts['ZL3b'] = (T.voynich('data/ZL3b-n.txt'), T.units); texts['IT2a'] = (T.voynich('data/IT2a-n.txt'), T.units)
    out = {}
    for k, (L, u) in texts.items():
        out[k] = [mantel(take(L, h * NHALF, NHALF), u, rng)[0] for h in (0, 1)]
        print(k, [(round(x['rho'], 4), x['p']) for x in out[k]], round(time.time() - t0, 1), flush=True)
    G = [l for l in ([re.findall(r'[a-z]+', x) for x in open(C + 'ts_generated_text.txt') if not x.startswith('#')]) if l]
    look = dict(generator_10k=mantel(take(G, 0, 10000), T.units, rng)[0],
                ZL3b_first10k=mantel(take(texts['ZL3b'][0], 0, 10000), T.units, rng)[0])
    print('look', look, flush=True)
    R['texts'] = out; R['look_generator'] = look
    vo = [x for k in ('ZL3b', 'IT2a') for x in out[k]]; na = [x['rho'] for k in nat for x in out[k]]
    h1 = 'NOT TESTABLE' if not R['gates']['ok'] else ('LINKED' if all(x['p'] < ALPHA / 4 for x in vo) else
                                                      ('NOT LINKED' if all(x['p'] >= ALPHA / 4 for x in vo) else 'SPLIT'))
    lo, hi = min(na), max(na); vr = [x['rho'] for x in vo]
    h2 = 'HIGHER' if all(v > hi for v in vr) else 'LOWER' if all(v < lo for v in vr) else 'INSIDE' if all(lo <= v <= hi for v in vr) else 'STRADDLE'
    R['verdict'] = dict(H1=h1, H2=h2, natural_range=[lo, hi]); R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C049_results.json', 'w'), indent=1, default=float); print(R['verdict'], R['runtime_s'])

if __name__ == '__main__': main()
