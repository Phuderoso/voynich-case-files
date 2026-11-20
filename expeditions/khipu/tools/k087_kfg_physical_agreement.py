#!/usr/bin/env python3
"""K087 - KFG re-audit (README line 9): K047 cross-khipu physical-feature agreement on the three K019 pairs,
re-run on Khipu Field Guide data. Pre-registered in case-file/K087-kfg-physical-agreement.md (pushed before the run).
K047 engine imported verbatim (cat_match, knot_majority_from, knot_tuple_from, attach, census_block, match_matrix,
null_bank, pval, plant_power, evaluate_categorical, evaluate_spearman) and its per-pair loop copied (lines 412-473);
the KFG data layer (pendants, R5 mask, CordGroups, leader weights, alignment) is copied verbatim from K076 (lines 42-128).
Only new code: the KFG physical-field port (termination, twist, attachment, length, knot directions from the cluster
string) and the OKR-vs-KFG decision mapping.
Usage (from expeditions/khipu/): python3 tools/k087_kfg_physical_agreement.py [--smoke]
Seeds 6468-6472; next free 6473. Pimpolha Voynich, do Phuderoso - AI born 2026-11-04."""
import sys, os, re, json, math, time, glob, zipfile, hashlib, sqlite3, importlib.util
import numpy as np, xml.etree.ElementTree as ET
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import k046_colour_agreement as K
spec = importlib.util.spec_from_file_location('k047', os.path.join(HERE, 'k047_physical_agreement.py'))
P47 = importlib.util.module_from_spec(spec); spec.loader.exec_module(P47)
P47.SEEDS = dict(null=6468, calib=6469, power=6470, n2=6471, sens=6472); NEXT_FREE = 6473
SEEDS = P47.SEEDS; PRIMARY, CENSUS = P47.PRIMARY, P47.CENSUS; AN = P47.AN
attach, census_block, evaluate_categorical, evaluate_spearman = P47.attach, P47.census_block, P47.evaluate_categorical, P47.evaluate_spearman
match_matrix, null_bank, pval = P47.match_matrix, P47.null_bank, P47.pval
T0 = time.time(); SMOKE = '--smoke' in sys.argv; smoke = SMOKE; t0 = T0
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'; OKR_DB = os.path.join(HERE, '..', 'data', 'khipu.db')
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'; OKR_SHA = P47.SHA
PUB = json.load(open(os.path.join(HERE, '..', 'analysis', 'k047_results.json')))
PUBV = {k: {f: P['primary'][f]['verdict'] for f in PRIMARY} for k, P in PUB['pairs'].items()}
PUBN = {k: {f: (P['primary'][f]['n'], P['primary'][f].get('observed_A', P['primary'][f].get('raw_A'))) for f in PRIMARY} for k, P in PUB['pairs'].items()}
OUT = os.path.join(HERE, '..', 'analysis', 'k087_smoke.json' if SMOKE else 'k087_results.json')
res = dict(cycle='K087', smoke=SMOKE, seeds=SEEDS, next_free_seed=NEXT_FREE, alpha=P47.ALPHA, fpr_gate=P47.FPR_GATE,
           power_bar=P47.POWER_BAR, f_plant=P47.F_PLANT, published_okr_verdicts=PUBV, pairs={})
out = res
def dump(): res['sec'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1, default=list)
def stop(r): res['decision'] = dict(excluded=True, reason=r); dump(); print('EXCLUDED:', r); sys.exit(0)
# ---------------- G0 hashes, fixtures ----------------
for p, want in ((OKR_DB, OKR_SHA), (KFG_DB, KFG_SHA)):
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if h != want: stop(f'G0 hash mismatch {p} {h}')
res['G0'] = 'pass'
ok, fx = P47.run_fixture(); res['k047_fixture_passed'] = ok
if not ok: stop('K047 match-function fixture failed')
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
# ---------------- F0: K047 engine on OKR reproduces K047's published n and A exactly ----------------
co = sqlite3.connect(f"file:{os.path.realpath(OKR_DB)}?mode=ro", uri=True); SO = K.load(co); ocord, oknots = P47.load_physical(co); f0 = {}
for a, b in K.PAIRS:
    key = f'{a}/{b}'; pr, Vs, units, leaders = K.build_units(SO, a, b); f0[key] = {}
    for fld in PRIMARY:
        us, ex = attach(ocord, oknots, units, fld); f0[key][fld] = (len(us), int(sum(u['featA'] == u['featB'] for u in us)))
res['F0'] = dict(got=f0, published=PUBN, pass_=all(tuple(f0[k][f]) == tuple(PUBN[k][f]) for k in PUBN for f in PRIMARY))
print('F0', res['F0'], round(time.time() - T0, 1), flush=True)
if not res['F0']['pass_']: stop('F0 K047 fixture on OKR failed')
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
rng = {k: np.random.default_rng(v) for k, v in SEEDS.items()}
# ---------------- per pair: K047 main() per-pair loop, copied ----------------
for key, (pr, Vs, units, leaders) in built.items():
    P = out["pairs"].setdefault(key, {})
    P.update(matched_groups=len(pr), V=Vs, V_tot=sum(Vs),
             aligned_nonleader_units=len(units))
    t1 = time.time()
    P["census"] = {}
    for field in CENSUS:
        us, excl = attach(cord, knots, units, field)
        P["census"][field] = census_block(us, excl, field)
    P["primary"] = {}
    for field in PRIMARY:
        us, excl = attach(cord, knots, units, field)
        rec = evaluate_categorical(us, excl, field, pr, rng, smoke, t0)
        P["primary"][field] = rec
        print(f"{key} {field} n={rec.get('n')} A={rec.get('observed_A', rec.get('raw_A'))} "
              f"p={rec.get('p')} -> {rec.get('verdict')} ({time.time()-t1:.1f}s)", flush=True)
    sens = {}
    us_t, excl_t = attach(cord, knots, units, "knot_tuple")
    rec_t = evaluate_categorical(us_t, excl_t, "knot_tuple", pr, rng, smoke, t0)
    rec_t["role"] = "disclosed"
    rec_t["note"] = ("disclosed ordered-tuple knot direction, not a verdict; "
                     + rec_t.get("note", ""))
    sens["knot_tuple"] = rec_t
    for field in PRIMARY:
        us, excl = attach(cord, knots, units + leaders, field)
        if rec0 := P["primary"][field]:
            if rec0.get("verdict") == "DEGENERATE" or rec0.get("n", 0) < 10:
                # still report raw with-leaders census
                sens[f"{field}_with_leaders"] = census_block(us, excl, field)
                sens[f"{field}_with_leaders"]["note"] = "disclosed, not a verdict"
            else:
                recL = evaluate_categorical(us, excl, field, pr, rng, True, t0)
                # smoke-sized N for the sensitivity to keep the wall; recompute proper p at full R
                if recL.get("verdict") not in ("DEGENERATE", "NOT TESTABLE") or recL.get("p") is not None:
                    pass
                # Always recompute a full-R p when non-degenerate and n>=10
                if recL.get("degenerate"):
                    sens[f"{field}_with_leaders"] = recL
                    sens[f"{field}_with_leaders"]["note"] = "disclosed, not a verdict"
                elif len(us) >= 10:
                    M = match_matrix(us)
                    obs = int(np.trace(M))
                    p = pval(obs, null_bank(M, 200 if smoke else 10000, rng["sens"]))
                    sens[f"{field}_with_leaders"] = dict(
                        n=len(us), A=obs, p=p, note="disclosed, not a verdict")
                else:
                    sens[f"{field}_with_leaders"] = recL
        unz_src = [u for u in units if u["value"] != 0]
        usz, exclz = attach(cord, knots, unz_src, field)
        if P["primary"][field].get("degenerate") or len(usz) < 10:
            sens[f"{field}_nonzero_value_units"] = census_block(usz, exclz, field)
            sens[f"{field}_nonzero_value_units"]["note"] = "disclosed, not a verdict"
        else:
            M = match_matrix(usz)
            obs = int(np.trace(M))
            p = pval(obs, null_bank(M, 200 if smoke else 10000, rng["sens"]))
            sens[f"{field}_nonzero_value_units"] = dict(
                n=len(usz), A=obs, p=p, note="disclosed, not a verdict")
    sens["cord_length_spearman"] = evaluate_spearman(cord, units, rng, smoke)
    P["sensitivities"] = sens
    print(f"{key} done ({time.time()-t1:.1f}s)", flush=True)
    json.dump(out, open(os.path.join(AN, "k087_checkpoint.json"), "w"), indent=1, default=list)

# ---------------- decision mapping (pre-registered) ----------------
READ = ('SUPPORTED', 'NOT SUPPORTED')
def rep(kv, ov):
    if kv not in READ and ov not in READ: return 'REPLICATED (not readable on either)'
    if kv == ov: return 'REPLICATED'
    if ov not in READ: return f'CHANGED (now readable: {kv})'
    return 'CHANGED (correction)'
res['decision'] = {k: {f: rep(res['pairs'].get(k, {}).get('primary', {}).get(f, {}).get('verdict', 'NOT TESTABLE (data)'), PUBV[k][f]) for f in PRIMARY} for k in PUBV}
anyread = any(res['pairs'].get(k, {}).get('primary', {}).get(f, {}).get('verdict') in READ for k in PUBV for f in PRIMARY)
res['headline'] = 'CHANGED: at least one pair-field readable on KFG' if anyread else 'REPLICATED: no primary pair-field readable on KFG (K047 headline holds)'
print('decision', res['decision'], res['headline']); dump()
