#!/usr/bin/env python3
"""K070 - KFG re-audit of K004 (pendant = sum of its own subsidiaries), pre-registered in case-file/K070-kfg-replication-k004.md.
Usage: python3 tools/k070_kfg_k004_replication.py data/khipu.db [out.json]. Seed 6418 (next free 6419)."""
import sqlite3, json, sys, re, glob, hashlib, time, numpy as np
from collections import defaultdict
T0 = time.time(); KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
OKR_DB = sys.argv[1] if len(sys.argv) > 1 else 'data/khipu.db'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'analysis/k070_results.json'
rng = np.random.default_rng(6418)
okr = {r[0] for r in sqlite3.connect(OKR_DB).execute('select OKR_NUM from khipu_main') if r[0]}
c = sqlite3.connect(KFG_DB); sha = dict(c.execute('select name, sha256 from khipu'))
g0_bad = [f.split('/')[-1][:-5] for f in sorted(glob.glob(f'{XLSX}/*.xlsx'))
          if hashlib.sha256(open(f, 'rb').read()).hexdigest() != sha.get(f.split('/')[-1][:-5])]
P1 = re.compile(r'^p(\d+)$'); P2 = re.compile(r'^p(\d+)s(\d+)$')
lv1 = defaultdict(dict); subs = defaultdict(list)
for kh, nm, v in c.execute('select khipu, cord_name, value from cord order by khipu, idx'):
    if kh in g0_bad: continue
    x = int(float(v)) if v not in (None, '') else 0; nm = str(nm or '')
    m = P1.match(nm)
    if m: lv1[kh][int(m.group(1))] = x; continue
    m = P2.match(nm)
    if m: subs[kh].append((int(m.group(1)), x))
K_ = []
for kh in sorted(subs):
    sv = np.array([x for _, x in subs[kh]], np.int64); pars = [p for p, _ in subs[kh]]
    elig = sorted({p for p in pars if lv1[kh].get(p, 0) >= 10 and pars.count(p) >= 2})
    if not elig: continue
    pi = {p: j for j, p in enumerate(elig)}; M = np.zeros((len(sv), len(elig)), np.int64)
    for i, p in enumerate(pars):
        if p in pi: M[i, pi[p]] = 1
    K_.append(dict(kh=kh, sv=sv, M=M, pv=np.array([lv1[kh][p] for p in elig], np.int64), heldout=kh not in okr))
def H(S, M, P):
    return (((S @ M) == P) & (((S > 0).astype(np.int64) @ M) >= 2)).sum(1)
def permS(sv, B): return np.array([rng.permutation(sv) for _ in range(B)])
def pval(o, n): return (1 + (n >= o).sum()) / (1 + len(n))
def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps); o = np.argsort(ps); thr = q * np.arange(1, m + 1) / m
    ok = ps[o] <= thr; kk = np.max(np.where(ok)[0]) + 1 if ok.any() else 0
    s = np.zeros(m, bool); s[o[:kk]] = True; return s
def corpus(D, KC, nb=False):
    o = sum(int(H(d['sv'][None], d['M'], d['pv'])[0]) for d in D); na = np.zeros(KC, np.int64); nbt = np.zeros(KC, np.int64)
    for d in D:
        na += H(permS(d['sv'], KC), d['M'], d['pv'])
        if nb: nbt += H(d['sv'][None], d['M'], np.array([rng.permutation(d['pv']) for _ in range(KC)]))
    r = dict(n_khipus=len(D), n_eligible=int(sum(len(d['pv']) for d in D)), H_obs=o, Na_mean=float(na.mean()), Na_max=int(na.max()), p_Na=pval(o, na))
    if nb: r.update(Nb_mean=float(nbt.mean()), Nb_max=int(nbt.max()), p_Nb=pval(o, nbt))
    return r
T1 = corpus(K_, 10000, nb=True); print('T1', T1, round(time.time() - T0, 1), flush=True)
rows = []
for d in K_:
    if len(d['pv']) < 3: continue
    sv, M, pv_ = d['sv'], d['M'], d['pv']
    o = int(H(sv[None], M, pv_)[0]); p1 = pval(o, H(permS(sv, 2000), M, pv_)); p = p1
    if p1 <= 0.01: p = pval(o, H(permS(sv, 20000), M, pv_))
    pb = pval(o, H(sv[None], M, np.array([rng.permutation(pv_) for _ in range(2000)])))
    fake = rng.permutation(sv); pc = pval(int(H(fake[None], M, pv_)[0]), H(permS(fake, 2000), M, pv_))
    pl = rng.permutation(sv).copy(); pp = pv_.copy()
    for j in rng.choice(len(pv_), 2, replace=False):
        ix = np.where(M[:, j] == 1)[0]
        if (pl[ix] > 0).sum() < 2: pl[ix[:2]] = np.maximum(pl[ix[:2]], rng.integers(1, 30, 2))
        pp[j] = pl[ix].sum()
    ppl = pval(int(H(pl[None], M, pp)[0]), H(permS(pl, 2000), M, pp))
    rows.append(dict(khipu=d['kh'], heldout=d['heldout'], n_eligible=len(pv_), n_subs=len(sv), H=o, p_Na=p, p_Na_stage1=p1, p_Nb=pb, p_calib=pc, p_planted=ppl))
sig = bh([r['p_Na'] for r in rows])
for r, s in zip(rows, sig): r['bh_sig'] = bool(s)
ne = np.array([r['n_eligible'] for r in rows]); ppl = np.array([r['p_planted'] for r in rows]); calib = np.array([r['p_calib'] for r in rows])
T2 = dict(n_tested=len(rows), calib_fpr_05=float((calib <= 0.05).mean()), planted_recovery_05=float((ppl <= 0.05).mean()),
          planted_by_eligible={f'{a}-{b}': float((ppl[(ne >= a) & (ne <= b)] <= 0.05).mean()) if ((ne >= a) & (ne <= b)).any() else None
                               for a, b in ((3, 5), (6, 10), (11, 20), (21, 10**6))},
          n_bh=int(sig.sum()), bh_names=sorted(r['khipu'] for r in rows if r['bh_sig']))
print('T2', T2, round(time.time() - T0, 1), flush=True)
T3 = corpus([d for d in K_ if d['kh'] != 'KH0349'], 10000); print('T3', T3, flush=True)
HO = [d for d in K_ if d['heldout']]; T4 = corpus(HO, 10000) if HO else dict(n_khipus=0)
e = (12 - 5.97) / (1315 - 82); m_pl = int(round(e * T4.get('n_eligible', 0))); hits = []
if HO and m_pl >= 1:
    slots = [(i, j) for i, d in enumerate(HO) for j in range(len(d['pv']))]
    for _ in range(200):
        Dp = [dict(sv=rng.permutation(d['sv']), M=d['M'], pv=d['pv'].copy()) for d in HO]
        for k in rng.choice(len(slots), m_pl, replace=False):
            i, j = slots[k]; d = Dp[i]; ix = np.where(d['M'][:, j] == 1)[0]
            if (d['sv'][ix] > 0).sum() < 2: d['sv'][ix[:2]] = np.maximum(d['sv'][ix[:2]], rng.integers(1, 30, 2))
            d['pv'][j] = d['sv'][ix].sum()
        hits.append(corpus(Dp, 1000)['p_Na'] <= 0.05)
T4.update(excess_rate=e, m_planted=m_pl, power_05=float(np.mean(hits)) if hits else 0.0, heldout_names=[d['kh'] for d in HO])
print('T4', {k: v for k, v in T4.items() if k != 'heldout_names'}, round(time.time() - T0, 1), flush=True)
# decisions
k069 = set(json.load(open('analysis/k069_results.json'))['summary'].get('okr_k001_bh', [])) | set(json.load(open('analysis/k069_results.json'))['summary'].get('new_kfg_bh_names', []))
ur = next((r for r in rows if r['khipu'] == 'KH0349'), None)
R1 = 'REPLICATED' if T1['p_Na'] <= 0.01 else 'NOT REPLICATED'
R2 = 'NOT TESTABLE' if ur is None else 'REPLICATED' if ur['bh_sig'] else 'WEAKENED' if ur['p_Na'] <= 0.05 else 'NOT REPLICATED'
nrep = (R1 == 'REPLICATED') + (R2 == 'REPLICATED'); head = ['NOT REPLICATED', 'CHANGED', 'REPLICATED'][nrep]
R3 = 'NOT TESTABLE (data-limited)' if T4['power_05'] < 0.5 else 'established on held-out data' if T4['p_Na'] <= 0.01 else 'suggestive' if T4['p_Na'] <= 0.05 else 'not replicated (powered negative)'
gates = dict(G0_hash_mismatch=len(g0_bad), G2_calib_fpr=T2['calib_fpr_05'], G2_pass=T2['calib_fpr_05'] <= 0.05)
if not (gates['G2_pass'] and not g0_bad): head = 'GATES FAIL'
summary = dict(seed=6418, next_free_seed=6419, gates=gates, T1=T1, T2=T2, T3=T3, T4=T4, KH0349=ur, R1=R1, R2=R2, headline=head, R3=R3,
               overlap_with_k069=sorted(set(T2['bh_names']) & k069), seconds=round(time.time() - T0, 1))
json.dump(dict(summary=summary, rows=rows), open(OUT, 'w'), indent=1); print(json.dumps({k: v for k, v in summary.items() if k not in ('T4',)}, indent=1, default=str))
