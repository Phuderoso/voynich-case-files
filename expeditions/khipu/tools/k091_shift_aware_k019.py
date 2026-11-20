#!/usr/bin/env python3
"""K091 - K019 cord-level check of the K018 pairs (KH0097-KH0586, KH0192-KH0470, KH0192-KH0469) on KFG and OKR with a
SHIFT-AWARE exact null and an EXHAUSTIVE calibration corpus. Pre-registered in case-file/K091-shift-aware-k019.md.
Derived from tools/k090_kfg_k019_cord_level.py (K090, fde05b9) by a scripted patch; every change is marked K091.
- Statistic unchanged (V_tot = sum of LCS of non-leaders over leader-matched groups).
- K091 null: each matched B_j receives a uniformly random leader group i2 of A with |i2 - i| > W (W = 1 primary:
  the true partner AND its two neighbours in A's leader-group order are excluded). Descriptive: W = 0 (K090), 2, 3.
- K091 calibration: ALL ordered pairs of candidate KFG khipus (not a 20 000-draw sample), same >= 8 / fallback >= 5 rule,
  no cap; pairs where some matched group has no admissible alternative under W are dropped and counted.
Usage (from expeditions/khipu/): timeout 600 python3 tools/k091_shift_aware_k019.py run [--smoke]
Seeds: MC 6487, power 6488, curve 6489; next free 6490. Pimpolha Voynich, do Phuderoso - AI born 2026-11-04."""
import sys, os, re, json, math, time, glob, zipfile, hashlib, sqlite3, subprocess, tempfile, shutil
import numpy as np, xml.etree.ElementTree as ET
from fractions import Fraction
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import k046_colour_agreement as K
T0 = time.time(); SMOKE = '--smoke' in sys.argv
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'; OKR_DB = os.path.join(HERE, '..', 'data', 'khipu.db')
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'; OKR_SHA = K.SHA
K019_TOOL = os.path.join(HERE, 'k019_cord_level.py'); K019_PUB = os.path.join(HERE, '..', 'analysis', 'k019_results.json')
SEEDS = dict(mc=6487, power=6488, curve=6489); NEXT_FREE = 6490  # K091
W = 1; W_DESC = (0, 2, 3)  # K091 exclusion radius
PAIRS = K.PAIRS; M_FAM = 3; ALPHA_FAM = 0.01; ALPHA_PAIR = ALPHA_FAM / M_FAM   # K019: Bonferroni 0.01/3; here Holm at 0.01
FPR_GATE = 0.02; SHIFT_GATE = 0.10; POWER_BAR = 0.5; F_PLANT = 0.25; F_CURVE = (0.10, 0.15, 0.25, 0.40)
N_CAL = 20 if SMOKE else 200; MIN_GROUPS, MIN_GROUPS_FALLBACK, MIN_CAL = 8, 5, 100; MAX_TRY = 20000
R_MC = 500 if SMOKE else 10000
OUT = os.path.join(HERE, '..', 'analysis', 'k091_smoke.json' if SMOKE else 'k091_results.json')
res = dict(cycle='K091', W=W, smoke=SMOKE, seeds=SEEDS, next_free_seed=NEXT_FREE, alpha_family=ALPHA_FAM, alpha_pair_first_holm_step=ALPHA_PAIR,
           fpr_gate=FPR_GATE, shift_gate=SHIFT_GATE, power_bar=POWER_BAR, f_plant=F_PLANT, pairs={}, okr_exact={})
def dump(): res['sec'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1, default=str)
def stop(r): res['decision'] = dict(excluded=True, reason=r); dump(); print('EXCLUDED:', r); sys.exit(0)
# ---------------- G0 hashes ----------------
for p, want in ((OKR_DB, OKR_SHA), (KFG_DB, KFG_SHA)):
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if h != want: stop(f'G0 hash mismatch {p} {h}')
res['G0'] = 'pass'
# ---------------- exact-null engine (new code) ----------------
def lcs(a, b):  # K019 verbatim
    d = [0] * (len(b) + 1)
    for x in a:
        p = 0
        for j, y in enumerate(b):
            t = d[j + 1]; d[j + 1] = p + 1 if x == y else max(d[j + 1], d[j]); p = t
    return d[-1]
def exact_null(choices, obs):
    """choices: list (one per matched B group) of lists of integer scores, each equally likely.
    Returns exact P(S >= obs) as a Fraction, the exact mean and the max of S = sum of one independent pick per list."""
    dist = {0: 1}; tot = 1
    for ch in choices:
        c = Counter(ch); new = defaultdict(int)
        for s, w in dist.items():
            for v, k in c.items(): new[s + v] += w * k
        dist = new; tot *= len(ch)
    ge = sum(w for s, w in dist.items() if s >= obs)
    mean = Fraction(sum(s * w for s, w in dist.items()), tot)
    return Fraction(ge, tot), mean, max(dist)
def brute(choices, obs):
    import itertools
    n = ge = 0
    for pick in itertools.product(*choices): n += 1; ge += sum(pick) >= obs
    return Fraction(ge, n)
fr = np.random.default_rng(0); fx = []
for t in range(40):
    ch = [list(fr.integers(0, 6, size=int(fr.integers(1, 5)))) for _ in range(int(fr.integers(1, 6)))]
    ch = [[int(x) for x in c] for c in ch]; o = int(fr.integers(0, 4 * len(ch) + 2))
    fx.append(exact_null(ch, o)[0] == brute(ch, o))
fx.append(exact_null([[0, 1], [0, 1]], 2)[0] == Fraction(1, 4)); fx.append(exact_null([[3, 3, 3]], 3)[0] == 1)
res['exact_fixture'] = dict(cases=len(fx), passed=sum(fx))
if not all(fx): stop('exact-null fixture failed')
def adm(i, n, w=None):  # K091
    w = W if w is None else w
    return [i2 for i2 in range(n) if abs(i2 - i) > w]
def scores(GA, GB, pr, w=None):
    """V per matched pair, and for each matched (i, j) the list of V(i2, j) over i2 != i (K019 'others')."""
    cache = {}
    def V_(i2, j):
        if (i2, j) not in cache: cache[(i2, j)] = lcs(GA[i2][0][1:], GB[j][0][1:])
        return cache[(i2, j)]
    V = [V_(i, j) for i, j in pr]
    others = [[V_(i2, j) for i2 in adm(i, len(GA), w)] for i, j in pr]  # K091
    return V, others, V_
def exact_p(GA, GB, pr, w=None):
    V, others, V_ = scores(GA, GB, pr, w)
    if any(len(o) == 0 for o in others): return None, others, V_  # K091: no admissible alternative
    p, mean, mx = exact_null(others, sum(V))
    return dict(V=V, V_tot=sum(V), p_exact=p, null_mean=mean, null_max=mx), others, V_
def shift_fpr(GA, GB, pr, V_):
    m = len(pr); ps = []
    for k in range(1, m):
        fake = [(pr[(g + k) % m][0], pr[g][1]) for g in range(m)]
        o = sum(V_(i, j) for i, j in fake)
        ch = [[V_(i2, j) for i2 in adm(i, len(GA))] for i, j in fake]  # K091
        if any(len(c) == 0 for c in ch): ps.append(Fraction(1)); continue
        ps.append(exact_null(ch, o)[0])
    return ps
def holm(pd, alpha, m):
    keys = sorted(pd, key=lambda k: pd[k]); out = {k: False for k in pd}
    for r, k in enumerate(keys):
        if pd[k] < alpha / (m - r): out[k] = True
        else: break
    return out
# ---------------- A0: K019 tool verbatim on the OKR, in a scratch dir ----------------
pub = json.load(open(K019_PUB)); tmp = tempfile.mkdtemp(prefix='k091_a0_'); os.makedirs(os.path.join(tmp, 'analysis'))
pr_ = subprocess.run([sys.executable, K019_TOOL, os.path.realpath(OKR_DB)], cwd=tmp, capture_output=True, text=True, timeout=300)
try: got = json.load(open(os.path.join(tmp, 'analysis', 'k019_results.json')))
except Exception: got = {}
shutil.rmtree(tmp, ignore_errors=True)
a0 = got.get('results') == pub['results'] and got.get('R') == pub['R']
res['A0'] = dict(pass_=a0, rc=pr_.returncode, note='k019_cord_level.py run unchanged on OKR; results dict compared to the published k019_results.json (sec excluded)')
print('A0', a0, round(time.time() - T0, 1), flush=True)
if not a0: stop('A0 K019 rebuild failed')
# ---------------- OKR exact arm (descriptive + K019 relabel check) ----------------
co = sqlite3.connect(f"file:{os.path.realpath(OKR_DB)}?mode=ro", uri=True); SO = K.load(co)
for a, b in ([] if SMOKE else PAIRS):  # the smoke never computes the OKR exact arm
    key = f'{a}/{b}'; GA, GB = SO['lgroups'](SO['byokr'][a]), SO['lgroups'](SO['byokr'][b])
    pr = SO['walign']([g[0][0] for g in GA], [g[0][0] for g in GB]); e, others, V_ = exact_p(GA, GB, pr)
    pw_desc = {str(w): float(exact_p(GA, GB, pr, w)[0]['p_exact']) for w in W_DESC if exact_p(GA, GB, pr, w)[0] is not None}  # K091
    sp = shift_fpr(GA, GB, pr, V_)
    res['okr_exact'][key] = dict(matched_groups=len(pr), V_tot=e['V_tot'], same_as_K019=(e['V'] == pub['results'][key]['V']),
        p_exact=e['p_exact'], p_exact_float=float(e['p_exact']), null_mean=float(e['null_mean']), null_max=e['null_max'],
        shift_offsets=len(sp), fpr_shift=float(np.mean([x < ALPHA_PAIR for x in sp])) if sp else None, p_exact_by_W=pw_desc, shift_p=[float(x) for x in sp])
print('OKR exact', json.dumps(res['okr_exact'], default=str), flush=True); dump()
# ---- KFG data layer, verbatim from K076 lines 42-124 ----
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
need = sorted({x for p in PAIRS for x in p})
res['kfg_data'] = dict(n_with_pendants=len(pend), n_grouped=len(groups), G1_bad=len(g1_bad), n_eligible=len(ids), n_R5_masked=NR5[0],
                       pair_khipus_eligible={kh: kh in ids for kh in need})
missing = [kh for kh in need if kh not in ids]
if SMOKE:  # non-leader values shuffled within each khipu (only the smoke ever sees this)
    sr = np.random.default_rng(0)
    for kh in groups:
        lead = {a for a, b in groups[kh]}; pos = [i for i in range(len(VAL[kh])) if i not in lead]
        vals = [VAL[kh][i] for i in pos]; perm = sr.permutation(len(pos))
        for i, q in zip(pos, perm): VAL[kh][i] = vals[q]
# ---------------- KFG named pairs ----------------
rng_mc = np.random.default_rng(SEEDS['mc']); pvals = {}; gx = {}
for a, b in PAIRS:
    key = f'{a}/{b}'; P = res['pairs'].setdefault(key, {})
    if a in missing or b in missing: P['verdict'] = 'NOT TESTABLE (data)'; continue
    GA, GB = lgroups(a), lgroups(b); pr = walign([g[0][0] for g in GA], [g[0][0] for g in GB])
    if len(pr) < 2 or len(GA) < 2: P['verdict'] = 'NOT TESTABLE (data)'; P['reason'] = 'fewer than 2 matched groups'; continue
    e, others, V_ = exact_p(GA, GB, pr)
    if e is None: P['verdict'] = 'NOT TESTABLE (data)'; P['reason'] = 'a matched group has no admissible alternative'; continue
    P['p_exact_by_W'] = {str(w): float(exact_p(GA, GB, pr, w)[0]['p_exact']) for w in W_DESC if exact_p(GA, GB, pr, w)[0] is not None}  # K091 descriptive
    # K019 Monte Carlo procedure, verbatim draw order (cross-check only)
    oth = {j: adm(i, len(GA)) for i, j in pr}; ge = 0; obs = e['V_tot']; nulls = []  # K091
    for r in range(R_MC):
        s = sum(V_(int(rng_mc.choice(oth[j])), j) for i, j in pr); nulls.append(s); ge += s >= obs
    p_mc = (1 + ge) / (R_MC + 1); pe = float(e['p_exact'])
    tol = 4 * math.sqrt(max(pe * (1 - pe), 1e-12) / R_MC) + 2 / R_MC; gx[key] = abs(p_mc - pe) <= tol
    sp = shift_fpr(GA, GB, pr, V_); fs = float(np.mean([x < ALPHA_PAIR for x in sp]))
    # Kryptos-borrowed multiplicity look (descriptive): leave-one-matched-group-out, strict winners
    loo = []
    for g in range(len(pr)):
        pr2 = pr[:g] + pr[g + 1:]; loo.append(float(exact_p(GA, GB, pr2)[0]['p_exact']))
    win = sum(V_(i, j) > max(others[g]) for g, (i, j) in enumerate(pr)); tie = sum(V_(i, j) == max(others[g]) for g, (i, j) in enumerate(pr))
    P.update(matched_groups=len(pr), pairs_ij=pr, V=e['V'], V_tot=obs, okr_V=pub['results'][key]['V'], okr_V_tot=pub['results'][key]['V_tot'],
             A_groups=len(GA), p_exact=e['p_exact'], p_exact_float=pe, null_mean=float(e['null_mean']), null_max=e['null_max'],
             p_mc=p_mc, mc_null_mean=float(np.mean(nulls)), mc_null_max=int(max(nulls)), mc_agrees=gx[key],
             shift_offsets=len(sp), fpr_shift=fs, shift_p_min=float(min(sp)) if sp else None,
             shift_p=[float(x) for x in sp], loo_max_p=max(loo), loo_argmax_group=int(np.argmax(loo)), strict_winners=win, ties_at_max=tie)
    P['pair_gate'] = 'TOOL EXCLUDED (shift)' if fs > SHIFT_GATE else 'ok'
    if P['pair_gate'] == 'ok': pvals[key] = pe
    print(f"{key} groups={len(pr)} V={obs} null_mean={float(e['null_mean']):.2f} max={e['null_max']} p_exact={pe:.3e} p_mc={p_mc:.5f} shift={fs:.3f} loo_max={max(loo):.2e} win={win}", flush=True)
    dump()
res['G_EX'] = dict(pass_=all(gx.values()), per_pair=gx)
# ---------------- calibration corpus: random unrelated KFG pairs ----------------
named = set(need); pool = sorted(k for k in ids if k not in named); LG = {k: lgroups(k) for k in pool}
cand = [k for k in pool if len(LG[k]) >= 2]
ALN = {}  # K091: exhaustive enumeration of all ordered candidate pairs (smoke: first 40 candidates only)
_cc = cand[:40] if SMOKE else cand
for a in _cc:
    for b in _cc:
        if a != b:
            pr = walign([g[0][0] for g in LG[a]], [g[0][0] for g in LG[b]])
            if len(pr) >= MIN_GROUPS_FALLBACK: ALN[(a, b)] = pr
print('enumerated', len(_cc) * (len(_cc) - 1), 'ordered pairs; >=5 groups:', len(ALN), round(time.time() - T0, 1), flush=True)
NO_ADM = {}
def draw(min_g):
    out = []; drop = 0
    for (a, b), pr in sorted(ALN.items()):
        if len(pr) < min_g: continue
        if exact_p(LG[a], LG[b], pr)[0] is None: drop += 1; continue
        out.append((a, b, pr))
    NO_ADM[min_g] = drop
    return out, len(_cc) * (len(_cc) - 1)
cal, tries = draw(MIN_GROUPS); used_min = MIN_GROUPS
if len(cal) < MIN_CAL: cal, tries = draw(MIN_GROUPS_FALLBACK); used_min = MIN_GROUPS_FALLBACK
cp = [float(exact_p(LG[a], LG[b], pr)[0]['p_exact']) for a, b, pr in cal]
fpr = float(np.mean([p < ALPHA_PAIR for p in cp])) if cp else None
res['G_FPR'] = dict(n_pairs=len(cal), enumerated=tries, dropped_no_admissible=NO_ADM, min_groups=used_min, candidates=len(cand), fpr_at_alpha_pair=fpr,
                    fpr_at_0_05=float(np.mean([p < 0.05 for p in cp])) if cp else None, mean_p=float(np.mean(cp)) if cp else None,
                    hits=[(a, b, len(pr), p) for (a, b, pr), p in zip(cal, cp) if p < ALPHA_PAIR],
                    pass_=bool(len(cal) >= MIN_CAL and fpr is not None and fpr <= FPR_GATE))
print('G_FPR', {k: v for k, v in res['G_FPR'].items() if k != 'hits'}, 'hits', len(res['G_FPR']['hits']), round(time.time() - T0, 1), flush=True); dump()
# ---------------- power: planted partial copy on the same pairs ----------------
def plant(GA, GB, pr, f, r):
    GB2 = [(list(v), c) for v, c in GB]
    for i, j in pr:
        va = GA[i][0][1:]; vb = GB2[j][0]
        for y in range(1, len(vb)):
            if y - 1 < len(va) and r.random() < f: vb[y] = va[y - 1]
    return GB2
def power(f, seed):
    r = np.random.default_rng(seed); ps = []
    for a, b, pr in cal: ps.append(float(exact_p(LG[a], plant(LG[a], LG[b], pr, f, r), pr)[0]['p_exact']))
    return float(np.mean([p < ALPHA_PAIR for p in ps])) if ps else None
pw = power(F_PLANT, SEEDS['power']); curve = {str(f): power(f, SEEDS['curve']) for f in F_CURVE}
res['G_POW'] = dict(f=F_PLANT, power=pw, curve=curve, pass_=bool(pw is not None and pw >= POWER_BAR))
print('G_POW', res['G_POW'], round(time.time() - T0, 1), flush=True); dump()
# ---------------- decision ----------------
pipe = res['G_EX']['pass_'] and res['G_FPR']['pass_']   # gates any reading; G_POW gates only a NOT CONFIRMED
rej = holm(pvals, ALPHA_FAM, M_FAM)
okr_rej = holm({k: v['p_exact_float'] for k, v in res['okr_exact'].items() if (v['fpr_shift'] or 0) <= SHIFT_GATE}, ALPHA_FAM, M_FAM)
dec = {}
for a, b in PAIRS:
    key = f'{a}/{b}'; P = res['pairs'][key]
    if 'verdict' in P: v = P['verdict']
    elif not pipe: v = 'NOT TESTABLE (pipeline gate)'
    elif P['pair_gate'] != 'ok': v = P['pair_gate']
    elif rej[key]: v = 'CONFIRMED'
    else: v = 'NOT CONFIRMED' if res['G_POW']['pass_'] else 'NOT TESTABLE (power)'
    P['verdict'] = v; P['bonferroni_K019_rule'] = bool(P.get('p_exact_float', 1) < ALPHA_PAIR)
    dec[key] = 'REPLICATED' if v == 'CONFIRMED' else ('CHANGED (correction)' if v == 'NOT CONFIRMED' else 'NOT TESTABLE')
    if key not in res['okr_exact']: continue
    o = res['okr_exact'][key]; o['verdict_new_rules'] = ('TOOL EXCLUDED (shift)' if (o['fpr_shift'] or 0) > SHIFT_GATE else
                                                       ('CONFIRMED' if okr_rej.get(key) else 'NOT CONFIRMED'))
    o['K019_correction'] = o['verdict_new_rules'] != 'CONFIRMED'
res['pipeline_gates_pass'] = pipe; res['decision'] = dec
print('decision', dec, 'okr', {k: v['verdict_new_rules'] for k, v in res['okr_exact'].items()}); dump()
