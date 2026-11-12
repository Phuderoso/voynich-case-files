#!/usr/bin/env python3
"""K072 post hoc (disclosed, not pre-registered): split the KFG holdout rows of analysis/k072_results.json by whether the
khipu's pendant values AND groups are identical on OKR and KFG (unchanged), changed, or KFG-only. Descriptive sums of
observed G/G_s/G_ns and per-khipu null means from the registered run; no new random draw, no verdict."""
import json, sqlite3, re, sys, runpy, io, contextlib
d = json.load(open('analysis/k072_results.json')); rows = d['rows']
# reuse the registered tool's loaders in smoke-free mode would re-run nulls; instead rebuild the two group maps here
OKR = 'data/khipu.db'; c = sqlite3.connect(OKR)
dups = {r[0] for r in c.execute('select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1')}
nm = {r[0]: r[1] for r in c.execute('select KHIPU_ID, OKR_NUM from khipu_main')}
from collections import defaultdict
val = defaultdict(int)
for cid, v in c.execute('select CORD_ID, knot_value_type from knot'):
    if v is not None: val[cid] += int(v)
ok = defaultdict(list)
for kid, cid, cl in c.execute('select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL'):
    if kid not in dups and nm.get(kid): ok[nm[kid]].append((val.get(cid, 0), cl))
def sizes(cl):
    out, last = [], object()
    for x in cl:
        if x != last: out.append(1); last = x
        else: out[-1] += 1
    return out
src = open('tools/k071_kfg_k025_replication.py').read().split('# ---------- K025 machinery')[0]
src = src.replace("k069 = json.load(open('analysis/k069_results.json'))['summary']; K069_NAMES = set(k069['okr_k001_bh']) | set(k069['new_kfg_bh_names'])", '')
g = {}
with contextlib.redirect_stdout(io.StringIO()): exec(src, g)
pend, groups = g['pend'], g['groups']
cls = defaultdict(lambda: dict(n=0, G=0, G_s=0, G_ns=0, null_mean=0.0, names=[]))
for r in rows:
    k = r['khipu']
    if not r['in_okr']: lab = 'kfg_only'
    else:
        o = ok.get(k, []); kv = [x for _, x in pend[k]]; ks = [b - a for a, b in groups[k]]
        lab = 'unchanged' if [x for x, _ in o] == kv and sizes([y for _, y in o]) == ks else 'changed'
    cc = cls[lab]; cc['n'] += 1; cc['G'] += r['G']; cc['G_s'] += r['G_s']; cc['G_ns'] += r['G_ns']; cc['null_mean'] += r['null_mean']
    if r['bh']: cc['names'].append(k)
out = {k: dict(v, null_mean=round(v['null_mean'], 3)) for k, v in cls.items()}
json.dump(out, open('analysis/k072_posthoc.json', 'w'), indent=1); print(json.dumps(out, indent=1))
