#!/usr/bin/env python3
"""C050 (F-EMB step 2): repair of C049's power plant, extended controls (Finnish, devowelled Latin/Italian/Spanish),
an ending-removed variant (pairs whose last unit differs), and the Timm-Schinner generator at matched size (5 seeds).
Statistic as C049 (Spearman rho, PPMI context cosine vs 1 - Levenshtein/max, top 200 types, Mantel 200).
Pre-registered in case-file/C050-context-spelling-step2.md. Seed 5050.
Run: timeout 600 python3 tools/c050_context_spelling_step2.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c049_context_spelling as E
from c004_generator_sweep import generate

SEED, K, NHALF, NPERM, NG, ALPHA, PLANT = 5050, 200, 15000, 200, 20, 0.05, 0.5
GSEEDS, GLINES = [501, 502, 503, 504, 505], 3400
C = 'data/corpora/'

def mantel2(lines, unit, rng, spell=None):
    """returns (all-pairs result, ending-removed result); ending = last unit of the spelling"""
    types, rc = E.context_sim(lines); sp = [unit(w) for w in types] if spell is None else [list(spell[w]) for w in types]
    SM = E.spell_mat(sp); a, b = np.triu_indices(len(sp), 1); last = np.array([s[-1] for s in sp], dtype=object)
    def both(q):
        s = SM[q[a], q[b]]; full = E.rho(rc, s); m = last[q[a]] != last[q[b]]
        return full, E.rho(E.rank(rc[m]), s[m])
    o = both(np.arange(len(sp))); nl = np.array([both(rng.permutation(len(sp))) for _ in range(NPERM)])
    res = []
    for k in (0, 1):
        res.append(dict(rho=float(o[k]), null_mean=float(nl[:, k].mean()), null_sd=float(nl[:, k].std()),
                        p=float((1 + (nl[:, k] >= o[k]).sum()) / (NPERM + 1))))
    return res

def plant(lines, rng, m, frac):
    """frac of the top-K types take the spelling of their nearest PPMI-cosine neighbour (the statistic's own similarity) with one letter changed"""
    types, _ = E.context_sim(lines)
    from collections import Counter
    f = Counter(w for l in lines for w in l); ctx = [w for w, _ in f.most_common(E.NCTX)]; ci = {w: i for i, w in enumerate(ctx)}
    ti = {w: i for i, w in enumerate(types)}; M = np.zeros((K, E.NCTX))
    for l in lines:
        for i, w in enumerate(l):
            if w in ti:
                for j in range(max(0, i - E.WIN), min(len(l), i + E.WIN + 1)):
                    if j != i and l[j] in ci: M[ti[w], ci[l[j]]] += 1
    tot = M.sum(); pr = M.sum(1, keepdims=True) / tot; pc = M.sum(0, keepdims=True) / tot
    with np.errstate(divide='ignore', invalid='ignore'):
        P = np.log((M / tot) / (pr * pc)); P[~np.isfinite(P)] = 0; P = np.maximum(P, 0)
    n = np.linalg.norm(P, axis=1, keepdims=True); n[n == 0] = 1; S = (P / n) @ (P / n).T; np.fill_diagonal(S, -1)
    letters = sorted({c for s in m.values() for c in s}); m2 = dict(m); used = set(m.values())
    for i in rng.choice(K, int(K * frac), replace=False):
        src = m2[types[int(np.argmax(S[i]))]]
        for _ in range(50):
            k = int(rng.integers(len(src))); s = src[:k] + str(rng.choice(letters)) + src[k + 1:]
            if s not in used: used.add(s); m2[types[i]] = s; break
    return m2

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); R = dict(seed=SEED, K=K, NHALF=NHALF, NPERM=NPERM, plant=PLANT, gseeds=GSEEDS)
    g = T.gutenberg
    nat = {'Latin_Caesar': g(C + 'pg218.txt'), 'Latin_Descartes': g(C + 'pg23306.txt'), 'Italian_Dante': g(C + 'pg1012.txt'),
           'Italian_Machiavelli': g(C + 'pg56498.txt'), 'Spanish_Cervantes': g(C + 'pg2000.txt'), 'Hebrew_Genesis': T.hebrew(C + 'Gen.xml'),
           'Hebrew_Exodus': T.hebrew(C + 'Exod.xml'), 'Finnish_Kalevala': g(C + 'pg7000.txt'), 'Finnish_Kivi': g(C + 'pg11940.txt')}
    for k in ('Latin_Caesar', 'Italian_Dante', 'Spanish_Cervantes'): nat[k + '_devowel'] = T.devowel(nat[k])
    nat = {k: [l for l in v if len(l) >= 3] for k, v in nat.items()}
    names = [k for k in nat if not k.endswith('_devowel')]
    fp = [0, 0]; pw = [0, 0]
    for i in range(NG):
        L = E.take(nat[names[i % len(names)]], 0, NHALF); r = mantel2(L, None, rng, spell=E.recode(L, rng))
        L2 = E.take(nat[names[(i + 4) % len(names)]], NHALF, NHALF); r2 = mantel2(L2, None, rng, spell=plant(L2, rng, E.recode(L2, rng), PLANT))
        for k in (0, 1): fp[k] += r[k]['p'] < ALPHA; pw[k] += r2[k]['p'] < ALPHA
        print('gate', i, fp, pw, round(time.time() - t0, 1), flush=True)
    G = {nm: dict(fpr=f'{fp[k]}/{NG}', power=f'{pw[k]}/{NG}', ok=bool(fp[k] <= 2 and pw[k] >= 14)) for k, nm in enumerate(('full', 'ending_removed'))}
    R['gates'] = G
    out = {}
    for k, L in nat.items():
        out[k] = [mantel2(E.take(L, h * NHALF, NHALF), list, rng) for h in (0, 1)]
        print(k, [[round(x['rho'], 4) for x in y] for y in out[k]], round(time.time() - t0, 1), flush=True)
    for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        L = T.voynich(f); out[k] = [mantel2(E.take(L, h * NHALF, NHALF), T.units, rng) for h in (0, 1)]
        print(k, [[(round(x['rho'], 4), x['p']) for x in y] for y in out[k]], round(time.time() - t0, 1), flush=True)
    gen = {}
    for s in GSEEDS:
        L = generate({'text.lines_to_create': GLINES}, s)
        n = sum(map(len, L)) if L else 0
        if not L or n < 2 * NHALF: gen[s] = dict(ok=False, n=n); print('gen', s, n, flush=True); continue
        gen[s] = dict(ok=True, n=n, halves=[mantel2(E.take(L, h * NHALF, NHALF), T.units, rng) for h in (0, 1)])
        print('gen', s, n, [[round(x['rho'], 4) for x in y] for y in gen[s]['halves']], round(time.time() - t0, 1), flush=True)
    R['texts'] = out; R['generator'] = gen
    vo = [y for k in ('ZL3b', 'IT2a') for y in out[k]]
    def link(idx, gate):
        if not G[gate]['ok']: return 'NOT TESTABLE'
        s = [y[idx]['p'] < ALPHA / 4 for y in vo]
        return 'LINKED' if all(s) else 'NOT LINKED' if not any(s) else 'SPLIT'
    def place(vals, ref):
        lo, hi = min(ref), max(ref)
        return ('ABOVE' if all(v > hi for v in vals) else 'BELOW' if all(v < lo for v in vals) else
                'INSIDE' if all(lo <= v <= hi for v in vals) else 'STRADDLE'), [lo, hi]
    natv = [y[0]['rho'] for k in nat for y in out[k]]; genv = [y[0]['rho'] for s in gen if gen[s]['ok'] for y in gen[s]['halves']]
    vv = [y[0]['rho'] for y in vo]
    h2, nr = place(vv, natv); h4 = place(vv, genv) if len(genv) >= 6 else ('NOT TESTABLE', None)
    R['verdict'] = dict(H1=link(0, 'full'), H2=h2, natural_range=nr, H3=link(1, 'ending_removed'), H4=h4[0], generator_range=h4[1])
    R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C050_results.json', 'w'), indent=1, default=float); print(R['verdict'], R['runtime_s'])

if __name__ == '__main__': main()
