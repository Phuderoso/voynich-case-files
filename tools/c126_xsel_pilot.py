#!/usr/bin/env python3
"""C126 rev 1 -- cross-selection pilot (CONTROLS ONLY; never reads the Voynich transcription).

Kryptos's blind review of rev 0 (2026-11-23), point 1: choose the argmax singulion order on
half A of every page (odd pseudo-lines), measure adjacency similarity on half B (even lines).
Statistics (all on half B, order pi* chosen on half A):
  X     = [S_B(pi*) - S_B(bound)] / sd_pi S_B(pi)        (primary candidate)
  X_tr  = [T_B(pi*) - mean_pi T_B(pi)] / sd_pi T_B(pi)    (transitions only; sensitivity)
          T = mean similarity over the n-1 bifolio-to-bifolio transitions of a singulion order.
Two decision routes are piloted:
  (P) exact bifolio-relabel null: B-half bifolio identities permuted by every sigma in S_n
      (A half, pi* and the bound order fixed); p_perm = rank of X among the n! relabelings.
  (R) reference route as in rev 0: X vs control references R_NEST / R_SHUF (other text).
Gate asked by Kryptos: on no-continuity controls (SHUF), mean X near 0 and FPR <= 1/20.
Plant ladder lam in {1, 0.75, 0.5} (review point 3).
Reuses layouts / similarity / control generator from tools/c126_order.py (rev 0, unchanged).
"""
import argparse, json, time, hashlib, sys, itertools
import numpy as np
sys.path.insert(0, "tools")
from c126_order import Quire, sim_matrix, make_quire, load_tokens, singulion_pages, nested_pages, nonconfoliate_pairs

LINE = 10  # words per pseudo-line in controls

def halves(page):
    A, B = [], []
    for i in range(0, len(page), LINE):
        (A if (i // LINE) % 2 == 0 else B).extend(page[i:i + LINE])
    return A, B

def trans_idx(q):
    # transitions of each singulion order: last page of bifolio t (L2v) -> first page of t+1 (L1r)
    return np.array([[(4 * pi[t] + 3, 4 * pi[t + 1] + 0) for t in range(q.n - 1)] for pi in q.perms])

def relabel(M, sig):
    # page index 4*b+k -> 4*sig[b]+k
    idx = np.array([4 * sig[p // 4] + p % 4 for p in range(M.shape[0])])
    return M[np.ix_(idx, idx)]

def stats_x(q, TI, MA, MB, bound, perm_null=True):
    sA = q.S_sing(MA)
    best = int(np.argmax(sA))
    def x_of(M):
        s = q.S_sing(M); sd = float(s.std()) or 1e-12
        t = M[TI[..., 0], TI[..., 1]].mean(1); tsd = float(t.std()) or 1e-12
        return (float(s[best]) - q.S_nested(M, bound)) / sd, (float(t[best]) - float(t.mean())) / tsd
    X, Xtr = x_of(MB)
    out = dict(X=X, Xtr=Xtr, best=best)
    if perm_null:
        xs, ts = [], []
        for sig in q.perms:
            a, b = x_of(relabel(MB, sig)); xs.append(a); ts.append(b)
        xs, ts = np.array(xs), np.array(ts)
        out["p_perm"] = float((xs >= X - 1e-12).sum() / len(xs))
        out["p_perm_tr"] = float((ts >= Xtr - 1e-12).sum() / len(ts))
    return out

def selftest():
    ok = True
    def chk(c, m):
        nonlocal ok; print(("PASS " if c else "FAIL ") + m); ok &= bool(c)
    A, B = halves([str(i) for i in range(45)])
    chk(len(A) == 25 and len(B) == 20 and not set(A) & set(B), "halves split by alternating 10-word lines")
    q = Quire(5); TI = trans_idx(q)
    chk(TI.shape == (120, 4, 2), "transition index shape")
    M = np.arange(400, dtype=float).reshape(20, 20)
    chk(np.allclose(relabel(M, tuple(range(5))), M), "identity relabel")
    # strong planted singulion -> pi* true and p_perm small
    rng = np.random.default_rng(0); n = 5
    vocab = [f"w{i}" for i in range(4000)]
    st = [[vocab[int(x)] for x in rng.integers(100 * i, 100 * i + 150, 200)] for i in range(4 * n)]
    pages = [None] * (4 * n)
    for r, (b, k) in enumerate(singulion_pages(list(range(n)))): pages[4 * b + k] = st[r]
    H = [halves(p) for p in pages]
    s = stats_x(q, TI, sim_matrix([h[0] for h in H]), sim_matrix([h[1] for h in H]), [3, 0, 4, 1, 2])
    chk(q.perms[s["best"]].tolist() == list(range(n)) and s["p_perm"] <= 1 / 120 + 1e-9, f"strong plant: pi* true, p_perm {s['p_perm']:.4f}")
    print("SELFTEST", "ALL PASS" if ok else "FAILED"); return ok

def pilot(a):
    t0 = time.time(); rng = np.random.default_rng(a.seed)
    texts = {"caesar": "data/corpora/pg218.txt", "cervantes": "data/corpora/pg2000.txt"}
    toks = {k: load_tokens(v) for k, v in texts.items()}
    res = dict(seed=a.seed, W=a.W, R_ref=a.R, E=a.E, alpha=a.alpha, line=LINE,
               texts={k: hashlib.sha256(open(v, "rb").read()).hexdigest() for k, v in texts.items()},
               tool_sha=hashlib.sha256(open(__file__, "rb").read()).hexdigest(), cells=[])
    log = []
    for n in (5, 6):
        q = Quire(n); TI = trans_idx(q)
        for metric in ("cos", "jac"):
            classes = [("NEST", 1.0), ("SHUF", 1.0)] + [("SING", l) for l in (1.0, 0.75, 0.5)]
            D = {}
            for tx in toks:
                for cls, lam in classes:
                    rows = []
                    for i in range(a.R + a.E):
                        pages, bound, _ = make_quire(toks[tx], n, a.W, cls, lam, rng)
                        H = [halves(p) for p in pages]
                        rows.append(stats_x(q, TI, sim_matrix([h[0] for h in H], metric),
                                            sim_matrix([h[1] for h in H], metric), bound, perm_null=(i >= a.R)))
                    D[(tx, cls, lam)] = rows
            for ref, ev in (("caesar", "cervantes"), ("cervantes", "caesar")):
                rN = np.array([r["X"] for r in D[(ref, "NEST", 1.0)][:a.R]])
                rU = np.array([r["X"] for r in D[(ref, "SHUF", 1.0)][:a.R]])
                for cls, lam in classes:
                    ev_rows = D[(ev, cls, lam)][a.R:]
                    X = np.array([r["X"] for r in ev_rows])
                    pp = np.array([r["p_perm"] for r in ev_rows]); pt = np.array([r["p_perm_tr"] for r in ev_rows])
                    pN = np.array([(1 + (rN >= x).sum()) / (1 + len(rN)) for x in X])
                    pU = np.array([(1 + (rU >= x).sum()) / (1 + len(rU)) for x in X])
                    cell = dict(n=n, metric=metric, ref=ref, eval=ev, cls=cls, lam=lam,
                                X_mean=round(float(X.mean()), 3), X_sd=round(float(X.std()), 3),
                                Xall_mean_eval=round(float(np.mean([r["X"] for r in D[(ev, cls, lam)][:a.R]])), 3),
                                perm_hits=int((pp <= a.alpha).sum()), perm_tr_hits=int((pt <= a.alpha).sum()),
                                ref_SUP=int(((pN <= a.alpha) & (pU <= a.alpha)).sum()), E=a.E,
                                perm_floor=round(1 / len(q.perms), 5))
                    res["cells"].append(cell)
                    line = (f"n={n} {metric} ref={ref:9s} ev={ev:9s} {cls}{'' if cls!='SING' else '(%.2f)'%lam:11s} "
                            f"X {cell['X_mean']:+.2f}+-{cell['X_sd']:.2f} | perm p<=a {cell['perm_hits']}/{a.E} "
                            f"tr {cell['perm_tr_hits']}/{a.E} | ref SUP {cell['ref_SUP']}/{a.E}")
                    print(line, flush=True); log.append(line)
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(a.out + ".json", "w"), indent=1)
    open(a.out + ".log", "w").write("\n".join(log) + f"\nelapsed {res['elapsed_s']} s\n")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--seed", type=int, default=11884); ap.add_argument("--W", type=int, default=200)
    ap.add_argument("--R", type=int, default=200); ap.add_argument("--E", type=int, default=40)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--out", default="analysis/C126_xsel_pilot")
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if a.pilot: pilot(a)
