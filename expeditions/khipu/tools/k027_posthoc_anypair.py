#!/usr/bin/env python3
# POST-HOC (disclosed): same as k027 but the lead pair is NOT excluded from N2, so N2 under the null estimates the
# corpus-wide chance that ANY pair shares a 9-block over {1,2,3}. Power section kept at 1 trial (not used).
"""K027 - is KH0240/KH0496's collapsed pattern a shared small-number template? Pre-registered in
case-file/K027-small-number-template.md. Usage: python3 tools/k027_small_number_template.py khipu.db"""
import sqlite3, sys, json, time, numpy as np
from collections import defaultdict
t0 = time.time(); c = sqlite3.connect(sys.argv[1]); rng = np.random.default_rng(27028); R, TR = 2000, 1
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
ids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]; seqs = [np.array(kh[k], np.int64) for k in ids]
okr = [meta[k][0] for k in ids]; LEAD = {okr.index('KH0240'), okr.index('KH0496')}
print('khipus', len(ids), 'lead idx', LEAD, flush=True)
def runs(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; return np.split(s, b)
RUNS = [runs(s) for s in seqs]
def collapse(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; return s[np.concatenate([[0], b])].tolist()
P = (1, 2, 1, 2, 3, 1, 2, 1, 3)
def contains(cs, pat):
    n = len(pat)
    return any(tuple(cs[i:i + n]) == pat for i in range(len(cs) - n + 1))
def stats(CS):
    n1 = sum(contains(cs, P) for k, cs in enumerate(CS) if k not in LEAD)
    grams = defaultdict(set)
    for k, cs in enumerate(CS):
        for i in range(len(cs) - 8):
            g = tuple(cs[i:i + 9])
            if all(1 <= x <= 3 for x in g): grams[g].add(k)
    pairs = set()
    for g, ks in grams.items():
        ks = sorted(ks)
        for a in range(len(ks)):
            for b in range(a + 1, len(ks)): pairs.add((ks[a], ks[b]))
    pass
    return n1, len(pairs), pairs
CS0 = [collapse(s) for s in seqs]
n1, n2, pairs = stats(CS0); print('obs', n1, n2, round(time.time() - t0, 1), flush=True)
def nullCS():
    return [collapse(np.concatenate([r[i] for i in rng.permutation(len(r))])) for r in RUNS]
N1, N2 = [], []
for rep in range(R):
    a, b, _ = stats(nullCS()); N1.append(a); N2.append(b)
    if rep % 500 == 0: print('null', rep, round(time.time() - t0, 1), flush=True)
    if time.time() - t0 > 420: print('time cap at', rep + 1, flush=True); break
N1, N2 = np.array(N1), np.array(N2); Rr = len(N1)
p1 = (1 + np.sum(N1 >= n1)) / (Rr + 1); p2 = (1 + np.sum(N2 >= n2)) / (Rr + 1)
q1, q2 = np.quantile(N1, 0.975), np.quantile(N2, 0.975)
others = [k for k in range(len(ids)) if k not in LEAD]
def write(cs, block):
    i = rng.integers(0, max(1, len(cs) - len(block))); cs = list(cs); cs[i:i + len(block)] = list(block)
    # keep collapsed form valid: drop equal neighbours created at the edges
    return [x for j, x in enumerate(cs) if j == 0 or x != cs[j - 1]]
pw1 = pw2 = 0
for t in range(TR):
    CS = nullCS()
    for k in rng.choice(others, 3, replace=False): CS[k] = write(CS[k], P)
    pw1 += stats(CS)[0] > q1
    CS = nullCS()
    for _ in range(5):
        blk = [int(rng.integers(1, 4))]
        while len(blk) < 9:
            x = int(rng.integers(1, 4))
            if x != blk[-1]: blk.append(x)
        a, b = rng.choice(others, 2, replace=False); CS[a] = write(CS[a], blk); CS[b] = write(CS[b], blk)
    pw2 += stats(CS)[1] > q2
    if time.time() - t0 > 560: print('power cap at', t + 1, flush=True); TR = t + 1; break
out = dict(n_khipus=len(ids), R=Rr, T1=dict(obs=n1, null_mean=float(N1.mean()), q975=float(q1), p=float(p1), power=pw1 / TR),
           T2=dict(obs=n2, null_mean=float(N2.mean()), q975=float(q2), p=float(p2), power=pw2 / TR,
                   pairs=[(okr[a] + ' ' + meta[ids[a]][1], okr[b] + ' ' + meta[ids[b]][1]) for a, b in sorted(pairs)][:40]),
           P_holders=[okr[k] + ' ' + meta[ids[k]][1] for k, cs in enumerate(CS0) if contains(cs, P)], trials=TR, secs=round(time.time() - t0, 1))
json.dump(out, open('analysis/k027_posthoc_anypair.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
