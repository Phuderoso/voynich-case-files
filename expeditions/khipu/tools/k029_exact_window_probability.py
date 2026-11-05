#!/usr/bin/env python3
"""K029 - exact per-window match probability p_k and the weighted detector W. Pre-registered in
case-file/K029-exact-window-probability.md. Usage: python3 tools/k029_exact_window_probability.py khipu.db"""
import sqlite3, sys, json, time, math, numpy as np
from collections import defaultdict, Counter
from math import comb
t0 = time.time(); DB = sys.argv[1]; KMAX = 12; MINP = 10; R = 1000; CAP = 20000
rng = np.random.default_rng(29029); c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: kh[khid].append(val.get(cid, 0))
def pk_exact(v):
    n = len(v); X = int(v.max()); f = np.zeros((KMAX + 1, X + 1)); f[0, 0] = 1.0
    for y in v:
        y = int(y)
        if y > X: continue  # values above X can never be in a subset summing to <= X
        for cc in range(KMAX, 0, -1): f[cc, y:] += f[cc - 1, :X + 1 - y]
    big = [int(y) for y in v if y > X]  # none by construction
    cnt = Counter(int(y) for y in v); n0 = cnt.get(0, 0); p = np.zeros(KMAX + 1)
    for y, m in cnt.items():
        if y < 10: continue
        g = np.zeros_like(f); g[0] = f[0]
        for cc in range(1, KMAX + 1):
            g[cc] = f[cc].copy(); g[cc, y:] -= g[cc - 1, :X + 1 - y]
        for k in range(2, KMAX + 1):
            if k > n - 1: break
            N = g[k, y] - (m - 1) * comb(n0, k - 1)
            p[k] += m * max(N, 0.0) / comb(n - 1, k)
    return p / n
def matches(V):  # V (B,n): returns per-row list of (k) match count arrays: M[B, k] and hit-cord count S
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    hit = np.zeros((B, n), bool); idx = np.arange(n); M = np.zeros((B, KMAX + 1), np.int64); big = V >= 10
    for k in range(2, KMAX + 1):
        ok = idx + k < n; i = idx[ok]
        m = (P[:, i + k + 1] - P[:, i + 1] == V[:, i]) & (NZ[:, i + k + 1] - NZ[:, i + 1] >= 2) & big[:, i]
        hit[:, i] |= m; M[:, k] += m.sum(1)
        ok = idx - k >= 0; i = idx[ok]
        m = (P[:, i] - P[:, i - k] == V[:, i]) & (NZ[:, i] - NZ[:, i - k] >= 2) & big[:, i]
        hit[:, i] |= m; M[:, k] += m.sum(1)
    return M, hit.sum(1)
def perms(v, B): return np.array([rng.permutation(v) for _ in range(B)])
def pv(o, nul): return (1 + np.sum(nul >= o - 1e-9)) / (1 + len(nul))
elig = [(k, np.array(v, np.int64)) for k, v in kh.items() if sum(x > 0 for x in v) >= MINP]
skipped = [names[k][0] for k, v in elig if v.max() > CAP]; elig = [(k, v) for k, v in elig if v.max() <= CAP]
print('eligible', len(elig), 'skipped (max>CAP)', len(skipped), flush=True)
# --- audit ---
aud = []
for j in rng.choice(len(elig), 20, replace=False):
    k_, v = elig[j]; p = pk_exact(v); n = len(v)
    E = sum(2 * (n - k) * p[k] for k in range(2, KMAX + 1) if k < n)
    M, _ = matches(perms(v, 2000)); tot = M.sum(1); se = tot.std() / math.sqrt(len(tot))
    aud.append(dict(okr=names[k_][0], n=n, exact=float(E), mc=float(tot.mean()), se=float(se), ok=bool(abs(E - tot.mean()) <= 3 * se + 1e-9)))
aud_pass = sum(a['ok'] for a in aud) >= 19
print('audit', sum(a['ok'] for a in aud), '/20', round(time.time() - t0, 1), flush=True)
rows = []
for idx_, (k_, v) in enumerate(elig):
    p = pk_exact(v); w = np.array([-math.log(p[k]) if p[k] > 0 else 0.0 for k in range(KMAX + 1)])
    def score(V):
        M, S = matches(V); return M @ w, S
    nulV = perms(v, R); Wn, Sn = score(nulV); Wo, So = score(v[None])
    fake = rng.permutation(v); Wf, Sf = score(fake[None]); Wfn, Sfn = score(perms(fake, R))
    row = dict(okr=names[k_][0], inv=names[k_][1], n=len(v), W_obs=float(Wo[0]), S_obs=int(So[0]), pW=pv(Wo[0], Wn), pS=pv(So[0], Sn),
               calW=pv(Wf[0], Wfn), calS=pv(Sf[0], Sfn))
    if len(v) >= 20:
        pl = rng.permutation(v).copy()
        for st in rng.choice(np.arange(0, len(v) - 4), 2, replace=False):
            blk = pl[st + 1: st + 4]
            if (blk > 0).sum() < 2: blk[:] = np.maximum(blk, rng.integers(1, 30, 3))
            pl[st + 1: st + 4] = blk; pl[st] = blk.sum() if blk.sum() >= 10 else blk.sum() + 10
            if pl[st] != blk.sum(): pl[st + 1] += pl[st] - blk.sum()
        if pl.max() <= CAP:
            pp = pk_exact(pl); ww = np.array([-math.log(pp[k]) if pp[k] > 0 else 0.0 for k in range(KMAX + 1)])
            Mn, Snl = matches(perms(pl, R)); Mo, Sol = matches(pl[None])
            row['plW'] = pv(float(Mo[0] @ ww), Mn @ ww); row['plS'] = pv(int(Sol[0]), Snl)
    rows.append(row)
    if idx_ % 50 == 0: print('khipu', idx_, round(time.time() - t0, 1), flush=True)
    if time.time() - t0 > 540: print('time cap at', idx_ + 1, flush=True); break
def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps); o = np.argsort(ps); ok = ps[o] <= q * np.arange(1, m + 1) / m
    kmax = np.max(np.where(ok)[0]) + 1 if ok.any() else 0; s = np.zeros(m, bool); s[o[:kmax]] = True; return s
calW = np.mean([r['calW'] <= 0.05 for r in rows]); calS = np.mean([r['calS'] <= 0.05 for r in rows])
pl = [r for r in rows if 'plW' in r]; a = np.array([r['plW'] <= 0.05 for r in pl]); b = np.array([r['plS'] <= 0.05 for r in pl])
n10, n01 = int(np.sum(a & ~b)), int(np.sum(~a & b)); nd = n10 + n01
mc = min(1.0, 2 * sum(comb(nd, i) for i in range(0, min(n10, n01) + 1)) / 2 ** nd) if nd else 1.0
powW, powS = float(a.mean()), float(b.mean())
adopted = bool(aud_pass and calW <= 0.06 and powW - powS >= 0.05 and mc < 0.05)
sigW = bh([r['pW'] for r in rows]); sigS = bh([r['pS'] for r in rows])
out = dict(n_scored=len(rows), skipped_cap=skipped, audit=aud, audit_pass=aud_pass, calib_fpr=dict(W=float(calW), S=float(calS)),
           power=dict(W=powW, S=powS, n=len(pl), W_only=n10, S_only=n01, mcnemar_p=mc), adopted=adopted,
           bh_W=[r['okr'] + ' ' + r['inv'] for r, s in zip(rows, sigW) if s], bh_S=[r['okr'] + ' ' + r['inv'] for r, s in zip(rows, sigS) if s],
           secs=round(time.time() - t0, 1))
json.dump(dict(summary=out, rows=rows), open('analysis/k029_results.json', 'w'), indent=1, default=float)
print(json.dumps({k: out[k] for k in out if k != 'audit'}, indent=1, default=float))
