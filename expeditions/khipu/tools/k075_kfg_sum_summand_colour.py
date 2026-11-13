#!/usr/bin/env python3
"""K075 - KFG re-audit step 7 (README line 9): line 6, K022 (totals vs summand colour) and K023 (held-out Inkawasi
'apart') re-run on Khipu Field Guide data. Pre-registered in case-file/K075-kfg-sum-summand-colour.md.
K022 engine verbatim (block, bidx, score, anchor null, two-sided p, planted 'match'/'apart' at 30 %, verdict rule,
alpha 0.05, FPR bar 0.08); K023 rule verbatim (one-sided 'apart', same controls). KFG pendants / colour coding as K074
(primary = first '/'-segment, '(a-b)' removed; sensitivity = ':'-components sorted, reported only).
Usage: python3 tools/k075_kfg_sum_summand_colour.py data/khipu.db [--smoke]. Seed 6428 (one stream); next free 6429."""
import sqlite3, json, sys, re, hashlib, time, numpy as np
from collections import defaultdict
T0 = time.time(); KFG_DB = '/workspace/kfg/kfg_20261111.db'
OKR_DB = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'data/khipu.db'
SMOKE = '--smoke' in sys.argv; OUT = 'analysis/k075_smoke.json' if SMOKE else 'analysis/k075_results.json'
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'
OKR_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
R = 300 if SMOKE else 20000; NC = 10 if SMOKE else 200; KMAX = 12; SEED = 6428; NEXT_FREE = 6429; ALPHA = 0.05
rng = np.random.default_rng(SEED)
PUB = dict(K022_primary=dict(n=95, A=50.666666666666664, verdict='not supported'),
           K022_secondary=dict(n=712, A=298.1304834054834, p=0.0588, direction='apart'),
           K023=dict(n=49, n_khipus=15, A=13.862121212121211, verdict='supported'))
res = dict(design=dict(seed=SEED, next_free_seed=NEXT_FREE, R=R, NC=NC, alpha=ALPHA, smoke=SMOKE), published_okr=PUB)
def dump(): res['secs'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1)
def stop(r): res['decision'] = dict(excluded=True, reason=r); dump(); print('EXCLUDED:', r); sys.exit(0)
for path, want in ((OKR_DB, OKR_SHA), (KFG_DB, KFG_SHA)):
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    if h != want: stop(f'G0 hash mismatch {path} {h}')
res['G0'] = 'pass'
# ---------------- K022 engine verbatim ----------------
def block(V, i):
    n = len(V); P = np.r_[0, np.cumsum(V)]; NZ = np.r_[0, np.cumsum(V > 0)]
    if V[i] < 10: return None
    for k in range(2, KMAX + 1):
        if i + k < n and P[i + k + 1] - P[i + 1] == V[i] and NZ[i + k + 1] - NZ[i + 1] >= 2: return (k, 1)
        if i - k >= 0 and P[i] - P[i - k] == V[i] and NZ[i] - NZ[i - k] >= 2: return (k, -1)
    return None
def bidx(i, k, d, n):
    js = list(range(i + 1, i + k + 1)) if d == 1 else list(range(i - k, i))
    return js if js[0] >= 0 and js[-1] < n else None
def score(C, i, js):
    kn = [C[j] for j in js if C[j] is not None]
    return None if not kn else sum(x == C[i] for x in kn) / len(kn)
def build(kh):  # kh: name -> list of (value, colour or None)
    items = []
    for name, L in kh.items():
        V = np.array([v for v, _ in L], np.int64); C = [x for _, x in L]; n = len(L)
        bl = {i: block(V, i) for i in range(n)}; sums = {i for i, b in bl.items() if b}
        elig_ns = [j for j in range(n) if V[j] >= 10 and C[j] is not None and j not in sums]
        for i in sorted(sums):
            if C[i] is None: continue
            k, d = bl[i]; s = score(C, i, bidx(i, k, d, n))
            if s is None: continue
            pool = []
            for j in elig_ns:
                js = bidx(j, k, d, n)
                if js is None: continue
                sj = score(C, j, js)
                if sj is not None: pool.append((j, js, sj))
            if not pool: continue
            items.append(dict(okr=name, obs=s, pool=pool, C=C, k=k, d=d))
    return items
def null_draw(its, Rr):
    tot = np.zeros(Rr)
    for it in its:
        ps = np.array([p[2] for p in it['pool']]); tot += ps[rng.integers(0, len(ps), Rr)]
    return tot
def p2(o, nl):
    hi = (1 + (nl >= o - 1e-12).sum()) / (1 + len(nl)); lo = (1 + (nl <= o + 1e-12).sum()) / (1 + len(nl))
    return float(min(1.0, 2 * min(hi, lo)))
def p_lo(o, nl): return float((1 + (nl <= o + 1e-12).sum()) / (1 + len(nl)))
def planted(it, j, js, mode):
    C = it['C']; kn = [C[x] for x in js if C[x] is not None]; eq = []
    for x in kn:
        e = x == C[j]
        if rng.random() < 0.3: e = (mode == 'match')
        eq.append(e)
    return sum(eq) / len(eq)
def run22(its, label):  # K022 run() verbatim, controls on
    A = sum(it['obs'] for it in its); N = null_draw(its, R); out = dict(pop=label, n_khipus=len({it['okr'] for it in its}), n_sum_cords=len(its), A=A,
        A_null_mean=float(N.mean()), A_null_sd=float(N.std()), p_two_sided=p2(A, N), direction='match' if A > N.mean() else 'apart')
    fp = pm = pa = 0
    for _ in range(NC):
        pick = [it['pool'][rng.integers(len(it['pool']))] for it in its]
        fp += p2(sum(p[2] for p in pick), N) <= ALPHA
        pm += p2(sum(planted(it, p[0], p[1], 'match') for it, p in zip(its, pick)), N) <= ALPHA
        pa += p2(sum(planted(it, p[0], p[1], 'apart') for it, p in zip(its, pick)), N) <= ALPHA
    out.update(calib_fpr=fp / NC, power_match=pm / NC, power_apart=pa / NC)
    pw = out['power_match'] if out['direction'] == 'match' else out['power_apart']
    out['verdict'] = ('controls failed' if out['calib_fpr'] > 0.08 else
                      ('totals match summands' if out['direction'] == 'match' else 'totals coloured apart') if out['p_two_sided'] <= ALPHA
                      else 'not supported' if pw >= 0.5 else 'not testable')
    return out
def run23(its, label):  # K023 rule verbatim
    A = sum(it['obs'] for it in its); N = null_draw(its, R); fp = pw = 0
    for _ in range(NC):
        pick = [it['pool'][rng.integers(len(it['pool']))] for it in its]
        fp += p_lo(sum(p[2] for p in pick), N) <= ALPHA
        pw += p_lo(sum(planted(it, p[0], p[1], 'apart') for it, p in zip(its, pick)), N) <= ALPHA
    out = dict(pop=label, n_khipus=len({it['okr'] for it in its}), khipus=sorted({it['okr'] for it in its}), n_sum_cords=len(its), A=A,
               A_null_mean=float(N.mean()), A_null_sd=float(N.std()), p_one_sided_apart=p_lo(A, N), calib_fpr=fp / NC, power_apart=pw / NC)
    out['verdict'] = ('controls failed' if out['calib_fpr'] > 0.08 else 'supported' if out['p_one_sided_apart'] <= ALPHA
                      else 'not supported' if out['power_apart'] >= 0.5 else 'not testable')
    return out
# ---------------- OKR (K022 loader verbatim) -> F0 fixture ----------------
c = sqlite3.connect(OKR_DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
okrname = {r[0]: r[1] or '' for r in c.execute("select KHIPU_ID, OKR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
col = {}
for cid, fc in c.execute("select CORD_ID, FULL_COLOR from ascher_cord_color order by CORD_ID, RANGE_BEG, color_id"):
    if cid not in col and fc not in (None, '', "''"): col[cid] = fc.strip()
okr = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: okr[okrname[khid] or f'id{khid}'].append((val.get(cid, 0), col.get(cid)))
sigk = sorted({r['okr'] for r in json.load(open('analysis/k001_results_K5000.json'))['rows'] if r.get('bh_sig_N1')})
ink = {r[0] for r in c.execute("select OKR_NUM from khipu_main where PROVENANCE='Incahuasi'")}
oi = build(okr)
f0 = dict(K022_primary=[len([i for i in oi if i['okr'] in sigk]), sum(i['obs'] for i in oi if i['okr'] in sigk)],
          K022_secondary=[len(oi), sum(i['obs'] for i in oi)],
          K023=[len([i for i in oi if i['okr'] in ink and i['okr'] not in sigk]), sum(i['obs'] for i in oi if i['okr'] in ink and i['okr'] not in sigk)])
res['F0'] = dict(got=f0, pass_=all(f0[k][0] == PUB[k]['n'] and abs(f0[k][1] - PUB[k]['A']) < 1e-9 for k in PUB)); print('F0', res['F0'], flush=True)
if not res['F0']['pass_']: stop('F0 K022/K023 fixture on OKR failed')
# ---------------- KFG (K074 loader verbatim) ----------------
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
kink = {r[0] for r in k.execute("select name from khipu where provenance='Incahuasi'")}
k023_set = sorted(json.load(open('analysis/k023_results.json'))['khipus'])
okr_names = set(okrname.values())
h3_pop = sorted(n for n in kink if n not in okr_names and n not in sigk)
res['data'] = dict(n_kfg=len(raw), nonseq_excluded=nonseq, kfg_incahuasi=len(kink), H3_population_kfg_only_incahuasi=h3_pop)
if SMOKE:
    sr = np.random.default_rng(0)
    kfg = {kh: list(zip([a for a, _ in L], [L[i][1] for i in sr.permutation(len(L))])) for kh, L in kfg.items()}
out = {}
for cname, cf in (('primary_coding', c_prim), ('sorted_coding', c_sort)):
    it = build({kh: [(a, cf(b)) for a, b in L] for kh, L in kfg.items()})
    o = dict(H1_K022_primary=run22([i for i in it if i['okr'] in sigk], 'OKR K001 BH names on KFG'),
             S_K022_all=run22(it, 'all KFG khipus with a sum cord'),
             H2_K023_set=run23([i for i in it if i['okr'] in kink and i['okr'] not in sigk], 'Incahuasi minus K001 BH names (KFG provenance)'))
    h3 = [i for i in it if i['okr'] in h3_pop]
    o['H3_kfg_only_incahuasi'] = run23(h3, 'KFG-only Incahuasi') if h3 else dict(n_sum_cords=0, verdict='not testable (empty population)')
    out[cname] = o
    print(cname, json.dumps({a: {x: b.get(x) for x in ('n_khipus', 'n_sum_cords', 'A', 'A_null_mean', 'p_two_sided', 'p_one_sided_apart', 'direction', 'calib_fpr', 'power_match', 'power_apart', 'verdict')} for a, b in o.items()}), round(time.time() - T0, 1), flush=True)
res['results'] = out
def rep(kv, ov):
    if kv.startswith('not testable') or kv == 'controls failed': return 'NOT TESTABLE'
    return 'REPLICATED' if kv == ov else 'CHANGED (correction)'
P = out['primary_coding']
res['decision'] = dict(H1_K022=rep(P['H1_K022_primary']['verdict'], 'not supported'), H2_K023=rep(P['H2_K023_set']['verdict'], 'supported'),
                       H3_new_heldout=P['H3_kfg_only_incahuasi']['verdict'], S_K022_all='descriptive (OKR lean apart p 0.059, reported only)')
print('decision', res['decision']); dump()
