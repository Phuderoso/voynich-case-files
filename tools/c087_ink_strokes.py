#!/usr/bin/env python3
"""C087 (NEW FAMILY F-INK: pen-stroke morphology measured on the Beinecke MS 408 scans).
Question: do two page-level image measures -- stroke width W (px) and glyph-component height G (px) of text-like ink
components -- differ between the scribal hands that ZL 3b's page headers record ($H, after L. Fagin Davis 2020), on herbal
pages (ZL $I=H)?  C1: hand 1 (Currier A) vs hand 2 (Currier B).  C2: inside Currier B herbal pages, hand 2 vs hands 3+5
(language held fixed).  Pre-registered in case-file/C087-ink-strokes.md. Analysis seed 8787.
numpy + PIL; scipy.ndimage (labelling only) from a venv: /workspace/voynich/venv87 (scipy 1.18.1, numpy 2.5.4).
Modes:  C087_MODE=smoke  -> estimator checks on the non-herbal smoke pages only (f58r, f103r, f111r) + synthetic gate rehearsal
        C087_MODE=main   -> the pre-registered run
Run: OMP_NUM_THREADS=1 timeout 600 /workspace/voynich/venv87/bin/python tools/c087_ink_strokes.py
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import os, re, sys, json, time, hashlib
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

SEED = 8787
SCANS = os.environ.get('VOY_SCANS', '/workspace/voynich/scans')
MODE = os.environ.get('C087_MODE', 'main')
INK_T, BG_R = 30, 25                          # C039 ink rule: blur(25) background - pixel > 30
H_RNG, W_RNG, A_MIN, FILL = (12, 90), (4, 120), 30, (0.08, 0.60)
NB_DY, NB_DX, NB_MIN = 15, 300, 3             # line context: >= 3 other kept comps within +-15 px (y) and +-300 px (x)
MIN_COMPS = 150                               # page dropped if fewer kept components
R_PERM, N_FP, N_PLANT = 9999, 40, 10
DELTAS = (0.5, 0.75, 1.0, 1.5)                # plant sizes in pooled page-SD units
ALPHA = 0.05
SMOKE = {'f58r': '115_f58r.jpg', 'f103r': '183_f103r.jpg', 'f111r': '195_f111r.jpg'}

def headers():
    out = {}
    for l in open('data/ZL3b-n.txt', encoding='utf-8', errors='replace'):
        m = re.match(r'<(f\w+)>\s*<!(.*)>', l)
        if m: out[m.group(1)] = dict(re.findall(r'\$(\w)=(\w+)', m.group(2)))
    return out

def scanfile(folio):
    for f in os.listdir(SCANS):
        if re.fullmatch(r'\d+_%s\.jpg' % folio, f): return f
    return None

def ink_mask(img, scale=1.0, t=INK_T):
    im = Image.open(img).convert('L')
    if scale != 1.0: im = im.resize((int(im.width * scale), int(im.height * scale)), Image.BICUBIC)
    a = np.asarray(im, np.float32); bg = np.asarray(im.filter(ImageFilter.GaussianBlur(BG_R)), np.float32)
    return (bg - a) > t

def measure(ink, hscale=1.0):
    """W = median over kept components of 2*area/boundary; G = median component height. Size rules scale with hscale."""
    lab, n = ndi.label(ink, structure=np.ones((3, 3), bool))
    if n == 0: return None
    sl = ndi.find_objects(lab)
    hh = np.array([s[0].stop - s[0].start for s in sl]); ww = np.array([s[1].stop - s[1].start for s in sl])
    yc = np.array([(s[0].stop + s[0].start) / 2 for s in sl]); xc = np.array([(s[1].stop + s[1].start) / 2 for s in sl])
    idx = np.arange(1, n + 1)
    area = ndi.sum_labels(ink, lab, idx)
    bnd = ink & ~ndi.binary_erosion(ink, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
    bcount = ndi.sum_labels(bnd, lab, idx)
    fill = area / np.maximum(hh * ww, 1)
    k = ((hh >= H_RNG[0] * hscale) & (hh <= H_RNG[1] * hscale) & (ww >= W_RNG[0] * hscale) & (ww <= W_RNG[1] * hscale)
         & (area >= A_MIN * hscale ** 2) & (fill >= FILL[0]) & (fill <= FILL[1]) & (bcount > 0))
    ki = np.flatnonzero(k)
    if len(ki) == 0: return None
    o = ki[np.argsort(yc[ki])]; ys, xs = yc[o], xc[o]; keep = np.zeros(len(o), bool)
    for j in range(len(o)):
        lo, hi = np.searchsorted(ys, ys[j] - NB_DY * hscale), np.searchsorted(ys, ys[j] + NB_DY * hscale, 'right')
        keep[j] = (np.abs(xs[lo:hi] - xs[j]) <= NB_DX * hscale).sum() - 1 >= NB_MIN
    o = o[keep]
    if len(o) == 0: return None
    W = 2 * area[o] / bcount[o]
    return dict(W=float(np.median(W)), G=float(np.median(hh[o])), n=int(len(o)))

def page(folio, f, t=INK_T):
    return measure(ink_mask(os.path.join(SCANS, f), t=t))

def dstat(x, lab):
    return np.median(x[lab]) - np.median(x[~lab])

def perm_p(x, lab, rng, R=R_PERM):
    d0 = dstat(x, lab); n1 = lab.sum(); N = len(x); ge = le = 0; ab = 0
    for _ in range(R):
        p = np.zeros(N, bool); p[rng.choice(N, n1, replace=False)] = True; d = dstat(x, p)
        ge += d >= d0 - 1e-12; le += d <= d0 + 1e-12; ab += abs(d) >= abs(d0) - 1e-12
    return d0, (ab + 1) / (R + 1), (ge + 1) / (R + 1), (le + 1) / (R + 1)

def holm(ps):
    o = np.argsort(ps); m = len(ps); adj = np.zeros(m); run = 0
    for r, i in enumerate(o): run = max(run, min(1, (m - r) * ps[i])); adj[i] = run
    return adj

def gate_sims(x_null, n1, rng, alpha_eff):
    """on true-null values x_null (one hand only): FP for iid fake labels, FP for contiguous-block fake labels (folio
    order), and plant power per delta (iid fake labels + shift delta*SD)"""
    N = len(x_null); sd = np.std(x_null, ddof=1); R = 999
    def p_of(x, lab): return perm_p(x, lab, rng, R)[1]
    fp_iid = fp_blk = 0
    for _ in range(N_FP):
        lab = np.zeros(N, bool); lab[rng.choice(N, n1, replace=False)] = True; fp_iid += p_of(x_null, lab) < alpha_eff
        s = rng.integers(0, N - n1 + 1); lab = np.zeros(N, bool); lab[s:s + n1] = True; fp_blk += p_of(x_null, lab) < alpha_eff
    power = {}
    for dl in DELTAS:
        hit = 0
        for _ in range(N_PLANT):
            lab = np.zeros(N, bool); lab[rng.choice(N, n1, replace=False)] = True
            hit += p_of(x_null + dl * sd * lab, lab) < alpha_eff
        power[dl] = hit
    return dict(fp_iid=fp_iid, fp_blk=fp_blk, power=power, n_null=N, n1=n1)

def smoke():
    R = dict(mode='smoke', pages={})
    for fo, f in SMOKE.items():
        base = measure(ink_mask(os.path.join(SCANS, f)))
        up = measure(ink_mask(os.path.join(SCANS, f), scale=1.10), hscale=1.10)
        dil = measure(ndi.binary_dilation(ink_mask(os.path.join(SCANS, f)), structure=np.ones((3, 3), bool)))
        R['pages'][fo] = dict(base=base, up110=up, dil1=dil,
                              G_ratio=up['G'] / base['G'], W_ratio=up['W'] / base['W'], dW_dil=dil['W'] - base['W'])
        print(fo, R['pages'][fo], flush=True)
    # synthetic rehearsal of the permutation gates on interchangeable draws (iid normal, AR(1) drift), class sizes as design
    rng = np.random.default_rng(SEED + 1); reh = {}
    for name, (N, n1) in dict(C1=(95, 20), C2=(20, 12)).items():
        for kind in ('iid', 'ar1'):
            z = rng.normal(size=N)
            if kind == 'ar1':
                for i in range(1, N): z[i] = 0.7 * z[i - 1] + np.sqrt(1 - 0.49) * z[i]
            reh['%s_%s' % (name, kind)] = gate_sims(z, min(n1, N // 2), rng, ALPHA / 4)
            print(name, kind, reh['%s_%s' % (name, kind)], flush=True)
    R['rehearsal'] = reh
    json.dump(R, open("analysis/C087_smoke.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))

def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); H = headers()
    herb = [(fo, d) for fo, d in H.items() if d.get('I') == 'H' and d.get('H') in ('1', '2', '3', '5') and scanfile(fo)]
    R = dict(mode='main', seed=SEED, ink_t=INK_T, pages={}, dropped=[], files={})
    for fo, d in herb:
        f = scanfile(fo); R['files'][fo] = f
        R.setdefault('sha256_16', {})[fo] = hashlib.sha256(open(os.path.join(SCANS, f), 'rb').read()).hexdigest()[:16]
        m = page(fo, f)
        if m is None or m['n'] < MIN_COMPS: R['dropped'].append(fo); continue
        m.update(hand=d['H'], lang=d.get('L')); R['pages'][fo] = m
    print('measured', len(R['pages']), 'dropped', R['dropped'], round(time.time() - t0), 's', flush=True)
    json.dump(R, open("analysis/C087_results.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    fos = list(R['pages']); P = R['pages']
    sets = dict(C1=([f for f in fos if P[f]['hand'] == '2'], [f for f in fos if P[f]['hand'] == '1']),
                C2=([f for f in fos if P[f]['hand'] in ('3', '5') and P[f]['lang'] == 'B'], [f for f in fos if P[f]['hand'] == '2' and P[f]['lang'] == 'B']))
    tests, ps = [], []
    for c, (g1, g0) in sets.items():
        order = [f for f in fos if f in g1 or f in g0]            # folio (file) order
        lab = np.array([f in g1 for f in order])
        for met in ('W', 'G'):
            x = np.array([P[f][met] for f in order])
            d0, p2, pge, ple = perm_p(x, lab, rng)
            tests.append(dict(contrast=c, metric=met, n1=int(lab.sum()), n0=int((~lab).sum()), D=float(d0),
                              med1=float(np.median(x[lab])), med0=float(np.median(x[~lab])), sd_pool=float(np.std(x, ddof=1)),
                              p_two=p2, p_ge=pge, p_le=ple)); ps.append(p2)
            print(tests[-1], flush=True)
    adj = holm(np.array(ps))
    for t, a in zip(tests, adj): t['p_holm'] = float(a)
    # gates: on the larger class only (true null for hand), same n1 as the contrast
    for t in tests:
        g1, g0 = sets[t['contrast']]; x0 = np.array([P[f][t['metric']] for f in fos if f in g0])
        t['gates'] = gate_sims(x0, min(t['n1'], len(x0) // 2), rng, ALPHA / 4)
        print(t['contrast'], t['metric'], t['gates'], round(time.time() - t0), 's', flush=True)
    R.update(tests=tests); json.dump(R, open('analysis/C087_results.json', 'w'), indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))  # checkpoint
    # sensitivity (pre-registered, cannot change verdicts): ink threshold 20 and 40, D only
    sens = {}
    for tt in (20, 40):
        Q = {}
        for fo in fos:
            m = page(fo, R['files'][fo], t=tt)
            if m: Q[fo] = m
        for c, (g1, g0) in sets.items():
            for met in ('W', 'G'):
                a1 = [Q[f][met] for f in g1 if f in Q]; a0 = [Q[f][met] for f in g0 if f in Q]
                sens['%s_%s_T%d' % (c, met, tt)] = float(np.median(a1) - np.median(a0))
        print('sens', tt, round(time.time() - t0), 's', flush=True)
    R.update(tests=tests, sensitivity=sens, seconds=round(time.time() - t0))
    json.dump(R, open("analysis/C087_results.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))

if __name__ == '__main__':
    smoke() if MODE == 'smoke' else main()
