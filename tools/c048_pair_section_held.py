#!/usr/bin/env python3
"""C048 (F-PAIR step 3): separate language from section in the same-line pair excess E.
T1 herbal A vs herbal B (section held); T2 herbal B vs non-herbal B (language held). Two-sided page-label permutation,
Bonferroni alpha 0.025; gates sized to each test on natural texts. Pre-registered in case-file/C048-pair-section-held.md.
Seed 4848. Run: timeout 600 python3 tools/c048_pair_section_held.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
from c046_line_pair_recurrence import Text, blocks, cap
from c047_pair_currier_split import ivtff_pages_lang, E, diff, contiguous_A

SEED, NPERM, NPERM_G, NG, ALPHA = 4848, 200, 40, 20, 0.025
C = 'data/corpora/'

def perm2(pl, A, rng, nperm):
    pages = list(dict.fromkeys(p for p, _ in pl)); k = len([p for p in pages if p in A]); obs = diff(pl, A, rng)
    nl = np.array([diff(pl, set(rng.choice(pages, k, replace=False)), rng) for _ in range(nperm)]); mu = nl.mean()
    return dict(obs=float(obs), null_mean=float(mu), null_sd=float(nl.std()),
                p=float((1 + (np.abs(nl - mu) >= abs(obs - mu)).sum()) / (nperm + 1)))

def plant(pl, A, rng):
    t = Text(pl); w = t.w.copy(); pid = np.array([pl[i][0] in A for i in t.lid])
    sel = pid & np.isin(t.lid, np.nonzero(rng.random(t.lid.max() + 1) < 0.6)[0]); idx = np.nonzero(sel)[0]
    o = idx[np.lexsort((rng.random(len(idx)), t.page[idx]))]; w[idx] = t.w[o]
    inv = {}; [inv.setdefault(int(v), x) for v, x in zip(t.w, [x for _, l in pl for x in l])]
    it = iter(w.tolist()); return [(p, [inv[next(it)] for _ in l]) for p, l in pl]

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); R = dict(seed=SEED, NPERM=NPERM, alpha=ALPHA)
    nat = {'Italian_Dante': blocks(T.gutenberg(C + 'pg1012.txt')), 'Spanish_Cervantes': blocks(T.gutenberg(C + 'pg2000.txt'))}
    def window(pl, n):
        s = int(rng.integers(0, max(1, len(pl) - 4000))); return cap(list(pl[s:]), n)
    G = {}
    for name, ntok, frac in [('T1', 11300, 0.30), ('T2', 22500, 0.15)]:
        fp = pw = 0
        for g in range(NG):
            pl = window(nat[list(nat)[g % 2]], ntok); fp += perm2(pl, contiguous_A(pl, rng, frac), rng, NPERM_G)['p'] < ALPHA
        for g in range(NG):
            pl = window(nat[list(nat)[g % 2]], ntok); A = contiguous_A(pl, rng, frac)
            pw += perm2(plant(pl, A, rng), A, rng, NPERM_G)['p'] < ALPHA
        G[name] = dict(fpr=f'{fp}/{NG}', power=f'{pw}/{NG}', ok=bool(fp <= 2 and pw >= 14))
        print('gate', name, G[name], round(time.time() - t0, 1), flush=True)
    R['gates'] = G
    V = {}
    for k, f in [('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')]:
        pl, lang, sect = ivtff_pages_lang(f)
        h = [x for x in pl if sect.get(x[0]) == 'H' and lang.get(x[0]) in ('A', 'B')]
        b = [x for x in pl if lang.get(x[0]) == 'B']
        HA = {p for p, _ in h if lang[p] == 'A'}; HB = {p for p, _ in b if sect.get(p) == 'H'}
        r1 = perm2(h, HA, rng, NPERM); r1.update(E_HA=E([x for x in h if x[0] in HA], rng), E_HB=E([x for x in h if x[0] not in HA], rng))
        r2 = perm2(b, HB, rng, NPERM); r2.update(E_HB=E([x for x in b if x[0] in HB], rng), E_nonHB=E([x for x in b if x[0] not in HB], rng),
                                                 pages_nonHB=len({p for p, _ in b} - HB), tokens_nonHB=sum(len(l) for p, l in b if p not in HB))
        V[k] = dict(T1=r1, T2=r2); print(k, V[k], round(time.time() - t0, 1), flush=True)
    R['voynich'] = V; ver = {}
    for t in ('T1', 'T2'):
        s = [V[k][t]['p'] < ALPHA for k in V]
        ver[t] = 'NOT TESTABLE' if not G[t]['ok'] else ('DIFFERENCE' if all(s) else ('NO DIFFERENCE SHOWN' if not any(s) else 'SPLIT'))
    R['verdict'] = ver; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C048_results.json', 'w'), indent=1, default=float); print(ver, R['runtime_s'])

if __name__ == '__main__': main()
