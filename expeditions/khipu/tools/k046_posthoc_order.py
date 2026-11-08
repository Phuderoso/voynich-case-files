#!/usr/bin/env python3
"""K046 post-hoc (written AFTER the K046 run; descriptive only, NOT a verdict, no Bonferroni claim).
Two looks prompted by the results, both disclosed as post hoc in the case file:
  1. order-free sensitivity: components compared as a sorted multiset (operators still identical,
     PK never matches); same N1 null, R = 10 000, seed 4651.
  2. code cross-tab: colour of side A vs colour of side B on the aligned units (counts only, no test),
     to see whether recorders used a consistent *different* code for the same slot.
Usage (from expeditions/khipu/): python3 tools/k046_posthoc_order.py -> analysis/k046_posthoc_order.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04."""
import json, os, sqlite3, sys
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import k046_colour_agreement as k

def m_sorted(a, b):
    if "PK" in a[0] or "PK" in b[0] or tuple(a[1]) != tuple(b[1]): return False
    return sorted(a[0]) == sorted(b[0])

def s(c): return "".join(x for t in zip(c[0], c[1] + ("",)) for x in t)

c = sqlite3.connect(f"file:{os.path.realpath(k.DB_CANDIDATES[0])}?mode=ro", uri=True)
S = k.load(c); rng = np.random.default_rng(4651); out = {"note": "post hoc, descriptive only; not a K046 verdict", "seed": 4651, "R": 10000, "pairs": {}}
for a, b in k.PAIRS:
    pr, Vs, units, leaders = k.build_units(S, a, b); us, _ = k.colour_units(S, units); n = len(us)
    M = np.array([[m_sorted(us[i]["colA"], us[j]["colB"]) for j in range(n)] for i in range(n)], dtype=np.int8)
    obs = int(np.trace(M)); bank = k.null_bank(M, 10000, rng)
    xt = Counter((s(u["colA"]), s(u["colB"])) for u in us)
    lead, _ = k.colour_units(S, leaders)
    out["pairs"][f"{a}/{b}"] = dict(n=n, A_order_free=obs, null_mean=float(bank.mean()), p=k.pval(obs, bank),
        crosstab=[dict(A=x, B=y, count=v) for (x, y), v in xt.most_common()],
        leaders_crosstab=[dict(A=x, B=y, count=v) for (x, y), v in Counter((s(u["colA"]), s(u["colB"])) for u in lead).most_common()])
    print(a, b, n, obs, round(float(bank.mean()), 3), out["pairs"][f"{a}/{b}"]["p"], xt.most_common(8))
json.dump(out, open(os.path.join(k.AN, "k046_posthoc_order.json"), "w"), indent=1)
