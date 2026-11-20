#!/usr/bin/env python3
"""C119 DRAFT v3 (Kryptos's second review, 19 Nov 2026 ~20:15 PT). CONTROL TEXT ONLY: devowelled Caesar W1; the manuscript is never loaded.
(a) B fit = direct optimisation: L-BFGS-B (scipy) on theta = (logit B_12, logit B_21), bounds logit(1e-6)..logit(1-1e-6), exact gradient from the
    forward-backward expected boundary counts, stop on projected gradient < 1e-8 (gtol); RB = 5 starts (the v2 Dirichlet starts, SeedSequence([11801, 5])).
    Global check: a 41 x 41 grid on the logit scale over the same box, on the OBSERVED text. EM (v2, cap 1000) is a printed cross-check only.
(b) Class balance of the hash label on W1; entropy of P(initial state | first glyph) under the frozen step 1.
POWER PREVIEW (non-decisive feasibility check, reserve seed 11806): hash plant at q 0.10 and 0.5 (+ state-aligned plant at q 0.10), each against
20 N-LINE nulls of the planted text. Decision rule frozen beforehand in DECISION_RULE_POWER_PREVIEW.md.
Seeds: 11801 sub-streams (pre-check): default_rng(11801) replicates 1-3 (same as v1/v2); [11801, 3] step-1 restarts (recomputed, identical to v2);
[11801, 5] B starts (identical to v2); [11801, 6] P-NOISE preview nulls 1-20 (same nulls as v2, refitted with L-BFGS-B).
11806 sub-streams (power preview): [11806, 1] hash plant q 0.10 draws; [11806, 2] hash plant q 0.5 draws; [11806, 3] nulls for hash q 0.10;
[11806, 4] nulls for hash q 0.5; [11806, 5] aligned plant q 0.10 draws; [11806, 6] nulls for aligned q 0.10. B starts in the preview: [11801, 5].
- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, hashlib, time
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c119_precheck_s as V2
from c119_precheck_s import nline, fit_word, word_ll, word_mats, line_arrays, line_ll_and_counts, fit_B, flat, pad, devowel_lines, NTOK

SEED, PSEED, RB, GTOL, NREP, NPREV, Q_LO, Q_HI = 11801, 11806, 5, 1e-8, 3, 20, 0.10, 0.5
LO, HI = np.log(1e-6 / (1 - 1e-6)), np.log((1 - 1e-6) / 1e-6)
sig = lambda x: 1 / (1 + np.exp(-x)); logit = lambda p: np.log(p / (1 - p))
Bof = lambda th: np.array([[1 - sig(th[0]), sig(th[0])], [sig(th[1]), 1 - sig(th[1])]])

def negll(th, arr, pi):
    B = Bof(th); ll, xi = line_ll_and_counts(*arr, pi, B); b12, b21 = B[0, 1], B[1, 0]
    g = np.array([xi[0, 1] * (1 - b12) - xi[0, 0] * b12, xi[1, 0] * (1 - b21) - xi[1, 1] * b21])
    return -ll, -g

def fit_B_lbfgs(arr, pi):
    rng = np.random.default_rng(np.random.SeedSequence([SEED, 5])); out = []
    for s in range(RB):
        B0 = rng.dirichlet([1, 1], 2); th0 = np.clip([logit(B0[0, 1]), logit(B0[1, 0])], LO, HI)
        r = minimize(negll, th0, args=(arr, pi), jac=True, method='L-BFGS-B', bounds=[(LO, HI)] * 2,
                     options=dict(gtol=GTOL, ftol=0, maxiter=100000, maxfun=100000))
        _, g = negll(r.x, arr, pi); B = Bof(r.x)
        # projected gradient (zero component when pinned at a bound and pushing outward)
        pg = [0.0 if (x <= LO + 1e-12 and gi > 0) or (x >= HI - 1e-12 and gi < 0) else float(gi) for x, gi in zip(r.x, g)]
        out.append(dict(ll=-float(r.fun), B=B.round(8).tolist(), theta=r.x.tolist(), nit=int(r.nit), nfev=int(r.nfev), success=bool(r.success),
                        message=str(r.message), max_abs_proj_grad=max(abs(x) for x in pg)))
    return out

def S_lbfgs(lines, cache, pi, nb):
    arr = line_arrays(lines, cache); ll0, _ = line_ll_and_counts(*arr, pi, np.tile(pi, (2, 1)))
    F = fit_B_lbfgs(arr, pi); b = int(np.argmax([f['ll'] for f in F])); Ss = [(f['ll'] - ll0) / nb for f in F]
    return dict(ll_reset=ll0, ll_best=F[b]['ll'], S_best=Ss[b], S_starts=Ss, SD_S_starts=float(np.std(Ss, ddof=1)), B_best=F[b]['B'],
                B_ii=[F[b]['B'][0][0], F[b]['B'][1][1]], all_success=all(f['success'] for f in F),
                max_abs_proj_grad=max(f['max_abs_proj_grad'] for f in F), nit=[f['nit'] for f in F], nfev=[f['nfev'] for f in F]), arr, ll0

def grid_check(arr, pi, ll_best):
    xs = np.linspace(LO, HI, 41); G = np.zeros((41, 41))
    for i, a in enumerate(xs):
        for j, b in enumerate(xs): G[i, j] = line_ll_and_counts(*arr, pi, Bof((a, b)))[0]
    i, j = np.unravel_index(np.argmax(G), G.shape)
    return dict(grid_max_ll=float(G.max()), grid_argmax_B12_B21=[float(sig(xs[i])), float(sig(xs[j]))], lbfgs_best_ll=ll_best,
                lbfgs_minus_grid=ll_best - float(G.max()), PASS=bool(ll_best >= G.max() - 1e-9))

def hclass(w): return hashlib.sha256(('11802:' + ''.join(w)).encode()).digest()[0] & 1

def hash_plant(lines, q, rng):
    out, n = [], 0
    for l in lines:
        l = list(l)
        if len(l) >= 5 and rng.random() < q:
            mid = l[1:-1]; first = int(rng.random() < 0.5)          # which class block comes first
            mid = [w for w in mid if hclass(w) == first] + [w for w in mid if hclass(w) != first]
            l = [l[0]] + mid + [l[-1]]; n += 1
        out.append(l)
    return out, n

def last_state(w, sid, pi, A, Em):
    a = pi * Em[:, sid[w[0]]]; a = a / a.sum()
    for u in w[1:]: a = (a @ A) * Em[:, sid[u]]; a = a / a.sum()
    return int(np.argmax(a))

def init_post(g, sid, pi, Em): p = pi * Em[:, sid[g]]; return p / p.sum()

def aligned_plant(lines, q, rng, sid, pi, A, Em):
    out, n = [], 0
    for l in lines:
        l = list(l)
        if len(l) >= 5 and rng.random() < q:
            pool = list(l[1:-1]); chain = [l[0]]
            while pool:
                c = last_state(chain[-1], sid, pi, A, Em)
                k = int(np.argmax([init_post(w[0], sid, pi, Em)[c] for w in pool]))   # ties -> earliest in original order
                chain.append(pool.pop(k))
            l = chain + [l[-1]]; n += 1
        out.append(l)
    return out, n

def rank_p(s, nulls):
    nulls = np.array(nulls); ties = int((np.abs(nulls - s) <= 1e-12).sum())
    return dict(planted_S=s, null_S_min=float(nulls.min()), null_S_max=float(nulls.max()), null_mean=float(nulls.mean()), null_sd=float(nulls.std(ddof=1)),
                rank=float(((nulls < s - 1e-12).sum() + 0.5 * ties) / len(nulls)), p=float((1 + (nulls >= s - 1e-12).sum()) / (1 + len(nulls))),
                top_of_null=bool(s > nulls.max() + 1e-12), z=float((s - nulls.mean()) / nulls.std(ddof=1)))

if __name__ == '__main__':
    t0 = time.time(); outp = sys.argv[1]
    lines = devowel_lines('Latin_Caesar', NTOK); obs = flat(lines)
    syms = sorted({u for w in obs for u in w}); sid = {u: i for i, u in enumerate(syms)}; nb = sum(len(l) - 1 for l in lines)
    ids = np.array([sid[u] for w in obs for u in w]); wid = np.array([k for k, w in enumerate(obs) for _ in w]); X, M = pad(ids, wid)
    rng1 = np.random.default_rng(np.random.SeedSequence([SEED, 3]))
    F1 = [fit_word(X, M, len(syms), rng1) for _ in range(10)]; P = F1[int(np.argmax([f['ll'] for f in F1]))]
    pi, A, Em = P['pi'], P['A'], P['Em']; cache = word_mats(set(obs), sid, A, Em)
    R = dict(text='CAE-DV W1', control_only=True, manuscript_loaded=False, n_word_boundaries=nb, step1_best_ll=P['ll'],
             step1_A=A.round(6).tolist(), step1_pi=pi.round(6).tolist(), gtol=GTOL, bounds_prob=[1e-6, 1 - 1e-6])
    # (b) diagnostics
    types = sorted(set(obs)); ct = [sum(hclass(w) == c for w in types) for c in (0, 1)]; ck = [sum(hclass(w) == c for w in obs) for c in (0, 1)]
    R['hash_class_balance'] = dict(types=dict(class0=ct[0], class1=ct[1], share1=ct[1] / len(types)), tokens=dict(class0=ck[0], class1=ck[1], share1=ck[1] / len(obs)))
    H = lambda p: float(-(p * np.log2(np.clip(p, 1e-300, 1))).sum())
    ent_all = [H(init_post(w[0], sid, pi, Em)) for w in obs]; ent_b = [H(init_post(w[0], sid, pi, Em)) for l in lines for w in l[1:]]
    gl = sorted({w[0] for w in obs}); R['init_state_entropy_bits'] = dict(
        token_mean_all_words=float(np.mean(ent_all)), token_mean_words_after_boundary=float(np.mean(ent_b)),
        type_mean_first_glyphs=float(np.mean([H(init_post(g, sid, pi, Em)) for g in gl])),
        per_first_glyph={g: [round(float(x), 6) for x in init_post(g, sid, pi, Em)] for g in gl}, note='max 1 bit (K = 2)')
    print('diag', json.dumps({k: R[k] for k in ('hash_class_balance',)}), json.dumps({k: v for k, v in R['init_state_entropy_bits'].items() if k != 'per_first_glyph'}), flush=True)
    # (a) invariance pre-check with L-BFGS-B + grid + EM cross-check
    rs = np.random.default_rng(SEED); reps = [nline(lines, rs) for _ in range(NREP)]; T = {}
    for name, ls in [('obs', lines)] + [(f'rep{r + 1}', sh) for r, sh in enumerate(reps)]:
        d, arr, ll0 = S_lbfgs(ls, cache, pi, nb)
        em = fit_B(*arr, pi, np.random.SeedSequence([SEED, 5])); emb = max(e['ll'] for e in em)
        d['EM_crosscheck'] = dict(EM_best_ll=emb, abs_dll_lbfgs_minus_EM=abs(d['ll_best'] - emb), lbfgs_minus_EM=d['ll_best'] - emb,
                                  EM_iters=[e['iters'] for e in em])
        if name == 'obs': d['grid_check'] = grid_check(arr, pi, d['ll_best'])
        T[name] = d; print(name, json.dumps(d), flush=True)
    So = T['obs']['S_best']; Sr = [T[f'rep{r + 1}']['S_best'] for r in range(NREP)]
    R['texts'] = T; R['precheck'] = dict(S_obs=So, S_reps=Sr, dS=[s - So for s in Sr], Var_S_reps=float(np.var(Sr, ddof=1)), SD_S_reps=float(np.std(Sr, ddof=1)),
        SD_S_starts_obs=T['obs']['SD_S_starts'], max_SD_S_starts_any=max(v['SD_S_starts'] for v in T.values()),
        PASS=bool(all(abs(s - So) * nb > 1e-3 for s in Sr) and len({round(s, 9) for s in [So] + Sr}) >= 2))
    print('precheck', json.dumps(R['precheck']), flush=True)
    # P-NOISE preview (same 20 nulls as v2) with the new fitter
    rp = np.random.default_rng(np.random.SeedSequence([SEED, 6])); pv = [S_lbfgs(nline(lines, rp), cache, pi, nb)[0] for _ in range(NPREV)]
    Sn = [v['S_best'] for v in pv]
    R['pnoise_preview'] = dict(label='PRE-REGISTRATION FEASIBILITY CHECK ON A CONTROL (CAE-DV W1 only); decides nothing', S_null=Sn, SD_S_null=float(np.std(Sn, ddof=1)),
        SD_S_starts_obs=T['obs']['SD_S_starts'], max_SD_S_starts_nulls=max(v['SD_S_starts'] for v in pv), all_success=all(v['all_success'] for v in pv),
        max_abs_proj_grad=max(v['max_abs_proj_grad'] for v in pv), **{'obs_vs_nulls': rank_p(So, Sn)})
    print('pnoise', json.dumps(R['pnoise_preview']), flush=True)
    # POWER PREVIEW (11806)
    def preview(label, planted, nplanted, null_sub):
        d = S_lbfgs(planted, cache, pi, nb)[0]; rn = np.random.default_rng(np.random.SeedSequence([PSEED, null_sub]))
        nl = [S_lbfgs(nline(planted, rn), cache, pi, nb)[0] for _ in range(NPREV)]
        out = dict(label=label, lines_planted=nplanted, planted=dict(S=d['S_best'], B_ii=d['B_ii'], SD_S_starts=d['SD_S_starts']),
                   null_S=[v['S_best'] for v in nl], all_success=all(v['all_success'] for v in nl + [d]), **rank_p(d['S_best'], [v['S_best'] for v in nl]))
        print('power', json.dumps(out), flush=True); return out
    PW = {}
    for q, ps, ns in ((Q_LO, 1, 3), (Q_HI, 2, 4)):
        pl, n = hash_plant(lines, q, np.random.default_rng(np.random.SeedSequence([PSEED, ps])))
        for a, b in zip(pl, lines): assert sorted(a) == sorted(b) and a[0] == b[0] and a[-1] == b[-1]
        PW[f'hash_q{q}'] = preview(f'hash plant q={q}', pl, n, ns)
    pl, n = aligned_plant(lines, Q_LO, np.random.default_rng(np.random.SeedSequence([PSEED, 5])), sid, pi, A, Em)
    for a, b in zip(pl, lines): assert sorted(a) == sorted(b) and a[0] == b[0] and a[-1] == b[-1]
    PW['aligned_q0.1'] = preview('state-aligned plant q=0.1', pl, n, 6)
    R['power_preview'] = dict(label='NON-DECISIVE FEASIBILITY CHECK ON A CONTROL (CAE-DV W1 only); p floor 1/21', **PW)
    R['seconds'] = round(time.time() - t0, 1)
    json.dump(R, open(outp, 'w'), indent=1); print('seconds', R['seconds'])
