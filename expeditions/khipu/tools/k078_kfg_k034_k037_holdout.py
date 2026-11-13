#!/usr/bin/env python3
"""K078 - KFG re-audit step 10 (README line 9): the K034 and K037 held-out confirmations of the four F1-only names
(KH0322/UR086, KH0420/UR182 from K034; KH0502/UR266, KH0511/UR273B from K037) re-run on Khipu Field Guide data.
Pre-registered in case-file/K078-kfg-k034-k037-holdout.md BEFORE any real KFG L statistic was computed.
Statistic, null, p, plant, FPR gate and power code copied verbatim from tools/k037_f1_holdout_confirmation.py
(= K034 design); KFG pendants/groups exactly as tools/k077_kfg_k036_f1.py (K071 loader).
Usage (from expeditions/khipu):  python3 tools/k078_kfg_k034_k037_holdout.py data/khipu.db {fixture|smoke|all}
  fixture = G0 hashes + F0 (K034/K037 L and p reproduced EXACTLY on OKR with their own seeds) + KFG data gates + counts
  smoke   = fixture, then the pipeline on KFG values SHUFFLED within each khipu, small R (syntax check only)
  all     = fixture, KFG confirmation (seeds 6437-6440), FPR gate (6441), power (6442).
Next free seed 6443."""
import sqlite3, sys, json, time, os, hashlib, re, glob, zipfile
import numpy as np, xml.etree.ElementTree as ET
from collections import defaultdict
from math import lgamma, log, exp
T0 = time.time()
OKR_DB = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'fixture'; SMOKE = MODE == 'smoke'
OKR_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'
OUT = 'analysis/k078_smoke.json' if SMOKE else 'analysis/k078_results.json'
TARGETS = ('KH0322', 'KH0420', 'KH0502', 'KH0511')
ORIGIN = dict(KH0322='K034', KH0420='K034', KH0502='K037', KH0511='K037')
OKR_SEEDS = dict(KH0322=3430, KH0420=3431, KH0502=3730, KH0511=3731)
SEEDS = dict(KH0322=6437, KH0420=6438, KH0502=6439, KH0511=6440, fpr=6441, power=6442); NEXT_FREE = 6443
R_CONF = 200 if SMOKE else 20000; R_FPR = 100 if SMOKE else 5000; R_POW = 100 if SMOKE else 5000
N_FPR = 20 if SMOKE else 200; N_POW = 20 if SMOKE else 200
ALPHA = 0.025; FAMILY = 0.05

# ---------------- engine (K037 verbatim) ----------------
def valid_masks(gids):
    n = len(gids); vr, vl = [None] * 13, [None] * 13
    for k in range(2, 13):
        r = np.zeros(n, bool); l = np.zeros(n, bool)
        for i in range(n):
            if i + k < n: r[i] = bool(np.all(gids[i:i + k + 1] == gids[i]))
            if i - k >= 0: l[i] = bool(np.all(gids[i - k:i + 1] == gids[i]))
        vr[k], vl[k] = r, l
    return vr, vl
def longest_L_batch(V, gids, vr, vl):
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    idx = np.arange(n); big = V >= 10; L = np.zeros(B, np.int32)
    for k in range(2, 13):
        hk = np.zeros((B, n), bool)
        i = idx[idx + k < n]; i = i[vr[k][i]]
        if len(i): hk[:, i] |= ((P[:, i + k + 1] - P[:, i + 1]) == V[:, i]) & ((NZ[:, i + k + 1] - NZ[:, i + 1]) >= 2)
        i = idx[idx - k >= 0]; i = i[vl[k][i]]
        if len(i): hk[:, i] |= ((P[:, i] - P[:, i - k]) == V[:, i]) & ((NZ[:, i] - NZ[:, i - k]) >= 2)
        hk &= big; L = np.where(hk.any(1), np.maximum(L, k), L)
    return L
def hit_detail(v, gids, vr, vl):
    V = v[None]; n = len(v)
    P = np.zeros((1, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((1, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    idx = np.arange(n); big = V >= 10; hit = np.zeros(n, bool); k_at = np.zeros(n, np.int32); L = 0
    for k in range(2, 13):
        hk = np.zeros(n, bool)
        i = idx[idx + k < n]; i = i[vr[k][i]]
        if len(i): hk[i] |= ((P[0, i + k + 1] - P[0, i + 1]) == V[0, i]) & ((NZ[0, i + k + 1] - NZ[0, i + 1]) >= 2) & big[0, i]
        i = idx[idx - k >= 0]; i = i[vl[k][i]]
        if len(i): hk[i] |= ((P[0, i] - P[0, i - k]) == V[0, i]) & ((NZ[0, i] - NZ[0, i - k]) >= 2) & big[0, i]
        hit |= hk
        if hk.any(): L = max(L, k); k_at[hk] = np.maximum(k_at[hk], k)
    ng = int(gids.max()) + 1; gsize = np.bincount(gids, minlength=ng)
    ghit = np.bincount(gids, weights=hit.astype(float), minlength=ng).astype(int)
    n_gh = int(((gsize >= 4) & (ghit > 0)).sum())
    max_groups = sorted({int(gids[i]) for i in range(n) if k_at[i] == L and L > 0}); loo_L = None
    if max_groups:
        v2 = v.copy()
        for g in max_groups: v2[gids == g] = 0
        loo_L = int(longest_L_batch(v2[None], gids, vr, vl)[0])
    return dict(L=int(L), n_hits=int(hit.sum()), n_groups_hit=n_gh, n_eligible_groups=int((gsize >= 4).sum()),
                max_k_groups=max_groups, loo_L_after_zeroing_max_groups=loo_L)
def p_from_nulls(L_obs, null_L): return float((1 + int((null_L >= L_obs).sum())) / (1 + len(null_L)))
def binom_tail(x, n, a=0.05):
    if n == 0: return float('nan')
    return float(min(1.0, sum(exp(lgamma(n + 1) - lgamma(i + 1) - lgamma(n - i + 1) + i * log(a) + (n - i) * log(1 - a))
                              for i in range(x, n + 1))))
def group_ranges(gids):
    n, out, i = len(gids), [], 0
    while i < n:
        j = i
        while j < n and gids[j] == gids[i]: j += 1
        out.append((i, j)); i = j
    return out
def plant_L6(rng, v, gids):
    pl = rng.permutation(v).copy(); ranges = group_ranges(gids)
    for k_want in (6, 5):
        ch = [(a, b) for a, b in ranges if (b - a) >= k_want + 2]
        if not ch: continue
        a, b = ch[int(rng.integers(0, len(ch)))]; max_st = b - k_want - 1
        if max_st < a: continue
        st = int(rng.integers(a, max_st + 1)); sl = slice(st + 1, st + 1 + k_want); blk = pl[sl].copy()
        if (blk > 0).sum() < 2: blk[:] = np.maximum(blk, rng.integers(1, 30, len(blk)))
        s = int(blk.sum())
        if s < 10: blk[0] += 10 - s; s = int(blk.sum())
        pl[sl] = blk; pl[st] = s
        return pl
    return None
def null_Ls(rng, v, gids, vr, vl, R, chunk=500):
    out = np.empty(R, np.int32); left, pos = R, 0
    while left > 0:
        m = min(chunk, left); V = np.array([rng.permutation(v) for _ in range(m)])
        out[pos:pos + m] = longest_L_batch(V, gids, vr, vl); pos += m; left -= m
    return out
def gid_from_runs(labels):
    g = np.empty(len(labels), np.int32); gi, last = -1, object()
    for i, x in enumerate(labels):
        if x != last: gi += 1; last = x
        g[i] = gi
    return g
def n_ge4(gids): return sum(1 for a, b in group_ranges(gids) if b - a >= 4)
def confirm(v, g, seed, R):
    vr, vl = valid_masks(g); d = hit_detail(v, g, vr, vl)
    nl = null_Ls(np.random.default_rng(seed), v, g, vr, vl, R)
    return dict(L_obs=d['L'], p=p_from_nulls(d['L'], nl), detail=d, null_mean=float(nl.mean()),
                null_p95=float(np.percentile(nl, 95)), null_p99=float(np.percentile(nl, 99)), null_max=int(nl.max()),
                n_pend=len(v), sizes=[b - a for a, b in group_ranges(g)], R=R, seed=seed)
res = dict(cycle='K078', mode=MODE, design=dict(statistic='longest_within_group_exact_sum_window_L (K034/K037)',
           alpha_per_name=ALPHA, family_holm_alpha=FAMILY, R_CONF=R_CONF, R_FPR=R_FPR, R_POW=R_POW, N_FPR=N_FPR, N_POW=N_POW,
           plant='one within-group exact sum k=6 (fallback k=5)', seeds=SEEDS, next_free_seed=NEXT_FREE,
           groups='KFG CordGroups spans (K071)', universe='>= 10 nonzero pendants and >= 2 groups of size >= 4 (K034)'))
def dump(): res['secs'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1, default=float)
def stop(r): res['stopped'] = r; dump(); print('STOP:', r, flush=True); sys.exit(0)

# ---------------- G0 + F0 on OKR ----------------
G0 = dict(okr_sha_ok=hashlib.sha256(open(OKR_DB, 'rb').read()).hexdigest() == OKR_SHA,
          kfg_sha_ok=hashlib.sha256(open(KFG_DB, 'rb').read()).hexdigest() == KFG_SHA)
res['G0'] = G0
if not all(G0.values()): stop('hash mismatch')
c = sqlite3.connect(OKR_DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
kh = defaultdict(list)
for khid, cid, cl in c.execute("select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups: continue
    kh[khid].append((cl, val.get(cid, 0)))
okr_elig = {}
for khid, cords in kh.items():
    v = np.array([x[1] for x in cords], np.int64)
    if (v > 0).sum() < 10: continue
    okr_elig[khid] = (v, gid_from_runs([x[0] for x in cords]))
okr_by_num = {names[k][0]: k for k in okr_elig}
ref = {}
for f in ('k034', 'k037'):
    r = json.load(open(f'analysis/{f}_results.json'))
    for o, cc in r['confirmation'].items(): ref[o] = dict(L=cc['L_obs'], p=cc['p'], power=r['per_khipu'][o]['power'], detail=cc['detail'])
F0 = {}
for o in TARGETS:
    v, g = okr_elig[okr_by_num[o]]; x = confirm(v, g, OKR_SEEDS[o], 20000)
    F0[o] = dict(L=x['L_obs'], p=x['p'], L_ref=ref[o]['L'], p_ref=ref[o]['p'],
                 exact=bool(x['L_obs'] == ref[o]['L'] and x['p'] == ref[o]['p'] and x['detail'] == ref[o]['detail']))
F0['pass'] = all(F0[o]['exact'] for o in TARGETS); res['F0_engine_on_okr'] = F0
print('G0', G0, 'F0', F0, round(time.time() - T0, 1), flush=True)
if not F0['pass']: stop('F0 engine fixture on OKR failed')

# ---------------- KFG data (K077 loader verbatim) ----------------
k = sqlite3.connect(KFG_DB); sha = dict(k.execute('select name, sha256 from khipu'))
PEN = re.compile(r'^p(\d+)$'); pend = defaultdict(list)
for khn, nm, v in k.execute('select khipu, cord_name, value from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0
    pend[khn].append((int(m.group(1)), x))
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
GRP = re.compile(r'^[\d.]+cm group of (\d+) pendants \((\d+)-(\d+)\)'); ONE = re.compile(r'^[\d.]+cm 1 \((\d+)\)')
def sheet_strings(f, name):
    z = zipfile.ZipFile(f); wb = ET.fromstring(z.read('xl/workbook.xml'))
    i = [s.get('name') for s in wb.iter(NS + 'sheet')].index(name) + 1
    ss = [''.join(x.text or '' for x in si.iter(NS + 't')) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(NS + 'si')] if 'xl/sharedStrings.xml' in z.namelist() else []
    out = []
    for cc in ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).iter(NS + 'c'):
        vv = cc.find(NS + 'v')
        if cc.get('t') == 's' and vv is not None: out.append(ss[int(vv.text)])
        elif cc.get('t') == 'inlineStr': out.append(''.join(x.text or '' for x in cc.iter(NS + 't')))
        elif vv is not None: out.append(vv.text)
    return out
g0_bad, g1_bad, groups = [], [], {}
for f in sorted(glob.glob(f'{XLSX}/*.xlsx')):
    khn = f.split('/')[-1][:-5]
    if hashlib.sha256(open(f, 'rb').read()).hexdigest() != sha.get(khn): g0_bad.append(khn); continue
    spans = []
    for s in sheet_strings(f, 'CordGroups'):
        m = GRP.match(s)
        if m: spans.append((int(m.group(2)), int(m.group(3))))
        else:
            m = ONE.match(s)
            if m: spans.append((int(m.group(1)), int(m.group(1))))
    L = pend.get(khn, []); n = len(L)
    if n and [p for p, _ in L] == list(range(1, n + 1)) and [p for a, b in spans for p in range(a, b + 1)] == list(range(1, n + 1)):
        groups[khn] = spans
    elif n: g1_bad.append(khn)
gates = dict(G0_xlsx_hash_mismatch=len(g0_bad), G1_partition_rate=len(groups) / max(1, len(groups) + len(g1_bad)), G1_bad=g1_bad)
okr_num = {names[x][0] for x in names if names[x][0]}
kfg_elig = {}
for khn, spans in groups.items():
    v = np.array([x for _, x in pend[khn]], np.int64)
    if (v > 0).sum() < 10: continue
    g = np.empty(len(v), np.int32)
    for gi, (a, b) in enumerate(spans): g[a - 1:b] = gi
    kfg_elig[khn] = (v, g)
kfg_pop = sorted(x for x, (v, g) in kfg_elig.items() if n_ge4(g) >= 2)
data = dict(n_kfg_khipus=len(sha), n_grouped=len(groups), n_eligible=len(kfg_elig), n_pop=len(kfg_pop),
            targets_in_pop=[o for o in TARGETS if o in kfg_pop], targets_missing=[o for o in TARGETS if o not in kfg_pop],
            identical_values=[o for o in TARGETS if o in kfg_elig and np.array_equal(kfg_elig[o][0], okr_elig[okr_by_num[o]][0])],
            identical_groups=[o for o in TARGETS if o in kfg_elig and np.array_equal(kfg_elig[o][1], okr_elig[okr_by_num[o]][1])],
            n_pend={o: [len(okr_elig[okr_by_num[o]][0]), len(kfg_elig[o][0]) if o in kfg_elig else None] for o in TARGETS})
gates['pass_data'] = gates['G0_xlsx_hash_mismatch'] == 0 and gates['G1_partition_rate'] >= 0.95
res['data_gates'] = gates; res['data'] = data
print('data gates', {a: b for a, b in gates.items() if a != 'G1_bad'}, flush=True); print('data', data, flush=True)
if not gates['pass_data']: stop('KFG data gate failed')
if MODE == 'fixture': dump(); print('fixture done', round(time.time() - T0, 1)); sys.exit(0)
if SMOKE:
    sr = np.random.default_rng(0)
    for x in kfg_pop: kfg_elig[x] = (sr.permutation(kfg_elig[x][0]), kfg_elig[x][1])

# ---------------- confirmation on KFG ----------------
conf = {}
for o in TARGETS:
    if o not in kfg_pop: continue
    v, g = kfg_elig[o]; conf[o] = confirm(v, g, SEEDS[o], R_CONF)
    print('CONF', o, 'L', conf[o]['L_obs'], 'p', conf[o]['p'], round(time.time() - T0, 1), flush=True)
res['confirmation'] = conf; dump()
# ---------------- FPR gate (K037 verbatim on the KFG pop) ----------------
rng_f = np.random.default_rng(SEEDS['fpr']); cand = [x for x in kfg_pop if x not in TARGETS]; rng_f.shuffle(cand)
pick = cand[:N_FPR]; hits = 0
for j, x in enumerate(pick):
    v, g = kfg_elig[x]; vr, vl = valid_masks(g); y = rng_f.permutation(v)
    Lo = int(longest_L_batch(y[None], g, vr, vl)[0]); p = p_from_nulls(Lo, null_Ls(rng_f, y, g, vr, vl, R_FPR))
    hits += int(p <= ALPHA)
    if (j + 1) % 50 == 0: print('FPR', j + 1, round(time.time() - T0, 1), flush=True)
fpr = hits / max(1, len(pick)); fpr_gate = fpr <= 0.08
res['fpr'] = dict(n=len(pick), hits=hits, fpr=fpr, gate_pass=fpr_gate, gate_threshold=0.08, binom_p_above_0_05=binom_tail(hits, len(pick)))
print('FPR', res['fpr'], flush=True); dump()
# ---------------- power ----------------
rng_p = np.random.default_rng(SEEDS['power']); power = {}
for o in conf:
    v, g = kfg_elig[o]; vr, vl = valid_masks(g); ok = att = sk = 0
    for _ in range(N_POW):
        pl = plant_L6(rng_p, v, g)
        if pl is None: sk += 1; continue
        att += 1; Lo = int(longest_L_batch(pl[None], g, vr, vl)[0])
        ok += int(p_from_nulls(Lo, null_Ls(rng_p, pl, g, vr, vl, R_POW)) <= ALPHA)
    power[o] = dict(n_plants=att, skipped=sk, detected=ok, power=ok / att if att else float('nan'))
    print('POW', o, power[o], round(time.time() - T0, 1), flush=True)
res['power'] = power
# ---------------- decisions ----------------
per = {}
for o in TARGETS:
    if o not in conf: per[o] = dict(fate='NOT TESTABLE (not in KFG pop)'); continue
    p, pw = conf[o]['p'], power[o]['power']
    if not fpr_gate: fate = 'NOT TESTABLE (FPR gate)'
    elif p <= ALPHA: fate = 'REPLICATED'
    elif pw >= 0.5: fate = 'CHANGED (not confirmed on KFG)'
    else: fate = 'NOT TESTABLE (power < 0.5)'
    per[o] = dict(origin=ORIGIN[o], L_okr=ref[o]['L'], p_okr=ref[o]['p'], power_okr=ref[o]['power'], L_kfg=conf[o]['L_obs'],
                  p_kfg=p, power_kfg=pw, fate=fate, identical_values=o in data['identical_values'], identical_groups=o in data['identical_groups'])
ps = sorted((conf[o]['p'], o) for o in conf); holm = {}
for i, (p, o) in enumerate(ps):
    holm[o] = bool(p <= FAMILY / (len(ps) - i)) and all(holm[q] for _, q in ps[:i])
for o in conf: per[o]['holm4_sig'] = holm[o]
res['per_name'] = per; res['summary'] = dict(replicated=sum(per[o]['fate'] == 'REPLICATED' for o in TARGETS),
    changed=sum(per[o]['fate'].startswith('CHANGED') for o in TARGETS), not_testable=sum(per[o]['fate'].startswith('NOT') for o in TARGETS),
    holm4_sig=sum(holm.values()), fpr_gate=fpr_gate)
dump(); print(json.dumps(res['summary'], indent=1)); [print('NAME', o, per[o]) for o in TARGETS]
print('seconds', round(time.time() - T0, 1), flush=True)
