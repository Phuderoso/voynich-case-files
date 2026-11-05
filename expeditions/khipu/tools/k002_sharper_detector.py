#!/usr/bin/env python3
"""K002 - sharper sum-cord detector. Pre-registered in case-file/K002-sharper-sum-detector.md.
Usage: python3 tools/k002_sharper_detector.py data/khipu.db {dev|eval|corpus} [chosen]
Stages: dev (seed 1001, K=300), eval (seed 2002, K=500), corpus (seed 3003, K=1000 then fresh K=20000 if p<=0.01)."""
import sqlite3, json, sys, time, numpy as np
from collections import defaultdict
DB, STAGE = sys.argv[1], sys.argv[2]
CHOSEN = sys.argv[3] if len(sys.argv) > 3 else None
CANDS = ['D0', 'D1', 'D2', 'D3']
c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
kh = defaultdict(list)
for khid, cid, cl in c.execute("select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups: continue
    kh[khid].append((cl, val.get(cid, 0)))
data = []
for khid, cords in kh.items():
    v = np.array([x[1] for x in cords], np.int64)
    if (v > 0).sum() < 10: continue
    gid = []; last = object(); g = -1
    for x in cords:
        if x[0] != last: g += 1; last = x[0]
        gid.append(g)
    data.append((khid, v, np.array(gid)))

def stats(V, gid):
    """V (B,n) -> dict of candidate statistics, each shape (B,)."""
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    h6 = np.zeros((B, n), bool); h12 = np.zeros((B, n), bool); idx = np.arange(n)
    for k in range(2, 13):
        hk = np.zeros((B, n), bool)
        i = idx[idx + k < n]
        hk[:, i] |= ((P[:, i + k + 1] - P[:, i + 1]) == V[:, i]) & ((NZ[:, i + k + 1] - NZ[:, i + 1]) >= 2)
        i = idx[idx - k >= 0]
        hk[:, i] |= ((P[:, i] - P[:, i - k]) == V[:, i]) & ((NZ[:, i] - NZ[:, i - k]) >= 2)
        h12 |= hk
        if k <= 6: h6 |= hk
    big = V >= 10; h6 &= big; h12 &= big
    ng = gid.max() + 1
    M = np.zeros((n, ng), np.int64); M[idx, gid] = 1
    G = V @ M; GNZ = (V > 0).astype(np.int64) @ M
    okg = GNZ >= 2
    r2 = np.zeros((B, n), bool)
    for j in range(ng):
        r2 |= (V == G[:, j:j + 1]) & okg[:, j:j + 1] & (gid != j)[None, :]
    r2 &= big
    w = np.where(big, np.log10(np.maximum(V, 1)), 0.0)
    return dict(D0=h12.sum(1).astype(float), D1=(w * h12).sum(1), D2=(w * h6).sum(1), D3=(w * (h12 | r2)).sum(1))

def perm(rng, v, B): return np.array([rng.permutation(v) for _ in range(B)])
def pv(obs, null): return (1 + (null >= obs - 1e-9).sum()) / (1 + len(null))
def plant(rng, v, spec):
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
def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps); o = np.argsort(ps); thr = q * np.arange(1, m + 1) / m
    ok = ps[o] <= thr; kk = np.max(np.where(ok)[0]) + 1 if ok.any() else 0
    s = np.zeros(m, bool); s[o[:kk]] = True; return s

t0 = time.time()
if STAGE in ('dev', 'eval'):
    seed, K = (1001, 300) if STAGE == 'dev' else (2002, 500)
    rng = np.random.default_rng(seed); cands = CANDS if STAGE == 'dev' else sorted({'D0', CHOSEN})
    specs = ['A'] if STAGE == 'dev' else ['A', 'B']
    rec = {d: dict(calib=[], **{s: [] for s in specs}) for d in cands}
    for khid, v, gid in data:
        tests = [('calib', rng.permutation(v))] + [(s, plant(rng, v, s)) for s in specs if len(v) >= 20]
        for lab, x in tests:
            if x is None: continue
            o = stats(x[None], gid); nl = stats(perm(rng, x, K), gid)
            for d in cands: rec[d][lab].append(pv(o[d][0], nl[d]))
    out = {d: {lab: dict(n=len(p), rate_p05=float((np.array(p) <= 0.05).mean())) for lab, p in r.items()} for d, r in rec.items()}
    if STAGE == 'dev':
        ok = [d for d in CANDS if out[d]['calib']['rate_p05'] <= 0.05]
        out['chosen'] = max(ok, key=lambda d: (out[d]['A']['rate_p05'], -CANDS.index(d))) if ok else None
    out.update(seed=seed, K=K, seconds=round(time.time() - t0, 1))
    json.dump(out, open(f'analysis/k002_{STAGE}.json', 'w'), indent=1); print(json.dumps(out, indent=1))
else:
    rng = np.random.default_rng(3003); d = CHOSEN; rows = []
    for khid, v, gid in data:
        o = stats(v[None], gid)[d][0]; p1 = pv(o, stats(perm(rng, v, 1000), gid)[d]); p = p1; K2 = None
        if p1 <= 0.01:
            nl = np.concatenate([stats(perm(rng, v, 2000), gid)[d] for _ in range(10)]); p = pv(o, nl); K2 = len(nl)
        rows.append(dict(khipu_id=khid, okr=names[khid][0], inv=names[khid][1], n_pend=len(v), stat=float(o), p_stage1=p1, p=p, K2=K2))
    sig = bh([r['p'] for r in rows])
    for r, s in zip(rows, sig): r['bh_sig'] = bool(s)
    k001 = json.load(open('analysis/k001_results_K5000.json'))['rows']; old = {r['khipu_id'] for r in k001 if r['bh_sig_N1']}
    new = {r['khipu_id'] for r in rows if r['bh_sig']}
    summ = dict(detector=d, n=len(rows), n_p01=int(sum(r['p_stage1'] <= 0.01 for r in rows)), n_bh=int(sig.sum()),
                k001_detections=len(old), k001_also_flagged=len(old & new), new_not_in_k001=len(new - old),
                series_of_bh={s: sum(1 for r in rows if r['bh_sig'] and r['inv'].startswith(s)) for s in ('UR', 'AS', 'other')},
                seconds=round(time.time() - t0, 1))
    summ['series_of_bh']['other'] = summ['n_bh'] - summ['series_of_bh']['UR'] - summ['series_of_bh']['AS']
    json.dump(dict(summary=summ, rows=rows), open('analysis/k002_corpus.json', 'w'), indent=1); print(json.dumps(summ, indent=1))
    for r in sorted(rows, key=lambda r: r['p'])[:25]: print(r['okr'], r['inv'], r['n_pend'], round(r['stat'], 2), r['p'], r['bh_sig'])
