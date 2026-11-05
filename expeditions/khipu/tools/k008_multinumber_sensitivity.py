#!/usr/bin/env python3
"""K008 - sensitivity of K001 (adjacent sums) and K004 (subsidiary sums) to multi-number cords (K007's R5 cords).
Pre-registered in case-file/K008-multinumber-sensitivity.md. Usage: python3 tools/k008_multinumber_sensitivity.py data/khipu.db
R5 cord: >= 2 knot clusters with a single decimal place, and the places read in knot_cluster.ORDINAL order are not
strictly decreasing (same definition as K007). Masking: an R5 cord is never a sum target, never part of a summand
block, and keeps its position; nulls permute only the non-R5 values among non-R5 positions."""
import sqlite3, sys, json, time, numpy as np
from collections import defaultdict
t0 = time.time(); DB = sys.argv[1]; c = sqlite3.connect(DB)
K1 = 5000; KMAX = 12; MINP = 10; rng = np.random.default_rng(20261105)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
# --- R5 definition (K007) ---
def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
clplaces = defaultdict(set); clcord = {}
for cid, cl, t, v in c.execute("select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
    t = (t or '').strip()
    if t in ('S', 'L', 'E') and v: clplaces[cl].add(place(int(v)) if t == 'S' else 0)
    clcord[cl] = cid
ordn = {r[0]: r[1] for r in c.execute("select CLUSTER_ID, ORDINAL from knot_cluster")}
bycord = defaultdict(dict)
for cl, pl in clplaces.items():
    if len(pl) == 1 and ordn.get(cl) is not None: bycord[clcord[cl]][ordn[cl]] = next(iter(pl))
R5 = set()
for cd, d in bycord.items():
    s = [d[o] for o in sorted(d)]
    if len(s) >= 2 and not all(a > b for a, b in zip(s, s[1:])): R5.add(cd)
def pval(o, n): return (1 + (n >= o).sum()) / (1 + len(n))
def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps); o = np.argsort(ps); thr = q * np.arange(1, m + 1) / m
    ok = ps[o] <= thr; kk = np.max(np.where(ok)[0]) + 1 if ok.any() else 0
    s = np.zeros(m, bool); s[o[:kk]] = True; return s
# ---------------- K001 masked ----------------
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups: continue
    kh[khid].append(cid)
def S_batch(V, bad):  # bad: (n,) bool, fixed positions
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    BD = np.zeros(n + 1, np.int64); BD[1:] = np.cumsum(bad)
    hit = np.zeros((B, n), bool); idx = np.arange(n)
    for k in range(2, KMAX + 1):
        i = idx[idx + k < n]
        ok = (BD[i + k + 1] - BD[i + 1]) == 0
        s = P[:, i + k + 1] - P[:, i + 1]; z = NZ[:, i + k + 1] - NZ[:, i + 1]
        hit[:, i] |= (s == V[:, i]) & (z >= 2) & ok
        i = idx[idx - k >= 0]
        ok = (BD[i] - BD[i - k]) == 0
        s = P[:, i] - P[:, i - k]; z = NZ[:, i] - NZ[:, i - k]
        hit[:, i] |= (s == V[:, i]) & (z >= 2) & ok
    hit &= (V >= 10) & ~bad
    return hit.sum(1)
def permmask(v, bad, B):
    free = np.where(~bad)[0]; out = np.tile(v, (B, 1))
    for b in range(B): out[b, free] = rng.permutation(v[free])
    return out
k001_old = {r['khipu_id']: r for r in json.load(open('analysis/k001_results_K5000.json'))['rows']}
rows1 = []
for khid, cids in kh.items():
    if khid not in k001_old: continue  # same eligible set as K001
    v = np.array([val.get(x, 0) for x in cids], np.int64); bad = np.array([x in R5 for x in cids])
    nb = int(bad.sum())
    if ((v > 0) & ~bad).sum() < MINP:
        rows1.append(dict(khipu_id=khid, okr=names[khid][0], inv=names[khid][1], n_r5=nb, testable=False)); continue
    obs = int(S_batch(v[None], bad)[0])
    if nb == 0: p = k001_old[khid]['p_N1']; pc = None  # unchanged data -> reuse K001 p (same statistic)
    else:
        p = pval(obs, S_batch(permmask(v, bad, K1), bad))
        fake = permmask(v, bad, 1)[0]; pc = pval(int(S_batch(fake[None], bad)[0]), S_batch(permmask(fake, bad, 2000), bad))
    rows1.append(dict(khipu_id=khid, okr=names[khid][0], inv=names[khid][1], n_pend=len(v), n_r5=nb, testable=True,
                      S_old=k001_old[khid]['S_obs'], S_masked=obs, p_old=k001_old[khid]['p_N1'], p_masked=p,
                      p_calib=pc, bh_old=k001_old[khid]['bh_sig_N1']))
print('K001 done', round(time.time() - t0, 1), flush=True)
T = [r for r in rows1 if r['testable']]; sig = bh([r['p_masked'] for r in T])
for r, s in zip(T, sig): r['bh_masked'] = bool(s)
old_sig = [r for r in T if r['bh_old']]
cal = [r['p_calib'] for r in T if r['p_calib'] is not None]
k001 = dict(n_khipus=len(rows1), n_testable=len(T), n_with_r5=sum(r['n_r5'] > 0 for r in rows1),
            n_untestable=len(rows1) - len(T), bh_old=len(old_sig), bh_masked=int(sig.sum()),
            old_sig_survive=sum(r['bh_masked'] for r in old_sig),
            new_sig=[(r['okr'], r['inv']) for r in T if r['bh_masked'] and not r['bh_old']],
            lost=[(r['okr'], r['inv'], r['p_masked']) for r in old_sig if not r['bh_masked']],
            calib_fpr_05=float(np.mean([p <= 0.05 for p in cal])) if cal else None, calib_n=len(cal),
            old_sig_rows=[{k: r[k] for k in ('okr', 'inv', 'n_r5', 'S_old', 'S_masked', 'p_old', 'p_masked', 'bh_masked')} for r in old_sig])
print(json.dumps(k001, indent=1), flush=True)
# ---------------- K004 masked ----------------
lvl1 = {}; subs = defaultdict(list)
for khid, cid, lev, par in c.execute("select KHIPU_ID, CORD_ID, CORD_LEVEL, PENDANT_FROM from cord order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups: continue
    if lev == 1: lvl1[cid] = khid
    elif lev == 2: subs[khid].append((cid, par))
def H(S, M, P):
    tot = S @ M; nz = (S > 0).astype(np.int64) @ M
    return ((tot == P) & (nz >= 2)).sum(1)
def build(masked):
    out = []
    for khid in sorted(subs):
        pars = [p for _, p in subs[khid]]
        badpar = {p for s, p in subs[khid] if s in R5} if masked else set()
        elig = sorted({p for p in pars if p in lvl1 and lvl1[p] == khid and val.get(p, 0) >= 10 and pars.count(p) >= 2
                       and not (masked and (p in R5 or p in badpar))})
        if not elig: continue
        sl = [(s, p) for s, p in subs[khid] if not (masked and s in R5)]  # R5 subs leave the permutation pool
        sv = np.array([val.get(s, 0) for s, _ in sl], np.int64); pi = {p: j for j, p in enumerate(elig)}
        M = np.zeros((len(sv), len(elig)), np.int64)
        for i, (_, p) in enumerate(sl):
            if p in pi: M[i, pi[p]] = 1
        out.append(dict(khid=khid, sv=sv, M=M, pv=np.array([val[p] for p in elig], np.int64)))
    return out
def corpus(K_, drop=None, KC=10000):
    o = 0; nt = np.zeros(KC, np.int64); ne = 0
    for d in K_:
        if drop and names[d['khid']][0] == drop: continue
        o += int(H(d['sv'][None], d['M'], d['pv'])[0]); ne += len(d['pv'])
        nt += H(np.array([rng.permutation(d['sv']) for _ in range(KC)]), d['M'], d['pv'])
    return dict(n_khipus=len(K_) - (1 if drop else 0), n_eligible=ne, H_obs=o, null_mean=float(nt.mean()), null_max=int(nt.max()), p=pval(o, nt))
Km = build(True)
k004 = dict(masked=corpus(Km), masked_without_KH0349=corpus(Km, 'KH0349'))
d349 = [d for d in Km if names[d['khid']][0] == 'KH0349'][0]
o = int(H(d349['sv'][None], d349['M'], d349['pv'])[0])
k004['KH0349_masked'] = dict(n_eligible=len(d349['pv']), H=o, p=pval(o, H(np.array([rng.permutation(d349['sv']) for _ in range(20000)]), d349['M'], d349['pv'])))
# planted control on masked data: corpus with 10 planted hits in shuffled copies must reach p<=0.01
pl_hits = []
for rep in range(20):
    Kp = []
    for d in Km: Kp.append(dict(khid=d['khid'], sv=rng.permutation(d['sv']), M=d['M'], pv=d['pv'].copy()))
    for j in rng.choice(len(Kp), 10, replace=False):
        d = Kp[j]; col = rng.integers(d['M'].shape[1]); ix = np.where(d['M'][:, col] == 1)[0]
        if len(ix) < 2: continue
        if (d['sv'][ix] > 0).sum() < 2: d['sv'][ix[:2]] = np.maximum(d['sv'][ix[:2]], rng.integers(1, 30, 2))
        d['pv'][col] = d['sv'][ix].sum()
    pl_hits.append(corpus(Kp, KC=2000)['p'])
k004['planted10_power_p01'] = float(np.mean([p <= 0.01 for p in pl_hits]))
cal = [corpus([dict(khid=d['khid'], sv=rng.permutation(d['sv']), M=d['M'], pv=d['pv']) for d in Km], KC=2000)['p'] for _ in range(20)]
k004['calib_fpr_05_of20'] = float(np.mean([p <= 0.05 for p in cal]))
k004['n_r5_cords_total'] = len(R5)
print(json.dumps(k004, indent=1))
json.dump(dict(k001=k001, k004=k004, rows_k001=rows1, seconds=round(time.time() - t0, 1)), open('analysis/k008_results.json', 'w'), indent=1, default=str)
print('seconds', round(time.time() - t0, 1))
