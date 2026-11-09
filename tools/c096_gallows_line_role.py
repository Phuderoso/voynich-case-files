#!/usr/bin/env python3
"""C096 (NEW FAMILY F-ALLO: allograph shape by line role, measured on the Beinecke MS 408 scans).
Question: on the same page, are the tall (gallows-sized) ink components on the FIRST line of a paragraph taller
(H1, height / page median component height) or differently proportioned (H2, width/height) than on the page's other
lines, with the paragraph-initial region (first 250 px of each line) excluded?
Pages and text boxes = C039's pre-registered set (f58r, f58v, f111r, f113v; ink rule blur(25) - pixel > 30; C039 line
tracing and monotone DP matching to ZL 3b lines, imported verbatim). FIRST = ZL line whose text starts a paragraph (<%>).
Pre-registered in case-file/C096-gallows-line-role.md. Seed 9696.
Modes: C096_MODE=diag -> registered diagnostic D1 only (added with the pre-registration after the rehearsal failed its
        gates; it reads no FIRST-line height or aspect): Spearman of kept components per line vs ZL line weight (matching
        sanity) and of tall components per line vs ZL gallows count, both per page and pooled.
       C096_MODE=rehearsal -> reach, alignment gate, FPR and power gates using OTHER lines only (no FIRST-line height
        or aspect value is computed or printed);  C096_MODE=main -> the registered tests.
Run: OMP_NUM_THREADS=1 timeout 600 /workspace/voynich/venv87/bin/python tools/c096_gallows_line_role.py
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote and ran this)"""
import os, re, sys, json, time
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi, stats
sys.path.insert(0, os.path.dirname(__file__))
import c039_comma_gap_widths as L

SEED, R_MAIN, R_GATE, N_GATE = 9696, 9999, 999, 200
MODE = os.environ.get('C096_MODE', 'main')
EXCL_PX = 250                 # paragraph-initial region excluded from H1/H2 (about one word at ~35 px per weight unit)
TALL = 1.6                    # tall component: height >= 1.6 x page median component height
MIN_TALL = 2                  # a line enters H1/H2 only with >= 2 tall components outside the excluded region
ASSIGN_DY = 25                # component bottom - 8 px must lie within +-25 px of the traced line centre
H_RNG, W_RNG, A_MIN, FILL = (8, 160), (4, 160), 30, (0.05, 0.70)
PLANT = 1.10                  # planted 10 % shift of the line statistic on fake-FIRST lines
ALPHA, ALPHA_POW = 0.05, 0.025
G0_FIRST, G0_OTHER, FPR_MAX, POW_MIN, ALIGN_RHO, ALIGN_P = 20, 60, 0.075, 0.80, 0.30, 0.01

def zl_lines(folio):
    raw = L.raw_lines(folio); first = []
    for line in open('data/ZL3b-n.txt', encoding='utf-8', errors='replace'):
        m = re.match(r'<(%s)\.(\d+),[@+=*&~-](\w+)>\s*(.*)' % folio, line.rstrip('\n'))
        if not m: continue
        t = m.group(4)
        g = re.sub(r'<[^>]*>', '', t); g = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', g); g = re.sub(r'[^a-z]', '', g)
        first.append(dict(first=t.lstrip().startswith('<%>'), gallows=sum(g.count(c) for c in 'ktpf')))
    assert len(first) == len(raw)
    return [dict(locus=r[0], weight=r[3], **f) for r, f in zip(raw, first)]

def trace(img, box):
    """C039 page_lines, plus the interpolated centre y per column (needed to assign components)."""
    x0, x1, y0, y1 = box
    im = Image.open(img).convert('L'); a = np.asarray(im, float)
    bg = np.asarray(im.filter(ImageFilter.GaussianBlur(L.BG_R)), float); ink = (bg - a) > L.INK_T
    ink[:y0] = 0; ink[y1:] = 0; ink[:, :x0] = 0; ink[:, x1:] = 0
    tr = L.page_lines(img, box)            # verbatim C039 traces (for matching)
    seed = L.peaks(ink[:, x0 + 60:x0 + 60 + L.SEED_W].sum(1))
    xs = list(range(x0 + 60, x1, L.STRIP)); spk = {x: L.peaks(ink[:, x:x + L.STRIP].sum(1)) for x in xs}
    yys = []
    for y in seed:                          # same loop as C039, keeping yy; kept only where C039 kept a line
        t_ = [(x0 + 60 + L.SEED_W / 2, y)]; cur = y
        for x in xs[2:]:
            c = [q for q in spk[x] if abs(q - cur) < L.TRACK]
            if c: cur = min(c, key=lambda q: abs(q - cur)); t_.append((x + L.STRIP / 2, cur))
        X_, Y_ = np.array([t[0] for t in t_]), np.array([t[1] for t in t_])
        cols = np.arange(x0, x1); yy = np.interp(cols, X_, Y_)
        band = np.array([ink[int(y_) + L.BAND[0]:int(y_) + L.BAND[1], c].sum() for c, y_ in zip(cols, yy)])
        on = np.flatnonzero(np.convolve(band > 0, np.ones(5), 'same') >= 3)
        if len(on) == 0: continue
        yys.append(yy)
    assert len(yys) == len(tr)
    for t, yy in zip(tr, yys): t['yy'] = yy
    return tr, ink, x0

def components(ink):
    lab, n = ndi.label(ink, structure=np.ones((3, 3), bool))
    sl = ndi.find_objects(lab); idx = np.arange(1, n + 1)
    area = ndi.sum_labels(ink, lab, idx); out = []
    for s, ar in zip(sl, area):
        h = s[0].stop - s[0].start; w = s[1].stop - s[1].start; fill = ar / max(h * w, 1)
        if H_RNG[0] <= h <= H_RNG[1] and W_RNG[0] <= w <= W_RNG[1] and ar >= A_MIN and FILL[0] <= fill <= FILL[1]:
            out.append((s[0].start, s[0].stop, s[1].start, s[1].stop))
    return out

def page(folio, img, box):
    zl = zl_lines(folio); tr, ink, x0 = trace(os.path.join(L.SCANS, img), box)
    pairs, ppw = L.match_lines(tr, L.raw_lines(folio))
    comps = components(ink)
    lines = [dict(t=tr[i], z=zl[j], comps=[]) for i, j in pairs]
    for (r0, r1, c0, c1) in comps:
        xc = (c0 + c1) // 2; yb = r1 - 8; best, bd = None, ASSIGN_DY + 1
        for k, ln in enumerate(lines):
            t = ln['t']
            if not (t['xa'] - 20 <= xc <= t['xb'] + 20): continue
            d = abs(yb - ln['t']['yy'][min(max(xc - x0, 0), len(ln['t']['yy']) - 1)])
            if d < bd: best, bd = k, d
        if best is not None: lines[best]['comps'].append((r1 - r0, c1 - c0, xc))
    hs = [h for ln in lines for h, _, _ in ln['comps']]
    h0 = float(np.median(hs)) if hs else float('nan')
    rows = []
    for ln in lines:
        t = ln['t']; tall_all = [(h, w, x) for h, w, x in ln['comps'] if h >= TALL * h0]
        tall = [(h, w, x) for h, w, x in tall_all if x >= t['xa'] + EXCL_PX]
        rows.append(dict(folio=folio, locus=ln['z']['locus'], first=bool(ln['z']['first']),
                         n_comps_line=len(ln['comps']), zl_weight=ln['z']['weight'], zl_gallows=ln['z']['gallows'],
                         n_tall_all=len(tall_all),
                         zl_gallows_per_w=ln['z']['gallows'] / max(ln['z']['weight'], 1),
                         tall_per_100px=100 * len(tall_all) / max(t['xb'] - t['xa'], 1), n_tall=len(tall),
                         Hm=float(np.median([h for h, _, _ in tall]) / h0) if len(tall) >= MIN_TALL else None,
                         Am=float(np.median([w / h for h, w, _ in tall])) if len(tall) >= MIN_TALL else None))
    return dict(h0=h0, traces=len(tr), zl_lines=len(zl), matched=len(pairs), n_comps=len(comps), px_per_weight=ppw), rows

def dstat(x, lab): return x[lab].mean() - x[~lab].mean()

def perm_p(x, lab, pg, rng, R):
    d0 = dstat(x, lab); cnt = 0; groups = [np.flatnonzero(pg == p) for p in np.unique(pg)]
    for _ in range(R):
        l2 = lab.copy()
        for g in groups: l2[g] = rng.permutation(lab[g])
        cnt += abs(dstat(x, l2)) >= abs(d0) - 1e-12
    return d0, (1 + cnt) / (R + 1)

def holm(ps):
    o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for r, i in enumerate(o): run = max(run, min(1, (m - r) * ps[i])); adj[i] = run
    return adj.tolist()

def gates(rows, stat, rng):
    oth = [r for r in rows if not r['first'] and r[stat] is not None]
    nfirst = {}
    for r in rows:
        if r['first'] and r[stat] is not None: nfirst[r['folio']] = nfirst.get(r['folio'], 0) + 1
    x = np.array([r[stat] for r in oth]); pg = np.array([r['folio'] for r in oth])
    fp = pw = 0
    for _ in range(N_GATE):
        lab = np.zeros(len(x), bool)
        for f, k in nfirst.items():
            g = np.flatnonzero(pg == f); lab[rng.choice(g, min(k, len(g) // 2), replace=False)] = True
        _, p = perm_p(x, lab, pg, rng, R_GATE); fp += p < ALPHA
        xp = x.copy(); xp[lab] *= PLANT; _, p2 = perm_p(xp, lab, pg, rng, R_GATE); pw += p2 < ALPHA_POW
    sd = float(np.std(x, ddof=1))
    return dict(n_other=len(x), first_per_page=nfirst, fpr=fp / N_GATE, power=pw / N_GATE,
                fpr_ok=fp / N_GATE <= FPR_MAX, power_ok=pw / N_GATE >= POW_MIN, sd_other=sd,
                plant_abs=float((PLANT - 1) * np.mean(x)))

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); pages, rows = {}, []
    for f, (img, box) in L.PAGES.items():
        info, r = page(f, img, box); info['image'] = img; info['box'] = box; pages[f] = info; rows += r
        print(f, json.dumps(info, default=lambda o: o.item()), flush=True)
    a = np.array([r['tall_per_100px'] for r in rows]); b = np.array([r['zl_gallows_per_w'] for r in rows])
    rho, prho = stats.spearmanr(a, b)
    align = dict(rho=float(rho), p=float(prho), n=len(rows), ok=bool(rho >= ALIGN_RHO and prho < ALIGN_P))
    reach = dict(first_valid=sum(r['first'] and r['Hm'] is not None for r in rows),
                 other_valid=sum((not r['first']) and r['Hm'] is not None for r in rows),
                 first_matched=sum(r['first'] for r in rows), other_matched=sum(not r['first'] for r in rows))
    reach['ok'] = reach['first_valid'] >= G0_FIRST and reach['other_valid'] >= G0_OTHER
    G = {s: gates(rows, s, rng) for s in ('Hm', 'Am')}
    out = dict(mode=MODE, seed=SEED, pages=pages, alignment=align, reach=reach, gates=G)
    print('ALIGN', json.dumps(align, default=lambda o: o.item())); print('REACH', json.dumps(reach, default=lambda o: o.item())); print('GATES', json.dumps(G, default=lambda o: o.item()), flush=True)
    if MODE == 'diag':
        D = {}
        for f in list(pages) + ['ALL']:
            v = [r for r in rows if f == 'ALL' or r['folio'] == f]
            c1 = stats.spearmanr([r['n_comps_line'] for r in v], [r['zl_weight'] for r in v])
            c2 = stats.spearmanr([r['n_tall_all'] for r in v], [r['zl_gallows'] for r in v])
            D[f] = dict(n=len(v), rho_comps_vs_weight=float(c1[0]), p1=float(c1[1]),
                        rho_tall_vs_gallows=float(c2[0]), p2=float(c2[1]))
        out['D1'] = D; print('D1', json.dumps(D, default=lambda o: o.item()))
    if MODE == 'main':
        run = {s: align['ok'] and reach['ok'] and G[s]['fpr_ok'] and G[s]['power_ok'] for s in ('Hm', 'Am')}
        tests = {}
        for s in ('Hm', 'Am'):
            v = [r for r in rows if r[s] is not None]
            x = np.array([r[s] for r in v]); lab = np.array([r['first'] for r in v]); pg = np.array([r['folio'] for r in v])
            d, p = perm_p(x, lab, pg, rng, R_MAIN)
            tests[s] = dict(runnable=run[s], D=float(d), p=float(p), mean_first=float(x[lab].mean()),
                            mean_other=float(x[~lab].mean()), n_first=int(lab.sum()), n_other=int((~lab).sum()))
        live = [s for s in tests if tests[s]['runnable']]
        adj = holm([tests[s]['p'] for s in live]) if live else []
        for s, q in zip(live, adj):
            tests[s]['holm'] = q
            tests[s]['verdict'] = ('DIFFERENT (' + ('higher' if tests[s]['D'] > 0 else 'lower') + ' on FIRST lines)') if q < ALPHA else 'NOT DETECTED at this power'
        for s in tests:
            if not tests[s]['runnable']: tests[s]['verdict'] = 'NOT TESTABLE (gate failed); value descriptive only'
        fr = np.array([r['first'] for r in rows])
        desc = dict(tall_per_100px_first=float(a[fr].mean()), tall_per_100px_other=float(a[~fr].mean()),
                    zl_gallows_per_w_first=float(b[fr].mean()), zl_gallows_per_w_other=float(b[~fr].mean()))
        out.update(tests=tests, descriptive=desc, rows=rows)
        print('TESTS', json.dumps(tests, default=lambda o: o.item())); print('DESC', json.dumps(desc, default=lambda o: o.item()))
    out['seconds'] = round(time.time() - t0, 1)
    fn = {'rehearsal': 'analysis/C096_rehearsal.json', 'diag': 'analysis/C096_diag.json'}.get(MODE, 'analysis/C096_results.json')
    if MODE != 'main': out.pop('rows', None)
    json.dump(out, open(fn, "w"), indent=1, default=lambda o: o.item()); print('wrote', fn, out['seconds'], 's')

if __name__ == '__main__':
    main()
