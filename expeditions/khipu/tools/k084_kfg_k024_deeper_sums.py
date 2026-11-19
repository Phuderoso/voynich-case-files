#!/usr/bin/env python3
"""K084 - KFG re-audit of K024 (deeper parent = sum of its own children). Pre-registered in
case-file/K084-kfg-replication-k024.md (commit d2caa59). Usage: python3 tools/k084_kfg_k024_deeper_sums.py data/khipu.db
Seed 6463 (next free 6464)."""
import sqlite3, json, sys, re, glob, hashlib, time, numpy as np
from collections import defaultdict
T0 = time.time(); KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
OKR_DB = sys.argv[1] if len(sys.argv) > 1 else 'data/khipu.db'; OUT = 'analysis/k084_results.json'
rng = np.random.default_rng(6463); KC = 10000; KCTL = 1000; NCTL = 200

def build(levels, val, parent):
    """levels: khid -> depth -> [(cid, parent_cid)]; returns K024 units."""
    units = []
    for kh, levs in levels.items():
        for L, ch in levs.items():
            if L < 3: continue
            sv = np.array([val.get(x, 0) for x, _ in ch], np.int64); pars = [p for _, p in ch]
            cnt = defaultdict(int)
            for p in pars: cnt[p] += 1
            elig = sorted((p for p in cnt if p is not None and cnt[p] >= 2 and val.get(p, 0) >= 10 and parent.get(p, (None, None))[1] == L - 1
                           and parent.get(p, (None, None))[0] == kh), key=str)
            if not elig: continue
            pi = {p: j for j, p in enumerate(elig)}; M = np.zeros((len(sv), len(elig)), np.int64)
            for i, p in enumerate(pars):
                if p in pi: M[i, pi[p]] = 1
            units.append(dict(kh=kh, L=L, sv=sv, M=M, pv=np.array([val[p] for p in elig], np.int64), names=elig))
    return units

# A0: OKR anchor (K024 loader verbatim)
c = sqlite3.connect(OKR_DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
okrname = {r[0]: r[1] for r in c.execute("select KHIPU_ID, OKR_NUM from khipu_main")}
okr_set = {v for v in okrname.values() if v}
v0 = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: v0[cid] += int(v)
lv0 = defaultdict(lambda: defaultdict(list)); par0 = {}
for kh, cid, L, par in c.execute("select KHIPU_ID, CORD_ID, CORD_LEVEL, PENDANT_FROM from cord order by KHIPU_ID, CORD_ORDINAL"):
    if kh in dups: continue
    par0[cid] = (kh, L)
    if L is not None and L >= 3: lv0[kh][L].append((cid, par))
U0 = build(lv0, v0, par0)
def H(S, M, P): return (((S @ M) == P) & (((S > 0).astype(np.int64) @ M) >= 2)).sum(-1)
A0 = dict(n_eligible=int(sum(len(u['pv']) for u in U0)), hits=int(sum(H(u['sv'][None], u['M'], u['pv'])[0] for u in U0)))
A0['pass'] = A0 == dict(n_eligible=109, hits=2) or (A0['n_eligible'] == 109 and A0['hits'] == 2)

# KFG
k = sqlite3.connect(KFG_DB); sha = dict(k.execute('select name, sha256 from khipu'))
g0_bad = [f.split('/')[-1][:-5] for f in sorted(glob.glob(f'{XLSX}/*.xlsx'))
          if hashlib.sha256(open(f, 'rb').read()).hexdigest() != sha.get(f.split('/')[-1][:-5])]
PAT = re.compile(r'^p\d+(s\d+)*$'); val = {}; par = {}; lv = defaultdict(lambda: defaultdict(list)); n_skip = 0
for kh, nm, v in k.execute('select khipu, cord_name, value from cord order by khipu, idx'):
    if kh in g0_bad: continue
    nm = str(nm or '')
    if not PAT.match(nm): n_skip += 1; continue
    cid = (kh, nm); val[cid] = int(float(v)) if v not in (None, '') else 0
    d = nm.count('s') + 1; par[cid] = (kh, d)
    p = (kh, nm[:nm.rfind('s')]) if d >= 2 else None
    lv[kh][d].append((cid, p))
U = build(lv, val, par)
def permS(sv, B): return sv[np.argsort(rng.random((B, len(sv))), 1)]
def corpus(us, K, svs=None, pvs=None):
    svs = svs or [u['sv'] for u in us]; pvs = pvs or [u['pv'] for u in us]
    o = sum(int(H(s[None], u['M'], p)[0]) for u, s, p in zip(us, svs, pvs)); nl = np.zeros(K, np.int64)
    for u, s, p in zip(us, svs, pvs): nl += H(permS(s, K), u['M'], p)
    return dict(H=o, null_mean=float(nl.mean()), null_sd=float(nl.std()), null_max=int(nl.max()), p=float((1 + (nl >= o).sum()) / (1 + K)))
elig_by_depth = defaultdict(int)
for u in U: elig_by_depth[u['L'] - 1] += len(u['pv'])
res = dict(seed=6463, next_free_seed=6464, A0=A0, G0_hash_mismatch=g0_bad, skipped_non_path_cords=n_skip,
           n_units=len(U), n_khipus=len({u['kh'] for u in U}), n_eligible=int(sum(len(u['pv']) for u in U)),
           eligible_by_parent_depth=dict(sorted(elig_by_depth.items())))
res['primary'] = corpus(U, KC); print('primary', res['primary'], round(time.time() - T0, 1), flush=True)
res['without_KH0349'] = corpus([u for u in U if u['kh'] != 'KH0349'], KC)
HO = [u for u in U if u['kh'] not in okr_set]
res['heldout_descriptive'] = dict(corpus(HO, KC), n_khipus=len({u['kh'] for u in HO}), n_eligible=int(sum(len(u['pv']) for u in HO))) if HO else None
allp = [(ui, j) for ui, u in enumerate(U) for j in range(len(u['pv']))]
def plant(m):
    svs = [permS(u['sv'], 1)[0].copy() for u in U]; pvs = [u['pv'].copy() for u in U]
    for kk in rng.choice(len(allp), m, replace=False):
        ui, j = allp[kk]; ix = np.where(U[ui]['M'][:, j] == 1)[0]; s = svs[ui]
        if (s[ix] > 0).sum() < 2: s[ix[:2]] = np.maximum(s[ix[:2]], rng.integers(1, 30, 2))
        if s[ix].sum() < 10: s[ix[0]] += 10 - s[ix].sum()
        pvs[ui][j] = s[ix].sum()
    return corpus(U, KCTL, svs=svs, pvs=pvs)['p'] <= 0.01
fp = sum(corpus(U, KCTL, svs=[permS(u['sv'], 1)[0] for u in U])['p'] <= 0.01 for _ in range(NCTL))
print('calib', fp, round(time.time() - T0, 1), flush=True)
pw3 = sum(plant(3) for _ in range(NCTL)); pw5 = sum(plant(5) for _ in range(NCTL))
res['controls'] = dict(calib_fpr_01=fp / NCTL, power_3planted=pw3 / NCTL, power_5planted_disclosed=pw5 / NCTL, K_control=KCTL, n_corpora=NCTL)
p = res['primary']['p']; gates_ok = (not g0_bad) and A0['pass'] and fp / NCTL <= 0.03
if not gates_ok: v, st = 'GATES FAIL', 'no verdict'
elif p <= 0.01: v, st = 'evidence', 'CHANGED'
elif pw3 / NCTL >= 0.5: v, st = 'not supported (powered negative)', 'CHANGED'
else: v, st = 'not testable', 'REPLICATED'
res['verdict'] = v; res['kfg_status'] = st
hits = []
for u in U:
    h = ((u['sv'] @ u['M']) == u['pv']) & (((u['sv'] > 0).astype(np.int64) @ u['M']) >= 2)
    for j in np.where(h)[0]:
        hits.append(dict(khipu=u['kh'], parent=u['names'][j][1], parent_depth=u['L'] - 1, value=int(u['pv'][j]), heldout=u['kh'] not in okr_set))
res['hits'] = hits; res['seconds'] = round(time.time() - T0, 1)
json.dump(res, open(OUT, 'w'), indent=1); print(json.dumps({x: res[x] for x in res if x != 'hits'}, indent=1, default=str)); print('hits', hits)
