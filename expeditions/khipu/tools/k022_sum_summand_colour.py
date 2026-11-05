#!/usr/bin/env python3
"""K022 - Are sum cords the same colour as their summands? Pre-registered in case-file/K022 (commit d2acdd49).
A = sum over sum cords of share of summand-block cords (known colour) equal to the sum cord's colour.
Null: per sum cord, a random non-sum eligible cord of the same khipu with a block of the same k and direction."""
import sqlite3, json, sys, time, numpy as np
from collections import defaultdict
t0 = time.time(); DB = '../khipu.db'; R = 20000; NC = 200; KMAX = 12; SEED = 20261107; ALPHA = 0.05
rng = np.random.default_rng(SEED); c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
col = {}
for cid, fc in c.execute("select CORD_ID, FULL_COLOR from ascher_cord_color order by CORD_ID, RANGE_BEG, color_id"):
    if cid not in col and fc not in (None, '', "''"): col[cid] = fc.strip()
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: kh[khid].append(cid)
sigk = {r['okr'] for r in json.load(open('analysis/k001_results_K5000.json'))['rows'] if r.get('bh_sig_N1')}
def block(V, i):  # first matching block: smallest k, right before left -> (k, dir) or None
    n = len(V); P = np.r_[0, np.cumsum(V)]; NZ = np.r_[0, np.cumsum(V > 0)]
    if V[i] < 10: return None
    for k in range(2, KMAX + 1):
        if i + k < n and P[i + k + 1] - P[i + 1] == V[i] and NZ[i + k + 1] - NZ[i + 1] >= 2: return (k, 1)
        if i - k >= 0 and P[i] - P[i - k] == V[i] and NZ[i] - NZ[i - k] >= 2: return (k, -1)
    return None
def bidx(i, k, d, n):
    js = list(range(i + 1, i + k + 1)) if d == 1 else list(range(i - k, i))
    return js if js[0] >= 0 and js[-1] < n else None
def score(C, i, js):
    kn = [C[j] for j in js if C[j] is not None]
    return None if not kn else sum(x == C[i] for x in kn) / len(kn)
items = []  # per sum cord: observed score, pool of null anchor scores, pool anchors (for controls), khipu data
for khid, cids in kh.items():
    V = np.array([val.get(x, 0) for x in cids], np.int64); C = [col.get(x) for x in cids]; n = len(cids)
    bl = {i: block(V, i) for i in range(n)}; sums = {i for i, b in bl.items() if b}
    elig_ns = [j for j in range(n) if V[j] >= 10 and C[j] is not None and j not in sums]
    for i in sorted(sums):
        if C[i] is None: continue
        k, d = bl[i]; s = score(C, i, bidx(i, k, d, n))
        if s is None: continue
        pool = []
        for j in elig_ns:
            js = bidx(j, k, d, n)
            if js is None: continue
            sj = score(C, j, js)
            if sj is not None: pool.append((j, js, sj))
        if not pool: continue
        items.append(dict(okr=names[khid][0], prim=names[khid][0] in sigk, obs=s, pool=pool, C=C, k=k, d=d))
def null_draw(its, Rr):
    tot = np.zeros(Rr)
    for it in its:
        ps = np.array([p[2] for p in it['pool']]); tot += ps[rng.integers(0, len(ps), Rr)]
    return tot
def p2(o, nl):
    hi = (1 + (nl >= o - 1e-12).sum()) / (1 + len(nl)); lo = (1 + (nl <= o + 1e-12).sum()) / (1 + len(nl))
    return float(min(1.0, 2 * min(hi, lo)))
def planted(it, j, js, mode):
    C = it['C']; kn = [C[x] for x in js if C[x] is not None]; eq = []
    for x in kn:
        e = x == C[j]
        if rng.random() < 0.3: e = (mode == 'match')
        eq.append(e)
    return sum(eq) / len(eq)
def run(its, label, controls):
    A = sum(it['obs'] for it in its); N = null_draw(its, R); out = dict(pop=label, n_sum_cords=len(its), A=A,
        A_null_mean=float(N.mean()), A_null_sd=float(N.std()), p_two_sided=p2(A, N), direction='match' if A > N.mean() else 'apart')
    if controls:
        fp = pm = pa = 0
        for _ in range(NC):
            pick = [it['pool'][rng.integers(len(it['pool']))] for it in its]
            fp += p2(sum(p[2] for p in pick), N) <= ALPHA
            pm += p2(sum(planted(it, p[0], p[1], 'match') for it, p in zip(its, pick)), N) <= ALPHA
            pa += p2(sum(planted(it, p[0], p[1], 'apart') for it, p in zip(its, pick)), N) <= ALPHA
        out.update(calib_fpr=fp / NC, power_match=pm / NC, power_apart=pa / NC)
        pw = out['power_match'] if out['direction'] == 'match' else out['power_apart']
        out['verdict'] = ('controls failed' if out['calib_fpr'] > 0.08 else
                          ('totals match summands' if out['direction'] == 'match' else 'totals coloured apart') if out['p_two_sided'] <= ALPHA
                          else 'not supported' if pw >= 0.5 else 'not testable')
    return out
prim = [it for it in items if it['prim']]
res = dict(seed=SEED, R=R, primary=run(prim, 'K001 BH-significant', True), secondary=run(items, 'all khipus with a sum cord', False))
pk = defaultdict(lambda: [0, 0.0, 0.0])
for it in prim:
    pk[it['okr']][0] += 1; pk[it['okr']][1] += it['obs']; pk[it['okr']][2] += float(np.mean([p[2] for p in it['pool']]))
res['per_khipu'] = [dict(okr=k, n=v[0], obs=round(v[1], 2), null_mean=round(v[2], 2)) for k, v in sorted(pk.items())]
res['runtime_s'] = round(time.time() - t0, 1)
json.dump(res, open('analysis/k022_results.json', 'w'), indent=1); print(json.dumps(res, indent=1))
