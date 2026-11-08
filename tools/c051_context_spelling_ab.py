#!/usr/bin/env python3
"""C051 (F-EMB step 3): (H1) a DIFFUSE plant for the C049/C050 context-spelling link (context clusters sharing a stem),
so that the existence question becomes testable at N = 10,000; (H2) is the link different in Currier A and Currier B
pages? Statistic as C049 (Spearman rho, PPMI context cosine vs 1 - Levenshtein/max, top 200 types).
H2: D = rho_A - rho_B, each group subsampled to 10,000 tokens by whole pages in random order; page-label permutation.
Pre-registered in case-file/C051-context-spelling-ab.md. Seed 5151.
Run: timeout 600 python3 tools/c051_context_spelling_ab.py [pilot]   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c049_context_spelling as E
from c047_pair_currier_split import ivtff_pages_lang

SEED, K, N, NMANTEL, NPAGE, NG1, NG2, ALPHA, FRAC, NCL, PAGE = 5151, 200, 10000, 200, 100, 20, 10, 0.05, 1.0, 10, 115
C = 'data/corpora/'
_LEV = {}

def smat(sp):
    n = len(sp); S = np.ones((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            key = (sp[i], sp[j]) if sp[i] <= sp[j] else (sp[j], sp[i])
            v = _LEV.get(key)
            if v is None: v = _LEV[key] = 1 - E.lev(sp[i], sp[j]) / max(len(sp[i]), len(sp[j]))
            S[i, j] = S[j, i] = v
    return S

def ppmi_unit(lines, types):
    from collections import Counter
    f = Counter(w for l in lines for w in l); ctx = [w for w, _ in f.most_common(E.NCTX)]; ci = {w: i for i, w in enumerate(ctx)}
    ti = {w: i for i, w in enumerate(types)}; M = np.zeros((len(types), E.NCTX))
    for l in lines:
        for i, w in enumerate(l):
            if w in ti:
                for j in range(max(0, i - E.WIN), min(len(l), i + E.WIN + 1)):
                    if j != i and l[j] in ci: M[ti[w], ci[l[j]]] += 1
    tot = M.sum(); pr = M.sum(1, keepdims=True) / tot; pc = M.sum(0, keepdims=True) / tot
    with np.errstate(divide='ignore', invalid='ignore'):
        P = np.log((M / tot) / (pr * pc)); P[~np.isfinite(P)] = 0; P = np.maximum(P, 0)
    n = np.linalg.norm(P, axis=1, keepdims=True); n[n == 0] = 1; return P / n

def rho_of(lines, spell):
    """spell: function word -> tuple of units"""
    types, rc = E.context_sim(lines); sp = [tuple(spell(w)) for w in types]; S = smat(sp)
    a, b = np.triu_indices(len(sp), 1); return E.rho(rc, S[a, b]), rc, S

def mantel(lines, spell, rng):
    r, rc, S = rho_of(lines, spell); a, b = np.triu_indices(K, 1)
    nl = np.array([E.rho(rc, S[q[a], q[b]]) for q in (rng.permutation(K) for _ in range(NMANTEL))])
    return dict(rho=float(r), null_mean=float(nl.mean()), null_sd=float(nl.std()), p=float((1 + (nl >= r).sum()) / (NMANTEL + 1)))

def diffuse_plant(lines, m, rng, frac=FRAC):
    """k-means (NCL clusters, cosine) of the top-K types' PPMI vectors; each cluster gets a random 2-letter stem;
    a fraction frac of member types (length >= 3) have their first two letters replaced by the stem. Diffuse: many
    moderately similar pairs, not a few near-copies."""
    from collections import Counter
    f = Counter(w for l in lines for w in l); types = [w for w, _ in f.most_common(K)]; U = ppmi_unit(lines, types)
    cen = U[rng.choice(K, NCL, replace=False)].copy()
    for _ in range(25):
        lab = np.argmax(U @ cen.T, 1)
        for c in range(NCL):
            if (lab == c).any():
                v = U[lab == c].mean(0); nv = np.linalg.norm(v); cen[c] = v / nv if nv else v
    letters = sorted({c for s in m.values() for c in s}); stems = [''.join(rng.choice(letters, 2)) for _ in range(NCL)]
    m2 = dict(m); used = set(m.values())
    for i in rng.choice(K, int(K * frac), replace=False):
        w = types[i]; s0 = m2[w]
        if len(s0) < 3: continue
        s = stems[lab[i]] + s0[2:]
        if s not in used: used.discard(s0); used.add(s); m2[w] = s
    return m2

def subsample(pl, group, rng):
    pages = sorted({p for p, _ in pl if p in group}); rng.shuffle(pages); by = {}
    for p, l in pl: by.setdefault(p, []).append(l)
    out, t = [], 0
    for p in pages:
        for l in by[p]:
            if t >= N: return out
            out.append(l[:N - t]); t += len(out[-1])
    return out

def D_stat(pl, A, spellA, spellB, seed):
    rng = np.random.default_rng(seed); allp = {p for p, _ in pl}
    return rho_of(subsample(pl, A, rng), spellA)[0] - rho_of(subsample(pl, allp - A, rng), spellB)[0]

def _perm(args):
    pl, A, nA, spellA_is_split, seed = args; rng = np.random.default_rng(seed); pages = sorted({p for p, _ in pl})
    Ap = set(rng.choice(pages, nA, replace=False).tolist()); return D_stat(pl, Ap, SPELL[0], SPELL[1], seed + 7)

SPELL = [None, None]

def perm_test(pl, A, spA, spB, seed, pool):
    SPELL[0], SPELL[1] = spA, spB
    obs = D_stat(pl, A, spA, spB, seed)
    nl = np.array(pool.map(_perm, [(pl, A, len(A), False, seed * 1000 + i) for i in range(NPAGE)]))
    return dict(D=float(obs), null_sd=float(nl.std()), p=float((1 + (np.abs(nl) >= abs(obs)).sum()) / (NPAGE + 1)))

def pseudo_pages(lines, start, ntok):
    L = E.take(lines, start, ntok); pl, cur, t, k = [], [], 0, 0
    for l in L:
        pl.append((f'p{k:04d}', l)); t += len(l)
        if t >= PAGE: k += 1; t = 0
    return pl

def nat_texts():
    g = T.gutenberg
    nat = {'Latin_Caesar': g(C + 'pg218.txt'), 'Latin_Descartes': g(C + 'pg23306.txt'), 'Italian_Dante': g(C + 'pg1012.txt'),
           'Italian_Machiavelli': g(C + 'pg56498.txt'), 'Spanish_Cervantes': g(C + 'pg2000.txt'), 'Hebrew_Genesis': T.hebrew(C + 'Gen.xml'),
           'Hebrew_Exodus': T.hebrew(C + 'Exod.xml'), 'Finnish_Kalevala': g(C + 'pg7000.txt'), 'Finnish_Kivi': g(C + 'pg11940.txt')}
    return {k: [l for l in v if len(l) >= 3] for k, v in nat.items()}

class MapSpell:
    def __init__(self, m): self.m = m
    def __call__(self, w): return self.m[w]

def main():
    pilot = len(sys.argv) > 1 and sys.argv[1] == 'pilot'
    t0 = time.time(); rng = np.random.default_rng(SEED); nat = nat_texts(); names = list(nat)
    R = dict(seed=SEED, K=K, N=N, NMANTEL=NMANTEL, NPAGE=NPAGE, frac=FRAC, clusters=NCL, page_tokens=PAGE)
    if pilot:
        for nm in names[:4]:
            L = E.take(nat[nm], 0, N); m = E.recode(L, rng); m2 = diffuse_plant(L, m, rng)
            print('pilot', nm, round(rho_of(L, MapSpell(m))[0], 4), round(rho_of(L, MapSpell(m2))[0], 4), round(time.time() - t0, 1), flush=True)
        return
    # ---- H1 gates (existence, Mantel at N)
    fp = pw = 0
    for i in range(NG1):
        L = E.take(nat[names[i % len(names)]], 0, N); fp += mantel(L, MapSpell(E.recode(L, rng)), rng)['p'] < ALPHA
        L2 = E.take(nat[names[(i + 4) % len(names)]], N, N); pw += mantel(L2, MapSpell(diffuse_plant(L2, E.recode(L2, rng), rng)), rng)['p'] < ALPHA
        print('H1 gate', i, fp, pw, round(time.time() - t0, 1), flush=True)
    G1 = dict(fpr=f'{fp}/{NG1}', power=f'{pw}/{NG1}', ok=bool(fp <= 2 and pw >= 14)); R['gates_H1'] = G1; print(G1, flush=True)
    with Pool(8) as pool:
        # ---- H2 gates: contiguous split (first 45% pages = pseudo-A) on recoded natural text; power = diffuse plant in pseudo-A only
        fp2 = pw2 = 0; g2 = []
        for i in range(NG2):
            nm = names[i % len(names)]; pl = pseudo_pages(nat[nm], 0, 2 * N + 3000); pages = sorted({p for p, _ in pl})
            A = set(pages[:int(0.45 * len(pages))]); Lall = [l for _, l in pl]; m = E.recode(Lall, rng)
            r0 = perm_test(pl, A, MapSpell(m), MapSpell(m), SEED + 10 * i, pool)
            m2 = diffuse_plant([l for p, l in pl if p in A], m, rng)
            r1 = perm_test(pl, A, MapSpell(m2), MapSpell(m), SEED + 10 * i + 5, pool)
            fp2 += r0['p'] < ALPHA; pw2 += r1['p'] < ALPHA; g2.append(dict(text=nm, null=r0, plant=r1))
            print('H2 gate', i, nm, fp2, pw2, round(r0['D'], 4), round(r1['D'], 4), round(time.time() - t0, 1), flush=True)
        G2 = dict(fpr=f'{fp2}/{NG2}', power=f'{pw2}/{NG2}', ok=bool(fp2 <= 1 and pw2 >= 7), trials=g2); R['gates_H2'] = G2
        V = {}
        for k, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
            pl, lang, _ = ivtff_pages_lang(f); pl = [x for x in pl if lang.get(x[0]) in ('A', 'B')]
            A = {p for p, _ in pl if lang[p] == 'A'}; Bp = {p for p, _ in pl} - A; sp = lambda w: tuple(T.units(w))
            r = perm_test(pl, A, sp, sp, SEED + 77, pool)
            rg = np.random.default_rng(SEED + 99)
            r['mantel_A'] = mantel(subsample(pl, A, rg), sp, rg); r['mantel_B'] = mantel(subsample(pl, Bp, rg), sp, rg)
            r['pages_A'], r['pages_B'] = len(A), len(Bp); V[k] = r
            print(k, round(r['D'], 4), r['p'], round(r['mantel_A']['rho'], 4), r['mantel_A']['p'], round(r['mantel_B']['rho'], 4), r['mantel_B']['p'], round(time.time() - t0, 1), flush=True)
    R['voynich'] = V
    ms = [V[k][g]['p'] < ALPHA / 4 for k in V for g in ('mantel_A', 'mantel_B')]
    H1 = 'NOT TESTABLE' if not G1['ok'] else ('LINKED' if all(ms) else 'NOT LINKED' if not any(ms) else 'SPLIT')
    ps = [V[k]['p'] < ALPHA for k in V]; sg = [np.sign(V[k]['D']) for k in V]
    H2 = 'NOT TESTABLE' if not G2['ok'] else (('A > B' if sg[0] > 0 else 'B > A') if all(ps) and sg[0] == sg[1] else 'NO DIFFERENCE SHOWN' if not any(ps) else 'SPLIT')
    R['verdict'] = dict(H1=H1, H2=H2); R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C051_results.json', 'w'), indent=1, default=float); print(R['verdict'], R['runtime_s'])

if __name__ == '__main__': main()
