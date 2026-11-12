#!/usr/bin/env python3
"""K071 post hoc (disclosed, not pre-registered): for each KFG BH khipu that is also in the OKR, recompute K025's G on
OKR data and say whether the difference comes from pendant values, group boundaries, or both (swap one at a time)."""
import sqlite3, json, re, numpy as np, importlib.util, sys
from collections import defaultdict
sys.argv = ['x', 'data/khipu.db', '/tmp/k071_dummy.json']
r = json.load(open('analysis/k071_results.json')); bhs = [x for x in r['summary']['bh_khipus']]
c = sqlite3.connect('data/khipu.db')
dups = {a[0] for a in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
name = {a[0]: a[1] for a in c.execute("select KHIPU_ID, OKR_NUM from khipu_main")}; byname = {v: k for k, v in name.items()}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
kh = defaultdict(list)
for khid, cid, cl in c.execute("select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    kh[khid].append((val.get(cid, 0), cl))
src = open('tools/k071_kfg_k025_replication.py').read().split('# ---------- K025 machinery')[0]
ns = {}; exec(compile(src, 'k071', 'exec'), ns)
exec(compile(open('tools/k071_kfg_k025_replication.py').read().split('spans) ----------')[1].split('res = dict(')[0], 'm', 'exec'), ns)
def okr_groups(cl):
    g = []; last = object()
    for i, x in enumerate(cl):
        if x != last: g.append([i, i + 1]); last = x
        else: g[-1][1] = i + 1
    return [tuple(a) for a in g]
out = []
for nm in bhs:
    k = byname.get(nm); vk = np.array([x for _, x in ns['pend'][nm]], np.int64); gk = ns['groups'][nm]
    row = dict(khipu=nm, in_okr=k is not None, G_kfg=int(ns['G'](vk[None], ns['prep'](gk, len(vk)))[0]))
    if k is not None:
        vo = np.array([x[0] for x in kh[k]], np.int64); go = okr_groups([x[1] for x in kh[k]])
        row.update(okr_duplicate_flag=k in dups, n_pend_okr=len(vo), n_pend_kfg=len(vk), G_okr=int(ns['G'](vo[None], ns['prep'](go, len(vo)))[0]),
                   same_values=bool(len(vo) == len(vk) and (vo == vk).all()), same_groups=go == gk)
        if len(vo) == len(vk):
            row['G_kfgvalues_okrgroups'] = int(ns['G'](vk[None], ns['prep'](go, len(vk)))[0])
            row['G_okrvalues_kfggroups'] = int(ns['G'](vo[None], ns['prep'](gk, len(vo)))[0])
            row['n_values_changed'] = int((vo != vk).sum())
    out.append(row); print(row)
json.dump(out, open('analysis/k071_posthoc.json', 'w'), indent=1)
