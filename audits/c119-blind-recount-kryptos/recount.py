#!/usr/bin/env python3
"""Independent blind recount of Voynich C119, written from the case-file prose.

Does not import tools/c119_*.py or read any C119 result/log/gate/frozen file.
Shared loaders (C003/C047/C049/C051/C108/C115) and the C111/C117 EM update
are re-typed here from the functions named by the case file.

Seeds (exclusive, as declared): 11802 main, 11803 unused here (frozen calib
values taken from case-file R11), 11804 bootstrap, 11805 extension if needed.
11809 is not used.

Run from anywhere:
  python3 /workspace/c119-blind-recount/recount.py --phase load
  python3 /workspace/c119-blind-recount/recount.py --phase precheck
  python3 /workspace/c119-blind-recount/recount.py --phase run
  python3 /workspace/c119-blind-recount/recount.py --phase summarize
"""
from __future__ import annotations

import argparse, hashlib, json, os, re, sys, time, unicodedata
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from numpy.random import SeedSequence

PT = timezone(timedelta(hours=-7))
HERE = Path("/workspace/c119-blind-recount")
REPO = HERE / "repo"
WORK = HERE / "work"
NTOK = 10000
NITER1 = 500
TOL_REL = 1e-6
NNULL = 79
R1 = 10
CONV_TOL1 = 5.0
RB = 5
CONV_TOLB = 0.001
KKT_TOL = 1e-8
DLL_TOL = 1e-9
DLL_WINDOW = 5
WARM_MAX = 20
TIE = 1e-9
Q_PLANT = 0.10
ALPHA = 0.05
M_HOLM = 3
HASH_KEY = "11802"
GRID_N = 41

# R2 text names (C113 hash_name), asserted below.
NAMES = {
    "CAE_DV_W1": 3442, "CAE_DV_W2": 3451, "CAE_V": 1214, "HEB_ABJ": 2027,
    "GPOW": 816, "ZL_A": 787, "ZL_B1": 1036, "ZL_B2": 1041,
}


def now_pt():
    return datetime.now(PT).strftime("%Y-%m-%d %H:%M:%S PT")


def hash_name(n):
    return sum((i + 1) * ord(c) for i, c in enumerate(n))


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Shared loaders, retyped from the named tools (not C119).
# ---------------------------------------------------------------------------

UNITS = ["cth", "ckh", "cph", "cfh", "ch", "sh"]
FINALS = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}


def units(w, raw=False):
    if raw:
        return list(w)
    out, i = [], 0
    while i < len(w):
        for u in UNITS:
            if w.startswith(u, i):
                out.append(u)
                i += len(u)
                break
        else:
            out.append(w[i])
            i += 1
    return out


def gutenberg(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    a = s.find("*** START")
    b = s.find("*** END")
    s = s[s.find("\n", a) + 1 : b] if a >= 0 and b > a else s
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return [re.findall(r"[a-z]+", l) for l in s.split("\n") if re.findall(r"[a-z]+", l)]


def hebrew(path, merge_finals=False):
    s = open(path, encoding="utf-8").read()
    lines = []
    for verse in re.findall(r"<verse[^>]*>(.*?)</verse>", s, re.S):
        ws = []
        for w in re.findall(r"<w [^>]*>([^<]*)</w>", verse):
            w = "".join(c for c in unicodedata.normalize("NFD", w) if "\u05d0" <= c <= "\u05ea")
            if merge_finals:
                w = "".join(FINALS.get(c, c) for c in w)
            if w:
                ws.append(w)
        if ws:
            lines.append(ws)
    return lines


def devowel(lines):
    out = [[re.sub("[aeiou]", "", w) for w in l] for l in lines]
    return [[w for w in l if w] for l in out if any(l)]


def take(lines, start, n):
    out, t, seen = [], 0, 0
    for l in lines:
        if seen < start:
            seen += len(l)
            continue
        if t >= n:
            break
        out.append(l)
        t += len(l)
    return out


def flat(lines):
    return [w for l in lines for w in l]


def chars(words):
    return [tuple(w) for w in words]


def nat_texts():
    C = REPO / "data" / "corpora"
    nat = {
        "Latin_Caesar": gutenberg(C / "pg218.txt"),
        "Hebrew_Genesis": hebrew(C / "Gen.xml"),
    }
    return {k: [l for l in v if len(l) >= 3] for k, v in nat.items()}


def ivtff_pages_lang(path):
    out, lang, sect = [], {}, {}
    for line in open(path, encoding="utf-8", errors="replace"):
        h = re.match(r"<(f\w+)>\s+<!(.*)>", line)
        if h:
            m = re.search(r"\$L=(\w)", h.group(2))
            lang[h.group(1)] = m.group(1) if m else None
            m = re.search(r"\$I=(\w)", h.group(2))
            sect[h.group(1)] = m.group(1) if m else None
            continue
        m = re.match(r"<(f\w+)\.\d+,([@+=*&~-])(\w+)>\s*(.*)", line.rstrip("\n"))
        if not m or not m.group(3).startswith("P"):
            continue
        t = m.group(4).replace("<->", ".")
        t = re.sub(r"<[^>]*>", "", t)
        t = re.sub(r"@\d+;", "", t)
        t = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", t).replace("{", "").replace("}", "").replace("'", "")
        ws = [w for w in re.split(r"[.,\s]+", t) if w]
        if len(ws) < 3 or not all(re.fullmatch(r"[a-z]+", w) for w in ws):
            continue
        out.append((m.group(1), ws))
    return out, lang, sect


def lines_by(pl, lang, sect, L=None, S=None):
    return [l for p, l in pl if (L is None or lang.get(p) == L) and (S is None or sect.get(p) == S)]


def strata(path, with_lines=False):
    pl, lang, sect = ivtff_pages_lang(path)
    u = lambda ls: [tuple(units(w)) for w in flat(ls)]
    A, Bl = lines_by(pl, lang, sect, "A"), lines_by(pl, lang, sect, "B")
    L = dict(A=take(A, 0, NTOK), B1=take(Bl, 0, NTOK), B2=take(Bl, NTOK, NTOK))
    out = {k: u(v) for k, v in L.items()}
    if with_lines:
        return out, {k: [[tuple(units(w)) for w in l] for l in v] for k, v in L.items()}
    return out


def devowel_lines(name, n):
    nat = nat_texts()
    ls = [l for l in devowel(nat[name]) if len(l) >= 3]
    return [chars(l) for l in take(ls, 0, n)]


def encode(words):
    sym = {}
    ids, wid = [], []
    for k, w in enumerate(words):
        for u in w:
            ids.append(sym.setdefault(u, len(sym)))
            wid.append(k)
    inv = [None] * len(sym)
    for u, i in sym.items():
        inv[i] = u
    return np.array(ids, dtype=np.int64), np.array(wid, dtype=np.int64), inv


def pad(ids, wid):
    W = int(wid[-1]) + 1
    lens = np.bincount(wid, minlength=W)
    L = int(lens.max())
    pos = np.arange(len(ids)) - np.repeat(np.cumsum(lens) - lens, lens)
    X = np.zeros((W, L), np.int64)
    M = np.zeros((W, L), bool)
    X[wid, pos] = ids
    M[wid, pos] = True
    return X, M


def nline(lines, rng):
    out = []
    for l in lines:
        l = list(l)
        if len(l) >= 5:
            mid = l[1:-1]
            perm = rng.permutation(len(mid))
            l = [l[0]] + [mid[i] for i in perm] + [l[-1]]
        out.append(l)
    return out


def line_sha(lines) -> str:
    s = "\n".join(" ".join("".join(w) for w in line) for line in lines)
    return sha256_bytes(s.encode("utf-8"))


def line_stats(lines):
    words = flat(lines)
    n_bound = sum(max(len(l) - 1, 0) for l in lines)
    n_mov_lines = sum(1 for l in lines if len(l) >= 5)
    # C118 printed share includes fixed ends of movable lines.
    mov_incl_ends = sum(len(l) for l in lines if len(l) >= 5)
    mov_middles = sum(len(l) - 2 for l in lines if len(l) >= 5)
    glyphs = sum(len(w) for w in words)
    return dict(
        n_words=len(words),
        n_lines=len(lines),
        n_glyphs=glyphs,
        n_boundaries=n_bound,
        n_movable_lines=n_mov_lines,
        movable_token_share_incl_fixed_ends=mov_incl_ends / len(words) if words else 0.0,
        movable_middle_share=mov_middles / len(words) if words else 0.0,
        mean_line_len=len(words) / len(lines) if lines else 0.0,
        sha=line_sha(lines),
    )


# ---------------------------------------------------------------------------
# Step 1: C111/C117 EM, cap 500, relative TOL 1e-6, returns full parameters.
# ---------------------------------------------------------------------------

def fit_hmm_full(X, M, S, rng, niter=NITER1, tol=TOL_REL):
    """One free 2-state restart. Returns dict with loop_ll (C111 convention)
    and params after the last M-step, plus recomputed_ll at those params."""
    W, L = X.shape
    pi = rng.dirichlet([1.0, 1.0])
    A = rng.dirichlet([1.0, 1.0], 2)
    Bm = rng.dirichlet(np.ones(S), 2)
    last = -np.inf
    loop_ll = None
    hit_cap = True
    it_used = 0
    for it in range(niter):
        al = np.zeros((W, L, 2))
        c = np.ones((W, L))
        a = pi[None] * Bm[:, X[:, 0]].T
        c[:, 0] = a.sum(1)
        al[:, 0] = a / c[:, :1]
        for t in range(1, L):
            a = (al[:, t - 1] @ A) * Bm[:, X[:, t]].T
            s = a.sum(1)
            m = M[:, t]
            c[m, t] = s[m]
            al[m, t] = a[m] / s[m, None]
            al[~m, t] = al[~m, t - 1]
        be = np.ones((W, L, 2))
        xi = np.zeros((2, 2))
        for t in range(L - 2, -1, -1):
            m = M[:, t + 1]
            e = Bm[:, X[:, t + 1]].T * be[:, t + 1]
            b = (e @ A.T) / c[:, t + 1 : t + 2]
            be[m, t] = b[m]
            xi += np.einsum("wi,ij,wj->ij", al[m, t], A, e[m] / c[m, t + 1 : t + 2])
        ll = float(np.log(c[M]).sum())
        g = al * be
        g = g / g.sum(2, keepdims=True)
        # Parameters that produced this ll (pre-M-step). C111 updates after
        # computing ll and returns the post-M-step params with the pre-M-step ll.
        # S's zero point is ℓ at the frozen step-1 parameters, and section 6
        # identifies that ℓ with the reported best loop_ll, so we freeze the
        # pre-M-step parameters.
        pi_ll, A_ll, Bm_ll = pi, A, Bm
        pi = g[:, 0].mean(0)
        A = xi / xi.sum(1, keepdims=True)
        Bn = np.zeros((2, S))
        np.add.at(Bn.T, X[M], g[M])
        Bm = (Bn + 1e-12) / (Bn + 1e-12).sum(1, keepdims=True)
        loop_ll = ll
        it_used = it + 1
        if ll - last < tol * abs(ll):
            hit_cap = False
            pi, A, Bm = pi_ll, A_ll, Bm_ll
            break
        last = ll
    recomputed = word_row_ll(X, M, pi, A, Bm)
    return dict(
        loop_ll=float(loop_ll),
        recomputed_ll=float(recomputed),
        pi=np.asarray(pi, float),
        A=np.asarray(A, float),
        Bm=np.asarray(Bm, float),
        iters=it_used,
        hit_cap=hit_cap,
    )


def word_row_ll(X, M, pi, A, Bm):
    W, L = X.shape
    c0 = (pi[None] * Bm[:, X[:, 0]].T).sum(1)
    al = (pi[None] * Bm[:, X[:, 0]].T) / c0[:, None]
    ll = np.log(c0).sum()
    for t in range(1, L):
        a = (al @ A) * Bm[:, X[:, t]].T
        s = a.sum(1)
        m = M[:, t]
        ll += np.log(s[m]).sum()
        al[m] = a[m] / s[m, None]
        # al[~m] stays (padding)
    return float(ll)


def classify_basin(A, pi):
    """Align states so pi[0] >= pi[1], then classify the within-word A.
    This definition is ours: the case-file procedure does not define 'alternating'
    vs 'sticky' in the sections we read. See AMBIGUITIES.md.
    sticky: both self-transitions >= 0.5
    alternating: both off-diagonals >= 0.5
    mixed: otherwise
    """
    A = np.asarray(A, float).copy()
    pi = np.asarray(pi, float).copy()
    flipped = False
    if pi[1] > pi[0]:
        A = A[::-1, ::-1]
        pi = pi[::-1]
        flipped = True
    a00, a01 = float(A[0, 0]), float(A[0, 1])
    a10, a11 = float(A[1, 0]), float(A[1, 1])
    if a00 >= 0.5 and a11 >= 0.5:
        label = "sticky"
    elif a01 >= 0.5 and a10 >= 0.5:
        label = "alternating"
    else:
        label = "mixed"
    return dict(label=label, A=A.tolist(), pi=pi.tolist(), flipped=flipped,
                A_raw_diag=[a00, a11], A_raw_off=[a01, a10])


def align_to(ref_Bm, Bm, A, pi):
    """Flip states if emission rows match the reference better when flipped."""
    d_same = np.abs(ref_Bm - Bm).sum()
    d_flip = np.abs(ref_Bm - Bm[::-1]).sum()
    if d_flip < d_same:
        return A[::-1, ::-1], pi[::-1], Bm[::-1], True
    return A, pi, Bm, False


# ---------------------------------------------------------------------------
# Step 2: line-stream B fit, L-BFGS-B on (B_12, B_21) in [0, 1].
# ---------------------------------------------------------------------------

def word_F(ids, A, Bm):
    Tlen = len(ids)
    F = np.zeros((2, 2), float)
    if Tlen == 0:
        return np.eye(2)
    if Tlen == 1:
        F[0, 0] = Bm[0, ids[0]]
        F[1, 1] = Bm[1, ids[0]]
        return F
    alpha = np.zeros((2, 2), float)
    alpha[0, 0] = Bm[0, ids[0]]
    alpha[1, 1] = Bm[1, ids[0]]
    for t in range(1, Tlen):
        alpha = (alpha @ A) * Bm[:, ids[t]]
    return alpha


def precompute_F_for_lines(lines, sym, A, Bm):
    cache = {}
    Fs_lines = []
    for line in lines:
        Fs = []
        for w in line:
            key = w
            if key not in cache:
                ids = [sym[u] for u in w]
                cache[key] = word_F(ids, A, Bm)
            Fs.append(cache[key])
        Fs_lines.append(Fs)
    return Fs_lines


def line_ll_and_grad(Fs, B, pi):
    """Scalar version (kept for checks). Sum ll and unconstrained G over one line."""
    n = len(Fs)
    if n == 0:
        return 0.0, np.zeros((2, 2))
    if n == 1:
        p = pi @ Fs[0]
        sm = p.sum()
        return (np.log(sm) if sm > 0 else -np.inf), np.zeros((2, 2))
    alpha = [None] * n
    c = np.zeros(n)
    a = pi @ Fs[0]
    c[0] = a.sum()
    if c[0] <= 0:
        return -np.inf, np.zeros((2, 2))
    alpha[0] = a / c[0]
    logp = np.log(c[0])
    for k in range(1, n):
        a = alpha[k - 1] @ B @ Fs[k]
        c[k] = a.sum()
        if c[k] <= 0:
            return -np.inf, np.zeros((2, 2))
        alpha[k] = a / c[k]
        logp += np.log(c[k])
    beta = [None] * n
    beta[n - 1] = np.ones(2)
    G = np.zeros((2, 2))
    for k in range(n - 2, -1, -1):
        Fb = Fs[k + 1] @ beta[k + 1]
        G += np.outer(alpha[k], Fb) / c[k + 1]
        beta[k] = (B @ Fb) / c[k + 1]
    return float(logp), G


def pack_Fs(Fs_lines):
    n = len(Fs_lines)
    L = max((len(Fs) for Fs in Fs_lines), default=0)
    F = np.zeros((n, L, 2, 2))
    M = np.zeros((n, L), bool)
    for i, Fs in enumerate(Fs_lines):
        for t, mat in enumerate(Fs):
            F[i, t] = mat
            M[i, t] = True
    lens = M.sum(1).astype(int)
    return F, M, lens


def total_ll_grad_vec(F, M, lens, B, pi):
    """Vectorized line-stream ll and unconstrained G_ij = dℓ/dB_ij."""
    n, L, _, _ = F.shape
    if L == 0 or n == 0:
        return 0.0, np.zeros((2, 2))
    alpha = np.zeros((n, L, 2))
    c = np.ones((n, L))
    a0 = np.einsum("i,nij->nj", pi, F[:, 0])
    c[:, 0] = a0.sum(1)
    good = c[:, 0] > 0
    alpha[good, 0] = a0[good] / c[good, 0:1]
    ll = np.full(n, -np.inf)
    ll[good] = np.log(c[good, 0])
    for t in range(1, L):
        m = M[:, t]
        if not np.any(m):
            break
        a = np.einsum("ni,ij,njk->nk", alpha[:, t - 1], B, F[:, t])
        c[m, t] = a[m].sum(1)
        ok = m & (c[:, t] > 0)
        bad = m & (c[:, t] <= 0)
        alpha[ok, t] = a[ok] / c[ok, t:t + 1]
        ll[ok] += np.log(c[ok, t])
        ll[bad] = -np.inf
    beta = np.zeros((n, L, 2))
    last = np.clip(lens - 1, 0, None)
    for i in range(n):
        if lens[i] > 0:
            beta[i, last[i]] = 1.0
    G = np.zeros((2, 2))
    finite = np.isfinite(ll)
    for t in range(L - 2, -1, -1):
        m = M[:, t + 1] & finite
        if not np.any(m):
            continue
        Fb = np.einsum("nij,nj->ni", F[:, t + 1], beta[:, t + 1])
        invc = np.zeros(n)
        invc[m] = 1.0 / c[m, t + 1]
        G += np.einsum("n,ni,nj->ij", invc[m], alpha[m, t], Fb[m])
        beta[m, t] = (Fb[m] @ B.T) * invc[m, None]
    if not np.all(finite):
        return float("-inf"), G
    return float(ll.sum()), G


def total_ll_grad(Fs_lines, B, pi, packed=None):
    if packed is None:
        packed = pack_Fs(Fs_lines)
    return total_ll_grad_vec(*packed, B, pi)


def B_from_x(x):
    b12, b21 = float(x[0]), float(x[1])
    return np.array([[1.0 - b12, b12], [b21, 1.0 - b21]], float)


def constrained_grad(G):
    # dℓ/dB_12 = G_12 - G_11; dℓ/dB_21 = G_21 - G_22
    return np.array([G[0, 1] - G[0, 0], G[1, 0] - G[1, 1]], float)


def projected_grad(x, g, bound_eps=0.0):
    """KKT projected gradient for MAXIMIZING ℓ on [0,1]^2. g = dℓ/dx.
    A coordinate at 0 with non-positive dℓ/dx, or at 1 with non-negative dℓ/dx,
    is projected to 0. Returns the vector; 'max KKT' is the max-abs component.
    """
    proj = np.array(g, float, copy=True)
    for i in range(2):
        xi = x[i]
        gi = g[i]
        if xi <= 0.0 + bound_eps and gi <= 0:
            proj[i] = 0.0
        elif xi >= 1.0 - bound_eps and gi >= 0:
            proj[i] = 0.0
    return proj


def newton_polish(x, packed, pi, nsteps=5, h=1e-8):
    """One or two Newton steps on (B_12, B_21) using a finite-difference Hessian
    of the exact gradient. Used only when L-BFGS + warm restarts have already
    agreed on ℓ but ||proj g|| is still above 1e-8 (flat, ill-conditioned max).
    ℓ is not allowed to decrease. Thresholds are unchanged.
    """
    x = np.asarray(x, float).copy()
    def ev(z):
        ll, G = total_ll_grad_vec(*packed, B_from_x(z), pi)
        g = constrained_grad(G)
        zK = z.copy()
        zK[np.abs(zK - 0) < 1e-14] = 0.0
        zK[np.abs(zK - 1) < 1e-14] = 1.0
        pg = projected_grad(zK, g)
        return ll, g, pg, float(np.max(np.abs(pg)))
    ll, g, pg, kkt = ev(x)
    for _ in range(nsteps):
        if kkt < KKT_TOL:
            break
        H = np.zeros((2, 2))
        for j in range(2):
            xp, xm = x.copy(), x.copy()
            xp[j] = np.clip(xp[j] + h, 0.0, 1.0)
            xm[j] = np.clip(xm[j] - h, 0.0, 1.0)
            denom = xp[j] - xm[j]
            if denom == 0:
                continue
            H[:, j] = (ev(xp)[1] - ev(xm)[1]) / denom
        try:
            dx = np.linalg.solve(H, g)
        except np.linalg.LinAlgError:
            break
        x2 = np.clip(x - dx, 0.0, 1.0)
        ll2, g2, pg2, k2 = ev(x2)
        if ll2 < ll - 1e-12:
            break
        x, ll, g, pg, kkt = x2, ll2, g2, pg2, k2
    return x, ll, g, kkt


def fit_B(Fs_lines, pi, starts, reset_ll=None):
    """Fit B from given 2x2 Dirichlet (or other) starts. Returns best and per-start diagnostics."""
    packed = pack_Fs(Fs_lines)
    per = []
    for sidx, B0 in enumerate(starts):
        x0 = np.array([B0[0, 1], B0[1, 0]], float)
        x0 = np.clip(x0, 0.0, 1.0)
        ell_hist = []
        n_warm = 0
        x = x0.copy()
        last_res = None
        cache = {}

        def eval_z(z):
            z = np.asarray(z, float)
            key = (float(z[0]), float(z[1]))
            if cache.get("key") != key:
                B = B_from_x(z)
                ll, G = total_ll_grad_vec(*packed, B, pi)
                d = constrained_grad(G)
                cache["key"] = key
                cache["pack"] = (-ll, -d, ll, G)
            return cache["pack"]

        def cb(zk):
            pack = eval_z(zk)
            ell_hist.append(pack[2])

        for warm in range(WARM_MAX + 1):
            # scipy's default gtol is 1e-5, coarser than the declared KKT 1e-8,
            # so a default stop + warm restart often exits at once with ||proj g||
            # still above 1e-8 and unchanged S. Tighten gtol/ftol so the declared
            # threshold is actually reachable; the two-criterion rule is unchanged.
            res = minimize(
                lambda z: eval_z(z)[0],
                x,
                method="L-BFGS-B",
                jac=lambda z: eval_z(z)[1],
                bounds=[(0.0, 1.0), (0.0, 1.0)],
                callback=cb,
                options=dict(ftol=1e-15, gtol=1e-12, maxiter=15000),
            )
            last_res = res
            x = np.clip(res.x, 0.0, 1.0)
            negll, negd, ll, G = eval_z(x)
            if not ell_hist or abs(ell_hist[-1] - ll) > 1e-15:
                ell_hist.append(ll)
            g = constrained_grad(G)
            x_kkt = x.copy()
            x_kkt[np.abs(x_kkt - 0) < 1e-14] = 0.0
            x_kkt[np.abs(x_kkt - 1) < 1e-14] = 1.0
            pg = projected_grad(x_kkt, g)
            max_kkt = float(np.max(np.abs(pg)))
            conv_kkt = max_kkt < KKT_TOL
            conv_dll = (len(ell_hist) >= DLL_WINDOW + 1) and (abs(ell_hist[-1] - ell_hist[-1 - DLL_WINDOW]) < DLL_TOL)
            if conv_kkt or conv_dll:
                n_warm = warm
                break
            n_warm = warm + 1
            if warm >= WARM_MAX:
                break
        B = B_from_x(x)
        _, _, ll, G = eval_z(x)
        g = constrained_grad(G)
        x_kkt = x.copy()
        x_kkt[np.abs(x_kkt - 0) < 1e-14] = 0.0
        x_kkt[np.abs(x_kkt - 1) < 1e-14] = 1.0
        pg = projected_grad(x_kkt, g)
        max_kkt = float(np.max(np.abs(pg)))
        conv_kkt = max_kkt < KKT_TOL
        conv_dll = (len(ell_hist) >= DLL_WINDOW + 1) and (abs(ell_hist[-1] - ell_hist[-1 - DLL_WINDOW]) < DLL_TOL)
        if not (conv_kkt or conv_dll):
            x, ll, g, max_kkt = newton_polish(x, packed, pi)
            cache.clear()
            B = B_from_x(x)
            ell_hist.append(ll)
            x_kkt = x.copy()
            x_kkt[np.abs(x_kkt - 0) < 1e-14] = 0.0
            x_kkt[np.abs(x_kkt - 1) < 1e-14] = 1.0
            conv_kkt = max_kkt < KKT_TOL
            conv_dll = (len(ell_hist) >= DLL_WINDOW + 1) and (abs(ell_hist[-1] - ell_hist[-1 - DLL_WINDOW]) < DLL_TOL)
        rows_on = int(np.isclose(x[0], 0) or np.isclose(x[0], 1)) + int(
            np.isclose(x[1], 0) or np.isclose(x[1], 1)
        )
        per.append(
            dict(
                start=sidx,
                x=x.tolist(),
                B=B.tolist(),
                ll=float(ll),
                max_kkt=max_kkt,
                conv_kkt=bool(conv_kkt),
                conv_dll=bool(conv_dll),
                converged=bool(conv_kkt or conv_dll),
                n_warm=int(n_warm),
                n_ell=len(ell_hist),
                rows_on_bound=rows_on,
                scipy_success=bool(last_res.success) if last_res is not None else False,
                scipy_message=str(last_res.message) if last_res is not None else "",
                nit=int(getattr(last_res, "nit", 0) or 0),
            )
        )
    best = max(per, key=lambda d: d["ll"])
    lls = np.array([d["ll"] for d in per], float)
    return best, per, lls


def S_from(ll_B, ll_reset, n_bound):
    return (ll_B - ll_reset) / n_bound


# ---------------------------------------------------------------------------
# Plants (G-POW state-aligned).
# ---------------------------------------------------------------------------

def word_end_state(ids, pi, A, Bm):
    """Normalised forward at last glyph, starting from π; argmax is c(w)."""
    alpha = pi * Bm[:, ids[0]]
    s = alpha.sum()
    if s <= 0:
        return 0, alpha
    alpha = alpha / s
    for t in range(1, len(ids)):
        alpha = (alpha @ A) * Bm[:, ids[t]]
        s = alpha.sum()
        if s <= 0:
            break
        alpha = alpha / s
    return int(np.argmax(alpha)), alpha


def aligned_plant(lines, sym, pi, A, Bm, rng, q=Q_PLANT):
    """State-aligned greedy chain on movable lines, independently with prob q.
    RNG is used only for the per-movable-line Bernoulli (lines in order).
    Ties in the chain: earliest remaining word in the original middle order.
    Ties in argmax for c(w): np.argmax (state 0 if equal).
    """
    c_cache = {}
    a_cache = {}

    def typ(w):
        return w

    def c_of(w):
        key = typ(w)
        if key not in c_cache:
            ids = [sym[u] for u in w]
            c_cache[key] = word_end_state(ids, pi, A, Bm)[0]
        return c_cache[key]

    def a_of(w, s):
        key = (typ(w), s)
        if key not in a_cache:
            g0 = sym[w[0]]
            raw = pi * Bm[:, g0]
            z = raw.sum()
            a_cache[(typ(w), 0)] = float(raw[0] / z) if z > 0 else 0.5
            a_cache[(typ(w), 1)] = float(raw[1] / z) if z > 0 else 0.5
        return a_cache[key]

    out = []
    n_planted = 0
    for line in lines:
        line = list(line)
        if len(line) >= 5 and rng.random() < q:
            first, last = line[0], line[-1]
            remaining = list(line[1:-1])  # original order
            new_mid = []
            prev = first
            while remaining:
                s = c_of(prev)
                best_i = 0
                best_sc = a_of(remaining[0], s)
                for i in range(1, len(remaining)):
                    sc = a_of(remaining[i], s)
                    if sc > best_sc:
                        best_sc = sc
                        best_i = i
                nxt = remaining.pop(best_i)
                new_mid.append(nxt)
                prev = nxt
            out.append([first] + new_mid + [last])
            n_planted += 1
        else:
            out.append(line)
    return out, n_planted


# ---------------------------------------------------------------------------
# Text loading
# ---------------------------------------------------------------------------

def load_all_texts():
    os.chdir(REPO)
    nat = nat_texts()
    # W1 / W2 from the same filtered devowelled Caesar lines.
    cae_dv_src = [l for l in devowel(nat["Latin_Caesar"]) if len(l) >= 3]
    w1 = [chars(l) for l in take(cae_dv_src, 0, NTOK)]
    w2 = [chars(l) for l in take(cae_dv_src, NTOK, NTOK)]
    # first line index of W2 in the source list
    seen, w2_first = 0, None
    for i, l in enumerate(cae_dv_src):
        if seen >= NTOK:
            w2_first = i
            break
        seen += len(l)
    w1_last = len(w1) - 1
    # textual equality of whole lines
    w1_set = {tuple(l) for l in w1}
    n_w2_eq = sum(1 for l in w2 if tuple(l) in w1_set)

    cae_v = [chars(l) for l in take(nat["Latin_Caesar"], 0, NTOK)]
    heb = [chars(l) for l in take(nat["Hebrew_Genesis"], 0, NTOK)]

    zl_tok, zl_lines = strata(REPO / "data" / "ZL3b-n.txt", with_lines=True)

    texts = {
        "CAE_DV_W1": w1,
        "CAE_DV_W2": w2,
        "CAE_V": cae_v,
        "HEB_ABJ": heb,
        "ZL_A": zl_lines["A"],
        "ZL_B1": zl_lines["B1"],
        "ZL_B2": zl_lines["B2"],
    }
    info = {k: line_stats(v) for k, v in texts.items()}
    info["CAE_DV_W2"]["first_line_index"] = w2_first
    info["CAE_DV_W2"]["w1_last_index"] = w1_last
    info["CAE_DV_W2"]["n_lines_textually_equal_to_a_w1_line"] = n_w2_eq
    info["meta"] = dict(
        zl3b_sha=sha256_file(REPO / "data" / "ZL3b-n.txt"),
        pg218_sha=sha256_file(REPO / "data" / "corpora" / "pg218.txt"),
        gen_sha=sha256_file(REPO / "data" / "corpora" / "Gen.xml"),
        hash_name={k: hash_name(k) for k in NAMES},
        hash_name_ok=all(hash_name(k) == v for k, v in NAMES.items()),
        token_counts={k: info[k]["n_words"] for k in texts},
    )
    return texts, info


def symbol_map(lines):
    """Frozen symbol IDs: sorted unique units of the observed text.
    The case-file prose does not specify the ID order. Insertion order (C108
    encode) on CAE-DV W1 with seed [11801, 3] does not reproduce the frozen
    section-6 step-1 ℓ; sorted order does, exactly (−79,623.3260516). That is
    also the convention used in C118's invariance check to keep IDs stable.
    """
    words = flat(lines)
    inv = sorted({u for w in words for u in w})
    sym = {u: i for i, u in enumerate(inv)}
    ids = np.array([sym[u] for w in words for u in w], dtype=np.int64)
    wid = np.array([k for k, w in enumerate(words) for _ in w], dtype=np.int64)
    return sym, inv, ids, wid


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

def step1_for_text(name, lines, seed_mode, run_seed=11802):
    """Fit step 1. seed_mode 'run' uses independent SS per restart (R4);
    'precheck' uses one sequential rng from SeedSequence([11801, 3]).
    """
    sym, inv, ids, wid = symbol_map(lines)
    X, M = pad(ids, wid)
    S = len(inv)
    restarts = []
    t0 = time.time()
    if seed_mode == "precheck":
        rng = np.random.default_rng(SeedSequence([11801, 3]))
        for i in range(R1):
            ti = time.time()
            restarts.append(fit_hmm_full(X, M, S, rng))
            r = restarts[-1]
            print(f"  step1 {name} restart {i}: loop_ll={r['loop_ll']:.6f} rec={r['recomputed_ll']:.6f} "
                  f"iters={r['iters']} cap={r['hit_cap']} {time.time()-ti:.2f}s", flush=True)
    else:
        for i in range(R1):
            rng = np.random.default_rng(SeedSequence([run_seed, hash_name(name), 1000, i]))
            ti = time.time()
            restarts.append(fit_hmm_full(X, M, S, rng))
            r = restarts[-1]
            print(f"  step1 {name} restart {i}: loop_ll={r['loop_ll']:.6f} rec={r['recomputed_ll']:.6f} "
                  f"iters={r['iters']} cap={r['hit_cap']} {time.time()-ti:.2f}s", flush=True)
    print(f"  step1 {name} all restarts {time.time()-t0:.2f}s", flush=True)
    # Select best by loop_ll (C111 convention). Freeze post-M-step params.
    best_i = int(np.argmax([r["loop_ll"] for r in restarts]))
    best = restarts[best_i]
    # Recompute word-row ll at frozen params (zero point of S / A1).
    ll0 = best["recomputed_ll"]
    within = [j for j, r in enumerate(restarts) if r["loop_ll"] >= best["loop_ll"] - CONV_TOL1]
    # basin of each restart, aligned to the best's emissions
    basins = []
    for r in restarts:
        A, pi, Bm, flipped = align_to(best["Bm"], r["Bm"], r["A"], r["pi"])
        lab = classify_basin(A, pi)
        basins.append(dict(label=lab["label"], loop_ll=r["loop_ll"], recomputed_ll=r["recomputed_ll"],
                           iters=r["iters"], hit_cap=r["hit_cap"], flipped_to_best=flipped,
                           A=A.tolist(), pi=pi.tolist()))
    best_lab = basins[best_i]["label"]
    n_same = sum(1 for b in basins if b["label"] == best_lab)
    step1_conv = len(within) >= 3
    return dict(
        name=name,
        best_i=best_i,
        loop_ll=best["loop_ll"],
        recomputed_ll=ll0,
        pi=best["pi"].tolist(),
        A=best["A"].tolist(),
        Bm=best["Bm"].tolist(),
        inv=[(u if isinstance(u, str) else "".join(u) if isinstance(u, (list, tuple)) else str(u)) for u in inv],
        n_sym=S,
        n_within_tol=len(within),
        within=within,
        step1_converged=step1_conv,
        cap_hits=sum(1 for r in restarts if r["hit_cap"]),
        basin=best_lab,
        n_restarts_same_basin=n_same,
        basins=basins,
        classify_note="states aligned so emissions match the best restart, then labelled after pi[0]>=pi[1]",
    ), sym, inv, best


def dirichlet_starts(rng, n=RB):
    return [rng.dirichlet([1.0, 1.0], 2) for _ in range(n)]


def job_B(name, obs_lines, step1, sym, rep, run_seed=11802, starts=None, shuffle_rng=None):
    pi = np.asarray(step1["pi"], float)
    A = np.asarray(step1["A"], float)
    Bm = np.asarray(step1["Bm"], float)
    if shuffle_rng is None:
        rng = np.random.default_rng(SeedSequence([run_seed, hash_name(name), rep]))
    else:
        rng = shuffle_rng
    if rep > 0:
        lines = nline(obs_lines, rng)
        # A2 asserts
        for a, b in zip(obs_lines, lines):
            assert a[0] == b[0] and a[-1] == b[-1] and sorted(a) == sorted(b)
            if len(a) <= 4:
                assert a == b
    else:
        lines = obs_lines
    if starts is None:
        starts = dirichlet_starts(rng, RB)
    Fs_lines = precompute_F_for_lines(lines, sym, A, Bm)
    Breset = np.vstack([pi, pi])
    ll_reset, _ = total_ll_grad(Fs_lines, Breset, pi)
    # A1 on observed (rep 0): reset ll vs word-row recomputed
    best, per, lls = fit_B(Fs_lines, pi, starts)
    n_bound = sum(max(len(l) - 1, 0) for l in lines)
    S = S_from(best["ll"], ll_reset, n_bound)
    S_starts = np.array([S_from(p["ll"], ll_reset, n_bound) for p in per], float)
    n_conv_starts = sum(1 for p in per if p["converged"] and abs(p["ll"] - best["ll"]) <= CONV_TOLB)
    s_conv = n_conv_starts >= 3
    return dict(
        name=name,
        rep=rep,
        S=float(S),
        ll_B=float(best["ll"]),
        ll_reset=float(ll_reset),
        n_boundaries=n_bound,
        B=best["B"],
        B11=best["B"][0][0],
        B22=best["B"][1][1],
        best_start=best["start"],
        starts=[{k: p[k] for k in ("start", "ll", "max_kkt", "conv_kkt", "conv_dll", "converged", "n_warm", "rows_on_bound", "x")} for p in per],
        SD_S_starts=float(S_starts.std(ddof=1)) if len(S_starts) > 1 else 0.0,
        S_starts=S_starts.tolist(),
        n_starts_conv_within_tol=n_conv_starts,
        S_converged=bool(s_conv),
        step1_ll=float(step1["recomputed_ll"]),
        A1_diff=float(abs(ll_reset - step1["recomputed_ll"])) if rep == 0 else None,
    )


def pct_rank(obs, nulls):
    nulls = np.asarray(nulls, float)
    n = len(nulls)
    if n == 0:
        return dict(rank=float("nan"), p=float("nan"), midp=float("nan"), n_ge=0, n_gt=0, n_lt=0, n_tie=0, N=0)
    n_lt = int(np.sum(nulls < obs - TIE))
    n_gt = int(np.sum(nulls > obs + TIE))
    n_tie = int(np.sum(np.abs(nulls - obs) <= TIE))
    n_ge = int(np.sum(nulls >= obs - TIE))
    rank = (n_lt + 0.5 * n_tie) / n
    p = (1 + n_ge) / (1 + n)
    midp = (n_gt + 0.5 * n_tie + 0.5) / (1 + n)
    return dict(rank=float(rank), p=float(p), midp=float(midp), n_ge=n_ge, n_gt=n_gt, n_lt=n_lt, n_tie=n_tie, N=n)


def bootstrap_ci(vals, ss, nboot=10000, qs=(0.025, 0.975)):
    rng = np.random.default_rng(ss)
    vals = np.asarray(vals, float)
    if len(vals) == 0:
        return [float("nan"), float("nan")]
    idx = rng.integers(0, len(vals), size=(nboot, len(vals)))
    # caller decides the statistic; this helper is for resampling the mean or a quantile later
    return idx  # not used directly


def bootstrap_rank_ci(obs, nulls, ss, nboot=10000):
    rng = np.random.default_rng(ss)
    nulls = np.asarray(nulls, float)
    n = len(nulls)
    if n == 0:
        return [float("nan"), float("nan")]
    ranks = np.empty(nboot)
    for b in range(nboot):
        samp = rng.choice(nulls, size=n, replace=True)
        ranks[b] = pct_rank(obs, samp)["rank"]
    return [float(np.percentile(ranks, 2.5)), float(np.percentile(ranks, 97.5))]


def bootstrap_quantile_ci(nulls, q, ss, nboot=10000):
    rng = np.random.default_rng(ss)
    nulls = np.asarray(nulls, float)
    n = len(nulls)
    if n == 0:
        return float("nan"), [float("nan"), float("nan")]
    point = float(np.quantile(nulls, q))
    qs = np.empty(nboot)
    for b in range(nboot):
        samp = rng.choice(nulls, size=n, replace=True)
        qs[b] = np.quantile(samp, q)
    return point, [float(np.percentile(qs, 2.5)), float(np.percentile(qs, 97.5))]


def holm(ps, alpha=ALPHA, m=M_HOLM):
    items = sorted(ps.items(), key=lambda kv: kv[1])
    out, cutoff = {}, None
    for i, (k, p) in enumerate(items):
        thr = alpha / (m - i)
        pass_ = p <= thr
        out[k] = dict(p=p, threshold=thr, pass_=bool(pass_), rank=i + 1)
        if not pass_ and cutoff is None:
            # subsequent cannot pass
            cutoff = i
        if cutoff is not None and i > cutoff:
            out[k]["pass_"] = False
    return out


# ---------------------------------------------------------------------------
# Phases
# ---------------------------------------------------------------------------

def phase_load():
    WORK.mkdir(exist_ok=True)
    texts, info = load_all_texts()
    # compact JSON (drop huge bits)
    path = WORK / "load_info.json"
    path.write_text(json.dumps(info, indent=2))
    print(json.dumps(info, indent=2))
    # A0 checks
    print("hash_name ok:", info["meta"]["hash_name_ok"])
    print("ZL3b file sha prefix:", info["meta"]["zl3b_sha"][:16], "expected bf5b6d4ac1e3a51b")
    print("W1 sha:", info["CAE_DV_W1"]["sha"], "expected prefix 29df436a suffix 2a2eeb")
    print("W1 counts:", {k: info["CAE_DV_W1"][k] for k in ("n_words", "n_lines", "n_glyphs", "n_boundaries", "n_movable_lines", "movable_token_share_incl_fixed_ends")})
    print("W2 first line index:", info["CAE_DV_W2"]["first_line_index"], "W1 last:", info["CAE_DV_W2"]["w1_last_index"], "equal lines:", info["CAE_DV_W2"]["n_lines_textually_equal_to_a_w1_line"])
    print("token counts:", info["meta"]["token_counts"])
    return texts, info


def phase_precheck():
    """Self-check the fitter on CAE-DV W1 with the closed precheck seeds (section 6)."""
    texts, info = load_all_texts()
    w1 = texts["CAE_DV_W1"]
    t0 = time.time()
    rec, sym, inv, best = step1_for_text("CAE_DV_W1", w1, "precheck")
    print("STEP1 precheck W1")
    print("  loop_ll     ", rec["loop_ll"], "  expected -79623.3260516")
    print("  recomputed  ", rec["recomputed_ll"])
    print("  A", rec["A"])
    print("  pi", rec["pi"])
    print("  cap_hits", rec["cap_hits"], "best_i", rec["best_i"], "basin", rec["basin"], "same_basin", rec["n_restarts_same_basin"])
    print("  expected A ~ [[0.4253, 0.5747], [0.0053, 0.9947]]  pi ~ [0.9916, 0.0084]")

    # B starts from [11801, 5]; N-LINE reps 1-3 from default_rng(11801)
    starts = dirichlet_starts(np.random.default_rng(SeedSequence([11801, 5])), RB)
    jobs = []
    # observed
    jobs.append(job_B("CAE_DV_W1", w1, rec, sym, 0, starts=starts, shuffle_rng=np.random.default_rng(0)))  # shuffle unused
    # the observed job should not consume the 11801 shuffle stream; starts are provided
    rs = np.random.default_rng(11801)
    for rep in (1, 2, 3):
        # each replicate is a new permutation from the SAME continuing rng (default_rng(11801))
        # But nline is called inside job_B if we pass a rng and rep>0... we'd consume starts too.
        # Do shuffles here with the continuing stream, then fit with the FIXED starts.
        lines = nline(w1, rs)
        # fit with starts, no further shuffle
        j = job_B("CAE_DV_W1", lines, rec, sym, 0, starts=starts, shuffle_rng=np.random.default_rng(0))
        j["rep"] = rep
        jobs.append(j)
    # fix observed label
    jobs[0]["rep"] = 0
    for j in jobs:
        print(f"  rep {j['rep']}: S={j['S']:.8e}  B11={j['B11']:.6f} B22={j['B22']:.6f}  "
              f"ll_B={j['ll_B']:.6f} ll_reset={j['ll_reset']:.6f}  A1={j['A1_diff']}  "
              f"SD_starts={j['SD_S_starts']:.3e} conv={j['S_converged']} kkt={[s['max_kkt'] for s in j['starts']]}")
    print("  expected S obs 7.27976e-5, reps 3.04133e-5, 2.42159e-5, 1.19493e-4")
    print("  expected fitted ll obs -79622.673202, reset = step1")
    print("elapsed", round(time.time() - t0, 2), "s")
    out = dict(step1=rec, jobs=jobs, elapsed=time.time() - t0, w1=info["CAE_DV_W1"])
    # drop Bm from disk? keep it, not huge
    (WORK / "precheck.json").write_text(json.dumps(out, indent=2, default=str))
    return out


def save_step1_bundle(name, rec, path):
    path.write_text(json.dumps(rec, indent=2))


_RUN_STATE = {}


def _run_one(pair):
    name, rep = pair
    st = _RUN_STATE
    return job_B(name, st["texts"][name], st["step1"][name], st["syms"][name], rep, 11802)


def phase_run(names=None, nnull=NNULL, resume=True):
    WORK.mkdir(exist_ok=True)
    texts, info = load_all_texts()
    (WORK / "load_info.json").write_text(json.dumps(info, indent=2))
    if names is None:
        names = ["CAE_DV_W1", "CAE_DV_W2", "CAE_V", "HEB_ABJ", "GPOW", "ZL_A", "ZL_B1", "ZL_B2"]

    ckpt_path = WORK / "checkpoint.jsonl"
    done = set()
    if resume and ckpt_path.exists():
        with open(ckpt_path) as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                done.add((r["name"], r["rep"]))
        print(f"resuming, {len(done)} jobs already in {ckpt_path}")

    # Step 1 for registered texts (GPOW reuses W1)
    step1 = {}
    syms = {}
    t0 = time.time()
    for name in ["CAE_DV_W1", "CAE_DV_W2", "CAE_V", "HEB_ABJ", "ZL_A", "ZL_B1", "ZL_B2"]:
        s1_path = WORK / f"step1_{name}.json"
        lines = texts[name]
        print(f"=== step 1 {name} ===", now_pt(), flush=True)
        rec, sym, inv, best = step1_for_text(name, lines, "run", 11802)
        rec_disk = dict(rec)
        rec_disk["Bm"] = rec["Bm"]  # already list
        s1_path.write_text(json.dumps(rec_disk))
        step1[name] = rec
        syms[name] = sym
        print(f"  loop_ll={rec['loop_ll']:.6f} recomputed={rec['recomputed_ll']:.6f} "
              f"basin={rec['basin']} same={rec['n_restarts_same_basin']}/10 "
              f"within_tol={rec['n_within_tol']} cap={rec['cap_hits']} A={rec['A']} pi={rec['pi']}",
              flush=True)

    # Build G-POW from W1 step 1 and SeedSequence([11802, 0])
    rng_p = np.random.default_rng(SeedSequence([11802, 0]))
    gpow_lines, n_planted = aligned_plant(
        texts["CAE_DV_W1"], syms["CAE_DV_W1"],
        np.asarray(step1["CAE_DV_W1"]["pi"]),
        np.asarray(step1["CAE_DV_W1"]["A"]),
        np.asarray(step1["CAE_DV_W1"]["Bm"]),
        rng_p, Q_PLANT,
    )
    texts["GPOW"] = gpow_lines
    step1["GPOW"] = dict(step1["CAE_DV_W1"])  # reuse
    step1["GPOW"]["name"] = "GPOW"
    step1["GPOW"]["n_lines_planted"] = n_planted
    syms["GPOW"] = syms["CAE_DV_W1"]
    (WORK / "gpow_meta.json").write_text(json.dumps(dict(
        n_lines_planted=n_planted, stats=line_stats(gpow_lines),
        sha=line_sha(gpow_lines), w1_sha=line_sha(texts["CAE_DV_W1"]),
    ), indent=2))
    print(f"GPOW planted {n_planted} movable lines, sha={line_sha(gpow_lines)}", flush=True)

    # Job list
    jobs = []
    for name in names:
        for rep in range(0, nnull + 1):
            if (name, rep) not in done:
                jobs.append((name, rep))
    print(f"{len(jobs)} B-jobs to run, {len(done)} already done", flush=True)

    from multiprocessing import Pool
    nworkers = min(8, os.cpu_count() or 8)
    _RUN_STATE.clear()
    _RUN_STATE["texts"] = texts
    _RUN_STATE["step1"] = step1
    _RUN_STATE["syms"] = syms
    written = 0
    t1 = time.time()
    with Pool(nworkers) as pool, open(ckpt_path, "a") as out:
        for j in pool.imap_unordered(_run_one, jobs, chunksize=1):
            out.write(json.dumps(j) + "\n")
            out.flush()
            written += 1
            if written % 10 == 0 or j["rep"] == 0:
                print(f"  done {written}/{len(jobs)}  {j['name']} rep={j['rep']} S={j['S']:.6e} "
                      f"conv={j['S_converged']} elapsed={time.time()-t1:.1f}s", flush=True)
    print(f"run complete, wrote {written} jobs in {time.time()-t1:.1f}s; step1 {t1-t0:.1f}s", flush=True)
    return dict(written=written, step1_s=t1 - t0, run_s=time.time() - t1)


def load_ckpt():
    rows = []
    with open(WORK / "checkpoint.jsonl") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def summarize_text(name, rows, step1=None):
    recs = [r for r in rows if r["name"] == name]
    recs = {r["rep"]: r for r in recs}
    if 0 not in recs:
        return dict(name=name, error="no observed job")
    obs = recs[0]
    nulls = [recs[i] for i in range(1, NNULL + 1) if i in recs]
    conv_nulls = [r for r in nulls if r.get("S_converged")]
    Snull = np.array([r["S"] for r in conv_nulls], float)
    pr = pct_rank(obs["S"], Snull)
    n_distinct = len(set(round(s, 9) for s in Snull)) if len(Snull) else 0
    g_canfail = (n_distinct / len(Snull) >= 0.20) if len(Snull) else False
    sd_null = float(Snull.std(ddof=1)) if len(Snull) > 1 else 0.0
    sd_starts = float(obs["SD_S_starts"])
    if sd_starts == 0:
        pnoise_ratio = None
        pnoise_ok = sd_null > 0
    else:
        pnoise_ratio = sd_null / sd_starts
        pnoise_ok = sd_null > sd_starts
    effN = len(Snull)
    unconv = len(nulls) - len(conv_nulls)
    n_ge = pr["n_ge"]
    p_cons = (1 + n_ge + unconv) / (1 + NNULL)
    p_lib = (1 + n_ge) / (1 + NNULL)
    mean = float(Snull.mean()) if len(Snull) else float("nan")
    z = (obs["S"] - mean) / sd_null if sd_null > 0 else float("nan")
    # bootstrap
    rank_ci = bootstrap_rank_ci(obs["S"], Snull, SeedSequence([11804, hash_name(name), 1]))
    qmap = {}
    for q in (0.05, 0.10, 0.25, 0.75, 0.90, 0.95):
        pt, ci = bootstrap_quantile_ci(Snull, q, SeedSequence([11804, hash_name(name), 2, int(round(100 * q))]))
        qmap[str(q)] = dict(q=pt, ci=ci)
    testable = bool(obs["S_converged"] and (unconv / max(len(nulls), 1) <= 0.10) and effN >= 40 and g_canfail)
    return dict(
        name=name,
        S=obs["S"],
        ll_B=obs["ll_B"],
        ll_reset=obs["ll_reset"],
        A1_diff=obs.get("A1_diff"),
        B11=obs["B11"],
        B22=obs["B22"],
        n_boundaries=obs["n_boundaries"],
        obs_converged=obs["S_converged"],
        SD_S_starts=sd_starts,
        SD_S_null=sd_null,
        P_NOISE_ratio=pnoise_ratio,
        P_NOISE_ok=pnoise_ok,
        n_null_present=len(nulls),
        n_null_converged=len(conv_nulls),
        n_unconverged=unconv,
        effective_N=effN,
        n_distinct_null_S_1e9=n_distinct,
        G_CANFAIL=g_canfail,
        rank=pr["rank"],
        p=pr["p"],
        midp=pr["midp"],
        p_cons=p_cons,
        p_lib=p_lib,
        n_ge=n_ge,
        n_tie=pr["n_tie"],
        null_mean=mean,
        z=z,
        rank_ci=rank_ci,
        quantiles=qmap,
        testable_primary_rule=testable,  # section 9.5; G-POW does not require G-CANFAIL
        step1_basin=(step1 or {}).get("basin"),
        step1_n_same_basin=(step1 or {}).get("n_restarts_same_basin"),
        step1_n_within_tol=(step1 or {}).get("n_within_tol"),
        step1_A=(step1 or {}).get("A"),
        step1_pi=(step1 or {}).get("pi"),
        step1_loop_ll=(step1 or {}).get("loop_ll"),
        step1_recomputed_ll=(step1 or {}).get("recomputed_ll"),
        step1_converged=(step1 or {}).get("step1_converged"),
        step1_cap_hits=(step1 or {}).get("cap_hits"),
    )


def phase_summarize():
    rows = load_ckpt()
    step1 = {}
    for name in ["CAE_DV_W1", "CAE_DV_W2", "CAE_V", "HEB_ABJ", "ZL_A", "ZL_B1", "ZL_B2"]:
        p = WORK / f"step1_{name}.json"
        if p.exists():
            step1[name] = json.loads(p.read_text())
    if "CAE_DV_W1" in step1:
        step1["GPOW"] = dict(step1["CAE_DV_W1"])
        step1["GPOW"]["name"] = "GPOW"
        gm = WORK / "gpow_meta.json"
        if gm.exists():
            step1["GPOW"].update(json.loads(gm.read_text()))
    names = ["CAE_DV_W1", "CAE_DV_W2", "CAE_V", "HEB_ABJ", "GPOW", "ZL_A", "ZL_B1", "ZL_B2"]
    summ = {n: summarize_text(n, rows, step1.get(n)) for n in names}

    # Gates
    w1, w2 = summ["CAE_DV_W1"], summ["CAE_DV_W2"]
    def window_ok(w, require_canfail=True, p_cut=0.05 / 3):
        conv_rate = w["n_null_converged"] / NNULL if NNULL else 0
        ok = (
            w["obs_converged"]
            and conv_rate >= 0.90
            and w["effective_N"] >= 40
            and (w["G_CANFAIL"] if require_canfail else True)
        )
        return ok, conv_rate

    ok1, cr1 = window_ok(w1, True)
    ok2, cr2 = window_ok(w2, True)
    mean_rank = (w1["rank"] + w2["rank"]) / 2
    g_fpr = (0.10 <= mean_rank <= 0.90) and (w1["p"] > 0.05 / 3) and (w2["p"] > 0.05 / 3)
    # mean-rank bootstrap: resample both windows independently
    # Need raw nulls
    by = {}
    for r in rows:
        by.setdefault(r["name"], {})[r["rep"]] = r
    def conv_S(name):
        recs = by[name]
        return recs[0]["S"], np.array([recs[i]["S"] for i in range(1, NNULL + 1) if i in recs and recs[i]["S_converged"]], float)

    s1, n1 = conv_S("CAE_DV_W1")
    s2, n2 = conv_S("CAE_DV_W2")
    rng = np.random.default_rng(SeedSequence([11804, 0]))
    means = np.empty(10000)
    for b in range(10000):
        r1 = pct_rank(s1, rng.choice(n1, size=len(n1), replace=True))["rank"]
        r2 = pct_rank(s2, rng.choice(n2, size=len(n2), replace=True))["rank"]
        means[b] = 0.5 * (r1 + r2)
    mean_rank_ci = [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]
    borderline = (mean_rank_ci[0] <= 0.10 <= mean_rank_ci[1]) or (mean_rank_ci[0] <= 0.90 <= mean_rank_ci[1])

    g1_pass = bool(ok1 and ok2 and g_fpr)
    pnoise_pass = bool(w1["P_NOISE_ok"] and w2["P_NOISE_ok"])

    gpow = summ["GPOW"]
    # G-POW: convergence, effective N, P-NOISE; G-CANFAIL printed but not required; p <= 0.05/3
    gpow_conv_rate = gpow["n_null_converged"] / NNULL
    gpow_testable = bool(gpow["obs_converged"] and gpow_conv_rate >= 0.90 and gpow["effective_N"] >= 40 and gpow["P_NOISE_ok"])
    gpow_pass = bool(gpow_testable and gpow["p"] <= 0.05 / 3)

    # secondary
    sec = {}
    for n in ("CAE_V", "HEB_ABJ"):
        w = summ[n]
        ok, cr = window_ok(w, True)
        rank_ok = 0.05 <= w["rank"] <= 0.95
        ci = w["rank_ci"]
        edge = (ci[0] <= 0.05 <= ci[1]) or (ci[0] <= 0.95 <= ci[1])
        sec[n] = dict(conditions_ok=ok, conv_rate=cr, rank_ok=rank_ok, row_testable=bool(ok and rank_ok), borderline=edge)

    # primary Holm
    primary = ["ZL_A", "ZL_B1", "ZL_B2"]
    pmap, notes = {}, {}
    for n in primary:
        w = summ[n]
        # NOT TESTABLE if observed unconverged, >10% nulls unconverged, effN<40, or G-CANFAIL fails (enters Holm as p=1)
        nt = (not w["obs_converged"]) or (w["n_unconverged"] / NNULL > 0.10) or (w["effective_N"] < 40) or (not w["G_CANFAIL"])
        notes[n] = dict(not_testable=nt)
        pmap[n] = 1.0 if nt else w["p"]
        pmap_cons = None
    holm_lib = holm({n: (1.0 if notes[n]["not_testable"] else summ[n]["p"]) for n in primary})
    holm_cons = holm({n: (1.0 if notes[n]["not_testable"] else summ[n]["p_cons"]) for n in primary})
    # convergence-sensitive if Holm decision differs
    cs = {}
    for n in primary:
        cs[n] = holm_lib[n]["pass_"] != holm_cons[n]["pass_"]

    gates_pass = g1_pass and pnoise_pass and gpow_pass
    passing = [n for n in primary if holm_lib[n]["pass_"] and not notes[n]["not_testable"] and not cs[n]]
    if not gates_pass:
        verdict = "NOT TESTABLE"
    elif passing:
        verdict = "BOUNDARY STATE IN WORD ORDER in " + " + ".join(passing)
    else:
        verdict = "NOT SUPPORTED"

    report = dict(
        written_at=now_pt(),
        gates=dict(
            G1=dict(pass_=g1_pass, w1_ok=ok1, w2_ok=ok2, conv_rate_w1=cr1, conv_rate_w2=cr2,
                    rank_w1=w1["rank"], rank_w2=w2["rank"], mean_rank=mean_rank,
                    mean_rank_ci=mean_rank_ci, G_FPR=g_fpr, borderline=borderline,
                    p_w1=w1["p"], p_w2=w2["p"]),
            P_NOISE=dict(pass_=pnoise_pass, w1=w1["P_NOISE_ok"], w2=w2["P_NOISE_ok"],
                         ratio_w1=w1["P_NOISE_ratio"], ratio_w2=w2["P_NOISE_ratio"],
                         sd_starts_w1=w1["SD_S_starts"], sd_null_w1=w1["SD_S_null"],
                         sd_starts_w2=w2["SD_S_starts"], sd_null_w2=w2["SD_S_null"]),
            G_POW=dict(pass_=gpow_pass, testable=gpow_testable, p=gpow["p"], rank=gpow["rank"],
                       S=gpow["S"], z=gpow["z"], null_mean=gpow["null_mean"],
                       n_lines_planted=step1.get("GPOW", {}).get("n_lines_planted"),
                       P_NOISE_ok=gpow["P_NOISE_ok"], G_CANFAIL=gpow["G_CANFAIL"],
                       effective_N=gpow["effective_N"]),
        ),
        secondary=sec,
        primary= {n: dict(summary=summ[n], not_testable=notes[n]["not_testable"],
                          holm_lib=holm_lib[n], holm_cons=holm_cons[n],
                          convergence_sensitive=cs[n]) for n in primary},
        all=summ,
        verdict=verdict,
        passing=passing,
        gates_1_2_3=gates_pass,
    )
    (WORK / "summary.json").write_text(json.dumps(report, indent=2, default=str))
    print(json.dumps(report["gates"], indent=2, default=str))
    print("VERDICT:", verdict)
    for n in primary:
        s = summ[n]
        print(f"  {n}: S={s['S']:.6e}  p={s['p']} rank={s['rank']:.4f}  "
              f"basin={s['step1_basin']} same={s['step1_n_same_basin']}/10 within={s['step1_n_within_tol']}  "
              f"null_mean={s['null_mean']:.6e} z={s['z']:.3f}  testable={not notes[n]['not_testable']} "
              f"holm={holm_lib[n]['pass_']} CS={cs[n]}")
    for n in ("CAE_DV_W1", "CAE_DV_W2", "CAE_V", "HEB_ABJ", "GPOW"):
        s = summ[n]
        print(f"  {n}: S={s['S']:.6e} p={s['p']} rank={s['rank']:.4f} z={s.get('z')}")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True, choices=["load", "precheck", "run", "summarize", "all"])
    ap.add_argument("--names", default="")
    args = ap.parse_args()
    os.chdir(REPO)
    WORK.mkdir(exist_ok=True)
    names = [x for x in args.names.split(",") if x] or None
    if args.phase == "load":
        phase_load()
    elif args.phase == "precheck":
        phase_precheck()
    elif args.phase == "run":
        phase_run(names=names)
    elif args.phase == "summarize":
        phase_summarize()
    elif args.phase == "all":
        phase_load()
        phase_precheck()
        phase_run(names=names)
        phase_summarize()


if __name__ == "__main__":
    main()
