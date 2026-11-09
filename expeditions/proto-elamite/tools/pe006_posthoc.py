#!/usr/bin/env python3
"""PE006 post hoc (after gates and test; no decision weight). Deterministic.
P1 list length: CAP vs balance within strata of obverse entry count (<= 6 / > 6), fresh set, one-sided Fisher each.
P2 direction of mismatch: among non-balancing fresh tablets, total < sum vs total > sum in the reading system
   (C for CAP tablets; for non-CAP, every admitted system must agree, else 'mixed').
P3 sub-units: CAP non-balancing fresh tablets that balance when every sub-unit sign is dropped (N01 and above only).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe006_cap as T, pe005_balance as F, pe001_totals as P, pe004_restore as Q
from collections import Counter
rows, _, _ = T.load(); y = [T.label(r) for r in rows]; out = {}
for name, cond in (("entries<=6", lambda r: len(r["t"]["entries"]) <= 6), ("entries>6", lambda r: len(r["t"]["entries"]) > 6)):
    idx = [i for i, r in enumerate(rows) if cond(r)]
    out["P1_" + name] = T.table([rows[i]["cap"] for i in idx], [y[i] for i in idx]) | {"n": len(idx)}
def direction(r):
    ds = set()
    for X, tb in Q.SYS.items():
        vs = [P.value(e, tb) for e in r["t"]["entries"]]; vt = P.value(r["t"]["total"], tb)
        if vt is None or any(v is None for v in vs): continue
        ds.add("total<sum" if vt < sum(vs) else "total>sum")
    return ds.pop() if len(ds) == 1 else "mixed"
out["P2_mismatch_direction"] = {g: dict(Counter(direction(r) for r, yi in zip(rows, y) if not yi and r["cap"] == g)) for g in (True, False)}
out["P2_mismatch_direction"] = {("CAP" if k else "nonCAP"): v for k, v in out["P2_mismatch_direction"].items()}
fix = 0; tot = 0
for r, yi in zip(rows, y):
    if yi or not r["cap"]: continue
    tot += 1; strip = lambda c: {s: k for s, k in c.items() if s not in P.C_SUB_SIGNS}
    e = [strip(x) for x in r["t"]["entries"]]; t = strip(r["t"]["total"])
    e = [x for x in e if x]
    if t and e and P.balances(e, t): fix += 1
out["P3_CAP_nonbalancing_fixed_by_dropping_subunits"] = {"fixed": fix, "of": tot}
json.dump(out, open("analysis/pe006_posthoc.json", "w"), indent=1); print(json.dumps(out, indent=1))
