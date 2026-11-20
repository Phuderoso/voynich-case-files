#!/usr/bin/env python3
"""C119 DRAFT v2, mandatory invariance pre-check + P-NOISE feasibility preview with the PRIMARY statistic S
(Kryptos's P5, blind review 19 Nov 2026). CONTROL TEXT ONLY: devowelled Caesar W1. The manuscript is never loaded.
Step 1: C117 model (2-state HMM, reset at every word: A, pi, emissions), R1 EM restarts, cap NITER1 = 500, on the OBSERVED text once.
        Its fit depends only on the word multiset (C118 Amendment 1), so it is reused for every N-LINE replicate.
Step 2: A, pi, emissions frozen; only B (2x2, last glyph of word k -> first glyph of word k+1, same line) is fitted by EM,
        RB starts, cap 1000 iterations, stop when the ll gain < TOLB nats.
S = (ll(B fitted) - ll(B rows = pi, i.e. reset)) / n_word_boundaries.  ll(B = reset) == C117 word-reset ll (anchor A1 = zero point of S).
Seeds (all sub-streams of the C119 pre-check seed 11801):
  N-LINE replicates 1-3: default_rng(11801)  (the SAME 3 replicates as the v1 pre-check, reused on purpose);
  step-1 restarts: SeedSequence([11801, 3]); B-EM starts: SeedSequence([11801, 5]) (identical starts for every text);
  P-NOISE preview nulls 1-20: default_rng(SeedSequence([11801, 6])).
- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, hashlib, time
import numpy as np
VCF = os.environ.get('VCF', '/workspace/vcf-c104')
sys.path.insert(0, os.path.join(VCF, 'tools'))
from c108_sukhotin_alternation import flat
from c111_hmm_sukhotin_convergence import pad, TOL
from c115_hmm_switch_currier import devowel_lines, NTOK

SEED, K, R1, NITER1, RB, NITERB, TOLB, NREP, NPREV = 11801, 2, 10, 500, 5, 1000, 1e-7, 3, 20

def nline(lines, rng):
    out = []
    for l in lines:
        l = list(l)
        if len(l) >= 5:
            mid = l[1:-1]; perm = rng.permutation(len(mid)); l = [l[0]] + [mid[i] for i in perm] + [l[-1]]
        out.append(l)
    return out

def fit_word(X, M, S, rng):
    """C111/C117 free EM (word rows), returning parameters; cap NITER1"""
    W, L = X.shape; pi = rng.dirichlet([1, 1]); A = rng.dirichlet([1, 1], 2); Em = rng.dirichlet(np.ones(S), 2); last = -np.inf
    for it in range(NITER1):
        al = np.zeros((W, L, 2)); c = np.ones((W, L))
        a = pi[None] * Em[:, X[:, 0]].T; c[:, 0] = a.sum(1); al[:, 0] = a / c[:, :1]
        for t in range(1, L):
            a = (al[:, t - 1] @ A) * Em[:, X[:, t]].T; s = a.sum(1); m = M[:, t]
            c[m, t] = s[m]; al[m, t] = a[m] / s[m, None]; al[~m, t] = al[~m, t - 1]
        be = np.ones((W, L, 2)); xi = np.zeros((2, 2))
        for t in range(L - 2, -1, -1):
            m = M[:, t + 1]; e = Em[:, X[:, t + 1]].T * be[:, t + 1]
            b = (e @ A.T) / c[:, t + 1:t + 2]; be[m, t] = b[m]
            xi += np.einsum('wi,ij,wj->ij', al[m, t], A, e[m] / c[m, t + 1:t + 2])
        ll = float(np.log(c[M]).sum())
        if ll - last < TOL * abs(ll): break          # converged at these parameters (C111 rule)
        last = ll; g = al * be; g = g / g.sum(2, keepdims=True)
        pi = g[:, 0].mean(0); A = xi / xi.sum(1, keepdims=True)
        Bn = np.zeros((2, S)); np.add.at(Bn.T, X[M], g[M]); Em = (Bn + 1e-12) / (Bn + 1e-12).sum(1, keepdims=True)
    return dict(ll=ll, pi=pi, A=A, Em=Em, iters=it + 1, hit_cap=bool(it + 1 == NITER1 and not (ll - last < TOL * abs(ll))))

def word_ll(X, M, pi, A, Em):
    """independent code path: C117 word-row forward pass at fixed parameters"""
    W, L = X.shape; a = pi[None] * Em[:, X[:, 0]].T; ll = np.log(a.sum(1)).sum(); a = a / a.sum(1, keepdims=True)
    for t in range(1, L):
        b = (a @ A) * Em[:, X[:, t]].T; s = b.sum(1); m = M[:, t]; ll += np.log(s[m]).sum(); a[m] = b[m] / s[m, None]
    return float(ll)

def word_mats(words, sid, A, Em):
    """per word type: log-scale + normalised 2x2 matrix W[i,j] = P(glyphs, end state j | start state i)"""
    cache = {}
    for w in set(words):
        g = [sid[u] for u in w]; Mx = np.diag(Em[:, g[0]]); ls = 0.0
        for x in g[1:]:
            Mx = Mx @ A @ np.diag(Em[:, x]); s = Mx.sum(); ls += np.log(s); Mx = Mx / s
        cache[w] = (Mx, ls)
    return cache

def line_arrays(lines, cache):
    N = len(lines); Kw = max(map(len, lines)); Wm = np.tile(np.eye(2), (N, Kw, 1, 1)); LS = np.zeros((N, Kw)); Mk = np.zeros((N, Kw), bool)
    for r, l in enumerate(lines):
        for k, w in enumerate(l): Wm[r, k], LS[r, k] = cache[w]; Mk[r, k] = True
    return Wm, LS, Mk

def line_ll_and_counts(Wm, LS, Mk, pi, B):
    N, Kw = Mk.shape; al = np.zeros((N, Kw, 2)); c = np.ones((N, Kw))
    a = np.einsum('i,nij->nj', pi, Wm[:, 0]); c[:, 0] = a.sum(1); al[:, 0] = a / c[:, :1]
    for k in range(1, Kw):
        a = np.einsum('ni,ij,njl->nl', al[:, k - 1], B, Wm[:, k]); s = a.sum(1); m = Mk[:, k]
        c[m, k] = s[m]; al[m, k] = a[m] / s[m, None]; al[~m, k] = al[~m, k - 1]
    be = np.ones((N, Kw, 2)); xi = np.zeros((2, 2))
    for k in range(Kw - 1, 0, -1):
        m = Mk[:, k]; e = np.einsum('njl,nl->nj', Wm[:, k], be[:, k])     # (W_k beta_k)[j]
        b = np.einsum('ij,nj->ni', B, e) / c[:, k:k + 1]; be[m, k - 1] = b[m]
        xi += np.einsum('ni,ij,nj->ij', al[m, k - 1], B, e[m] / c[m, k:k + 1])
    ll = float(np.log(c[Mk]).sum() + LS[Mk].sum())
    return ll, xi

def fit_B(Wm, LS, Mk, pi, ss):
    rng = np.random.default_rng(ss); out = []
    for s in range(RB):
        B = rng.dirichlet([1, 1], 2); last = -np.inf
        for it in range(NITERB):
            ll, xi = line_ll_and_counts(Wm, LS, Mk, pi, B)
            if ll - last < TOLB: break
            last = ll; B = xi / xi.sum(1, keepdims=True)
        out.append(dict(ll=ll, B=B.round(6).tolist(), iters=it + 1, hit_cap=it + 1 == NITERB))
    return out

def S_of(lines, cache, pi, nb):
    Wm, LS, Mk = line_arrays(lines, cache)
    ll0, _ = line_ll_and_counts(Wm, LS, Mk, pi, np.tile(pi, (2, 1)))        # B = reset to pi
    fits = fit_B(Wm, LS, Mk, pi, np.random.SeedSequence([SEED, 5]))
    Ss = [(f['ll'] - ll0) / nb for f in fits]; b = int(np.argmax([f['ll'] for f in fits]))
    return dict(ll_reset=round(ll0, 6), S_best=Ss[b], S_starts=Ss, SD_S_starts=float(np.std(Ss, ddof=1)),
                B_best=fits[b]['B'], B_ii=[fits[b]['B'][0][0], fits[b]['B'][1][1]], B_iters=[f['iters'] for f in fits],
                B_hit_cap=sum(f['hit_cap'] for f in fits))

if __name__ == '__main__':
    t0 = time.time()
    lines = devowel_lines('Latin_Caesar', NTOK); obs = flat(lines)
    syms = sorted({u for w in obs for u in w}); sid = {u: i for i, u in enumerate(syms)}
    tok_sha = hashlib.sha256('\n'.join(' '.join(''.join(w) for w in l) for l in lines).encode()).hexdigest()
    nb = sum(len(l) - 1 for l in lines)
    ids = np.array([sid[u] for w in obs for u in w]); wid = np.array([k for k, w in enumerate(obs) for _ in w]); X, M = pad(ids, wid)
    rng1 = np.random.default_rng(np.random.SeedSequence([SEED, 3]))
    F = [fit_word(X, M, len(syms), rng1) for _ in range(R1)]; bi = int(np.argmax([f['ll'] for f in F])); P = F[bi]
    res = dict(text='CAE-DV W1', control_only=True, manuscript_loaded=False, text_sha256=tok_sha, word_tokens=len(obs), lines=len(lines),
               glyph_tokens=int(M.sum()), n_word_boundaries=nb, K=K, R1=R1, NITER1=NITER1, RB=RB, NITERB=NITERB, TOLB=TOLB,
               seeds=dict(replicates_1_3='default_rng(11801) (same 3 replicates as v1)', step1='SeedSequence([11801, 3])',
                          B_starts='SeedSequence([11801, 5]) identical for every text', preview_nulls='default_rng(SeedSequence([11801, 6]))'),
               step1=dict(lls=[round(f['ll'], 3) for f in F], best=round(P['ll'], 6), iters=[f['iters'] for f in F],
                          hit_cap_frac=sum(f['hit_cap'] for f in F) / R1, A=P['A'].round(6).tolist(), pi=P['pi'].round(6).tolist()))
    # A1: ll(B = reset) via the line path must equal the word-row C117 forward pass at the same parameters
    cache = word_mats(set(obs), sid, P['A'], P['Em'])
    Wm, LS, Mk = line_arrays(lines, cache); ll_line0, _ = line_ll_and_counts(Wm, LS, Mk, P['pi'], np.tile(P['pi'], (2, 1)))
    ll_word = word_ll(X, M, P['pi'], P['A'], P['Em'])
    res['A1'] = dict(ll_line_reset=ll_line0, ll_word_rows=ll_word, abs_diff=abs(ll_line0 - ll_word), PASS=abs(ll_line0 - ll_word) < 1e-6)
    print('step1', json.dumps(res['step1']), '\nA1', res['A1'], flush=True)
    rs = np.random.default_rng(SEED); reps = [nline(lines, rs) for _ in range(NREP)]
    T = {'obs': S_of(lines, cache, P['pi'], nb)}
    for r, sh in enumerate(reps):
        for a, b in zip(sh, lines): assert sorted(a) == sorted(b) and a[0] == b[0] and a[-1] == b[-1] and (len(b) >= 5 or a == b)
        T[f'rep{r + 1}'] = S_of(sh, cache, P['pi'], nb); T[f'rep{r + 1}']['word_tokens_moved'] = sum(a != b for a, b in zip(flat(sh), obs))
    for k, v in T.items(): print(k, json.dumps(v), flush=True)
    Sr = [T[f'rep{r + 1}']['S_best'] for r in range(NREP)]; So = T['obs']['S_best']
    dS = [s - So for s in Sr]; sd_starts = T['obs']['SD_S_starts']
    res['texts'] = T
    res['precheck'] = dict(S_obs=So, S_reps=Sr, dS=dS, Var_S_reps=float(np.var(Sr, ddof=1)), SD_S_reps=float(np.std(Sr, ddof=1)),
                           SD_S_starts_obs=sd_starts, max_SD_S_starts_any_text=max(v['SD_S_starts'] for v in T.values()),
                           S_distinct=len({round(s, 9) for s in [So] + Sr}),
                           PASS=bool(all(abs(d) * nb > 1e-3 for d in dS) and len({round(s, 9) for s in [So] + Sr}) >= 2))
    print('precheck', json.dumps(res['precheck']), flush=True)
    # P-NOISE feasibility preview (control only, pre-registration feasibility, decides nothing)
    rp = np.random.default_rng(np.random.SeedSequence([SEED, 6])); pv = []
    for r in range(NPREV):
        sh = nline(lines, rp); v = S_of(sh, cache, P['pi'], nb); pv.append(v)
    Sn = np.array([v['S_best'] for v in pv]); sdn = float(Sn.std(ddof=1))
    res['pnoise_preview'] = dict(label='PRE-REGISTRATION FEASIBILITY CHECK ON A CONTROL (CAE-DV W1 only); decides nothing', n_null=NPREV,
                                 S_null=Sn.tolist(), null_mean=float(Sn.mean()), SD_S_null=sdn, SD_S_starts_obs=sd_starts,
                                 max_SD_S_starts_over_nulls=max(v['SD_S_starts'] for v in pv), ratio_null_over_starts=(sdn / sd_starts) if sd_starts > 0 else None,
                                 would_pass_P_NOISE=bool(sdn > sd_starts), obs_rank=(float((Sn < So).sum() + 0.5 * (np.abs(Sn - So) <= 1e-12).sum()) / NPREV),
                                 B_hit_cap_total=sum(v['B_hit_cap'] for v in pv), distinct_frac=len(np.unique(np.round(Sn, 9))) / NPREV)
    res['seconds'] = round(time.time() - t0, 1)
    print('pnoise', json.dumps(res['pnoise_preview']), flush=True)
    json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else 'precheck_c119_S.json', 'w'), indent=1)
