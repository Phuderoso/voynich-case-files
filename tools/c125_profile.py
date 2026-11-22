#!/usr/bin/env python3
"""C125 rev 1 — additive line-overlap distance profile (Currier B), with Kryptos's rev-0 review built in.
O(d) = mean over same-page line pairs (i, i+d) of |T_i & T_j| / sqrt(|T_i||T_j|) (T = set of word types of a line), pooled over pages.
PRIMARY  A_LL  = O(1) - exp(fit), weighted (by pair count n_d) log-linear fit of O(d) on d = 2..4, extrapolated to d = 1.
SENS.    A_LIN = O(1) - [2 O(2) - O(3)].
NULL     N-WIN3 primary (per page: random phase, consecutive 3-line windows, lines permuted within windows); N-WIN4 sensitivity.
p = (1 + #{null >= obs}) / (R + 1), one-sided.
Modes: selftest | gates | ms.  Seeds: gates 11875, ms N-WIN3 11876, ms N-WIN4 11877 (reserved 11875-11882; next free 11883).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import c123_mi_para_block as C3
from c120_mi_distance import recut
from c121_mi_calibrated import plant, controls
import c124_mi_flip as C4
T0 = time.time()
def log(*a): print(*a, f'[{time.time()-T0:.1f}s]', flush=True)
DMAX, FIT_D = 8, (2, 3, 4)
ALPHA, NT = 0.05, 2
AG = ALPHA / NT                     # 0.025 gate level
R_GATE, R_MS = 1000, 2000
TAUS, DX_LAMS = (2, 4, 8), (0.35, 0.5, 0.75)
DR_LAMS = (0.35, 0.5, 0.75)         # C124 linear drift plant, admissible candidates
ADMIT = 0.25                        # admission: O(8)/O(1) >= 0.25 and non-increasing profile (d = 1..8, tolerance 0.002)
LADDER = C4.LADDER
TRANS = ('ZL3b', 'IT2a')
def wilson(k, n, z=1.96):
    if n == 0: return (float('nan'),) * 2
    p = k / n; c = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n); m = (p + z * z / (2 * n)) / (1 + z * z / n)
    return (float(m - c), float(m + c))
class Text:
    def __init__(self, pages):
        self.M, self.n = [], []
        for p in pages:
            p = [set(l) for l in p if len(l)]
            n = len(p)
            if n < 2: continue
            M = np.zeros((n, n))
            for i in range(n):
                for j in range(i + 1, n):
                    M[i, j] = M[j, i] = len(p[i] & p[j]) / np.sqrt(len(p[i]) * len(p[j]))
            self.M.append(M); self.n.append(n)
        self.nd = np.array([sum(max(n - d, 0) for n in self.n) for d in range(1, DMAX + 1)], float)
    def profile(self, perms=None, R=1):
        S = np.zeros((R, DMAX))
        for k, (M, n) in enumerate(zip(self.M, self.n)):
            P = np.tile(np.arange(n), (R, 1)) if perms is None else perms[k]
            for d in range(1, min(DMAX, n - 1) + 1):
                S[:, d - 1] += M[P[:, :-d], P[:, d:]].sum(1)
        return S / self.nd
    def win_perms(self, W, R, rng):
        out = []
        for n in self.n:
            ph = rng.integers(0, W, R)[:, None]
            key = (np.arange(n)[None, :] + ph) // W + rng.random((R, n))
            out.append(np.argsort(key, axis=1))
        return out
def A_of(O, nd):
    x = np.array(FIT_D, float); w = nd[[d - 1 for d in FIT_D]]
    with np.errstate(divide='ignore', invalid='ignore'):
        Y = np.log(O[:, [d - 1 for d in FIT_D]])
    xm = (w * x).sum() / w.sum(); ym = (Y * w).sum(1) / w.sum()
    b = ((w * (x - xm))[None, :] * (Y - ym[:, None])).sum(1) / (w * (x - xm) ** 2).sum()
    a = ym - b * xm
    All = O[:, 0] - np.exp(a + b * 1.0)
    Alin = O[:, 0] - (2 * O[:, 1] - O[:, 2])
    return All, Alin
def test(T, W, R, rng):
    O = T.profile(); A0, L0 = A_of(O, T.nd)
    On = T.profile(T.win_perms(W, R, rng), R); An, Ln = A_of(On, T.nd)
    def p(o, v):
        if not np.isfinite(o): return float('nan')
        v = np.where(np.isfinite(v), v, -np.inf); return float((1 + (v >= o).sum()) / (R + 1))
    return dict(O=[float(x) for x in O[0]], A_LL=float(A0[0]), A_LIN=float(L0[0]), p_LL=p(A0[0], An), p_LIN=p(L0[0], Ln),
                null_sd_LL=float(np.nanstd(An, ddof=1)), null_mean_LL=float(np.nanmean(An)), nonfinite_null=int((~np.isfinite(An)).sum()),
                null_mean_O=[float(x) for x in np.nanmean(On, 0)], n_pairs=[int(x) for x in T.nd])
def dx_plant(pages, rng, tau, lam):
    """exponential-decay drift: AR(1) latent per line (rho = exp(-1/tau)); tokens keyed lam*u_type + sqrt(1-lam^2)*noise; lines filled in z-rank order."""
    rho = np.exp(-1.0 / tau); out = []
    for p in pages:
        n = len(p); z = np.zeros(n); z[0] = rng.standard_normal()
        for i in range(1, n): z[i] = rho * z[i - 1] + np.sqrt(1 - rho * rho) * rng.standard_normal()
        w = [x for l in p for x in l]; ty = sorted(set(w)); u = dict(zip(ty, rng.standard_normal(len(ty))))
        key = np.array([lam * u[x] for x in w]) + np.sqrt(1 - lam * lam) * rng.standard_normal(len(w))
        w2 = [w[i] for i in np.argsort(key, kind='stable')]; new = [None] * n; c = 0
        for i in np.argsort(z, kind='stable'): new[i] = w2[c:c + len(p[i])]; c += len(p[i])
        out.append(new)
    return out
def templates():
    return {t: C3.split_pp(C3.pages_of(f'data/{t}-n.txt', 'CB'))[0] for t in TRANS}
def admissible(O):
    O = np.array(O); return bool(O[7] / O[0] >= ADMIT and np.all(np.diff(O) <= 0.002)), float(O[7] / O[0])
def mixing(tpl, W, rng, R=200):
    """descriptive: share of null distance-d pairs that were original distance-d' pairs (positions only)."""
    T = Text([[[i] for i in range(len(p))] for p in tpl])  # dummy
    cnt = np.zeros((3, DMAX + 1))
    for n in T.n:
        ph = rng.integers(0, W, R)[:, None]; P = np.argsort((np.arange(n)[None, :] + ph) // W + rng.random((R, n)), 1)
        for d in (1, 2, 3):
            if n > d:
                od = np.abs(P[:, :-d] - P[:, d:]).ravel(); cnt[d - 1] += np.bincount(np.minimum(od, DMAX), minlength=DMAX + 1)
    return {f'null_d{d}': {f'orig_d{k}': float(cnt[d - 1, k] / cnt[d - 1].sum()) for k in range(1, 6)} for d in (1, 2, 3)}
def gates(seed=11875):
    tpls = templates(); ctl = controls(); res = dict(seed=seed, mixing={}, fpr=[], spec={}, power={})
    for t, tpl in tpls.items():
        for W in (3, 4): res['mixing'][f'{t}_W{W}'] = mixing(tpl, W, np.random.default_rng([seed, 0, W, TRANS.index(t)]))
    log('mixing', json.dumps(res['mixing']['ZL3b_W3']))
    base = {(t, ci): recut(words, tpl) for t, tpl in tpls.items() for ci, (name, words, eva) in enumerate(ctl)}
    # G-FPR: unplanted controls (natural drift), 10 controls x 2 templates
    k = 0
    for (t, ci), b in base.items():
        r = test(Text(b), 3, R_GATE, np.random.default_rng([seed, 1, ci, TRANS.index(t)])); r.update(ctl=ctl[ci][0], tpl=t); res['fpr'].append(r)
        k += r['p_LL'] <= AG
    log(f'G-FPR rejections {k}/20 (gate <= 2)')
    # G-SPEC: drift plants (DX tau x lam, DR lam)
    cells = [('DX', tau, lam) for tau in TAUS for lam in DX_LAMS] + [('DR', None, lam) for lam in DR_LAMS]
    for kind, tau, lam in cells:
        rows = []
        for (t, ci), b in base.items():
            rng = np.random.default_rng([seed, 2, cells.index((kind, tau, lam)), ci, TRANS.index(t)])
            pp = dx_plant(b, rng, tau, lam) if kind == 'DX' else C4.plant_drift(b, rng, lam)
            r = test(Text(pp), 3, R_GATE, rng); r4 = test(Text(pp), 4, R_GATE, rng)
            rows.append(dict(p_LL=r['p_LL'], p_LIN=r['p_LIN'], p_LL_W4=r4['p_LL'], O=r['O'], ratio=r['O'][7] / r['O'][0], adm=admissible(r['O'])[0]))
        nm = f'{kind} tau={tau} lam={lam}'; rej = sum(x['p_LL'] <= AG for x in rows)
        ratio = float(np.mean([x['ratio'] for x in rows])); adm = sum(x['adm'] for x in rows) >= 10
        res['spec'][nm] = dict(rej_LL=rej, rej_LIN=sum(x['p_LIN'] <= AG for x in rows), rej_LL_W4=sum(x['p_LL_W4'] <= AG for x in rows),
                               n=20, wilson=wilson(rej, 20), mean_ratio_O8_O1=ratio, admissible=adm, O_mean=list(np.mean([x['O'] for x in rows], 0)))
        log(f'G-SPEC {nm}: rej LL {rej}/20 LIN {res["spec"][nm]["rej_LIN"]}/20 W4 {res["spec"][nm]["rej_LL_W4"]}/20 ratio {ratio:.3f} admissible {adm}')
    # G-POW: copy plant ladder
    for q, kk in LADDER:
        rows = []
        for (t, ci), b in base.items():
            rng = np.random.default_rng([seed, 3, int(q * 100), kk, ci, TRANS.index(t)])
            r = test(Text(plant(b, rng, q, kk)), 3, R_GATE, rng); rows.append(r)
        pw = sum(x['p_LL'] <= AG for x in rows); dO = float(np.mean([x['O'][0] - x['O'][1] for x in rows]))
        res['power'][f'{q}x{kk}'] = dict(power_LL=pw, power_LIN=sum(x['p_LIN'] <= AG for x in rows), n=20, planted_O1_minus_O2=dO)
        log(f'G-POW copy {q}x{kk}: {pw}/20 (LIN {res["power"][f"{q}x{kk}"]["power_LIN"]}) O1-O2 {dO:+.4f}')
    # unplanted O1-O2 and DR(0.75) reference
    res['ref_O1_minus_O2_unplanted'] = float(np.mean([x['O'][0] - x['O'][1] for x in res['fpr']]))
    return res
def ms(seed3=11876, seed4=11877, seedrep=11878):
    tpls = templates(); out = {}
    for i, (t, tpl) in enumerate(tpls.items()):
        T = Text(tpl); r3 = test(T, 3, R_MS, np.random.default_rng([seed3, i])); r4 = test(T, 4, R_MS, np.random.default_rng([seed4, i]))
        rr = test(T, 3, R_MS, np.random.default_rng([seedrep, i]))
        out[t] = dict(W3=r3, W4=r4, W3_fresh_replica=rr, n_pages=len(T.n), n_lines=int(sum(T.n)))
        log(t, f"A_LL {r3['A_LL']:+.5f} p {r3['p_LL']:.4f} | A_LIN {r3['A_LIN']:+.5f} p {r3['p_LIN']:.4f} | W4 p_LL {r4['p_LL']:.4f} | O1..4", [round(x, 4) for x in r3['O'][:4]])
    return out
def verdict(G, Mres):
    """mechanical decision rule (frozen in the prereg)."""
    v = dict(gates={})
    fpr = sum(r['p_LL'] <= AG for r in G['fpr']); v['gates']['G-FPR'] = dict(rej=fpr, n=20, ok=fpr <= 2)
    spec_ok, per_tau = True, {}
    for tau in TAUS:
        adm = {k: s for k, s in G['spec'].items() if k.startswith(f'DX tau={tau} ') and s['admissible']}
        per_tau[tau] = dict(admissible=list(adm), ok=bool(adm) and all(s['rej_LL'] <= 3 for s in adm.values()))
        spec_ok &= per_tau[tau]['ok']
    dr = {k: s for k, s in G['spec'].items() if k.startswith('DR') and s['admissible']}
    dr_ok = all(s['rej_LL'] <= 3 for s in dr.values())
    v['gates']['G-SPEC'] = dict(per_tau=per_tau, DR_admissible=list(dr), DR_ok=dr_ok, ok=spec_ok and dr_ok)
    step = next((k for k, s in G['power'].items() if s['power_LL'] >= 18), None)
    v['gates']['G-POW'] = dict(step=step, ok=step is not None)
    v['gates_pass'] = all(g['ok'] for g in v['gates'].values())
    ps = sorted(((Mres[t]['W3']['p_LL'], t) for t in TRANS)); lv = {ps[0][1]: ALPHA / 2, ps[1][1]: ALPHA}
    if ps[0][0] > ALPHA / 2: lv[ps[1][1]] = None     # Holm stops
    per = {}
    for t in TRANS:
        p, pl, prep = Mres[t]['W3']['p_LL'], Mres[t]['W3']['p_LIN'], Mres[t]['W3_fresh_replica']['p_LL']
        a = lv[t] if lv[t] is not None else ALPHA / 2
        rej = lv[t] is not None and p <= a; rej_lin = pl <= a
        front = (0.5 <= p / a <= 2) or (rej != rej_lin)
        robust = (not front) and (p / a <= 0.5 or p / a >= 2) and ((prep <= a) == (p <= a)) and (prep / a <= 0.5 or prep / a >= 2)
        per[t] = dict(p_LL=p, p_LIN=pl, level=a, reject=rej, reject_LIN=rej_lin, FRONTEIRA=front, robusto=robust, p_LL_fresh=prep, p_LL_W4=Mres[t]['W4']['p_LL'])
    v['per_transcription'] = per
    if not v['gates_pass']: v['verdict'] = 'NOT TESTABLE (gates)'
    else:
        nrej = sum(x['reject'] and not x['FRONTEIRA'] for x in per.values()); nfr = sum(x['FRONTEIRA'] for x in per.values())
        if nrej == 2: v['verdict'] = 'ADJACENCIA'
        elif nrej == 1: v['verdict'] = 'PARCIAL'
        elif nfr: v['verdict'] = 'FRONTEIRA'
        else:
            dref = G['spec']['DR tau=None lam=0.75']['O_mean']; dO_dr = dref[0] - dref[1]
            fine = G['power'][step]['planted_O1_minus_O2'] <= 2 * dO_dr
            v['verdict'] = 'DERIVA-COMPATIVEL' if fine else 'NOT TESTABLE (coarse ruler)'
            v['ruler'] = dict(step_O1_minus_O2=G['power'][step]['planted_O1_minus_O2'], DR075_O1_minus_O2=dO_dr)
    return v
def selftest():
    rng = np.random.default_rng(0); ok = True
    pages = [[list(rng.integers(0, 50, 8)) for _ in range(12)] for _ in range(30)]
    T = Text(pages); O = T.profile()
    direct = np.mean([len(set(p[i]) & set(p[i + 1])) / np.sqrt(len(set(p[i])) * len(set(p[i + 1]))) for p in pages for i in range(11)])
    ok &= abs(O[0, 0] - direct) < 1e-12; print('profile matches direct', abs(O[0, 0] - direct) < 1e-12)
    P = T.win_perms(3, 50, rng); good = all(np.all(np.abs(np.sort(p, 1) - np.arange(n)) == 0) and np.all(np.abs(p - np.arange(n)) <= 2) for p, n in zip(P, T.n))
    ok &= good; print('win3 perms valid, moves <= 2', good)
    Oe = np.array([[0.2 * np.exp(-d / 3) for d in range(1, DMAX + 1)]]); All, Alin = A_of(Oe, T.nd)
    ok &= abs(All[0]) < 1e-12 and Alin[0] > 0; print('pure exponential: A_LL 0 (', All[0], '), A_LIN > 0 [Kryptos point 1] (', Alin[0], ')')
    cp = plant(pages, np.random.default_rng(1), 1.0, 4); r = test(Text(cp), 3, 200, np.random.default_rng(2)); ok &= r['p_LL'] <= 0.025; print('copy1.0x4 p_LL', r['p_LL'])
    r0 = test(T, 3, 200, np.random.default_rng(3)); print('iid p_LL', r0['p_LL'])
    print('SELFTEST', 'ALL PASS' if ok else 'FAIL'); return ok
if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'selftest': sys.exit(0 if selftest() else 1)
    if mode == 'gates': json.dump(gates(), open('analysis/C125_gates.json', 'w'), indent=1, default=float)
    if mode == 'verdict':
        V = verdict(json.load(open('analysis/C125_gates.json')), json.load(open('analysis/C125_ms.json'))); print(json.dumps(V, indent=1)); json.dump(V, open('analysis/C125_verdict.json', 'w'), indent=1)
    if mode == 'ms':
        if not os.path.exists('analysis/C125_gates.json'): sys.exit('gates first')
        json.dump(ms(), open('analysis/C125_ms.json', 'w'), indent=1, default=float)
