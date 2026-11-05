#!/usr/bin/env python3
"""K030 - exact per-hit odds (D7/D8/D9) vs D5 on shared plants and nulls. Pre-registered in
case-file/K030-exact-weights-vs-d5.md. Usage: python3 tools/k030_exact_weights_vs_d5.py khipu.db"""
import sqlite3, sys, json, time, math, numpy as np
from collections import defaultdict, Counter
from math import comb, lgamma
t0 = time.time(); DB = sys.argv[1]; KMAX = 12; CAP = 20000; TCAP = 270  # seconds per stage
c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: kh[khid].append(val.get(cid, 0))
data = [(k, np.array(v, np.int64)) for k, v in kh.items() if (np.array(v) > 0).sum() >= 10]
skipped = sorted(names[k][0] for k, v in data if v.max() > CAP); data = [(k, v) for k, v in data if v.max() <= CAP]
def lcomb(a, b): return lgamma(a + 1) - lgamma(b + 1) - lgamma(a - b + 1)
def tables(v):
    """-log q_k(x) lookup L (13, X+1) and -log p_k vector."""
    n = len(v); X = int(v.max()); f = np.zeros((KMAX + 1, X + 1)); f[0, 0] = 1.0
    for y in v:
        y = int(y)
        for cc in range(KMAX, 0, -1): f[cc, y:] += f[cc - 1, :X + 1 - y]
    cnt = Counter(int(y) for y in v); n0 = cnt.get(0, 0); L = np.zeros((KMAX + 1, X + 1)); p = np.zeros(KMAX + 1)
    for y, m in cnt.items():
        if y < 10: continue
        g = np.zeros_like(f); g[0] = f[0]
        for cc in range(1, KMAX + 1):
            g[cc] = f[cc].copy(); g[cc, y:] -= g[cc - 1, :X + 1 - y]
        for k in range(2, min(KMAX, n - 1) + 1):
            N = max(g[k, y] - (m - 1) * comb(n0, k - 1), 0.0)
            if N > 0:
                q = math.exp(math.log(N) - lcomb(n - 1, k)); L[k, y] = -math.log(min(q, 1.0)); p[k] += m * q / n
    lp = np.array([-math.log(x) if x > 0 else 0.0 for x in p]); return L, lp
def scores(V, L, lp):
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    idx = np.arange(n); big = V >= 10; w10 = np.where(big, np.log10(np.maximum(V, 1)), 0.0)
    W5 = np.zeros((B, 11)); W9 = np.zeros((B, 11)); d7 = np.zeros(B)
    for k in range(2, 13):
        hk = np.zeros((B, n), bool)
        i = idx[idx + k < n]
        hk[:, i] |= ((P[:, i + k + 1] - P[:, i + 1]) == V[:, i]) & ((NZ[:, i + k + 1] - NZ[:, i + 1]) >= 2)
        i = idx[idx - k >= 0]
        hk[:, i] |= ((P[:, i] - P[:, i - k]) == V[:, i]) & ((NZ[:, i] - NZ[:, i - k]) >= 2)
        hk &= big; W5[:, k - 2] = (w10 * hk).sum(1); W9[:, k - 2] = (L[k][V] * hk).sum(1); d7 += hk.sum(1) * lp[k]
    return dict(D5=W5, D7=d7, D8=W9.sum(1), D9=W9)
def colrank_p(N, x):
    Ns = np.sort(N, 0); K = N.shape[0]
    return np.stack([(K - np.searchsorted(Ns[:, j], x[:, j] - 1e-9, 'left')) / K for j in range(N.shape[1])], 1)
def pvals(x, null, cands):
    L, lp = tables(x); So = scores(x[None], L, lp); Sn = scores(null, L, lp); K = len(null); out = {}
    for d in cands:
        No, Nn = So[d], Sn[d]
        if No.ndim == 1: out[d] = (1 + (Nn >= No[0] - 1e-9).sum()) / (1 + K); continue
        live = (Nn.max(0) > 0) | (No[0] > 0)
        if not live.any(): out[d] = 1.0; continue
        Nn, No = Nn[:, live], No[:, live]
        pn = colrank_p(Nn, Nn).min(1); po = colrank_p(Nn, No).min(1)[0]
        out[d] = (1 + (pn <= po + 1e-12).sum()) / (1 + K)
    return out
def perm(rng, v, B): return np.array([rng.permutation(v) for _ in range(B)])
def plant(rng, v, spec):  # K003 plant code, unchanged
    pl = rng.permutation(v).copy(); n = len(pl)
    for _ in range(2):
        k = 3 if spec == 'A' else int(rng.integers(2, 11))
        if n < k + 2: return None
        right = spec == 'A' or rng.random() < 0.5
        st = int(rng.integers(0, n - k)) if right else int(rng.integers(k, n))
        sl = slice(st + 1, st + 1 + k) if right else slice(st - k, st)
        blk = pl[sl]
        if (blk > 0).sum() < 2: blk[:] = np.maximum(blk, rng.integers(1, 30, len(blk)))
        s = int(blk.sum())
        if s < 10: blk[0] += 10 - s; s = int(blk.sum())
        pl[sl] = blk; pl[st] = s
    return pl
def stage(seed, K, cands):
    rng = np.random.default_rng(seed); rec = {d: defaultdict(list) for d in cands}; ts = time.time(); done = 0
    for khid, v in data:
        tests = [('calib', rng.permutation(v))] + [(s, plant(rng, v, s)) for s in ('A', 'B') if len(v) >= 20]
        for lab, x in tests:
            if x is None or x.max() > CAP: continue
            p = pvals(x, perm(rng, x, K), cands)
            for d in cands: rec[d][lab].append((khid, p[d]))
        done += 1
        if done % 100 == 0: print('seed', seed, 'khipu', done, round(time.time() - t0, 1), flush=True)
        if time.time() - ts > TCAP: print('time cap at', done, flush=True); break
    return rec, done
def rate(lst): return float(np.mean([p <= 0.05 for _, p in lst])) if lst else float('nan')
dev, ndev = stage(3030, 300, ['D5', 'D7', 'D8', 'D9'])
devs = {d: dict(fpr=rate(r['calib']), A=rate(r['A']), B=rate(r['B'])) for d, r in dev.items()}
ok = [d for d in ['D7', 'D8', 'D9'] if devs[d]['fpr'] <= 0.05]
chosen = max(ok, key=lambda d: ((devs[d]['A'] + devs[d]['B']) / 2, -['D7', 'D8', 'D9'].index(d))) if ok else None
print('dev', json.dumps(devs), 'chosen', chosen, flush=True)
res = dict(skipped_cap=skipped, dev=devs, dev_khipus=ndev, chosen=chosen)
if chosen:
    ev, nev = stage(3031, 500, ['D5', chosen]); e = {d: dict(fpr=rate(r['calib']), A=rate(r['A']), B=rate(r['B'])) for d, r in ev.items()}
    a = np.array([p <= 0.05 for lab in 'AB' for _, p in ev[chosen][lab]]); b = np.array([p <= 0.05 for lab in 'AB' for _, p in ev['D5'][lab]])
    n10, n01 = int((a & ~b).sum()), int((~a & b).sum()); nd = n10 + n01
    mc = min(1.0, 2 * sum(comb(nd, i) for i in range(min(n10, n01) + 1)) / 2 ** nd) if nd else 1.0
    gain = (e[chosen]['A'] + e[chosen]['B']) / 2 - (e['D5']['A'] + e['D5']['B']) / 2
    res.update(eval=e, eval_khipus=nev, chosen_only=n10, d5_only=n01, mcnemar_p=mc, mean_gain=gain,
               adopted=bool(e[chosen]['fpr'] <= 0.05 and gain >= 0.03 and mc < 0.05),
               k003_bar_met=bool(e[chosen]['fpr'] <= 0.05 and e[chosen]['A'] >= 0.80 and e[chosen]['B'] >= 0.60))
res['secs'] = round(time.time() - t0, 1)
json.dump(res, open('analysis/k030_results.json', 'w'), indent=1, default=float); print(json.dumps(res, indent=1, default=float))
