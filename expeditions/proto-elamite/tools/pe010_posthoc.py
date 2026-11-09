#!/usr/bin/env python3
"""PE010 post hoc (after gates and test; no decision weight; deterministic).
Q1 where the reverse sits relative to the mean entry: n * total / sum in C (1 = mean entry) on D2, A_PE009, B_PE009.
Q2 where it sits relative to the entries: share of totals below the smallest entry, between min and max, above max
   (D1 uses readable entries only, so 'below min' there is a lower bound on nothing - reported, read with care).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe010_per_line as X
S = {**X.build_sets(), **X.exposed_sets()}; out = {}
for name, tabs in S.items():
    rel = []; pos = {"below_min": 0, "min_to_max": 0, "above_max": 0}
    for t in tabs:
        vs = X.vals(t); v = X.cv(t["total"])
        if None in vs or v is None: continue
        if t["complete"]: rel.append(round(len(vs) * v / sum(vs), 3))
        pos["below_min" if v < min(vs) else "above_max" if v > max(vs) else "min_to_max"] += 1
    rel.sort()
    out[name] = {"tablets": len(tabs), "n_total_over_sum_sorted": rel,
                 "median_n_total_over_sum": rel[len(rel) // 2] if rel else None, "position_vs_entries": pos}
json.dump(out, open("analysis/pe010_posthoc.json", "w"), indent=1)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "n_total_over_sum_sorted"} for k, v in out.items()}, indent=1))
