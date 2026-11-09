#!/usr/bin/env python3
"""PE008 post hoc (after gates and test; no decision weight; deterministic).
Q1 'omit-one': total = sum of all entries minus exactly one entry (any position), any admitted system; set P and R.
Q2 'any subset': total = sum of some subset of >= 1 entries (proper subset), any admitted system (n <= 16 only).
Q3 ratio total/sum (in C for tablets that admit C) on P: quantiles; and how many totals exceed the sum.
For Q1/Q2 the total-permutation rate (R = 999, seed 811) is given only as a scale for chance, not as a test.
"""
import json, os, sys, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe008_grain_totals as G, pe001_totals as P
S = G.target_sets(); out = {}
def omit_one(e, t):
    for tb in G.SYS.values():
        vs = [P.value(x, tb) for x in e]; vt = P.value(t, tb)
        if vt is None or None in vs or len(vs) < 3: continue
        if any(sum(vs) - v == vt for v in vs): return True
    return False
def any_subset(e, t):
    for tb in G.SYS.values():
        vs = [P.value(x, tb) for x in e]; vt = P.value(t, tb)
        if vt is None or None in vs or len(vs) > 16: continue
        sums = {0}
        for v in vs: sums |= {s + v for s in sums}
        if vt in sums and vt != sum(vs): return True
    return False
for name in ("P", "R"):
    tabs = S[name]
    for q, f in (("Q1_omit_one", omit_one), ("Q2_any_proper_subset", any_subset)):
        obs = sum(f(t["entries"], t["total"]) for t in tabs); rng = random.Random(811); tots = [t["total"] for t in tabs]; nl = []
        for _ in range(999):
            sh = tots[:]; rng.shuffle(sh); nl.append(sum(f(t["entries"], x) for t, x in zip(tabs, sh)))
        out[f"{name}_{q}"] = {"matched": obs, "of": len(tabs), "perm_mean": sum(nl) / len(nl),
                              "perm_rate_ge_obs": (1 + sum(m >= obs for m in nl)) / 1000,
                              "pids": [t["pid"] for t in tabs if f(t["entries"], t["total"])]}
C = G.SYS["C"]; rs = []
for t in S["P"]:
    vs = [P.value(x, C) for x in t["entries"]]; vt = P.value(t["total"], C)
    if vt is None or None in vs: continue
    rs.append(round(vt / sum(vs), 3))
rs.sort(); out["Q3_P_ratio_total_over_sum_C"] = {"n": len(rs), "ratios_sorted": rs, "above_1": sum(r > 1 for r in rs),
    "median": rs[len(rs) // 2] if rs else None}
json.dump(out, open("analysis/pe008_posthoc.json", "w"), indent=1); print(json.dumps(out, indent=1))
