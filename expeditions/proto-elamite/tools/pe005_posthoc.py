#!/usr/bin/env python3
"""PE005 post-hoc diagnostics (run AFTER the gates and the test; no decision weight; deterministic).
H1  Overlap of CAP and MULTI (capacity sub-unit signs force system C, so CAP implies not MULTI): 2x2x2 table.
H2  For CAP tablets: does the account balance in the N01-and-above units of system C once all sub-unit signs
    (N39B, N24, N30C, N30D, N39C) are dropped from entries and total?  (Does the mismatch live in the sub-units?)
H3  Same split as the test, but by edition (primary publication), to see whether the even half differs by volume.
"""
import json, os, sys, csv, re
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe005_balance as B, pe001_totals as P, pe004_restore as Q

cal, rows, nocover = B.load(); out = {}
tab = Counter()
for r in rows: tab[(r["f"]["CAP"], r["f"]["MULTI"], B.label(r))] += 1
out["H1_cap_multi_balance"] = {f"CAP={a},MULTI={b},balances={c}": n for (a, b, c), n in sorted(tab.items())}
C = P.c_table(); h2 = Counter()
for r in rows:
    if not r["f"]["CAP"]: continue
    strip = lambda c: Counter({s: k for s, k in c.items() if s not in P.C_SUB_SIGNS})
    e = [strip(x) for x in r["t"]["entries"]]; t = strip(r["t"]["total"])
    big = sum(P.value(x, C) for x in e) == P.value(t, C)
    h2[(B.label(r), big)] += 1
out["H2_cap_tablets_balance_vs_integer_part_balance"] = {f"balances={a},integer_part_balances={b}": n for (a, b), n in sorted(h2.items())}
csv.field_size_limit(10**9); pub = {}
for row in csv.DictReader(open(os.path.join("data", "cdli_cat.csv"), encoding="utf-8", errors="replace")):
    if row["id_text"].strip().isdigit(): pub["P%06d" % int(row["id_text"])] = re.sub(r",.*", "", row["primary_publication"])
h3 = Counter()
for r in rows: h3[(pub.get(r["pid"]), "odd" if B.odd(r["pid"]) else "even", r["f"]["CAP"], B.label(r))] += 1
out["H3_edition_parity_cap_balance"] = {f"{a}|{b}|CAP={c}|bal={d}": n for (a, b, c, d), n in sorted(h3.items())}
json.dump(out, open("analysis/pe005_posthoc.json", "w"), indent=1); print(json.dumps(out, indent=1))
