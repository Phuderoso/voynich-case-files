#!/usr/bin/env python3
"""K083 - KFG re-audit of line 4: K007 decoding rules (R1 E, R2 L, R3 S, R5 multi-number, R7 multiplicity) and
K026 concentration (H1, G by khipu and series) + field classification (H2) of the E/L violations, on KFG tokens.
Pre-registered in case-file/K083-kfg-k007-k026-decoding.md BEFORE any rate, G or category count on the real data.
KFG unit = one knot token 'nT(pos,dir),v' (a cluster of n knots of one type T). Types S/L/E audited; EE LL BL SP TF U
counted as not auditable (OKR 'unknown_type' analogue). R4/R6 not testable (single-type tokens), R8 not comparable.
Usage (from expeditions/khipu):  python3 tools/k083_kfg_k007_k026_decoding.py {fixture|all}"""
import sqlite3, sys, json, re, hashlib, time
import numpy as np
from collections import Counter, defaultdict
from math import lgamma, exp, log
MODE = sys.argv[1] if len(sys.argv) > 1 else 'fixture'
KFG_DB = '/workspace/kfg/kfg_20261111.db'
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'
SEED_H1 = 6460; SEED_POW = 6461; SEED_PLANT = 6462; NEXT_FREE = 6463
R = 10000; NPOW = 100
OKR = dict(R1=(89, 8356), R2=(490, 21893), R3=(31, 75055), R7=(2749, 90956))  # K007 analysis/k007_results.json
K007_R5_PENDANT_SHARE = 0.097
K026_CATS = {'L-turn0': 186, 'L-turn10+': 155, 'L-shift': 117, 'E-type': 43, 'E-zero': 22}  # noteworthy (n >= 20)
TOK = re.compile(r'^(\d+)([A-Z]+)\(([-\d.]+),[^)]*\),(-?\d+)')
PEN = re.compile(r'^p(\d+)$'); CLU = re.compile(r'^(\d+)([A-Z]+)\(([-\d.]+),[^)]*\),(-?\d+)$')
def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
def kfg_r5(knots):  # verbatim from K080/K082
    cls = []
    for j, t in enumerate(str(knots or '').split(';')):
        m = CLU.match(t.strip())
        if not m: continue
        typ, pos, v = m.group(2), float(m.group(3)), int(m.group(4))
        if v == 0 or typ[0] not in 'SLE': continue
        cls.append((pos, j, place(v) if typ[0] == 'S' else 0))
    s = [p for _, _, p in sorted(cls)]
    return len(s) >= 2 and not all(a > b for a, b in zip(s, s[1:]))
def n_pow10(n, v):  # v == n * 10^p for some p >= 0
    if n < 1 or v < n or v % n: return None
    q = v // n; p = place(q)
    return p if 10 ** p == q else None
def viol_E(n, v): return n == 0 or v != n
def viol_L(n, v): return not (2 <= n <= 9 and v == n)
def viol_S(n, v): return n_pow10(n, v) is None
def series(alias):
    first = str(alias or '').split(',')[0].strip(); m = re.match(r'[A-Za-z]+', first)
    return m.group(0).upper() if m else '?'
def cp_ci(x, n):  # exact Clopper-Pearson 95% by bisection on the binomial cdf
    def cdf(k, p):
        if p <= 0: return 1.0
        if p >= 1: return 0.0 if k < n else 1.0
        return sum(exp(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * log(p) + (n - i) * log(1 - p)) for i in range(0, k + 1))
    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid): hi = mid
            else: lo = mid
        return (lo + hi) / 2
    lo = 0.0 if x == 0 else solve(lambda p: 1 - cdf(x - 1, p) >= 0.025)
    hi = 1.0 if x == n else solve(lambda p: cdf(x, p) <= 0.025)
    return lo, hi
def rate_class(r): return 'consistent (<0.1%)' if r < 0.001 else ('slightly inconsistent (0.1-5%)' if r < 0.05 else 'inconsistent (>=5%)')

t0 = time.time(); res = dict(mode=MODE, seeds=dict(H1=SEED_H1, power=SEED_POW, plant=SEED_PLANT, next_free=NEXT_FREE))
res['G0'] = dict(kfg_sha_ok=hashlib.sha256(open(KFG_DB, 'rb').read()).hexdigest() == KFG_SHA)
assert res['G0']['kfg_sha_ok'], 'G0 failed'
k = sqlite3.connect(KFG_DB)
alias = dict(k.execute('select name, aliases from khipu'))
T = []; cords = []; unparsed = 0; other = Counter()
for kh, idx, nm, kn in k.execute('select khipu, idx, cord_name, knots from cord order by khipu, idx'):
    toks = []
    for j, t in enumerate(str(kn or '').split(';')):
        t = t.strip()
        if not t: continue
        m = TOK.match(t)
        if not m: unparsed += 1; continue
        n, ty, pos, v = int(m.group(1)), m.group(2), float(m.group(3)), int(m.group(4))
        if ty not in ('S', 'L', 'E'): other[ty] += 1; continue
        toks.append(dict(kh=kh, cord=(kh, idx), name=nm, j=j, n=n, t=ty, pos=pos, v=v))
    if toks:
        maxpos = max((x['pos'], x['j']) for x in toks)
        for x in toks: x['last'] = (x['pos'], x['j']) == maxpos
    T += toks; cords.append(dict(kh=kh, name=str(nm or ''), toks=toks, r5=kfg_r5(kn)))
res['data'] = dict(n_khipus=len(alias), n_tokens_SLE=len(T), unparsed=unparsed, not_auditable_types=dict(other),
                   by_type=dict(Counter(x['t'] for x in T)))
print('data', res['data'], flush=True)
def rates(TT, cords_):
    out = {}
    for r, ty, f in (('R1', 'E', viol_E), ('R2', 'L', viol_L), ('R3', 'S', viol_S)):
        xs = [x for x in TT if x['t'] == ty]; out[r] = (sum(f(x['n'], x['v']) for x in xs), len(xs))
    r7 = 0; n7 = 0
    for c in cords_:
        el = [x for x in c['toks'] if x['t'] in 'LE']; ss = [x for x in c['toks'] if x['t'] == 'S']
        if el: n7 += 1; r7 += len(el) > 1
        for x in ss: n7 += 1; r7 += x['n'] > 9
    out['R7'] = (r7, n7)
    return out
# planted control (gate): 50 violations per rule R1-R3 on a copy, each must be detected
rng = np.random.default_rng(SEED_PLANT); P = [dict(x) for x in T]
pl = {}
for r, ty, f, bad in (('R1', 'E', viol_E, lambda x: x['v'] + 1), ('R2', 'L', viol_L, lambda x: x['v'] + 1 if x['n'] < 9 else 7),
                      ('R3', 'S', viol_S, lambda x: x['v'] * 3 + (1 if x['v'] % 10 == 0 else 0))):
    ok = [i for i, x in enumerate(P) if x['t'] == ty and not f(x['n'], x['v'])]
    pick = rng.choice(ok, 50, replace=False)
    for i in pick: P[i]['v'] = bad(P[i])
    pl[r] = int(sum(f(P[i]['n'], P[i]['v']) for i in pick))
res['plant_gate'] = dict(found_of_50=pl, passed=all(v == 50 for v in pl.values()))
if MODE == 'fixture':
    json.dump(res, open('analysis/k083_fixture.json', 'w'), indent=1); print(json.dumps(res, indent=1)); sys.exit(0)
# ---------------- registered run ----------------
rt = rates(T, cords); A = {}
for r in ('R1', 'R2', 'R3', 'R7'):
    x, n = rt[r]; ox, on = OKR[r]; lo, hi = cp_ci(x, n); kc, oc = rate_class(x / n), rate_class(ox / on)
    ok = res['plant_gate']['found_of_50'].get(r, 50) == 50
    A[r] = dict(kfg=[x, n, round(x / n, 5)], kfg_ci95=[round(lo, 5), round(hi, 5)], okr=[ox, on, round(ox / on, 5)],
                kfg_class=kc, okr_class=oc, verdict=('REPLICATED' if kc == oc else 'CHANGED') if ok else 'NOT TESTABLE')
pend = [c for c in cords if PEN.match(c['name'])]
sh = sum(c['r5'] for c in pend) / len(pend)
A['R5'] = dict(kfg_pendants_r5=[sum(c['r5'] for c in pend), len(pend), round(sh, 4)], okr_share=K007_R5_PENDANT_SHARE,
               all_cords_r5=[sum(c['r5'] for c in cords), len(cords)],
               verdict='REPLICATED' if 0.05 <= sh <= 0.15 else 'CHANGED')
A['R4'] = A['R6'] = 'NOT TESTABLE (KFG tokens are single-type clusters)'; A['R8'] = 'NOT COMPARABLE (OKR TOTAL_VALUE semantics)'
res['K007'] = A; print('K007', json.dumps(A), flush=True)
# K026 H1
EL = [x for x in T if x['t'] in 'LE']
lab = np.array([viol_E(x['n'], x['v']) if x['t'] == 'E' else viol_L(x['n'], x['v']) for x in EL])
typ = np.array([x['t'] == 'E' for x in EL])
khs = sorted({x['kh'] for x in EL}); khi = {kk: i for i, kk in enumerate(khs)}
sers = sorted({series(alias.get(kk)) for kk in khs}); sei = {s: i for i, s in enumerate(sers)}
gk = np.array([khi[x['kh']] for x in EL]); gs = np.array([sei[series(alias.get(x['kh']))] for x in EL])
def expected(g, ng, L):
    e = np.zeros(ng)
    for tm in (typ, ~typ):
        e += L[tm].sum() * np.bincount(g[tm], minlength=ng) / max(tm.sum(), 1)
    return e
def Gstat(L, g, ng, e):
    o = np.bincount(g[L], minlength=ng).astype(float); m = o > 0
    return float(2 * np.sum(o[m] * np.log(o[m] / e[m])))
rng = np.random.default_rng(SEED_H1); idxE = np.where(typ)[0]; idxL = np.where(~typ)[0]
nE = int(lab[typ].sum()); nL = int(lab[~typ].sum())
def null_labels(rg):
    L = np.zeros(len(EL), bool); L[rg.choice(idxE, nE, replace=False)] = True; L[rg.choice(idxL, nL, replace=False)] = True; return L
H1 = {}
for name, g, ng, keys in (('khipu', gk, len(khs), khs), ('series', gs, len(sers), sers)):
    e = expected(g, ng, lab); obs = Gstat(lab, g, ng, e)
    nulls = np.array([Gstat(null_labels(rng), g, ng, e) for _ in range(R)])
    p = float((1 + np.sum(nulls >= obs)) / (R + 1)); o = np.bincount(g[lab], minlength=ng)
    top = sorted(range(ng), key=lambda i: -(o[i] - e[i]))[:12]
    H1[name] = dict(G_obs=obs, null_mean=float(nulls.mean()), null_q99=float(np.quantile(nulls, 0.99)), p=p,
                    supported=p < 0.025, top_excess=[dict(group=(keys[i] + ' ' + str(alias.get(keys[i]))) if name == 'khipu' else keys[i],
                                                          obs=int(o[i]), exp=round(float(e[i]), 2)) for i in top])
    if name == 'khipu':
        q975 = float(np.quantile(nulls, 0.975)); rp = np.random.default_rng(SEED_POW); hits = 0
        for _ in range(NPOW):
            L = null_labels(rp); pick = rp.choice(len(khs), 3, replace=False)
            cand = np.where(np.isin(gk, pick) & ~L)[0]
            if len(cand) < 50: cand = np.where(~L)[0]
            L[rp.choice(cand, min(50, len(cand)), replace=False)] = True
            hits += Gstat(L, gk, len(khs), expected(gk, len(khs), L)) > q975
        H1[name]['power_50_in_3'] = hits / NPOW
pw = H1['khipu']['power_50_in_3']
for name in H1:
    H1[name]['verdict'] = ('REPLICATED (concentrated)' if H1[name]['supported'] else 'CHANGED (not concentrated)') if pw >= 0.8 else 'NOT TESTABLE'
res['K026_H1'] = dict(n_audited=len(EL), n_viol=int(lab.sum()), nE_viol=nE, nL_viol=nL, n_khipus=len(khs), n_series=len(sers), **H1)
print('H1', {kk: (H1[kk]['G_obs'], H1[kk]['p'], H1[kk]['verdict']) for kk in H1}, flush=True)
# K026 H2
cat = defaultdict(list)
for x, bad in zip(EL, lab):
    if not bad: continue
    n, v = x['n'], x['v']
    if x['t'] == 'E':
        pp = n_pow10(n, v) if n >= 1 else None
        if n == 0 or v == 0: cat['E-zero'].append(x)
        elif pp is not None and pp >= 1: cat['E-value' if x['last'] else 'E-type'].append(x)
        else: cat['E-other'].append(x)
    else:
        if 2 <= n <= 9:
            pp = n_pow10(n, v)
            if v == 0: cat['L-zero'].append(x)
            elif pp is not None and pp >= 1: cat['L-shift'].append(x)
            elif abs(v - n) == 1: cat['L-off1'].append(x)
            else: cat['L-other'].append(x)
        elif n == 1: cat['L-turn1'].append(x)
        elif n == 0: cat['L-turn0'].append(x)
        else: cat['L-turn10+'].append(x)
allc = sorted(set(cat) | set(K026_CATS) | {'E-value', 'E-other', 'L-zero', 'L-off1', 'L-other', 'L-turn1'})
H2 = {}
for c in allc:
    xs = cat.get(c, []); nw = len(xs) >= 20; okw = c in K026_CATS
    H2[c] = dict(n=len(xs), noteworthy=nw, k026_noteworthy=okw, k026_n=K026_CATS.get(c),
                 verdict='REPLICATED' if nw == okw else 'CHANGED',
                 khipus=Counter(x['kh'] + ' ' + str(alias.get(x['kh'])) for x in xs).most_common(5),
                 values=Counter((x['n'], x['v']) for x in xs).most_common(5),
                 examples=[f"{x['kh']} {x['name']} tok{x['j']}" for x in xs[:6]])
res['K026_H2'] = H2; res['runtime_s'] = round(time.time() - t0, 1)
json.dump(res, open('analysis/k083_results.json', 'w'), indent=1, default=str)
print('H2', {c: (H2[c]['n'], H2[c]['verdict']) for c in H2}); print('runtime', res['runtime_s'])
