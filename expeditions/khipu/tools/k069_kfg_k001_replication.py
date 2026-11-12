#!/usr/bin/env python3
"""K069 - KFG re-audit of K001 (adjacent sum cords), pre-registered in case-file/K069-kfg-replication-k001.md.
Same statistic, nulls, controls and BH rule as tools/k001_sum_cords.py (amendment A1, K = 5000), on Khipu Field Guide data.
Input: KFG store /workspace/kfg/kfg_20261111.db (K068 loader) + the per-khipu Excel files in /workspace/kfg/xlsx
(only the CordGroups sheet is read from Excel, for the N2 group-order null). Seed 6417 (next free 6418).
Pendant = cord whose Cord_Name matches ^p\\d+$, in sheet order; value = KFG 'Value' column (integer; blank -> 0)."""
import sqlite3, json, sys, re, glob, zipfile, hashlib, time
import numpy as np, xml.etree.ElementTree as ET
from collections import defaultdict
T0 = time.time()
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'; OKR_DB = sys.argv[1] if len(sys.argv) > 1 else 'data/khipu.db'
K = int(sys.argv[2]) if len(sys.argv) > 2 else 5000; KMAX = 12; SEED = 6417; MINP = 10
OUT = sys.argv[3] if len(sys.argv) > 3 else 'analysis/k069_results.json'
rng = np.random.default_rng(SEED)
k1 = json.load(open('analysis/k001_results_K5000.json'))
okr_rows = {r['khipu_id']: r for r in k1['rows']}
oc = sqlite3.connect(OKR_DB)
okr_name = {r[0]: r[1] for r in oc.execute('select KHIPU_ID, OKR_NUM from khipu_main')}
OKR_K001_BH = sorted(okr_name[r['khipu_id']] for r in k1['rows'] if r['bh_sig_N1'])
OKR_TESTED = {okr_name[r['khipu_id']] for r in k1['rows']}

# ---------- load KFG ----------
c = sqlite3.connect(KFG_DB)
sha = {n: s for n, s in c.execute('select name, sha256 from khipu')}
PEN = re.compile(r'^p(\d+)$'); bad_val = 0; nonseq = []
pend = defaultdict(list)
for kh, idx, nm, v in c.execute('select khipu, idx, cord_name, value from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0; bad_val += 1
    pend[kh].append((int(m.group(1)), x))
for kh, L in pend.items():
    if [p for p, _ in L] != list(range(1, len(L) + 1)): nonseq.append(kh)

# ---------- CordGroups from Excel (G0 hash check, G1 partition check) ----------
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
g0_bad = []; groups = {}; g1_bad = []
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
    n = len(pend.get(kh, []))
    cover = [p for a, b in spans for p in range(a, b + 1)]
    if cover == list(range(1, n + 1)): groups[kh] = spans
    else: g1_bad.append(kh)

# ---------- K001 machinery (verbatim logic) ----------
def S_batch(V):
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    hit = np.zeros((B, n), bool); idx = np.arange(n)
    for k in range(2, KMAX + 1):
        ok = idx + k < n; i = idx[ok]
        s = P[:, i + k + 1] - P[:, i + 1]; z = NZ[:, i + k + 1] - NZ[:, i + 1]
        hit[:, i] |= (s == V[:, i]) & (z >= 2)
        ok = idx - k >= 0; i = idx[ok]
        s = P[:, i] - P[:, i - k]; z = NZ[:, i] - NZ[:, i - k]
        hit[:, i] |= (s == V[:, i]) & (z >= 2)
    hit &= V >= 10
    return hit.sum(1)
def n1(v, B): return np.array([rng.permutation(v) for _ in range(B)])
def n2(gs, B):
    out = []
    for _ in range(B):
        o = rng.permutation(len(gs)); out.append(np.concatenate([gs[j] for j in o]))
    return np.array(out)
def pval(obs, null): return (1 + (null >= obs).sum()) / (1 + len(null))
def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps)
    if m == 0: return np.zeros(0, bool)
    o = np.argsort(ps); thr = q * np.arange(1, m + 1) / m
    passed = ps[o] <= thr; kmax = np.max(np.where(passed)[0]) + 1 if passed.any() else 0
    sig = np.zeros(m, bool); sig[o[:kmax]] = True; return sig

rows = []
for kh in sorted(pend):
    if kh in g0_bad: continue
    v = np.array([x for _, x in pend[kh]], np.int64)
    if (v > 0).sum() < MINP: continue
    gs = [v[a - 1:b] for a, b in groups[kh]] if kh in groups else None
    obs = int(S_batch(v[None])[0])
    s1 = S_batch(n1(v, K)); p1 = pval(obs, s1)
    p2 = pval(obs, S_batch(n2(gs, K))) if gs is not None and len(gs) >= 4 else None
    fake = rng.permutation(v); pc = pval(int(S_batch(fake[None])[0]), S_batch(n1(fake, K)))
    pp = None
    if len(v) >= 20:
        pl = rng.permutation(v).copy()
        for st in rng.choice(np.arange(0, len(v) - 4), 2, replace=False):
            blk = pl[st + 1: st + 4]
            if (blk > 0).sum() < 2: blk[:] = np.maximum(blk, rng.integers(1, 30, 3))
            pl[st + 1: st + 4] = blk; pl[st] = blk.sum() if blk.sum() >= 10 else blk.sum() + 10
            if pl[st] != blk.sum(): pl[st + 1] += pl[st] - blk.sum()
        pp = pval(int(S_batch(pl[None])[0]), S_batch(n1(pl, K)))
    rows.append(dict(khipu=kh, n_pend=len(v), n_nonzero=int((v > 0).sum()), n_groups=len(gs) if gs is not None else None,
                     S_obs=obs, S_null_mean=float(s1.mean()), p_N1=p1, p_N2=p2, p_calib=pc, p_planted=pp, okr_shared=kh in okr_name.values()))
sig = bh([r['p_N1'] for r in rows])
for r, s in zip(rows, sig): r['bh_sig_N1'] = bool(s)
r2 = [r for r in rows if r['p_N2'] is not None]; sig2 = bh([r['p_N2'] for r in r2])
for r, s in zip(r2, sig2): r['bh_sig_N2'] = bool(s)
rs = [r for r in rows if r['okr_shared']]; sigs = bh([r['p_N1'] for r in rs])  # S1: BH over shared ids only
for r, s in zip(rs, sigs): r['bh_sig_N1_shared'] = bool(s)
by = {r['khipu']: r for r in rows}

# ---------- R1 per-name classification ----------
cls = {}
for nm in OKR_K001_BH:
    r = by.get(nm)
    if r is None: cls[nm] = 'NOT TESTABLE'
    elif r['bh_sig_N1']: cls[nm] = 'REPLICATED'
    elif r['p_N1'] <= 0.05: cls[nm] = 'WEAKENED'
    else: cls[nm] = 'NOT REPLICATED'
nrep = sum(v == 'REPLICATED' for v in cls.values())
calib = np.array([r['p_calib'] for r in rows]); plant = np.array([r['p_planted'] for r in rows if r['p_planted'] is not None])
g1_rate = 1 - len([k for k in g1_bad if k in by]) / len(rows)
gates = dict(G0_hash_mismatch=len(g0_bad), G1_partition_rate=g1_rate, G1_pass=g1_rate >= 0.95,
             G2_calib_fpr=float((calib <= 0.05).mean()), G2_pass=float((calib <= 0.05).mean()) <= 0.05)
ok = gates['G1_pass'] and gates['G2_pass'] and gates['G0_hash_mismatch'] == 0
verdict = 'GATES FAIL' if not ok else ('REPLICATED' if nrep >= 8 else 'PARTLY REPLICATED' if nrep >= 5 else 'NOT REPLICATED')
new_names = sorted(r['khipu'] for r in rows if r['bh_sig_N1'] and r['khipu'] not in OKR_K001_BH)
summary = dict(K=K, seed=SEED, next_free_seed=6418, n_tested=len(rows), n_tested_shared=len(rs), bad_values=bad_val, nonseq_pendant_names=nonseq,
               g1_bad=g1_bad, gates=gates, calib_bh_sig=int(bh(calib).sum()), planted_power_05=float((plant <= 0.05).mean()), planted_n=len(plant),
               n_p05_N1=int(sum(r['p_N1'] <= 0.05 for r in rows)), n_bh_N1=int(sig.sum()), n_bh_N1_sharedonly=int(sigs.sum()),
               n_tested_N2=len(r2), n_bh_N2=int(sig2.sum()), bh_N2_names=sorted(r['khipu'] for r in r2 if r['bh_sig_N2']),
               okr_k001_bh=OKR_K001_BH, R1=cls, n_replicated=nrep, verdict=verdict, new_kfg_bh_names=new_names,
               new_names_okr_status={n: ('tested, p_N1 %.4g' % okr_rows[[k for k, o in okr_name.items() if o == n][0]]['p_N1']
                                         if any(o == n and k in okr_rows for k, o in okr_name.items()) else ('in OKR, not tested' if n in okr_name.values() else 'KFG-only'))
                                     for n in new_names},
               total_S_obs=int(sum(r['S_obs'] for r in rows)), total_S_null=float(sum(r['S_null_mean'] for r in rows)), seconds=round(time.time() - T0, 1))
json.dump(dict(summary=summary, rows=rows), open(OUT, 'w'), indent=1)
print(json.dumps(summary, indent=1))
