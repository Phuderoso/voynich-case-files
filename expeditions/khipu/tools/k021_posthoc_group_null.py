#!/usr/bin/env python3
"""K021 post-hoc (disclosed, NOT pre-registered): is H2 (sum cords share a colour) explained by sum cords sitting in the
same cord groups? Stricter null: sum cords are redrawn only within their own cord group (CLUSTER_ID), keeping the number
per group. Primary population only. Exploratory; it can weaken but not upgrade the pre-registered verdict."""
import sqlite3, json, numpy as np
from collections import defaultdict
exec(open('tools/k021_sum_cord_colour.py').read().split('units = []')[0])  # same loading/definitions
rng = np.random.default_rng(20261106); R = 20000
clu = {cid: cl for cid, cl in c.execute("select CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1")}
T2o = 0; N = np.zeros(R, np.int64); rows = []
for khid, cids in kh.items():
    if names[khid][0] not in sigk: continue
    V = np.array([val.get(x, 0) for x in cids], np.int64); h = hits(V); C = [col.get(x) for x in cids]
    elig = [i for i in range(len(cids)) if V[i] >= 10 and C[i] is not None]
    lab = {x: k for k, x in enumerate(sorted({C[i] for i in elig}))}; K = len(lab)
    byg = defaultdict(list)
    for i in elig: byg[clu[cids[i]]].append(i)
    oh_obs = np.zeros(K, np.int64); oh = np.zeros((R, K), np.int64)
    for g, idx in byg.items():
        m = sum(h[i] for i in idx)
        for i in idx:
            if h[i]: oh_obs[lab[C[i]]] += 1
        if m == 0: continue
        cl = np.array([lab[C[i]] for i in idx]); pick = np.argsort(rng.random((R, len(idx))), 1)[:, :m]
        for j in range(m): np.add.at(oh, (np.arange(R), cl[pick[:, j]]), 1)
    o = int((oh_obs * (oh_obs - 1) // 2).sum()); n = (oh * (oh - 1) // 2).sum(1)
    T2o += o; N += n; rows.append(dict(okr=names[khid][0], T2=o, null_mean=float(n.mean()), p=float((1 + (n >= o).sum()) / (1 + R))))
res = dict(T2=T2o, null_mean=float(N.mean()), p=float((1 + (N >= T2o).sum()) / (1 + R)), per_khipu=rows)
json.dump(res, open('analysis/k021_posthoc_group_null.json', 'w'), indent=1); print(json.dumps(res, indent=1))
