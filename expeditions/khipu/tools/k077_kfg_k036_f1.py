#!/usr/bin/env python3
"""K077 - KFG re-audit step 9 (README line 9): the frozen K036 F1 / D5w line-1 reference list re-run on Khipu Field
Guide data. Pre-registered in case-file/K077-kfg-k036-f1.md BEFORE any real KFG D5w statistic was computed.
Detector, null, p-construction, BH family and gates copied from tools/k054_multinumber_k036_f1.py (all-False mask =
K036 unmasked D5w); KFG pendants/groups exactly as tools/k072_kfg_line2_corpus.py (K071 loader).
Usage (from expeditions/khipu):  python3 tools/k077_kfg_k036_f1.py data/khipu.db {fixture|smoke|all}
  fixture = G0 hashes + F0 engine fixture on OKR + KFG data gates + population counts (no D5w on KFG values)
  smoke   = fixture, then the pipeline on KFG values SHUFFLED within each khipu, K = 200 (syntax check only)
  all     = fixture, gates (seed 6435), KFG scan (seed 6436), summary.  Checkpoint analysis/k077_checkpoint.json.
Seeds 6435 (gates), 6436 (scan); next free 6437."""
import sqlite3, sys, json, time, os, hashlib, re, glob, zipfile
import numpy as np, xml.etree.ElementTree as ET
from collections import defaultdict
from math import sqrt
T0 = time.time()
OKR_DB = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'fixture'
SMOKE = MODE == 'smoke'
OKR_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'
CK = 'analysis/k077_smoke_ck.json' if SMOKE else 'analysis/k077_checkpoint.json'
OUT = 'analysis/k077_smoke.json' if SMOKE else 'analysis/k077_results.json'
SEED_G, SEED_SCAN, NEXT_FREE = 6435, 6436, 6437
K = 200 if SMOKE else 10000; Q = 0.05; CHUNK = 1000; MINP = 10; M_PLANT = 6
K036_F1 = ["KH0322/UR086", "KH0395/UR155", "KH0420/UR182", "KH0428/UR190", "KH0478/UR242", "KH0491/UR255",
           "KH0492/UR256", "KH0502/UR266", "KH0504/UR267B", "KH0506/UR269", "KH0507/UR270", "KH0511/UR273B",
           "KH0513/UR274B", "KH0514/UR275"]
THIRDS = (32.66666666666666, 82.33333333333331)  # K036 OKR stratum cut points (descriptive labels only)

# ---------------- engine (K054 verbatim, mask all-False except where stated) ----------------
_valid_cache = {}
def valid_masks(gids):
    key = gids.tobytes()
    if key in _valid_cache: return _valid_cache[key]
    n = len(gids); vr, vl = [None] * 13, [None] * 13
    for k in range(2, 13):
        r = np.zeros(n, bool); l = np.zeros(n, bool)
        for i in range(n):
            if i + k < n: r[i] = bool(np.all(gids[i:i + k + 1] == gids[i]))
            if i - k >= 0: l[i] = bool(np.all(gids[i - k:i + 1] == gids[i]))
        vr[k], vl[k] = r, l
    _valid_cache[key] = (vr, vl); return vr, vl
def scores_w(V, gids):
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    idx = np.arange(n); big = V >= 10
    w = np.where(big, np.log10(np.maximum(V.astype(np.float64), 1)), 0.0)
    W = np.zeros((B, 11)); vr, vl = valid_masks(gids)
    for k in range(2, 13):
        hk = np.zeros((B, n), bool)
        i = idx[idx + k < n]; i = i[vr[k][i]]
        if len(i): hk[:, i] |= ((P[:, i + k + 1] - P[:, i + 1]) == V[:, i]) & ((NZ[:, i + k + 1] - NZ[:, i + 1]) >= 2)
        i = idx[idx - k >= 0]; i = i[vl[k][i]]
        if len(i): hk[:, i] |= ((P[:, i] - P[:, i - k]) == V[:, i]) & ((NZ[:, i] - NZ[:, i - k]) >= 2)
        hk &= big; W[:, k - 2] = (w * hk).sum(1)
    return W
def colrank_p(N, x):
    Ns = np.sort(N, 0); KK = N.shape[0]
    return np.stack([(KK - np.searchsorted(Ns[:, j], x[:, j] - 1e-9, 'left')) / KK for j in range(N.shape[1])], 1)
def minp_pooled_detail(No, Nn):
    A = np.vstack([No, Nn]); live = A.max(0) > 0
    if not live.any(): return 1.0, int(A.shape[0]), int(A.shape[0])
    A = A[:, live]; pa = colrank_p(A, A).min(1); cnt = int((pa <= pa[0] + 1e-12).sum())
    return float(cnt / A.shape[0]), cnt, int(A.shape[0])
def perm(rng, v, B): return v[rng.random((B, len(v))).argsort(1)]
def d5w_p(rng, x, gids):
    Wow = scores_w(x[None], gids); out = []; left = K
    while left > 0:
        m = min(CHUNK, left); out.append(scores_w(perm(rng, x, m), gids)); left -= m
    p, cnt, denom = minp_pooled_detail(Wow, np.vstack(out))
    return p, cnt, denom, (sqrt(p * (1 - p) / denom) if 0 < p < 1 else 0.0), float(Wow.sum())
def bh(pvals, q=Q):
    p = np.asarray(pvals, float); m = len(p); sig = np.zeros(m, bool)
    if m == 0: return sig
    o = np.argsort(p); ok = p[o] <= q * np.arange(1, m + 1) / m
    if ok.any(): sig[o[:np.max(np.nonzero(ok)[0]) + 1]] = True
    return sig
def group_ranges(gids):
    n, out, i = len(gids), [], 0
    while i < n:
        j = i
        while j < n and gids[j] == gids[i]: j += 1
        out.append((i, j)); i = j
    return out
def _fill(rng, pl, sl, st):
    blk = pl[sl].copy()
    if (blk > 0).sum() < 2: blk[:] = np.maximum(blk, rng.integers(1, 30, len(blk)))
    s = int(blk.sum())
    if s < 10: blk[0] += 10 - s; s = int(blk.sum())
    pl[sl] = blk; pl[st] = s
def plant_within_m(rng, v, gids, m):  # K054 plant_within_m_masked with an all-False mask (= K036 plant_within_m)
    pl = perm(rng, v, 1)[0]; ranges = group_ranges(gids)
    for _ in range(m):
        spec = 'A_within' if rng.random() < 0.5 else 'B_within'; ch = []
        if spec == 'A_within':
            for a, b in ranges:
                if (b - a) < 5: continue
                for st in range(a, b - 3): ch.append((st, 3, True))
        else:
            for a, b in ranges:
                for k in range(2, min(10, b - a - 1) + 1):
                    if b - a < k + 2: continue
                    for st in range(a, b - k): ch.append((st, k, True))
                    for st in range(a + k, b): ch.append((st, k, False))
        if not ch: return None
        st, k, right = ch[int(rng.integers(0, len(ch)))]
        if right: _fill(rng, pl, slice(st + 1, st + 1 + k), st)
        else: _fill(rng, pl, slice(st - k, st), st)
    return pl
def gid_from_runs(labels):
    g = np.empty(len(labels), np.int32); gi, last = -1, object()
    for i, x in enumerate(labels):
        if x != last: gi += 1; last = x
        g[i] = gi
    return g
def n_ge4(gids): return sum(1 for a, b in group_ranges(gids) if b - a >= 4)
def stratum(n): return 'small' if n <= THIRDS[0] else ('mid' if n <= THIRDS[1] else 'large')
res = dict(cycle='K077', mode=MODE, design=dict(K=K, q=Q, seeds=dict(gates=SEED_G, scan=SEED_SCAN), next_free_seed=NEXT_FREE,
           m_plant=M_PLANT, p_construction='pooled_exchangeable (K033/K036)', groups='KFG CordGroups spans (K071)',
           universe='pop: >= 10 nonzero pendants and >= 2 groups of size >= 4 (K036)'))
def dump(): res['secs'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1, default=str)
def stop(r): res['stopped'] = r; dump(); print('STOP:', r, flush=True); sys.exit(0)

# ---------------- G0 + F0 on OKR ----------------
h_okr = hashlib.sha256(open(OKR_DB, 'rb').read()).hexdigest(); h_kfg = hashlib.sha256(open(KFG_DB, 'rb').read()).hexdigest()
G0 = dict(okr_sha_ok=h_okr == OKR_SHA, kfg_sha_ok=h_kfg == KFG_SHA)
if not (G0['okr_sha_ok'] and G0['kfg_sha_ok']): res['G0'] = G0; stop('hash mismatch')
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
okr_pop = {k for k, (v, g) in okr_elig.items() if n_ge4(g) >= 2}
k036 = json.load(open('analysis/k036_results.json')); k054 = json.load(open('analysis/k054_results.json'))
k036_pop = {r['khipu_id'] for r in k036['rows'] if r['stratum'] != 'S0'}
rep = sum(np.isclose(float(scores_w(okr_elig[r['khipu_id']][0][None], okr_elig[r['khipu_id']][1]).sum()), r['stat_D5w_unmasked'])
          for r in k054['rows'])
okr_stat14 = {}
for khid in okr_pop:
    lab = names[khid][0] + '/' + names[khid][1]
    if lab in K036_F1: okr_stat14[names[khid][0]] = float(scores_w(okr_elig[khid][0][None], okr_elig[khid][1]).sum())
F0 = dict(n_eligible=len(okr_elig), n_pop=len(okr_pop), pop_ids_equal_k036=okr_pop == k036_pop,
          f1_list_equal=list(k036['real']['hits']['F1']) == K036_F1, k054_stat_reproduced=f'{rep}/{len(k054["rows"])}',
          names_found=len(okr_stat14))
F0['pass'] = bool(F0['n_eligible'] == 457 and F0['n_pop'] == 378 and F0['pop_ids_equal_k036'] and F0['f1_list_equal']
                  and rep == len(k054['rows']) and len(okr_stat14) == 14)
res['G0'] = G0; res['F0_engine_on_okr'] = F0; res['okr_stat_D5w_14'] = okr_stat14
print('G0', G0, 'F0', F0, round(time.time() - T0, 1), flush=True)
if not F0['pass']: stop('F0 engine fixture on OKR failed')

# ---------------- KFG data (K071/K072 loader verbatim, R5 not used) ----------------
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
f1_kfg = {nm.split('/')[0]: nm for nm in K036_F1}
data = dict(n_kfg_khipus=len(sha), n_grouped=len(groups), n_eligible=len(kfg_elig), n_pop=len(kfg_pop),
            n_pop_okr_shared=sum(x in okr_num for x in kfg_pop), n_pop_kfg_only=sum(x not in okr_num for x in kfg_pop),
            f1_in_pop=sorted(x for x in f1_kfg if x in kfg_pop), f1_not_in_pop=sorted(x for x in f1_kfg if x not in kfg_pop),
            f1_not_in_kfg=sorted(x for x in f1_kfg if x not in sha),
            f1_identical_values=sorted(x for x in f1_kfg if x in kfg_elig and any(names[o][0] == x for o in okr_elig)
                                       and np.array_equal(kfg_elig[x][0], okr_elig[[o for o in okr_elig if names[o][0] == x][0]][0])),
            f1_identical_groups=sorted(x for x in f1_kfg if x in kfg_elig and any(names[o][0] == x for o in okr_elig)
                                       and np.array_equal(kfg_elig[x][1], okr_elig[[o for o in okr_elig if names[o][0] == x][0]][1])))
gates['pass_data'] = gates['G0_xlsx_hash_mismatch'] == 0 and gates['G1_partition_rate'] >= 0.95
res['data_gates'] = gates; res['data'] = data
print('data gates', {a: b for a, b in gates.items() if a != 'G1_bad'}, flush=True); print('data', data, flush=True)
if not gates['pass_data']: stop('KFG data gate failed')
if MODE == 'fixture': dump(); print('fixture done', round(time.time() - T0, 1)); sys.exit(0)
if SMOKE:
    sr = np.random.default_rng(0)
    for x in kfg_pop: kfg_elig[x] = (sr.permutation(kfg_elig[x][0]), kfg_elig[x][1])
ck = json.load(open(CK)) if os.path.exists(CK) else {}
def save(): json.dump(ck, open(CK, 'w'), indent=1)

# ---------------- G1 calibration FPR / G2 planted power at m = 6 (K054 gates, mask empty) ----------------
if 'gates' not in ck:
    rng = np.random.default_rng(SEED_G); cal, pw, skipped = [], [], []
    for j, x in enumerate(kfg_pop):
        v, g = kfg_elig[x]
        cal.append(d5w_p(rng, perm(rng, v, 1)[0], g)[0])
        pl = plant_within_m(rng, v, g, M_PLANT)
        if pl is None: skipped.append(x)
        else: pw.append(d5w_p(rng, pl, g)[0])
        if (j + 1) % 50 == 0: print('gates', j + 1, '/', len(kfg_pop), round(time.time() - T0, 1), 's', flush=True)
    cal, pw = np.asarray(cal), np.asarray(pw)
    G = dict(calib_n=len(cal), fpr=float(np.mean(cal <= 0.05)), calib_bh_flags=int(bh(cal).sum()),
             plant_n=len(pw), plant_skipped=skipped, power=float(np.mean(pw <= 0.05)) if len(pw) else None,
             power_bh=float(np.mean(bh(np.concatenate([pw, cal]))[:len(pw)])) if len(pw) else None)
    G['G1'] = bool(G['fpr'] <= 0.05); G['G2'] = bool(G['plant_n'] >= 30 and G['power'] is not None and G['power'] >= 0.50)
    ck['gates'] = G; save()
res['gates'] = ck['gates']; print('gates', {a: b for a, b in ck['gates'].items() if a != 'plant_skipped'}, round(time.time() - T0, 1), flush=True)

# ---------------- KFG scan ----------------
if 'scan' not in ck:
    rng = np.random.default_rng(SEED_SCAN); rows = []
    for j, x in enumerate(kfg_pop):
        v, g = kfg_elig[x]; p, cnt, denom, se, st = d5w_p(rng, v, g)
        rows.append(dict(khipu=x, in_okr=x in okr_num, n_pend=len(v), stratum=stratum(len(v)), n_groups_ge4=n_ge4(g),
                         stat_D5w=st, p=p, cnt=cnt, denom=denom, se=se))
        if (j + 1) % 50 == 0: print('scan', j + 1, '/', len(kfg_pop), round(time.time() - T0, 1), 's', flush=True)
    for r, s in zip(rows, bh([r['p'] for r in rows])): r['bh_sig'] = bool(s)
    ck['scan'] = rows; save()
rows = {r['khipu']: r for r in ck['scan']}
ps = np.array([r['p'] for r in ck['scan']]); o = np.sort(ps); thr = Q * np.arange(1, len(ps) + 1) / len(ps)
okk = o <= thr; rank = int(np.max(np.nonzero(okk)[0]) + 1) if okk.any() else 0
G = ck['gates']
def fate(x):
    if x not in rows: return 'NOT TESTABLE'
    if not (G['G1'] and G['G2']): return 'NOT TESTABLE (gate)'
    return 'REPLICATED' if rows[x]['bh_sig'] else 'CHANGED (not BH-significant on KFG)'
names14 = [dict(name=f1_kfg[x], kfg=x, fate=fate(x), stat_okr=okr_stat14.get(x), stat_kfg=rows.get(x, {}).get('stat_D5w'),
                p_okr=[r['p_D5w'] for r in k036['rows'] if r['okr'] == x][0], p_kfg=rows.get(x, {}).get('p'),
                identical_values=x in data['f1_identical_values'], identical_groups=x in data['f1_identical_groups'])
           for x in sorted(f1_kfg)]
new = sorted(x for x, r in rows.items() if r['bh_sig'] and x not in f1_kfg)
summary = dict(n_tested=len(rows), n_bh=int(sum(r['bh_sig'] for r in rows.values())), bh_rank=rank,
               bh_bar=float(thr[rank - 1]) if rank else None,
               replicated=sum(n['fate'] == 'REPLICATED' for n in names14),
               changed=sum(n['fate'].startswith('CHANGED') for n in names14),
               not_testable=sum(n['fate'].startswith('NOT TESTABLE') for n in names14),
               new_okr_shared=[x for x in new if rows[x]['in_okr']], new_kfg_only=[x for x in new if not rows[x]['in_okr']],
               gates_pass=bool(G['G1'] and G['G2']))
res['summary'] = summary; res['names14'] = names14; res['rows'] = ck['scan']; dump()
print(json.dumps(summary, indent=1))
for n in names14: print('F1', n)
print('seconds', round(time.time() - T0, 1), flush=True)
