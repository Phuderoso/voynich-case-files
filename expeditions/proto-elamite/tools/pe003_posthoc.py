#!/usr/bin/env python3
"""PE003 post-hoc diagnostics (run AFTER stage 2; no decision weight). Seed 305, R = 9 999.
P1  Split by tablet type: the contrast K and its tie-aware stratified-shuffle p on single-total tablets only and on
    multi-line tablets only (the null shuffles within the subgroup).
P2  Subset tests without the full sum: lines equal to their tablet's full (valid-entry) sum are dropped, then K and p
    on the rest (does anything beyond 'the total of everything' survive?).
P3  Overlap: how many distinct tablets carry the exact hits across the testable tests.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe003_contrast as Q

def sub(d, keep):
    idx = np.where(keep)[0]; return {**d, "pos_tab": d["pos_tab"][idx], "vals": d["vals"][idx], "single": d["single"][idx]}

def kp(d, rng):
    if len(d["vals"]) < 5: return {"n": int(len(d["vals"]))}
    K = Q.kmatrix(d, d["vals"]); obs, p, null = Q.ptest(K, Q.tie_strata(d["vals"]), Q.R_TEST, rng)
    return {"n": int(len(d["vals"])), "K_half": obs / 2, "null_mean_half": float(null.mean()) / 2, "p": p}

def main():
    tabs = Q.load(); rng = np.random.default_rng(305); res = {"P1_split": {}, "P2_subset_without_full_sum": {}, "P3_tablets": {}}
    for X, m in [("C", "full")] + [(X, "subset") for X in Q.SYSTEMS]:
        d = Q.build(tabs, X, m); key = f"{X}-{m}"
        res["P1_split"][key] = {"single_total": kp(sub(d, d["single"]), rng), "multi_line": kp(sub(d, ~d["single"]), rng)}
        hits = {d["pids"][d["pos_tab"][i]] for i in range(len(d["vals"])) if d["vals"][i] in d["reaches"][d["pos_tab"][i]]}
        res["P3_tablets"][key] = sorted(hits)
        if m == "subset":
            fs = np.array([d["vals"][i] == sum(d["ents"][d["pos_tab"][i]]) for i in range(len(d["vals"]))])
            r = kp(sub(d, ~fs), rng); r["dropped_full_sum_lines"] = int(fs.sum()); res["P2_subset_without_full_sum"][key] = r
        print(key, res["P1_split"][key], res["P2_subset_without_full_sum"].get(key), flush=True)
    allhits = set().union(*res["P3_tablets"].values()); res["P3_distinct_tablets_with_exact_hit"] = len(allhits)
    json.dump(res, open("analysis/pe003_posthoc.json", "w"), indent=1); print("distinct", len(allhits))

if __name__ == "__main__":
    main()
