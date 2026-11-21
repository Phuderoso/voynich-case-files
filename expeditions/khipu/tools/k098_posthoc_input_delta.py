#!/usr/bin/env python3
"""K098 post hoc (descriptive, after the verdict labels were fixed): OKR vs KFG pendant values for the five names whose label changed. Usage from expeditions/khipu."""
import sqlite3, json, re, numpy as np
from collections import defaultdict
o = sqlite3.connect('/workspace/khipu/khipu.db')
ids = {r[1]: r[0] for r in o.execute("select KHIPU_ID, OKR_NUM from khipu_main where DUPLICATE_FLAG is not 1")}
val = defaultdict(int)
for cid, v in o.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
k = sqlite3.connect('/workspace/kfg/kfg_20261111.db'); PEN = re.compile(r'^p(\d+)$')
out = {}
for n in ('KH0027', 'KH0068', 'KH0513', 'KH0168', 'KH0491'):
    ov = [val.get(c, 0) for (c,) in o.execute("select CORD_ID from cord where CORD_LEVEL=1 and KHIPU_ID=? order by CORD_ORDINAL", (ids[n],))]
    kv = []
    for nm, v in k.execute("select cord_name, value from cord where khipu=? order by idx", (n,)):
        if PEN.match(str(nm or '')):
            try: kv.append(int(float(v)) if v not in (None, '') else 0)
            except Exception: kv.append(0)
    diff = [(i, a, b) for i, (a, b) in enumerate(zip(ov, kv)) if a != b]
    out[n] = dict(n_okr=len(ov), n_kfg=len(kv), n_diff_positions=len(diff), first_diffs=diff[:12], same=ov == kv)
print(json.dumps(out, indent=1))
json.dump(out, open('analysis/k098_posthoc_input_delta.json', 'w'), indent=1)
