#!/usr/bin/env python3
"""C119 DRAFT, mandatory invariance pre-check (CONTROL TEXT ONLY: devowelled Caesar W1; the manuscript is never loaded).
Instrument (Kryptos's boundary design, 19 Nov 2026): a 2-state HMM over each LINE's glyph stream.
  A = within-word transition (glyph t-1 and t in the same word); constrained family clamps A_ii >= DMIN = 0.90 after each M-step (C117).
  B = boundary transition (last glyph of a word -> first glyph of the next word in the same line); K x K, FREE in both families.
  pi = line-initial distribution; emissions shared. EM as C111/C117 (NITER 150, relative TOL 1e-6).
  Descriptive variant 'tied': one matrix crosses the boundary (B := A, clamped with A in the constrained family).
Statistic T = (best ll constrained - best ll free) / n_glyph_tokens.
Pre-check: observed W1 and 3 N-LINE replicates (middle words shuffled within the line, first/last fixed, lines L <= 4 fixed),
SAME EM initialisation for all four texts; PASS iff every replicate has |dll| > EPS_LL in both families' best ll (primary design)
and the four T values are not all equal (rounded 1e-6).  Seed 11801 (C119 block).
- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json, hashlib, time
import numpy as np
VCF = os.environ.get('VCF', '/workspace/vcf-c104')
sys.path.insert(0, os.path.join(VCF, 'tools'))
from c108_sukhotin_alternation import flat
from c111_hmm_sukhotin_convergence import NITER, TOL
from c115_hmm_switch_currier import devowel_lines, NTOK

SEED, NREP, R, DMIN, EPS_LL, K = 11801, 3, 3, 0.90, 1e-3, 2

def nline(lines, rng):
    out = []
    for l in lines:
        l = list(l)
        if len(l) >= 5:
            mid = l[1:-1]; perm = rng.permutation(len(mid)); l = [l[0]] + [mid[i] for i in perm] + [l[-1]]
        out.append(l)
    return out

def pad_lines(lines, sid):
    """one LINE per row; bd[r, t] = True when the transition (t-1 -> t) crosses a word boundary"""
    seqs = [[sid[u] for w in l for u in w] for l in lines]
    bds = []
    for l in lines:
        b = []
        for k, w in enumerate(l):
            for j in range(len(w)): b.append(k > 0 and j == 0)
        bds.append(b)
    Lm = max(map(len, seqs)); N = len(seqs)
    X = np.zeros((N, Lm), np.int64); Mk = np.zeros((N, Lm), bool); BD = np.zeros((N, Lm), bool)
    for r, (s, b) in enumerate(zip(seqs, bds)):
        X[r, :len(s)] = s; Mk[r, :len(s)] = True; BD[r, :len(b)] = b
    return X, Mk, BD

def fit(X, Mk, BD, S, rng, sticky, tied=False):
    N, L = X.shape; pi = rng.dirichlet([1] * K); A = rng.dirichlet([1] * K, K); Bt = rng.dirichlet([1] * K, K)
    Em = rng.dirichlet(np.ones(S), K)
    def clamp(A):
        if not sticky: return A
        A = A.copy()
        for i in range(K):
            if A[i, i] < DMIN: A[i, i] = DMIN; A[i, 1 - i] = 1 - DMIN
        return A
    A = clamp(A)
    if tied: Bt = A
    last = -np.inf
    for it in range(NITER):
        al = np.zeros((N, L, K)); c = np.ones((N, L))
        a = pi[None] * Em[:, X[:, 0]].T; c[:, 0] = a.sum(1); al[:, 0] = a / c[:, :1]
        for t in range(1, L):
            prev = al[:, t - 1]; tr = np.where(BD[:, t, None], prev @ Bt, prev @ A)
            a = tr * Em[:, X[:, t]].T; s = a.sum(1); m = Mk[:, t]
            c[m, t] = s[m]; al[m, t] = a[m] / s[m, None]; al[~m, t] = al[~m, t - 1]
        be = np.ones((N, L, K)); xA = np.zeros((K, K)); xB = np.zeros((K, K))
        for t in range(L - 2, -1, -1):
            m = Mk[:, t + 1]; e = Em[:, X[:, t + 1]].T * be[:, t + 1]; bd = BD[:, t + 1]
            b = np.where(bd[:, None], e @ Bt.T, e @ A.T) / c[:, t + 1:t + 2]; be[m, t] = b[m]
            mA = m & ~bd; mB = m & bd
            xA += np.einsum('wi,ij,wj->ij', al[mA, t], A, e[mA] / c[mA, t + 1:t + 2])
            xB += np.einsum('wi,ij,wj->ij', al[mB, t], Bt, e[mB] / c[mB, t + 1:t + 2])
        ll = float(np.log(c[Mk]).sum()); g = al * be; g = g / g.sum(2, keepdims=True)
        pi = g[:, 0].mean(0)
        if tied: A = clamp((xA + xB) / (xA + xB).sum(1, keepdims=True)); Bt = A
        else: A = clamp(xA / xA.sum(1, keepdims=True)); Bt = xB / xB.sum(1, keepdims=True)
        En = np.zeros((K, S)); np.add.at(En.T, X[Mk], g[Mk]); Em = (En + 1e-12) / (En + 1e-12).sum(1, keepdims=True)
        if ll - last < TOL * abs(ll): break
        last = ll
    return round(ll, 6), round(float(np.diag(A).min()), 5), it + 1

def fams(lines, syms, ss, tied=False):
    sid = {u: i for i, u in enumerate(syms)}; X, Mk, BD = pad_lines(lines, sid); rng = np.random.default_rng(ss)
    F = [fit(X, Mk, BD, len(syms), rng, False, tied) for _ in range(R)]; C = [fit(X, Mk, BD, len(syms), rng, True, tied) for _ in range(R)]
    n = int(Mk.sum()); lf, lc = [f[0] for f in F], [x[0] for x in C]
    return dict(free=lf, con=lc, best_free=max(lf), best_con=max(lc), T=round((max(lc) - max(lf)) / n, 8), n=n,
                n_boundaries=int(BD.sum()), iters_free=[f[2] for f in F], iters_con=[x[2] for x in C],
                con_min_Aii=[x[1] for x in C])

if __name__ == '__main__':
    t0 = time.time()
    lines = devowel_lines('Latin_Caesar', NTOK); obs = flat(lines)
    syms = sorted({u for w in obs for u in w})          # FIXED symbol order: same glyph -> same id in every replicate
    tok_sha = hashlib.sha256('\n'.join(' '.join(''.join(w) for w in l) for l in lines).encode()).hexdigest()
    mov_lines = [l for l in lines if len(l) >= 5]
    res = dict(text='CAE-DV W1 (devowel_lines(Latin_Caesar, 10000))', control_only=True, manuscript_loaded=False,
               word_tokens=len(obs), lines=len(lines), glyph_tokens=sum(len(w) for w in obs), text_sha256=tok_sha,
               within_line_boundaries=sum(len(l) - 1 for l in lines),
               boundaries_in_movable_lines=sum(len(l) - 1 for l in mov_lines),
               movable_lines=len(mov_lines), movable_word_share=round(sum(len(l) - 2 for l in mov_lines) / len(obs), 4),
               seed=SEED, shuffle_stream='default_rng(11801)', em_init='SeedSequence([11801, 1]) for every text (identical init)',
               em_init_tied='SeedSequence([11801, 2])', R_free=R, R_con=R, DMIN=DMIN, EPS_LL=EPS_LL, K=K, NITER=NITER, TOL=TOL)
    rs = np.random.default_rng(SEED); reps = []
    for r in range(NREP):
        sh = nline(lines, rs)
        for a, b in zip(sh, lines):
            assert sorted(a) == sorted(b) and a[0] == b[0] and a[-1] == b[-1] and (len(b) >= 5 or a == b)
        reps.append(sh)
    texts = [('obs', lines)] + [(f'rep{r + 1}', sh) for r, sh in enumerate(reps)]
    out = {}
    for name, ls in texts:
        P = fams(ls, syms, np.random.SeedSequence([SEED, 1]))
        Tt = fams(ls, syms, np.random.SeedSequence([SEED, 2]), tied=True)
        moved = sum(a != b for a, b in zip(flat(ls), obs))
        out[name] = dict(word_tokens_moved=moved, primary=P, tied_descriptive=Tt); print(name, json.dumps(out[name]), flush=True)
    o = out['obs']
    for name in out:
        if name == 'obs': continue
        for v in ('primary', 'tied_descriptive'):
            d = out[name][v]; d['dll_best_free'] = round(d['best_free'] - o[v]['best_free'], 6)
            d['dll_best_con'] = round(d['best_con'] - o[v]['best_con'], 6)
            d['max_abs_dll_same_restart'] = round(max(abs(a - b) for a, b in zip(d['free'] + d['con'], o[v]['free'] + o[v]['con'])), 6)
    def verdict(v):
        dl = all(abs(out[n][v]['dll_best_free']) > EPS_LL and abs(out[n][v]['dll_best_con']) > EPS_LL for n in out if n != 'obs')
        Ts = [out[n][v]['T'] for n in out]; distinct = len({round(t, 6) for t in Ts})
        return dict(dll_nonzero_all_reps=dl, T_values=Ts, T_distinct=distinct, T_variable=distinct >= 2, PASS=bool(dl and distinct >= 2))
    res['texts'] = out; res['precheck_primary'] = verdict('primary'); res['tied_descriptive_check'] = verdict('tied_descriptive')
    res['seconds'] = round(time.time() - t0, 1)
    print(json.dumps(dict(primary=res['precheck_primary'], tied=res['tied_descriptive_check']), indent=1))
    json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else 'precheck_c119.json', 'w'), indent=1)
