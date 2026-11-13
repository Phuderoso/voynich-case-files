#!/usr/bin/env python3
"""K076 - KFG re-audit step 8 (README line 9): line 6, K046 cross-khipu colour agreement on the three K019 pairs,
re-run on Khipu Field Guide data. Pre-registered in case-file/K076-kfg-colour-agreement.md.
K046 engine imported verbatim (colour_match, lcs_traceback, match_matrix, null_bank, pval, plant_power, fixture) and
its per-pair verdict block copied; only the data layer is ported: KFG pendants (^p\\d+$, pendant order), KFG value with
R5 multi-number pendants masked to 0 (K072/K073 port), groups from each Excel CordGroups sheet (K071 parser), K019 leader
weights recomputed over KFG eligible khipus, colour = K074 primary coding (first '/'-segment, trailing '(a-b)' removed)
split into components and operators on ':', '-', '%', '^' (stored order, no re-sort).
Usage (from expeditions/khipu/): python3 tools/k076_kfg_colour_agreement.py [--smoke]
Seeds 6430-6434 (6429 stays reserved for Kryptos); next free 6435. Pimpolha Voynich, do Phuderoso - AI born 2026-11-04."""
import sys, os, re, json, math, time, glob, zipfile, hashlib, sqlite3
import numpy as np, xml.etree.ElementTree as ET
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import k046_colour_agreement as K
T0 = time.time(); SMOKE = '--smoke' in sys.argv
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'; OKR_DB = os.path.join(HERE, '..', 'data', 'khipu.db')
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'; OKR_SHA = K.SHA
SEEDS = dict(null=6430, calib=6431, power=6432, n2=6433, sens=6434); NEXT_FREE = 6435
PUB = {"KH0097/KH0586": dict(n=89, A=6, verdict="SUPPORTED"), "KH0192/KH0470": dict(n=37, A=7, verdict="SUPPORTED"),
       "KH0192/KH0469": dict(n=36, A=0, verdict="NOT SUPPORTED")}
OUT = os.path.join(HERE, '..', 'analysis', 'k076_smoke.json' if SMOKE else 'k076_results.json')
res = dict(cycle='K076', smoke=SMOKE, seeds=SEEDS, next_free_seed=NEXT_FREE, alpha=K.ALPHA, fpr_gate=K.FPR_GATE,
           power_bar=K.POWER_BAR, f_plant=K.F_PLANT, published_okr=PUB, pairs={})
def dump(): res['sec'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1, default=list)
def stop(r): res['decision'] = dict(excluded=True, reason=r); dump(); print('EXCLUDED:', r); sys.exit(0)
# ---------------- G0 hashes, fixture ----------------
for p, want in ((OKR_DB, OKR_SHA), (KFG_DB, KFG_SHA)):
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if h != want: stop(f'G0 hash mismatch {p} {h}')
res['G0'] = 'pass'
ok, fx = K.run_fixture(); res['fixture_passed'] = ok
if not ok: stop('K046 match-function fixture failed')
# ---------------- F0: K046 engine on OKR reproduces K046's published A/n exactly ----------------
co = sqlite3.connect(f"file:{os.path.realpath(OKR_DB)}?mode=ro", uri=True); SO = K.load(co); f0 = {}
for a, b in K.PAIRS:
    key = f'{a}/{b}'; pr, Vs, units, leaders = K.build_units(SO, a, b); us, _ = K.colour_units(SO, units)
    f0[key] = dict(groups=len(pr), V=sum(Vs), n=len(us), A=int(np.trace(K.match_matrix(us))))
res['F0'] = dict(got=f0, pass_=all(f0[k]['n'] == PUB[k]['n'] and f0[k]['A'] == PUB[k]['A'] and (f0[k]['groups'], f0[k]['V']) == K.K019[k] for k in PUB))
print('F0', res['F0'], round(time.time() - T0, 1), flush=True)
if not res['F0']['pass_']: stop('F0 K046 fixture on OKR failed')
# ---------------- KFG data layer ----------------
kc = sqlite3.connect(KFG_DB); sha = dict(kc.execute('select name, sha256 from khipu'))
PEN = re.compile(r'^p(\d+)$'); CLU = re.compile(r'^(\d+)([A-Z]+)\(([-\d.]+),[^)]*\),(-?\d+)$')
RNG = re.compile(r'\([-\d.]+-[-\d.]+\)$'); OPS = re.compile(r'([:\-%^])')
def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
def kfg_r5(knots):  # K072/K073 port, verbatim
    cls = []
    for j, t in enumerate(str(knots or '').split(';')):
        m = CLU.match(t.strip())
        if not m: continue
        typ, pos, v = m.group(2), float(m.group(3)), int(m.group(4))
        if v == 0 or typ[0] not in 'SLE': continue
        cls.append((pos, j, place(v) if typ[0] == 'S' else 0))
    s = [p for _, _, p in sorted(cls)]
    return len(s) >= 2 and not all(a > b for a, b in zip(s, s[1:]))
def c_prim(s):  # K074 primary coding, verbatim
    if s is None: return None
    s = RNG.sub('', str(s).split('/')[0].strip()).strip()
    return s or None
def parse(s):
    s = c_prim(s)
    if s is None or s.lower() in ('none', 'nan'): return None, 'no_colour'
    parts = OPS.split(s); comps = tuple(x.strip() for x in parts[0::2]); ops = tuple(parts[1::2])
    if not comps or any(not x for x in comps): return None, 'unparsed'
    return (comps, ops), 'ok'
pend = defaultdict(list); NR5 = [0]
for kh, nm, v, kn, cl in kc.execute('select khipu, cord_name, value, knots, color from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0
    r5 = kfg_r5(kn); NR5[0] += r5
    pend[kh].append((int(m.group(1)), 0 if r5 else x, cl))
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
GRP = re.compile(r'^[\d.]+cm group of (\d+) pendants \((\d+)-(\d+)\)'); ONE = re.compile(r'^[\d.]+cm 1 \((\d+)\)')
def sheet_strings(f, name):  # K071 parser, verbatim
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
groups, g1_bad, g0_bad = {}, [], []
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
    L = sorted(pend.get(kh, [])); n = len(L)
    if n and [p for p, _, _ in L] == list(range(1, n + 1)) and [p for a, b in spans for p in range(a, b + 1)] == list(range(1, n + 1)):
        groups[kh] = [(a - 1, b) for a, b in spans]
    elif n: g1_bad.append(kh)
if g0_bad: stop(f'G0 xlsx hash mismatch {g0_bad[:5]}')
VAL = {kh: [x for _, x, _ in sorted(pend[kh])] for kh in groups}
COL = {(kh, i): sorted(pend[kh])[i][2] for kh in groups for i in range(len(pend[kh]))}
ids = [kh for kh, v in VAL.items() if sum(x > 0 for x in v) >= 10]
def raw_groups(kh): return [(VAL[kh][a:b], [(kh, i) for i in range(a, b)]) for a, b in groups[kh]]
def lgroups(kh): return [g for g in raw_groups(kh) if len(g[0]) >= 5 and g[0][0] > 0]
lf = Counter(g[0][0] for kh in ids for g in lgroups(kh)); lt = sum(lf.values()); WL = {v: -math.log2(n / lt) for v, n in lf.items()}
def walign(a, b):  # K019/K046 weighted leader LCS, verbatim
    n, m = len(a), len(b); D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = max(D[i-1][j], D[i][j-1], D[i-1][j-1] + WL[a[i-1]] if a[i-1] == b[j-1] else -1)
    i, j, pr = n, m, []
    while i and j:
        if a[i-1] == b[j-1] and abs(D[i][j] - (D[i-1][j-1] + WL[a[i-1]])) < 1e-9: pr.append((i-1, j-1)); i -= 1; j -= 1
        elif D[i-1][j] >= D[i][j-1]: i -= 1
        else: j -= 1
    return pr[::-1]
SK = dict(byokr={kh: kh for kh in ids}, lgroups=lgroups, walign=walign, colour=lambda u: parse(COL[u]))
need = sorted({x for p in K.PAIRS for x in p})
res['kfg_data'] = dict(n_with_pendants=len(pend), n_grouped=len(groups), G1_bad=len(g1_bad), n_eligible=len(ids), n_R5_masked=NR5[0],
                       pair_khipus_eligible={kh: kh in ids for kh in need})
missing = [kh for kh in need if kh not in ids]
if SMOKE:  # colours shuffled within each khipu (only smoke ever sees this)
    sr = np.random.default_rng(0)
    for kh in groups:
        ks = [(kh, i) for i in range(len(pend[kh]))]; perm = sr.permutation(len(ks)); vals = [COL[k] for k in ks]
        for k_, j in zip(ks, perm): COL[k_] = vals[j]
# ---------------- per pair: K046 main() per-pair block, copied ----------------
R = 200 if SMOKE else 10000; NCAL = 50 if SMOKE else 1000; NPOW = 10 if SMOKE else 200; RP = 200 if SMOKE else 2000; NCURVE = 10 if SMOKE else 100
res.update(R=R, n_calibration=NCAL, n_power=NPOW, R_power=RP)
rng = {k: np.random.default_rng(v) for k, v in SEEDS.items()}
for a, b in K.PAIRS:
    key = f'{a}/{b}'; P = res['pairs'].setdefault(key, {}); t1 = time.time()
    if a in missing or b in missing: P['verdict'] = 'NOT TESTABLE (data)'; P['reason'] = 'khipu not eligible / not grouped in KFG'; continue
    pr, Vs, units, leaders = K.build_units(SK, a, b)
    us, excl = K.colour_units(SK, units); n = len(us)
    P.update(matched_groups=len(pr), V=Vs, V_tot=sum(Vs), okr_groups_V=list(K.K019[key]), aligned_nonleader_units=len(units),
             coloured_units=n, excluded_units=dict(excl))
    if n < 10: P['verdict'] = 'NOT TESTABLE'; P['reason'] = f'only {n} coloured units'; continue
    cp = [{**u, 'colB': u['colA']} for u in us]; Mc = K.match_matrix(cp); oc = int(np.trace(Mc))
    want = sum('PK' not in u['colA'][0] for u in us); pc = K.pval(oc, K.null_bank(Mc, 2000, np.random.default_rng(SEEDS['power'] + 100)))
    P['positive_control_copy_all'] = dict(A=oc, expected=want, p=pc, passed=bool(oc == want and pc < K.ALPHA))
    M = K.match_matrix(us); bank = K.null_bank(M, R, rng['null']); cal = []
    for _ in range(NCAL):
        perm = rng['calib'].permutation(n); cal.append(K.pval(int(M[np.arange(n), perm].sum()), bank))
    fpr_perm = float(np.mean(np.array(cal) < K.ALPHA))
    lo = math.ceil(0.1 * n); shifts = [k for k in range(1, n) if min(k, n - k) >= lo]
    sp = [K.pval(int(M[np.arange(n), (np.arange(n) + k) % n].sum()), bank) for k in shifts]
    fpr_shift = float(np.mean(np.array(sp) < K.ALPHA)) if sp else None
    pw, pmed, kpl = K.plant_power(us, K.F_PLANT, NPOW, RP, rng['power'])
    curve = {str(f): K.plant_power(us, f, NCURVE, RP, rng['power'])[0] for f in K.F_CURVE}
    obs = int(np.trace(M)); p = K.pval(obs, bank)
    bank_n2 = K.null_bank(M, R, rng['n2'], blocks=[[i for i, u in enumerate(us) if u['group_pair'] == g] for g in range(len(pr))])
    P.update(observed_A=obs, rate=obs / n, null_mean=float(bank.mean()), null_sd=float(bank.std()), null_q95=float(np.quantile(bank, 0.95)),
             p=p, calibration=dict(fpr_perm=fpr_perm, n=NCAL, shift_offsets=len(shifts), fpr_shift=fpr_shift),
             power=dict(f=K.F_PLANT, k_planted=kpl, power=pw, median_p=pmed, curve=curve),
             N2_within_group=dict(null_mean=float(bank_n2.mean()), p=K.pval(obs, bank_n2), note='descriptive'))
    if not P['positive_control_copy_all']['passed'] or fpr_perm > K.FPR_GATE or (fpr_shift is not None and fpr_shift > K.FPR_GATE): v = 'TOOL EXCLUDED'
    elif pw < K.POWER_BAR: v = 'NOT TESTABLE'
    elif p < K.ALPHA: v = 'SUPPORTED'
    else: v = 'NOT SUPPORTED'
    P['verdict'] = v
    sens = {}
    Mby = K.match_matrix(us, True); ob = int(np.trace(Mby)); sens['BY_eq_YB'] = dict(A=ob, p=K.pval(ob, K.null_bank(Mby, R, rng['sens'])))
    srt = [{**u, 'colA': (tuple(sorted(u['colA'][0])), tuple(sorted(u['colA'][1]))), 'colB': (tuple(sorted(u['colB'][0])), tuple(sorted(u['colB'][1])))} for u in us]
    Ms = K.match_matrix(srt); os_ = int(np.trace(Ms)); sens['order_free'] = dict(A=os_, p=K.pval(os_, K.null_bank(Ms, R, rng['sens'])))
    ul, _ = K.colour_units(SK, units + leaders); Ml = K.match_matrix(ul); ol = int(np.trace(Ml))
    sens['with_leaders'] = dict(n=len(ul), A=ol, p=K.pval(ol, K.null_bank(Ml, R, rng['sens'])))
    P['sensitivities'] = sens
    P['colour_counts_A'] = dict(Counter(':'.join(u['colA'][0]) + '|' + ''.join(u['colA'][1]) for u in us).most_common())
    P['colour_counts_B'] = dict(Counter(':'.join(u['colB'][0]) + '|' + ''.join(u['colB'][1]) for u in us).most_common())
    P['matching_units'] = [dict(gA=u['gA'], gB=u['gB'], posA=u['posA'], posB=u['posB'], value=u['value'], colour=COL[u['cidA']])
                           for u in us if K.colour_match(u['colA'], u['colB'])]
    print(f"{key} groups={len(pr)} V={sum(Vs)} n={n} A={obs} null={bank.mean():.2f} p={p:.5f} fpr={fpr_perm:.3f}/{fpr_shift} pw={pw:.2f} -> {v} ({time.time()-t1:.1f}s)", flush=True)
    dump()
def rep(kv, ov):
    if kv.startswith('NOT TESTABLE') or kv == 'TOOL EXCLUDED': return 'NOT TESTABLE'
    return 'REPLICATED' if kv == ov else 'CHANGED (correction)'
res['decision'] = {k: rep(res['pairs'][k]['verdict'], PUB[k]['verdict']) for k in PUB}
print('decision', res['decision']); dump()
