#!/usr/bin/env python3
"""K024 - deeper-level subsidiary sums (parent at level >=2 = sum of its children). Pre-registered in case-file/K024
(commit 99e115c4). Null N_a: permute child values among cords of the same level within the khipu.
Control nulls use K = 1000 replicates per control corpus (the primary test uses 10 000)."""
import sqlite3, json, time, numpy as np
from collections import defaultdict
t0 = time.time(); c = sqlite3.connect('../khipu.db'); rng = np.random.default_rng(20261109)
KC = 10000; KCTL = 1000; NCTL = 200
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
lev = {}; kof = {}; bylev = defaultdict(lambda: defaultdict(list))
for khid, cid, L, par in c.execute("select KHIPU_ID, CORD_ID, CORD_LEVEL, PENDANT_FROM from cord order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups: continue
    lev[cid] = L; kof[cid] = khid
    if L is not None and L >= 3: bylev[khid][L].append((cid, par))
units = []  # (khid, level, child values, M, parent values)
for khid, levs in bylev.items():
    for L, ch in levs.items():
        sv = np.array([val.get(x, 0) for x, _ in ch], np.int64); pars = [p for _, p in ch]
        cnt = defaultdict(int)
        for p in pars: cnt[p] += 1
        elig = sorted(p for p in cnt if cnt[p] >= 2 and lev.get(p) == L - 1 and kof.get(p) == khid and val.get(p, 0) >= 10)
        if not elig: continue
        pi = {p: j for j, p in enumerate(elig)}; M = np.zeros((len(sv), len(elig)), np.int64)
        for i, p in enumerate(pars):
            if p in pi: M[i, pi[p]] = 1
        units.append(dict(khid=khid, okr=names[khid][0], inv=names[khid][1], L=L, sv=sv, M=M, pv=np.array([val[p] for p in elig], np.int64)))
def H(S, M, P):
    return (((S @ M) == P) & (((S > 0).astype(np.int64) @ M) >= 2)).sum(-1)
def perm(sv, B): return np.argsort(rng.random((B, len(sv))), 1).choose(sv) if False else sv[np.argsort(rng.random((B, len(sv))), 1)]
def corpus_test(us, K, svs=None, pvs=None):
    svs = svs or [u['sv'] for u in us]; pvs = pvs or [u['pv'] for u in us]
    obs = sum(int(H(s[None], u['M'], p)[0]) for u, s, p in zip(us, svs, pvs)); nl = np.zeros(K, np.int64)
    for u, s, p in zip(us, svs, pvs): nl += H(perm(s, K), u['M'], p)
    return obs, nl, float((1 + (nl >= obs).sum()) / (1 + K))
res = dict(n_units=len(units), n_khipus=len({u['khid'] for u in units}), n_eligible=int(sum(len(u['pv']) for u in units)),
           eligible_by_level={int(L): int(sum(len(u['pv']) for u in units if u['L'] == L)) for L in sorted({u['L'] for u in units})})
o, nl, p = corpus_test(units, KC); res['primary'] = dict(H=o, null_mean=float(nl.mean()), null_max=int(nl.max()), p=p)
nou = [u for u in units if u['okr'] != 'KH0349']
o2, nl2, p2 = corpus_test(nou, KC); res['without_KH0349'] = dict(H=o2, null_mean=float(nl2.mean()), null_max=int(nl2.max()), p=p2)
print(json.dumps(res, indent=1), round(time.time() - t0, 1), flush=True)
# controls
fp = pw = 0
allp = [(ui, j) for ui, u in enumerate(units) for j in range(len(u['pv']))]
for t in range(NCTL):
    svs = [perm(u['sv'], 1)[0] for u in units]
    fp += corpus_test(units, KCTL, svs=svs)[2] <= 0.01
    svs = [s.copy() for s in svs]; pvs = [u['pv'].copy() for u in units]
    for k in rng.choice(len(allp), 3, replace=False):
        ui, j = allp[k]; ix = np.where(units[ui]['M'][:, j] == 1)[0]; s = svs[ui]
        if (s[ix] > 0).sum() < 2: s[ix[:2]] = np.maximum(s[ix[:2]], rng.integers(1, 30, 2))
        if s[ix].sum() < 10: s[ix[0]] += 10 - s[ix].sum()
        pvs[ui][j] = s[ix].sum()
    pw += corpus_test(units, KCTL, svs=svs, pvs=pvs)[2] <= 0.01
res['controls'] = dict(calib_fpr_01=fp / NCTL, power_3planted=pw / NCTL, K_control=KCTL)
res['verdict'] = ('controls failed' if fp / NCTL > 0.03 else 'evidence' if p <= 0.01 else
                  'not supported' if pw / NCTL >= 0.5 else 'not testable')
hits = []
for u in units:
    h = ((u['sv'] @ u['M']) == u['pv']) & (((u['sv'] > 0).astype(np.int64) @ u['M']) >= 2)
    if h.any(): hits.append(dict(okr=u['okr'], inv=u['inv'], level=u['L'] - 1, n_hits=int(h.sum()), n_elig=len(u['pv'])))
res['hits_by_khipu'] = hits; res['runtime_s'] = round(time.time() - t0, 1)
json.dump(res, open('analysis/k024_results.json', 'w'), indent=1); print(json.dumps({k: res[k] for k in ('controls', 'verdict', 'hits_by_khipu', 'runtime_s')}, indent=1))
