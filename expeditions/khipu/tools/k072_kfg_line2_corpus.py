#!/usr/bin/env python3
"""K072 - KFG re-audit step 4 (README line 9): the line-2 corpus verdicts K040 (H1 pooled holdout G, H2 per-khipu BH),
K042 (H1 singleton-total G_s, H2 non-singleton G_ns, Bonferroni x2) and K056 (R5 multi-number mask: KH0359, KH0405,
masked G, masked G_s) re-run on Khipu Field Guide data. Pre-registered in case-file/K072-kfg-line2-corpus.md.
Statistic, nulls, controls and decision rules copied from tools/k040_holdout_wholegroup.py, tools/k042_singleton_count.py
and tools/k056_multinumber_wholegroup.py; KFG pendants/groups exactly as tools/k071_kfg_k025_replication.py.
Usage: python3 tools/k072_kfg_line2_corpus.py data/khipu.db [--smoke]
Seeds 6420 (unmasked nulls), 6421 (unmasked calibration), 6422 (unmasked power), 6423 (masked arms). Next free 6424."""
import sqlite3, json, sys, re, glob, zipfile, hashlib, time
import numpy as np, xml.etree.ElementTree as ET
from collections import defaultdict
T0 = time.time(); KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
OKR_DB = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'data/khipu.db'
SMOKE = '--smoke' in sys.argv
OUT = 'analysis/k072_smoke.json' if SMOKE else 'analysis/k072_results.json'
OKR_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
DISC = ('KH0359', 'KH0405')
R_C = 300 if SMOKE else 10000; R_T = 1000 if SMOKE else 20000; NC = 10 if SMOKE else 200; NP = 10 if SMOKE else 200
MIN_N = 1 if SMOKE else 30; M = 9; WALL = 540
SEEDS = dict(nulls=6420, calib=6421, power=6422, masked=6423); NEXT_FREE = 6424
# published OKR values (K040, K042, K056 results JSON)
PUB = dict(K040_H1=dict(G=23, null_mean=14.1067, p=0.0162, verdict='supported'),
           K040_H2=dict(n_bh=0, verdict='not supported'),
           K042_H1=dict(G_s=10, null_mean=1.7338, p=9.999e-05, verdict='supported'),
           K042_H2=dict(G_ns=13, null_mean=12.3305, p=0.4608, verdict='not supported'),
           K056_KH0359=dict(G=4, verdict='survives'), K056_KH0405=dict(G=4, verdict='survives'),
           K056_G=dict(G=18, null_mean=12.7355, p=0.0955, verdict='no longer established'),
           K056_G_s=dict(G=10, null_mean=1.5118, p=0.0002, verdict='survives'))
res = dict(design=dict(seeds=SEEDS, next_free_seed=NEXT_FREE, R_corpus=R_C, R_primary=R_T, N_cal=NC, N_pow=NP, m=M, smoke=SMOKE),
           published_okr=PUB)
def dump():
    res['secs'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1)
def stop(reason):
    res['decision'] = dict(excluded=True, reason=reason); dump(); print('EXCLUDED:', reason, flush=True); sys.exit(0)

# ---------------- statistic (K025/K040/K042/K056 verbatim; groups as [s, e) spans) ----------------
def prep(gs, n):
    pairs = []
    for s, e in gs:
        if e - s < 2: continue
        if s - 1 >= 0: pairs.append((s - 1, s, e))
        if e < n: pairs.append((e, s, e))
    return np.array(pairs, np.int64).reshape(-1, 3)
def legal(pr, bad):
    if len(pr) == 0: return pr
    keep = [k for k in range(len(pr)) if not bad[pr[k, 0]] and not bad[pr[k, 1]:pr[k, 2]].any()]
    return pr[keep].reshape(-1, 3)
def hitH(V, pr):
    B, n = V.shape; H = np.zeros((B, n), bool)
    if len(pr) == 0: return H
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    Z = np.zeros((B, n + 1), np.int64); Z[:, 1:] = np.cumsum(V > 0, 1)
    i, s, e = pr[:, 0], pr[:, 1], pr[:, 2]; vi = V[:, i]
    hit = (vi >= 10) & (vi == P[:, e] - P[:, s]) & ((Z[:, e] - Z[:, s]) >= 2)
    for k in range(len(pr)): H[:, i[k]] |= hit[:, k]
    return H
def stats(V, pr, sing):  # -> G, G_s, G_ns
    H = hitH(V, pr); g = H.sum(1).astype(np.int64); gs = H[:, sing].sum(1).astype(np.int64); return g, gs, g - gs
def permmask(rng, v, bad, B):
    free = np.where(~bad)[0]; out = np.tile(v, (B, 1))
    if len(free): out[:, free] = v[free][rng.random((B, len(free))).argsort(1)]
    return out
def pv(o, nl): nl = np.asarray(nl); return float((1 + (nl >= o).sum()) / (1 + len(nl)))
def bh(ps, q=0.05):
    ps = np.asarray(ps, float); m = len(ps); o = np.argsort(ps); ok = ps[o] <= q * np.arange(1, m + 1) / m
    kk = int(np.max(np.where(ok)[0]) + 1) if ok.any() else 0; s = np.zeros(m, bool); s[o[:kk]] = True; return s
def plant_pair(x, i, s, e, rng):
    x = x.copy(); blk = x[s:e].copy()
    if (blk > 0).sum() < 2: blk[:2] = np.maximum(blk[:2], rng.integers(1, 30, 2))
    if int(blk.sum()) < 10: blk[0] += 10 - int(blk.sum())
    x[s:e] = blk; x[i] = int(blk.sum()); return x
def plant_k(x, pr, k, rng):
    used = set(); planted = 0
    for idx in rng.permutation(len(pr)):
        i, s, e = [int(t) for t in pr[idx]]; span = set(range(s, e)) | {i}
        if used & span: continue
        x = plant_pair(x, i, s, e, rng); used |= span; planted += 1
        if planted >= k: break
    return x, planted
def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
def singles(gs, n):
    s = np.zeros(n, bool)
    for a, b in gs:
        if b - a == 1: s[a:b] = True
    return s
def borderline(p, a, R):  # Kryptos case 191 habit: flag p within 2 Monte Carlo SE of alpha (verdict unchanged)
    return bool(abs(p - a) < 2 * np.sqrt(a * (1 - a) / R))

# ---------------- OKR (engine fixture F0 and R5 gate) ----------------
h = hashlib.sha256(open(OKR_DB, 'rb').read()).hexdigest()
if h != OKR_SHA: stop('OKR hash mismatch ' + h)
c = sqlite3.connect(OKR_DB)
dups = {r[0] for r in c.execute('select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1')}
okrname = {r[0]: r[1] or '' for r in c.execute('select KHIPU_ID, OKR_NUM from khipu_main')}
okr_set = {v for v in okrname.values() if v}
val = defaultdict(int)
for cid, v in c.execute('select CORD_ID, knot_value_type from knot'):
    if v is not None: val[cid] += int(v)
clplaces = defaultdict(set); clcord = {}
for cid, cl, t, v in c.execute('select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot'):
    t = (t or '').strip()
    if t in ('S', 'L', 'E') and v: clplaces[cl].add(place(int(v)) if t == 'S' else 0)
    clcord[cl] = cid
ordn = {r[0]: r[1] for r in c.execute('select CLUSTER_ID, ORDINAL from knot_cluster')}
bycord = defaultdict(dict)
for cl, pl in clplaces.items():
    if len(pl) == 1 and ordn.get(cl) is not None: bycord[clcord[cl]][ordn[cl]] = next(iter(pl))
R5_okr = set()
for cd, d in bycord.items():
    s = [d[o] for o in sorted(d)]
    if len(s) >= 2 and not all(a > b for a, b in zip(s, s[1:])): R5_okr.add(cd)
okr_kh = defaultdict(list)
for kid, cid, cl in c.execute('select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL'):
    if kid in dups: continue
    okr_kh[kid].append((val.get(cid, 0), cl, cid))
def okr_groups(cl):
    g, last = [], object()
    for i, x in enumerate(cl):
        if x != last: g.append([i, i + 1]); last = x
        else: g[-1][1] = i + 1
    return [(a, b) for a, b in g]
okr_elig = []
for kid, cords in okr_kh.items():
    gs = okr_groups([x[1] for x in cords])
    if len(gs) < 4: continue
    v = np.array([x[0] for x in cords], np.int64); pr = prep(gs, len(v))
    if len(pr) == 0 or (v >= 10).sum() == 0: continue
    bad = np.array([x[2] in R5_okr for x in cords])
    okr_elig.append(dict(name=okrname[kid], v=v, pr=pr, prm=legal(pr, bad), bad=bad, sing=singles(gs, len(v))))
oh = [e for e in okr_elig if e['name'] not in DISC]
F0 = dict(n_r5=len(R5_okr), n_eligible=len(okr_elig), n_holdout=len(oh),
          G=int(sum(stats(e['v'][None], e['pr'], e['sing'])[0][0] for e in oh)),
          G_s=int(sum(stats(e['v'][None], e['pr'], e['sing'])[1][0] for e in oh)),
          G_masked=int(sum(stats(e['v'][None], e['prm'], e['sing'])[0][0] for e in oh)),
          G_s_masked=int(sum(stats(e['v'][None], e['prm'], e['sing'])[1][0] for e in oh)),
          KH0359_masked=int([stats(e['v'][None], e['prm'], e['sing'])[0][0] for e in okr_elig if e['name'] == 'KH0359'][0]),
          KH0405_masked=int([stats(e['v'][None], e['prm'], e['sing'])[0][0] for e in okr_elig if e['name'] == 'KH0405'][0]))
F0['pass'] = (F0['n_r5'], F0['n_eligible'], F0['n_holdout'], F0['G'], F0['G_s'], F0['G_masked'], F0['G_s_masked'],
              F0['KH0359_masked'], F0['KH0405_masked']) == (3069, 369, 367, 23, 10, 18, 10, 4, 4)
res['F0_engine_on_okr'] = F0; print('F0', F0, flush=True)
if not F0['pass']: stop('F0 engine fixture on OKR failed')

# ---------------- KFG (K071 loader verbatim) + KFG R5 ----------------
k = sqlite3.connect(KFG_DB); sha = dict(k.execute('select name, sha256 from khipu'))
PEN = re.compile(r'^p(\d+)$'); CLU = re.compile(r'^(\d+)([A-Z]+)\(([-\d.]+),[^)]*\),(-?\d+)$')
pend = defaultdict(list)
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
for kh, nm, v, kn in k.execute('select khipu, cord_name, value, knots from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0
    pend[kh].append((int(m.group(1)), x, kfg_r5(kn)))
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
    if n and [p for p, _, _ in L] == list(range(1, n + 1)) and [p for a, b in spans for p in range(a, b + 1)] == list(range(1, n + 1)):
        groups[kh] = [(a - 1, b) for a, b in spans]
    elif n: g1_bad.append(kh)
gates = dict(G0_hash_mismatch=len(g0_bad), G1_partition_rate=len(groups) / max(1, len(groups) + len(g1_bad)), G1_bad=g1_bad)
# GR: KFG R5 rule vs OKR R5 on khipus whose pendant value vectors are identical on both sources
okr_by_name = {}
for kid, cords in okr_kh.items():
    if okrname[kid]: okr_by_name[okrname[kid]] = cords
agree = tot = nk = 0; r5o = r5k = 0
for nm, L in pend.items():
    o = okr_by_name.get(nm)
    if not o or len(o) != len(L) or [x[0] for x in o] != [x for _, x, _ in L]: continue
    nk += 1
    for (vo, _, cid), (_, _, rk) in zip(o, L):
        ro = cid in R5_okr; agree += ro == rk; tot += 1; r5o += ro; r5k += rk
gates['GR_r5'] = dict(khipus_identical=nk, pendants=tot, agree=agree, rate=agree / max(1, tot), r5_okr=r5o, r5_kfg=r5k)
gates['pass_data'] = gates['G0_hash_mismatch'] == 0 and gates['G1_partition_rate'] >= 0.95
gates['pass_r5'] = gates['GR_r5']['rate'] >= 0.95
res['gates'] = gates; print('gates', json.dumps({a: b for a, b in gates.items() if a != 'G1_bad'}), round(time.time() - T0, 1), flush=True)
if not gates['pass_data']: stop('KFG data gate G0/G1 failed')

SMOKE_RNG = np.random.default_rng(0)
elig = []
for kh in sorted(groups):
    gs = groups[kh]
    if len(gs) < 4: continue
    L = pend[kh]; v = np.array([x for _, x, _ in L], np.int64); pr = prep(gs, len(v))
    if SMOKE: v = SMOKE_RNG.permutation(v)  # smoke = syntax check on shuffled KFG values only; no real count is computed
    if len(pr) == 0 or (v >= 10).sum() == 0: continue
    bad = np.array([r for _, _, r in L], bool)
    elig.append(dict(kid=kh, okr=kh in okr_set, v=v, pr=pr, prm=legal(pr, bad), bad=bad, sing=singles(gs, len(v))))
byname = {e['kid']: e for e in elig}
ho = [e for e in elig if e['kid'] not in DISC]
res['data'] = dict(n_eligible=len(elig), n_holdout=len(ho), n_holdout_in_okr=sum(e['okr'] for e in ho),
                   n_holdout_kfg_only=sum(not e['okr'] for e in ho), discovery_present=all(d in byname for d in DISC),
                   r5_pendants_holdout=int(sum(e['bad'].sum() for e in ho)), holdout_no_legal_pair=int(sum(len(e['prm']) == 0 for e in ho)))
print('data', res['data'], flush=True)
if not res['data']['discovery_present']: stop('discovery pair missing on KFG')
NOBAD = {e['kid']: np.zeros(len(e['v']), bool) for e in elig}

# ---------------- unmasked arms: K040 H1/H2 and K042 H1/H2 ----------------
rng = np.random.default_rng(SEEDS['nulls'])
oG = oS = oN = 0; tG = np.zeros(R_C, np.int64); tS = np.zeros(R_C, np.int64); tN = np.zeros(R_C, np.int64); rows = []
for j, e in enumerate(ho):
    g, gs, gn = stats(e['v'][None], e['pr'], e['sing']); nG, nS, nN = stats(permmask(rng, e['v'], NOBAD[e['kid']], R_C), e['pr'], e['sing'])
    e['nl'] = nG; oG += int(g[0]); oS += int(gs[0]); oN += int(gn[0]); tG += nG; tS += nS; tN += nN
    rows.append(dict(khipu=e['kid'], in_okr=e['okr'], G=int(g[0]), G_s=int(gs[0]), G_ns=int(gn[0]), null_mean=float(nG.mean()), p=pv(int(g[0]), nG)))
    if (j + 1) % 100 == 0: print(f'nulls {j + 1}/{len(ho)} G={oG} {time.time() - T0:.1f}s', flush=True)
sig = bh([r['p'] for r in rows])
for r, s in zip(rows, sig): r['bh'] = bool(s)
obs = dict(G=oG, G_s=oS, G_ns=oN, G_null_mean=float(tG.mean()), G_null_sd=float(tG.std()), p_G=pv(oG, tG),
           G_s_null_mean=float(tS.mean()), p_G_s=pv(oS, tS), G_ns_null_mean=float(tN.mean()), p_G_ns=pv(oN, tN),
           bh_names=sorted(r['khipu'] for r in rows if r['bh']), n_bh=int(sig.sum()))
# same-data split of the KFG holdout into OKR-shared and KFG-only khipus (descriptive, no verdict)
for lab, sel in (('okr_shared', True), ('kfg_only', False)):
    ix = [j for j, e in enumerate(ho) if e['okr'] == sel]
    obs[lab] = dict(n=len(ix), G=sum(rows[j]['G'] for j in ix), G_s=sum(rows[j]['G_s'] for j in ix), G_ns=sum(rows[j]['G_ns'] for j in ix),
                    bh=sorted(rows[j]['khipu'] for j in ix if rows[j]['bh']))
res['unmasked_observed'] = obs; res['rows'] = rows; dump(); print('observed', {a: b for a, b in obs.items()}, round(time.time() - T0, 1), flush=True)

rc = np.random.default_rng(SEEDS['calib']); fG = fS = fN = fB = 0; ncal = 0
for _ in range(NC):
    if time.time() - T0 > WALL: break
    sg = ss = sn = 0; ps = []
    for e in ho:
        g, gs, gn = stats(rc.permutation(e['v'])[None], e['pr'], e['sing']); sg += int(g[0]); ss += int(gs[0]); sn += int(gn[0]); ps.append(pv(int(g[0]), e['nl']))
    fG += pv(sg, tG) <= 0.05; fS += pv(ss, tS) <= 0.025; fN += pv(sn, tN) <= 0.025; fB += bh(ps).sum() > 0; ncal += 1
cal = dict(n=ncal, fpr_G=fG / max(ncal, 1), fpr_G_s=fS / max(ncal, 1), fpr_G_ns=fN / max(ncal, 1), bh_gate=fB / max(ncal, 1))
res['unmasked_calibration'] = cal; dump(); print('calib', cal, round(time.time() - T0, 1), flush=True)

rp = np.random.default_rng(SEEDS['power']); plantable = [e for e in ho if len(e['pr'])]; cand4 = [e for e in ho if len(e['pr']) >= 4]
def pow_h1():  # K040: one plant in each of m distinct khipus, fresh permutation elsewhere
    hits = n = 0
    for _ in range(NP):
        if time.time() - T0 > WALL: break
        ch = {plantable[i]['kid'] for i in rp.choice(len(plantable), M, replace=False)}; t = 0
        for e in ho:
            x = rp.permutation(e['v'])
            if e['kid'] in ch: x, _ = plant_k(x, e['pr'], 1, rp)
            t += int(stats(x[None], e['pr'], e['sing'])[0][0])
        n += 1; hits += pv(t, tG) <= 0.05
    return dict(n=n, hits=hits, rate=hits / n if n else None)
def pow_h2(kp):  # K040 H2: one khipu with kp disjoint plants must be BH-significant
    hits = n = att = sk = 0
    while n < NP and att < 5 * NP and time.time() - T0 <= WALL:
        att += 1; e0 = (cand4 if kp >= 4 else plantable)[int(rp.integers(len(cand4 if kp >= 4 else plantable)))]
        x0, got = plant_k(rp.permutation(e0['v']), e0['pr'], kp, rp)
        if got < kp: sk += 1; continue
        ps = []; idx = None
        for j, e in enumerate(ho):
            if e is e0: g = int(stats(x0[None], e['pr'], e['sing'])[0][0]); idx = j
            else: g = int(stats(rp.permutation(e['v'])[None], e['pr'], e['sing'])[0][0])
            ps.append(pv(g, e['nl']))
        n += 1; hits += bool(bh(ps)[idx])
    return dict(n=n, hits=hits, skipped=sk, rate=hits / n if n else None)
def pow_corpus(rgen, pred, which, alpha, nulls, masked):  # K042 / K056: m disjoint plants of the required form anywhere
    act = [e for e in ho if len(e['prm' if masked else 'pr'])]
    cands = [(e, kk) for e in act for kk in range(len(e['prm' if masked else 'pr'])) if pred(e, e['prm' if masked else 'pr'][kk])]
    hits = n = att = 0
    while n < NP and att < 5 * NP and time.time() - T0 <= WALL:
        att += 1
        xs = {e['kid']: permmask(rgen, e['v'], e['bad'] if masked else NOBAD[e['kid']], 1)[0] for e in act}; used = defaultdict(set); planted = 0
        for ix in rgen.permutation(len(cands)):
            e, kk = cands[ix]; i, s, ee = [int(t) for t in e['prm' if masked else 'pr'][kk]]; span = set(range(s, ee)) | {i}
            if used[e['kid']] & span: continue
            xs[e['kid']] = plant_pair(xs[e['kid']], i, s, ee, rgen); used[e['kid']] |= span; planted += 1
            if planted >= M: break
        if planted < M: continue
        st = 0
        for e in act: st += int(stats(xs[e['kid']][None], e['prm' if masked else 'pr'], e['sing'])[which][0])
        n += 1; hits += pv(st, nulls) <= alpha
    return dict(n=n, hits=hits, attempts=att, rate=hits / n if n else None)
pw = dict(K040_H1_m9=pow_h1()); print('pow H1', pw, round(time.time() - T0, 1), flush=True)
pw['K040_H2_4plant'] = pow_h2(4); pw['K040_H2_1plant_disclosed'] = pow_h2(1); print('pow H2', pw, round(time.time() - T0, 1), flush=True)
pw['K042_H1_m9'] = pow_corpus(rp, lambda e, t: bool(e['sing'][t[0]]), 1, 0.025, tS, False)
pw['K042_H2_m9'] = pow_corpus(rp, lambda e, t: not bool(e['sing'][t[0]]), 2, 0.025, tN, False)
res['unmasked_power'] = pw; dump(); print('pow K042', pw, round(time.time() - T0, 1), flush=True)

def verdict(p, a, fpr, gate, power, ncal_ok=True):
    if fpr is None or not ncal_ok: return 'not testable'
    if fpr > gate: return 'excluded'
    if power is None or power.get('n', 0) < MIN_N: return 'not testable'
    if power['rate'] < 0.5: return 'not testable'
    return 'supported' if p <= a else 'not supported'
cal_ok = ncal == NC
V = {}
V['K040_H1'] = dict(obs=oG, null_mean=obs['G_null_mean'], p=obs['p_G'], fpr=cal['fpr_G'], power=pw['K040_H1_m9']['rate'],
                    borderline=borderline(obs['p_G'], 0.05, R_C), kfg=verdict(obs['p_G'], 0.05, cal['fpr_G'], 0.08, pw['K040_H1_m9'], cal_ok))
h2 = 'not testable' if not cal_ok else 'excluded' if cal['bh_gate'] > 0.08 else 'supported' if obs['n_bh'] > 0 else \
     ('not supported' if pw['K040_H2_4plant']['n'] >= MIN_N and pw['K040_H2_4plant']['rate'] >= 0.5 else 'not testable')
V['K040_H2'] = dict(n_bh=obs['n_bh'], names=obs['bh_names'], bh_gate=cal['bh_gate'], power_4plant=pw['K040_H2_4plant']['rate'], kfg=h2)
V['K042_H1'] = dict(obs=oS, null_mean=obs['G_s_null_mean'], p=obs['p_G_s'], fpr=cal['fpr_G_s'], power=pw['K042_H1_m9']['rate'],
                    borderline=borderline(obs['p_G_s'], 0.025, R_C), kfg=verdict(obs['p_G_s'], 0.025, cal['fpr_G_s'], 0.08, pw['K042_H1_m9'], cal_ok))
V['K042_H2'] = dict(obs=oN, null_mean=obs['G_ns_null_mean'], p=obs['p_G_ns'], fpr=cal['fpr_G_ns'], power=pw['K042_H2_m9']['rate'],
                    borderline=borderline(obs['p_G_ns'], 0.025, R_C), kfg=verdict(obs['p_G_ns'], 0.025, cal['fpr_G_ns'], 0.08, pw['K042_H2_m9'], cal_ok))
res['verdicts'] = V; dump()

# ---------------- masked arms: K056 on KFG (only if GR passes) ----------------
MV = {}
if not gates['pass_r5']:
    for t in ('K056_KH0359', 'K056_KH0405', 'K056_G', 'K056_G_s'): MV[t] = dict(kfg='not testable', reason='GR R5 gate failed')
else:
    rm = np.random.default_rng(SEEDS['masked'])
    for nm in DISC:
        e = byname[nm]; prm = e['prm']
        if len(prm) == 0: MV['K056_' + nm] = dict(kfg='not testable', reason='no legal pair'); continue
        o = int(stats(e['v'][None], prm, e['sing'])[0][0]); nl = stats(permmask(rm, e['v'], e['bad'], R_T), prm, e['sing'])[0]; p = pv(o, nl)
        fp = float(np.mean([pv(int(stats(permmask(rm, e['v'], e['bad'], 1), prm, e['sing'])[0][0]), nl) <= 0.025 for _ in range(NC)]))
        hits = 0
        for _ in range(NP):
            x = permmask(rm, e['v'], e['bad'], 1)[0]; i, s, ee = [int(t) for t in prm[rm.integers(len(prm))]]
            hits += pv(int(stats(plant_pair(x, i, s, ee, rm)[None], prm, e['sing'])[0][0]), nl) <= 0.025
        pwr = hits / NP
        MV['K056_' + nm] = dict(n_r5=int(e['bad'].sum()), pairs=len(e['pr']), pairs_masked=len(prm), obs=o, null_mean=float(nl.mean()), p=p, fpr=fp, power=pwr,
                               kfg='excluded' if fp > 0.05 else 'survives' if p <= 0.025 else 'no longer established' if pwr >= 0.5 else 'not testable')
    act = [e for e in ho if len(e['prm'])]; mG = mS = 0; tmG = np.zeros(R_C, np.int64); tmS = np.zeros(R_C, np.int64)
    for e in act:
        g, gs, _ = stats(e['v'][None], e['prm'], e['sing']); mG += int(g[0]); mS += int(gs[0])
        nG, nS, _ = stats(permmask(rm, e['v'], e['bad'], R_C), e['prm'], e['sing']); tmG += nG; tmS += nS
    fG = fS = nc2 = 0
    for _ in range(NC):
        if time.time() - T0 > WALL: break
        sg = ss = 0
        for e in act:
            g, gs, _ = stats(permmask(rm, e['v'], e['bad'], 1), e['prm'], e['sing']); sg += int(g[0]); ss += int(gs[0])
        fG += pv(sg, tmG) <= 0.05; fS += pv(ss, tmS) <= 0.025; nc2 += 1
    pG = pow_corpus(rm, lambda e, t: True, 0, 0.05, tmG, True); pS = pow_corpus(rm, lambda e, t: bool(e['sing'][t[0]]), 1, 0.025, tmS, True)
    for nm, o, nl, a, f, pr_ in (('K056_G', mG, tmG, 0.05, fG, pG), ('K056_G_s', mS, tmS, 0.025, fS, pS)):
        p = pv(o, nl); fpr = f / nc2 if nc2 else None
        kv = 'not testable' if nc2 < NC else 'excluded' if fpr > 0.08 else 'survives' if p <= a else \
             ('no longer established' if pr_['n'] >= MIN_N and pr_['rate'] >= 0.5 else 'not testable')
        MV[nm] = dict(obs=o, null_mean=float(nl.mean()), null_sd=float(nl.std()), p=p, fpr=fpr, power_m9=pr_, n_active=len(act),
                      borderline=borderline(p, a, R_C), kfg=kv)
res['verdicts'].update(MV)
# ---------------- mapping to OKR published verdicts ----------------
rep = {}
for t, d in res['verdicts'].items():
    kv = d['kfg']; pub = PUB[t]['verdict']
    if kv in ('not testable', 'excluded'): rep[t] = kv.upper()
    else: rep[t] = 'REPLICATED' if kv == pub else 'CHANGED'
res['replication'] = rep; res['cumulative_alpha_note'] = 'alphas kept per original test (K040 0.05, K042 Bonferroni 0.025, K056 kept)'
dump(); print(json.dumps(res['verdicts'], indent=1, default=str)); print(json.dumps(rep), res['secs'], flush=True)
