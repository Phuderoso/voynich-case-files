#!/usr/bin/env python3
"""C126 (F-ORDER) design tool -- CONTROLS ONLY in rev 0.

Question (case-file/C126-bifolio-order.md): in a quire of n bifolia, is the gain in
adjacent-page vocabulary similarity from the best *singulion* (sequential-bifolia)
order over the bound *nested* order larger than when the nested order is the true
reading order, and larger than when pages carry no continuity at all?

Layout conventions
  bifolio b = (leaf L1, leaf L2); pages L1r L1v L2r L2v.
  nested binding of bifolio sequence c1..cn (outer -> inner):
      leaves c1.L1 .. cn.L1, cn.L2 .. c1.L2 ; reading = r,v of each leaf.
  singulion order pi: bifolia read one after another, each as L1r L1v L2r L2v.
  Bifolio orientation is fixed (no flips), as in Layfield & Davis (n! orders).
  S(order) = mean similarity over consecutive page pairs that are NOT confoliate
  (confoliate pairs are adjacent in every arrangement): 2n-1 pairs in both layouts.
  G = max_pi S(pi) - S(bound);  G_std = G / sd_pi S(pi)   (primary, scale-free).

This file NEVER reads the Voynich transcription in rev 0.
"""
import argparse, itertools, json, math, re, sys, time, hashlib
import numpy as np

# ---------------------------------------------------------------- layouts
def nested_pages(bifs):
    """bifs: list of bifolio ids in outer->inner order; each bifolio has pages
    (b,0..3) = L1r L1v L2r L2v. Returns reading order of page keys."""
    leaves = [(b, 0) for b in bifs] + [(b, 1) for b in reversed(bifs)]
    out = []
    for b, l in leaves:
        out += [(b, 2 * l), (b, 2 * l + 1)]
    return out

def singulion_pages(bifs):
    out = []
    for b in bifs:
        out += [(b, 0), (b, 1), (b, 2), (b, 3)]
    return out

def nonconfoliate_pairs(order):
    """consecutive pairs except recto/verso of the same leaf."""
    pr = []
    for a, c in zip(order, order[1:]):
        same_leaf = a[0] == c[0] and a[1] // 2 == c[1] // 2
        if not same_leaf:
            pr.append((a, c))
    return pr

# ---------------------------------------------------------------- similarity
def sim_matrix(pages, metric="cos", floor=2):
    """pages: list of token lists. Types with quire count < floor are dropped."""
    from collections import Counter
    tot = Counter(w for p in pages for w in p)
    voc = sorted(w for w, c in tot.items() if c >= floor)
    ix = {w: i for i, w in enumerate(voc)}
    X = np.zeros((len(pages), max(1, len(voc))))
    for i, p in enumerate(pages):
        for w in p:
            j = ix.get(w)
            if j is not None:
                X[i, j] += 1
    if metric == "cos":
        nrm = np.linalg.norm(X, axis=1)
        nrm[nrm == 0] = 1
        Y = X / nrm[:, None]
        return Y @ Y.T
    B = (X > 0).astype(float)
    inter = B @ B.T
    sz = B.sum(1)
    uni = sz[:, None] + sz[None, :] - inter
    uni[uni == 0] = 1
    return inter / uni

class Quire:
    """n bifolia, page index p = 4*b + k (k = 0..3)."""
    def __init__(self, n):
        self.n = n
        self.perms = np.array(list(itertools.permutations(range(n))))
        # pair index arrays for every singulion permutation
        P = []
        for pi in self.perms:
            pr = nonconfoliate_pairs(singulion_pages(list(pi)))
            P.append([(4 * a[0] + a[1], 4 * c[0] + c[1]) for a, c in pr])
        self.sing_pairs = np.array(P)            # (n!, 2n-1, 2)
        assert self.sing_pairs.shape[1] == 2 * n - 1
    def S_sing(self, M):
        a, c = self.sing_pairs[..., 0], self.sing_pairs[..., 1]
        return M[a, c].mean(1)
    def S_nested(self, M, bifs):
        pr = nonconfoliate_pairs(nested_pages(list(bifs)))
        assert len(pr) == 2 * self.n - 1
        return float(np.mean([M[4 * a[0] + a[1], 4 * c[0] + c[1]] for a, c in pr]))
    def stats(self, M, bound_bifs, true_sing=None):
        s = self.S_sing(M)
        sb = self.S_nested(M, bound_bifs)
        best = int(np.argmax(s))
        sd = float(s.std()) or 1e-12
        out = dict(G=float(s[best] - sb), G_std=float((s[best] - sb) / sd),
                   S_bound=sb, S_best=float(s[best]), n_pairs=2 * self.n - 1)
        if true_sing is not None:
            t = int(np.where((self.perms == np.array(true_sing)).all(1))[0][0])
            out["true_rank_norm"] = float((s > s[t]).sum() / (len(s) - 1))
            out["true_is_best"] = bool(best == t)
        return out

# ---------------------------------------------------------------- control text
def load_tokens(path):
    t = open(path, encoding="utf-8", errors="ignore").read()
    a = t.find("*** START"); b = t.find("*** END")
    if a >= 0: t = t[t.find("\n", a):]
    if b >= 0: t = t[:t.find("*** END")]
    return re.findall(r"[^\W\d_]+", t.lower())

def make_quire(tok, n, W, cls, lam, rng):
    """Returns (pages indexed 4*b+k, bound bifolio order, true singulion order or None).
    Continuity stream: contiguous text; each word kept with prob lam, else replaced
    by a word drawn from a random position in the whole text (dilution plant)."""
    npg = 4 * n
    L = len(tok)
    def stream(m):
        s = int(rng.integers(0, L - m - 1))
        w = list(tok[s:s + m])
        rep = rng.random(m) >= lam
        for i in np.where(rep)[0]:
            w[i] = tok[int(rng.integers(0, L))]
        return w
    if cls == "SHUF":   # no continuity: every page from an independent random place
        chunks = [stream(W) for _ in range(npg)]
    else:
        st = stream(W * npg)
        chunks = [st[i * W:(i + 1) * W] for i in range(npg)]
    pages = [None] * npg
    if cls == "NEST":   # true reading order = nested order of bifolia 0..n-1
        order = nested_pages(list(range(n)))
        for r, (b, k) in enumerate(order):
            pages[4 * b + k] = chunks[r]
        return pages, list(range(n)), None
    if cls == "SING":   # true reading = singulions 0..n-1 ; misbound nested by random perm
        for r, (b, k) in enumerate(singulion_pages(list(range(n)))):
            pages[4 * b + k] = chunks[r]
        bound = list(rng.permutation(n))
        return pages, bound, list(range(n))
    # SHUF: arbitrary assignment, bound = identity
    for i in range(npg):
        pages[i] = chunks[i]
    return pages, list(range(n)), None

# ---------------------------------------------------------------- selftest
def selftest():
    ok = True
    def chk(c, m):
        nonlocal ok
        print(("PASS " if c else "FAIL ") + m); ok &= bool(c)
    np_ = nested_pages([0, 1])
    chk(np_ == [(0, 0), (0, 1), (1, 0), (1, 1), (1, 2), (1, 3), (0, 2), (0, 3)], "nested layout n=2")
    chk(len(nonconfoliate_pairs(np_)) == 3, "nested non-confoliate pairs = 2n-1")
    for n in (5, 6):
        q = Quire(n)
        chk(len(q.perms) == math.factorial(n), f"n={n}: {len(q.perms)} singulion orders")
    # planted: pages of a perfect singulion chain -> true order is best
    rng = np.random.default_rng(0)
    n = 5; q = Quire(n)
    vocab = [f"w{i}" for i in range(4000)]
    st = []
    for i in range(4 * n):   # strong drift: page i uses words from window around i
        st.append([vocab[int(x)] for x in rng.integers(100 * i, 100 * i + 150, 200)])
    pages = [None] * (4 * n)
    for r, (b, k) in enumerate(singulion_pages(list(range(n)))):
        pages[4 * b + k] = st[r]
    M = sim_matrix(pages)
    s = q.stats(M, [3, 0, 4, 1, 2], true_sing=list(range(n)))
    chk(s["true_is_best"] and s["G"] > 0, f"strong planted singulion recovered (G={s['G']:.3f})")
    pages2 = [None] * (4 * n)
    for r, (b, k) in enumerate(nested_pages(list(range(n)))):
        pages2[4 * b + k] = st[r]
    s2 = q.stats(sim_matrix(pages2), list(range(n)))
    chk(s2["G"] < 0, f"strong planted nested: best singulion below true nested (G={s2['G']:.3f})")
    J = sim_matrix(pages, metric="jac")
    chk(np.allclose(np.diag(J), 1) and J.max() <= 1 + 1e-9, "jaccard bounds")
    print("SELFTEST", "ALL PASS" if ok else "FAILED")
    return ok

# ---------------------------------------------------------------- pilot (controls only)
def pilot(args):
    t0 = time.time()
    rng = np.random.default_rng(args.seed)
    texts = {"caesar": "data/corpora/pg218.txt", "cervantes": "data/corpora/pg2000.txt"}
    toks = {k: load_tokens(v) for k, v in texts.items()}
    sha = {k: hashlib.sha256(open(v, "rb").read()).hexdigest() for k, v in texts.items()}
    res = {"seed": args.seed, "W": args.W, "R_ref": args.R, "R_eval": args.E,
           "alpha": args.alpha, "texts": sha, "cells": []}
    log = []
    for n in (5, 6):
        q = Quire(n)
        for lam in (1.0, 0.5, 0.25):
            for metric in ("cos", "jac"):
                dist = {}
                for tx in toks:
                    for cls in ("NEST", "SING", "SHUF"):
                        R = args.R + args.E
                        v, rec = [], []
                        for _ in range(R):
                            pages, bound, true = make_quire(toks[tx], n, args.W, cls, lam, rng)
                            st = q.stats(sim_matrix(pages, metric), bound, true)
                            v.append(st["G_std"])
                            if true is not None: rec.append(st["true_rank_norm"])
                        dist[(tx, cls)] = (np.array(v), rec)
                # reference on one text, held-out evaluation on the other
                for ref, ev in (("caesar", "cervantes"), ("cervantes", "caesar")):
                    rN = dist[(ref, "NEST")][0][:args.R]
                    rS = dist[(ref, "SING")][0][:args.R]
                    rU = dist[(ref, "SHUF")][0][:args.R]
                    def call(g):
                        pN = (1 + (rN >= g).sum()) / (1 + len(rN))
                        pU = (1 + (rU >= g).sum()) / (1 + len(rU))
                        pS = (1 + (rS <= g).sum()) / (1 + len(rS))
                        if pN <= args.alpha and pU <= args.alpha: return "SUPPORTED"
                        if pS <= args.alpha: return "EXCLUDED"
                        return "NOT_DISCRIMINATED"
                    cell = dict(n=n, lam=lam, metric=metric, ref=ref, eval=ev)
                    for cls in ("NEST", "SING", "SHUF"):
                        g = dist[(ev, cls)][0][args.R:]
                        calls = [call(x) for x in g]
                        cell[cls] = {c: calls.count(c) for c in ("SUPPORTED", "EXCLUDED", "NOT_DISCRIMINATED")}
                        cell[cls + "_Gstd_mean"] = round(float(g.mean()), 3)
                        cell[cls + "_Gstd_sd"] = round(float(g.std()), 3)
                    rec = dist[(ev, "SING")][1][args.R:]
                    cell["SING_true_rank_norm_mean"] = round(float(np.mean(rec)), 3)
                    res["cells"].append(cell)
                    line = (f"n={n} lam={lam} {metric} ref={ref:9s} eval={ev:9s} | "
                            f"G_std mean NEST {cell['NEST_Gstd_mean']:+.2f} SHUF {cell['SHUF_Gstd_mean']:+.2f} SING {cell['SING_Gstd_mean']:+.2f} | "
                            f"SING->SUP {cell['SING']['SUPPORTED']}/{args.E} NEST->SUP {cell['NEST']['SUPPORTED']}/{args.E} "
                            f"SHUF->SUP {cell['SHUF']['SUPPORTED']}/{args.E} NEST->EXC {cell['NEST']['EXCLUDED']}/{args.E} "
                            f"SHUF->EXC {cell['SHUF']['EXCLUDED']}/{args.E} | true-rank {cell['SING_true_rank_norm_mean']}")
                    print(line, flush=True); log.append(line)
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(args.out + ".json", "w"), indent=1)
    open(args.out + ".log", "w").write("\n".join(log) + f"\nelapsed {res['elapsed_s']} s\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--seed", type=int, default=11883)
    ap.add_argument("--W", type=int, default=200)
    ap.add_argument("--R", type=int, default=200)
    ap.add_argument("--E", type=int, default=20)
    ap.add_argument("--alpha", type=float, default=0.025)
    ap.add_argument("--out", default="analysis/C126_design_pilot")
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if a.pilot: pilot(a)
