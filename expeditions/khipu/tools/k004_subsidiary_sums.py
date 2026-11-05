#!/usr/bin/env python3
"""K004 - pendant = sum of its own subsidiaries? Pre-registered in case-file/K004-subsidiary-sums.md.
Usage: python3 tools/k004_subsidiary_sums.py data/khipu.db"""
import sqlite3, json, sys, time, numpy as np
from collections import defaultdict
t0 = time.time(); c = sqlite3.connect(sys.argv[1]); rng = np.random.default_rng(8008)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
lvl1 = {}; subs = defaultdict(list)
for khid, cid, lev, par in c.execute("select KHIPU_ID, CORD_ID, CORD_LEVEL, PENDANT_FROM from cord order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups: continue
    if lev == 1: lvl1[cid] = khid
    elif lev == 2: subs[khid].append((cid, par))
K_ = []
for khid in sorted({k for k in subs}):
    sv = np.array([val.get(s, 0) for s, _ in subs[khid]], np.int64); pars = [p for _, p in subs[khid]]
    elig = sorted({p for p in pars if p in lvl1 and lvl1[p] == khid and val.get(p, 0) >= 10 and pars.count(p) >= 2})
    if not elig: continue
    pi = {p: j for j, p in enumerate(elig)}
    M = np.zeros((len(sv), len(elig)), np.int64)
    for i, p in enumerate(pars):
        if p in pi: M[i, pi[p]] = 1
    pv_ = np.array([val[p] for p in elig], np.int64)
    K_.append(dict(khid=khid, sv=sv, M=M, pv=pv_))

def H(S, M, P):  # S (B,m) sub values, P (B,e) or (e,) parent values -> (B,)
    tot = S @ M; nz = (S > 0).astype(np.int64) @ M
    return ((tot == P) & (nz >= 2)).sum(1)
def permS(sv, B): return np.array([rng.permutation(sv) for _ in range(B)])
def pval(o, n): return (1 + (n >= o).sum()) / (1 + len(n))
def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps); o = np.argsort(ps); thr = q * np.arange(1, m + 1) / m
    ok = ps[o] <= thr; kk = np.max(np.where(ok)[0]) + 1 if ok.any() else 0
    s = np.zeros(m, bool); s[o[:kk]] = True; return s

# (1) corpus test
KC = 10000; obs_tot = 0; null_tot = np.zeros(KC, np.int64); nullb_tot = np.zeros(KC, np.int64); n_elig = 0
for d in K_:
    obs_tot += int(H(d['sv'][None], d['M'], d['pv'])[0]); n_elig += len(d['pv'])
    null_tot += H(permS(d['sv'], KC), d['M'], d['pv'])
    nullb_tot += H(d['sv'][None], d['M'], np.array([rng.permutation(d['pv']) for _ in range(KC)]))
corpus = dict(n_khipus_with_eligible=len(K_), n_eligible_parents=n_elig, H_obs=obs_tot,
              Na_null_mean=float(null_tot.mean()), Na_null_max=int(null_tot.max()), p_Na=pval(obs_tot, null_tot),
              Nb_null_mean=float(nullb_tot.mean()), Nb_null_max=int(nullb_tot.max()), p_Nb=pval(obs_tot, nullb_tot))
print(json.dumps(corpus, indent=1), round(time.time() - t0, 1), flush=True)
# (2) per khipu
rows = []
for d in K_:
    if len(d['pv']) < 3: continue
    sv, M, pv_ = d['sv'], d['M'], d['pv']
    o = int(H(sv[None], M, pv_)[0]); p1 = pval(o, H(permS(sv, 2000), M, pv_)); p = p1
    if p1 <= 0.01: p = pval(o, H(permS(sv, 20000), M, pv_))
    pb = pval(o, H(sv[None], M, np.array([rng.permutation(pv_) for _ in range(2000)])))
    fake = rng.permutation(sv); pc = pval(int(H(fake[None], M, pv_)[0]), H(permS(fake, 2000), M, pv_))
    # planted: two eligible parents := sum of their subs in a shuffled copy
    pl = rng.permutation(sv).copy(); pp = pv_.copy()
    for j in rng.choice(len(pv_), 2, replace=False):
        ix = np.where(M[:, j] == 1)[0]
        if (pl[ix] > 0).sum() < 2: pl[ix[:2]] = np.maximum(pl[ix[:2]], rng.integers(1, 30, 2))
        pp[j] = pl[ix].sum()
    ppl = pval(int(H(pl[None], M, pp)[0]), H(permS(pl, 2000), M, pp))
    rows.append(dict(khipu_id=d['khid'], okr=names[d['khid']][0], inv=names[d['khid']][1], n_eligible=len(pv_),
                     n_subs=len(sv), H=o, null_mean=None, p_Na=p, p_Na_stage1=p1, p_Nb=pb, p_calib=pc, p_planted=ppl))
sig = bh([r['p_Na'] for r in rows])
for r, s in zip(rows, sig): r['bh_sig'] = bool(s)
k3 = {r['khipu_id'] for r in json.load(open('analysis/k003_corpus.json'))['rows'] if r['bh_sig']}
fl = {r['khipu_id'] for r in rows if r['bh_sig']}
ne = np.array([r['n_eligible'] for r in rows]); pp = np.array([r['p_planted'] for r in rows])
per = dict(n_tested=len(rows), calib_fpr_05=float(np.mean([r['p_calib'] <= 0.05 for r in rows])),
           planted_recovery_05=float((pp <= 0.05).mean()),
           planted_recovery_by_eligible={f'{a}-{b}': float((pp[(ne >= a) & (ne <= b)] <= 0.05).mean()) if ((ne >= a) & (ne <= b)).any() else None
                                          for a, b in ((3, 5), (6, 10), (11, 20), (21, 10**6))},
           n_bh=int(sig.sum()), overlap_with_k003=len(fl & k3), k003_n=len(k3),
           series_of_bh=sorted(r['inv'] for r in rows if r['bh_sig']))
out = dict(corpus=corpus, per_khipu=per, rows=rows, seconds=round(time.time() - t0, 1))
json.dump(out, open('analysis/k004_results.json', 'w'), indent=1); print(json.dumps(per, indent=1))
for r in sorted(rows, key=lambda r: r['p_Na'])[:20]: print(r['okr'], r['inv'], r['n_eligible'], r['H'], r['p_Na'], r['p_Nb'], r['bh_sig'])
