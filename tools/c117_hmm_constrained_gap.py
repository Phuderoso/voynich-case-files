#!/usr/bin/env python3
"""C117 (F-HMM step 6): a graded, always-finite re-test of C113's 'stickier than word-position slots', per Currier stratum.
Why: C116's DL statistic had a degenerate null (no slot-shuffled restart ever reached the sticky mode, effective N = 0), so its
floor p carried no information. Design adopted from Kryptos's review (2026-11-19 ~07:58 PT):
- per text, R_F free EM restarts (C111 fit_hmm algorithm, unchanged) and R_C STICKY-CONSTRAINED restarts (same EM, but after every
  M-step each transition row is clamped so A_ii >= DMIN = 0.90, i.e. SW <= 0.10 < 0.15, the C116 sticky boundary; for a 2-state
  row clamping is the exact constrained M-step because the row log-likelihood is concave in A_ii);
- statistic T = (best ll constrained - best ll free) / n_glyph_tokens.  Finite by construction (both fits always exist).
  T ~ 0: a sticky solution is (nearly) as good as the best free one; T << 0: sticky is disfavoured.
- one-sided toward 'sticky favoured': p = (1 + #{converged null T >= obs T}) / (1 + #converged null); mid-p printed beside it.
- convergence: a fit family (free or constrained) converges when its best ll is reached within CONV_TOL by >= CONV_MIN = 3 restarts.
  R and CONV_TOL are chosen by the 'calib' stage on CONTROL texts only (rule in the case file) and then frozen by amendment
  before any manuscript fit.  Unconverged null replicates are excluded and counted; p_cons / p_lib bounds; if Holm pass differs
  between them the stratum is CONVERGENCE-SENSITIVE (no pass).  NOT TESTABLE if observed fit unconverged or > 10 % of nulls are.
- G-CANFAIL per primary stratum: >= 20 % distinct null T values (rounded 1e-6) else NOT TESTABLE.
- gates: G-POW (Caesar + WEAK twin plant q 0.10) must reach p <= 0.05/3; G-FPR (unplanted Caesar) must converge and not pass.
- effective N (converged finite nulls), ties at the observed value, convergence rate printed beside every p.
Null: N-SLOT (C109 shuffle_slot).  Seed 11791 (calibration uses SeedSequence([11791, 99, ...]), disjoint from the run).
- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c108_sukhotin_alternation import encode
from c109_sukhotin_slot_null import slot_keys, shuffle_slot
from c111_hmm_sukhotin_convergence import pad, NITER, TOL
from c113_hmm_switch_slot_null import hash_name
from c115_hmm_switch_currier import strata, devowel_tokens, twin, NTOK

SEED, DMIN, QWEAK, CONV_MIN, MAX_UNCONV, MIN_DISTINCT = 11791, 0.90, 0.10, 3, 0.10, 0.20
R_CAL, CAL_R_GRID, CAL_TOL_GRID, CAL_NNULL = 30, (10, 15, 20, 30), (1.0, 2.0, 5.0), 3
FROZEN = 'analysis/C117_frozen.json'       # written once by 'calib'; holds R and CONV_TOL
NNULL_P, NNULL_G, ALPHA, SOFT_S = 79, 59, 0.05, 520
PRIMARY, GATES, DESC = ('ZL_A', 'ZL_B1', 'ZL_B2'), ('GPOW', 'GFPR'), ('IT_A', 'IT_B1', 'IT_B2')
CKPT = 'analysis/C117_checkpoint.jsonl'

def fit(X, M, S, rng, sticky):
    W, L = X.shape; pi = rng.dirichlet([1, 1]); A = rng.dirichlet([1, 1], 2); Bm = rng.dirichlet(np.ones(S), 2)
    def clamp(A):
        if not sticky: return A
        A = A.copy()
        for i in range(2):
            if A[i, i] < DMIN: A[i, i] = DMIN; A[i, 1 - i] = 1 - DMIN
        return A
    A = clamp(A); last = -np.inf
    for it in range(NITER):
        al = np.zeros((W, L, 2)); c = np.ones((W, L))
        a = pi[None] * Bm[:, X[:, 0]].T; c[:, 0] = a.sum(1); al[:, 0] = a / c[:, :1]
        for t in range(1, L):
            a = (al[:, t - 1] @ A) * Bm[:, X[:, t]].T; s = a.sum(1); m = M[:, t]
            c[m, t] = s[m]; al[m, t] = a[m] / s[m, None]; al[~m, t] = al[~m, t - 1]
        be = np.ones((W, L, 2)); xi = np.zeros((2, 2))
        for t in range(L - 2, -1, -1):
            m = M[:, t + 1]; e = Bm[:, X[:, t + 1]].T * be[:, t + 1]
            b = (e @ A.T) / c[:, t + 1:t + 2]; be[m, t] = b[m]
            xi += np.einsum('wi,ij,wj->ij', al[m, t], A, e[m] / c[m, t + 1:t + 2])
        ll = float(np.log(c[M]).sum()); g = al * be; g = g / g.sum(2, keepdims=True)
        pi = g[:, 0].mean(0); A = clamp(xi / xi.sum(1, keepdims=True))
        Bn = np.zeros((2, S)); np.add.at(Bn.T, X[M], g[M]); Bm = (Bn + 1e-12) / (Bn + 1e-12).sum(1, keepdims=True)
        if ll - last < TOL * abs(ll): break
        last = ll
    G = np.zeros((S, 2)); np.add.at(G, X[M], g[M]); occ = G.sum(0) / G.sum()
    return round(ll, 3), round(float((occ * (1 - np.diag(A))).sum()), 5), it + 1

def texts():
    zl, _ = strata('data/ZL3b-n.txt'); it, _ = strata('data/IT2a-n.txt'); cae = devowel_tokens('Latin_Caesar', NTOK)
    T = dict(GPOW=twin(cae, np.random.default_rng(np.random.SeedSequence([SEED, 0])), QWEAK), GFPR=cae)
    T.update({'ZL_' + k: v for k, v in zl.items()}); T.update({'IT_' + k: v for k, v in it.items()}); return T

_T = None
def _fits(name, rep, nr, ss):
    global _T
    if _T is None: _T = texts()
    words = _T[name]; ids, wid, inv = encode(words); rng = np.random.default_rng(ss)
    if rep > 0: ids = shuffle_slot(ids, slot_keys(words), rng)
    X, M = pad(ids, wid); S = len(inv)
    F = [fit(X, M, S, rng, False) for _ in range(nr)]; C = [fit(X, M, S, rng, True) for _ in range(nr)]
    return dict(name=name, rep=rep, n=int(len(ids)), F=F, C=C)

def _cal_job(j):
    name, rep = j; return _fits(name, rep, R_CAL, np.random.SeedSequence([SEED, 99, hash_name(name), rep]))

def conv(lls, tol): b = max(lls); return sum(l >= b - tol for l in lls) >= CONV_MIN

def calib():
    """CONTROL texts only (Caesar unplanted + weak plant, observed and 3 slot-shuffles each). Rule: smallest R in CAL_R_GRID, then
    smallest tol in CAL_TOL_GRID, such that ALL 16 fit families (8 texts x free/constrained) converge using their first R restarts;
    if none, R = 30 and tol = 5.0 and the instrument is flagged. Written once to FROZEN; refuses to overwrite."""
    assert not os.path.exists(FROZEN), 'already frozen'
    from multiprocessing import Pool
    t0 = time.time(); J = [(k, r) for k in GATES for r in range(CAL_NNULL + 1)]
    with Pool(8) as P: recs = P.map(_cal_job, J)
    json.dump(recs, open('analysis/C117_calibration.json', 'w'))
    table, choice = {}, None
    for R in CAL_R_GRID:
        for tol in CAL_TOL_GRID:
            ok = [conv([f[0] for f in rec[fam][:R]], tol) for rec in recs for fam in ('F', 'C')]
            table[f'R{R}_tol{tol}'] = f'{sum(ok)}/{len(ok)}'
            if choice is None and all(ok): choice = (R, tol)
    flagged = choice is None
    if flagged: choice = (30, 5.0)
    desc = {f'{r["name"]}#{r["rep"]}': dict(T30=round((max(c[0] for c in r['C']) - max(f[0] for f in r['F'])) / r['n'], 6),
            freeSW_best=r['F'][int(np.argmax([f[0] for f in r['F']]))][1], conSW_max=max(c[1] for c in r['C'])) for r in recs}
    out = dict(R=choice[0], CONV_TOL=choice[1], flagged=flagged, table=table, controls_descriptive=desc,
               seconds=round(time.time() - t0, 1))
    json.dump(out, open(FROZEN, 'w'), indent=1); print(json.dumps(out, indent=1))

def frozen(): return json.load(open(FROZEN))

def joblist():
    nn = {**{k: NNULL_G for k in GATES}, **{k: NNULL_P for k in PRIMARY}, **{k: 0 for k in DESC}}
    J = [(k, r) for k in GATES for r in range(NNULL_G + 1)]
    J += [(k, 0) for k in PRIMARY + DESC]
    J += [(k, r) for r in range(1, NNULL_P + 1) for k in PRIMARY]
    return J, nn

def _job(j):
    name, rep = j; return _fits(name, rep, frozen()['R'], np.random.SeedSequence([SEED, hash_name(name), rep]))

def load():
    D = {}
    if os.path.exists(CKPT):
        for line in open(CKPT):
            if line.strip(): r = json.loads(line); D[(r['name'], r['rep'])] = r
    return D

def run():
    from multiprocessing import Pool
    frozen(); t0 = time.time(); done = load(); J, _ = joblist(); todo = [j for j in J if j not in done]
    print('jobs', len(J), 'done', len(done), 'todo', len(todo), flush=True)
    if not todo: return
    P = Pool(8); it = P.imap(_job, todo); n = 0
    with open(CKPT, 'a') as f:
        try:
            for rec in it:
                f.write(json.dumps(rec) + '\n'); f.flush(); n += 1
                if time.time() - t0 > SOFT_S: break
        finally: P.terminate()
    print('wrote', n, 'in', round(time.time() - t0, 1), 's; done', len(done) + n, '/', len(J), flush=True)

def status():
    done = load(); J, _ = joblist(); left = [j for j in J if j not in done]
    print('done', len(J) - len(left), '/', len(J), 'next', left[:3])

def stat(rec, tol):
    lf = [f[0] for f in rec['F']]; lc = [c[0] for c in rec['C']]
    return dict(T=(max(lc) - max(lf)) / rec['n'], conv=bool(conv(lf, tol) and conv(lc, tol)),
                conv_F=conv(lf, tol), conv_C=conv(lc, tol), free_best_SW=rec['F'][int(np.argmax(lf))][1],
                basin_share=float(np.mean([f[1] < 0.15 for f in rec['F']])))

def holm(ps):
    order = sorted(ps, key=lambda k: ps[k]); out, ok = {}, True
    for i, k in enumerate(order):
        bar = ALPHA / (len(ps) - i); ok = ok and ps[k] <= bar + 1e-12; out[k] = dict(p=ps[k], bar=round(bar, 5), pass_=ok)
    return out

def verdict():
    Fz = frozen(); tol = Fz['CONV_TOL']; D = load(); J, nn = joblist(); missing = [j for j in J if j not in D]
    assert not missing, f'{len(missing)} jobs missing: run more calls first'
    S = {k: stat(v, tol) for k, v in D.items()}; R = dict(per_text={}, frozen=Fz, seed=SEED); pt = R['per_text']
    for k in GATES + PRIMARY + DESC:
        o = S[(k, 0)]; nul = [S[(k, r)] for r in range(1, nn[k] + 1)]
        cn = np.array([s['T'] for s in nul if s['conv']]); unc = sum(not s['conv'] for s in nul)
        rec = dict(obs=o, n_null=nn[k], unconverged=unc, conv_rate=(1 - unc / nn[k]) if nn[k] else None)
        if nn[k]:
            ge = int((cn >= o['T'] - 1e-12).sum()); ties = int((np.abs(cn - o['T']) <= 1e-6).sum()); gt = int((cn > o['T'] + 1e-6).sum())
            rec.update(p=(1 + ge) / (1 + len(cn)), mid_p=(gt + 0.5 * ties + 0.5) / (1 + len(cn)),
                       p_cons=(1 + ge + unc) / (1 + nn[k]), p_lib=(1 + ge) / (1 + nn[k]), effective_N=len(cn), ties=ties,
                       distinct_frac=(len(np.unique(np.round(cn, 6))) / len(cn)) if len(cn) else 0.0,
                       null_T_mean=float(cn.mean()) if len(cn) else None, null_T_sd=float(cn.std(ddof=1)) if len(cn) > 1 else None,
                       null_T_q95=float(np.quantile(cn, 0.95)) if len(cn) else None,
                       null_basin_share_mean=float(np.mean([s['basin_share'] for s in nul])))
            rec['testable'] = bool(o['conv'] and unc <= MAX_UNCONV * nn[k] and (k not in PRIMARY or rec['distinct_frac'] >= MIN_DISTINCT))
        pt[k] = rec; print(k, json.dumps(rec, default=float), flush=True)
    bar1 = ALPHA / 3
    R['gates'] = dict(G_POW=dict(p=pt['GPOW']['p'], pass_=bool(pt['GPOW']['testable'] and pt['GPOW']['p'] <= bar1 + 1e-12)),
                      G_FPR=dict(p=pt['GFPR']['p'], pass_=bool(pt['GFPR']['testable'] and pt['GFPR']['p'] > bar1 + 1e-12)))
    gok = all(g['pass_'] for g in R['gates'].values())
    pv = lambda f: {k: (pt[k][f] if pt[k]['testable'] else 1.0) for k in PRIMARY}
    H, Hc, Hl = holm(pv('p')), holm(pv('p_cons')), holm(pv('p_lib'))
    cs = [k for k in PRIMARY if pt[k]['testable'] and Hc[k]['pass_'] != Hl[k]['pass_']]
    passed = [k for k in PRIMARY if H[k]['pass_'] and pt[k]['testable'] and k not in cs]
    untest = [k for k in PRIMARY if not pt[k]['testable']]
    if not gok: lab = 'NOT TESTABLE (gates)'
    elif passed: lab = 'STICKY FAVOURED in ' + '+'.join(passed)
    elif len(untest) == 3: lab = 'NOT TESTABLE (convergence / can-fail)'
    else: lab = 'NOT SUPPORTED' + (f' (not testable: {"+".join(untest)})' if untest else '')
    if cs: lab += ' (CONVERGENCE-SENSITIVE: ' + '+'.join(cs) + ', no pass)'
    R.update(holm=H, holm_cons=Hc, holm_lib=Hl, verdict=lab); print(R['gates'], H, lab)
    json.dump(R, open('analysis/C117_results.json', 'w'), indent=1, default=float)

if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'status'
    {'calib': calib, 'run': run, 'verdict': verdict}.get(a, status)()
