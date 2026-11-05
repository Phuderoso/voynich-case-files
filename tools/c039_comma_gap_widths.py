#!/usr/bin/env python3
"""C039 (F-SEG step 4): on the Beinecke scans, is the ink gap at a ZL comma (uncertain space) as wide as a
certain space, as narrow as a within-word glyph join, or in between? Does gap width track the C035 Harris score
and Takahashi's (IT2a) space/no-space choice at the same comma?
Pre-registered in case-file/C039-comma-gap-widths.md. Seed 3939. numpy + PIL only.
Run: timeout 600 python3 tools/c039_comma_gap_widths.py   — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, time
import numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
import c003_position_rigidity as T
import c034_harris_boundaries as X
import c035_comma_half_boundaries as Y
import c036_commas_vs_takahashi as C

SEED, NPERM, NREP, NGATE = 3939, 2000, 40, 200
ALPHA = 0.05 / 2                     # tests A and B
SCANS = os.environ.get('VOY_SCANS', '/workspace/voynich/scans')
# pre-registered pages and text boxes (x0, x1, y0, y1) in full-resolution pixels, set from thumbnails before any run
PAGES = {'f58r': ('115_f58r.jpg', (650, 2450, 280, 3050)),
         'f58v': ('116_f58v.jpg', (900, 2800, 280, 2980)),
         'f111r': ('195_f111r.jpg', (345, 2450, 100, 3230)),
         'f113v': ('200_f113v.jpg', (495, 2600, 110, 3260))}
INK_T, BG_R = 30, 25                 # ink = background(blur 25) - pixel > 30
SEED_W, STRIP, MD, TRACK = 320, 150, 45, 22
BAND = (-14, 10)                     # core band around traced line centre
RUN_MIN, END_GAP, CAP = 10, 60, 60   # anchor-candidate run >=10 px; line ends at first blank run >=60 px; widths capped
# Amendment 1 (pushed before run 2): run 1 accepted only 9 lines -> NOT TESTABLE. The run-count clause of the line gate is
# dropped (runs >= 10 px include within-word joins, so counts overshoot); the length clause stays. Run 1: RUN_GATE = True.
RUN_GATE = os.environ.get('C039_RUN_GATE', '0') == '1'
OUT = 'analysis/C039_results_run1.json' if RUN_GATE else 'analysis/C039_results.json'

def wt(u):
    if u in ('ch', 'sh'): return 1.6
    if len(u) > 2: return 2.0
    if u[0] in 'ktpf': return 1.4
    return {'i': 0.5, 'e': 0.8}.get(u, 1.0)

def raw_lines(folio):
    """every paragraph-or-not text line of the folio in file order: (locus, n_spaces, n_commas, weight) for matching"""
    out = []
    for line in open('data/ZL3b-n.txt', encoding='utf-8', errors='replace'):
        m = re.match(r'<(%s)\.(\d+),[@+=*&~-](\w+)>\s*(.*)' % folio, line.rstrip('\n'))
        if not m: continue
        t = m.group(4).replace('<->', '.'); t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t); t = re.sub(r'[^a-z.,]', '', t)
        toks = [x for x in re.split(r'([.,]+)', t) if x]
        ns = sum(1 for x in toks[1:-1] if re.fullmatch(r'[.,]+', x) and '.' in x)
        nc = sum(1 for x in toks[1:-1] if re.fullmatch(r'[.,]+', x) and '.' not in x)
        w = sum(wt(u) for x in toks if not re.fullmatch(r'[.,]+', x) for u in T.units(x))
        out.append(('%s.%s' % (folio, m.group(2)), ns, nc, w))
    return out

def peaks(p, md=MD):
    ps = np.convolve(p, np.ones(11) / 11, 'same')
    c = [i for i in range(1, len(ps) - 1) if ps[i] >= ps[i - 1] and ps[i] > ps[i + 1] and ps[i] > 3]
    keep = []
    for i in sorted(c, key=lambda i: -ps[i]):
        if all(abs(i - j) >= md for j in keep): keep.append(i)
    keep.sort(); out = []
    for n, i in enumerate(keep):
        lo = ps[keep[n - 1]:i].min() if n > 0 else 0; hi = ps[i:keep[n + 1]].min() if n < len(keep) - 1 else 0
        if ps[i] - max(lo, hi) > 0.35 * ps[i]: out.append(i)
    return out

def runs_of(b, off=0, mn=1):
    r, s = [], None
    for i, v in enumerate(list(b) + [False]):
        if v and s is None: s = i
        if not v and s is not None:
            if i - s >= mn: r.append((s + off, i + off))
            s = None
    return r

def page_lines(img, box):
    """trace text lines; return list of dict(band=col ink counts, x0=, xa, xb, runs)"""
    x0, x1, y0, y1 = box
    im = Image.open(img).convert('L'); a = np.asarray(im, float)
    bg = np.asarray(im.filter(ImageFilter.GaussianBlur(BG_R)), float); ink = (bg - a) > INK_T
    ink[:y0] = 0; ink[y1:] = 0; ink[:, :x0] = 0; ink[:, x1:] = 0
    seed = peaks(ink[:, x0 + 60:x0 + 60 + SEED_W].sum(1))
    xs = list(range(x0 + 60, x1, STRIP)); spk = {x: peaks(ink[:, x:x + STRIP].sum(1)) for x in xs}
    out = []
    for y in seed:
        tr = [(x0 + 60 + SEED_W / 2, y)]; cur = y
        for x in xs[2:]:
            c = [q for q in spk[x] if abs(q - cur) < TRACK]
            if c: cur = min(c, key=lambda q: abs(q - cur)); tr.append((x + STRIP / 2, cur))
        X_, Y_ = np.array([t[0] for t in tr]), np.array([t[1] for t in tr])
        cols = np.arange(x0, x1); yy = np.interp(cols, X_, Y_).astype(int)
        band = np.array([ink[y + BAND[0]:y + BAND[1], c].sum() for c, y in zip(cols, yy)])
        on = np.flatnonzero(np.convolve(band > 0, np.ones(5), 'same') >= 3)
        if len(on) == 0: continue
        xa = int(on[0]); blank = band == 0
        big = [r for r in runs_of(blank[xa:], xa, END_GAP)]
        xb = big[0][0] if big else int(on[-1])
        runs = [r for r in runs_of(blank[xa:xb], xa, RUN_MIN)]
        out.append(dict(band=band, xa=xa, xb=xb, runs=runs, y=int(np.median(Y_))))
    return out

def match_lines(tr, zl):
    """monotone DP between traced lines and ZL lines; cost from run count vs (spaces + commas/2) and length"""
    ppw = np.median([t['xb'] - t['xa'] for t in tr]) / np.median([z[3] for z in zl])
    def cost(t, z):
        return abs(len(t['runs']) - (z[1] + z[2] / 2)) / 2 + 4 * abs((t['xb'] - t['xa']) / ppw - z[3]) / max(z[3], 1)
    n, m = len(tr), len(zl); D = np.full((n + 1, m + 1), 1e9); D[0, :] = np.arange(m + 1) * 3.0; D[:, 0] = np.arange(n + 1) * 2.0
    B = {}
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            opts = [(D[i - 1, j - 1] + cost(tr[i - 1], zl[j - 1]), 'm'), (D[i - 1, j] + 2.0, 't'), (D[i, j - 1] + 3.0, 'z')]
            D[i, j], B[i, j] = min(opts)
    i, j, pairs = n, m, []
    while i > 0 and j > 0:
        b = B[i, j]
        if b == 'm': pairs.append((i - 1, j - 1)); i -= 1; j -= 1
        elif b == 't': i -= 1
        else: j -= 1
    return pairs[::-1], ppw

def measure_line(t, u, g, ppw):
    """width (px, capped) of the longest blank run touching the expected position of every boundary j=1..n-1;
    expected positions interpolated in glyph-weight space between anchors = certain spaces matched to runs
    (leave-one-out: a space is measured with its own anchor removed)."""
    w = np.array([wt(x) for x in u]); cum = np.concatenate([[0], np.cumsum(w)]); W = cum[-1]
    xa, xb, runs, band = t['xa'], t['xb'], t['runs'], t['band']
    sp = [j for j in range(1, len(u)) if g[j] == 1]
    exp = {j: xa + cum[j] / W * (xb - xa) for j in sp}
    # anchor DP: each space -> distinct run, in order, score = width - 0.1*|centre - expected| (or unmatched = 0)
    R = [(a, b, b - a, (a + b) / 2) for a, b in runs]; S = len(sp); N = len(R)
    F = np.zeros((S + 1, N + 1)); P = {}
    for i in range(1, S + 1):
        F[i, 0] = F[i - 1, 0]; P[i, 0] = 'u'
        for k in range(1, N + 1):
            sc = R[k - 1][2] - 0.1 * abs(R[k - 1][3] - exp[sp[i - 1]])
            opts = [(F[i - 1, k], 'u'), (F[i, k - 1], 's')] + ([(F[i - 1, k - 1] + sc, 'm')] if sc > 0 else [])
            F[i, k], P[i, k] = max(opts)
    anch, i, k = {}, S, N
    while i > 0:
        p = P[i, k] if k > 0 else 'u'
        if p == 'm': anch[sp[i - 1]] = R[k - 1]; i -= 1; k -= 1
        elif p == 's': k -= 1
        else: i -= 1
    half = 0.6 * ppw; blank = band == 0; out = []
    for j in range(1, len(u)):
        L = [(0, xa)] + [(q, anch[q][1]) for q in sorted(anch) if q < j]
        Rr = [(q, anch[q][0]) for q in sorted(anch) if q > j] + [(len(u), xb)]
        (jl, xl), (jr, xr) = L[-1], Rr[0]
        ex = xl + (cum[j] - cum[jl]) / max(cum[jr] - cum[jl], 1e-9) * (xr - xl)
        lo, hi = int(ex - half), int(ex + half) + 1; best = 0
        for a, b in runs_of(blank[max(lo, 0):hi], max(lo, 0)):
            # extend to full run length
            while a > 0 and blank[a - 1]: a -= 1
            while b < len(blank) and blank[b]: b += 1
            best = max(best, b - a)
        out.append(min(best, CAP))
    return np.array([0] + out, float), len(anch), S

def strat(lab, cand, y):
    a = sum(float(y_[l].sum()) for l, y_ in zip(lab, y)); na = sum(int(l.sum()) for l in lab)
    b = sum(float(y_[c & ~l].sum()) for l, c, y_ in zip(lab, cand, y)); nb = sum(int((c & ~l).sum()) for l, c in zip(lab, cand))
    return a / max(na, 1) - b / max(nb, 1)

def null(lab, cand, y, rng, n):
    out = []
    for _ in range(n):
        L = []
        for l, c in zip(lab, cand):
            idx = np.flatnonzero(c); k = int(l.sum()); z = np.zeros_like(l)
            if k: z[rng.choice(idx, k, replace=False)] = True
            L.append(z)
        out.append(strat(L, cand, y))
    return np.array(out)

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED)
    Z, I = C.loci('data/ZL3b-n.txt'), C.loci('data/IT2a-n.txt')
    s, _ = Y.zl_stream(); sc = X.scores(s); offs, pos = {}, 0
    for k in Z: offs[k] = pos; pos += len(Z[k][0])
    assert pos == len(s)
    R = dict(pages={}, method=dict(ink='blur%d-diff>%d' % (BG_R, INK_T), band=BAND, run_min=RUN_MIN, end_gap=END_GAP, cap=CAP))
    lines = []  # (locus, widths, gaptypes)
    for f, (img, box) in PAGES.items():
        tr = page_lines(os.path.join(SCANS, img), box); zl = raw_lines(f)
        pairs, ppw = match_lines(tr, zl); acc = 0; rej = 0; anc = [0, 0]
        for ti, zi in pairs:
            loc = zl[zi][0]
            if loc not in Z: continue
            u, g = Z[loc]; t = tr[ti]
            # acceptance gate (symmetric in commas): detected runs within [spaces-1, spaces+commas+1]; length within 25%
            ok = (not RUN_GATE or zl[zi][1] - 1 <= len(t['runs']) <= zl[zi][1] + zl[zi][2] + 1) and \
                 abs((t['xb'] - t['xa']) / ppw - zl[zi][3]) <= 0.25 * zl[zi][3]
            if not ok: rej += 1; continue
            wd, na, ns = measure_line(t, u, g, ppw); anc[0] += na; anc[1] += ns
            lines.append((loc, wd, np.array(g))); acc += 1
        R['pages'][f] = dict(image=img, box=box, traces=len(tr), zl_lines=len(zl), matched=len(pairs), accepted=acc,
                             rejected=rej, px_per_weight=round(float(ppw), 2), spaces_anchored=anc)
        print(f, R['pages'][f], round(time.time() - t0, 1), 's', flush=True)
    wd = [l[1] for l in lines]; g = [l[2] for l in lines]
    comma = [x == 2 for x in g]; space = [x == 1 for x in g]; none = [x == 0 for x in g]
    for x in none: x[0] = False
    cnt = lambda M: sum(int(m.sum()) for m in M)
    desc = lambda M: dict(n=cnt(M), mean=float(np.mean(np.concatenate([w[m] for w, m in zip(wd, M)]))),
                          median=float(np.median(np.concatenate([w[m] for w, m in zip(wd, M)]))),
                          frac_ge15=float(np.mean(np.concatenate([w[m] for w, m in zip(wd, M)]) >= 15)))
    R['lines_used'] = len(lines); R['widths'] = dict(space=desc(space), comma=desc(comma), nongap=desc(none))
    print(R['widths'], flush=True)
    candA = [c | n for c, n in zip(comma, none)]; candB = [c | s_ for c, s_ in zip(comma, space)]
    oA = strat(comma, candA, wd); nA = null(comma, candA, wd, rng, NPERM); pA = (1 + (nA >= oA).sum()) / (NPERM + 1)
    oB = strat(space, candB, wd); nB = null(space, candB, wd, rng, NPERM); pB = (1 + (nB >= oB).sum()) / (NPERM + 1)
    # sanity: certain spaces vs non-gaps (alignment works at all?)
    candS = [s_ | n for s_, n in zip(space, none)]; oS = strat(space, candS, wd); nS = null(space, candS, wd, rng, 500)
    R['A_comma_vs_nongap'] = dict(diff=oA, p=float(pA)); R['B_space_vs_comma'] = dict(diff=oB, p=float(pB))
    R['sanity_space_vs_nongap'] = dict(diff=oS, p=float((1 + (nS >= oS).sum()) / 501))
    print('A', oA, pA, 'B', oB, pB, 'S', oS, round(time.time() - t0, 1), 's', flush=True)
    # gates: label-level planted controls on the measured widths (as C036)
    nA2, nB2 = nA[:NGATE], nB[:NGATE]; fa = fb = pa = pb = 0
    def fake(mix=None, src=None):
        out = []
        for c, s_, n in zip(comma, space, none):
            k = int(c.sum()); z = np.zeros_like(c)
            if mix is None:
                pool = np.flatnonzero(src(s_, n)); kk = min(k, len(pool))
                if kk: z[rng.choice(pool, kk, replace=False)] = True
            else:
                for pool_arr, kk in ((s_, (k + 1) // 2), (n, k // 2)):
                    pool = np.flatnonzero(pool_arr & ~z); kk = min(kk, len(pool))
                    if kk: z[rng.choice(pool, kk, replace=False)] = True
            out.append(z)
        return out
    pv = lambda nul, o: (1 + (nul >= o).sum()) / (NGATE + 1)
    for _ in range(NREP):
        f = fake(src=lambda s_, n: n); fa += pv(nA2, strat(f, [x | n for x, n in zip(f, none)], wd)) < ALPHA
        f = fake(src=lambda s_, n: s_); fb += pv(nB2, strat([s_ & ~x for s_, x in zip(space, f)], [s_ | x for s_, x in zip(space, f)], wd)) < ALPHA
        f = fake(mix=True)
        pa += pv(nA2, strat(f, [x | n for x, n in zip(f, none)], wd)) < ALPHA
        pb += pv(nB2, strat([s_ & ~x for s_, x in zip(space, f)], [s_ | x for s_, x in zip(space, f)], wd)) < ALPHA
    ok = fa <= 4 and fb <= 4 and pa >= 32 and pb >= 32
    R['gates'] = dict(fpr_A=fa / NREP, fpr_B=fb / NREP, power_A=pa / NREP, power_B=pb / NREP, passed=bool(ok))
    sA, sB = pA < ALPHA, pB < ALPHA
    R['verdict'] = 'NOT TESTABLE' if not ok else ('HALF (intermediate width)' if sA and sB else 'SPACE-LIKE' if sA else
                                                  'NON-GAP-LIKE' if sB else 'UNRESOLVED')
    # Look 2 (secondary, alpha 0.05/2 each): comma width vs C035 Harris score (Spearman) and vs IT2a space choice (AUC)
    cw, cs, it = [], [], []
    for (loc, w_, g_) in lines:
        for j in np.flatnonzero(g_ == 2):
            v = sc[offs[loc] + j]
            cw.append(w_[j]); cs.append(v)
            it.append((I[loc][1][j] in (1, 2)) if (loc in I and I[loc][0] == Z[loc][0]) else None)
    cw, cs = np.array(cw), np.array(cs, float); m = ~np.isnan(cs)
    rw, rs = X.rankdata(cw[m]), X.rankdata(cs[m]); rho = float(np.corrcoef(rw, rs)[0, 1]) if m.sum() > 2 else float('nan')
    ge = sum(np.corrcoef(rng.permutation(rw), rs)[0, 1] >= rho for _ in range(NPERM)) if m.sum() > 2 else 0
    R['look2_harris'] = dict(n=int(m.sum()), spearman=rho, p=float((1 + ge) / (NPERM + 1)))
    sel = np.array([x is not None for x in it]); yv = np.array([bool(x) for x in it if x is not None])
    wv = cw[sel]
    if len(yv) and 0 < yv.sum() < len(yv):
        r = X.rankdata(wv); n1 = yv.sum(); auc = float((r[yv].sum() - n1 * (n1 + 1) / 2) / (n1 * (len(yv) - n1)))
        ge = 0
        for _ in range(NPERM):
            yy = rng.permutation(yv); ge += (r[yy].sum() - n1 * (n1 + 1) / 2) / (n1 * (len(yv) - n1)) >= auc
        R['look2_it2a'] = dict(n=int(len(yv)), n_it2a_space=int(n1), auc=auc, p=float((1 + ge) / (NPERM + 1)),
                               mean_w_it2a_space=float(wv[yv].mean()), mean_w_it2a_nospace=float(wv[~yv].mean()))
    else:
        R['look2_it2a'] = dict(n=int(len(yv)), note='one class empty')
    R['seconds'] = round(time.time() - t0, 1)
    print(R['gates'], R['verdict'], R['look2_harris'], R['look2_it2a'], R['seconds'], flush=True)
    R['run_gate'] = RUN_GATE
    json.dump(R, open(OUT, 'w'), indent=1, default=float)

if __name__ == '__main__':
    main()
