#!/usr/bin/env python3
"""C132 (F-DIAL step 2, CONFIRMATION of C131 leads): page-level re-test of the four C131 floor pages f57r, f66r, f113r (Currier B)
and f88v (Currier A), with registered thresholds. See case-file/C132-floor-pages.md (the pre-registration); this is a summary.
REUSE (credit): instrument, null and plants are IMPORTED unchanged from tools/c131_intermediate_pages.py (sha256 259472b3...f1d3ea):
 Inst (add-0.5 leave-out A/B unigram profiles, lam-hat on {0,.01,..,1}, d = distance from own pole), N-RUN pseudo-pages
 (n_i consecutive tokens of the page's own (L, I) stratum, donors left out), own-page line plants, control recuts.
NEW HERE: R = 2000 per page (floor 1/2001); effect-size floor d >= 0.10; Holm over the 4 pages (ZL3b primary);
 IT2a concordance; pole-degenerate flag (share of null d == 0 >= 0.95 -> NOT TESTABLE); repaired EXCLUDED rule
 (raw p > 0.05 AND own-page f 0.5 plants caught >= 0.80); matched-size plant gate (G-POW_i: plants on N-RUN bases of the page's
 stratum at the smallest f whose mean planted d >= observed d, caught >= 0.80 at p <= 0.0125 and d >= 0.10);
 control FPR at R 2000 on the three C131 two-source controls; f79r as the artifact check (descriptive); f57r-full (all 11 lines,
 `<->` splits joined) as a descriptive sensitivity; hand $H reported per page and per stratum (descriptive).
Run: python3 tools/c132_floor_pages.py struct | run
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import sys, os, re, json, time, math
import numpy as np
from collections import defaultdict, OrderedDict
sys.path.insert(0, os.path.dirname(__file__))
import c131_intermediate_pages as C
from c131_intermediate_pages import Inst, ms_pages, ctrl_pages, holm, wilson, ZH, FILES, CTRL

SEED_NULL, SEED_MPLANT, SEED_OPLANT, SEED_CNULL, SEED_FULL = 11910, 11911, 11912, 11913, 11914   # next free 11915
R, NPL, ALPHA, DMIN, POLE_DEG, POW, A_CATCH = 2000, 40, 0.05, 0.10, 0.95, 0.80, 0.0125
NPL_OWN = 50
FGRID = [round(0.1 * k, 1) for k in range(1, 11)]
PAGES = ['f57r', 'f66r', 'f113r', 'f88v']; ARTIFACT = 'f79r'
OUT = 'analysis/C132_results.json'
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)

def pval(nd, d): return float((1 + (nd >= d - 1e-12).sum()) / (len(nd) + 1))

def null_of(I, p, seed, ti, pi, ntok=None):
    rng = np.random.default_rng([seed, ti, pi]); L = I.P[p]['L']; nd = np.empty(R)
    save = None
    if ntok is not None: save = int(I.n[I.idx[p]]); I.n[I.idx[p]] = ntok      # pseudo-page length = ntok (f57r-full only)
    for r in range(R):
        t, ex = I.pseudo(p, rng); nd[r] = I.d(I.lam(t, ex), L)
    if save is not None: I.n[I.idx[p]] = save
    return nd

def nrun_lines(I, p, rng):
    """N-RUN base as whole lines (for matched plants): consecutive lines of the stratum (page i skipped) until >= n_i tokens."""
    L, Ii = I.P[p]['L'], I.P[p]['I']; need = int(I.n[I.idx[p]])
    flat = [(q, ln) for q in I.strat[(L, Ii)] if q != p for ln in I.P[q]['lines']]
    j = int(rng.integers(len(flat))); out, don, k = [], set(), 0
    while k < need:
        q, ln = flat[j % len(flat)]; out.append(ln); don.add(I.idx[q]); k += len(ln); j += 1
    return out, don | {I.idx[p]}

def matched_plants(I, p, nd, seed, ti, pi, d_obs):
    L = I.P[p]['L']; pool = I.foreign_pool(p); curve = OrderedDict()
    for fi, f in enumerate(FGRID):
        rng = np.random.default_rng([seed, ti, pi, fi]); ds, c05, c0125 = [], 0, 0
        for _ in range(NPL):
            lines, don = nrun_lines(I, p, rng); k = int(round(f * len(lines)))
            rep = set(rng.choice(len(lines), size=k, replace=False).tolist()) if k else set(); toks = []
            for li, ln in enumerate(lines):
                if li in rep:
                    q, fl = pool[int(rng.integers(len(pool)))]; toks.extend(fl); don.add(I.idx[q])
                else: toks.extend(ln)
            dp = I.d(I.lam(I.ids(toks), don), L); pp = pval(nd, dp); ds.append(dp)
            c05 += (pp <= ALPHA and dp >= DMIN); c0125 += (pp <= A_CATCH and dp >= DMIN)
        curve[f] = dict(d_mean=float(np.mean(ds)), catch_0125=c0125 / NPL, catch_05=c05 / NPL)
    fm = next((f for f in FGRID if curve[f]['d_mean'] >= d_obs - 1e-12), FGRID[-1])
    return dict(curve=curve, f_match=fm, catch_at_match=curve[fm]['catch_0125'], gate_ok=bool(curve[fm]['catch_0125'] >= POW))

def own_plants(I, p, nd, seed, ti, pi):
    rng = np.random.default_rng([seed, ti, pi]); L = I.P[p]['L']; c, ds = 0, []
    for _ in range(NPL_OWN):
        t, ex = I.plant(p, 0.5, rng); dp = I.d(I.lam(t, ex), L); ds.append(dp); c += (pval(nd, dp) <= ALPHA and dp >= DMIN)
    return dict(catch=c / NPL_OWN, n=NPL_OWN, d_mean=float(np.mean(ds)), bound_ok=bool(c / NPL_OWN >= POW))

def score_page(I, p, ti, pi, plants=True):
    L = I.P[p]['L']; i = I.idx[p]; tok = I.ids([w for ln in I.P[p]['lines'] for w in ln])
    lam = I.lam(tok, {i}); d0 = I.d(lam, L); st = I.status(p)
    h = ZH.get(p, {})
    r = dict(L=L, I=I.P[p]['I'], H=h.get('H'), Q=h.get('Q'), ntok=int(I.n[i]), nlines=len(I.P[p]['lines']), status=st, lam=lam, d=d0)
    if st != 'INFORMATIVE': return r, None
    nd = null_of(I, p, SEED_NULL, ti, pi)
    r.update(p=pval(nd, d0), null_mean=float(nd.mean()), null_q95=float(np.quantile(nd, 0.95)), null_q99=float(np.quantile(nd, 0.99)),
             null_max=float(nd.max()), pole_share=float((nd <= 1e-12).mean()), degenerate=bool((nd <= 1e-12).mean() >= POLE_DEG),
             n_null_ge=int((nd >= d0 - 1e-12).sum()))
    if plants:
        r['matched'] = matched_plants(I, p, nd, SEED_MPLANT, ti, pi, d0)
        r['own_f0.5'] = own_plants(I, p, nd, SEED_OPLANT, ti, pi)
    return r, nd

def units(I, P):
    u = defaultdict(lambda: defaultdict(int)); hnd = defaultdict(lambda: defaultdict(int))
    for p in I.names:
        st = I.status(p); u[f"{P[p]['L']}-{P[p]['I']}"][st] += 1; hnd[f"{P[p]['L']}-H{ZH.get(p, {}).get('H')}"][st] += 1
    return {k: dict(v) for k, v in sorted(u.items())}, {k: dict(v) for k, v in sorted(hnd.items())}

def f57r_full(path):
    """all P-locus lines of f57r, `<->` drawing splits joined, first reading of [a:b], no length rule (descriptive only)."""
    out = []
    for raw in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'<f57r\.(\d+),([@+=*&~-])(\w+)>\s*(.*)', raw.rstrip('\n'))
        if not m or not m.group(3).startswith('P'): continue
        t = m.group(4).replace('<->', '.'); t = re.sub(r'<[^>]*>', '', t); t = re.sub(r'@\d+;', '', t)
        t = re.sub(r'\[([^:\]]*):[^\]]*\]', r'\1', t).replace('{', '').replace('}', '').replace("'", '')
        out.append([w for w in re.split(r'[.,\s]+', t) if w and re.fullmatch(r'[a-z]+', w)])
    return out

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'struct'
    tmpl = ms_pages(FILES[0][1])
    if mode == 'struct':
        for t, f in FILES:
            P = ms_pages(f); I = Inst(P); u, h = units(I, P)
            print(t, 'units per L-I stratum', json.dumps(u)); print(t, 'units per L-hand', json.dumps(h))
            for p in PAGES + [ARTIFACT]: print('  ', p, P[p]['L'], P[p]['I'], ZH.get(p, {}).get('H'), len(P[p]['lines']), I.status(p))
        for name, fa, fb in CTRL:
            P, use = ctrl_pages(tmpl, fa, fb); I = Inst(P); print(name, 'informative', sum(I.status(p) == 'INFORMATIVE' for p in I.names))
        print('f57r-full lines', [len(x) for x in f57r_full(FILES[0][1])])
        return
    out = dict(seeds=dict(null=SEED_NULL, matched_plant=SEED_MPLANT, own_plant=SEED_OPLANT, control_null=SEED_CNULL, f57r_full=SEED_FULL,
               next_free=11915), R=R, NPL=NPL, NPL_OWN=NPL_OWN, FGRID=FGRID, DMIN=DMIN, POLE_DEG=POLE_DEG, A_CATCH=A_CATCH,
               tool_c131_sha256='259472b33a4433647f8ac1680d4a3ea92ff475e2213931fa72ddace5fef1d3ea', controls={}, manuscript={})
    # ---- gate G-FPR first (controls at the same R)
    for ci, (name, fa, fb) in enumerate(CTRL):
        P, use = ctrl_pages(tmpl, fa, fb); I = Inst(P); k05 = kfull = k0125 = n = 0
        for pi, p in enumerate(I.names):
            if I.status(p) != 'INFORMATIVE': continue
            L = I.P[p]['L']; tok = I.ids([w for ln in I.P[p]['lines'] for w in ln]); d0 = I.d(I.lam(tok, {I.idx[p]}), L)
            nd = null_of(I, p, SEED_CNULL, ci, pi); pp = pval(nd, d0); deg = (nd <= 1e-12).mean() >= POLE_DEG; n += 1
            k05 += pp <= ALPHA; k0125 += pp <= A_CATCH; kfull += (pp <= ALPHA and d0 >= DMIN and not deg)
        S = dict(n=n, flagged_p05=int(k05), share_p05=k05 / n, wilson=wilson(int(k05), n), flagged_p0125=int(k0125),
                 flagged_fullrule=int(kfull), share_fullrule=kfull / n, gate_ok=bool(k05 / n <= 0.10))
        out['controls'][name] = S; log('control', name, json.dumps(S)); json.dump(out, open(OUT, 'w'), indent=1, default=float)
    g_fpr = all(out['controls'][n]['gate_ok'] for n, _, _ in CTRL)
    # ---- manuscript pages
    for ti, (t, f) in enumerate(FILES):
        P = ms_pages(f); I = Inst(P); u, h = units(I, P); res = OrderedDict()
        for p in PAGES + [ARTIFACT]:
            r, nd = score_page(I, p, ti, I.names.index(p), plants=(p in PAGES)); res[p] = r
            log(t, p, json.dumps({k: v for k, v in r.items() if k not in ('matched',)}, default=float))
            if 'matched' in r: log('   matched', r['matched']['f_match'], r['matched']['catch_at_match'], json.dumps(r['matched']['curve']))
        if t == 'ZL3b':
            lines = f57r_full(f); P2 = OrderedDict((k, dict(v)) for k, v in P.items()); P2['f57r'] = dict(P['f57r'], lines=lines)
            I2 = Inst(P2); i2 = I2.idx['f57r']; tok = I2.ids([w for ln in lines for w in ln]); lam = I2.lam(tok, {i2}); d0 = I2.d(lam, 'B')
            nd = null_of(I2, 'f57r', SEED_FULL, ti, i2)
            out['f57r_full'] = dict(ntok=len(tok), nlines=len(lines), lam=lam, d=d0, p=pval(nd, d0), null_mean=float(nd.mean()),
                                    null_q95=float(np.quantile(nd, 0.95)), lines_retained_by_C070=len(P['f57r']['lines']))
            log('f57r-full (descriptive)', json.dumps(out['f57r_full']))
        out['manuscript'][t] = dict(units_LI=u, units_LH=h, pages=res); json.dump(out, open(OUT, 'w'), indent=1, default=float)
    # ---- verdict (ZL3b primary; IT2a concordance)
    Z = out['manuscript']['ZL3b']['pages']; T = out['manuscript']['IT2a']['pages']
    raw = [Z[p]['p'] for p in PAGES]; adj = holm(raw); V = OrderedDict()
    for j, p in enumerate(PAGES):
        z, it = Z[p], T[p]
        conc = bool(it.get('status') == 'INFORMATIVE' and it['p'] <= ALPHA and it['d'] >= DMIN and not it['degenerate'])
        if not g_fpr: v = 'NOT TESTABLE (G-FPR)'
        elif z['degenerate']: v = 'NOT TESTABLE (pole-degenerate null)'
        elif not z['matched']['gate_ok']: v = 'NOT TESTABLE (matched-size power < 0.80)'
        elif adj[j] <= ALPHA and z['d'] >= DMIN: v = 'CONFIRMED MIXED-PROFILE' + (' (IT2a concordant)' if conc else ' (IT2a DISCORDANT)')
        elif z['p'] > ALPHA and z['own_f0.5']['bound_ok']: v = 'EXCLUDED (f 0.5 would have been caught)'
        else: v = 'UNRESOLVED'
        V[p] = dict(verdict=v, p=z['p'], holm=adj[j], d=z['d'], lam=z['lam'], IT2a_p=it.get('p'), IT2a_d=it.get('d'), IT2a_concordant=conc, H=z['H'])
    a = Z[ARTIFACT]; out['artifact_check'] = dict(page=ARTIFACT, d=a['d'], p=a.get('p'), pole_share=a.get('pole_share'),
        flag='NOT TESTABLE (pole-degenerate null)' if a.get('degenerate') else ('below d floor' if a['d'] < DMIN else 'testable'))
    out['verdict'] = dict(G_FPR=g_fpr, pages=V); json.dump(out, open(OUT, 'w'), indent=1, default=float)
    log('ARTIFACT', json.dumps(out['artifact_check'])); log('VERDICT', json.dumps(out['verdict'], default=float))

if __name__ == '__main__': main()
