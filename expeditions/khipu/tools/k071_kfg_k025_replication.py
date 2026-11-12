#!/usr/bin/env python3
"""K071 - KFG re-audit of K025 (whole-group sums), pre-registered in case-file/K071-kfg-replication-k025.md.
Statistic, null (within-khipu pendant permutation), controls and BH rule verbatim from tools/k025_whole_group_sums.py,
on Khipu Field Guide data: pendants ^p\\d+$ from the K068 store, groups from each Excel CordGroups sheet (K069 parser).
Usage: python3 tools/k071_kfg_k025_replication.py data/khipu.db [out.json]. Seed 6419 (next free 6420)."""
import sqlite3, json, sys, re, glob, zipfile, hashlib, time
import numpy as np, xml.etree.ElementTree as ET
from collections import defaultdict
T0 = time.time(); KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
OKR_DB = sys.argv[1] if len(sys.argv) > 1 else 'data/khipu.db'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'analysis/k071_results.json'
SEED = 6419; rng = np.random.default_rng(SEED); R = 20000; NC = 200; RS = 5000; E_RATE = (23 - 14.1067) / 367
okr = {r[0] for r in sqlite3.connect(OKR_DB).execute('select OKR_NUM from khipu_main') if r[0]}
k069 = json.load(open('analysis/k069_results.json'))['summary']; K069_NAMES = set(k069['okr_k001_bh']) | set(k069['new_kfg_bh_names'])
c = sqlite3.connect(KFG_DB); sha = dict(c.execute('select name, sha256 from khipu'))
PEN = re.compile(r'^p(\d+)$'); pend = defaultdict(list)
for kh, nm, v in c.execute('select khipu, cord_name, value from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0
    pend[kh].append((int(m.group(1)), x))
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
GRP = re.compile(r'^[\d.]+cm group of (\d+) pendants \((\d+)-(\d+)\)'); ONE = re.compile(r'^[\d.]+cm 1 \((\d+)\)')
def sheet_strings(f, name):
    z = zipfile.ZipFile(f); wb = ET.fromstring(z.read('xl/workbook.xml'))
    i = [s.get('name') for s in wb.iter(NS + 'sheet')].index(name) + 1
    ss = [''.join(x.text or '' for x in si.iter(NS + 't')) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(NS + 'si')] if 'xl/sharedStrings.xml' in z.namelist() else []
    out = []
    for cc in ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).iter(NS + 'c'):
        v = cc.find(NS + 'v')
        if cc.get('t') == 's' and v is not None: out.append(ss[int(v.text)])
        elif cc.get('t') == 'inlineStr': out.append(''.join(x.text or '' for x in cc.iter(NS + 't')))
        elif v is not None: out.append(v.text)
    return out
g0_bad = []; g1_bad = []; groups = {}
for f in sorted(glob.glob(f'{XLSX}/*.xlsx')):
    kh = f.split('/')[-1][:-5]
    if hashlib.sha256(open(f, 'rb').read()).hexdigest() != sha.get(kh): g0_bad.append(kh); continue
    spans = []
    for s in sheet_strings(f, 'CordGroups'):
        m = GRP.match(s)
        if m: spans.append((int(m.group(2)), int(m.group(3))))
        else:
            m = ONE.match(s)
            if m: spans.append((int(m.group(1)), int(m.group(1))))
    L = pend.get(kh, []); n = len(L)
    if n and [p for p, _ in L] == list(range(1, n + 1)) and [p for a, b in spans for p in range(a, b + 1)] == list(range(1, n + 1)):
        groups[kh] = [(a - 1, b) for a, b in spans]
    elif n: g1_bad.append(kh)
print('parsed', len(groups), 'G1 bad', len(g1_bad), 'G0 bad', len(g0_bad), round(time.time() - T0, 1), flush=True)
# ---------- K025 machinery (verbatim logic; groups given as [s, e) spans) ----------
def prep(gs, n):
    pairs = []
    for s, e in gs:
        if e - s < 2: continue
        if s - 1 >= 0: pairs.append((s - 1, s, e))
        if e < n: pairs.append((e, s, e))
    return np.array(pairs, np.int64).reshape(-1, 3)
def Ghits(V, pr):
    B, n = V.shape; H = np.zeros((B, n), bool)
    if len(pr) == 0: return H
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    Z = np.zeros((B, n + 1), np.int64); Z[:, 1:] = np.cumsum(V > 0, 1)
    i, s, e = pr[:, 0], pr[:, 1], pr[:, 2]; vi = V[:, i]
    hit = (vi >= 10) & (vi == P[:, e] - P[:, s]) & ((Z[:, e] - Z[:, s]) >= 2)
    for k in range(len(pr)): H[:, i[k]] |= hit[:, k]
    return H
def G(V, pr): return Ghits(V, pr).sum(1)
def perm(v, B): return v[np.argsort(rng.random((B, len(v))), 1)]
def pv(o, nl): return float((1 + (nl >= o).sum()) / (1 + len(nl)))
def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps); o = np.argsort(ps); ok = ps[o] <= q * np.arange(1, m + 1) / m
    kk = np.max(np.where(ok)[0]) + 1 if ok.any() else 0; s = np.zeros(m, bool); s[o[:kk]] = True; return s
def plant(v, pr):
    x = rng.permutation(v).copy(); i, s, e = pr[rng.integers(len(pr))]
    blk = x[s:e]
    if (blk > 0).sum() < 2: blk[:2] = np.maximum(blk[:2], rng.integers(1, 30, 2))
    if blk.sum() < 10: blk[0] += 10 - blk.sum()
    x[s:e] = blk; x[i] = blk.sum(); return x
def vec(kh): return np.array([x for _, x in pend[kh]], np.int64)
res = dict(seed=SEED, next_free_seed=SEED + 1, R=R, primary={})
K025 = {'KH0359': [416, 390, 406, 481], 'KH0405': [658, 612, 805, 17]}
for nm in ('KH0359', 'KH0405'):
    if nm not in groups: res['primary'][nm] = dict(verdict='NOT TESTABLE (data)', reason='missing or G1 fail'); continue
    v = vec(nm); gs = groups[nm]; pr = prep(gs, len(v))
    hm = Ghits(v[None], pr)[0]; o = int(hm.sum()); nl = G(perm(v, R), pr); p = pv(o, nl)
    cal = sum(pv(int(G(rng.permutation(v)[None], pr)[0]), nl) <= 0.025 for _ in range(NC)) / NC
    pw = sum(pv(int(G(plant(v, pr)[None], pr)[0]), nl) <= 0.025 for _ in range(NC)) / NC
    hits = [dict(pendant=f'p{j + 1}', value=int(v[j])) for j in np.where(hm)[0]]
    res['primary'][nm] = dict(n_pend=len(v), n_groups=len(gs), n_candidate_pairs=len(pr), G=o, null_mean=float(nl.mean()), p=p,
                              calib_fpr=cal, power_1planted=pw, hits=hits, k025_values=K025[nm],
                              values_match_k025=sorted(h['value'] for h in hits) == sorted(K025[nm]),
                              verdict='REPLICATED' if p <= 0.025 else 'NOT REPLICATED' if pw >= 0.5 else 'NOT TESTABLE')
print(json.dumps(res['primary'], indent=1), round(time.time() - T0, 1), flush=True)
rows = []; null = {}; cal_p = []
for kh in sorted(groups):
    gs = groups[kh]
    if len(gs) < 4: continue
    v = vec(kh); pr = prep(gs, len(v))
    if len(pr) == 0 or (v >= 10).sum() == 0: continue
    o = int(G(v[None], pr)[0]); nl = G(perm(v, RS), pr); null[kh] = (v, pr, nl)
    cal_p.append(pv(int(G(rng.permutation(v)[None], pr)[0]), nl))
    rows.append(dict(khipu=kh, heldout=kh not in okr, G=o, null_mean=float(nl.mean()), p=pv(o, nl)))
sig = bh([r['p'] for r in rows])
for r, s in zip(rows, sig): r['bh'] = bool(s)
def tot(sel):
    o = sum(r['G'] for r in sel); n = sum(null[r['khipu']][2] for r in sel) if sel else np.zeros(RS, np.int64)
    return dict(n_khipus=len(sel), G_total=o, null_mean=float(n.mean()), p=pv(o, n)), n
T2, _ = tot(rows); T2b, _ = tot([r for r in rows if r['khipu'] not in K025]); HO = [r for r in rows if r['heldout']]; T3, n3 = tot(HO)
m = max(1, round(E_RATE * len(HO))); hits_pw = 0; NP = 200
for _ in range(NP):
    pick = set(rng.choice(len(HO), min(m, len(HO)), replace=False)) if HO else set(); o = 0
    for j, r in enumerate(HO):
        v, pr, _n = null[r['khipu']]
        o += int(G((plant(v, pr) if j in pick else rng.permutation(v))[None], pr)[0])
    hits_pw += pv(o, n3) <= 0.05
T3.update(m_planted=m, e_rate=E_RATE, power_05=hits_pw / NP)
T3['verdict'] = ('NOT TESTABLE (data-limited)' if T3['power_05'] < 0.5 else 'ESTABLISHED (held-out)' if T3['p'] <= 0.01
                 else 'SUGGESTIVE' if T3['p'] <= 0.05 else 'NOT REPLICATED (powered negative)')
bhset = sorted(r['khipu'] for r in rows if r['bh'])
gates = dict(G0_hash_mismatch=len(g0_bad), G1_partition_rate=len(groups) / (len(groups) + len(g1_bad)), G1_bad=g1_bad,
             G2_primary_fpr={k: v.get('calib_fpr') for k, v in res['primary'].items()})
gates['pass'] = gates['G0_hash_mismatch'] == 0 and gates['G1_partition_rate'] >= 0.95 and all((x is None) or x <= 0.05 for x in gates['G2_primary_fpr'].values())
nrep = sum(v['verdict'] == 'REPLICATED' for v in res['primary'].values())
res.update(T2=T2, T2b=T2b, T3=T3, n_bh=len(bhset), bh_khipus=bhset, calib_bh_false=int(bh(cal_p).sum()),
           calib_fpr_05=float(np.mean(np.array(cal_p) <= 0.05)), overlap_k069=sorted(set(bhset) & K069_NAMES),
           top=sorted(rows, key=lambda r: r['p'])[:12], gates=gates,
           headline=('REPLICATED' if nrep == 2 else 'CHANGED' if nrep == 1 else 'NOT REPLICATED') if gates['pass'] else 'VOID (gate fail)',
           seconds=round(time.time() - T0, 1))
json.dump(dict(summary=res, rows=rows), open(OUT, 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ('primary', 'top')}, indent=1))
for r in res['top']: print(r)
