#!/usr/bin/env python3
"""C068 (new family F-VERT, two-dimensional page layout): are one-glyph near-copies between a line and the line directly
above placed at the SAME horizontal position more often than near-copies between the same line and lines from other pages?
Unit of analysis: ordered line pairs (upper U, lower L) of paragraph text (P loci), consecutive lines of the same page and
paragraph (L marker '+' or '='); lines with drawing breaks '<->' or non [a-z] words are skipped (positions would be wrong).
Horizontal position proxy: word centre in EVA characters (start offset, 1 char per separator, + len/2) from the
transliteration (no scans). Words: interior only (first and last word of each line excluded), >= 3 glyph units.
Candidate pair: (u in U, l in L) with unit edit distance <= 1. Aligned: |centre_u - centre_l| <= 3 chars (Dc) or
|centre_u/len_U - centre_l/len_L| <= 0.05 (Df, fractional, secondary).
For each lower line i: (a0, n0) with its real upper line and (a_k, n_k), k = 1..K = 5, with upper lines drawn from OTHER pages
of the same Currier language and section ($L, $I). Statistic: Delta = sum a0 / sum n0 - sum_k a_k / sum_k n_k.
Null (swap test, controls line length, within-line position trends and page vocabulary of L): for every lower line the
'real' slot is re-drawn uniformly among its K + 1 uppers; R = 2000; one-sided p = (1 + #Delta* >= Delta)/(R + 1).
Gates (per transcription and statistic), from the manuscript's own lines:
 FPR: 20 pseudo replicates where the real upper is replaced by a random other-page upper -> p <= 0.05 in <= 2/20;
 power: same pseudo replicates with a planted aligned copy: each eligible interior lower word replaced, with probability
  Q = 0.02 (the ~2% near-copy rate estimated by voynich-text-examination), by a one-unit substitution of the pseudo-upper's interior word with the nearest centre -> p <= 0.05 in >= 16/20.
Holm over 4 tests (Dc, Df x ZL, IT2a) among gated tests at alpha 0.05.
Decision (on Dc, primary): ALIGNED-EXCESS if both transcriptions reject; PARTIAL if one; NOT DETECTED if none (gates pass);
NOT TESTABLE if a gate fails.  Descriptive (no p claims): 9 natural texts wrapped into 55-char lines and 29-line pages;
Timm-Schinner generator, 3 settings x 20 runs (first 20 of 30 fresh seeds with >= 1,200 lines): default (sourceChooser=page,
same_position_probability=28) seeds 9101-9130, spp=0 seeds 9201-9230, sourceChooser=position seeds 9301-9330; range rule
INSIDE / OUTSIDE-ABOVE / OUTSIDE-BELOW per setting. Prior work: voynich-text-examination.netlify.app (word boxes on 33 pages:
excess similarity to the line above is not tied to the physically aligned word) and Timm 2014 (arXiv 1407.6639).
Seed 6868. Pre-registered in case-file/C068-vertical-alignment.md. Run: timeout 600 python3 tools/c068_vertical_alignment.py
Design-only run (gates on ZL with the design seed, no manuscript statistic): python3 tools/c068_vertical_alignment.py design
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import sys, os, re, json, time
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
from c004_generator_sweep import generate

SEED, DESIGN_SEED, K, R, NG, Q, TOL_C, TOL_F, ALPHA = 6868, 6869, 5, 2000, 20, 0.02, 3.0, 0.05, 0.05
FILES = (('ZL3b', 'data/ZL3b-n.txt'), ('IT2a', 'data/IT2a-n.txt'))
GEN = {'default': ({}, range(9101, 9131)), 'spp0': ({'method.sourceChooser.same_position_probability': 0}, range(9201, 9231)),
       'position': ({'method.sourceChooser': 'position'}, range(9301, 9331))}
GLINES, NGEN = 1500, 20

def positions(words):
    c, s = [], 0
    for w in words: c.append(s + len(w) / 2); s += len(w) + 1
    return np.array(c), s - 1

class Line:
    __slots__ = ('page', 'grp', 'words', 'units', 'c', 'len')
    def __init__(self, page, grp, words, unitf):
        self.page, self.grp, self.words = page, grp, list(words)
        self.units = [tuple(unitf(w)) for w in self.words]; self.c, self.len = positions(self.words)

def parse_voynich(path):
    meta, lines, pairs, prev = {}, [], [], None
    for raw in open(path, encoding='utf-8', errors='replace'):
        raw = raw.rstrip('\n')
        h = re.match(r'<(f\w+)>\s+<!(.*)>', raw)
        if h:
            d = dict(re.findall(r'\$(\w)=(\S+)', h.group(2))); meta[h.group(1)] = (d.get('L'), d.get('I')); prev = None; continue
        m = re.match(r'<(f\w+)\.(\d+),([@+=*&~-])(\w+)>\s*(.*)', raw)
        if not m: continue
        page, mk, loc, t = m.group(1), m.group(3), m.group(4), m.group(5)
        if not loc.startswith('P'): prev = None; continue
        ok = '<->' not in t
        t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        ws = [w for w in re.split(r'[.,\s]+', t) if w]
        ok = ok and len(ws) >= 3 and all(re.fullmatch(r'[a-z]+', w) for w in ws)
        if not ok: prev = None; continue
        L, I = meta.get(page, (None, None))
        lines.append(Line(page, f'{L}{I}', ws, T.units)); cur = len(lines) - 1
        if prev is not None and mk in '+=' and lines[prev].page == page: pairs.append((prev, cur))
        prev = cur
    return lines, pairs

def wrap_text(lines_in, unitf, maxlen=55, per_page=29, maxlines=None):
    ws = [w for l in lines_in for w in l]; out, cur, n = [], [], 0
    for w in ws:
        if cur and n + 1 + len(w) > maxlen: out.append(cur); cur, n = [], 0
        n = len(w) if not cur else n + 1 + len(w); cur.append(w)
    if cur: out.append(cur)
    out = [l for l in out if len(l) >= 3]
    if maxlines: out = out[:maxlines]
    return block_text(out, unitf, per_page)

def block_text(rows, unitf, per_page=29):
    lines, pairs = [], []
    for i, r in enumerate(rows):
        lines.append(Line(f'p{i // per_page}', 'g', r, unitf))
        if i % per_page and i > 0: pairs.append((i - 1, i))
    return lines, pairs

_memo = {}
def ed1(a, b):
    if a == b: return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1: return False
    key = (a, b) if a < b else (b, a)
    r = _memo.get(key)
    if r is not None: return r
    if la == lb: r = sum(x != y for x, y in zip(a, b)) == 1
    else:
        if la > lb: a, b = b, a
        i = 0
        while i < len(a) and a[i] == b[i]: i += 1
        r = a[i:] == b[i + 1:]
    _memo[key] = r; return r

def counts(U, L):
    ac = af = n = 0
    iu = [j for j in range(1, len(U.units) - 1) if len(U.units[j]) >= 3]
    il = [j for j in range(1, len(L.units) - 1) if len(L.units[j]) >= 3]
    for j in il:
        for k in iu:
            if ed1(L.units[j], U.units[k]):
                n += 1
                ac += abs(U.c[k] - L.c[j]) <= TOL_C
                af += abs(U.c[k] / U.len - L.c[j] / L.len) <= TOL_F
    return ac, af, n

def pools(lines, pairs):
    P = {}
    for u, _ in pairs: P.setdefault(lines[u].grp, []).append(u)
    return {g: np.array(sorted(set(v))) for g, v in P.items()}

def draw_other(lines, pool, page, rng, m):
    out = []
    while len(out) < m:
        c = int(pool[rng.integers(len(pool))])
        if lines[c].page != page and c not in out: out.append(c)
    return out

def table(lines, pairs, rng, pseudo=False, plant=0.0, alphabet=None):
    """rows: per lower line, arrays over K+1 slots (slot 0 = 'real' upper)."""
    P = pools(lines, pairs); A_c, A_f, N = [], [], []
    for u, l in pairs:
        L = lines[l]; pool = P[L.grp]
        if len({lines[x].page for x in pool}) < K + 3: continue
        oth = draw_other(lines, pool, L.page, rng, K + (1 if pseudo else 0))
        real = oth.pop() if pseudo else u
        if plant > 0: L = planted(lines[real], L, rng, plant, alphabet)
        r = [counts(lines[x], L) for x in [real] + oth]
        A_c.append([x[0] for x in r]); A_f.append([x[1] for x in r]); N.append([x[2] for x in r])
    return np.array(A_c), np.array(A_f), np.array(N)

def planted(U, L, rng, q, alphabet):
    iu = [k for k in range(1, len(U.units) - 1) if len(U.units[k]) >= 3]
    if not iu: return L
    words = list(L.words); units = list(L.units); changed = False
    for j in range(1, len(units) - 1):
        if len(units[j]) >= 3 and rng.random() < q:
            k = min(iu, key=lambda k: abs(U.c[k] - L.c[j])); src = list(U.units[k]); p = int(rng.integers(len(src)))
            src[p] = alphabet[int(rng.integers(len(alphabet)))]
            while src[p] == U.units[k][p]: src[p] = alphabet[int(rng.integers(len(alphabet)))]
            units[j] = tuple(src); words[j] = ''.join(src); changed = True
    if not changed: return L
    M = Line.__new__(Line); M.page, M.grp, M.words, M.units = L.page, L.grp, words, units; M.c, M.len = positions(words)
    return M

def swap_test(A, N, rng):
    def d(a, n):
        a0, n0 = a[:, 0].sum(), n[:, 0].sum(); ar, nr = a[:, 1:].sum(), n[:, 1:].sum()
        return a0 / max(n0, 1) - ar / max(nr, 1)
    obs = d(A, N); ta, tn = A.sum(1), N.sum(1); m = len(A); null = np.empty(R)
    for r in range(R):
        j = rng.integers(K + 1, size=m); a0 = A[np.arange(m), j]; n0 = N[np.arange(m), j]
        null[r] = a0.sum() / max(n0.sum(), 1) - (ta - a0).sum() / max((tn - n0).sum(), 1)
    return dict(delta=float(obs), p=float((1 + (null >= obs).sum()) / (R + 1)), null_mean=float(null.mean()),
                share_real=float(A[:, 0].sum() / max(N[:, 0].sum(), 1)), share_other=float(A[:, 1:].sum() / max(N[:, 1:].sum(), 1)),
                n_real=int(N[:, 0].sum()), n_other_per_slot=float(N[:, 1:].sum() / K), lines=int(m))

def both(lines, pairs, rng, **kw):
    Ac, Af, N = table(lines, pairs, rng, **kw)
    return dict(Dc=swap_test(Ac, N, rng), Df=swap_test(Af, N, rng))

def alphabet_of(lines): return sorted({u for L in lines for w in L.units for u in w})

def gate_job(a):
    key, path, i, seed = a; lines, pairs = parse_voynich(path); al = alphabet_of(lines)
    rng = np.random.default_rng(seed * 1000 + i)
    f = both(lines, pairs, rng, pseudo=True); p = both(lines, pairs, rng, pseudo=True, plant=Q, alphabet=al)
    return key, i, {s: (f[s]['p'], p[s]['p'], f[s]['delta'], p[s]['delta']) for s in ('Dc', 'Df')}

def gen_job(a):
    name, s = a; cfg = dict(GEN[name][0]); cfg['text.lines_to_create'] = GLINES
    Lg = generate(cfg, s)
    if not Lg or len(Lg) < 1200: return name, s, None
    lines, pairs = block_text([l for l in Lg if len(l) >= 3][:1200], T.units)
    return name, s, both(lines, pairs, np.random.default_rng(SEED * 10 + s))

def nat_job(a):
    k, rows, unitf = a; lines, pairs = wrap_text(rows, unitf, maxlines=3000)
    return k, both(lines, pairs, np.random.default_rng(SEED + len(k)))

def cls(v, ref):
    lo, hi = min(ref), max(ref); return 'INSIDE' if lo <= v <= hi else ('OUTSIDE-ABOVE' if v > hi else 'OUTSIDE-BELOW')

def holm(ps):
    o = np.argsort(ps); m = len(ps); rej = [False] * m
    for r, i in enumerate(o):
        if ps[i] <= ALPHA / (m - r): rej[i] = True
        else: break
    return rej

def main():
    t0 = time.time(); design = len(sys.argv) > 1 and sys.argv[1] == 'design'
    with Pool(8) as pool:
        if design:
            res = pool.map(gate_job, [('ZL3b', 'data/ZL3b-n.txt', i, DESIGN_SEED) for i in range(NG)])
            for s in ('Dc', 'Df'):
                fp = sum(r[2][s][0] <= ALPHA for r in res); pw = sum(r[2][s][1] <= ALPHA for r in res)
                print('DESIGN', s, 'FPR', fp, '/20 power', pw, '/20', 'mean planted delta', round(np.mean([r[2][s][3] for r in res]), 4))
            print('time', round(time.time() - t0, 1)); return
        out = dict(seed=SEED, K=K, R=R, Q=Q, TOL_C=TOL_C, TOL_F=TOL_F)
        gj = pool.map_async(gate_job, [(k, f, i, SEED) for k, f in FILES for i in range(NG)])
        jobs = [(n, s) for n in GEN for s in GEN[n][1]]
        gn = pool.map_async(gen_job, jobs)
        import c051_context_spelling_ab as B
        nat = B.nat_texts(); nj = pool.map_async(nat_job, [(k, v, list) for k, v in nat.items()])
        V = {}
        for k, f in FILES:
            lines, pairs = parse_voynich(f); V[k] = both(lines, pairs, np.random.default_rng(SEED))
            V[k]['n_lines'] = len(lines); V[k]['n_pairs'] = len(pairs)
            print(k, json.dumps(V[k]), flush=True)
        gates = {}
        for key, i, d in gj.get():
            for s in d: g = gates.setdefault(f'{key}_{s}', dict(fp=0, pw=0, fp_delta=[], pw_delta=[])); g['fp'] += d[s][0] <= ALPHA; g['pw'] += d[s][1] <= ALPHA; g['fp_delta'].append(d[s][2]); g['pw_delta'].append(d[s][3])
        for g in gates.values(): g['pass'] = g['fp'] <= 2 and g['pw'] >= 16; g['fp_delta'] = float(np.mean(g['fp_delta'])); g['pw_delta'] = float(np.mean(g['pw_delta']))
        print('gates', json.dumps(gates), flush=True)
        tests = [(k, s) for k, _ in FILES for s in ('Dc', 'Df') if gates[f'{k}_{s}']['pass']]
        rej = holm([V[k][s]['p'] for k, s in tests]); H = {f'{k}_{s}': bool(r) for (k, s), r in zip(tests, rej)}
        gres = {}
        for name, s, r in gn.get():
            if r is not None and len(gres.setdefault(name, {})) < NGEN: gres[name][s] = r
        natr = dict(nj.get())
    G = {}
    for name, runs in gres.items():
        G[name] = dict(n=len(runs), seeds=sorted(runs))
        for s in ('Dc', 'Df'):
            ref = [r[s]['delta'] for r in runs.values()]
            G[name][s] = dict(min=min(ref), median=float(np.median(ref)), max=max(ref), n_sig=sum(r[s]['p'] <= ALPHA for r in runs.values()),
                              cls={k: cls(V[k][s]['delta'], ref) for k, _ in FILES})
    N_ = {k: {s: dict(delta=v[s]['delta'], p=v[s]['p']) for s in ('Dc', 'Df')} for k, v in natr.items()}
    def verdict(s):
        if not all(gates[f'{k}_{s}']['pass'] for k, _ in FILES): return 'NOT TESTABLE'
        n = sum(H.get(f'{k}_{s}', False) for k, _ in FILES)
        return 'ALIGNED-EXCESS' if n == 2 else 'PARTIAL' if n == 1 else 'NOT DETECTED'
    out.update(voynich=V, gates=gates, holm=H, generator=G, natural=N_, verdict={s: verdict(s) for s in ('Dc', 'Df')}, runtime_s=round(time.time() - t0, 1))
    os.makedirs('analysis', exist_ok=True); json.dump(out, open('analysis/C068_results.json', 'w'), indent=1)
    print('generator', json.dumps(G)); print('natural', json.dumps(N_)); print('holm', H); print('verdict', out['verdict']); print('time', out['runtime_s'])

if __name__ == '__main__':
    main()
