#!/usr/bin/env python3
"""Per RULE.md: null max NC per nq bin from the cycle 229 Y lines; max_NC ~ ln N_bin vs nq."""
import re, glob, os, collections, sys
import numpy as np
from scipy.stats import rankdata
W = '/workspace/k229-nq-vs-search-size'
R = W + '/kryptos-main/data/cycle229/R'
PAT = re.compile(r'^Y model=(\w) p=(\d+) nq=(\d+) n=(\d+) pass=(\d+) max=(\S+)$')
SEED = 20261121; NPERM = 10000

def read(prefix_re):
    cells = []
    for f in sorted(glob.glob(R + '/*.txt')):
        b = os.path.basename(f)
        m = re.match(prefix_re, b)
        if not m: continue
        text = m.group(1); scope = m.group(2)
        for l in open(f):
            if l.startswith('Y '):
                g = PAT.match(l.strip()); assert g, l
                cells.append(dict(text=text, file=b, scope=scope, model=g.group(1), p=int(g.group(2)), nq=int(g.group(3)),
                                  n=int(g.group(4)), k=int(g.group(5)), mx=float(g.group(6))))
    return cells
NULL = read(r'^(null\d+)_(.+)\.txt$')
K4 = read(r'^(k4)_(.+)\.txt$')

def bins(cells, filt=lambda c: True):
    B = {}
    for c in cells:
        if not filt(c): continue
        d = B.setdefault(c['nq'], dict(N=0, mx=-99.0, k=0))
        d['N'] += c['n']; d['k'] += c['k']; d['mx'] = max(d['mx'], c['mx'])
    return B

# ---------- OLS helpers
def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    rss = float(res @ res); m, k = X.shape
    s2 = rss / (m - k) if m > k else float('nan')
    cov = s2 * np.linalg.inv(X.T @ X)
    t = beta / np.sqrt(np.diag(cov))
    return beta, res, rss, t
def fit_table(nq, N, y):
    m = len(y); ln = np.log(N)
    designs = {
        'M0': ['a'], 'M1': ['a', 'lnN'], 'M2': ['a', 'nq'], 'M3': ['a', 'lnN', 'nq'],
        'M4': ['a', 'sqrt(2lnN)/sqrt(nq)'], 'M5': ['a', '1/sqrt(nq)']}
    cols = {'a': np.ones(m), 'lnN': ln, 'nq': nq.astype(float), 'sqrt(2lnN)/sqrt(nq)': np.sqrt(2 * ln) / np.sqrt(nq), '1/sqrt(nq)': 1 / np.sqrt(nq)}
    out = {}
    sst = float(((y - y.mean()) ** 2).sum())
    for name, cn in designs.items():
        X = np.column_stack([cols[c] for c in cn]); k = X.shape[1]
        beta, res, rss, t = ols(X, y)
        aic = m * np.log(rss / m) + 2 * (k + 1)
        aicc = aic + 2 * (k + 1) * (k + 2) / (m - k - 2) if m - k - 2 > 0 else float('nan')
        r2 = 1 - rss / sst if sst > 0 else float('nan')
        adj = 1 - (1 - r2) * (m - 1) / (m - k) if m > k else float('nan')
        out[name] = dict(k=k, rss=rss, r2=r2, adj=adj, aic=aic, aicc=aicc, beta=beta, t=t, names=cn)
    return out

def fl_perm(y, Xfull, Xred, j, rng, nperm):
    """Freedman-Lane: test coefficient j of Xfull; reduced model Xred."""
    beta_r, res_r, _, _ = ols(Xred, y); fitted = Xred @ beta_r
    t_obs = ols(Xfull, y)[3][j]; cnt = 0
    for _ in range(nperm):
        ys = fitted + rng.permutation(res_r)
        if abs(ols(Xfull, ys)[3][j]) >= abs(t_obs) - 1e-12: cnt += 1
    return t_obs, (1 + cnt) / (nperm + 1)

def analyze(B, minN, label, out, rng, full=True):
    keys = sorted(k for k in B if B[k]['N'] >= minN)
    nq = np.array(keys); N = np.array([B[k]['N'] for k in keys], float); y = np.array([B[k]['mx'] for k in keys])
    ln = np.log(N)
    out.append(f'== {label}  (N_bin >= {minN}): bins {len(keys)} (nq {keys[0]}..{keys[-1]})')
    if len(keys) < 6: out.append('  too few bins'); return None
    out.append(f'  corr(lnN, nq) = {np.corrcoef(ln, nq)[0,1]:.3f}; corr(y, lnN) = {np.corrcoef(y, ln)[0,1]:.3f}; corr(y, nq) = {np.corrcoef(y, nq)[0,1]:.3f}')
    F = fit_table(nq, N, y); best = min(f['aicc'] for f in F.values() if not np.isnan(f['aicc']))
    rows = []
    for name, f in F.items():
        coefs = ', '.join(f"{n}={b:.4f}(t={t:.1f})" for n, b, t in zip(f['names'], f['beta'], f['t']))
        out.append(f"  {name}: k={f['k']} R2={f['r2']:.3f} adjR2={f['adj']:.3f} AIC={f['aic']:.2f} AICc={f['aicc']:.2f} dAICc={f['aicc']-best:.2f}  {coefs}")
        rows.append((label, minN, name, len(keys), f['k'], f['rss'], f['r2'], f['adj'], f['aic'], f['aicc'], f['aicc'] - best, coefs))
    r1, r3 = ln, nq.astype(float)
    vif = 1 / (1 - np.corrcoef(r1, r3)[0, 1] ** 2); out.append(f'  VIF(M3) = {vif:.2f}')
    if full:
        # rank checks
        ry, r_ln, r_nq = rankdata(y), rankdata(ln), rankdata(nq)
        def sp(a, b): return float(np.corrcoef(a, b)[0, 1])
        obs1, obs2 = sp(ry, r_ln), sp(ry, r_nq)
        c1 = c2 = c3 = 0; d_obs = F['M1']['r2'] - F['M2']['r2']
        for _ in range(NPERM):
            ys = rng.permutation(y); rys = rankdata(ys)
            c1 += abs(sp(rys, r_ln)) >= abs(obs1) - 1e-12; c2 += abs(sp(rys, r_nq)) >= abs(obs2) - 1e-12
            Fs = fit_table(nq, N, ys); c3 += abs(Fs['M1']['r2'] - Fs['M2']['r2']) >= abs(d_obs) - 1e-12
        out.append(f'  Spearman rho(y, lnN) = {obs1:.3f} perm p = {(1+c1)/(NPERM+1):.4f}; rho(y, nq) = {obs2:.3f} perm p = {(1+c2)/(NPERM+1):.4f}')
        out.append(f'  R2(M1) - R2(M2) = {d_obs:.3f}; shuffled-y two-sided perm p = {(1+c3)/(NPERM+1):.4f}')
        one = np.ones(len(y)); XM3 = np.column_stack([one, ln, nq.astype(float)]); XM1 = np.column_stack([one, ln]); XM2 = np.column_stack([one, nq.astype(float)])
        tb, pb = fl_perm(y, XM3, XM2, 1, rng, NPERM); tc, pc = fl_perm(y, XM3, XM1, 2, rng, NPERM)
        out.append(f'  Freedman-Lane: b (lnN | nq) t = {tb:.2f} p = {pb:.4f};  c (nq | lnN) t = {tc:.2f} p = {pc:.4f}')
        # partial Spearman via rank-residual correlations
        def resid(a, X): b = np.linalg.lstsq(X, a, rcond=None)[0]; return a - X @ b
        X_nq = np.column_stack([one, r_nq]); X_ln = np.column_stack([one, r_ln])
        pr1 = sp(resid(ry, X_nq), resid(r_ln, X_nq)); pr2 = sp(resid(ry, X_ln), resid(r_nq, X_ln))
        # Freedman-Lane on ranks
        XR3 = np.column_stack([one, r_ln, r_nq])
        _, pp1 = fl_perm(ry, XR3, X_nq, 1, rng, NPERM); _, pp2 = fl_perm(ry, XR3, X_ln, 2, rng, NPERM)
        out.append(f'  partial Spearman: rho(y, lnN | nq) = {pr1:.3f} perm p = {pp1:.4f};  rho(y, nq | lnN) = {pr2:.3f} perm p = {pp2:.4f}')
        a1 = F['M1']['aicc']; a2 = F['M2']['aicc']
        lab = 'INCONCLUSIVE'
        if a1 <= a2 - 2 and pb < 0.05 and not pc < 0.05: lab = 'LOGN-DOMINATES'
        elif a2 <= a1 - 2 and pc < 0.05 and not pb < 0.05: lab = 'NQ-DOMINATES'
        elif pb < 0.05 and pc < 0.05: lab = 'BOTH'
        out.append(f'  VERDICT (RULE.md rule): {lab}   [AICc M1 {a1:.2f}, M2 {a2:.2f}, M3 {F["M3"]["aicc"]:.2f}]')
    return rows

def main():
    out = []; rng = np.random.default_rng(SEED)
    Bp = bins(NULL); Bk = bins(K4)
    Bv = bins(NULL, lambda c: c['model'] == 'V'); Bq = bins(NULL, lambda c: c['model'] == 'Q'); Ba = bins(NULL, lambda c: c['scope'].startswith('all'))
    tot = sum(d['N'] for d in Bp.values())
    out.append(f'null Y cells {len(NULL)}; decipherments {tot}; K4 Y cells {len(K4)}; null texts {len({c["text"] for c in NULL})}')
    with open(W + '/counts_by_nq.tsv', 'w') as f:
        f.write('nq\tN_bin\tmax_NC\tpass_bin\tK4_N\tK4_max_NC\tK4_pass\tV_N\tV_max\tQ_N\tQ_max\tall_N\tall_max\n')
        for q in range(1, 65):
            def g(B, k, d='NA'): return (f"{B[q][k]:.3f}" if k == 'mx' else str(B[q][k])) if q in B else d
            f.write(f"{q}\t{g(Bp,'N','0')}\t{g(Bp,'mx')}\t{g(Bp,'k','0')}\t{g(Bk,'N','0')}\t{g(Bk,'mx')}\t{g(Bk,'k','0')}\t{g(Bv,'N','0')}\t{g(Bv,'mx')}\t{g(Bq,'N','0')}\t{g(Bq,'mx')}\t{g(Ba,'N','0')}\t{g(Ba,'mx')}\n")
    # pass cells
    pc = [c for c in NULL if c['k'] > 0]
    with open(W + '/pass_cells.tsv', 'w') as f:
        f.write('text\tfile\tmodel\tp\tnq\tN\tpass\tmax_NC\n')
        for c in sorted(pc, key=lambda c: (c['nq'], c['text'])): f.write(f"{c['text']}\t{c['file']}\t{c['model']}\t{c['p']}\t{c['nq']}\t{c['n']}\t{c['k']}\t{c['mx']:.3f}\n")
    out.append(f'PASS cells (Y cells with pass>0): {len(pc)}; null texts with >=1 pass {len({c["text"] for c in pc})}/16; total passing hits {sum(c["k"] for c in pc)}')
    for c in sorted(pc, key=lambda c: (c['nq'], c['text'])): out.append(f"  {c['text']} {c['file']} {c['model']} p={c['p']} nq={c['nq']} N={c['n']} pass={c['k']} max={c['mx']:.3f}")
    el = [c for c in pc if c['nq'] >= 10]
    out.append(f"BAR-ELIGIBLE passes (nq >= 10, the house bar's floor): Y cells {len(el)}, hits {sum(c['k'] for c in el)}, distinct nulls {len({c['text'] for c in el})}/16, nq values {sorted(c['nq'] for c in el)}, none at nq 10-11: {not any(c['nq'] in (10, 11) for c in el)}")
    out.append(f"  passes with nq < 10 (below the floor, NOT bar passes): Y cells {len(pc)-len(el)}, hits {sum(c['k'] for c in pc if c['nq'] < 10)}, nq range {sorted({c['nq'] for c in pc if c['nq'] < 10})}")
    out.append('null max NC and N by nq 10..25: ' + '; '.join(f"{q}:{Bp[q]['mx']:.3f}/N={Bp[q]['N']}" for q in range(10, 26) if q in Bp))
    out.append('passes by nq: ' + str({q: Bp[q]['k'] for q in sorted(Bp) if Bp[q]['k']}))
    out.append('nq 10, 11, 12 (pooled): ' + '; '.join(f"nq {q}: N {Bp[q]['N']} max {Bp[q]['mx']:.3f} pass {Bp[q]['k']}" for q in (10, 11, 12)))
    out.append('K4 passes by nq: ' + str({q: Bk[q]['k'] for q in sorted(Bk) if Bk[q]['k']}) + f"; K4 max over all bins {max(d['mx'] for d in Bk.values()):.3f}; null max over all bins {max(d['mx'] for d in Bp.values()):.3f}")
    rows = []
    for B, lab, full in ((Bp, 'pooled', True),):
        for minN in (20, 5, 100, 1000):
            r = analyze(B, minN, lab, out, rng, full=True)
            if r: rows += r
    Bp10 = {q: d for q, d in Bp.items() if q >= 10}
    r = analyze(Bp10, 20, 'S-nq10 (nq >= 10 only; added AFTER the first run, not part of the verdict)', out, rng, full=True)
    if r: rows += r
    for B, lab in ((Bv, 'V only'), (Bq, 'Q only'), (Ba, 'all.bin scope')):
        r = analyze(B, 20, lab, out, rng, full=True)
        if r: rows += r
    with open(W + '/fits.tsv', 'w') as f:
        f.write('stratum\tminN\tmodel\tbins\tk\tRSS\tR2\tadjR2\tAIC\tAICc\tdAICc\tcoefficients\n')
        for r in rows: f.write('\t'.join(f'{x:.4f}' if isinstance(x, float) else str(x) for x in r) + '\n')
    open(W + '/summary_nq_search.txt', 'w').write('\n'.join(out) + '\n')
    open(W + '/perm.txt', 'w').write('\n'.join(l for l in out if 'Spearman' in l or 'Freedman' in l or 'VERDICT' in l or l.startswith('==') or 'R2(M1)' in l) + '\n')
    print('\n'.join(out))
main()
