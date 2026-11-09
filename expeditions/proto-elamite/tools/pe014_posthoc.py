#!/usr/bin/env python3
"""PE014 post hoc (descriptive, no decision weight; written AFTER the registered run of tools/pe014_ratio.py test).
Full set with the Born-named tablets put back; which RSET ratios hit; tablets with the most hits; H2W excess by tablet size.
Usage (from expeditions/proto-elamite/): python3 tools/pe014_posthoc.py"""
import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe014_ratio as X, pe004_restore as Q

def ratios(a, b):
    va, vb = X.values(a), X.values(b)
    return sorted({x / y for x in va.values() for y in vb.values() if y and x / y in X.RSET})

tabs = Q.parse(os.path.join("data", "pe.atf"))
s, p, _ = X.build("H2", tabs); grp = X.adjacent_pairs.grp[:]
rc, tc = Counter(), Counter()
for i, j in p:
    r = ratios(s[i], s[j])
    if r: tc[grp[i]] += 1
    for x in r: rc[str(x)] += 1
size = Counter(grp)
hits_by = Counter(); pairs_by = Counter()
for i, j in p:
    b = "2" if size[grp[i]] == 2 else "3-5" if size[grp[i]] <= 5 else "6+"
    pairs_by[b] += 1; hits_by[b] += X.hit(s[i], s[j])
sf, pf, _ = X.build("H2", tabs, exclude=set())
out = {"note": "descriptive, after the decision; no weight",
       "H2_T": X.T(s, p), "full_set_incl_Born": {"pairs": len(pf), "T": X.T(sf, pf)},
       "ratio_counts_among_hits (a pair can show several)": dict(rc.most_common()),
       "tablets_with_most_hit_pairs": dict(tc.most_common(8)),
       "hits_by_tablet_informative_entries": {b: [hits_by[b], pairs_by[b]] for b in ("2", "3-5", "6+")}}
json.dump(out, open("analysis/pe014_posthoc.json", "w"), indent=1); print(json.dumps(out, indent=1))
