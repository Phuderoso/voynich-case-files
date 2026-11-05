#!/usr/bin/env python3
"""K028 - exact doublet-preserving null for the KH0240/KH0496 lead. Pre-registered in case-file/K028-markov-null-lead.md.
Usage: python3 tools/k028_markov_null_lead.py khipu.db"""
import sqlite3, sys, json, time, random
import numpy as np
from collections import defaultdict, Counter
t0 = time.time(); c = sqlite3.connect(sys.argv[1]); rnd = random.Random(28028)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
meta = {r[0]: (r[1], r[2]) for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
def place_(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
clpl = defaultdict(set); clcd = {}
for cid_, cl_, t_, v_ in c.execute("select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
    t_ = (t_ or '').strip()
    if t_ in ('S', 'L', 'E') and v_: clpl[cl_].add(place_(int(v_)) if t_ == 'S' else 0)
    clcd[cl_] = cid_
ordn_ = {r[0]: r[1] for r in c.execute("select CLUSTER_ID, ORDINAL from knot_cluster")}
bc_ = defaultdict(dict)
for cl_, pl_ in clpl.items():
    if len(pl_) == 1 and ordn_.get(cl_) is not None: bc_[clcd[cl_]][ordn_[cl_]] = next(iter(pl_))
R5 = {cd for cd, d in bc_.items() if len(d) >= 2 and not all(a > b for a, b in zip([d[o] for o in sorted(d)], [d[o] for o in sorted(d)][1:]))}
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: kh[khid].append(0 if cid in R5 else val.get(cid, 0))
ids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]
def collapse(s): return [x for j, x in enumerate(s) if j == 0 or x != s[j - 1]]
CS0 = [collapse(kh[k]) for k in ids]; okr = [meta[k][0] for k in ids]
A, B = okr.index('KH0240'), okr.index('KH0496'); print('khipus', len(ids), 'lead', A, B, flush=True)
# --- exact doublet-preserving shuffle (Kandel et al. 1996, Wilson's algorithm for the last-exit arborescence) ---
EDGES = []
for cs in CS0:
    out = defaultdict(list)
    for a, b in zip(cs, cs[1:]): out[a].append(b)
    EDGES.append(out)
def dshuffle(k):
    cs = CS0[k]
    if len(cs) < 3: return list(cs)
    out = EDGES[k]; last = cs[-1]; intree = {last}; nxt = {}
    for v in list(out):
        u = v
        while u not in intree:
            nxt[u] = rnd.choice(out[u]); u = nxt[u]
        u = v
        while u not in intree:
            intree.add(u); u = nxt[u]
    lists = {}
    for v, tg in out.items():
        t = list(tg)
        if v != last:
            t.remove(nxt[v]); rnd.shuffle(t); t.append(nxt[v])
        else: rnd.shuffle(t)
        lists[v] = t
    ptr = defaultdict(int); seq = [cs[0]]; u = cs[0]
    for _ in range(len(cs) - 1):
        w = lists[u][ptr[u]]; ptr[u] += 1; seq.append(w); u = w
    return seq
# shuffler check
def dub(cs): return Counter(zip(cs, cs[1:]))
bad = 0; differ = 0; elig = 0
for k in range(len(CS0)):
    d0 = dub(CS0[k]); dif = False
    for _ in range(20):
        s = dshuffle(k)
        if s[0] != CS0[k][0] or s[-1] != CS0[k][-1] or dub(s) != d0 or len(s) != len(CS0[k]): bad += 1
        if s != CS0[k]: dif = True
    if len(set(zip(CS0[k], CS0[k][1:]))) >= 3: elig += 1; differ += dif
check = dict(violations=bad, differ_share=round(differ / max(elig, 1), 4), eligible=elig, passed=bad == 0 and differ / max(elig, 1) >= 0.9)
print('check', check, round(time.time() - t0, 1), flush=True)
def npairs(CS):
    grams = defaultdict(set)
    for k, cs in enumerate(CS):
        for i in range(len(cs) - 8):
            g = tuple(cs[i:i + 9])
            if all(1 <= x <= 3 for x in g): grams[g].add(k)
    pairs = set()
    for ks in grams.values():
        ks = sorted(ks)
        for a in range(len(ks)):
            for b in range(a + 1, len(ks)): pairs.add((ks[a], ks[b]))
    return len(pairs)
def longest(x, y):
    best = 0; prev = [0] * (len(y) + 1)
    for i in range(1, len(x) + 1):
        cur = [0] * (len(y) + 1)
        for j in range(1, len(y) + 1):
            if x[i - 1] == y[j - 1] and x[i - 1] > 0: cur[j] = prev[j - 1] + 1; best = max(best, cur[j])
        prev = cur
    return best
S_obs = npairs(CS0); D_obs = longest(CS0[A], CS0[B]); print('obs S', S_obs, 'D', D_obs, flush=True)
NS = []
for r in range(1000):
    NS.append(npairs([dshuffle(k) for k in range(len(CS0))]))
    if r % 100 == 0: print('S null', r, round(time.time() - t0, 1), flush=True)
    if time.time() - t0 > 420: print('time cap at', r + 1, flush=True); break
NS = np.array(NS); pS = (1 + np.sum(NS >= S_obs)) / (len(NS) + 1)
ND = []
for r in range(20000):
    ND.append(longest(dshuffle(A), dshuffle(B)))
    if time.time() - t0 > 560: print('D cap at', r + 1, flush=True); break
ND = np.array(ND); pD = (1 + np.sum(ND >= D_obs)) / (len(ND) + 1)
out = dict(n_khipus=len(ids), check=check, S=dict(obs=S_obs, R=len(NS), null_dist=dict(Counter(NS.tolist())), p=float(pS), survives=bool(pS < 0.05 and check['passed'])),
           D=dict(obs=D_obs, R=len(ND), null_dist=dict(sorted(Counter(ND.tolist()).items())), p=float(pD)),
           lead_seqs={okr[A]: CS0[A], okr[B]: CS0[B]}, secs=round(time.time() - t0, 1))
json.dump(out, open('analysis/k028_results.json', 'w'), indent=1, default=str)
print(json.dumps({k: out[k] for k in ('check', 'S', 'D', 'secs')}, indent=1, default=str))
