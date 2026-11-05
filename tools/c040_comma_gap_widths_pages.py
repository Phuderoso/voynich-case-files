#!/usr/bin/env python3
"""C040 (F-SEG step 5): the C039 anchored ink-gap ruler, unchanged, on every usable text-only / stars page that has
ZL commas (f58r/v, f103r-f116r), so that test B (certain spaces wider than commas) can reach its power gate.
Pre-registered in case-file/C040-comma-gap-widths-all-pages.md. Seed 4040. numpy + PIL only.
Reuses tools/c039_comma_gap_widths.py helpers (imported, not edited; C039 stays reproducible).
Run: timeout 600 python3 tools/c040_comma_gap_widths_pages.py
Geometry-only dry run (no widths, no tests): C040_GEOMETRY_ONLY=1 python3 tools/c040_comma_gap_widths_pages.py
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c039_comma_gap_widths as G          # page_lines, match_lines, measure_line, raw_lines, strat, null (C039 run-2 rule)
import c034_harris_boundaries as X
import c035_comma_half_boundaries as Y
import c036_commas_vs_takahashi as C

SEED, NPERM, NREP, NGATE = 4040, 2000, 40, 200
ALPHA = 0.05 / 2                     # tests A and B
SCANS = G.SCANS
# pre-registered pages and text boxes (x0, x1, y0, y1), full-resolution pixels, set from 1/4-scale thumbnails before any run.
# C039's four pages keep C039's boxes. Skipped: f112v (staggered left margin, stars inside the text block), f116v (1 ZL line);
# f109/f110 do not exist in the codex.
PAGES = dict(G.PAGES)
PAGES.update({
    'f103r': ('183_f103r.jpg', (320, 2450, 200, 3240)),
    'f103v': ('184_f103v.jpg', (670, 2680, 130, 3200)),
    'f104r': ('185_f104r.jpg', (330, 2590, 160, 3110)),
    'f104v': ('186_f104v.jpg', (500, 2640, 130, 3090)),
    'f105r': ('187_f105r.jpg', (300, 2540, 320, 3050)),
    'f105v': ('188_f105v.jpg', (410, 2600, 120, 2940)),
    'f106r': ('189_f106r.jpg', (360, 2400, 150, 3310)),
    'f106v': ('190_f106v.jpg', (500, 2600, 150, 3310)),
    'f107r': ('191_f107r.jpg', (320, 2280, 130, 3250)),
    'f107v': ('192_f107v.jpg', (505, 2590, 100, 3270)),
    'f108r': ('193_f108r.jpg', (330, 2320, 140, 3190)),
    'f108v': ('194_f108v.jpg', (530, 2560, 140, 3270)),
    'f111v': ('196_f111v.jpg', (590, 2560, 120, 3210)),
    'f112r': ('197_f112r.jpg', (290, 2130, 150, 3210)),
    'f113r': ('199_f113r.jpg', (200, 2260, 140, 3250)),
    'f114r': ('201_f114r.jpg', (215, 2260, 120, 3090)),
    'f114v': ('202_f114v.jpg', (540, 2600, 140, 3030)),
    'f115r': ('203_f115r.jpg', (230, 2290, 140, 3210)),
    'f115v': ('204_f115v.jpg', (500, 2580, 150, 3110)),
    'f116r': ('205_f116r.jpg', (210, 2260, 150, 3180))})
GEOM = os.environ.get('C040_GEOMETRY_ONLY', '0') == '1'
OUT = 'analysis/C040_geometry_dryrun.json' if GEOM else 'analysis/C040_results.json'

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED)
    Z, I = C.loci('data/ZL3b-n.txt'), C.loci('data/IT2a-n.txt')
    R = dict(pages={}, method=dict(ruler='C039 run-2 (Amendment 1: length clause only)', ink='blur%d-diff>%d' % (G.BG_R, G.INK_T),
                                   band=G.BAND, run_min=G.RUN_MIN, end_gap=G.END_GAP, cap=G.CAP, seed=SEED))
    lines = []  # (folio, locus, widths, gaptypes)
    for f, (img, box) in PAGES.items():
        tr = G.page_lines(os.path.join(SCANS, img), box); zl = G.raw_lines(f)
        pairs, ppw = G.match_lines(tr, zl); acc = rej = 0; anc = [0, 0]
        for ti, zi in pairs:
            loc = zl[zi][0]
            if loc not in Z: continue
            u, g = Z[loc]; t = tr[ti]
            ok = abs((t['xb'] - t['xa']) / ppw - zl[zi][3]) <= 0.25 * zl[zi][3]      # C039 Amendment-1 gate
            if not ok: rej += 1; continue
            acc += 1
            if GEOM: continue
            wd, na, ns = G.measure_line(t, u, g, ppw); anc[0] += na; anc[1] += ns
            lines.append((f, loc, wd, np.array(g)))
        R['pages'][f] = dict(image=img, box=box, traces=len(tr), zl_lines=len(zl), matched=len(pairs), accepted=acc,
                             rejected=rej, px_per_weight=round(float(ppw), 2), spaces_anchored=anc)
        print(f, R['pages'][f], round(time.time() - t0, 1), 's', flush=True)
    if GEOM:
        R['accepted_total'] = sum(p['accepted'] for p in R['pages'].values()); R['seconds'] = round(time.time() - t0, 1)
        json.dump(R, open(OUT, 'w'), indent=1, default=float); print('geometry only', R['accepted_total']); return
    s, _ = Y.zl_stream(); sc = X.scores(s); offs, pos = {}, 0
    for k in Z: offs[k] = pos; pos += len(Z[k][0])
    assert pos == len(s)
    wd = [l[2] for l in lines]; g = [l[3] for l in lines]
    comma = [x == 2 for x in g]; space = [x == 1 for x in g]; none = [x == 0 for x in g]
    for x in none: x[0] = False
    cnt = lambda M: sum(int(m.sum()) for m in M)
    def desc(M, W=wd):
        v = np.concatenate([w[m] for w, m in zip(W, M)]) if M else np.array([])
        return dict(n=int(len(v)), mean=float(v.mean()) if len(v) else None, median=float(np.median(v)) if len(v) else None,
                    frac_ge15=float(np.mean(v >= 15)) if len(v) else None)
    R['lines_used'] = len(lines); R['widths'] = dict(space=desc(space), comma=desc(comma), nongap=desc(none))
    R['per_page'] = {}
    for f in PAGES:
        ix = [i for i, l in enumerate(lines) if l[0] == f]; W = [wd[i] for i in ix]
        R['per_page'][f] = dict(lines=len(ix), space=desc([space[i] for i in ix], W), comma=desc([comma[i] for i in ix], W),
                                nongap=desc([none[i] for i in ix], W))
    print(R['widths'], flush=True)
    candA = [c | n for c, n in zip(comma, none)]; candB = [c | s_ for c, s_ in zip(comma, space)]
    oA = G.strat(comma, candA, wd); nA = G.null(comma, candA, wd, rng, NPERM); pA = (1 + (nA >= oA).sum()) / (NPERM + 1)
    oB = G.strat(space, candB, wd); nB = G.null(space, candB, wd, rng, NPERM); pB = (1 + (nB >= oB).sum()) / (NPERM + 1)
    candS = [s_ | n for s_, n in zip(space, none)]; oS = G.strat(space, candS, wd); nS = G.null(space, candS, wd, rng, 500)
    R['A_comma_vs_nongap'] = dict(diff=oA, p=float(pA)); R['B_space_vs_comma'] = dict(diff=oB, p=float(pB))
    R['sanity_space_vs_nongap'] = dict(diff=oS, p=float((1 + (nS >= oS).sum()) / 501))
    print('A', oA, pA, 'B', oB, pB, 'S', oS, round(time.time() - t0, 1), 's', flush=True)
    # gates: label-level planted controls on the measured widths (identical to C039)
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
        f = fake(src=lambda s_, n: n); fa += pv(nA2, G.strat(f, [x | n for x, n in zip(f, none)], wd)) < ALPHA
        f = fake(src=lambda s_, n: s_); fb += pv(nB2, G.strat([s_ & ~x for s_, x in zip(space, f)], [s_ | x for s_, x in zip(space, f)], wd)) < ALPHA
        f = fake(mix=True)
        pa += pv(nA2, G.strat(f, [x | n for x, n in zip(f, none)], wd)) < ALPHA
        pb += pv(nB2, G.strat([s_ & ~x for s_, x in zip(space, f)], [s_ | x for s_, x in zip(space, f)], wd)) < ALPHA
    ok = fa <= 4 and fb <= 4 and pa >= 32 and pb >= 32
    R['gates'] = dict(fpr_A=fa / NREP, fpr_B=fb / NREP, power_A=pa / NREP, power_B=pb / NREP, passed=bool(ok),
                      gate_A_only=bool(fa <= 4 and pa >= 32), gate_B_only=bool(fb <= 4 and pb >= 32))
    sA, sB = pA < ALPHA, pB < ALPHA
    R['verdict'] = 'NOT TESTABLE' if not ok else ('HALF (intermediate width)' if sA and sB else 'SPACE-LIKE' if sA else
                                                  'NON-GAP-LIKE' if sB else 'UNRESOLVED')
    print(R['gates'], R['verdict'], round(time.time() - t0, 1), 's', flush=True)
    # Look 2 (secondary, alpha 0.025 each): comma width vs C035 Harris score (Spearman), vs IT2a space choice (AUC)
    cw, cs, it = [], [], []
    for (f, loc, w_, g_) in lines:
        for j in np.flatnonzero(g_ == 2):
            cw.append(w_[j]); cs.append(sc[offs[loc] + j])
            it.append((I[loc][1][j] in (1, 2)) if (loc in I and I[loc][0] == Z[loc][0]) else None)
    cw, cs = np.array(cw), np.array(cs, float); m = ~np.isnan(cs)
    rw, rs = X.rankdata(cw[m]), X.rankdata(cs[m]); rho = float(np.corrcoef(rw, rs)[0, 1]) if m.sum() > 2 else float('nan')
    ge = sum(np.corrcoef(rng.permutation(rw), rs)[0, 1] >= rho for _ in range(NPERM)) if m.sum() > 2 else 0
    R['look2_harris'] = dict(n=int(m.sum()), spearman=rho, p=float((1 + ge) / (NPERM + 1)))
    sel = np.array([x is not None for x in it]); yv = np.array([bool(x) for x in it if x is not None]); wv = cw[sel]
    if len(yv) and 0 < yv.sum() < len(yv):
        r = X.rankdata(wv); n1 = yv.sum(); auc = float((r[yv].sum() - n1 * (n1 + 1) / 2) / (n1 * (len(yv) - n1))); ge = 0
        for _ in range(NPERM):
            yy = rng.permutation(yv); ge += (r[yy].sum() - n1 * (n1 + 1) / 2) / (n1 * (len(yv) - n1)) >= auc
        R['look2_it2a'] = dict(n=int(len(yv)), n_it2a_space=int(n1), auc=auc, p=float((1 + ge) / (NPERM + 1)),
                               mean_w_it2a_space=float(wv[yv].mean()), mean_w_it2a_nospace=float(wv[~yv].mean()))
    else:
        R['look2_it2a'] = dict(n=int(len(yv)), note='one class empty')
    R['seconds'] = round(time.time() - t0, 1)
    print(R['look2_harris'], R['look2_it2a'], R['seconds'], flush=True)
    json.dump(R, open(OUT, 'w'), indent=1, default=float)

if __name__ == '__main__':
    main()
