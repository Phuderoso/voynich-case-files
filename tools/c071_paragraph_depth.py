#!/usr/bin/env python3
"""C071 (NEW FAMILY F-PARA, the paragraph as a unit): does the glyph make-up of a line's INTERIOR words depend on where
the line sits in its paragraph (top, second, last) compared with the paragraph's middle lines?
Paragraphs: paragraph-locus (P*) lines from a '<%>' line to the next '<$>' line on the same page, consecutive; kept only if
>= 4 lines and every line usable (no '<->', every word [a-z]+ after markup removal, C068 rules). Interior words = positions
3..n-2 (word 1, word 2 and the last two excluded, so F-LINE edge effects and C070's word-2 sh boost cannot enter).
Classes: T = top line, S = second line, M = lines 3..last-1, Lst = last line.  Glyph units: C003 units (ch sh cth ckh cph cfh one unit).
Statistic: JSD (bits) between pooled unit counts of class X and of M, X in {T, S, Lst}.
Null: within every paragraph the line order is permuted (class labels re-drawn), R = 1000 (gates R = 200); p = (1+#JSD*>=JSD)/(R+1).
Tests: {T, S, Lst} x {Currier A, Currier B} x {IT2a, ZL} = 12, Holm alpha 0.05.
Gates per test (20 pseudo replicates: lines already permuted within paragraph, seed 7171): FPR p<=0.05 in <=2/20; power:
plant - in class-X lines each interior word replaced with prob 0.08 by a word drawn uniformly from the 20 commonest interior
words of the subset -> p<=0.05 in >=16/20.  Verdict per (X, language): DIFFERENT if both transcriptions reject; PARTIAL if
one; NOT DETECTED if none (gates pass); NOT TESTABLE if a gate fails.  Descriptive: top 5 units by contribution (log-ratio
share difference) for each class; interior-word length mean by class.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, re, json, time
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T3

SEED, R, RG, NG, Q, ALPHA = 7171, 1000, 200, 20, 0.08, 0.05
FILES = (('IT2a', 'data/IT2a-n.txt'), ('ZL3b', 'data/ZL3b-n.txt'))
CLS = ('T', 'S', 'Lst')

def clean(t):
    t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
    t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
    return [w for w in re.split(r'[.,\s]+', t) if w]

def parse(path):
    meta, paras, cur, ok, lastpage = {}, [], None, True, None
    for raw in open(path, encoding='utf-8', errors='replace'):
        raw = raw.rstrip('\n')
        h = re.match(r'<(f\w+)>\s+<!(.*)>', raw)
        if h: meta[h.group(1)] = dict(re.findall(r'\$(\w)=(\S+)', h.group(2))); cur = None; continue
        m = re.match(r'<(f\w+)\.(\d+),([@+=*&~-])(\w+)>\s*(.*)', raw)
        if not m: continue
        page, loc, t = m.group(1), m.group(4), m.group(5)
        if not loc.startswith('P'): cur = None; continue
        if t.lstrip().startswith('<%>'): cur, ok = [], True
        if cur is None: continue
        ws = clean(t)
        if '<->' in t or not ws or not all(re.fullmatch(r'[a-z]+', w) for w in ws): ok = False
        cur.append(ws)
        if '<$>' in t:
            if ok and len(cur) >= 4: paras.append(dict(page=page, L=meta.get(page, {}).get('L'), lines=cur))
            cur = None
    return paras

def interior(ws): return [tuple(T3.units(w)) for w in ws[2:-2]]

def counts(words):
    c = Counter()
    for w in words: c.update(w)
    return c

def jsd(c1, c2):
    keys = sorted(set(c1) | set(c2)); a = np.array([c1[k] for k in keys], float); b = np.array([c2[k] for k in keys], float)
    if a.sum() == 0 or b.sum() == 0: return 0.0
    p, q = a / a.sum(), b / b.sum(); m = (p + q) / 2
    f = lambda x: np.sum(x[x > 0] * np.log2(x[x > 0] / m[x > 0]))
    return float(0.5 * f(p) + 0.5 * f(q))

def classes(n):
    return ['T', 'S'] + ['M'] * (n - 3) + ['Lst']

def build(paras):
    """per paragraph: list of per-line unit Counters (interior words)."""
    return [[counts(interior(ws)) for ws in p['lines']] for p in paras]

def stat(P, order=None):
    agg = {c: Counter() for c in ('T', 'S', 'M', 'Lst')}
    for i, lines in enumerate(P):
        lab = classes(len(lines)); idx = order[i] if order is not None else range(len(lines))
        for c, j in zip(lab, idx): agg[c].update(lines[j])
    return {x: jsd(agg[x], agg['M']) for x in CLS}

def perm(P, rng, r=None):
    r = r or R; obs = stat(P); null = {x: [] for x in CLS}
    for _ in range(r):
        s = stat(P, [rng.permutation(len(l)) for l in P])
        for x in CLS: null[x].append(s[x])
    return {x: (obs[x], float((1 + sum(v >= obs[x] for v in null[x])) / (r + 1))) for x in CLS}

def gate_job(a):
    k, lang, i = a; paras = [p for p in parse(dict(FILES)[k]) if p['L'] == lang]
    rng = np.random.default_rng(SEED * 1000 + i + (0 if k == 'IT2a' else 500) + (0 if lang == 'A' else 250))
    shuf = [dict(p, lines=[p['lines'][j] for j in rng.permutation(len(p['lines']))]) for p in paras]
    P0 = build(shuf); f = perm(P0, rng, RG)
    top = [w for w, _ in Counter(w for p in shuf for ws in p['lines'] for w in ws[2:-2]).most_common(20)]
    pw = {}
    for x in CLS:
        pl = []
        for p in shuf:
            lab = classes(len(p['lines'])); L = []
            for c, ws in zip(lab, p['lines']):
                if c == x: ws = ws[:2] + [top[rng.integers(20)] if rng.random() < Q else w for w in ws[2:-2]] + ws[-2:] if len(ws) > 4 else ws
                L.append(ws)
            pl.append(L)
        Pp = [[counts(interior(ws)) for ws in L] for L in pl]
        # test only class x (statistic for x)
        obs = stat(Pp)[x]; null = [stat(Pp, [rng.permutation(len(l)) for l in Pp])[x] for _ in range(RG)]
        pw[x] = float((1 + sum(v >= obs for v in null)) / (RG + 1))
    return k, lang, i, {x: (f[x][1], pw[x]) for x in CLS}

def main_job(a):
    k, lang = a; paras = [p for p in parse(dict(FILES)[k]) if p['L'] == lang]
    P = build(paras); res = perm(P, np.random.default_rng(SEED + (0 if k == 'IT2a' else 1) + (0 if lang == 'A' else 2)))
    agg = {c: Counter() for c in ('T', 'S', 'M', 'Lst')}; lens = {c: [] for c in agg}
    for p in paras:
        for c, ws in zip(classes(len(p['lines'])), p['lines']):
            iw = interior(ws); agg[c].update(counts(iw)); lens[c] += [len(w) for w in iw]
    desc = {}
    for x in CLS:
        tx, tm = sum(agg[x].values()), sum(agg['M'].values())
        d = sorted(((agg[x][u] / tx - agg['M'][u] / tm, u) for u in set(agg[x]) | set(agg['M'])), key=lambda z: -abs(z[0]))[:5]
        desc[x] = dict(top_units=[(u, round(v, 4)) for v, u in d], n_units=tx)
    return k, lang, dict(n_paras=len(paras), n_units_M=sum(agg['M'].values()), tests={x: dict(JSD=res[x][0], p=res[x][1]) for x in CLS},
                          desc=desc, mean_len={c: float(np.mean(v)) if v else None for c, v in lens.items()})

def main():
    t0 = time.time()
    with Pool(8) as pool:
        gj = pool.map_async(gate_job, [(k, l, i) for k, _ in FILES for l in ('A', 'B') for i in range(NG)], chunksize=1)
        M = {f'{k}_{l}': r for k, l, r in pool.map(main_job, [(k, l) for k, _ in FILES for l in ('A', 'B')])}
        print('main', json.dumps(M), flush=True)
        G = {}
        for k, l, i, d in gj.get():
            for x in CLS: g = G.setdefault(f'{k}_{l}_{x}', dict(fp=0, pw=0)); g['fp'] += d[x][0] <= ALPHA; g['pw'] += d[x][1] <= ALPHA
    for g in G.values(): g['pass'] = g['fp'] <= 2 and g['pw'] >= 16
    names = [f'{k}_{l}_{x}' for k, _ in FILES for l in ('A', 'B') for x in CLS if G[f'{k}_{l}_{x}']['pass']]
    ps = [M['_'.join(n.split('_')[:2])]['tests'][n.split('_')[2]]['p'] for n in names]
    o = np.argsort(ps); rej, stop = {}, False
    for r, i in enumerate(o):
        ok = (not stop) and ps[i] <= ALPHA / (len(ps) - r); rej[names[i]] = bool(ok); stop = stop or not ok
    ver = {}
    for l in ('A', 'B'):
        for x in CLS:
            if not all(G[f'{k}_{l}_{x}']['pass'] for k, _ in FILES): ver[f'{l}_{x}'] = 'NOT TESTABLE'; continue
            m = sum(rej.get(f'{k}_{l}_{x}', False) for k, _ in FILES); ver[f'{l}_{x}'] = 'DIFFERENT' if m == 2 else 'PARTIAL' if m == 1 else 'NOT DETECTED'
    out = dict(seed=SEED, R=R, Q=Q, main=M, gates=G, holm=rej, verdict=ver, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open('analysis/C071_results.json', 'w'), indent=1)
    for k in ('gates', 'holm', 'verdict', 'runtime_s'): print(k, json.dumps(out[k]))

if __name__ == '__main__':
    main()
