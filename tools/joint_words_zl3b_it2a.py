#!/usr/bin/env python3
"""Joint ZL3b vs IT2a word-division audit (audits/joint/zl3b-it2a-words/CRITERION.md v2 is the frozen rule).
Descriptive only: aligns the two transcriptions line by line and token by token and counts how they divide / read the same glyph strings.
Usage:
  python3 tools/joint_words_zl3b_it2a.py control OUTDIR      planted control (seed 11848): builds a ZL3b copy with known splits/merges/swaps, aligns, compares to truth
  python3 tools/joint_words_zl3b_it2a.py real OUTDIR         real count on data/ZL3b-n.txt and data/IT2a-n.txt, base + all registered sensitivities
Pure standard library + numpy; no randomness in 'real'.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import re, sys, os, json, math, hashlib, functools
from collections import Counter, defaultdict
import numpy as np

CONTROL_SEED = 11848
LOC = re.compile(r'^<(f\w+)\.(\d+),([@+=*&~/!-])(\w+)>\s*(.*)$')
HDR = re.compile(r'<(f\w+)>\s+<!(.*)>')
CORE = set('acdefhiklmnopqrsty')          # glyph map 'rare': every other glyph except '?' -> '#'
MOVES = ((1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 2), (1, 0), (0, 1))     # CRITERION s4 list order = tie-break order

class Cfg:
    def __init__(self, name='base', arrow='sep', comma='sep', alt='first', gmap=None, wild=False, lt=1/3, tt=1/2, fallback=True):
        self.name, self.arrow, self.comma, self.alt, self.gmap, self.wild, self.lt, self.tt, self.fallback = name, arrow, comma, alt, gmap, wild, lt, tt, fallback

def wilson(k, n, z=1.96):
    if n == 0: return (None, None)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d, 5), round((c + h) / d, 5))
def share(k, n): return dict(k=int(k), n=int(n), share=(k / n if n else None), wilson=wilson(k, n))

# ------------------------------------------------------------------ parsing
def headers(path):
    meta = {}
    for raw in open(path, encoding='utf-8', errors='replace'):
        h = HDR.match(raw.rstrip('\n'))
        if h: meta[h.group(1)] = dict(re.findall(r'\$(\w)=(\S+)', h.group(2)))
    return meta

def norm(t, cfg):
    t = t.replace('<->', ' ' if cfg.arrow == 'sep' else '')
    t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
    t = re.sub(r'\[([^:\]]*):([^\]]*)\]', r'\1' if cfg.alt == 'first' else r'\2', t)
    t = t.replace('{', '').replace('}', '').replace("'", '')
    if cfg.comma == 'none': t = t.replace(',', '')
    parts = re.split(r'([.,\s]+)', t)
    toks, seps, cur = [], [], None
    for i, p in enumerate(parts):
        if i % 2 == 0:
            if p:
                if cur is not None: seps.append(cur)
                toks.append(p); cur = None
        else:
            if toks: cur = ',' if set(p) == {','} else '.'
    return toks, seps

def retained_c070(t):
    """C070 / C123 retention rule, first reading, independent of cfg."""
    if '<->' in t: return False
    tt = re.sub(r'<[^>]*>', '', t); tt = re.sub(r'@\d+;', '', tt)
    tt = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', tt).replace('{', '').replace('}', '').replace("'", '')
    ws = [w for w in re.split(r'[.,\s]+', tt) if w]
    return len(ws) >= 5 and all(re.fullmatch(r'[a-z]+', w) for w in ws)

def gm(s, cfg):
    return ''.join('#' if (c not in CORE and c != '?') else c for c in s) if cfg.gmap == 'rare' else s

def load(path, cfg):
    meta = headers(path); out = []; bad = []
    for ix, raw in enumerate(open(path, encoding='utf-8', errors='replace')):
        raw = raw.rstrip('\n'); m = LOC.match(raw)
        if not m:
            if raw.startswith('<f') and not HDR.match(raw): bad.append(raw[:60])
            continue
        folio, num, code, t = m.group(1), int(m.group(2)), m.group(4), m.group(5)
        toks, seps = norm(t, cfg); toks = [gm(x, cfg) for x in toks]
        out.append(dict(ix=len(out), folio=folio, num=num, typ=code[0], code=code, toks=toks, seps=seps, G=''.join(toks),
                        ret=retained_c070(t), L=meta.get(folio, {}).get('L')))
    return out, bad

# ------------------------------------------------------------------ Levenshtein
@functools.lru_cache(maxsize=None)
def lev(a, b, wild=False):
    if a == b: return 0
    if not a: return len(b)
    if not b: return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            s = 0 if (ca == cb or (wild and (ca == '?' or cb == '?'))) else 1
            cur.append(min(prev[j - 1] + s, prev[j] + 1, cur[j - 1] + 1))
        prev = cur
    return prev[-1]

def lev_cols(a, b, wild=False):
    """alignment columns (traceback preference: diagonal, then delete-from-a, then insert-from-b); returns colA, colB (column index of every glyph)."""
    n, m = len(a), len(b); D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): D[i][0] = i
    for j in range(m + 1): D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            s = 0 if (a[i - 1] == b[j - 1] or (wild and (a[i - 1] == '?' or b[j - 1] == '?'))) else 1
            D[i][j] = min(D[i - 1][j - 1] + s, D[i - 1][j] + 1, D[i][j - 1] + 1)
    i, j, cols = n, m, []
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            s = 0 if (a[i - 1] == b[j - 1] or (wild and (a[i - 1] == '?' or b[j - 1] == '?'))) else 1
            if D[i][j] == D[i - 1][j - 1] + s: cols.append((i - 1, j - 1)); i -= 1; j -= 1; continue
        if i > 0 and D[i][j] == D[i - 1][j] + 1: cols.append((i - 1, None)); i -= 1; continue
        cols.append((None, j - 1)); j -= 1
    cols.reverse(); cA, cB = [None] * n, [None] * m
    for c, (x, y) in enumerate(cols):
        if x is not None: cA[x] = c
        if y is not None: cB[y] = c
    return cA, cB

# ------------------------------------------------------------------ level A: keys, fallback
def line_ok(a, b, cfg):
    return lev(a['G'], b['G'], cfg.wild) <= cfg.lt * max(len(a['G']), len(b['G']), 1)

def pair_lines(A, B, cfg):
    """stage 1: key = (folio, line number, locus type letter). With fallback on, a key pair whose lines fail the line threshold is released
    (a numbering shift shows up as 'unalignable'), then every unpaired line is aligned inside its folio by an order-preserving DP."""
    kb = {(l['folio'], l['num'], l['typ']): l for l in B}; pairs, used, raw_key, released = [], set(), 0, 0
    for a in A:
        b = kb.get((a['folio'], a['num'], a['typ']))
        if b is None: continue
        raw_key += 1
        if cfg.fallback and not line_ok(a, b, cfg): released += 1; continue
        pairs.append((a, b, 'key')); used.add(b['ix'])
    paired_a = {p[0]['ix'] for p in pairs}; nkey = len(pairs); nfb = 0
    if cfg.fallback:
        ua, ub = defaultdict(list), defaultdict(list)
        for a in A:
            if a['ix'] not in paired_a: ua[a['folio']].append(a)
        for b in B:
            if b['ix'] not in used: ub[b['folio']].append(b)
        for f in ua:
            if f not in ub: continue
            X, Y = ua[f], ub[f]; n, m = len(X), len(Y)
            ok = lambda x, y: x['typ'] == y['typ'] and line_ok(x, y, cfg)
            F = [[(0, 0)] * (m + 1) for _ in range(n + 1)]
            for i in range(n - 1, -1, -1):
                for j in range(m - 1, -1, -1):
                    best = min(F[i + 1][j], F[i][j + 1])
                    if ok(X[i], Y[j]):
                        c = lev(X[i]['G'], Y[j]['G'], cfg.wild); v = (F[i + 1][j + 1][0] - 1, F[i + 1][j + 1][1] + c)
                        best = min(best, v)
                    F[i][j] = best
            i = j = 0
            while i < n and j < m:
                if ok(X[i], Y[j]):
                    c = lev(X[i]['G'], Y[j]['G'], cfg.wild)
                    if F[i][j] == (F[i + 1][j + 1][0] - 1, F[i + 1][j + 1][1] + c): pairs.append((X[i], Y[j], 'fallback')); i += 1; j += 1; nfb += 1; continue
                if F[i][j] == F[i + 1][j]: i += 1
                else: j += 1
    return pairs, nkey, nfb, raw_key, released

# ------------------------------------------------------------------ level B / C
def line_class(a, b, cfg):
    if a['toks'] == b['toks']: return 'identical'
    if a['G'] == b['G']: return 'division_only'
    L = max(len(a['G']), len(b['G']))
    return 'glyph_different' if lev(a['G'], b['G'], cfg.wild) <= cfg.lt * L else 'unalignable_line'

def token_dp(X, Y, wild):
    """group DP, suffix-optimal with value (cost, -n11, n_gap); forward reconstruction picks the lowest MOVES index among optimal moves (= lexicographically smallest optimal move sequence)."""
    n, m = len(X), len(Y); INF = (10 ** 9, 0, 0); F = [[INF] * (m + 1) for _ in range(n + 1)]; F[n][m] = (0, 0, 0)
    def step(i, j, mv):
        di, dj = mv
        if i + di > n or j + dj > m: return None
        s = F[i + di][j + dj]
        if s == INF: return None
        if mv == (1, 0): c, g, e = len(X[i]), 1, 0
        elif mv == (0, 1): c, g, e = len(Y[j]), 1, 0
        else: c, g, e = lev(''.join(X[i:i + di]), ''.join(Y[j:j + dj]), wild), 0, (1 if mv == (1, 1) else 0)
        return (s[0] + c, s[1] - e, s[2] + g)
    for i in range(n, -1, -1):
        for j in range(m, -1, -1):
            if i == n and j == m: continue
            best = INF
            for mv in MOVES:
                v = step(i, j, mv)
                if v is not None and v < best: best = v
            F[i][j] = best
    i = j = 0; out = []
    while i < n or j < m:
        for mv in MOVES:
            v = step(i, j, mv)
            if v is not None and v == F[i][j]: out.append((i, j, mv)); i += mv[0]; j += mv[1]; break
    return out

def classify_groups(a, b, cfg):
    X, Y = a['toks'], b['toks']; res = []
    for i, j, (di, dj) in token_dp(X, Y, cfg.wild):
        sx, sy = ''.join(X[i:i + di]), ''.join(Y[j:j + dj])
        if di == 0 or dj == 0: res.append(dict(cls='unalignable', di=di, dj=dj, i=i, j=j)); continue
        c = lev(sx, sy, cfg.wild)
        if c == 0:
            if (di, dj) == (1, 1) and X[i] == Y[j]: res.append(dict(cls='identical', di=di, dj=dj, i=i, j=j))
            else: res.append(dict(cls='split_merge', di=di, dj=dj, i=i, j=j))
        elif c <= cfg.tt * max(len(sx), len(sy)): res.append(dict(cls='glyph_different', di=di, dj=dj, i=i, j=j, cost=c, div=(di, dj) != (1, 1) and (di != dj or di == 2)))
        else: res.append(dict(cls='unalignable', di=di, dj=dj, i=i, j=j, cost=c))
    return res

def boundary_alignment(a, b, cfg):
    """boundaries of a / b in the glyph-alignment column space; returns (set_a, set_b) of column indices of token-end glyphs."""
    Ga, Gb = a['G'], b['G']
    if Ga == Gb or not Ga or not Gb: cA, cB = list(range(len(Ga))), list(range(len(Gb)))
    else: cA, cB = lev_cols(Ga, Gb, cfg.wild)
    def ends(toks, c):
        p, out = 0, []
        for t in toks: p += len(t); out.append(c[p - 1])
        return out
    return ends(a['toks'], cA), ends(b['toks'], cB)

# ------------------------------------------------------------------ the count
def cb_geometry(L):
    """CB stratum as C123/C124: retained lines with page Currier L == 'B', per page in file order; block of 4 from offset 0; returns {ix: (page, idx, class)}."""
    pages = defaultdict(list)
    for l in L:
        if l['ret'] and l['L'] == 'B': pages[l['folio']].append(l['ix'])
    geo = {}
    for f, ixs in pages.items():
        nb = len(ixs) // 4
        for k, ix in enumerate(ixs):
            geo[ix] = (f, k, ('tail' if k >= 4 * nb else ('first' if k % 4 == 0 else ('last' if k % 4 == 3 else 'interior'))))
    return geo

def count(A, B, cfg, badA=(), badB=()):
    pairs, nkey, nfb, raw_key, released = pair_lines(A, B, cfg); R = dict(config=cfg.name)
    R['parse_unmatched_lines'] = dict(ZL3b=list(badA), IT2a=list(badB))
    R['A'] = dict(loci_ZL3b=len(A), loci_IT2a=len(B), raw_key_matched=raw_key, key_released_to_fallback=released, raw_key_match_rate_ZL3b=share(raw_key, len(A)), raw_key_match_rate_IT2a=share(raw_key, len(B)), key_matched=nkey, fallback_matched=nfb, matched=len(pairs),
                  only_ZL3b=len(A) - len(pairs), only_IT2a=len(B) - len(pairs),
                  key_match_rate_ZL3b=share(nkey, len(A)), key_match_rate_IT2a=share(nkey, len(B)),
                  matched_rate_ZL3b=share(len(pairs), len(A)), matched_rate_IT2a=share(len(pairs), len(B)))
    geoA, geoB = cb_geometry(A), cb_geometry(B)
    strata = {'all': lambda a, b: True, 'P': lambda a, b: a['typ'] == 'P' and b['typ'] == 'P',
              'P_ret_both': lambda a, b: a['typ'] == 'P' and b['typ'] == 'P' and a['ret'] and b['ret'],
              'P_ret_one': lambda a, b: a['typ'] == 'P' and b['typ'] == 'P' and (a['ret'] != b['ret']),
              'CurrierA': lambda a, b: a['L'] == 'A', 'CurrierB': lambda a, b: a['L'] == 'B',
              'CB_ZL3b': lambda a, b: a['ix'] in geoA, 'CB_IT2a': lambda a, b: b['ix'] in geoB}
    LC = {s: Counter() for s in strata}; TC = {s: Counter() for s in strata}; detail = Counter(); sepx = Counter(); subs = Counter(); split_gl = Counter(); wpl = []
    ret_dis = Counter(); hrows = []
    for a, b, how in pairs:
        cl = line_class(a, b, cfg)
        for s, f in strata.items():
            if f(a, b): LC[s][cl] += 1
        wpl.append(len(a['toks']) - len(b['toks'])); ret_dis[(a['ret'], b['ret'])] += 1
        if cl == 'unalignable_line': continue
        gs = classify_groups(a, b, cfg)
        for s, f in strata.items():
            if f(a, b):
                for g in gs: TC[s][g['cls']] += g['di'] + g['dj']      # token count of both transcriptions in the group
        for g in gs:
            c = g['cls']
            if c == 'split_merge':
                d = 'ZL3b_divided_in_IT2a' if g['di'] < g['dj'] else ('ZL3b_merged_in_IT2a' if g['di'] > g['dj'] else 'shift_2_2'); detail[d] += 1
                side = (b if g['di'] < g['dj'] else a); lo = g['j'] if side is b else g['i']; k = max(g['di'], g['dj'])
                seps_in = side['seps'][lo:lo + k - 1]
                for sp in seps_in: detail['dividing_sep_' + sp] += 1
                toks = side['toks'][lo:lo + k]
                for t1, t2 in zip(toks, toks[1:]): split_gl[t1[-1] + '|' + t2[0]] += 1
            elif c == 'glyph_different':
                detail['glyph_different_1_1' if (g['di'], g['dj']) == (1, 1) else 'glyph_different_other'] += 1
                sx = ''.join(a['toks'][g['i']:g['i'] + g['di']]); sy = ''.join(b['toks'][g['j']:g['j'] + g['dj']])
                if len(sx) == len(sy):
                    for p, q in zip(sx, sy):
                        if p != q: subs[p + '>' + q] += 1
        for g1, g2 in zip(gs, gs[1:]):
            if g1['cls'] in ('identical', 'split_merge', 'glyph_different') and g2['cls'] in ('identical', 'split_merge', 'glyph_different'):
                sa = a['seps'][g1['i'] + g1['di'] - 1] if g1['i'] + g1['di'] - 1 < len(a['seps']) else None
                sb = b['seps'][g1['j'] + g1['dj'] - 1] if g1['j'] + g1['dj'] - 1 < len(b['seps']) else None
                if sa and sb: sepx['ZL3b' + sa + '_IT2a' + sb] += 1
        if a['ix'] in geoA or b['ix'] in geoB:
            ea, eb = boundary_alignment(a, b, cfg); sa_, sb_ = set(ea), set(eb)
            hrows.append((a, b, cl, ea, eb, sa_, sb_))
    R['B'] = {s: dict(total=sum(c.values()), classes={k: share(c[k], sum(c.values())) for k in ('identical', 'division_only', 'glyph_different', 'unalignable_line')}) for s, c in LC.items()}
    R['C'] = {s: dict(tokens_in_aligned_lines=sum(c.values()), classes={k: share(c[k], sum(c.values())) for k in ('identical', 'split_merge', 'glyph_different', 'unalignable')}) for s, c in TC.items()}
    R['C_detail'] = dict(detail); R['C_separator_cross_at_group_boundaries'] = dict(sepx)
    R['C_top_glyph_substitutions_equal_length'] = subs.most_common(15); R['C_top_split_boundary_pairs'] = split_gl.most_common(15)
    R['retention_matched_pairs'] = {f'ZL3b_ret={k[0]}_IT2a_ret={k[1]}': v for k, v in ret_dis.items()}
    R['words_per_line_diff_ZL3b_minus_IT2a'] = dict(equal=share(sum(1 for x in wpl if x == 0), len(wpl)), mean=float(np.mean(wpl)), mean_abs=float(np.mean(np.abs(wpl))))
    # (h): '_' symbols of the CB unit stream of each transcription (one '_' after every word), by position class of the line in its own CB geometry
    H = {}
    for tname, geo, side in (('ZL3b', geoA, 0), ('IT2a', geoB, 1)):
        tab = defaultdict(Counter); lines_total = Counter()
        for l in (A if side == 0 else B):
            if l['ix'] in geo: lines_total[geo[l['ix']][2]] += len(l['toks'])
        matched_ix = set()
        for a, b, cl, ea, eb, sa_, sb_ in hrows:
            me = a if side == 0 else b
            if me['ix'] not in geo: continue
            matched_ix.add(me['ix']); own, oth = (ea, sb_) if side == 0 else (eb, sa_); cls = geo[me['ix']][2]
            for k, e in enumerate(own):
                final = k == len(own) - 1; key = (cls, 'final' if final else 'interior')
                same = e in oth
                tab[key]['same' if same else 'differ'] += 1
                tab[(cls, 'all')]['same' if same else 'differ'] += 1
                tab[('ALL', 'final' if final else 'interior')]['same' if same else 'differ'] += 1
                tab[('ALL', 'all')]['same' if same else 'differ'] += 1
                if cl == 'identical' or cl == 'division_only':
                    tab[(cls, 'all_Gidentical')]['same' if same else 'differ'] += 1; tab[('ALL', 'all_Gidentical')]['same' if same else 'differ'] += 1
                    if not final: tab[(cls, 'interior_Gidentical')]['same' if same else 'differ'] += 1; tab[('ALL', 'interior_Gidentical')]['same' if same else 'differ'] += 1
        unm = Counter()
        for l in (A if side == 0 else B):
            if l['ix'] in geo and l['ix'] not in matched_ix: unm[geo[l['ix']][2]] += len(l['toks']); unm['ALL'] += len(l['toks'])
        H[tname] = dict(table={f'{k[0]}|{k[1]}': dict(**share(v['differ'], v['differ'] + v['same']), same=v['same'], differ=v['differ']) for k, v in sorted(tab.items())},
                        underscores_in_lines_without_counterpart_or_unalignable=dict(unm), underscores_total_CB_stream=dict(lines_total), CB_lines=len(geo))
        H[tname]['underscores_total_CB_stream']['ALL'] = int(sum(lines_total.values()))
    R['h_underscore_differs_in_CB_unit_stream'] = H
    return R

def run_real(outdir):
    os.makedirs(outdir, exist_ok=True)
    cfgs = [Cfg('base'), Cfg('a_glyphmap_rare', gmap='rare'), Cfg('a2_question_wildcard', wild=True), Cfg('b_no_fallback', fallback=False),
            Cfg('c_arrow_removed', arrow='removed'), Cfg('d_comma_nosep', comma='none'), Cfg('e_line_1_4', lt=1 / 4), Cfg('e_line_1_2', lt=1 / 2),
            Cfg('e_token_1_3', tt=1 / 3), Cfg('e_token_2_3', tt=2 / 3), Cfg('alt_second_reading', alt='second')]
    for c in cfgs:
        A, bA = load('data/ZL3b-n.txt', c); B, bB = load('data/IT2a-n.txt', c)
        R = count(A, B, c, bA, bB); json.dump(R, open(f'{outdir}/real_{c.name}.json', 'w'), indent=1, sort_keys=True); print('done', c.name, flush=True)

# ------------------------------------------------------------------ planted control (g)
GL = sorted(set('acdefhiklmnopqrsty') | set('gxvz'))
RATES = dict(merge=0.04, split=0.04, swap=0.03, garble_line=0.02, delete_line=0.02, comma_to_dot=1.0)
def plant_file(src, dst, seed):
    rng = np.random.default_rng(seed); A, _ = load(src, Cfg('base')); truth = dict(merges=0, splits=0, swaps=0, tokens=0, garbled=[], deleted=[], bounds_total=0, key_map={}, line_merges={}, line_splits={})
    out_lines = []; cur_folio, shift = None, 0; B = []
    for l in A:
        if l['folio'] != cur_folio: cur_folio, shift = l['folio'], 0
        toks, seps = list(l['toks']), list(l['seps']); key = (l['folio'], l['num'], l['typ'])
        if rng.random() < RATES['delete_line']: truth['deleted'].append(key); shift += 1; continue
        truth['bounds_total'] += len(toks)
        garble = rng.random() < RATES['garble_line']; nt, ns, i = [], [], 0; ev = Counter(); lastsep = None
        while i < len(toks):
            t = toks[i]; r = rng.random(); truth['tokens'] += 1
            if garble: t2 = ''.join(GL[int(rng.integers(len(GL)))] if rng.random() < 0.7 else ch for ch in t); nt.append(t2); i += 1
            elif r < RATES['merge'] and i + 1 < len(toks): nt.append(t + toks[i + 1]); ev['m'] += 1; truth['merges'] += 1; i += 2; truth['tokens'] += 1
            elif r < RATES['merge'] + RATES['split'] and len(t) >= 2:
                k = int(rng.integers(1, len(t))); nt += [t[:k], t[k:]]; ns.append('.'); ev['s'] += 1; truth['splits'] += 1; i += 1
            elif r < RATES['merge'] + RATES['split'] + RATES['swap'] and len(t) >= 3:
                j = int(rng.integers(len(t))); c = GL[int(rng.integers(len(GL)))]
                while c == t[j]: c = GL[int(rng.integers(len(GL)))]
                nt.append(t[:j] + c + t[j + 1:]); ev['w'] += 1; truth['swaps'] += 1; i += 1
            else: nt.append(t); i += 1
        if garble: truth['garbled'].append(key)
        truth['line_merges'][f'{key[0]}.{key[1]}.{key[2]}'] = ev['m']; truth['line_splits'][f'{key[0]}.{key[1]}.{key[2]}'] = ev['s']
        # rebuild separators: '.' everywhere (IT2a-like: commas become dots)
        text = '.'.join(nt)
        B.append(dict(l, new=(l['folio'], l['num'] - shift, l['typ'], l['code'], text))); truth['key_map'][f'{key[0]}.{key[1]}.{key[2]}'] = f'{key[0]}.{l["num"] - shift}.{key[2]}'
    meta = headers(src); seen = set()
    with open(dst, 'w') as fh:
        for l in B:
            if l['new'] is None: continue
            f, n, tp, code, text = l['new']
            if f not in seen:
                seen.add(f); fh.write(f'<{f}> <! ' + ' '.join(f'${k}={v}' for k, v in meta.get(f, {}).items()) + '>\n')
            fh.write(f'<{f}.{n},+{code}> {text}\n')
    return truth

def run_control(outdir):
    os.makedirs(outdir, exist_ok=True); dst = f'{outdir}/planted_ZL3b_copy.txt'
    truth = plant_file('data/ZL3b-n.txt', dst, CONTROL_SEED); cfg = Cfg('base')
    A, _ = load('data/ZL3b-n.txt', cfg); B, _ = load(dst, cfg); R = count(A, B, cfg)
    # truth for the pair recovery: how many truth-paired lines does the aligner pair correctly?
    pairs, nkey, nfb, _, _ = pair_lines(A, B, cfg); kb = {f'{b["folio"]}.{b["num"]}.{b["typ"]}': b for b in B}
    gar = {f'{k[0]}.{k[1]}.{k[2]}' for k in truth['garbled']}
    gt = {k: v for k, v in truth['key_map'].items()}; got = {f'{a["folio"]}.{a["num"]}.{a["typ"]}': f'{b["folio"]}.{b["num"]}.{b["typ"]}' for a, b, _ in pairs}
    cnt = Counter()
    for k, v in gt.items():
        g = 'garbled' if k in gar else 'clean'
        cnt[g + '_truth'] += 1
        if k in got: cnt[g + ('_correct' if got[k] == v else '_wrong')] += 1
        else: cnt[g + '_unpaired'] += 1
    right, ntrue = cnt['clean_correct'], cnt['clean_truth']; spurious = sum(1 for k in got if k not in gt)
    wrong = cnt['clean_wrong']; missing = cnt['clean_unpaired']
    ctl = dict(seed=CONTROL_SEED, rates=RATES, truth={k: (v if not isinstance(v, (list, dict)) else len(v)) for k, v in truth.items()},
               pair_recovery=dict(clean_truth_pairs=int(ntrue), clean_correct=int(right), clean_wrong=int(wrong), clean_unpaired=int(missing), garbled_lines=dict(cnt) , spurious_pairs_for_deleted_lines=int(spurious),
                                  accuracy_clean=share(right, ntrue)), counts=R)
    # token-level recovery: truth events sit on disjoint tokens; recovered = groups of that type found by the aligner (all aligned lines)
    d = R['C_detail']; N = truth['tokens']; chk = {}
    for nm, tr, rec in (('merges', truth['merges'], d.get('ZL3b_merged_in_IT2a', 0)), ('splits', truth['splits'], d.get('ZL3b_divided_in_IT2a', 0)),
                        ('swaps', truth['swaps'], d.get('glyph_different_1_1', 0))):
        w = wilson(rec, N); chk[nm] = dict(truth=tr, recovered=rec, rate_truth=tr / N, rate_recovered=rec / N, wilson_recovered_rate=w, truth_inside_wilson=bool(w[0] <= tr / N <= w[1]))
    ctl['token_recovery'] = dict(planted_tokens_in_kept_lines=N, events=chk)
    # (h) check: ZL3b-side '_' with no counterpart = planted merges; IT2a-side '_' with no counterpart = planted splits; truth restricted to the paired lines of the CB stratum
    geoA, geoB = cb_geometry(A), cb_geometry(B); hres = {}
    pk = {f'{a["folio"]}.{a["num"]}.{a["typ"]}': (a, b) for a, b, _ in pairs}
    for side, name, ev, geo in ((0, 'ZL3b', truth['line_merges'], geoA), (1, 'IT2a', truth['line_splits'], geoB)):
        k_true = n_tot = 0
        for key, (a, b) in pk.items():
            me = a if side == 0 else b
            if me['ix'] not in geo or key not in gt: continue
            if line_class(a, b, cfg) == 'unalignable_line': continue
            k_true += ev.get(key, 0); n_tot += len(me['toks'])
        rec = R['h_underscore_differs_in_CB_unit_stream'][name]['table'].get('ALL|all')
        w = rec['wilson']; hres[name] = dict(truth_differ=k_true, truth_n=n_tot, truth_rate=k_true / n_tot, recovered=rec, truth_inside_wilson=bool(w[0] <= k_true / n_tot <= w[1]))
    ctl['h_check'] = hres
    ctl['pass'] = bool(ctl['pair_recovery']['accuracy_clean']['share'] >= 0.99 and all(v['truth_inside_wilson'] for v in chk.values()) and all(v['truth_inside_wilson'] for v in hres.values()))
    json.dump(ctl, open(f'{outdir}/control.json', 'w'), indent=1, sort_keys=True); print(json.dumps(ctl['pair_recovery']), json.dumps(ctl['token_recovery']), 'PASS' if ctl['pass'] else 'FAIL')

if __name__ == '__main__':
    mode = sys.argv[1]; out = sys.argv[2]
    if mode == 'control': run_control(out)
    elif mode == 'real': run_real(out)
    else: sys.exit('mode?')
