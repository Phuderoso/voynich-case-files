#!/usr/bin/env python3
"""C119 v4 pre-registration checks (Kryptos's third review, gate 3 approved, 19 Nov 2026 ~20:25 PT). CONTROL TEXT ONLY: devowelled Caesar W1.
The manuscript is never loaded.
B fitter (final): L-BFGS-B (scipy) directly on (B_12, B_21) in PROBABILITY space with exact bounds [0, 1] (l stays finite at an exact bound, because the
other entry of that row is then 1). Exact gradient dl/dB_12 = G_12 - G_11, dl/dB_21 = G_21 - G_22, with G_ij = dl/dB_ij from forward-backward.
A start converges when the KKT projected gradient < 1e-8 OR |dl| < 1e-9 nats over the last 5 iterations; if scipy stops before either\nholds, it is warm-restarted from its end point (history kept), at most 20 times, thresholds unchanged. S convergence: >= 3 of RB starts within
CONV_TOLB (calib, >= 0.001 nats; 0.001 used here) of the best. Rows of B exactly on a bound are counted per text.
Re-runs, on the SAME seed sub-streams as v3: 4 pre-check texts, the 20 P-NOISE nulls, the power preview (11806); plus the DESCRIPTIVE aligned-plant
ladder q = 0.01 / 0.02 / 0.05 (seed 11807: [11807, 1] / [11807, 2] / [11807, 3] = plant line draws), scored against the 20 aligned-q0.10 nulls of
[11806, 6] (N-LINE of any word-order plant has the same distribution, because plants only permute middle words).
- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, time
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c119_precheck_v3 import (nline, fit_word, word_ll, word_mats, line_arrays, line_ll_and_counts, flat, pad, devowel_lines, NTOK,
                              hash_plant, aligned_plant, hclass, rank_p, fit_B)
SEED, PSEED, LSEED, RB, GTOL, DLTOL, CONV_TOLB, NREP, NPREV = 11801, 11806, 11807, 5, 1e-8, 1e-9, 1e-3, 3, 20

def ll_grad(B, Wm, LS, Mk, pi):
    N, Kw = Mk.shape; al = np.zeros((N, Kw, 2)); c = np.ones((N, Kw))
    a = np.einsum('i,nij->nj', pi, Wm[:, 0]); c[:, 0] = a.sum(1); al[:, 0] = a / c[:, :1]
    for k in range(1, Kw):
        a = np.einsum('ni,ij,njl->nl', al[:, k - 1], B, Wm[:, k]); s = a.sum(1); m = Mk[:, k]
        c[m, k] = s[m]; al[m, k] = a[m] / s[m, None]; al[~m, k] = al[~m, k - 1]
    be = np.ones((N, Kw, 2)); G = np.zeros((2, 2))
    for k in range(Kw - 1, 0, -1):
        m = Mk[:, k]; e = np.einsum('njl,nl->nj', Wm[:, k], be[:, k])
        be[m, k - 1] = (np.einsum('ij,nj->ni', B, e) / c[:, k:k + 1])[m]
        G += np.einsum('ni,nj->ij', al[m, k - 1], e[m] / c[m, k:k + 1])          # dl/dB_ij (no division by B)
    return float(np.log(c[Mk]).sum() + LS[Mk].sum()), G

Bp = lambda x: np.array([[1 - x[0], x[0]], [x[1], 1 - x[1]]])

def fit_one(x0, arr, pi, max_restarts=20):
    """L-BFGS-B in probability space. If scipy stops (e.g. 'relative reduction of f <= factr*epsmch', i.e. no decrease at machine precision)
    before EITHER registered criterion holds, it is warm-restarted from its end point (fresh memory), the l history carrying over,
    up to max_restarts times. The thresholds are never changed; a start that meets neither criterion stays UNCONVERGED."""
    hist = []
    def f(x):
        ll, G = ll_grad(Bp(x), *arr, pi); return -ll, -np.array([G[0, 1] - G[0, 0], G[1, 0] - G[1, 1]])
    def crit_dl(): return len(hist) >= 6 and max(hist[-6:]) - min(hist[-6:]) < DLTOL
    def kkt_of(x):
        _, g = f(x); return max(0.0 if (xi <= 0 and gi > 0) or (xi >= 1 and gi < 0) else abs(float(gi)) for xi, gi in zip(x, g))
    def cb(intermediate_result):
        hist.append(-float(intermediate_result.fun))
        if crit_dl(): raise StopIteration
    x = np.asarray(x0, float); nit = 0; msgs = []
    for k in range(max_restarts + 1):
        r = minimize(f, x, jac=True, method='L-BFGS-B', bounds=[(0.0, 1.0)] * 2, callback=cb,
                     options=dict(gtol=GTOL, ftol=0, maxiter=100000, maxfun=100000))
        x = np.clip(r.x, 0, 1); nit += int(r.nit); msgs.append(str(r.message))
        if kkt_of(x) < GTOL or crit_dl(): break
    ll = -f(x)[0]; pg = kkt_of(x); kkt = pg < GTOL; dl = crit_dl()
    return dict(ll=ll, x=x.tolist(), kkt_proj_grad=pg, conv_kkt=bool(kkt), conv_dl=bool(dl), converged=bool(kkt or dl), nit=nit,
                warm_restarts=k, message=msgs[-1], rows_on_bound=int(sum(xi in (0.0, 1.0) for xi in x)))

def S_fit(lines, cache, pi, nb):
    arr = line_arrays(lines, cache); ll0, _ = line_ll_and_counts(*arr, pi, np.tile(pi, (2, 1)))
    rng = np.random.default_rng(np.random.SeedSequence([SEED, 5])); F = []
    for s in range(RB):
        B0 = rng.dirichlet([1, 1], 2); F.append(fit_one(np.array([B0[0, 1], B0[1, 0]]), arr, pi))
    lls = [f['ll'] for f in F]; b = int(np.argmax(lls)); Ss = [(l - ll0) / nb for l in lls]; B = Bp(F[b]['x'])
    return dict(ll_reset=ll0, ll_best=lls[b], S_best=Ss[b], S_starts=Ss, SD_S_starts=float(np.std(Ss, ddof=1)), B_best=B.tolist(),
                B_ii=[B[0, 0], B[1, 1]], rows_on_bound_best=F[b]['rows_on_bound'], starts_converged=sum(f['converged'] for f in F),
                starts_conv_kkt=sum(f['conv_kkt'] for f in F), starts_conv_dl=sum(f['conv_dl'] for f in F),
                S_converged=bool(sum(f['converged'] and f['ll'] >= lls[b] - CONV_TOLB for f in F) >= 3),
                max_kkt_proj_grad=max(f['kkt_proj_grad'] for f in F), nit=[f['nit'] for f in F], warm_restarts=[f['warm_restarts'] for f in F]), arr

if __name__ == '__main__':
    t0 = time.time(); outp = sys.argv[1]; V3 = json.load(open(sys.argv[2]))
    lines = devowel_lines('Latin_Caesar', NTOK); obs = flat(lines)
    syms = sorted({u for w in obs for u in w}); sid = {u: i for i, u in enumerate(syms)}; nb = sum(len(l) - 1 for l in lines)
    ids = np.array([sid[u] for w in obs for u in w]); wid = np.array([k for k, w in enumerate(obs) for _ in w]); X, M = pad(ids, wid)
    rng1 = np.random.default_rng(np.random.SeedSequence([SEED, 3]))
    F1 = [fit_word(X, M, len(syms), rng1) for _ in range(10)]; P = F1[int(np.argmax([f['ll'] for f in F1]))]
    pi, A, Em = P['pi'], P['A'], P['Em']; cache = word_mats(set(obs), sid, A, Em)
    assert abs(P['ll'] - V3['step1_best_ll']) < 1e-9
    R = dict(text='CAE-DV W1', control_only=True, manuscript_loaded=False, n_word_boundaries=nb, step1_best_ll=P['ll'], fitter='L-BFGS-B, probability space, bounds [0,1]',
             GTOL=GTOL, DLTOL=DLTOL, CONV_TOLB=CONV_TOLB)
    rs = np.random.default_rng(SEED); reps = [nline(lines, rs) for _ in range(NREP)]; T = {}
    for name, ls in [('obs', lines)] + [(f'rep{r + 1}', sh) for r, sh in enumerate(reps)]:
        d, arr = S_fit(ls, cache, pi, nb)
        em = fit_B(*arr, pi, np.random.SeedSequence([SEED, 5])); d['EM_minus_this_ll'] = max(e['ll'] for e in em) - d['ll_best']
        d['v3_S'] = V3['texts'][name]['S_best']; d['S_minus_v3'] = d['S_best'] - d['v3_S']
        if name == 'obs':
            xs = np.linspace(0, 1, 41); G = max(line_ll_and_counts(*arr, pi, Bp((a, b)))[0] for a in xs for b in xs)
            d['grid_prob_41x41'] = dict(grid_max_ll=G, this_minus_grid=d['ll_best'] - G, PASS=bool(d['ll_best'] >= G - 1e-9))
        T[name] = d; print(name, json.dumps(d), flush=True)
    So = T['obs']['S_best']; Sr = [T[f'rep{r + 1}']['S_best'] for r in range(NREP)]
    R['texts'] = T; R['precheck'] = dict(S_obs=So, S_reps=Sr, Var_S_reps=float(np.var(Sr, ddof=1)), SD_S_reps=float(np.std(Sr, ddof=1)),
        max_SD_S_starts=max(v['SD_S_starts'] for v in T.values()), PASS=bool(all(abs(s - So) * nb > 1e-3 for s in Sr) and len({round(s, 9) for s in [So] + Sr}) >= 2))
    print('precheck', json.dumps(R['precheck']), flush=True)
    rp = np.random.default_rng(np.random.SeedSequence([SEED, 6])); pv = [S_fit(nline(lines, rp), cache, pi, nb)[0] for _ in range(NPREV)]
    Sn = [v['S_best'] for v in pv]
    R['pnoise_preview'] = dict(S_null=Sn, SD_S_null=float(np.std(Sn, ddof=1)), max_SD_S_starts=max(v['SD_S_starts'] for v in pv),
        all_S_converged=all(v['S_converged'] for v in pv), max_abs_S_minus_v3=float(np.max(np.abs(np.array(Sn) - np.array(V3['pnoise_preview']['S_null'])))),
        rows_on_bound=[v['rows_on_bound_best'] for v in pv], obs_vs_nulls=rank_p(So, Sn), v3_rank=V3['pnoise_preview']['obs_vs_nulls']['rank'])
    print('pnoise', json.dumps(R['pnoise_preview']), flush=True)
    def scored(label, planted, nplanted, nulls_S):
        d = S_fit(planted, cache, pi, nb)[0]
        return dict(label=label, lines_planted=nplanted, planted=d, **rank_p(d['S_best'], nulls_S))
    PW = {}; nullsets = {}
    for key, q, ps, ns, kind in (('hash_q0.1', 0.10, 1, 3, 'h'), ('hash_q0.5', 0.5, 2, 4, 'h'), ('aligned_q0.1', 0.10, 5, 6, 'a')):
        rg = np.random.default_rng(np.random.SeedSequence([PSEED, ps]))
        pl, n = hash_plant(lines, q, rg) if kind == 'h' else aligned_plant(lines, q, rg, sid, pi, A, Em)
        rn = np.random.default_rng(np.random.SeedSequence([PSEED, ns])); nl = [S_fit(nline(pl, rn), cache, pi, nb)[0] for _ in range(NPREV)]
        nS = [v['S_best'] for v in nl]; nullsets[key] = nS
        PW[key] = scored(key, pl, n, nS); PW[key]['all_null_S_converged'] = all(v['S_converged'] for v in nl)
        PW[key]['v3_rank'] = V3['power_preview'][key]['rank']; PW[key]['v3_planted_S'] = V3['power_preview'][key]['planted_S']
        print('power', key, json.dumps({k: v for k, v in PW[key].items() if k != 'planted'}), flush=True)
    R['power_preview'] = PW
    LAD = {}
    for q, sub in ((0.01, 1), (0.02, 2), (0.05, 3)):
        pl, n = aligned_plant(lines, q, np.random.default_rng(np.random.SeedSequence([LSEED, sub])), sid, pi, A, Em)
        for a, b in zip(pl, lines): assert sorted(a) == sorted(b) and a[0] == b[0] and a[-1] == b[-1]
        LAD[f'q{q}'] = scored(f'aligned q={q} (descriptive ladder)', pl, n, nullsets['aligned_q0.1'])
        print('ladder', q, json.dumps({k: v for k, v in LAD[f'q{q}'].items() if k != 'planted'}), flush=True)
    LAD['q0.1'] = {k: v for k, v in PW['aligned_q0.1'].items()}
    R['ladder'] = dict(label='DESCRIPTIVE detection curve (does not change gate 3 q = 0.10); null = the 20 [11806, 6] nulls', **LAD)
    R['seconds'] = round(time.time() - t0, 1); json.dump(R, open(outp, 'w'), indent=1, default=float); print('seconds', R['seconds'])
