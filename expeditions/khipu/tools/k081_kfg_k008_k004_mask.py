#!/usr/bin/env python3
"""K081 - KFG re-audit step 13: K008's K004 arm (pendant = sum of its own subsidiaries, with multi-number R5 cords masked),
pre-registered in case-file/K081-kfg-k008-k004-mask.md. Loader/hierarchy/values/H verbatim from tools/k070_kfg_k004_replication.py;
R5 rule on KFG knots verbatim from tools/k080_kfg_k008_r5_mask.py (kfg_r5, from K072); masking verbatim from
tools/k008_multinumber_sensitivity.py build(masked=True): an R5 pendant is never an eligible parent, a parent with any R5
direct subsidiary is ineligible, and R5 subsidiaries leave the permutation pool. Seeds: 6451 (masked nulls), 6452 (calibration
and planted controls). Next free 6453.
Usage: python3 tools/k081_kfg_k008_k004_mask.py [--fixture]"""
import sqlite3, json, sys, re, glob, hashlib, time
import numpy as np
from collections import defaultdict
T0 = time.time(); FIXTURE = '--fixture' in sys.argv
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'; OUT = 'analysis/k081_results.json'
rng = np.random.default_rng(6451); rngc = np.random.default_rng(6452)
k70 = json.load(open('analysis/k070_results.json'))['summary']
def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
CLU = re.compile(r'^(\d+)([A-Z]+)\(([-\d.]+),[^)]*\),(-?\d+)$')
def kfg_r5(knots):
    cls = []
    for j, t in enumerate(str(knots or '').split(';')):
        m = CLU.match(t.strip())
        if not m: continue
        typ, pos, v = m.group(2), float(m.group(3)), int(m.group(4))
        if v == 0 or typ[0] not in 'SLE': continue
        cls.append((pos, j, place(v) if typ[0] == 'S' else 0))
    s = [p for _, _, p in sorted(cls)]
    return len(s) >= 2 and not all(a > b for a, b in zip(s, s[1:]))
c = sqlite3.connect(KFG_DB); sha = dict(c.execute('select name, sha256 from khipu'))
g0_bad = [f.split('/')[-1][:-5] for f in sorted(glob.glob(f'{XLSX}/*.xlsx'))
          if hashlib.sha256(open(f, 'rb').read()).hexdigest() != sha.get(f.split('/')[-1][:-5])]
P1 = re.compile(r'^p(\d+)$'); P2 = re.compile(r'^p(\d+)s(\d+)$')
lv1 = defaultdict(dict); r5p = defaultdict(set); subs = defaultdict(list)
for kh, nm, v, kn in c.execute('select khipu, cord_name, value, knots from cord order by khipu, idx'):
    if kh in g0_bad: continue
    x = int(float(v)) if v not in (None, '') else 0; nm = str(nm or '')
    m = P1.match(nm)
    if m:
        lv1[kh][int(m.group(1))] = x
        if kfg_r5(kn): r5p[kh].add(int(m.group(1)))
        continue
    m = P2.match(nm)
    if m: subs[kh].append((int(m.group(1)), x, kfg_r5(kn)))
def build(masked):
    out = []
    for kh in sorted(subs):
        pars = [p for p, _, _ in subs[kh]]
        badpar = {p for p, _, b in subs[kh] if b} if masked else set()
        elig = sorted({p for p in pars if lv1[kh].get(p, 0) >= 10 and pars.count(p) >= 2
                       and not (masked and (p in r5p[kh] or p in badpar))})
        if not elig: continue
        sl = [(p, x) for p, x, b in subs[kh] if not (masked and b)]
        sv = np.array([x for _, x in sl], np.int64); pi = {p: j for j, p in enumerate(elig)}
        M = np.zeros((len(sv), len(elig)), np.int64)
        for i, (p, _) in enumerate(sl):
            if p in pi: M[i, pi[p]] = 1
        out.append(dict(kh=kh, sv=sv, M=M, pv=np.array([lv1[kh][p] for p in elig], np.int64)))
    return out
def H(S, M, P):
    return (((S @ M) == P) & (((S > 0).astype(np.int64) @ M) >= 2)).sum(1)
def pval(o, n): return (1 + (n >= o).sum()) / (1 + len(n))
def corpus(D, KC, g):
    o = 0; ne = 0; nt = np.zeros(KC, np.int64)
    for d in D:
        o += int(H(d['sv'][None], d['M'], d['pv'])[0]); ne += len(d['pv'])
        nt += H(np.array([g.permutation(d['sv']) for _ in range(KC)]), d['M'], d['pv'])
    return dict(n_khipus=len(D), n_eligible=ne, H_obs=o, null_mean=float(nt.mean()), null_max=int(nt.max()), p=pval(o, nt))
def obs(D): return dict(n_khipus=len(D), n_eligible=int(sum(len(d['pv']) for d in D)), H_obs=int(sum(int(H(d['sv'][None], d['M'], d['pv'])[0]) for d in D)))
# ---- F0: empty mask reproduces K070's T1 and T3 observed counts and KH0349's 13/82 exactly ----
K0 = build(False); f1 = obs(K0); f3 = obs([d for d in K0 if d['kh'] != 'KH0349'])
d0 = next(d for d in K0 if d['kh'] == 'KH0349'); f349 = (len(d0['pv']), int(H(d0['sv'][None], d0['M'], d0['pv'])[0]))
F0 = dict(T1=f1, T3=f3, KH0349=f349,
          pass_=(f1 == {k: k70['T1'][k] for k in ('n_khipus', 'n_eligible', 'H_obs')} and f3 == {k: k70['T3'][k] for k in ('n_khipus', 'n_eligible', 'H_obs')}
                 and f349 == (k70['KH0349']['n_eligible'], k70['KH0349']['H'])))
nr5 = dict(pendants=int(sum(len(s) for s in r5p.values())), subsidiaries=int(sum(b for kh in subs for _, _, b in subs[kh])))
print('F0', F0, 'R5', nr5, 'G0 bad', len(g0_bad), round(time.time() - T0, 1), flush=True)
if FIXTURE: sys.exit()
if not F0['pass_'] or g0_bad: json.dump(dict(F0=F0, G0_bad=g0_bad, headline='GATES FAIL'), open(OUT, 'w'), indent=1, default=str); sys.exit('gate fail')
# ---- registered tests ----
Km = build(True)
M1 = corpus(Km, 10000, rng); print('M1', M1, flush=True)
M2 = corpus([d for d in Km if d['kh'] != 'KH0349'], 10000, rng); print('M2', M2, flush=True)
def single(name, KC=20000):
    d = next((d for d in Km if d['kh'] == name), None)
    if d is None: return dict(eligible_after_mask=False)
    o = int(H(d['sv'][None], d['M'], d['pv'])[0])
    return dict(eligible_after_mask=True, n_eligible=len(d['pv']), H=o, p=pval(o, H(np.array([rng.permutation(d['sv']) for _ in range(KC)]), d['M'], d['pv'])))
M3 = single('KH0349'); print('M3', M3, flush=True)
D276 = single('KH0276'); print('KH0276', D276, flush=True)
# ---- G2 calibration (20 shuffled masked corpora, K 2000) and G3 planted power (20 x 10 planted hits, K 2000), K008 verbatim ----
cal = [corpus([dict(kh=d['kh'], sv=rngc.permutation(d['sv']), M=d['M'], pv=d['pv']) for d in Km], 2000, rngc)['p'] for _ in range(20)]
kcal = int(sum(p <= 0.05 for p in cal))
from math import comb
tail = sum(comb(20, j) * 0.05 ** j * 0.95 ** (20 - j) for j in range(kcal, 21))
G2 = dict(n=20, n_le_05=kcal, binom_tail=tail, pass_=tail >= 0.01)
pl = []
for rep in range(20):
    Kp = [dict(kh=d['kh'], sv=rngc.permutation(d['sv']), M=d['M'], pv=d['pv'].copy()) for d in Km]
    for j in rngc.choice(len(Kp), 10, replace=False):
        d = Kp[j]; col = rngc.integers(d['M'].shape[1]); ix = np.where(d['M'][:, col] == 1)[0]
        if len(ix) < 2: continue
        if (d['sv'][ix] > 0).sum() < 2: d['sv'][ix[:2]] = np.maximum(d['sv'][ix[:2]], rngc.integers(1, 30, 2))
        d['pv'][col] = d['sv'][ix].sum()
    pl.append(corpus(Kp, 2000, rngc)['p'])
G3 = dict(power_p01=float(np.mean([p <= 0.01 for p in pl])), readable=float(np.mean([p <= 0.01 for p in pl])) >= 0.8)
print('G2', G2, 'G3', G3, round(time.time() - T0, 1), flush=True)
# ---- decisions (K008 rules verbatim, labels vs OKR K008) ----
def lab(p, okr_ok=True):
    if p <= 0.01: return 'REPLICATED' if okr_ok else 'CHANGED'
    return ('CHANGED' if G3['readable'] else 'NOT TESTABLE') if okr_ok else 'REPLICATED'
L1 = lab(M1['p']); L2 = 'REPLICATED' if M2['p'] <= 0.01 else 'CHANGED'
L3 = 'NOT TESTABLE' if not M3.get('eligible_after_mask') else lab(M3['p'])
ps = [M1['p'], M2['p'], M3.get('p', 1.0)]; o = np.argsort(ps); holm = [False] * 3
for r, i in enumerate(o):
    if ps[i] <= 0.01 / (3 - r): holm[i] = True
    else: break
holm_agrees = holm == [p <= 0.01 for p in ps]
head = 'GATES FAIL' if not G2['pass_'] else 'REPLICATED' if (L1, L2, L3) == ('REPLICATED',) * 3 else 'CORRECTION' if 'CHANGED' in (L1, L2, L3) else 'PARTLY NOT TESTABLE'
summ = dict(seeds=[6451, 6452], next_free_seed=6453, G0_hash_mismatch=len(g0_bad), F0=F0, r5_counts=nr5, M1_masked_corpus=M1, M2_masked_without_KH0349=M2,
            M3_KH0349_masked=M3, KH0276_masked_descriptive=D276, G2_calibration=G2, G2_cal_ps=cal, G3_planted=G3, G3_ps=pl,
            labels=dict(M1=L1, M2=L2, M3=L3), holm_alpha01=holm, holm_agrees_with_raw=holm_agrees, headline=head, seconds=round(time.time() - T0, 1))
json.dump(summ, open(OUT, 'w'), indent=1, default=str)
print(json.dumps({k: v for k, v in summ.items() if k not in ('G2_cal_ps', 'G3_ps')}, indent=1, default=str))
