#!/usr/bin/env python3
"""K074 - KFG re-audit step 6 (README line 9): line 6, K021 (colour of sum cords) re-run on Khipu Field Guide data.
Pre-registered in case-file/K074-kfg-sum-cord-colour.md. K021 engine verbatim (tools/k021_sum_cord_colour.py): sum cords =
adjacent-sum hits (value >= 10, k 2..12, >= 2 non-zero summands); eligible = value >= 10 and known colour; null draws the same
number of sum cords uniformly among each khipu's eligible cords (colour sequence untouched), R 20 000; T1 = sum cords whose
colour differs from both neighbours (H1 boundary), T2 = same-colour pairs among sum cords (H2 shared); alpha 0.025 each
(Bonferroni x2); calibration 200 random sets, planted power 200; verdict rule as K021.
KFG colour (primary) = first '/'-segment of `color`, trailing '(a-b)' range removed (the analogue of K021's first-range
FULL_COLOR); sensitivity = same with ':'-components sorted (mottled order ignored), reported only.
Usage: python3 tools/k074_kfg_sum_cord_colour.py data/khipu.db [--smoke]. Seed 6426 (single stream); next free 6427."""
import sqlite3, json, sys, re, hashlib, time, numpy as np
from collections import defaultdict, Counter
T0 = time.time(); KFG_DB = '/workspace/kfg/kfg_20261111.db'
OKR_DB = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'data/khipu.db'
SMOKE = '--smoke' in sys.argv; OUT = 'analysis/k074_smoke.json' if SMOKE else 'analysis/k074_results.json'
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'
OKR_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
R = 300 if SMOKE else 20000; NCAL = 10 if SMOKE else 200; KMAX = 12; SEED = 6426; NEXT_FREE = 6427; ALPHA = 0.025
rng = np.random.default_rng(SEED)
PUB = dict(primary=dict(n_khipus=10, n_sum=95, n_elig=1005, T1=35, T2=416, p1=0.1897, p2=5e-05, verdict_H1='not supported', verdict_H2='supported'),
           secondary=dict(n_khipus=245, n_sum=724, n_elig=10414, T1=290, T2=782, p1=0.1053, p2=5e-05, verdict_H1='not supported', verdict_H2='supported'))
res = dict(design=dict(seed=SEED, next_free_seed=NEXT_FREE, R=R, NCAL=NCAL, alpha=ALPHA, smoke=SMOKE), published_okr=PUB)
def dump(): res['secs'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1)
def stop(r): res['decision'] = dict(excluded=True, reason=r); dump(); print('EXCLUDED:', r); sys.exit(0)
for path, want in ((OKR_DB, OKR_SHA), (KFG_DB, KFG_SHA)):
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    if h != want: stop(f'G0 hash mismatch {path} {h}')
res['G0'] = 'pass'
# ---------------- K021 engine verbatim ----------------
def hits(V):
    n = len(V); P = np.r_[0, np.cumsum(V)]; NZ = np.r_[0, np.cumsum(V > 0)]; h = np.zeros(n, bool)
    for i in range(n):
        if V[i] < 10: continue
        for k in range(2, KMAX + 1):
            if i + k < n and P[i + k + 1] - P[i + 1] == V[i] and NZ[i + k + 1] - NZ[i + 1] >= 2: h[i] = True; break
            if i - k >= 0 and P[i] - P[i - k] == V[i] and NZ[i] - NZ[i - k] >= 2: h[i] = True; break
    return h
def make_units(kh, colof, flag):  # kh: name -> list of (value, colour or None)
    units = []
    for name, L in kh.items():
        V = np.array([v for v, _ in L], np.int64); h = hits(V); C = [colof(x) for _, x in L]; n = len(L)
        elig = [i for i in range(n) if V[i] >= 10 and C[i] is not None]
        if not elig: continue
        obs = np.array([h[i] for i in elig])
        if obs.sum() == 0: continue
        bnd = np.array([all(C[j] != C[i] for j in (i - 1, i + 1) if 0 <= j < n) for i in elig])
        cc = [C[i] for i in elig]; lab = {x: k for k, x in enumerate(sorted(set(cc)))}
        units.append(dict(name=name, m=int(obs.sum()), ne=len(elig), bnd=bnd, cl=np.array([lab[x] for x in cc]), obs=obs, flag=flag(name)))
    return units
def pairs(cl): cnt = np.bincount(cl); return int((cnt * (cnt - 1) // 2).sum())
def stats(us, masks): return sum(int(u['bnd'][mk].sum()) for u, mk in zip(us, masks)), sum(pairs(u['cl'][mk]) for u, mk in zip(us, masks))
def null(us, Rr):
    T1 = np.zeros(Rr, np.int64); T2 = np.zeros(Rr, np.int64)
    for u in us:
        ne, m = u['ne'], u['m']; K = len(np.unique(u['cl'])); idx = np.argsort(rng.random((Rr, ne)), 1)[:, :m]
        T1 += u['bnd'][idx].sum(1); oh = np.zeros((Rr, K), np.int64)
        for j in range(m): np.add.at(oh, (np.arange(Rr), u['cl'][idx[:, j]]), 1)
        T2 += (oh * (oh - 1) // 2).sum(1)
    return T1, T2
def pv(o, nl): return float((1 + (nl >= o).sum()) / (1 + len(nl)))
def run(us, label):
    o1, o2 = stats(us, [u['obs'] for u in us]); N1, N2 = null(us, R)
    out = dict(pop=label, n_khipus=len(us), n_sum=sum(u['m'] for u in us), n_elig=sum(u['ne'] for u in us),
               T1=o1, T1_null_mean=float(N1.mean()), p1=pv(o1, N1), T2=o2, T2_null_mean=float(N2.mean()), p2=pv(o2, N2))
    cal1 = cal2 = pw1 = pw2 = 0
    for _ in range(NCAL):
        mk = [np.isin(np.arange(u['ne']), rng.choice(u['ne'], u['m'], replace=False)) for u in us]
        a, b = stats(us, mk); cal1 += pv(a, N1) <= ALPHA; cal2 += pv(b, N2) <= ALPHA
        m1 = []; m2 = []
        for u, base in zip(us, mk):
            s = list(np.where(base)[0]); s1 = list(s); s2 = list(s)
            free_b = [i for i in np.where(u['bnd'] & ~base)[0]]; rng.shuffle(free_b)
            top = Counter(u['cl'][base]).most_common(1)[0][0]
            free_c = [i for i in np.where((u['cl'] == top) & ~base)[0]]; rng.shuffle(free_c)
            for k in range(len(s)):
                if rng.random() < 0.5 and free_b: s1[k] = free_b.pop()
                if rng.random() < 0.5 and free_c: s2[k] = free_c.pop()
            m1.append(np.isin(np.arange(u['ne']), s1)); m2.append(np.isin(np.arange(u['ne']), s2))
        pw1 += pv(stats(us, m1)[0], N1) <= ALPHA; pw2 += pv(stats(us, m2)[1], N2) <= ALPHA
    out.update(calib_fpr_H1=cal1 / NCAL, calib_fpr_H2=cal2 / NCAL, power_H1=pw1 / NCAL, power_H2=pw2 / NCAL)
    for h in ('1', '2'):
        p, pw, fp = out['p' + h], out['power_H' + h], out['calib_fpr_H' + h]
        out['verdict_H' + h] = ('controls failed' if fp > 0.05 else 'supported' if p <= ALPHA else 'not supported' if pw >= 0.5 else 'not testable')
    return out
# ---------------- OKR (K021 loader verbatim) -> F0 fixture ----------------
c = sqlite3.connect(OKR_DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
okrname = {r[0]: r[1] or '' for r in c.execute("select KHIPU_ID, OKR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
col = {}
for cid, fc, rb, i in c.execute("select CORD_ID, FULL_COLOR, RANGE_BEG, color_id from ascher_cord_color order by CORD_ID, RANGE_BEG, color_id"):
    if cid not in col and fc not in (None, '', "''"): col[cid] = fc.strip()
okr = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: okr[khid].append((val.get(cid, 0), col.get(cid)))
okr_bh = sorted({r['okr'] for r in json.load(open('analysis/k001_results_K5000.json'))['rows'] if r.get('bh_sig_N1')})
ou = make_units(okr, lambda x: x, lambda k: okrname[k] in okr_bh)
f0 = {}
for lab, us in (('primary', [u for u in ou if u['flag']]), ('secondary', ou)):
    o1, o2 = stats(us, [u['obs'] for u in us])
    f0[lab] = (len(us), sum(u['m'] for u in us), sum(u['ne'] for u in us), o1, o2)
res['F0'] = dict(got=f0, want={k: (v['n_khipus'], v['n_sum'], v['n_elig'], v['T1'], v['T2']) for k, v in PUB.items()})
res['F0']['pass'] = all(tuple(res['F0']['got'][k]) == res['F0']['want'][k] for k in PUB); print('F0', res['F0'], flush=True)
if not res['F0']['pass']: stop('F0 engine fixture on OKR failed')
# ---------------- KFG ----------------
k = sqlite3.connect(KFG_DB); PEN = re.compile(r'^p(\d+)$'); RNG = re.compile(r'\([-\d.]+-[-\d.]+\)$')
raw = defaultdict(list)
for kh, nm, v, cl in k.execute('select khipu, cord_name, value, color from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0
    raw[kh].append((int(m.group(1)), x, cl))
kfg, nonseq = {}, []
for kh, L in raw.items():
    if [p for p, _, _ in L] != list(range(1, len(L) + 1)): nonseq.append(kh); continue
    kfg[kh] = [(x, cl) for _, x, cl in L]
def c_prim(s):
    if s is None: return None
    s = RNG.sub('', str(s).split('/')[0].strip()).strip()
    return s or None
def c_sort(s):
    s = c_prim(s); return None if s is None else ':'.join(sorted(s.split(':')))
k069_bh = sorted(r['khipu'] for r in json.load(open('analysis/k069_results.json'))['rows'] if r.get('bh_sig_N1'))
res['data'] = dict(n_kfg_khipus=len(raw), nonseq_excluded=nonseq, okr_bh=okr_bh, okr_bh_present=[x for x in okr_bh if x in kfg], k069_bh=k069_bh)
# GC: colour-coding concordance on khipus whose pendant value vectors are identical in both sources (descriptive)
okr_by = {okrname[kid]: L for kid, L in okr.items() if okrname[kid]}
gc = dict(khipus=0, pendants=0, both_known=0, eq_prim=0, eq_sort=0)
for nm, L in kfg.items():
    o = okr_by.get(nm)
    if not o or len(o) != len(L) or [a for a, _ in o] != [a for a, _ in L]: continue
    gc['khipus'] += 1
    for (_, co), (_, ck) in zip(o, L):
        gc['pendants'] += 1; p = c_prim(ck)
        if co is None or p is None: continue
        gc['both_known'] += 1; gc['eq_prim'] += co == p; gc['eq_sort'] += ':'.join(sorted(co.split(':'))) == c_sort(ck)
gc['rate_prim'] = gc['eq_prim'] / max(1, gc['both_known']); gc['rate_sort'] = gc['eq_sort'] / max(1, gc['both_known'])
res['GC'] = gc; print('GC', gc, flush=True)
if SMOKE:  # smoke = syntax check on colours shuffled within each khipu; no real statistic is seen
    sr = np.random.default_rng(0)
    kfg = {kh: list(zip([a for a, _ in L], [L[i][1] for i in sr.permutation(len(L))])) for kh, L in kfg.items()}
out = {}
for cname, cf in (('primary_coding', c_prim), ('sorted_coding', c_sort)):
    us = make_units(kfg, cf, lambda n: n)
    out[cname] = dict(P1_okr_bh_names=run([u for u in us if u['name'] in okr_bh], 'OKR K001 BH names on KFG'),
                      P2_k069_bh=run([u for u in us if u['name'] in k069_bh], 'K069 KFG BH names'),
                      P3_all=run(us, 'all KFG khipus with a sum cord'))
    print(cname, json.dumps({a: {x: b[x] for x in ('n_khipus', 'n_sum', 'T1', 'T1_null_mean', 'p1', 'T2', 'T2_null_mean', 'p2', 'calib_fpr_H1', 'calib_fpr_H2', 'power_H1', 'power_H2', 'verdict_H1', 'verdict_H2')} for a, b in out[cname].items()}), round(time.time() - T0, 1), flush=True)
res['results'] = out
def rep(kfgv, okrv):
    if kfgv in ('not testable', 'controls failed'): return 'NOT TESTABLE'
    return 'REPLICATED' if kfgv == okrv else 'CHANGED (correction)'
P = out['primary_coding']
res['decision'] = {f'{pop}_{h}': rep(P[key][f'verdict_{h}'], PUB[pub][f'verdict_{h}'])
                   for pop, key, pub in (('primary', 'P1_okr_bh_names', 'primary'), ('secondary', 'P3_all', 'secondary')) for h in ('H1', 'H2')}
print('decision', res['decision']); dump()
