#!/usr/bin/env python3
"""PE004 post-hoc diagnostics (run AFTER the calibration gates; no decision weight; deterministic).
P1  Error decomposition of unique-but-wrong outputs: does the tablet balance in some system (sum == total)?
    If it balances, the error is system ambiguity or a non-canonical notation; if not, the tablet breaks the rule.
P2  Precision and recovery restricted to tablets that balance (an upper bound: on a damaged tablet balance cannot be
    checked, because the missing slot absorbs any difference).
P3  Why the frequency baseline is strong: share of entry tasks whose notation repeats on the same tablet.
"""
import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe004_restore as Q
import pe001_totals as P

cal = Q.calibration_set(Q.parse(os.path.join("data", "pe.atf")))
bal = {t["pid"]: P.balances(t["entries"], t["total"]) for t in cal}
rows = Q.score(cal, with_base=True); out = {"balancing_tablets": sum(bool(v) for v in bal.values()), "tablets": len(cal)}
for kind in ("entry", "total"):
    R = [r for r in rows if r["kind"] == kind]; W = [r for r in R if r["unique"] and not r["covered"]]
    Wb = [r for r in W if bal[r["pid"]]]
    canon_mismatch = 0
    for r in Wb:
        t = next(t for t in cal if t["pid"] == r["pid"])
        tru = t["total"] if kind == "total" else t["entries"][r["slot"]]
        canon_mismatch += any(Q.key(P.canonical(P.value(tru, Q.SYS[X]), Q.SYS[X]) or Counter()) != Q.key(tru) for X in bal[r["pid"]] if P.value(tru, Q.SYS[X]))
    Rb = [r for r in R if bal[r["pid"]]]; ub = sum(r["unique"] for r in Rb); ucb = sum(r["unique_correct"] for r in Rb)
    out[kind] = {"unique_wrong": len(W), "unique_wrong_on_balancing_tablets": len(Wb),
                 "of_which_true_notation_non_canonical": canon_mismatch,
                 "unique_wrong_on_non_balancing_tablets": len(W) - len(Wb),
                 "balancing_only": {"tasks": len(Rb), "unique": ub, "unique_correct": ucb,
                                    "precision": ucb / ub if ub else None, "cp95_low": Q.cp_low(ucb, ub) if ub else 0.0,
                                    "recovery": ucb / len(Rb) if Rb else None,
                                    "ambiguous": sum(r["n_cand"] > 1 for r in Rb)}}
E = [r for r in rows if r["kind"] == "entry"]
out["P3_entry_repeats_on_tablet"] = sum(next(t for t in cal if t["pid"] == r["pid"])["entries"].count(next(t for t in cal if t["pid"] == r["pid"])["entries"][r["slot"]]) > 1 for r in E) / len(E)
json.dump(out, open("analysis/pe004_posthoc.json", "w"), indent=1); print(json.dumps(out, indent=1))
