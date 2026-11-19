#!/usr/bin/env python3
"""K085 - KFG re-audit of K020 (two-stage scan: K018 weighted leaders on groups >= 3 cords, then K019 non-leader cord
check, Bonferroni over stage-1 discoveries at alpha 0.01). Pre-registered in case-file/K085-kfg-replication-k020.md.
K020's statistic, nulls, controls and decision rule verbatim; data = Khipu Field Guide pendants (^p\\d+$, KFG value,
R5 multi-number pendants masked to 0 by the K073 port), groups from each Excel CordGroups sheet (K071 parser).
A0: K020's OKR loader rebuilt here must reproduce K020's 2 763 leaders and the five published stage-1 W scores (+-1e-6).
Usage: python3 tools/k085_kfg_k020_two_stage.py data/khipu.db. Seed 6464 (next free 6465)."""
import sqlite3, json, sys, re, glob, zipfile, hashlib, time, math, os, ctypes, subprocess
import numpy as np, xml.etree.ElementTree as ET
from collections import defaultdict, Counter
T0 = time.time(); KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'
OKR_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
OKR_DB = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'data/khipu.db'; OUT = 'analysis/k085_a0.json' if '--a0-only' in sys.argv else 'analysis/k085_results.json'
SEED = 6464; NNULL, NHELD, NPLANT, R2 = 100, 20, 50, 10000
CONTROLS = [('KH0097', 'KH0586'), ('KH0192', 'KH0470'), ('KH0192', 'KH0469')]
TARGET = ('KH0502', 'KH0514'); STAGE1_ONLY = ('KH0491', 'KH0503')
known = {frozenset(p) for p in [('KH0240','KH0496'),('KH0362','KH0049'),('KH0128','KH0137'),('KH0140','KH0483'),('KH0305','KH0301'),('KH0304','KH0303'), TARGET, STAGE1_ONLY]}
res = dict(design=dict(seed=SEED, NNULL=NNULL, NHELD=NHELD, NPLANT=NPLANT, R2=R2, group_min=3, elig_nonzero=10, alpha2=0.01))
def dump(): res['sec'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1, default=str)
def stop(why): res['decision'] = dict(excluded=True, reason=why); dump(); print('STOP', why); sys.exit(0)
def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
SO = '/tmp/k085_wlcs.so'; subprocess.run(['gcc', '-O3', '-shared', '-fPIC', '-o', SO, os.path.join(os.path.dirname(__file__), 'k016_wlcs.c')], check=True)
lib = ctypes.CDLL(SO); dp = ctypes.POINTER(ctypes.c_double); ip = ctypes.POINTER(ctypes.c_int); lp = ctypes.POINTER(ctypes.c_longlong)
def lcs(a, b):
    d = [0] * (len(b) + 1)
    for x in a:
        p = 0
        for j, y in enumerate(b):
            t = d[j + 1]; d[j + 1] = p + 1 if x == y else max(d[j + 1], d[j]); p = t
    return d[-1]
class Pipe:
    """K020 verbatim on a corpus given as kh[name] = pendant values, grp[name] = list of value lists (groups in order)."""
    def __init__(self, kh, grp):
        self.kh, self.grp = kh, grp
        self.ids = sorted(k for k, v in kh.items() if sum(x > 0 for x in v) >= 10); self.N = len(self.ids); self.M = self.N * (self.N - 1) // 2
        self.LD = {k: [g[0] for g in grp[k] if len(g) >= 3 and g[0] > 0] for k in self.ids}
        lf = Counter(x for k in self.ids for x in self.LD[k]); self.lt = sum(lf.values()); self.nd = len(lf)
        self.WL = {v: -math.log2(n / self.lt) for v, n in lf.items()}
        self.base = [list(self.LD[k]) for k in self.ids]; self.AI, self.BI = np.triu_indices(self.N, 1)
    def allW(self, S):
        L = np.array([len(s) for s in S], np.int32); off = np.concatenate([[0], np.cumsum(L)[:-1]]).astype(np.int32)
        v = np.array([x for s in S for x in s], np.int64); w = np.array([self.WL[int(x)] for x in v], np.float64); out = np.zeros(self.M)
        lib.wlcs_all(self.N, off.ctypes.data_as(ip), L.ctypes.data_as(ip), v.ctypes.data_as(lp), w.ctypes.data_as(dp), out.ctypes.data_as(dp)); return out
    def pidx(self, a, b):
        a, b = min(a, b), max(a, b); N = self.N; return a * N - a * (a + 1) // 2 + (b - a - 1)
    def W(self, obs, a, b):
        if a not in self.ids or b not in self.ids: return None
        return float(obs[self.pidx(self.ids.index(a), self.ids.index(b))])
    def nullc(self, rng): return [list(rng.permutation(s)) if len(s) > 1 else list(s) for s in self.base]
    def lgroups(self, k): return [g for g in self.grp[k] if len(g) >= 3 and g[0] > 0]
    def walign(self, a, b):
        WL = self.WL; n, m = len(a), len(b); D = [[0.0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                D[i][j] = max(D[i-1][j], D[i][j-1], D[i-1][j-1] + WL[a[i-1]] if a[i-1] == b[j-1] else -1)
        i, j, pr = n, m, []
        while i and j:
            if a[i-1] == b[j-1] and abs(D[i][j] - (D[i-1][j-1] + WL[a[i-1]])) < 1e-9: pr.append((i-1, j-1)); i -= 1; j -= 1
            elif D[i-1][j] >= D[i][j-1]: i -= 1
            else: j -= 1
        return pr[::-1]
    def stage2(self, ka, kb, rng):
        GA, GB = self.lgroups(ka), self.lgroups(kb); pr = self.walign([g[0] for g in GA], [g[0] for g in GB])
        V = sum(lcs(GA[i][1:], GB[j][1:]) for i, j in pr); cache = {}
        def V_(i2, j):
            if (i2, j) not in cache: cache[(i2, j)] = lcs(GA[i2][1:], GB[j][1:])
            return cache[(i2, j)]
        oth = {j: [x for x in range(len(GA)) if x != i] for i, j in pr}; ge = 0; nl = []
        if pr and all(oth.values()):
            for r in range(R2):
                s = sum(V_(int(rng.choice(oth[j])), j) for i, j in pr); ge += s >= V; nl.append(s)
        return dict(matched=len(pr), V=V, p2=(1 + ge) / (R2 + 1), null_mean=float(np.mean(nl)) if nl else None)

# ---------------- G0 ----------------
for path, want in ((OKR_DB, OKR_SHA), (KFG_DB, KFG_SHA)):
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    if h != want: stop(f'G0 hash mismatch {path} {h}')
# ---------------- A0: K020 OKR loader verbatim ----------------
c = sqlite3.connect(OKR_DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
okrname = {r[0]: r[1] or '' for r in c.execute("select KHIPU_ID, OKR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
clpl = defaultdict(set); clcd = {}
for cid_, cl_, t_, v_ in c.execute("select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
    t_ = (t_ or '').strip()
    if t_ in ('S', 'L', 'E') and v_: clpl[cl_].add(place(int(v_)) if t_ == 'S' else 0)
    clcd[cl_] = cid_
ordn_ = {r[0]: r[1] for r in c.execute("select CLUSTER_ID, ORDINAL from knot_cluster")}
bc_ = defaultdict(dict)
for cl_, pl_ in clpl.items():
    if len(pl_) == 1 and ordn_.get(cl_) is not None: bc_[clcd[cl_]][ordn_[cl_]] = next(iter(pl_))
R5 = {cd for cd, d in bc_.items() if len(d) >= 2 and not all(a > b for a, b in zip([d[o] for o in sorted(d)], [d[o] for o in sorted(d)][1:]))}
okh = defaultdict(list); ogr = defaultdict(list)
for khid, cid, cl in c.execute("select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups: continue
    v = 0 if cid in R5 else val.get(cid, 0); nm = okrname[khid] or str(khid); okh[nm].append(v)
    if not ogr[nm] or ogr[nm][-1][0] != cl: ogr[nm].append([cl, []])
    ogr[nm][-1][1].append(v)
ogr = {k: [g[1] for g in v] for k, v in ogr.items()}
PO = Pipe(okh, ogr); oobs = PO.allW(PO.base)
pub = json.load(open('analysis/k020_results.json'))
rep = {f"{d['A']}/{d['B']}": PO.W(oobs, d['A'], d['B']) for d in pub['discoveries']}
A0 = dict(leaders=PO.lt, distinct=PO.nd, n_elig=PO.N, published={f"{d['A']}/{d['B']}": d['W'] for d in pub['discoveries']}, reproduced=rep)
A0['pass'] = PO.lt == 2763 and PO.nd == 606 and all(rep[k] is not None and abs(rep[k] - v) < 1e-6 for k, v in A0['published'].items())
res['A0_okr_rebuild'] = A0; print('A0', A0, flush=True); dump()
if not A0['pass']: stop('A0 OKR rebuild failed')
if '--a0-only' in sys.argv: print('A0 only, no KFG statistic'); sys.exit(0)
# ---------------- KFG pendants + R5 (K073 port) + CordGroups (K071 parser) ----------------
k = sqlite3.connect(KFG_DB); sha = dict(k.execute('select name, sha256 from khipu'))
meta = {r[0]: dict(aliases=r[1] or '', museum=(r[2] or '').strip(), mnum=(r[3] or '').strip()) for r in k.execute('select name, aliases, museum_name, museum_number from khipu')}
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
pend = defaultdict(list); NR5 = 0
for khn, nm, v, kn in k.execute('select khipu, cord_name, value, knots from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0
    r5 = kfg_r5(kn); NR5 += r5; pend[khn].append((int(m.group(1)), 0 if r5 else x))
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
g0_bad, g1_bad = [], []; kkh, kgr = {}, {}
for f in sorted(glob.glob(f'{XLSX}/*.xlsx')):
    kn_ = f.split('/')[-1][:-5]
    if hashlib.sha256(open(f, 'rb').read()).hexdigest() != sha.get(kn_): g0_bad.append(kn_); continue
    spans = []
    for s in sheet_strings(f, 'CordGroups'):
        m = GRP.match(s)
        if m: spans.append((int(m.group(2)), int(m.group(3))))
        else:
            m = ONE.match(s)
            if m: spans.append((int(m.group(1)), int(m.group(1))))
    L = sorted(pend.get(kn_, [])); n = len(L)
    if n and [p for p, _ in L] == list(range(1, n + 1)) and [p for a, b in spans for p in range(a, b + 1)] == list(range(1, n + 1)):
        vals = [x for _, x in L]; kkh[kn_] = vals; kgr[kn_] = [vals[a - 1:b] for a, b in spans]
    elif n: g1_bad.append(kn_)
res['gates'] = dict(G0_xlsx_mismatch=g0_bad, G1_partition_rate=round(len(kkh) / max(1, len(kkh) + len(g1_bad)), 4), G1_bad=g1_bad, n_R5_masked=NR5)
print('KFG parsed', len(kkh), 'G1 bad', len(g1_bad), 'G0 bad', len(g0_bad), round(time.time() - T0, 1), flush=True)
if g0_bad: stop('G0 xlsx hash mismatch')
if res['gates']['G1_partition_rate'] < 0.95: stop('G1 partition rate below 0.95')
missing = {x: ('absent/G1' if x not in kkh else 'ok') for p in CONTROLS + [TARGET, STAGE1_ONLY] for x in p}
res['named_presence'] = missing
# ---------------- KFG stage 1 ----------------
rng = np.random.default_rng(SEED); P = Pipe(kkh, kgr); obs = P.allW(P.base)
res['kfg_corpus'] = dict(n_parsed=len(kkh), n_elig=P.N, leaders=P.lt, distinct=P.nd, elig_also_okr=sum(x in okh for x in P.ids))
print('KFG', res['kfg_corpus'], flush=True)
mx = []
for r in range(NNULL):
    mx.append(P.allW(P.nullc(rng)).max())
    if time.time() - T0 > 540: stop(f'wall clock in nulls after {r + 1}')
TW = float(np.percentile(mx, 95))
held = [int((P.allW(P.nullc(rng)) > TW).any()) for _ in range(NHELD)]; calib = sum(held) <= 3
elig = [i for i in range(P.N) if len(P.base[i]) >= 12]; found = 0
for t in range(NPLANT):
    a, b = rng.choice(elig, 2, replace=False); S = [list(s) for s in P.base]
    ia = np.sort(rng.choice(len(S[a]), 10, replace=False)); ib = np.sort(rng.choice(len(S[b]), 10, replace=False))
    for x, y in zip(ia, ib): S[b][y] = S[a][x]
    found += int(P.allW(S)[P.pidx(a, b)] > TW)
res['stage1'] = dict(T_W=TW, null_max=dict(min=float(min(mx)), median=float(np.median(mx)), max=float(max(mx))), heldout_with_discovery=sum(held),
                     calibrated=calib, plants_found=found, plants=NPLANT)
alld = sorted([(float(obs[p]), P.ids[P.AI[p]], P.ids[P.BI[p]]) for p in np.flatnonzero(obs > TW)], reverse=True)
res['stage1']['n_disc'] = len(alld); print('stage1', res['stage1'], round(time.time() - T0, 1), flush=True); dump()
# ---------------- KFG stage 2 ----------------
K = max(len(alld), 1); st2 = []
for w_, ka, kb in alld:
    s = P.stage2(ka, kb, rng); A_, B_ = meta.get(ka, {}), meta.get(kb, {})
    st2.append(dict(A=ka, B=kb, W=round(w_, 3), **s, stage2=bool(s['p2'] < 0.01 / K), known=frozenset((ka, kb)) in known,
                    A_in_okr=ka in okh, B_in_okr=kb in okh, A_meta=A_, B_meta=B_))
    print(ka, kb, round(w_, 1), s, round(time.time() - T0, 1), flush=True)
    if time.time() - T0 > 590: stop('wall clock in stage 2')
res['stage2'] = st2; res['K'] = len(alld)
def both(p): return any({d['A'], d['B']} == set(p) and d['stage2'] for d in st2)
def s1(p): return any({d['A'], d['B']} == set(p) for d in st2)
pos = {'/'.join(p): both(p) for p in CONTROLS}; ok = bool(calib and all(pos.values()))
named = {}
for p in CONTROLS + [TARGET, STAGE1_ONLY]:
    named['/'.join(p)] = dict(W=P.W(obs, *p), stage1=s1(p), stage2=both(p))
tgt_present = all(x in P.ids for x in TARGET)
if not ok: tv = 'NOT TESTABLE (pipeline failed: calibration or a positive control missed)'
elif not tgt_present: tv = 'NOT TESTABLE (pair absent or ineligible in KFG)'
elif both(TARGET): tv = 'REPLICATED (confirmed in both stages)'
else: tv = 'CHANGED (correction): not confirmed in both stages on KFG'
s1v = ('REPLICATED (stage 1 only)' if s1(STAGE1_ONLY) and not both(STAGE1_ONLY) else
       'CHANGED: now confirmed in both stages' if both(STAGE1_ONLY) else 'CHANGED: no longer passes stage 1') if ok else 'NOT TESTABLE (pipeline failed)'
res['decision'] = dict(pipeline_ok=ok, positive_controls=pos, named=named, target_verdict=tv, KH0491_KH0503_verdict=s1v,
                       confirmed_new_candidates=[f"{d['A']}/{d['B']}" for d in st2 if d['stage2'] and not d['known'] and frozenset((d['A'], d['B'])) not in {frozenset(p) for p in CONTROLS}])
dump(); print(json.dumps(res['decision'], indent=1, default=str))
