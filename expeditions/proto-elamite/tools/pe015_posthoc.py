#!/usr/bin/env python3
"""PE015 post hoc (after the decision, descriptive, no weight): fine key x SYSTEM / SIZE tables for the H1G and H2W sets."""
import json, os, sys
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe015_finekey as F
rows, _ = F.build(); out = {}
for t in ("H1G", "H2W"):
    keys, labs, _, _, co = F.make(rows, t); tab = defaultdict(Counter)
    for k, l in zip(keys, labs): tab[k][str(l)] += 1
    out[t + "_table"] = {k: dict(sorted(v.items())) for k, v in sorted(tab.items(), key=lambda kv: -sum(kv[1].values()))}
json.dump(out, open("analysis/pe015_posthoc.json", "w"), indent=1); print(json.dumps(out, indent=1))
