#!/usr/bin/env python3
"""PE007 post hoc (after gates and test; no decision weight). Deterministic (seed 702 re-used for P2).
P1 where the errors are: unique-but-wrong entry outputs on balancing vs non-balancing tablets, sets A and B.
P2 why the power gate fails: in the planted-balance runs, pass rates of G2 alone and of G3 alone (entry target).
P3 B entry precision restricted to balancing tablets (upper bound, as PE004 P2).
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe007_noncap as S, pe004_restore as Q, pe001_totals as P
res = json.load(open("analysis/pe007_results.json")); sets = S.sets(); out = {}
for k, cal in sets.items():
    bal = {t["pid"]: bool(P.balances(t["entries"], t["total"])) for t in cal}
    rows = [r for r in res["sets"][k]["rows"] if r["kind"] == "entry"]
    wrong = [r for r in rows if r["unique"] and not r["unique_correct"]]
    ub = [r for r in rows if r["unique"] and bal[r["pid"]]]
    out["P1_P3_" + k] = {"tablets_balancing": sum(bal.values()), "tablets": len(cal),
        "wrong_unique_on_balancing": sum(bal[r["pid"]] for r in wrong), "wrong_unique_on_nonbalancing": sum(not bal[r["pid"]] for r in wrong),
        "precision_on_balancing": (sum(r["unique_correct"] for r in ub) / len(ub)) if ub else None, "unique_on_balancing": len(ub)}
    rng = np.random.default_rng(S.SEED_POW); g2 = g3 = 0
    for _ in range(S.R_POW):
        pc = S.force_balance(cal, rng); rr = Q.score(pc, with_base=True)
        n, u, uc, R = S.stats(rr, "entry"); g2 += S.g2(n, u, uc); g3 += S.mcnemar(R)[2] <= S.ALPHA
        S.stats(rr, "total")
    out["P2_" + k] = {"planted_G2_pass": g2 / S.R_POW, "planted_G3_pass": g3 / S.R_POW}
json.dump(out, open("analysis/pe007_posthoc.json", "w"), indent=1); print(json.dumps(out, indent=1))
