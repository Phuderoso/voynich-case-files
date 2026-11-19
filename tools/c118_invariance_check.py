#!/usr/bin/env python3
"""C118 amendment check (control text only, no manuscript): is the C117 instrument invariant under N-LINE?
The C111/C117 HMM (pad + fit) treats every WORD as an independent glyph sequence (forward pass restarts at each word, pi re-estimated
from word-initial posteriors), so the likelihood is a sum over words and cannot depend on word order.  N-LINE only permutes whole
words, so every N-LINE replicate has the observed word multiset -> identical likelihood surface -> T_null == T_obs by construction.
This script demonstrates it numerically on CAE-DV W1 (C118's main control): identical EM initialisation on the observed text and on
N-LINE replicates must give identical best log-likelihoods (to float rounding).  Seed 11797 (C118 reserve block).
- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from c108_sukhotin_alternation import encode, flat
from c111_hmm_sukhotin_convergence import pad
from c115_hmm_switch_currier import devowel_lines, NTOK
from c117_hmm_constrained_gap import fit

SEED, NREP, R = 11797, 3, 3

def nline(lines, rng):
    out = []
    for l in lines:
        l = list(l)
        if len(l) >= 5:
            mid = l[1:-1]; perm = rng.permutation(len(mid)); l = [l[0]] + [mid[i] for i in perm] + [l[-1]]
        out.append(l)
    return out

def fits(words, ss):
    # encode by a FIXED symbol order (sorted), so the same glyph gets the same id in every replicate
    syms = sorted({u for w in words for u in w}); sid = {u: i for i, u in enumerate(syms)}
    ids = np.array([sid[u] for w in words for u in w]); wid = np.array([k for k, w in enumerate(words) for _ in w])
    X, M = pad(ids, wid); rng = np.random.default_rng(ss)
    F = [fit(X, M, len(syms), rng, False) for _ in range(R)]; C = [fit(X, M, len(syms), rng, True) for _ in range(R)]
    return [f[0] for f in F], [c[0] for c in C], len(ids)

if __name__ == '__main__':
    lines = devowel_lines('Latin_Caesar', NTOK); obs = flat(lines); rs = np.random.default_rng(SEED)
    mov = sum(len(l) for l in lines if len(l) >= 5) / len(obs)
    res = dict(text='CAE-DV W1', tokens=len(obs), lines=len(lines), movable_token_share_incl_fixed_ends=round(mov, 4), seed=SEED, R=R)
    lf, lc, n = fits(obs, np.random.SeedSequence([SEED, 1])); res['obs'] = dict(free=lf, con=lc, T=(max(lc) - max(lf)) / n)
    res['replicates'] = []
    for r in range(NREP):
        sh = flat(nline(lines, rs)); changed = sum(a != b for a, b in zip(sh, obs))
        assert sorted(sh) == sorted(obs)
        lf2, lc2, _ = fits(sh, np.random.SeedSequence([SEED, 1]))   # SAME init as observed
        res['replicates'].append(dict(rep=r + 1, tokens_moved=changed, free=lf2, con=lc2, T=(max(lc2) - max(lf2)) / n,
                                      max_abs_ll_diff=max(abs(a - b) for a, b in zip(lf + lc, lf2 + lc2))))
    print(json.dumps(res, indent=1)); json.dump(res, open('audits/c118-invariance/invariance.json', 'w'), indent=1)
