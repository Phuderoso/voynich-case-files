#!/usr/bin/env python3
"""PE009 post hoc (after gates and test; no decision weight; deterministic, no randomness).
Q1 total/sum ratio in C on set A (first look at A; B's was published by PE008) - quantiles, how many above 1.
Q2 what the reverse number is made of: share of totals with sub-unit signs (grain-only notation) vs N01/N14-only
   (readable in any system), per set; for comparison the same on the non-CAP mismatches.
Q3 the two H1 matches: the ratio found and the sign pair.
"""
import json, os, sys
from fractions import Fraction as Fr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe009_other_quantity as X, pe008_grain_totals as G, pe001_totals as P
S = G.target_sets(); C = X.C; out = {}
rs = []
for t in S["R"]:
    s = X.csum(t); v = P.value(t["total"], C)
    if s and v is not None: rs.append(round(v / s, 3))
rs.sort(); out["Q1_A_ratio_total_over_sum_C"] = {"n": len(rs), "sorted": rs, "median": rs[len(rs) // 2], "above_1": sum(r > 1 for r in rs)}
def comp(tabs):
    sub = sum(any(s in P.C_SUB_SIGNS for s in t["total"]) for t in tabs)
    small = sum(set(t["total"]) <= {"N01", "N14"} for t in tabs)
    return {"tablets": len(tabs), "total_has_subunit": sub, "total_only_N01_N14": small}
out["Q2_total_composition"] = {"A_grain": comp(S["R"]), "B_grain": comp(S["P"]), "nonCAP_A": comp(S["nonCAP_R"]),
                               "nonCAP_B": comp(S["nonCAP_P"])}
names = {}
for a in C:
    for b in C:
        if a != b: names.setdefault(Fr(C[a], C[b]), []).append(f"{a}/{b}")
q3 = []
for name, key in (("A", "R"), ("B", "P")):
    for t in S[key]:
        s = X.csum(t); v = P.value(t["total"], C)
        if s and v is not None and Fr(v, s) in names:
            q3.append({"set": name, "pid": t["pid"], "ratio": str(Fr(v, s)), "sign_pairs": names[Fr(v, s)],
                       "n_entries": len(t["entries"])})
out["Q3_H1_matches"] = q3
json.dump(out, open("analysis/pe009_posthoc.json", "w"), indent=1); print(json.dumps(out, indent=1))
