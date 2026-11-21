#!/usr/bin/env python3
"""i342_subsample.py -- PREREGISTERED subsample test for Kryptos's I-342 (bar as a function of nq and maybe ln N).
Voynich desk, 2026-11-21.  See PREREG.md (same folder).  Modes:
  gates                      synthetic gates (plants built on the real cells' structure fields only; max= and pass= are NOT read)
  real  --i-froze-prereg     the real run on the c229 Y lines (refuses without the flag)
Input unit = a Y cell (null text, file family, model, p, nq, n, pass, max) from Kryptos's data/cycle229/R (16 nulls).
A 'draw' = a random subset of whole cells (cells cannot be split: the Y line only keeps n and the max) inside one pool
(family x nq window, or all families x nq window) taken in random order until the running total of decipherments N >= level L
(only cells with n <= L are eligible); its max NC is the max of the cell maxima, so the draw max is exact for the union.
"""
import re, glob, os, sys, json, hashlib, math, argparse, time
import numpy as np
from scipy.stats import norm
from multiprocessing import Pool

DEF_R = '/workspace/k229-nq-vs-search-size/kryptos-main/data/cycle229/R'
FAMS = ['bank_V_a', 'bank_V_b', 'all_V_a', 'all_V_b', 'bank_Q_r10', 'all_Q_r10']
WINS = [(10, 12), (13, 16), (17, 22), (23, 30), (31, 40)]
LEVELS = [10, 30, 100, 300, 1000]
BAR = -6.0
ALPHA = 0.05
M_TESTS = 4
DELTA_B = 0.05 / math.log(10)   # per unit ln N: a decade of N moves the null max by >= 0.05 NC
DELTA_C = 0.01                  # per quadgram: five quadgrams move the null max by >= 0.05 NC
M_B, M_C = DELTA_B / 4, DELTA_C / 4   # composition margins: a quarter of the materiality unit
SEEDS = dict(primary=11850, fresh=11851, halfA=11852, halfB=11853, gate_P0=11854, gate_P1=11855, gate_THIN=11856)
HALF_A = list(range(209559, 209567)); HALF_B = list(range(209567, 209575))
R_POINT, R_BOOT, B_PRIMARY, B_HALF = 2000, 200, 1000, 500
GATE_R_POINT, GATE_R_BOOT = 400, 100
PAT = re.compile(r'^Y model=(\w) p=(\d+) nq=(\d+) n=(\d+) pass=(\d+) max=(\S+)$')
MU0, SIG0 = -7.2, 1.1
PLANTS = dict(  # per-decipherment NC ~ Normal(mu_f, sig^2/nq); family offsets for the composition plant, thin tail for the negligible-effect plant
    P0=dict(off=[0, 0, 0, 0, 0, 0], sig=SIG0),
    P1=dict(off=[-0.40, -0.40, -0.20, -0.20, 0.50, 0.70], sig=SIG0),
    THIN=dict(off=[0, 0, 0, 0, 0, 0], sig=0.15))

# ------------------------------------------------------------------ loading
def load(rdir, with_nc):
    rows = []
    for f in sorted(glob.glob(rdir + '/null*.txt')):
        m = re.match(r'^null(\d+)_(.+)\.txt$', os.path.basename(f))
        seed, fam = int(m.group(1)), m.group(2)
        if fam not in FAMS: continue            # direct_* has no Y hits
        for l in open(f):
            if not l.startswith('Y '): continue
            g = PAT.match(l.strip()); assert g, l
            nq, n = int(g.group(3)), int(g.group(4))
            w = next((i for i, (a, b) in enumerate(WINS) if a <= nq <= b), -1)
            if w < 0: continue
            mx = float(g.group(6)) if with_nc else float('nan')   # gate mode never parses max=
            rows.append((seed, FAMS.index(fam), int(g.group(2)), nq, n, w, mx, int(g.group(5)) if with_nc else 0))
    a = np.array(rows, float)
    return dict(seed=a[:, 0].astype(int), fam=a[:, 1].astype(int), p=a[:, 2].astype(int), nq=a[:, 3].astype(int),
                n=a[:, 4].astype(int), w=a[:, 5].astype(int), mx=a[:, 6], k=a[:, 7].astype(int))

def verify_sums(rdir):
    base = os.path.dirname(rdir); bad = 0; seen = 0
    for l in open(base + '/SHA256SUMS'):
        h, p = l.split(); p = p[2:] if p.startswith('./') else p
        if not p.startswith('R/'): continue
        fp = base + '/' + p
        if not os.path.exists(fp): continue
        seen += 1
        if hashlib.sha256(open(fp, 'rb').read()).hexdigest() != h: bad += 1
    return seen, bad

def sub(C, idx): return {k: v[idx] for k, v in C.items()}

# ------------------------------------------------------------------ draws
def draws(C, rng, R):
    """returns dict of arrays: design (0 STRAT, 1 POOL), fam (-1 for POOL), w, L, N, nq, mx"""
    out = {k: [] for k in ('design', 'fam', 'w', 'L', 'N', 'nq', 'mx')}
    for design in (0, 1):
        for f in (range(len(FAMS)) if design == 0 else [-1]):
            for w in range(len(WINS)):
                m = (C['w'] == w) & ((C['fam'] == f) if f >= 0 else True)
                if not m.any(): continue
                n_, q_, x_ = C['n'][m], C['nq'][m], C['mx'][m]
                for L in LEVELS:
                    e = n_ <= L
                    if e.sum() < 5 or n_[e].sum() < 3 * L: continue
                    ne, qe, xe = n_[e].astype(float), q_[e].astype(float), x_[e]
                    o = np.argsort(rng.random((R, len(ne))), axis=1)
                    nn = ne[o]; cum = np.cumsum(nn, 1); k = (cum >= L).argmax(1)
                    ar = np.arange(R); pos = np.arange(len(ne))[None, :] <= k[:, None]
                    N = cum[ar, k]
                    mx = np.where(pos, xe[o], -np.inf).max(1)
                    nqd = (np.where(pos, nn * qe[o], 0)).sum(1) / np.where(pos, nn, 0).sum(1)
                    out['design'] += [np.full(R, design)]; out['fam'] += [np.full(R, f)]; out['w'] += [np.full(R, w)]
                    out['L'] += [np.full(R, L)]; out['N'] += [N]; out['nq'] += [nqd]; out['mx'] += [mx]
    return {k: np.concatenate(v) for k, v in out.items()}

# ------------------------------------------------------------------ fixed-effect slopes
def _demean(g, *cols):
    u, inv = np.unique(g, return_inverse=True); cnt = np.bincount(inv)
    return [c - (np.bincount(inv, weights=c) / cnt)[inv] for c in cols]

def _supported(g, key, need=3):
    """keep draws whose group g has >= need distinct values of key"""
    u, inv = np.unique(g, return_inverse=True)
    pair = np.unique(np.stack([inv, key], 1), axis=0)
    cnt = np.bincount(pair[:, 0], minlength=len(u))
    return cnt[inv] >= need

def slope_b(D, sel, y):
    """search-size effect at fixed nq window and fixed pool: FE (design,fam,w), covariate ln N"""
    g = D['design'][sel] * 1000 + (D['fam'][sel] + 1) * 10 + D['w'][sel]
    ok = _supported(g, D['L'][sel]); 
    if ok.sum() < 10: return float('nan')
    x, yy = _demean(g[ok], np.log(D['N'][sel][ok]), y[sel][ok])
    return float((x @ yy) / (x @ x))

def slope_c(D, sel, y):
    """length effect at fixed N level and fixed pool: FE (design,fam,L), covariates nq and ln N (overshoot control); coefficient of nq"""
    g = D['design'][sel] * 1000 + (D['fam'][sel] + 1) * 10 + np.searchsorted(LEVELS, D['L'][sel])
    ok = _supported(g, D['w'][sel])
    if ok.sum() < 10: return float('nan')
    q, ln, yy = _demean(g[ok], D['nq'][sel][ok], np.log(D['N'][sel][ok]), y[sel][ok])
    X = np.stack([q, ln], 1); beta = np.linalg.lstsq(X, yy, rcond=None)[0]
    return float(beta[0])

def joint(D, sel, y):
    """descriptive M3 inside STRAT: FE family, y ~ ln N + nq"""
    g = D['fam'][sel]
    ln, q, yy = _demean(g, np.log(D['N'][sel]), D['nq'][sel], y[sel])
    X = np.stack([ln, q], 1); beta = np.linalg.lstsq(X, yy, rcond=None)[0]
    return float(beta[0]), float(beta[1])

def estimates(D, y=None):
    y = D['mx'] if y is None else y
    S = D['design'] == 0; P = D['design'] == 1
    e = dict(bA_S=slope_b(D, S, y), bA_P=slope_b(D, P, y), cB_S=slope_c(D, S, y), cB_P=slope_c(D, P, y))
    e['dB'] = e['bA_P'] - e['bA_S']; e['dC'] = e['cB_P'] - e['cB_S']
    e['th'] = [e['bA_S'], -e['cB_S'], abs(e['dB']), abs(e['dC'])]
    return e

def per_family(D):
    out = []
    for f in range(len(FAMS)):
        s = (D['design'] == 0) & (D['fam'] == f)
        if s.sum() < 10: out.append((float('nan'),) * 2); continue
        out.append((slope_b(D, s, D['mx']), slope_c(D, s, D['mx'])))
    return out

THR = [DELTA_B, DELTA_C, M_B, M_C]
TEST_NAMES = ['T1 search-size slope b_A (STRAT) vs delta_b', 'T2 length slope -c_B (STRAT) vs delta_c',
              'T3 composition effect on b: |b_A(POOL)-b_A(STRAT)| vs margin m_b', 'T4 composition effect on c: |c_B(POOL)-c_B(STRAT)| vs margin m_c']

# ------------------------------------------------------------------ bootstrap over nulls
def _boot_one(args):
    C, seed_seq, nulls, R = args
    rng = np.random.default_rng(seed_seq)
    pick = rng.choice(nulls, size=len(nulls), replace=True)
    idx = np.concatenate([np.flatnonzero(C['seed'] == s) for s in pick])
    return estimates(draws(sub(C, idx), rng, R))['th']

def run_boot(C, nulls, seed, B, R_b, procs=8):
    Cn = sub(C, np.flatnonzero(np.isin(C['seed'], nulls)))
    ss = np.random.SeedSequence(seed).spawn(B + 1)
    rng0 = np.random.default_rng(ss[0])
    point = estimates(draws(Cn, rng0, R_POINT))
    with Pool(procs) as pl:
        th = np.array(pl.map(_boot_one, [(Cn, ss[i + 1], nulls, R_b) for i in range(B)], chunksize=4))
    return point, th

def pvals(point_th, th_boot):
    p, side = [], []
    for i in range(M_TESTS):
        t = th_boot[:, i]; t = t[~np.isnan(t)]; d = THR[i]
        lo = (1 + np.sum(t <= d)) / (len(t) + 1); hi = (1 + np.sum(t >= d)) / (len(t) + 1)
        p.append(min(1.0, 2 * min(lo, hi))); side.append(int(np.sign(point_th[i] - d)))
    return p, side

def holm(p, alpha=ALPHA):
    m = len(p); order = np.argsort(p); rej = [False] * m; thr = [0.0] * m; stop = False
    for r, i in enumerate(order):
        thr[i] = alpha / (m - r)
        if not stop and p[i] <= thr[i]: rej[i] = True
        else: stop = True
    return rej, thr

def distance(p, thr, rej):
    return thr / p if rej else p / thr

def wilson(k, n, z=1.959964):
    if n == 0: return (float('nan'),) * 2
    ph = k / n; den = 1 + z * z / n; c = (ph + z * z / (2 * n)) / den
    h = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)

# ------------------------------------------------------------------ expected max of N std normals (for the oracle in gates)
_ZG = np.linspace(-9, 9, 36001)
def _emax_table():
    lg = np.linspace(0, math.log(3e5), 120); out = []
    cdf = norm.cdf(_ZG); pdf = norm.pdf(_ZG)
    for l in lg:
        N = math.exp(l); out.append(np.trapezoid(_ZG * N * pdf * np.exp((N - 1) * np.log(np.clip(cdf, 1e-300, 1))), _ZG))
    return lg, np.array(out)
_LG, _EM = _emax_table()
def emax(N): return np.interp(np.log(N), _LG, _EM)

def synth_mx(C, plant, rng):
    P = PLANTS[plant]; off = np.array(P['off'])[C['fam']]
    sd = P['sig'] / np.sqrt(C['nq']); mu = MU0 + off
    U = rng.random(len(C['n']))
    q = -np.expm1(np.log(U) / C['n'])      # 1 - U^(1/n)
    return mu + sd * norm.isf(np.clip(q, 1e-300, 1))

def oracle_y(D, plant):
    """expected draw max under the plant (max of N normals; exact for the formula, nq taken as the draw's weighted mean)"""
    off = np.array(PLANTS[plant]['off']); f = np.clip(D['fam'], 0, None)
    return MU0 + off[f] + PLANTS[plant]['sig'] / np.sqrt(D['nq']) * emax(D['N'])

# ------------------------------------------------------------------ gates
def _gate_rep(args):
    plant, rep, Cs, B, procs = args
    rng = np.random.default_rng([SEEDS['gate_' + plant], rep])
    C = dict(Cs); C['mx'] = synth_mx(C, plant, rng)
    nulls = sorted(set(C['seed'].tolist()))
    ss = np.random.SeedSequence([SEEDS['gate_' + plant], rep, 7]).spawn(B + 1)
    D = draws(C, np.random.default_rng(ss[0]), GATE_R_POINT)
    point = estimates(D)
    orc = estimates(D, y=oracle_y(D, plant))
    th = np.array([_boot_one((C, ss[i + 1], nulls, GATE_R_BOOT)) for i in range(B)])
    p, side = pvals(point['th'], th)
    return dict(plant=plant, rep=rep, point=point, oracle=orc, p=p, side=side)

def run_gates(rdir, B=200, procs=8, reps=20):
    Cs = load(rdir, with_nc=False)
    res = {}
    for plant in ('P0', 'P1', 'THIN'):
        with Pool(procs) as pl:
            res[plant] = pl.map(_gate_rep, [(plant, r, Cs, B, 1) for r in range(reps)], chunksize=1)
    return res

def summarize_gates(res, reps=20):
    L = []; ok = True
    def line(s): L.append(s); print(s, flush=True)
    mat = lambda r, i: (r['p'][i] <= 0.05 and r['side'][i] > 0)     # theta significantly ABOVE its threshold
    neg = lambda r, i: (r['p'][i] <= 0.05 and r['side'][i] < 0)     # theta significantly BELOW its threshold
    for t, nm in ((2, 'T3'), (3, 'T4')):   # G1: no composition (P0): a 'material composition effect' must be rare
        k = sum(mat(r, t) for r in res['P0']); lo, hi = wilson(k, reps)
        g = k <= 3; ok &= g; line(f'G1 FPR {nm} on P0 (no composition): material-composition call {k}/{reps}, Wilson95 [{lo:.2f},{hi:.2f}]  gate <=3/20: {"PASS" if g else "FAIL"}')
    kb = sum(mat(r, 2) for r in res['P1']); kc = sum(mat(r, 3) for r in res['P1'])   # G2: composition plant
    ka = sum(mat(r, 2) or mat(r, 3) for r in res['P1']); lo, hi = wilson(ka, reps)
    g = ka >= 17; ok &= g
    line(f'G2 POW on P1 (composition plant): T3 {kb}/{reps}, T4 {kc}/{reps}, either {ka}/{reps}, Wilson95 [{lo:.2f},{hi:.2f}]  gate either>=17/20: {"PASS" if g else "FAIL"}')
    for plant in ('P0', 'P1', 'THIN'):      # G3: recovery vs oracle on the same draws (stratified estimates)
        kb = sum(abs(r['point']['bA_S'] - r['oracle']['bA_S']) <= 0.010 for r in res[plant])
        kc = sum(abs(r['point']['cB_S'] - r['oracle']['cB_S']) <= 0.005 for r in res[plant])
        g = kb >= 18 and kc >= 18; ok &= g
        mb = np.mean([r['point']['bA_S'] - r['oracle']['bA_S'] for r in res[plant]]); mc = np.mean([r['point']['cB_S'] - r['oracle']['cB_S'] for r in res[plant]])
        line(f'G3 REC {plant}: |b_A-oracle|<=0.010 in {kb}/{reps} (mean err {mb:+.4f}), |c_B-oracle|<=0.005 in {kc}/{reps} (mean err {mc:+.4f})  gate both>=18/20: {"PASS" if g else "FAIL"}')
    ob = np.mean([r['oracle']['bA_S'] for r in res['P0']]); oc = np.mean([-r['oracle']['cB_S'] for r in res['P0']])
    k1 = sum(mat(r, 0) for r in res['P0']); g = k1 >= 17; ok &= g      # G4: classification power, big effect (oracle b_A %.3f > delta_b, -c_B %.4f)
    line(f'G4 CLASS P0 (oracle b_A {ob:.4f} vs delta_b {DELTA_B:.4f}; -c_B {oc:.4f} vs delta_c {DELTA_C:.4f}): T1 MATERIAL {k1}/{reps}, T2 MATERIAL {sum(mat(r, 1) for r in res["P0"])}/{reps} (descriptive: -c_B is only {oc/DELTA_C:.2f}x delta_c)  gate T1 MATERIAL>=17/20: {"PASS" if g else "FAIL"}')
    ob = np.mean([r['oracle']['bA_S'] for r in res['THIN']]); oc = np.mean([-r['oracle']['cB_S'] for r in res['THIN']])
    n1 = sum(neg(r, 0) for r in res['THIN']); n2 = sum(neg(r, 1) for r in res['THIN']); f1 = sum(mat(r, 0) or mat(r, 1) for r in res['THIN'])
    g = n1 >= 17 and n2 >= 17 and f1 <= 3; ok &= g       # G5: classification of a negligible effect
    line(f'G5 CLASS THIN (oracle b_A {ob:.4f}, -c_B {oc:.4f}, both below thresholds): T1 NEGLIGIBLE {n1}/{reps}, T2 NEGLIGIBLE {n2}/{reps}, false MATERIAL {f1}/{reps}  gate both>=17/20 and false<=3/20: {"PASS" if g else "FAIL"}')
    line('GATES ' + ('ALL PASS' if ok else 'NOT ALL PASS'))
    return ok, L

# ------------------------------------------------------------------ real run
def passrates(C, nulls):
    rows = []
    for f in range(len(FAMS)):
        for w, (a, b) in enumerate(WINS):
            m = (C['fam'] == f) & (C['w'] == w); hit = set(C['seed'][m & (C['mx'] >= BAR)].tolist())
            k = len(hit & set(nulls)); lo, hi = wilson(k, len(nulls))
            rows.append((FAMS[f], f'{a}-{b}', int(C['n'][m].sum()), int(m.sum()), k, len(nulls), round(lo, 3), round(hi, 3), round(float(C['mx'][m].max()), 3) if m.any() else float('nan')))
    for w, (a, b) in enumerate(WINS):
        m = (C['w'] == w); hit = set(C['seed'][m & (C['mx'] >= BAR)].tolist()); k = len(hit & set(nulls)); lo, hi = wilson(k, len(nulls))
        rows.append(('ALL(overlap not de-duplicated)', f'{a}-{b}', int(C['n'][m].sum()), int(m.sum()), k, len(nulls), round(lo, 3), round(hi, 3), round(float(C['mx'][m].max()), 3)))
    return rows

def m3_vs_m4(D):
    S = D['design'] == 0; f = D['fam'][S]; y = D['mx'][S]; N = D['N'][S]; q = D['nq'][S]
    yy, ln, qq, ev = _demean(f, y, np.log(N), q, np.sqrt(2 * np.log(N)) / np.sqrt(q))
    sst = float(yy @ yy); out = {}
    X = np.stack([ln, qq], 1); b = np.linalg.lstsq(X, yy, rcond=None)[0]; out['M3_lnN_nq_FEfam'] = dict(b_lnN=float(b[0]), c_nq=float(b[1]), R2=1 - float(((yy - X @ b) ** 2).sum()) / sst)
    b4 = float((ev @ yy) / (ev @ ev)); out['M4_extreme_value_FEfam'] = dict(b=b4, R2=1 - float(((yy - ev * b4) ** 2).sum()) / sst)
    return out

def run_real(rdir, outdir, procs=8, smoke=False):
    seen, bad = verify_sums(rdir); assert bad == 0 and seen >= 160, (seen, bad)
    C = load(rdir, with_nc=not smoke)
    if smoke: C['mx'] = synth_mx(C, 'P1', np.random.default_rng([SEEDS['gate_P1'], 999]))   # code-path smoke on a synthetic plant, never real max=
    allnulls = sorted(set(C['seed'].tolist())); assert len(allnulls) == 16
    res = {'inputs': dict(R_files_verified=seen, bad=bad, cells=int(len(C['n'])), nulls=len(allnulls))}
    runs = {}
    Bp, Bh = (20, 10) if smoke else (B_PRIMARY, B_HALF)   # smoke: tiny B, synthetic NC, code path only
    for name, nulls, B in (('primary', allnulls, Bp), ('fresh', allnulls, Bp), ('halfA', HALF_A, Bh), ('halfB', HALF_B, Bh)):
        t0 = time.time(); point, th = run_boot(C, nulls, SEEDS[name], B, R_BOOT, procs)
        p, side = pvals(point['th'], th)
        runs[name] = dict(point=point, p=p, side=side, ci=[[float(np.nanpercentile(th[:, i], 2.5)), float(np.nanpercentile(th[:, i], 97.5))] for i in range(M_TESTS)])
        print(f'[{name}] seed {SEEDS[name]} B {B}  {time.time()-t0:.0f}s  th {np.round(point["th"], 4)}  p {np.round(p, 4)}', flush=True)
        if name == 'primary': thP = th; Dp = draws(sub(C, np.flatnonzero(np.isin(C['seed'], nulls))), np.random.default_rng(SEEDS['primary'] + 0), R_POINT)
    prim = runs['primary']; rej, thr = holm(prim['p'])
    tests = []
    for i in range(M_TESTS):
        dist = distance(max(prim['p'][i], 1e-12), thr[i], rej[i])
        sides = [prim['side'][i]] + [runs[k]['side'][i] for k in ('fresh', 'halfA', 'halfB')]
        same = len(set(sides)) == 1 and sides[0] != 0
        label = 'robusto' if (dist >= 2 and same) else 'FRONTEIRA'
        tests.append(dict(test=TEST_NAMES[i], theta=prim['point']['th'][i], threshold=THR[i], ci95=prim['ci'][i], p=prim['p'][i], holm_threshold=thr[i], reject=rej[i],
                          distance=dist, sides_primary_fresh_halfA_halfB=sides, label=label))
    res['tests'] = tests; res['runs'] = {k: dict(th=v['point']['th'], p=v['p'], ci=v['ci'], side=v['side']) for k, v in runs.items()}
    res['per_family_b_c_point'] = {FAMS[i]: v for i, v in enumerate(per_family(Dp))}
    res['M3_vs_M4_descriptive'] = m3_vs_m4(Dp)
    res['joint_M3_FEfam'] = joint(Dp, Dp['design'] == 0, Dp['mx'])
    os.makedirs(outdir, exist_ok=True)
    json.dump(res, open(outdir + '/results.json', 'w'), indent=1, default=float)
    with open(outdir + '/passrates.tsv', 'w') as fo:
        fo.write('family\tnq_window\tN\tcells\tnulls_with_pass\tnulls\twilson_lo\twilson_hi\tmax_NC\n')
        for r in passrates(C, allnulls): fo.write('\t'.join(map(str, r)) + '\n')
    return res

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['gates', 'real']); ap.add_argument('--rdir', default=DEF_R)
    ap.add_argument('--out', default='.'); ap.add_argument('--i-froze-prereg', action='store_true'); ap.add_argument('--procs', type=int, default=8)
    ap.add_argument('--gate-B', type=int, default=200); ap.add_argument('--smoke', action='store_true')
    a = ap.parse_args()
    if a.mode == 'gates':
        t0 = time.time(); res = run_gates(a.rdir, a.gate_B, a.procs); ok, L = summarize_gates(res)
        open(a.out + '/gates_output.txt', 'w').write('\n'.join(L) + f'\n(elapsed {time.time()-t0:.0f}s, tool sha256 {hashlib.sha256(open(__file__, "rb").read()).hexdigest()})\n')
        json.dump(res, open(a.out + '/gates_raw.json', 'w'), default=float)
    else:
        if not a.i_froze_prereg: sys.exit('refusing: real mode needs --i-froze-prereg (PREREG.md and this tool must be pushed first)')
        print(json.dumps(run_real(a.rdir, a.out, a.procs, a.smoke)['tests'], indent=1, default=float))
