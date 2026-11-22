#!/usr/bin/env python3
"""K099 - KFG re-audit step 28 (README line 9): K054, the R5 multi-number-cord sensitivity of the frozen K036 F1 / D5w
list, re-run on Khipu Field Guide data. Pre-registered in case-file/K099-kfg-k054-mask.md BEFORE any masked KFG D5w
statistic, gate or p-value was computed.
Engine: the K054 functions are IMPORTED VERBATIM from tools/k054_multinumber_k036_f1.py (AST extraction of the function
source, exec'd unchanged; sha256 of the extracted source is recorded). R5 rule: kfg_r5 (and its CLU / place helpers)
imported verbatim the same way from tools/k080_kfg_k008_r5_mask.py. KFG pendants and CordGroups groups: K077 loader
(tools/k077_kfg_k036_f1.py, itself K071/K072), extended only by reading the knots column for kfg_r5.
Usage (from expeditions/khipu): python3 tools/k099_kfg_k054_mask.py {fixture|a0|all}
  fixture = hashes, KFG pop == K077's 440, empty-mask scores == K077 stat_D5w (440/440), R5 counts, testable set,
            list presence (no masked D5w statistic on KFG values)
  a0      = exact OKR anchor: tools/k054 re-run unchanged on OKR khipu.db in a scratch dir, compared to analysis/k054_results.json
  all     = fixture, A0 check, gates (seed 6519), masked KFG scan (seed 6520), labels. Checkpoint analysis/k099_checkpoint.json.
Seeds 6519 (gates), 6520 (scan); next free 6521."""
import sqlite3, sys, json, time, os, re, glob, hashlib, shutil, subprocess, zipfile, ast
import numpy as np, xml.etree.ElementTree as ET
from collections import defaultdict
from math import sqrt
T0 = time.time(); MODE = sys.argv[1] if len(sys.argv) > 1 else 'fixture'
OKR_DB = '/workspace/khipu/khipu.db'; OKR_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'
CK = 'analysis/k099_checkpoint.json'; OUT = 'analysis/k099_results.json'; A0_OUT = 'analysis/k099_a0.json'
SEED_G, SEED_SCAN, NEXT_FREE = 6519, 6520, 6521
K = 10000; Q = 0.05; CHUNK = 1000; MINP = 10; M_PLANT = 6
K036_F1 = ["KH0322/UR086", "KH0395/UR155", "KH0420/UR182", "KH0428/UR190", "KH0478/UR242", "KH0491/UR255",
           "KH0492/UR256", "KH0502/UR266", "KH0504/UR267B", "KH0506/UR269", "KH0507/UR270", "KH0511/UR273B",
           "KH0513/UR274B", "KH0514/UR275"]

# ---------------- A0: exact OKR rebuild of K054 ----------------
if MODE == 'a0':
    d = '/tmp/k099_a0'; shutil.rmtree(d, ignore_errors=True); os.makedirs(d + '/analysis'); os.makedirs(d + '/tools')
    shutil.copy('analysis/k036_results.json', d + '/analysis/'); shutil.copy('tools/k054_multinumber_k036_f1.py', d + '/tools/')
    subprocess.run(['timeout', '600', 'python3', 'tools/k054_multinumber_k036_f1.py', OKR_DB, 'all'], cwd=d, check=True,
                   stdout=open('analysis/k099_a0_run.log', 'w'), stderr=subprocess.STDOUT)
    A = json.load(open(d + '/analysis/k054_results.json')); P = json.load(open('analysis/k054_results.json'))
    strip = lambda g: {k: v for k, v in g.items() if k != 'seconds'}
    res = dict(G0_equal=A['G0'] == P['G0'], gates_equal=strip(A['gates']) == strip(P['gates']), rows_equal=A['rows'] == P['rows'],
               summary_equal=A['summary'] == P['summary'], db_equal=A['db'] == P['db'])
    res['pass'] = all(res.values()); res['seconds'] = round(time.time() - T0, 1)
    json.dump(res, open(A0_OUT, 'w'), indent=1); print(json.dumps(res)); sys.exit(0 if res['pass'] else 1)

# ---------------- verbatim imports (AST) ----------------
def extract(path, names):
    src = open(path).read(); tree = ast.parse(src); out = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names: out[node.name] = ast.get_source_segment(src, node)
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
            out[node.targets[0].id] = ast.get_source_segment(src, node)
    missing = [n for n in names if n not in out]
    if missing: sys.exit(f'verbatim import failed {path}: {missing}')
    return [out[n] for n in names]
K054_NAMES = ['valid_masks', 'scores_w', 'scores_w_masked', 'colrank_p', 'minp_pooled_detail', 'permmask', 'null_scores_masked',
              'masked_p', 'bh', 'group_ranges', '_fill', 'plant_within_m_masked']
K080_NAMES = ['place', 'CLU', 'kfg_r5']
_valid_cache = {}
eng_src = extract('tools/k054_multinumber_k036_f1.py', K054_NAMES); r5_src = extract('tools/k080_kfg_k008_r5_mask.py', K080_NAMES)
for s in eng_src + r5_src: exec(s, globals())
IMPORT_SHA = dict(k054_engine=hashlib.sha256('\n\n'.join(eng_src).encode()).hexdigest(),
                  k080_r5=hashlib.sha256('\n\n'.join(r5_src).encode()).hexdigest())
def n_ge4(gids): return sum(1 for a, b in group_ranges(gids) if b - a >= 4)  # K077 helper (pop rule, K036)
res = dict(cycle='K099', mode=MODE, design=dict(K=K, q=Q, seeds=dict(gates=SEED_G, scan=SEED_SCAN), next_free_seed=NEXT_FREE,
           m_plant=M_PLANT, p_construction='pooled_exchangeable (K033/K036)', mask='K008 structure-preserving R5 (kfg_r5, K080)',
           groups='KFG CordGroups spans (K071/K077)', family='K077 KFG pop (440), testable after mask (>= 10 nonzero unmasked)'),
           imports=IMPORT_SHA)
def dump(): res['secs'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1, default=str)
def stop(r): res['stopped'] = r; dump(); print('STOP:', r, flush=True); sys.exit(1)

# ---------------- G0 hashes + OKR names ----------------
G0 = dict(okr_sha_ok=hashlib.sha256(open(OKR_DB, 'rb').read()).hexdigest() == OKR_SHA,
          kfg_sha_ok=hashlib.sha256(open(KFG_DB, 'rb').read()).hexdigest() == KFG_SHA)
if not all(G0.values()): res['G0'] = G0; stop('hash mismatch')
oc = sqlite3.connect(OKR_DB)
okr_num = {r[0] for r in oc.execute("select OKR_NUM from khipu_main") if r[0]}

# ---------------- KFG data (K077 loader + kfg_r5 on the knots column) ----------------
k = sqlite3.connect(KFG_DB); sha = dict(k.execute('select name, sha256 from khipu'))
PEN = re.compile(r'^p(\d+)$'); pend = defaultdict(list)
for khn, nm, v, kn in k.execute('select khipu, cord_name, value, knots from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0
    pend[khn].append((int(m.group(1)), x, kfg_r5(kn)))
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
    if n and [p for p, _, _ in L] == list(range(1, n + 1)) and [p for a, b in spans for p in range(a, b + 1)] == list(range(1, n + 1)):
        groups[khn] = spans
    elif n: g1_bad.append(khn)
kfg_elig = {}
for khn, spans in groups.items():
    v = np.array([x for _, x, _ in pend[khn]], np.int64)
    if (v > 0).sum() < 10: continue
    g = np.empty(len(v), np.int32)
    for gi, (a, b) in enumerate(spans): g[a - 1:b] = gi
    kfg_elig[khn] = (v, g, np.array([r for _, _, r in pend[khn]], bool))
kfg_pop = sorted(x for x, (v, g, b) in kfg_elig.items() if n_ge4(g) >= 2)
testable = [x for x in kfg_pop if ((kfg_elig[x][0] > 0) & ~kfg_elig[x][2]).sum() >= MINP]
k077 = json.load(open('analysis/k077_results.json')); k077_rows = {r['khipu']: r for r in k077['rows']}
k054 = json.load(open('analysis/k054_results.json'))
rep_empty = sum(np.isclose(float(scores_w_masked(kfg_elig[x][0][None], kfg_elig[x][1], np.zeros(len(kfg_elig[x][0]), bool)).sum()),
                           k077_rows[x]['stat_D5w']) for x in kfg_pop if x in k077_rows)
r5free = [x for x in kfg_pop if not kfg_elig[x][2].any()]
rep_r5free = sum(np.allclose(scores_w_masked(kfg_elig[x][0][None], kfg_elig[x][1], kfg_elig[x][2]),
                             scores_w(kfg_elig[x][0][None], kfg_elig[x][1])) for x in r5free)
f1 = {nm.split('/')[0]: nm for nm in K036_F1}
k054_fate = {x['name'].split('/')[0]: x['fate'] for x in k054['summary']['names']}
k054_nr5 = {x['name'].split('/')[0]: x['n_r5'] for x in k054['summary']['names']}
fx = dict(xlsx_hash_mismatch=len(g0_bad), partition_rate=len(groups) / max(1, len(groups) + len(g1_bad)), n_eligible=len(kfg_elig),
          n_pop=len(kfg_pop), pop_eq_k077=set(kfg_pop) == set(k077_rows), empty_mask_reproduces_k077=f'{rep_empty}/{len(kfg_pop)}',
          n_r5free_pop=len(r5free), r5free_masked_eq_unmasked=f'{rep_r5free}/{len(r5free)}',
          r5_pendants_pop=int(sum(kfg_elig[x][2].sum() for x in kfg_pop)), pop_with_r5=int(sum(kfg_elig[x][2].any() for x in kfg_pop)),
          n_testable=len(testable), not_testable=[x for x in kfg_pop if x not in testable],
          n_testable_okr_shared=sum(x in okr_num for x in testable), n_testable_kfg_only=sum(x not in okr_num for x in testable),
          f1_testable=sorted(x for x in f1 if x in testable), f1_untestable=sorted(x for x in f1 if x not in testable),
          f1_n_r5_okr_vs_kfg={x: (k054_nr5[x], int(kfg_elig[x][2].sum()) if x in kfg_elig else None) for x in sorted(f1)},
          k054_fates=k054_fate)
fx['pass'] = bool(fx['xlsx_hash_mismatch'] == 0 and fx['partition_rate'] >= 0.95 and fx['pop_eq_k077'] and rep_empty == len(kfg_pop)
                  and rep_r5free == len(r5free) and len(k054_fate) == 14 and list(k054_fate.values()).count('survives') == 13)
res['G0'] = G0; res['fixture'] = fx
print('FIXTURE', json.dumps(fx), flush=True)
if not fx['pass']: stop('fixture failed')
if MODE == 'fixture': dump(); sys.exit(0)
a0 = json.load(open(A0_OUT)) if os.path.exists(A0_OUT) else dict(pass_=False)
res['a0'] = a0
if not a0.get('pass'): stop('A0 not passed (run mode a0 first)')
ck = json.load(open(CK)) if os.path.exists(CK) else {}
def save(): json.dump(ck, open(CK, 'w'), indent=1)

# ---------------- G1 FPR / G2 power at m = 6 (K054 gates verbatim, KFG data) ----------------
if 'gates' not in ck:
    rng = np.random.default_rng(SEED_G); cal, pw, skipped = [], [], []; ts = time.time()
    for j, x in enumerate(testable):
        v, gids, b = kfg_elig[x]
        xs = permmask(rng, v, b, 1)[0]
        cal.append(masked_p(rng, xs, gids, b)[0])
        planted, specs = plant_within_m_masked(rng, v, gids, b, M_PLANT)
        if planted is None: skipped.append(x)
        else: pw.append(masked_p(rng, planted, gids, b)[0])
        if (j + 1) % 50 == 0: print('gates', j + 1, '/', len(testable), round(time.time() - ts, 1), 's', flush=True)
    cal, pw = np.asarray(cal), np.asarray(pw)
    G = dict(seed=SEED_G, K=K, m_plant=M_PLANT, calib_n=int(len(cal)), fpr=float(np.mean(cal <= 0.05)), calib_bh_flags=int(bh(cal).sum()),
             plant_n=int(len(pw)), plant_skipped_no_window=skipped, power=float(np.mean(pw <= 0.05)) if len(pw) else None)
    G['G1'] = bool(G['fpr'] <= 0.05); G['G2'] = bool(G['plant_n'] >= 30 and G['power'] is not None and G['power'] >= 0.50)
    G['seconds'] = round(time.time() - ts, 1); ck['gates'] = G; save()
G = ck['gates']; res['gates'] = G
print('gates', json.dumps({a: b for a, b in G.items() if a != 'plant_skipped_no_window'}), flush=True)

# ---------------- masked KFG scan ----------------
if 'scan' not in ck:
    rng = np.random.default_rng(SEED_SCAN); rows = []; ts = time.time()
    for j, x in enumerate(testable):
        v, gids, b = kfg_elig[x]; p, cnt, denom, se, stat_m = masked_p(rng, v, gids, b)
        rows.append(dict(khipu=x, in_okr=x in okr_num, n_pend=len(v), n_r5=int(b.sum()), n_unmasked_nz=int(((v > 0) & ~b).sum()),
                         stat_D5w_unmasked=float(scores_w(v[None], gids).sum()), stat_D5w_masked=stat_m, p=p, cnt=cnt, denom=denom, se=se,
                         p_k077_unmasked=k077_rows[x]['p'], bh_k077_unmasked=k077_rows[x]['bh_sig']))
        if (j + 1) % 50 == 0: print('scan', j + 1, '/', len(testable), round(time.time() - ts, 1), 's', flush=True)
    for r, s in zip(rows, bh([r['p'] for r in rows])): r['bh_sig'] = bool(s)
    ck['scan'] = dict(seed=SEED_SCAN, rows=rows, seconds=round(time.time() - ts, 1)); save()
rows = {r['khipu']: r for r in ck['scan']['rows']}
ps = np.array([r['p'] for r in ck['scan']['rows']]); o = np.sort(ps); thr = Q * np.arange(1, len(ps) + 1) / len(ps)
okk = o <= thr; rank = int(np.max(np.nonzero(okk)[0]) + 1) if okk.any() else 0; bar = float(thr[rank - 1]) if rank else None

# ---------------- labels (pre-registered) ----------------
def label(x):
    exp = {'survives': 'BH', 'no longer established': 'not BH', 'not testable': 'not testable'}[k054_fate[x]]
    r = rows.get(x)
    if r is None or exp == 'not testable': return exp, ('absent' if r is None else ('BH' if r['bh_sig'] else 'not BH')), 'NOT TESTABLE'
    got = 'BH' if r['bh_sig'] else 'not BH'
    if not G['G1']: return exp, got, 'NOT TESTABLE (G1)'
    if got == exp: return exp, got, 'REPLICATED'
    if not G['G2'] and exp == 'BH': return exp, got, 'NOT TESTABLE (underpowered drop)'
    return exp, got, 'CHANGED'
names14 = []
for x in sorted(f1):
    exp, got, lab = label(x); r = rows.get(x, {})
    names14.append(dict(name=f1[x], k054_fate=k054_fate[x], okr_masked=exp, kfg_masked=got, label=lab, n_r5_okr=k054_nr5[x],
                        n_r5_kfg=r.get('n_r5'), stat_masked_okr=[n['stat_masked'] for n in k054['summary']['names'] if n['name'] == f1[x]][0],
                        stat_masked_kfg=r.get('stat_D5w_masked'), p_masked_okr=[n['p_masked'] for n in k054['summary']['names'] if n['name'] == f1[x]][0],
                        p_masked_kfg=r.get('p'), p_over_bar=(r['p'] / bar) if (r and bar) else None,
                        k077_unmasked_bh=r.get('bh_k077_unmasked')))
new = sorted(x for x, r in rows.items() if r['bh_sig'] and x not in f1)
k077_cands = ['KH0143', 'KH0168', 'KH0505', 'KH0597', 'KH0604A', 'KH0674', 'KH0677', 'KH0695']
S = dict(n_tested=len(rows), n_bh=int(sum(r['bh_sig'] for r in rows.values())), bh_rank=rank, bh_bar=bar,
         replicated=sum(n['label'] == 'REPLICATED' for n in names14), changed=[n['name'] for n in names14 if n['label'] == 'CHANGED'],
         not_testable=[n['name'] for n in names14 if n['label'].startswith('NOT TESTABLE')],
         new_okr_shared=[x for x in new if rows[x]['in_okr']], new_kfg_only=[x for x in new if not rows[x]['in_okr']],
         k077_candidates_masked={x: (dict(p=rows[x]['p'], bh=rows[x]['bh_sig'], n_r5=rows[x]['n_r5']) if x in rows else 'not testable') for x in k077_cands},
         k077_bh_lost_by_mask=sorted(x for x, r in rows.items() if r['bh_k077_unmasked'] and not r['bh_sig']),
         gates_pass=bool(G['G1'] and G['G2']))
S['headline'] = ('NOT TESTABLE (G1)' if not G['G1'] else 'REPLICATED' if S['replicated'] == 14 else 'CORRECTION')
res['summary'] = S; res['names14'] = names14; res['rows'] = ck['scan']['rows']; dump()
print(json.dumps({a: b for a, b in S.items()}, indent=1))
for n in names14: print('F1', json.dumps(n))
print('seconds', round(time.time() - T0, 1), flush=True)
