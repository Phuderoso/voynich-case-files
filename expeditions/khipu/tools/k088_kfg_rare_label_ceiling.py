#!/usr/bin/env python3
"""K088 - KFG re-audit (README line 9) of K048: rare-label concordance (dual 'B' terminations, dual 'S' majority knot
direction) on the three K019 pairs, plus a pre-registered exact margin-ceiling gate (attainable alpha).
Pre-registered in case-file/K088-kfg-rare-label-ceiling.md (pushed before the real run).
K048 engine imported verbatim (fixture, knot_majority_from, attach, rare_match_matrix, null_bank, pval,
plant_rare_power, margins, is_degenerate, evaluate, sensitivity_block) and its per-pair loop copied (lines 395-419).
KFG knot-direction port (K087 lines 41-57) and the KFG data layer + physical port (K087 lines 67-177, itself K076's
layer verbatim) are copied verbatim. Only new code: the exact hypergeometric ceiling (p_floor) with its fixture and the
two-track decision mapping (frozen K048 rules vs K048 + ceiling gate) applied to both OKR (F0) and KFG.
Usage (from expeditions/khipu/): python3 tools/k088_kfg_rare_label_ceiling.py [--smoke]
Seeds 6473-6477 (copy-all derived seed 6475+100 = 6575, as in the K048 engine); next free 6478.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04."""
import sys, os, re, json, math, time, glob, zipfile, hashlib, sqlite3, importlib.util
import numpy as np, xml.etree.ElementTree as ET
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import k046_colour_agreement as K
spec = importlib.util.spec_from_file_location('k048', os.path.join(HERE, 'k048_rare_label_concordance.py'))
P48 = importlib.util.module_from_spec(spec); spec.loader.exec_module(P48)
P48.SEEDS = dict(null=6473, calib=6474, power=6475, n2=6476, sens=6477); NEXT_FREE = 6478
SEEDS = P48.SEEDS; PRIMARY, RARE, ALPHA, AN = P48.PRIMARY, P48.RARE, P48.ALPHA, P48.AN
attach, evaluate, sensitivity_block, margins, is_degenerate = P48.attach, P48.evaluate, P48.sensitivity_block, P48.margins, P48.is_degenerate
T0 = time.time(); SMOKE = '--smoke' in sys.argv; smoke = SMOKE; t0 = T0
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'; OKR_DB = os.path.join(HERE, '..', 'data', 'khipu.db')
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'; OKR_SHA = P48.SHA
PUB = json.load(open(os.path.join(HERE, '..', 'analysis', 'k048_results.json')))
PUBV = {k: {f: P['primary'][f]['verdict'] for f in PRIMARY} for k, P in PUB['pairs'].items()}
PUBN = {k: {f: [P['primary'][f][x] for x in ('n', 'n_rare_A', 'n_rare_B', 'observed_A')] for f in PRIMARY} for k, P in PUB['pairs'].items()}
OUT = os.path.join(HERE, '..', 'analysis', 'k088_smoke.json' if SMOKE else 'k088_results.json')
res = dict(cycle='K088', smoke=SMOKE, seeds=SEEDS, copy_all_seed=SEEDS['power'] + 100, next_free_seed=NEXT_FREE, alpha=ALPHA,
           fpr_gate=P48.FPR_GATE, power_bar=P48.POWER_BAR, f_plant=P48.F_PLANT, published_okr_verdicts=PUBV, pairs={})
out = res
def dump(): res['sec'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1, default=list)
def stop(r): res['decision'] = dict(excluded=True, reason=r); dump(); print('EXCLUDED:', r); sys.exit(0)
# ---------------- G0 hashes, fixtures ----------------
for p, want in ((OKR_DB, OKR_SHA), (KFG_DB, KFG_SHA)):
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if h != want: stop(f'G0 hash mismatch {p} {h}')
res['G0'] = 'pass'
ok, fx = P48.run_fixture(); res['k048_fixture_passed'] = ok; res['k048_fixture_cases'] = len(fx)
if not ok: stop('K048 match-function fixture failed')
# ---------------- new code: exact margin ceiling (attainable alpha) ----------------
def hyper_sf(n, nA, nB, a):
    """P(X >= a), X ~ Hypergeometric(population n, nA successes, nB draws): the exact N1 tail."""
    lo, hi = max(0, nA + nB - n), min(nA, nB)
    tot = math.comb(n, nB)
    return sum(math.comb(nA, x) * math.comb(n - nA, nB - x) for x in range(max(a, lo), hi + 1)) / tot
def p_floor(n, nA, nB):
    """Smallest one-sided-excess p the observed margins allow: P(X = min(nA, nB)) = P(X >= min(nA, nB))."""
    return hyper_sf(n, nA, nB, min(nA, nB))
def ceiling_block(n, nA, nB, A):
    if is_degenerate(n, nA, nB): return dict(applicable=False, reason='degenerate')
    pf = p_floor(n, nA, nB); m = min(nA, nB)
    # smallest common rare count m* with 1/C(n, m*) < alpha (equal margins, perfect overlap): descriptive yardstick
    ms = next(k for k in range(1, n + 1) if 1 / math.comb(n, k) < ALPHA)
    return dict(applicable=True, A_max=m, p_floor=pf, p_exact_obs=hyper_sf(n, nA, nB, A), fires=bool(pf >= ALPHA),
                min_equal_margin_for_alpha=ms, conditional_power_at_alpha=0.0 if pf >= ALPHA else None)
CFX = [((87, 4, 1), 4 / 87), ((5, 2, 2), 1 / 10), ((36, 3, 2), 3 / 630), ((37, 1, 3), 3 / 37), ((10, 5, 5), 1 / 252)]
cfx = [dict(case=c, expected=w, got=p_floor(*c)) for c, w in CFX]
cfx.append(dict(case='sf(87,4,1,0) == 1', expected=1.0, got=hyper_sf(87, 4, 1, 0)))
cfx.append(dict(case='sf(36,3,2,1) == 1 - C(33,2)/C(36,2)', expected=1 - math.comb(33, 2) / math.comb(36, 2), got=hyper_sf(36, 3, 2, 1)))
res['ceiling_fixture'] = cfx
if not all(abs(x['got'] - x['expected']) < 1e-12 for x in cfx): stop('ceiling fixture failed')
def verdict_ceiling(frozen, n, nA, nB):
    """Track B: excluded/degenerate first (frozen), then the ceiling gate, then the frozen K048 verdict."""
    if frozen in ('DEGENERATE', 'NOT TESTABLE (data)') or frozen.startswith('EXCLUDED'): return frozen
    return 'NOT TESTABLE (margin ceiling)' if p_floor(n, nA, nB) >= ALPHA else frozen
TOK = re.compile(r'^(\d+)([A-Z]+)\(([-\d.]+),([^)]*)\),(-?\d+)(\[[^\]]*\])?$')
def kfg_dirs(knots):
    """Per-knot direction list from a KFG cluster string (pre-registered port).
    Direction string of length > 1: one letter per knot. Else: S-type clusters ('S','SP') give n knots, every other type
    (L, E, EE, LL, TF, BL, U, ...) gives 1 knot. A trailing [..] annotation is ignored. Unparsed tokens are skipped."""
    d = []
    for t in str(knots or '').split(';'):
        m = TOK.match(t.strip())
        if not m: continue
        n, typ, dr = int(m.group(1)), m.group(2), m.group(4).strip()
        if len(dr) > 1: d.extend(dr)
        else: d.extend([dr] * (n if typ in ('S', 'SP') else 1))
    return d
KFX = [('2S(28.0,Z),20;6L(35.5,Z),6', list('ZZZ')), ('1S(21.0,S),100', ['S']), ('3S(10.0,SZZ),300', list('SZZ')),
       ('2L(9.0,S),2[AXD]', ['S']), ('1E(30.0,U),1', ['U']), ('', []), (None, [])]
kfx = [dict(case=s, expected=w, got=kfg_dirs(s)) for s, w in KFX]; res['kfg_knot_fixture'] = kfx
if not all(x['got'] == x['expected'] for x in kfx): stop('KFG knot-direction fixture failed')
# ---------------- F0: K048 engine on OKR reproduces K048's published (n, n_rare_A, n_rare_B, A) exactly ----------------
co = sqlite3.connect(f"file:{os.path.realpath(OKR_DB)}?mode=ro", uri=True); SO = K.load(co); ocord, oknots = P48.load_physical(co); f0 = {}
for a, b in K.PAIRS:
    key = f'{a}/{b}'; pr, Vs, units, leaders = K.build_units(SO, a, b); f0[key] = {}
    for fld in PRIMARY:
        us, ex = attach(ocord, oknots, units, fld); f0[key][fld] = list(margins(us, RARE[fld]))
res['F0'] = dict(got=f0, published=PUBN, pass_=all(f0[k][f] == PUBN[k][f] for k in PUBN for f in PRIMARY))
print('F0', res['F0'], round(time.time() - T0, 1), flush=True)
if not res['F0']['pass_']: stop('F0 K048 fixture on OKR failed')
res['okr_ceiling'] = {k: {f: dict(**ceiling_block(*f0[k][f]), k048_verdict=PUBV[k][f],
                                  verdict_with_ceiling=verdict_ceiling(PUBV[k][f], *f0[k][f][:3])) for f in PRIMARY} for k in PUBN}
# ---- KFG data layer, verbatim from K076 lines 42-128 ----
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

# ---------------- KFG physical-field port (new code) ----------------
def nz(x):
    x = None if x is None else str(x).strip()
    return None if x in (None, '', '?', 'None', 'nan') else x
raw = {}
for kh, nm, tw, at, kn, tm, ln in kc.execute('select khipu, cord_name, twist, attachment, knots, termination, length from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if m: raw[(kh, int(m.group(1)))] = (tw, at, kn, tm, ln)
cord, knots = {}, {}
for kh in groups:
    for i, (pn, _, _) in enumerate(sorted(pend[kh])):
        tw, at, kn, tm, ln = raw[(kh, pn)]
        try: L = float(ln) if nz(ln) is not None else None
        except Exception: L = None
        cord[(kh, i)] = dict(twist=nz(tw), attachment=nz(at), termination=nz(tm), length=L)
        knots[(kh, i)] = kfg_dirs(kn)
if SMOKE:  # physical features shuffled within each khipu (only smoke ever sees this)
    sr = np.random.default_rng(0)
    for kh in groups:
        ks = [(kh, i) for i in range(len(pend[kh]))]; perm = sr.permutation(len(ks))
        cv = [cord[k] for k in ks]; kv = [knots[k] for k in ks]
        for k_, j in zip(ks, perm): cord[k_] = cv[j]; knots[k_] = kv[j]
built = {}
for a, b in K.PAIRS:
    key = f'{a}/{b}'
    if a in missing or b in missing: res['pairs'][key] = dict(verdict='NOT TESTABLE (data)'); continue
    built[key] = K.build_units(SK, a, b)
res['alignment'] = {k: dict(groups=len(v[0]), V=sum(v[1])) for k, v in built.items()}
print('alignment', res['alignment'], flush=True)
if any((v['groups'], v['V']) != K.K019[k] for k, v in res['alignment'].items()): stop('K019 consistency gate failed on KFG')
rng = {k: np.random.default_rng(v) for k, v in SEEDS.items()}
# ---------------- per pair: K048 main() per-pair loop, copied ----------------
for key, (pr, Vs, units, leaders) in built.items():
    P = out["pairs"].setdefault(key, {})
    P.update(matched_groups=len(pr), V=Vs, V_tot=sum(Vs),
             aligned_nonleader_units=len(units))
    t1 = time.time()
    P["primary"] = {}
    for field in PRIMARY:
        us, excl = attach(cord, knots, units, field)
        rec = evaluate(us, excl, field, pr, rng, smoke, t0)
        P["primary"][field] = rec
        print(f"{key} {field} n={rec.get('n')} nA={rec.get('n_rare_A')} "
              f"nB={rec.get('n_rare_B')} A={rec.get('observed_A')} "
              f"p={rec.get('p')} -> {rec.get('verdict')} ({time.time()-t1:.1f}s)",
              flush=True)
    sens = {}
    for field in PRIMARY:
        rare = RARE[field]
        usL, exclL = attach(cord, knots, units + leaders, field)
        sens[f"{field}_with_leaders"] = sensitivity_block(
            usL, exclL, field, rare, rng, smoke)
        unz_src = [u for u in units if u["value"] != 0]
        usz, exclz = attach(cord, knots, unz_src, field)
        sens[f"{field}_nonzero_value_units"] = sensitivity_block(
            usz, exclz, field, rare, rng, smoke)
    P["sensitivities"] = sens
    print(f"{key} done ({time.time()-t1:.1f}s)", flush=True)
    json.dump(out, open(os.path.join(AN, "k088_checkpoint.json"), "w"), indent=1, default=list)
# ---------------- ceiling on KFG + decision mapping (pre-registered) ----------------
READ = ('SUPPORTED', 'NOT SUPPORTED')
def rep(kv, ov):
    if kv not in READ and ov not in READ: return 'REPLICATED (not readable on either)'
    if kv == ov: return 'REPLICATED'
    if ov not in READ: return f'CHANGED (now readable: {kv})'
    return 'CHANGED (correction)'
kfgv, kfgc = {}, {}
for k in PUBV:
    kfgv[k], kfgc[k] = {}, {}
    for f in PRIMARY:
        r = res['pairs'].get(k, {}).get('primary', {}).get(f)
        if r is None: kfgv[k][f] = kfgc[k][f] = 'NOT TESTABLE (data)'; continue
        kfgv[k][f] = r['verdict']; r['ceiling'] = ceiling_block(r['n'], r['n_rare_A'], r['n_rare_B'], r['observed_A'])
        kfgc[k][f] = r['verdict_with_ceiling'] = verdict_ceiling(r['verdict'], r['n'], r['n_rare_A'], r['n_rare_B'])
res['decision'] = dict(
    trackA_frozen_k048={k: {f: rep(kfgv[k][f], PUBV[k][f]) for f in PRIMARY} for k in PUBV},
    trackB_with_ceiling={k: {f: rep(kfgc[k][f], res['okr_ceiling'][k][f]['verdict_with_ceiling']) for f in PRIMARY} for k in PUBV},
    k048_corrections=[dict(pair=k, field=f, published=PUBV[k][f], with_ceiling=res['okr_ceiling'][k][f]['verdict_with_ceiling'])
                      for k in PUBV for f in PRIMARY if res['okr_ceiling'][k][f]['verdict_with_ceiling'] != PUBV[k][f]])
anyread = any(kfgc[k][f] in READ for k in PUBV for f in PRIMARY)
res['headline'] = ('READABLE: at least one pair-field readable on KFG with the ceiling gate' if anyread else
                   'NOT READABLE: no primary pair-field readable on KFG once the margin ceiling is applied')
print('decision', json.dumps(res['decision'], indent=1), res['headline']); dump()
