#!/usr/bin/env python3
"""K082 - KFG line 1: K008's multi-number (R5) mask applied to the L statistic (K034/K037) for the five names that L
supports on KFG data: KH0505 (K079, corroborated) and K078's four held-out confirmations KH0322, KH0420, KH0502, KH0511.
Pre-registered in case-file/K082-kfg-l-r5-mask.md BEFORE any masked L on real values was computed.
Engine (L, null, p, plant, FPR, power) verbatim from tools/k079_kfg_double_flag_L.py; KFG loader verbatim from K079;
R5 rule verbatim from tools/k080_kfg_k008_r5_mask.py (kfg_r5); masking as K008/K080: an R5 pendant is never a target,
never inside a summand window, keeps its position; nulls and plants permute only non-R5 values among non-R5 positions.
Masking is applied by removing windows from K079's valid-window masks, so an empty mask is K079 exactly (F0).
Usage (from expeditions/khipu):  python3 tools/k082_kfg_l_r5_mask.py data/khipu.db {fixture|all}
Seeds 6453-6457 (names, in TARGETS order), 6458 (FPR), 6459 (power). Next free seed 6460."""
import sqlite3, sys, json, time, os, hashlib, re, glob, zipfile
import numpy as np, xml.etree.ElementTree as ET
from collections import defaultdict
from math import lgamma, log, exp
T0 = time.time()
OKR_DB = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'fixture'
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'
OUT = 'analysis/k082_fixture.json' if MODE == 'fixture' else 'analysis/k082_results.json'
TARGETS = ('KH0505', 'KH0322', 'KH0420', 'KH0502', 'KH0511')
K078_SEEDS = dict(KH0322=6437, KH0420=6438, KH0502=6439, KH0511=6440); K079_SEED = 6443
SEEDS = dict(KH0505=6453, KH0322=6454, KH0420=6455, KH0502=6456, KH0511=6457, fpr=6458, power=6459); NEXT_FREE = 6460
EXCL_FPR = TARGETS + ('KH0677', 'KH0695', 'KH0143', 'KH0168', 'KH0597', 'KH0604A', 'KH0674')
R_CONF = 20000; R_FPR = 5000; R_POW = 5000; N_FPR = 200; N_POW = 200
ALPHA = 0.025; FAMILY = 0.05

# ---------------- engine (K079/K037 verbatim) ----------------
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
def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
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

# ---------------- masking layer (new in K082) ----------------
def mask_windows(gids, bad):
    """K079 valid windows minus any window whose target or summands include an R5 pendant."""
    vr, vl = valid_masks(gids); n = len(gids)
    if not bad.any(): return vr, vl
    BD = np.zeros(n + 1, np.int64); BD[1:] = np.cumsum(bad); mr, ml = [None] * 13, [None] * 13
    for k in range(2, 13):
        r = vr[k].copy(); l = vl[k].copy()
        for i in range(n):
            if r[i] and (bad[i] or BD[i + k + 1] - BD[i + 1] > 0): r[i] = False
            if l[i] and (bad[i] or BD[i] - BD[i - k] > 0): l[i] = False
        mr[k], ml[k] = r, l
    return mr, ml
def null_Ls_m(rng, v, gids, vr, vl, bad, R, chunk=500):
    free = np.where(~bad)[0]; out = np.empty(R, np.int32); left, pos = R, 0
    while left > 0:
        m = min(chunk, left); V = np.tile(v, (m, 1))
        for b in range(m): V[b, free] = rng.permutation(v[free])
        out[pos:pos + m] = longest_L_batch(V, gids, vr, vl); pos += m; left -= m
    return out
def plant_m(rng, v, gids, bad):
    free = np.where(~bad)[0]; pl = v.copy(); pl[free] = rng.permutation(v[free])
    lab = [(int(gids[i]) if not bad[i] else -1 - i) for i in range(len(v))]
    ranges = [(a, b) for a, b in group_ranges(gid_from_runs(lab)) if not bad[a]]
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
def confirm_m(v, g, bad, seed, R):
    vr, vl = mask_windows(g, bad); d = hit_detail(v, g, vr, vl)
    nl = null_Ls_m(np.random.default_rng(seed), v, g, vr, vl, bad, R)
    return dict(L_obs=d['L'], p=p_from_nulls(d['L'], nl), detail=d, null_mean=float(nl.mean()),
                null_p95=float(np.percentile(nl, 95)), null_p99=float(np.percentile(nl, 99)), null_max=int(nl.max()),
                n_pend=len(v), n_r5=int(bad.sum()), R=R, seed=seed)
res = dict(cycle='K082', mode=MODE, design=dict(statistic='L (K034/K037) with K008 R5 mask', alpha_per_name=ALPHA,
           family_holm_alpha=FAMILY, R_CONF=R_CONF, R_FPR=R_FPR, R_POW=R_POW, N_FPR=N_FPR, N_POW=N_POW, seeds=SEEDS,
           next_free_seed=NEXT_FREE))
def dump(): res['secs'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1, default=float)
def stop(r): res['stopped'] = r; dump(); print('STOP:', r, flush=True); sys.exit(0)
G0 = dict(kfg_sha_ok=hashlib.sha256(open(KFG_DB, 'rb').read()).hexdigest() == KFG_SHA); res['G0'] = G0
if not all(G0.values()): stop('hash mismatch')
names = {}
# ---------------- KFG data (K079 loader verbatim) ----------------
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
r5 = defaultdict(list)
for khn, nm, kn in k.execute('select khipu, cord_name, knots from cord order by khipu, idx'):
    if PEN.match(str(nm or '')): r5[khn].append(kfg_r5(kn))
badm = {x: np.array(r5[x], bool) for x in kfg_elig}
assert all(len(badm[x]) == len(kfg_elig[x][0]) for x in kfg_elig)
gates['pass_data'] = gates['G0_xlsx_hash_mismatch'] == 0 and gates['G1_partition_rate'] >= 0.95
res['data_gates'] = {a: b for a, b in gates.items() if a != 'G1_bad'}
res['data'] = dict(n_pop=len(kfg_pop), targets_in_pop=[o for o in TARGETS if o in kfg_pop],
                   n_r5={o: int(badm[o].sum()) for o in TARGETS}, n_pend={o: len(kfg_elig[o][0]) for o in TARGETS},
                   pop_with_r5=int(sum(badm[x].any() for x in kfg_pop)))
print('data', res['data_gates'], res['data'], flush=True)
if not gates['pass_data']: stop('KFG data gate failed')
# ---------------- F0: empty mask reproduces K078 (4 names) and K079 (KH0505) exactly ----------------
k78 = json.load(open('analysis/k078_results.json'))['confirmation']; k79 = json.load(open('analysis/k079_results.json'))['confirmation']
F0 = {}
for o in TARGETS:
    ref, sd = (k79[o], K079_SEED) if o == 'KH0505' else (k78[o], K078_SEEDS[o])
    v, g = kfg_elig[o]; x = confirm_m(v, g, np.zeros(len(v), bool), sd, 20000)
    F0[o] = dict(L=x['L_obs'], p=x['p'], exact=bool(x['L_obs'] == ref['L_obs'] and x['p'] == ref['p'] and x['detail'] == ref['detail']))
F0['pass'] = all(F0[o]['exact'] for o in TARGETS); res['F0'] = F0
print('F0', F0, round(time.time() - T0, 1), flush=True)
if not F0['pass']: stop('F0 failed')
# where the unmasked hits sit relative to R5 cords (structure only, no statistic)
loc = {}
for o in TARGETS:
    v, g = kfg_elig[o]; b = badm[o]; ng = int(g.max()) + 1
    loc[o] = dict(r5_positions=[int(i) + 1 for i in np.where(b)[0]], r5_per_group={int(j): int(b[g == j].sum()) for j in range(ng) if b[g == j].any()})
res['r5_layout'] = loc; print('layout', loc, flush=True)
if MODE == 'fixture': dump(); print('fixture done', round(time.time() - T0, 1)); sys.exit(0)
# ---------------- masked confirmation ----------------
conf = {}
for o in TARGETS:
    v, g = kfg_elig[o]; conf[o] = confirm_m(v, g, badm[o], SEEDS[o], R_CONF)
    print('CONF', o, 'L', conf[o]['L_obs'], 'p', conf[o]['p'], conf[o]['detail'], round(time.time() - T0, 1), flush=True)
res['confirmation_masked'] = conf; dump()
# ---------------- FPR gate (masked, K037 design) ----------------
rng_f = np.random.default_rng(SEEDS['fpr']); cand = [x for x in kfg_pop if x not in EXCL_FPR]; rng_f.shuffle(cand)
pick = cand[:N_FPR]; hits = 0
for j, x in enumerate(pick):
    v, g = kfg_elig[x]; b = badm[x]; vr, vl = mask_windows(g, b); free = np.where(~b)[0]
    y = v.copy(); y[free] = rng_f.permutation(v[free])
    Lo = int(longest_L_batch(y[None], g, vr, vl)[0]); p = p_from_nulls(Lo, null_Ls_m(rng_f, y, g, vr, vl, b, R_FPR))
    hits += int(p <= ALPHA)
    if (j + 1) % 50 == 0: print('FPR', j + 1, round(time.time() - T0, 1), flush=True)
fpr = hits / max(1, len(pick)); fpr_gate = fpr <= 0.08
res['fpr'] = dict(n=len(pick), hits=hits, fpr=fpr, gate_pass=fpr_gate, gate_threshold=0.08, n_with_r5=int(sum(badm[x].any() for x in pick)),
                  binom_p_above_0_05=binom_tail(hits, len(pick)))
print('FPR', res['fpr'], flush=True); dump()
# ---------------- masked power ----------------
rng_p = np.random.default_rng(SEEDS['power']); power = {}
for o in TARGETS:
    v, g = kfg_elig[o]; b = badm[o]; vr, vl = mask_windows(g, b); ok = att = sk = 0
    for _ in range(N_POW):
        pl = plant_m(rng_p, v, g, b)
        if pl is None: sk += 1; continue
        att += 1; Lo = int(longest_L_batch(pl[None], g, vr, vl)[0])
        ok += int(p_from_nulls(Lo, null_Ls_m(rng_p, pl, g, vr, vl, b, R_POW)) <= ALPHA)
    power[o] = dict(n_plants=att, skipped=sk, detected=ok, power=ok / att if att else float('nan'))
    print('POW', o, power[o], round(time.time() - T0, 1), flush=True)
res['power'] = power
# ---------------- decisions ----------------
per = {}
for o in TARGETS:
    p, pw, nr = conf[o]['p'], power[o]['power'], conf[o]['n_r5']
    if nr == 0: fate = 'UNAFFECTED (no R5 pendant; masked test = unmasked)'
    elif not fpr_gate: fate = 'NOT TESTABLE (FPR gate)'
    elif p <= ALPHA: fate = 'SURVIVES MASK'
    elif pw >= 0.5: fate = 'DROPS UNDER MASK'
    else: fate = 'NOT TESTABLE (masked power < 0.5)'
    per[o] = dict(L_masked=conf[o]['L_obs'], p_masked=p, power_masked=pw, n_r5=nr, F0_unmasked_L=F0[o]['L'], F0_unmasked_p=F0[o]['p'], fate=fate)
fam = [o for o in TARGETS if conf[o]['n_r5'] > 0]
ps = sorted((conf[o]['p'], o) for o in fam); holm = {}
for i, (p, o) in enumerate(ps):
    holm[o] = bool(p <= FAMILY / (len(ps) - i)) and all(holm[q] for _, q in ps[:i])
for o in TARGETS: per[o]['holm_sig'] = holm.get(o)
res['per_name'] = per; res['family'] = fam; res['summary'] = {f: sum(per[o]['fate'].startswith(f) for o in TARGETS)
    for f in ('SURVIVES', 'DROPS', 'NOT TESTABLE', 'UNAFFECTED')}
res['summary']['fpr_gate'] = fpr_gate
dump(); print(json.dumps(res['summary'], indent=1)); [print('NAME', o, per[o]) for o in TARGETS]
print('seconds', round(time.time() - T0, 1), flush=True)
