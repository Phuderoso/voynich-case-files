#!/usr/bin/env python3
"""C061 — NEW FAMILY F-LABEL, step 1: do the labels (IVTFF locus type L*) on a page occur in that page's own running text
(all non-label loci: paragraphs, circles, radii) more than in the text of other pages of the same illustration section?
Unit = distinct (page, label token) with >= 3 EVA units; pages need >= 20 running-text tokens.
M[i, j] = number of distinct labels of label-page i that occur (exactly) in the running text of page j.
H1: S = sum_i M[i, i]; null = 5000 permutations of label sets among label-pages of the SAME section ($I). One-sided p.
H2 (page-specific vs local drift): per label-page, own hit share minus mean hit share on its bound neighbours (previous/next
page in file order within the same section with running text); statistic = mean over pages; null = 5000 random sign flips.
alpha 0.025 each (ZL 3b primary); IT2a = replication, descriptive. Edit-distance-1 hits reported descriptively.
Gates (ZL page structure, 200 reps each): FPR — fake labels drawn uniformly from the distinct words (>= 3 units) of the section's running text excluding the own page,
same counts per page; power — same but 25% of label-pages get one label drawn from their own running text.
Bars: FPR <= 0.05 at alpha 0.025 (+binomial slack: <= 0.05), power >= 0.80. Seed 6161.
Pre-registered in case-file/C061-labels-in-own-text.md.   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T

SEED, NPERM, NREP, ALPHA, PFRAC, MINTXT = 6161, 5000, 200, 0.025, 0.25, 20

def clean(t):
    t = t.replace('<->', '.'); t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
    t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
    return [w for w in re.split(r'[.,\s]+', t) if w and re.fullmatch(r'[a-z]+', w)]

def parse(path):
    sect, order, txt, lab = {}, [], {}, {}
    for line in open(path, encoding='utf-8', errors='replace'):
        h = re.match(r'<(f\w+)>\s+<!(.*)>', line)
        if h:
            m = re.search(r'\$I=(\w)', h.group(2)); sect[h.group(1)] = m.group(1) if m else None; order.append(h.group(1)); continue
        m = re.match(r'<(f\w+)\.\d+,([@+=*&~-])(\w+)>\s*(.*)', line.rstrip('\n'))
        if not m: continue
        ws = clean(m.group(4)); p = m.group(1)
        if m.group(3).startswith('L'): lab.setdefault(p, set()).update(w for w in ws if len(T.units(w)) >= 3)
        else: txt.setdefault(p, []).extend(ws)
    tp = [p for p in order if len(txt.get(p, [])) >= MINTXT]
    lp = [p for p in tp if lab.get(p)]
    return sect, tp, lp, txt, lab

def nbr1(w, voc):
    for i in range(len(w) + 1):
        for c in 'abcdefghiklmnopqrstvxyz':
            if w[:i] + c + w[i:] in voc or (i < len(w) and w[:i] + c + w[i + 1:] in voc and c != w[i]): return True
        if i < len(w) and w[:i] + w[i + 1:] in voc: return True
    return False

def matrices(labsets, lp, tp, txt, edit=False):
    vocs = {p: set(txt[p]) for p in tp}; M = np.zeros((len(lp), len(tp)))
    for i, p in enumerate(lp):
        for j, q in enumerate(tp):
            M[i, j] = sum((w in vocs[q]) or (edit and nbr1(w, vocs[q])) for w in labsets[p])
    return M

def tests(M, lp, tp, sect, rng):
    col = {p: j for j, p in enumerate(tp)}; own = np.array([M[i, col[p]] for i, p in enumerate(lp)]); S = own.sum()
    groups = {}
    for i, p in enumerate(lp): groups.setdefault(sect[p], []).append(i)
    null = np.zeros(NPERM)
    for g in groups.values():
        cols = np.array([col[lp[i]] for i in g]); sub = M[np.ix_(g, cols)]
        for k in range(NPERM): null[k] += sub[np.arange(len(g)), rng.permutation(len(g))].sum()
    p1 = (1 + (null >= S).sum()) / (NPERM + 1)
    d = []
    for i, p in enumerate(lp):
        sec = [q for q in tp if sect[q] == sect[p]]; k = sec.index(p); nb = [sec[x] for x in (k - 1, k + 1) if 0 <= x < len(sec)]
        if nb: d.append((own[i] - np.mean([M[i, col[q]] for q in nb])) / len(lp_labels[p]))
    d = np.array(d); D = d.mean(); fl = np.array([(d * rng.choice([-1, 1], len(d))).mean() for _ in range(NPERM)])
    p2 = (1 + (fl >= D).sum()) / (NPERM + 1)
    return dict(S=float(S), null_mean=float(null.mean()), p_H1=float(p1), D=float(D), p_H2=float(p2), n_labelpages=len(lp),
                n_labels=int(sum(len(lp_labels[p]) for p in lp)), own_hit_share=float(S / sum(len(lp_labels[p]) for p in lp)))

def fake(lp, tp, txt, lab, sect, rng, plant):
    out = {}
    for p in lp:
        pool = sorted({w for q in tp if sect[q] == sect[p] and q != p for w in txt[q] if len(T.units(w)) >= 3})
        n = len(lab[p]); s = set(rng.choice(pool, n, replace=False)) if len(pool) >= n else set(pool)
        if plant and rng.random() < PFRAC:
            ownp = [w for w in txt[p] if len(T.units(w)) >= 3]
            if ownp: s = set(list(s)[1:]) | {ownp[int(rng.integers(len(ownp)))]}
        out[p] = s
    return out

lp_labels = {}
def main():
    global lp_labels
    t0 = time.time(); rng = np.random.default_rng(SEED); R = dict(seed=SEED)
    sect, tp, lp, txt, lab = parse('data/ZL3b-n.txt')
    g = {}
    for mode in ('fpr', 'power'):
        rej1 = rej2 = 0
        for r in range(NREP):
            lp_labels = fake(lp, tp, txt, lab, sect, rng, mode == 'power'); M = matrices(lp_labels, lp, tp, txt)
            t = tests(M, lp, tp, sect, rng); rej1 += t['p_H1'] <= ALPHA; rej2 += t['p_H2'] <= ALPHA
        g[mode] = dict(H1=rej1 / NREP, H2=rej2 / NREP); print(mode, g[mode], round(time.time() - t0, 1), flush=True)
    g['ok_H1'] = bool(g['fpr']['H1'] <= 0.05 and g['power']['H1'] >= 0.8); g['ok_H2'] = bool(g['fpr']['H2'] <= 0.05 and g['power']['H2'] >= 0.8)
    R['gates'] = g
    for name, f in (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt')):
        sect, tp, lp, txt, lab = parse(f); lp_labels = lab
        M = matrices(lab, lp, tp, txt); t = tests(M, lp, tp, sect, rng)
        Me = matrices(lab, lp, tp, txt, edit=True); te = tests(Me, lp, tp, sect, rng)
        t['edit1'] = {k: te[k] for k in ('S', 'null_mean', 'p_H1', 'D', 'p_H2', 'own_hit_share')}
        t['sections'] = {s: sum(sect[p] == s for p in lp) for s in set(sect[p] for p in lp)}
        hits = sorted({(p, w) for p in lp for w in lab[p] if w in set(txt[p])}); t['own_hits'] = [f'{p}:{w}' for p, w in hits]
        R[name] = t; print(name, {k: v for k, v in t.items() if k != 'own_hits'}, round(time.time() - t0, 1), flush=True)
    z = R['ZL3b']; V = {}
    V['H1'] = 'NOT TESTABLE' if not g['ok_H1'] else ('EXCESS' if z['p_H1'] <= ALPHA else 'NO EXCESS')
    V['H2'] = 'NOT TESTABLE' if not g['ok_H2'] else ('PAGE-SPECIFIC' if z['p_H2'] <= ALPHA else 'NOT PAGE-SPECIFIC')
    R['verdict'] = V; R['runtime_s'] = round(time.time() - t0, 1)
    json.dump(R, open('analysis/C061_results.json', 'w'), indent=1, default=float); print(V, R['runtime_s'])

if __name__ == '__main__': main()
