#!/usr/bin/env python3
"""K003 - combined-window sum detector + size-matched UR test. Pre-registered in case-file/K003-combined-window-detector.md.
Usage: python3 tools/k003_combined_window.py data/khipu.db {dev|eval|corpus} [chosen]"""
import sqlite3, json, sys, time, numpy as np
from collections import defaultdict
DB, STAGE = sys.argv[1], sys.argv[2]
CHOSEN = sys.argv[3] if len(sys.argv) > 3 else None
CANDS = ['D2', 'D4', 'D5']
c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups: continue
    kh[khid].append(val.get(cid, 0))
data = [(k, np.array(v, np.int64)) for k, v in kh.items() if (np.array(v) > 0).sum() >= 10]

def scores(V):
    """V (B,n) -> (B,11) matrix: column k-2 = log-weighted k-block hits; plus D2 (any k<=6)."""
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    idx = np.arange(n); big = V >= 10; w = np.where(big, np.log10(np.maximum(V, 1)), 0.0)
    W = np.zeros((B, 11)); hs = np.zeros((B, n), bool); hl = np.zeros((B, n), bool)
    for k in range(2, 13):
        hk = np.zeros((B, n), bool)
        i = idx[idx + k < n]
        hk[:, i] |= ((P[:, i + k + 1] - P[:, i + 1]) == V[:, i]) & ((NZ[:, i + k + 1] - NZ[:, i + 1]) >= 2)
        i = idx[idx - k >= 0]
        hk[:, i] |= ((P[:, i] - P[:, i - k]) == V[:, i]) & ((NZ[:, i] - NZ[:, i - k]) >= 2)
        hk &= big; W[:, k - 2] = (w * hk).sum(1)
        if k <= 6: hs |= hk
        else: hl |= hk
    return W, (w * hs).sum(1), (w * hl).sum(1)

def colrank_p(N, x):
    """p of each row of x against null columns N (K,m): (#N>=x)/K per column."""
    Ns = np.sort(N, 0); K = N.shape[0]
    return np.stack([(K - np.searchsorted(Ns[:, j], x[:, j] - 1e-9, 'left')) / K for j in range(N.shape[1])], 1)

def pvals(obs_V, null_V):
    """Return dict candidate -> p for one observed row against K null rows."""
    Wo, so, lo = scores(obs_V[None]); Wn, sn, ln = scores(null_V); K = len(null_V)
    out = {'D2': (1 + (sn >= so[0] - 1e-9).sum()) / (1 + K)}
    for name, No, Nn in (('D4', np.c_[so, lo], np.c_[sn, ln]), ('D5', Wo, Wn)):
        live = Nn.max(0) > 0  # scores that are always zero carry no information
        live = live | (No[0] > 0)
        if not live.any(): out[name] = 1.0; continue
        Nn, No = Nn[:, live], No[:, live]
        pn = colrank_p(Nn, Nn).min(1); po = colrank_p(Nn, No).min(1)[0]
        out[name] = (1 + (pn <= po + 1e-12).sum()) / (1 + K)
    return out

def perm(rng, v, B): return np.array([rng.permutation(v) for _ in range(B)])
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
    seed, K = (4004, 300) if STAGE == 'dev' else (5005, 500)
    rng = np.random.default_rng(seed); cands = CANDS if STAGE == 'dev' else sorted({'D2', CHOSEN})
    sizes = np.array([len(v) for _, v in data]); t1, t2 = np.quantile(sizes[sizes >= 20], [1/3, 2/3])
    rec = {d: defaultdict(list) for d in cands}
    for khid, v in data:
        tests = [('calib', rng.permutation(v))] + [(s, plant(rng, v, s)) for s in ('A', 'B') if len(v) >= 20]
        for lab, x in tests:
            if x is None: continue
            p = pvals(x, perm(rng, x, K))
            third = 'small' if len(v) <= t1 else ('mid' if len(v) <= t2 else 'large')
            for d in cands:
                rec[d][lab].append(p[d])
                if lab != 'calib': rec[d][lab + '_' + third].append(p[d])
    out = {d: {lab: dict(n=len(p), rate_p05=round(float((np.array(p) <= 0.05).mean()), 4)) for lab, p in r.items()} for d, r in rec.items()}
    if STAGE == 'dev':
        ok = [d for d in CANDS if out[d]['calib']['rate_p05'] <= 0.05]
        out['chosen'] = max(ok, key=lambda d: ((out[d]['A']['rate_p05'] + out[d]['B']['rate_p05']) / 2, -CANDS.index(d))) if ok else None
    else:
        e = out[CHOSEN]; out['success'] = bool(e['calib']['rate_p05'] <= 0.05 and e['A']['rate_p05'] >= 0.80 and e['B']['rate_p05'] >= 0.60)
    out.update(seed=seed, K=K, size_thirds=[float(t1), float(t2)], seconds=round(time.time() - t0, 1))
    json.dump(out, open(f'analysis/k003_{STAGE}.json', 'w'), indent=1); print(json.dumps(out, indent=1))
else:
    rng = np.random.default_rng(6006); d = CHOSEN; rows = []
    for khid, v in data:
        p1 = pvals(v, perm(rng, v, 1000))[d]; p = p1; K2 = None
        if p1 <= 0.01: p = pvals(v, perm(rng, v, 20000))[d]; K2 = 20000
        rows.append(dict(khipu_id=khid, okr=names[khid][0], inv=names[khid][1], n_pend=len(v), p_stage1=p1, p=p, K2=K2))
    sig = bh([r['p'] for r in rows])
    for r, s in zip(rows, sig): r['bh_sig'] = bool(s)
    k2 = {r['khipu_id'] for r in json.load(open('analysis/k002_corpus.json'))['rows'] if r['bh_sig']}
    new = {r['khipu_id'] for r in rows if r['bh_sig']}
    # line 5: size-matched UR test
    ur = np.array([r['inv'].upper().startswith('UR') for r in rows]); sg = np.array([r['bh_sig'] for r in rows])
    n = np.array([r['n_pend'] for r in rows]); q = np.quantile(n, [.2, .4, .6, .8]); strat = np.searchsorted(q, n, 'right')
    obs = int((ur & sg).sum()); r7 = np.random.default_rng(7007); cnt = 0; NP = 100000
    for _ in range(NP):
        u = ur.copy()
        for s in range(5):
            m = strat == s; u[m] = r7.permutation(u[m])
        cnt += (u & sg).sum() >= obs
    summ = dict(detector=d, n=len(rows), n_p01=int(sum(r['p_stage1'] <= 0.01 for r in rows)), n_bh=int(sg.sum()),
                k002_detections=len(k2), k002_also_flagged=len(k2 & new), new_not_in_k002=sorted(names[x][0] + '/' + names[x][1] for x in new - k2),
                lost_from_k002=sorted(names[x][0] + '/' + names[x][1] for x in k2 - new),
                ur_flagged=obs, ur_total=int(ur.sum()), size_quintile_cuts=q.tolist(),
                ur_size_matched_p=(1 + cnt) / (1 + NP), ur_expected_size_matched=None, seconds=round(time.time() - t0, 1))
    json.dump(dict(summary=summ, rows=rows), open('analysis/k003_corpus.json', 'w'), indent=1); print(json.dumps(summ, indent=1))
    for r in sorted(rows, key=lambda r: r['p'])[:22]: print(r['okr'], r['inv'], r['n_pend'], r['p'], r['bh_sig'])
