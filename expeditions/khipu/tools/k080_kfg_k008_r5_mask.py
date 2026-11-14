#!/usr/bin/env python3
"""K080 - KFG re-audit of K008 (K001 adjacent sums with multi-number R5 cords masked), pre-registered in
case-file/K080-kfg-k008-r5-mask.md. K001 statistic and loader verbatim from tools/k069_kfg_k001_replication.py;
R5 rule on KFG knots verbatim from tools/k072_kfg_line2_corpus.py (kfg_r5); masking verbatim from tools/k008_multinumber_sensitivity.py
(an R5 pendant is never a sum target, never inside a summand block, keeps its position; the null permutes only non-R5 values
among non-R5 positions). Seeds: 6449 (masked nulls), 6450 (calibration). Next free 6451.
Usage: python3 tools/k080_kfg_k008_r5_mask.py [--fixture]"""
import sqlite3, json, sys, re, glob, hashlib, time
import numpy as np
from collections import defaultdict
T0 = time.time(); FIXTURE = '--fixture' in sys.argv
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
K = 5000; KC = 2000; KMAX = 12; MINP = 10; OUT = 'analysis/k080_results.json'
rng = np.random.default_rng(6449); rngc = np.random.default_rng(6450)
k69 = json.load(open('analysis/k069_results.json')); k69rows = {r['khipu']: r for r in k69['rows']}
K69_BH = sorted(r['khipu'] for r in k69['rows'] if r['bh_sig_N1'])
k8 = json.load(open('analysis/k008_results.json'))['k001']
OKR_K008 = {r['okr']: ('SURVIVES' if r['bh_masked'] else 'DROPS') for r in k8['old_sig_rows']}
def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
c = sqlite3.connect(KFG_DB); sha = dict(c.execute('select name, sha256 from khipu'))
PEN = re.compile(r'^p(\d+)$'); CLU = re.compile(r'^(\d+)([A-Z]+)\(([-\d.]+),[^)]*\),(-?\d+)$')
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
pend = defaultdict(list)
for kh, idx, nm, v, kn in c.execute('select khipu, idx, cord_name, value, knots from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0
    pend[kh].append((int(m.group(1)), x, kfg_r5(kn)))
g0_bad = [f.split('/')[-1][:-5] for f in sorted(glob.glob(f'{XLSX}/*.xlsx'))
          if hashlib.sha256(open(f, 'rb').read()).hexdigest() != sha.get(f.split('/')[-1][:-5])]
def S_batch(V, bad):
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    BD = np.zeros(n + 1, np.int64); BD[1:] = np.cumsum(bad)
    hit = np.zeros((B, n), bool); idx = np.arange(n)
    for k in range(2, KMAX + 1):
        i = idx[idx + k < n]; ok = (BD[i + k + 1] - BD[i + 1]) == 0
        s = P[:, i + k + 1] - P[:, i + 1]; z = NZ[:, i + k + 1] - NZ[:, i + 1]
        hit[:, i] |= (s == V[:, i]) & (z >= 2) & ok
        i = idx[idx - k >= 0]; ok = (BD[i] - BD[i - k]) == 0
        s = P[:, i] - P[:, i - k]; z = NZ[:, i] - NZ[:, i - k]
        hit[:, i] |= (s == V[:, i]) & (z >= 2) & ok
    hit &= (V >= 10) & ~bad
    return hit.sum(1)
def permmask(g, v, bad, B):
    free = np.where(~bad)[0]; out = np.tile(v, (B, 1))
    for b in range(B): out[b, free] = g.permutation(v[free])
    return out
def pval(o, n): return (1 + (n >= o).sum()) / (1 + len(n))
def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps)
    if m == 0: return np.zeros(0, bool)
    o = np.argsort(ps); thr = q * np.arange(1, m + 1) / m
    ok = ps[o] <= thr; kk = np.max(np.where(ok)[0]) + 1 if ok.any() else 0
    s = np.zeros(m, bool); s[o[:kk]] = True; return s
# ---- F0: with an all-false mask, S equals K069's S_obs for every K069 row (exact); universe equals K069's ----
f0_bad = []; univ = []
for kh in sorted(pend):
    if kh in g0_bad: continue
    v = np.array([x for _, x, _ in pend[kh]], np.int64)
    if (v > 0).sum() < MINP: continue
    univ.append(kh)
    if kh not in k69rows or int(S_batch(v[None], np.zeros(len(v), bool))[0]) != k69rows[kh]['S_obs']: f0_bad.append(kh)
F0 = dict(n_universe=len(univ), n_k069=len(k69rows), mismatches=f0_bad, pass_=(not f0_bad and len(univ) == len(k69rows)))
r5_total = int(sum(b for kh in univ for _, _, b in pend[kh])); n_with = sum(any(b for _, _, b in pend[kh]) for kh in univ)
print('F0', F0, 'R5 pendants', r5_total, 'khipus with R5', n_with, 'G0 bad', len(g0_bad), round(time.time() - T0, 1), flush=True)
fx = dict(F0=F0, G0_hash_mismatch=len(g0_bad), r5_pendants=r5_total, khipus_with_r5=n_with,
          targets={n: dict(n_pend=len(pend[n]), n_r5=int(sum(b for _, _, b in pend[n])),
                           nonR5_nonzero=int(sum((x > 0) and not b for _, x, b in pend[n]))) for n in K69_BH})
if FIXTURE: print(json.dumps(fx, indent=1)); sys.exit()
if not F0['pass_'] or g0_bad: json.dump(dict(fixture=fx, verdict='GATES FAIL'), open(OUT, 'w'), indent=1); sys.exit('gate fail')
rows = []
for kh in univ:
    v = np.array([x for _, x, _ in pend[kh]], np.int64); bad = np.array([b for _, _, b in pend[kh]])
    nb = int(bad.sum())
    if ((v > 0) & ~bad).sum() < MINP: rows.append(dict(khipu=kh, n_r5=nb, testable=False)); continue
    obs = int(S_batch(v[None], bad)[0]); pc = None
    if nb == 0: p = k69rows[kh]['p_N1']
    else:
        p = pval(obs, S_batch(permmask(rng, v, bad, K), bad))
        fake = permmask(rngc, v, bad, 1)[0]; pc = pval(int(S_batch(fake[None], bad)[0]), S_batch(permmask(rngc, fake, bad, KC), bad))
    rows.append(dict(khipu=kh, n_pend=len(v), n_r5=nb, testable=True, S_unmasked=k69rows[kh]['S_obs'], S_masked=obs,
                     p_unmasked=k69rows[kh]['p_N1'], p_masked=p, p_calib=pc, bh_unmasked=k69rows[kh]['bh_sig_N1']))
T = [r for r in rows if r['testable']]; sig = bh([r['p_masked'] for r in T])
for r, s in zip(T, sig): r['bh_masked'] = bool(s)
by = {r['khipu']: r for r in rows}
cal = np.array([r['p_calib'] for r in T if r['p_calib'] is not None]); ncal = len(cal); kcal = int((cal <= 0.05).sum())
from math import comb
tail = sum(comb(ncal, j) * 0.05 ** j * 0.95 ** (ncal - j) for j in range(kcal, ncal + 1))
G2 = dict(n=ncal, n_le_05=kcal, rate=kcal / max(1, ncal), binom_tail=tail, pass_=tail >= 0.01)
def lab(n):
    r = by.get(n)
    if r is None or not r['testable']: return 'NOT TESTABLE', None
    return ('SURVIVES' if r['bh_masked'] else 'DROPS'), r
R1 = {}
for n in sorted(OKR_K008):
    st, r = lab(n)
    R1[n] = dict(okr_k008=OKR_K008[n], kfg=st, label=('NOT TESTABLE' if st == 'NOT TESTABLE' else 'REPLICATED' if st == OKR_K008[n] else 'CHANGED'),
                 **({k: r[k] for k in ('n_r5', 'S_unmasked', 'S_masked', 'p_unmasked', 'p_masked')} if r else {}))
R2 = {}
for n in K69_BH:
    if n in OKR_K008: continue
    st, r = lab(n); R2[n] = dict(kfg=st, **({k: r[k] for k in ('n_r5', 'S_unmasked', 'S_masked', 'p_unmasked', 'p_masked')} if r else {}))
headline = 'GATES FAIL' if not G2['pass_'] else ('REPLICATED' if all(x['label'] == 'REPLICATED' for x in R1.values()) else 'CORRECTION')
summ = dict(seeds=[6449, 6450], next_free_seed=6451, K=K, KC=KC, fixture=fx, G2_calibration=G2, n_testable=len(T), n_untestable=len(rows) - len(T),
            n_bh_masked=int(sig.sum()), R1_okr_k008_names=R1, R2_new_k069_names=R2,
            kfg_survivors_of_okr10=sorted(n for n, x in R1.items() if x['kfg'] == 'SURVIVES'),
            new_masked_bh_not_in_k069=sorted(r['khipu'] for r in T if r['bh_masked'] and r['khipu'] not in K69_BH),
            headline=headline, seconds=round(time.time() - T0, 1))
json.dump(dict(summary=summ, rows=rows), open(OUT, 'w'), indent=1)
print(json.dumps({k: v for k, v in summ.items() if k != 'fixture'}, indent=1))
