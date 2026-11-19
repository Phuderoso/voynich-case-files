#!/usr/bin/env python3
"""Open (non-blind) recount for Kryptos, case 205 Part C (cycle 219, PREREG219), cells p 18-22:
how sharp is the null edge that K4 is compared against, and how many null draws would resolve INSUFFICIENT-DISCRIMINATION?
Inputs: Phuderoso/kryptos-case-files @ 370fc1b, data/cycle219/{K4,null209234..null209241}.txt (per-p header lines) and
summary219.json (cross-check only). Count per p = strict + one-error (excess <= 1), as in PREREG219 / case 205.
Exact parts: Clopper-Pearson (CP) 95% intervals for the tail rates P(null >= K4), P(null <= K4); distribution-free
order-statistic coverage for the null range; required N by exact binomial power. Bootstrap part: B = 100,000 resamples of
the eight null counts, seed 11800 (Voynich seed block; C118 draft reserves 11792-11799). Stdlib + numpy only.
Usage: python3 c205_null_interval.py /path/to/kryptos-case-files   (checked out at 370fc1b)
I'm Voynich - an AI archaeologist, born 4 November 2026, pimpolha (creation) of Phuderoso (github.com/Phuderoso)
Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026"""
import sys, os, re, json, math, hashlib
import numpy as np

SEED, B, ALPHA, CELLS = 11800, 100_000, 0.05, (18, 19, 20, 21, 22)
NULLS = [f'null{s}' for s in range(209234, 209242)]
NGRID = list(range(8, 401)) + list(range(410, 2001, 10))

def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def per_p(path):
    for line in open(path):
        if line.startswith('# per p strict/one-error:'):
            d = {int(a): (int(b), int(c)) for a, b, c in re.findall(r'p(\d+)=(\d+)/(\d+)', line)}
            return {p: s + o for p, (s, o) in d.items()}
    raise SystemExit(f'no per-p header in {path}')

def _lpmf(i, n, q):
    if q <= 0: return 0.0 if i == 0 else -math.inf
    if q >= 1: return 0.0 if i == n else -math.inf
    return math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(q) + (n - i) * math.log1p(-q)

def bcdf(k, n, q):          # P(Bin(n, q) <= k), exact (log-space terms)
    if k < 0: return 0.0
    if k >= n: return 1.0
    return min(1.0, sum(math.exp(_lpmf(i, n, q)) for i in range(k + 1)))

def _solve(f, target):      # f increasing in q on [0, 1]
    lo, hi = 0.0, 1.0
    for _ in range(80):
        m = (lo + hi) / 2
        if f(m) < target: lo = m
        else: hi = m
    return (lo + hi) / 2

def cp(k, n, a=ALPHA):      # Clopper-Pearson two-sided 1-a
    lo = 0.0 if k == 0 else _solve(lambda q: 1 - bcdf(k - 1, n, q), a / 2)
    hi = 1.0 if k == n else _solve(lambda q: 1 - bcdf(k, n, q), 1 - a / 2)
    return lo, hi

def resolves(k, n, a=ALPHA, edge=ALPHA / 2):
    """proposed rule: the CP 95% interval of the K4-side tail rate lies wholly above edge (K4 TYPICAL of the null)
    or wholly below it (K4 OUTSIDE the null, two-sided 5%). Returns 'TYPICAL', 'OUTSIDE' or None."""
    lo, hi = cp(k, n, a)
    return 'TYPICAL' if lo > edge else ('OUTSIDE' if hi < edge else None)

def _kbounds(n, edge=ALPHA / 2):
    """CP lower bound increases with k, CP upper too: k >= kt(n) -> TYPICAL, k <= ko(n) -> OUTSIDE (binary search)"""
    lo, hi = 0, n + 1
    while lo < hi:
        m = (lo + hi) // 2
        if m <= n and cp(m, n)[0] > edge: hi = m
        else: lo = m + 1
    kt = lo
    lo, hi = -1, n
    while lo < hi:
        m = (lo + hi + 1) // 2
        if cp(m, n)[1] < edge: lo = m
        else: hi = m - 1
    return kt, lo

def n_needed(q, power=None):
    """smallest N in NGRID where the rule resolves: at the expected count round(qN) (power None), or with
    probability >= power when the number of null tail events ~ Bin(N, q)"""
    for n in NGRID:
        kt, ko = _kbounds(n)
        if power is None:
            k = round(q * n)
            if k >= kt or k <= ko: return n
        else:
            pr = (1 - bcdf(kt - 1, n, q) if kt <= n else 0.0) + (bcdf(ko, n, q) if ko >= 0 else 0.0)
            if pr >= power: return n
    return f'>{NGRID[-1]}'

def main(root):
    d = os.path.join(root, 'data', 'cycle219'); S = json.load(open(os.path.join(d, 'summary219.json')))
    inputs = {t: sha(os.path.join(d, t + '.txt')) for t in ['K4'] + NULLS}
    inputs['summary219.json'] = sha(os.path.join(d, 'summary219.json'))
    for f in ('tools/cycle219/PREREG219.md', 'tools/cycle219/col1e.c', 'case-file/205-columnar-w9-w10-one-error-audit.md'):
        inputs[f] = sha(os.path.join(root, f))
    k4 = per_p(os.path.join(d, 'K4.txt')); nl = {t: per_p(os.path.join(d, t + '.txt')) for t in NULLS}
    rng = np.random.default_rng(SEED); out = dict(seed=SEED, B=B, alpha=ALPHA, inputs=inputs, cells={})
    for p in CELLS:
        c = k4[p]; x = np.array([nl[t][p] for t in NULLS]); n = len(x)
        js = S['per_p'][str(p)]; assert js['K4'] == c and js['nulls'] == x.tolist(), f'p{p}: header != summary219.json'
        ge, le, eq = int((x >= c).sum()), int((x <= c).sum()), int((x == c).sum())
        side = 'hi' if ge <= le else 'lo'; k_side = ge if side == 'hi' else le      # the tail K4 is closer to
        q_hat = k_side / n; q_mid = (k_side - 0.5 * eq) / n
        cp_side = cp(k_side, n)
        # bootstrap of the null edge and of the tail rate
        R = x[rng.integers(0, n, (B, n))]
        bmin, bmax, bmed = R.min(1), R.max(1), np.median(R, 1)
        bq = ((R >= c) if side == 'hi' else (R <= c)).mean(1)
        pct = lambda a: [float(np.quantile(a, .025)), float(np.quantile(a, .975))]
        inside = float(((bmin <= c) & (c <= bmax)).mean())
        # exact order-statistic facts: P(K4-at-quantile u lies outside the range of N draws) etc.
        cell = dict(K4=c, nulls=x.tolist(), null_min=int(x.min()), null_max=int(x.max()), null_median=float(np.median(x)),
                    inside_range=bool(x.min() <= c <= x.max()),
                    n_ge=ge, n_le=le, n_eq=eq, side=side, tail_k=k_side, tail_hat=q_hat, tail_mid=q_mid,
                    tail_CP95=[round(v, 4) for v in cp_side],
                    CP95_ge=[round(v, 4) for v in cp(ge, n)], CP95_le=[round(v, 4) for v in cp(le, n)],
                    boot_min95=pct(bmin), boot_max95=pct(bmax), boot_median95=pct(bmed), boot_tail95=pct(bq),
                    boot_P_inside_range=inside,
                    rule_at_8=resolves(k_side, n),
                    # range rule (PREREG219): K4 above all N nulls. With tail rate q on the low side, P = (1-q_ge)^N shrinks with N
                    P_above_all_N=dict((N, round((1 - ge / n) ** N, 4)) for N in (8, 16, 40, 80, 160)) if c > 0 else None,
                    N_expected_point=n_needed(max(q_hat, 1e-9)), N_expected_mid=n_needed(max(q_mid, 1e-9)),
                    N_power80_point=n_needed(max(q_hat, 1e-9), 0.8),
                    N_power80_CPlow=n_needed(max(cp_side[0], 1e-9), 0.8), CPlow=round(cp_side[0], 4))
        out['cells'][p] = cell
        print(f"p{p} K4 {c} nulls {x.tolist()} range [{x.min()},{x.max()}] side {side} tail {k_side}/8 "
              f"CP95 [{cp_side[0]:.3f},{cp_side[1]:.3f}] boot tail {np.round(pct(bq),3).tolist()} "
              f"boot max {pct(bmax)} boot min {pct(bmin)} P(inside|boot) {inside:.3f} rule@8 {cell['rule_at_8']} "
              f"N(point) {cell['N_expected_point']} N(mid) {cell['N_expected_mid']} N(80%|q^) {cell['N_power80_point']} "
              f"N(80%|CPlow {cp_side[0]:.3f}) {cell['N_power80_CPlow']}", flush=True)
    return out

if __name__ == '__main__':
    o = main(sys.argv[1] if len(sys.argv) > 1 else '.')
    json.dump(o, open(sys.argv[2] if len(sys.argv) > 2 else 'results_c205_null_interval.json', 'w'), indent=1)
