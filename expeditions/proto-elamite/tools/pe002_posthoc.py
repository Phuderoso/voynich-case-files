#!/usr/bin/env python3
"""PE002 post-hoc diagnostics (run AFTER stage 2; no decision weight).
D1  Off-by-one-unit control for each test: does the exact value match more often than the same line shifted by
    +/- one unit of its own smallest sign? Real data and 999 stratified shuffles (seed 205).
D2  Why S/D/B-run failed FPR: FPR at f=0 (200 reps, R=999, seed 206) with (a) the preregistered rank strata,
    (b) tie-aware strata (equal values always share a stratum), (c) no strata.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe002_multiline as Q
import pe001_totals as P

def tie_strata(vals):
    v = np.array([float(x) for x in vals]); u = np.unique(v)
    # value classes assigned to quintiles by cumulative count; equal values never split
    order = np.searchsorted(u, v); cnt = np.bincount(order); cum = np.cumsum(cnt) - cnt
    cls = (cum * Q.N_STRATA) // len(v)
    return cls[order]

def shifted(tabs, X, m):
    """Per position: the line's value shifted by +/- the value of the smallest sign in its own notation."""
    tb = Q.SYS[X]; out = []
    for t in tabs:
        vals = [P.value(e, tb) for e in t["entries"]]
        if sum(v is not None for v in vals) < 2: continue
        if m == "subset" and sum(v is not None for v in vals) > Q.SUBSET_CAP: continue
        for r in t["rev"]:
            v = P.value(r, tb)
            if v is None or v <= 0: continue
            u = min(tb[s] for s in r); out.append((v - u, v + u))
    return out

def main():
    tabs = Q.load(); res = {"D1_offbyone": {}, "D2_fpr": {}}
    rng = np.random.default_rng(205)
    for X, m in Q.tests(tabs):
        d = Q.build(tabs, X, m); sh = shifted(tabs, X, m); n = len(d["vals"])
        exact = sum(int(d["vals"][i] in d["reaches"][d["pos_tab"][i]]) for i in range(n))
        off = sum(int(a in d["reaches"][d["pos_tab"][i]]) + int(b in d["reaches"][d["pos_tab"][i]]) for i, (a, b) in enumerate(sh)) / 2
        # same contrast under stratified shuffles of the line values (exact - mean off-by-one)
        st = Q.strata(d["vals"]); groups = [np.where(st == s)[0] for s in np.unique(st)]
        diffs = []
        for _ in range(999):
            perm = np.arange(n)
            for g in groups: perm[g] = g[rng.permutation(len(g))]
            e2 = sum(int(d["vals"][perm[i]] in d["reaches"][d["pos_tab"][i]]) for i in range(n))
            o2 = sum(int(sh[perm[i]][0] in d["reaches"][d["pos_tab"][i]]) + int(sh[perm[i]][1] in d["reaches"][d["pos_tab"][i]]) for i in range(n)) / 2
            diffs.append(e2 - o2)
        diffs = np.array(diffs)
        res["D1_offbyone"][f"{X}-{m}"] = {"exact": exact, "offbyone_mean": off, "contrast": exact - off,
            "null_contrast_mean": float(diffs.mean()), "p_contrast": (1 + int((diffs >= exact - off).sum())) / 1000}
        print("D1", X, m, res["D1_offbyone"][f"{X}-{m}"], flush=True)
    rng = np.random.default_rng(206)
    for X in ("S", "D", "B", "C"):
        d = Q.build(tabs, X, "run"); row = {}
        for name, sfun, strat in (("rank_strata", Q.strata, True), ("tie_aware_strata", tie_strata, True), ("no_strata", Q.strata, False)):
            h = 0
            for _ in range(200):
                v = Q.plant(d, 0.0, rng, "run"); H = Q.hitmatrix(d, v)
                _, p, _ = Q.ptest(H, sfun(v), 999, rng, stratified=strat); h += p <= 0.05
            row[name] = h / 200
        res["D2_fpr"][f"{X}-run"] = row; print("D2", X, row, flush=True)
    json.dump(res, open("analysis/pe002_posthoc.json", "w"), indent=1)

if __name__ == "__main__":
    main()
