#!/usr/bin/env python3
"""K058 - R5 multi-number-cord sensitivity of the FROZEN K023 held-out Inkawasi
'totals coloured apart from summands' result. Pre-registered in
case-file/K058-multinumber-inkawasi-holdout.md.

Frozen K022/K023 definitions: level-1 pendants, DUPLICATE_FLAG khipus dropped;
value = sum of knot values; colour = first ascher_cord_color row by
(RANGE_BEG, color_id); sum cord = pendant value>=10 with first matching block
(smallest k in 2..12, block to the right before left) whose sum equals it and
with >=2 nonzero cords; A = sum over sum cords of share of known-colour block
cords equal to the sum cord's colour; null = per sum cord, a random non-sum
eligible cord with a block of the same k and side; one-sided (A lower).
Population: PROVENANCE='Incahuasi' minus the ten K001 BH-significant khipus.

R5 MASK (K008, verbatim as K053-K057): an R5 pendant keeps its position but
is never a sum-cord target, never in a legal summand block, never an eligible
null anchor, and never inside a null anchor's block. Masked block search:
first LEGAL block (target non-R5, no R5 cord in the block).
Seeds: null 5858, FPR 5859, power 5860, sensitivity 58601..58605.
Usage: python3 tools/k058_multinumber_inkawasi_holdout.py khipu.db [--g0-only]
"""
import hashlib, json, sys, time, sqlite3
import numpy as np
from collections import defaultdict

t0 = time.time()
DB = sys.argv[1]
G0_ONLY = '--g0-only' in sys.argv
EXPECTED_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
KMAX = 12; R = 20000; NC = 200; ALPHA = 0.05; GATE = 0.08; POWER_BAR = 0.5
PUB = dict(n_khipus=15, n_sum=49, A=13.862121212121211, n_R5=3069, n_colour_cords=53750)
OUT = 'analysis/k058_g0.json' if G0_ONLY else 'analysis/k058_results.json'
res = dict(design=dict(R=R, NC=NC, alpha=ALPHA, gate=GATE, power_bar=POWER_BAR, published=PUB,
                       seeds=dict(null=5858, fpr=5859, power=5860, sens=[58601, 58602, 58603, 58604, 58605])))

def dump():
    res['secs'] = round(time.time() - t0, 1)
    json.dump(res, open(OUT, 'w'), indent=1)

def stop(reason):
    res['decision'] = dict(excluded=True, reason=reason); dump(); print('EXCLUDED:', reason); sys.exit(0)

h = hashlib.sha256(open(DB, 'rb').read()).hexdigest()
if h != EXPECTED_SHA: stop('hash mismatch ' + h)
c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute('select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1')}
names = {r[0]: (r[1] or '') for r in c.execute('select KHIPU_ID, OKR_NUM from khipu_main')}
ink = {r[0] for r in c.execute("select OKR_NUM from khipu_main where PROVENANCE='Incahuasi'")}
val = defaultdict(int)
for cid, v in c.execute('select CORD_ID, knot_value_type from knot'):
    if v is not None: val[cid] += int(v)
col = {}
for cid, fc in c.execute('select CORD_ID, FULL_COLOR from ascher_cord_color order by CORD_ID, RANGE_BEG, color_id'):
    if cid not in col and fc not in (None, '', "''"): col[cid] = fc.strip()
kh = defaultdict(list)
for khid, cid in c.execute('select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL'):
    if khid not in dups: kh[khid].append(cid)
sigk = {r['okr'] for r in json.load(open('analysis/k001_results_K5000.json'))['rows'] if r.get('bh_sig_N1')}

def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
clplaces = defaultdict(set); clcord = {}
for cid, cl, t, v in c.execute('select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot'):
    t = (t or '').strip()
    if t in ('S', 'L', 'E') and v: clplaces[cl].add(place(int(v)) if t == 'S' else 0)
    clcord[cl] = cid
ordn = {r[0]: r[1] for r in c.execute('select CLUSTER_ID, ORDINAL from knot_cluster')}
bycord = defaultdict(dict)
for cl, pl in clplaces.items():
    if len(pl) == 1 and ordn.get(cl) is not None: bycord[clcord[cl]][ordn[cl]] = next(iter(pl))
R5 = set()
for cd, d in bycord.items():
    s = [d[o] for o in sorted(d)]
    if len(s) >= 2 and not all(a > b for a, b in zip(s, s[1:])): R5.add(cd)
if len(R5) != PUB['n_R5']: stop(f'R5 count {len(R5)}')
if len(col) != PUB['n_colour_cords']: stop(f'colour cords {len(col)}')

def bidx(i, k, d, n):
    js = list(range(i + 1, i + k + 1)) if d == 1 else list(range(i - k, i))
    return js if js[0] >= 0 and js[-1] < n else None
def block(V, r5, i, masked):
    n = len(V)
    if V[i] < 10 or (masked and r5[i]): return None
    P = np.r_[0, np.cumsum(V)]; NZ = np.r_[0, np.cumsum(V > 0)]
    for k in range(2, KMAX + 1):
        if i + k < n and P[i + k + 1] - P[i + 1] == V[i] and NZ[i + k + 1] - NZ[i + 1] >= 2 \
                and not (masked and r5[i + 1:i + k + 1].any()): return (k, 1)
        if i - k >= 0 and P[i] - P[i - k] == V[i] and NZ[i] - NZ[i - k] >= 2 \
                and not (masked and r5[i - k:i].any()): return (k, -1)
    return None
def score(C, i, js):
    kn = [C[j] for j in js if C[j] is not None]
    return None if not kn else sum(x == C[i] for x in kn) / len(kn)

def build(masked, drop=()):
    items = []
    for khid, cids in kh.items():
        okr = names[khid]
        if okr not in ink or okr in sigk or okr in drop: continue
        V = np.array([val.get(x, 0) for x in cids], np.int64); C = [col.get(x) for x in cids]; n = len(cids)
        r5 = np.array([x in R5 for x in cids], dtype=bool)
        bl = {i: block(V, r5, i, masked) for i in range(n)}; sums = {i for i, b in bl.items() if b}
        elig = [j for j in range(n) if V[j] >= 10 and C[j] is not None and j not in sums and not (masked and r5[j])]
        for i in sorted(sums):
            if C[i] is None: continue
            k, d = bl[i]; s = score(C, i, bidx(i, k, d, n))
            if s is None: continue
            pool = []
            for j in elig:
                js = bidx(j, k, d, n)
                if js is None or (masked and r5[js].any()): continue
                sj = score(C, j, js)
                if sj is not None: pool.append((j, js, sj))
            if pool: items.append(dict(okr=okr, obs=s, pool=pool, C=C))
    return items

def null_draw(its, rng, Rr):
    tot = np.zeros(Rr)
    for it in its:
        ps = np.array([p[2] for p in it['pool']]); tot += ps[rng.integers(0, len(ps), Rr)]
    return tot
def p_lo(o, nl): return float((1 + (nl <= o + 1e-12).sum()) / (1 + len(nl)))
def planted(it, rng, j, js):
    C = it['C']; kn = [C[x] for x in js if C[x] is not None]; eq = []
    for x in kn:
        e = x == C[j]
        if rng.random() < 0.3: e = False
        eq.append(e)
    return sum(eq) / len(eq)

# ---- G0: empty-mask fixture must reproduce K023 ----
raw = build(False)
A0 = sum(it['obs'] for it in raw)
g0 = dict(n=len(raw), A=A0, n_khipus=len({it['okr'] for it in raw}),
          ok=(len(raw) == PUB['n_sum'] and abs(A0 - PUB['A']) < 1e-9 and len({it['okr'] for it in raw}) == PUB['n_khipus']))
res['G0'] = g0; dump(); print('G0', g0, flush=True)
if not g0['ok']: stop('G0 failed')
if G0_ONLY: sys.exit(0)

def analyse(its, seed_null, seed_fpr, seed_pow, controls=True):
    rng = np.random.default_rng(seed_null)
    A = sum(it['obs'] for it in its); N = null_draw(its, rng, R)
    out = dict(n_sum=len(its), n_khipus=len({it['okr'] for it in its}), A=A, null_mean=float(N.mean()),
               null_sd=float(N.std()), p=p_lo(A, N))
    if controls:
        rf = np.random.default_rng(seed_fpr); rp = np.random.default_rng(seed_pow); fp = pw = 0
        for _ in range(NC):
            pick = [it['pool'][rf.integers(len(it['pool']))] for it in its]
            fp += p_lo(sum(p[2] for p in pick), N) <= ALPHA
            pick = [it['pool'][rp.integers(len(it['pool']))] for it in its]
            pw += p_lo(sum(planted(it, rp, p[0], p[1]) for it, p in zip(its, pick)), N) <= ALPHA
        out.update(fpr=fp / NC, power=pw / NC)
    return out

masked = build(True)
res['masked_counts'] = dict(raw_sum=len(raw), masked_sum=len(masked),
                            raw_pool_mean=float(np.mean([len(i['pool']) for i in raw])),
                            masked_pool_mean=float(np.mean([len(i['pool']) for i in masked])) if masked else None)
res['stage'] = 'masked_built'; dump(); print(res['masked_counts'], flush=True)
if not masked: stop('no masked sum cords')
prim = analyse(masked, 5858, 5859, 5860)
res['primary'] = prim; res['stage'] = 'primary'; dump(); print('primary', prim, flush=True)
sens = []
for s in res['design']['seeds']['sens']:
    sens.append(analyse(masked, s, s + 1000, s + 2000, controls=False)['p'])
res['sens_p'] = sens; res['sens_p_mean'] = float(np.mean(sens))
m2 = build(True, drop=('KH0502',))
res['without_KH0502'] = analyse(m2, 5858, 5859, 5860, controls=False) if m2 else None
res['without_KH0502_sens_p'] = [analyse(m2, s, 0, 0, controls=False)['p'] for s in res['design']['seeds']['sens']] if m2 else None
if prim['fpr'] > GATE: verdict = 'EXCLUDED (FPR gate)'
elif prim['p'] <= ALPHA: verdict = 'ROBUST (supported under mask; fragile flag if any sensitivity seed > 0.05)'
elif prim['power'] >= POWER_BAR: verdict = 'NOT ESTABLISHED under the mask (powered)'
else: verdict = 'NOT TESTABLE under the mask (power < 0.5)'
res['decision'] = dict(verdict=verdict, fragile=any(p > ALPHA for p in sens)); res['stage'] = 'done'; dump()
print('VERDICT', res['decision'], flush=True)
