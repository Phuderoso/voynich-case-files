#!/usr/bin/env python3
"""K089 - KFG re-audit (README line 9) of K049: cross-khipu colour agreement on the five K010 significant_S value-block
pairs, plus the K088 exact margin-ceiling gate (attainable alpha), here generalised to multi-category colour equality.
Pre-registered in case-file/K089-kfg-block-colour-ceiling.md (pushed before the real run).
K049 engine imported verbatim (K046 fixture/colour_match/match_matrix/null_bank/pval via K049, find/locate_side,
build_units, colour_units, degeneracy_reason, n2_blocks, plant_power, colkey, colour_pretty, build_sequences,
load_colour) and its per-pair loop COPIED VERBATIM (k049 lines 359-480; only the checkpoint path is a variable).
KFG data layer copied verbatim from K076 (lines 43-106: pendants ^p\\d+$ in pendant order, KFG value with R5 multi-number
pendants masked to 0 by the K072/K073 port, K074 primary colour coding split on ':' '-' '%' '^', CordGroups parser).
New code only: exact N1 null distribution of A by dynamic programming over colour classes (exact_null), p_floor =
P(A = A_max) with a fixture (hand cases + brute force), and the two-track decision mapping.
Usage (from expeditions/khipu/): python3 tools/k089_kfg_block_colour_ceiling.py values | run [--smoke]
Seeds: N1 6478, calibration 6479, power 6480, N2/sensitivities 6481, copy-all 6482; next free 6483.
A0 re-runs the K049 loop on the OKR with K049's own seeds 4949-4953 (not new seeds).
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04."""
import sys, os, re, json, math, time, glob, zipfile, hashlib, sqlite3, importlib.util, itertools
import numpy as np, xml.etree.ElementTree as ET
from fractions import Fraction
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
_s = importlib.util.spec_from_file_location('k049', os.path.join(HERE, 'k049_block_colour_agreement.py'))
K49 = importlib.util.module_from_spec(_s); _s.loader.exec_module(K49)
AN = os.path.join(HERE, '..', 'analysis')
ALPHA, FPR_GATE, POWER_BAR, F_PLANT, F_CURVE, WALL = K49.ALPHA, K49.FPR_GATE, K49.POWER_BAR, K49.F_PLANT, K49.F_CURVE, K49.WALL
colour_match, match_matrix, null_bank, pval = K49.colour_match, K49.match_matrix, K49.null_bank, K49.pval
colour_units, degeneracy_reason, n2_blocks, plant_power = K49.colour_units, K49.degeneracy_reason, K49.n2_blocks, K49.plant_power
colkey, colour_pretty, public_side, locate_side, build_units = K49.colkey, K49.colour_pretty, K49.public_side, K49.locate_side, K49.build_units
PAIRS = K49.PAIRS
SEEDS_K049 = dict(K49.SEEDS)
SEEDS = dict(null=6478, calib=6479, power=6480, n2_sens=6481, copyall=6482); NEXT_FREE = 6483
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'; OKR_DB = os.path.join(HERE, '..', 'data', 'khipu.db')
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'; OKR_SHA = K49.SHA
PUB = json.load(open(os.path.join(AN, 'k049_results.json')))
MODE = sys.argv[1] if len(sys.argv) > 1 else ''; SMOKE = '--smoke' in sys.argv
T0 = time.time()
OUT = os.path.join(AN, 'k089_smoke.json' if SMOKE else 'k089_results.json')
res = dict(cycle='K089', smoke=SMOKE, seeds=SEEDS, a0_seeds=SEEDS_K049, next_free_seed=NEXT_FREE, alpha=ALPHA,
           fpr_gate=FPR_GATE, power_bar=POWER_BAR, f_plant=F_PLANT)
def dump(): res['sec'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1, default=list)
def stop(r):
    res['decision'] = dict(excluded=True, reason=r)
    if MODE == 'run': dump()
    print('EXCLUDED:', r); sys.exit(0)

# ---------------- new code: exact N1 null of A (uniform permutation of B's colours) ----------------
def exact_null(colsA, colsB, match=colour_match):
    """Exact distribution of A = #{i: match(colA_i, colB_sigma(i))} over all n! permutations sigma.
    DP over A units; state = remaining count of each distinct B colour; ways multiply by the remaining count.
    Returns dict a -> Fraction (sums to 1)."""
    n = len(colsA); assert n == len(colsB)
    kB = []; cnt = []
    for c in colsB:
        if c in kB: cnt[kB.index(c)] += 1
        else: kB.append(c); cnt.append(1)
    mm = [[1 if match(a, b) else 0 for b in kB] for a in colsA]
    cur = {tuple(cnt): {0: 1}}
    for i in range(n):
        nxt = defaultdict(lambda: defaultdict(int))
        for st, poly in cur.items():
            for d, r in enumerate(st):
                if r == 0: continue
                ns = st[:d] + (r - 1,) + st[d + 1:]
                for a, w in poly.items(): nxt[ns][a + mm[i][d]] += w * r
        cur = nxt
    (poly,) = cur.values(); tot = math.factorial(n); assert sum(poly.values()) == tot
    return {a: Fraction(w, tot) for a, w in sorted(poly.items())}
def ceiling(colsA, colsB, A_obs):
    d = exact_null(colsA, colsB); amax = max(d); pf = d[amax]
    p_obs = sum(v for a, v in d.items() if a >= A_obs)
    return dict(A_max=amax, A_min=min(d), p_floor=float(pf), p_floor_frac=f'{pf.numerator}/{pf.denominator}',
                p_exact_obs=float(p_obs), exact_mean=float(sum(a * v for a, v in d.items())),
                fires=bool(pf >= ALPHA), conditional_power_at_alpha=(0.0 if pf >= ALPHA else None),
                dist={str(a): float(v) for a, v in d.items()})
def brute(colsA, colsB):
    n = len(colsA); c = Counter(sum(colour_match(colsA[i], colsB[s[i]]) for i in range(n)) for s in itertools.permutations(range(n)))
    return {a: Fraction(v, math.factorial(n)) for a, v in sorted(c.items())}
def P_(x): return ((x,), ())
X, Y, Z, PK = P_('X'), P_('Y'), P_('Z'), P_('PK')
def run_ceiling_fixture():
    out, ok = [], True
    hand = [('K049 KH0362-like: A 11X+1Y, B 6X+6Z -> P(A=6)=1/2', [X] * 11 + [Y], [X] * 6 + [Z] * 6, Fraction(1, 2)),
            ('4 distinct shared: P(A=4)=1/24', [X, Y, Z, P_('W')], [X, Y, Z, P_('W')], Fraction(1, 24)),
            ('A 2X+2Y vs B 2X+2Y: P(A=4)=4/24', [X, X, Y, Y], [X, X, Y, Y], Fraction(1, 6)),
            ('K088 reduction: A 4 rare / 83 PK, B 1 rare / 86 PK -> 4/87', [X] * 4 + [PK] * 83, [X] + [PK] * 86, Fraction(4, 87)),
            ('K088 reduction 3/630: n 36, 3 / 2', [X] * 3 + [PK] * 33, [X] * 2 + [PK] * 34, Fraction(3, 630)),
            ('all PK: A identically 0 -> P(A=0)=1', [PK] * 5, [PK] * 5, Fraction(1)),
            ('monochrome shared: P(A=n)=1', [X] * 6, [X] * 6, Fraction(1))]
    for name, a, b, want in hand:
        d = exact_null(a, b); got = d[max(d)]
        out.append(dict(case=name, expected=str(want), got=str(got))); ok &= got == want
    d = exact_null([X, Y, Z, P_('W')], [X, Y, Z, P_('W')]); ok &= d[0] == Fraction(9, 24)
    out.append(dict(case='4 distinct: P(A=0) = derangements 9/24', expected='9/24', got=str(d[0])))
    rg = np.random.default_rng(0)  # fixture-only rng, not a registered seed (no data)
    pal = [X, Y, Z, PK, (('X', 'Y'), (':',)), (('X', 'Y'), ('-',))]
    for t in range(40):
        n = int(rg.integers(1, 8)); a = [pal[int(i)] for i in rg.integers(0, len(pal), n)]; b = [pal[int(i)] for i in rg.integers(0, len(pal), n)]
        e, bf = exact_null(a, b), brute(a, b); g = e == bf; ok &= g
        if not g: out.append(dict(case=f'brute {t}', a=str(a), b=str(b), exact=str(e), brute=str(bf)))
    out.append(dict(case='40 random cases n<=7 equal brute-force enumeration', passed=bool(ok)))
    return bool(ok), out

# ---------------- KFG data layer (K076 lines 43-106, verbatim; COL built for every khipu, not only grouped) ----------------
# ---------------- G0 hashes, fixtures ----------------
for p, want in ((OKR_DB, OKR_SHA), (KFG_DB, KFG_SHA)):
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if h != want: stop(f'G0 hash mismatch {p} {h}')
res['G0'] = 'pass'
ok, fx = K49.run_fixture(); res['k046_fixture_passed'] = ok; res['k046_fixture_cases'] = len(fx)
if not ok: stop('K046/K049 match-function fixture failed')
ok, cfx = run_ceiling_fixture(); res['ceiling_fixture_passed'] = ok; res['ceiling_fixture'] = cfx
if not ok: stop('ceiling fixture failed')
print('G0 + fixtures 14/14 + ceiling fixture pass', round(time.time() - T0, 1), flush=True)
# ---------------- KFG data layer (K076 lines 43-106, verbatim) ----------------
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
# K049-shaped sequence store on KFG (K073 sequences: all pendants in pendant order; cluster = CordGroups index or None)
COL = {(kh, i): sorted(pend[kh])[i][2] for kh in pend for i in range(len(pend[kh]))}
meta = {r[0]: dict(okr=r[0], inv=r[1] or '', museum=r[2] or '', mnum=r[3] or '', provenance=r[4] or '', region=r[5] or '')
        for r in kc.execute('select name, aliases, museum_name, museum_number, provenance, region from khipu')}
def gidx(kh, i):
    if kh not in groups: return None
    return next(g for g, (a, b) in enumerate(groups[kh]) if a <= i < b)
SK = dict(seq={kh: [dict(cid=(kh, i), value=x, cluster=gidx(kh, i), ordinal=i) for i, (_, x, _) in enumerate(sorted(pend[kh]))] for kh in pend},
          meta=meta, byokr={kh: kh for kh in pend})
res['kfg_data'] = dict(n_with_pendants=len(pend), n_grouped=len(groups), G1_bad=len(g1_bad), n_R5_masked=NR5[0])
def kfg_colour(cid):
    c, why = parse(COL[cid]); return c, why
# ---------------- values-only K010 consistency on both sources (no colour) ----------------
co = sqlite3.connect(f"file:{os.path.realpath(OKR_DB)}?mode=ro", uri=True); SO = K49.build_sequences(co)
def consistency(S, src):
    built, cons = {}, {}
    for spec in PAIRS:
        A = locate_side(S, spec['a'], spec['block'], spec['block_len']); B = locate_side(S, spec['b'], spec['block'], spec['block_len'])
        ok_ = bool(A['ok'] and B['ok'])
        pa, pb = public_side(A), public_side(B)
        cons[spec['key']] = dict(ok=ok_, a={k: pa.get(k) for k in ('khid', 'start', 'n_hits', 'block_len', 'n_clusters', 'n_pendants', 'reason')},
                                 b={k: pb.get(k) for k in ('khid', 'start', 'n_hits', 'block_len', 'n_clusters', 'n_pendants', 'reason')})
        if ok_: built[spec['key']] = (spec, A, B, build_units(A, B))
    return built, cons
built_o, cons_o = consistency(SO, 'OKR'); built_k, cons_k = consistency(SK, 'KFG')
PUBSTART = {k: (P['a']['start'], P['b']['start']) for k, P in PUB['pairs'].items()}
res['A0_values'] = dict(pass_=all(cons_o[k]['ok'] and (cons_o[k]['a']['start'], cons_o[k]['b']['start']) == PUBSTART[k] for k in PUBSTART))
res['consistency_okr'] = cons_o; res['consistency_kfg'] = cons_k
print('A0 values', res['A0_values'], {k: (v['a']['start'], v['b']['start']) for k, v in cons_o.items()}, flush=True)
print('KFG values', {k: (v['ok'], v['a']['start'], v['b']['start'], v['a']['n_clusters'], v['b']['n_clusters'], v['a']['reason'], v['b']['reason']) for k, v in cons_k.items()}, flush=True)
if not res['A0_values']['pass_']: stop('A0: K049 sequence builder does not reproduce K010 starts on OKR')
if MODE == 'values': print(json.dumps(dict(okr=cons_o, kfg=cons_k), indent=1, default=list)); sys.exit(0)
if MODE != 'run': sys.exit(__doc__)
if SMOKE:  # colours shuffled within each khipu (only smoke ever sees this)
    sr = np.random.default_rng(0)
    for kh in pend:
        ks = [(kh, i) for i in range(len(pend[kh]))]; perm = sr.permutation(len(ks)); vals = [COL[k] for k in ks]
        for k_, j in zip(ks, perm): COL[k_] = vals[j]

# ---------------- K049 per-pair loop (k049 lines 359-480, verbatim) ----------------
def pair_loop(built, colour, R, NCAL, NPOW, RP, NCURVE, rng, out, t0, ckpt):
    for key, (spec, A, B, units) in built.items():
        P = out["pairs"].setdefault(key, {})
        P["a"] = public_side(A)
        P["b"] = public_side(B)
        P["published_block"] = spec["block"]
        P["published_block_len"] = spec["block_len"]
        P["census"] = dict(a=dict(A["meta"]), b=dict(B["meta"]))
        us, excl = colour_units(colour, units)
        n = len(us)
        P.update(aligned_units=len(units), coloured_units=n, excluded_units=dict(excl))

        # copy-all on real structure (creates shared codes; independent of real inventories)
        if n >= 1:
            cp = [{**u, "colB": u["colA"]} for u in us]
            Mc = match_matrix(cp)
            obs_c = int(np.trace(Mc))
            want = sum("PK" not in u["colA"][0] for u in us)
            pc = pval(obs_c, null_bank(Mc, 2000, rng["copyall"]))
            P["positive_control_copy_all"] = dict(
                A=obs_c, expected=want, p=pc,
                passed=bool(obs_c == want and pc < ALPHA))
        else:
            P["positive_control_copy_all"] = dict(
                A=0, expected=0, p=None, passed=False, note="no coloured units")

        deg = degeneracy_reason(us)
        P["degeneracy_reason"] = deg
        P["colour_counts_A"] = dict(Counter(colkey(u["colA"]) for u in us).most_common())
        P["colour_counts_B"] = dict(Counter(colkey(u["colB"]) for u in us).most_common())

        if deg:
            obs = int(sum(colour_match(u["colA"], u["colB"]) for u in us)) if us else 0
            P.update(observed_A=obs, rate=(obs / n if n else None),
                     null_mean=obs if n else None, p=None,
                     verdict="DEGENERATE",
                     note=("no colour variation to shuffle toward extra matches "
                           f"({deg}); A is fixed by the inventories and N1 has max = min"))
            print(f"{key} n={n} A={obs} DEGENERATE ({deg})", flush=True)
            json.dump(out, open(ckpt, "w"), indent=1, default=list)
            continue

        t1 = time.time()
        M = match_matrix(us)
        bank = null_bank(M, R, rng["null"])
        cal = []
        for _ in range(NCAL):
            perm = rng["calib"].permutation(n)
            cal.append(pval(int(M[np.arange(n), perm].sum()), bank))
        fpr_perm = float(np.mean(np.array(cal) < ALPHA))
        lo = math.ceil(0.1 * n)
        shifts = [k for k in range(1, n) if min(k, n - k) >= lo]
        sp = [pval(int(M[np.arange(n), (np.arange(n) + k) % n].sum()), bank) for k in shifts]
        fpr_shift = float(np.mean(np.array(sp) < ALPHA)) if sp else None
        pw, pmed, kpl = plant_power(us, F_PLANT, NPOW, RP, rng["power"])
        curve = {}
        for f in F_CURVE:
            if time.time() - t0 > WALL * 0.8:
                curve[str(f)] = "cut_by_wall"
                continue
            curve[str(f)] = plant_power(us, f, NCURVE, RP, rng["power"])[0]
        print(f"{key} n={n} fpr_perm={fpr_perm:.4f} fpr_shift={fpr_shift} "
              f"power={pw:.3f} ({time.time() - t1:.1f}s)", flush=True)

        obs = int(np.trace(M))
        p = pval(obs, bank)
        blocks, uniq = n2_blocks(us)
        if blocks is None:
            n2 = dict(applicable=False, n_keys=len(uniq),
                      note="block is a single (clusterA, clusterB) key; N2 identical to N1")
        else:
            bank_n2 = null_bank(M, R, rng["n2_sens"], blocks=blocks)
            n2 = dict(applicable=True, n_keys=len(uniq),
                      key_sizes=[len(b) for b in blocks],
                      null_mean=float(bank_n2.mean()), p=pval(obs, bank_n2),
                      note="descriptive, not a verdict")

        P.update(
            observed_A=obs, rate=obs / n if n else None,
            null_mean=float(bank.mean()), null_sd=float(bank.std()),
            null_q95=float(np.quantile(bank, 0.95)), null_max=int(bank.max()),
            null_min=int(bank.min()), p=p,
            calibration=dict(fpr_perm=fpr_perm, n=NCAL, shift_offsets=len(shifts),
                             min_offset=lo, fpr_shift=fpr_shift,
                             shift_p_min=(min(sp) if sp else None)),
            power=dict(f=F_PLANT, k_planted=kpl, power=pw, median_p=pmed,
                       n=NPOW, curve=curve, curve_n=NCURVE),
            N2_within_group=n2,
        )
        copy_ok = P["positive_control_copy_all"]["passed"]
        if (not copy_ok) or fpr_perm > FPR_GATE or (fpr_shift is not None and fpr_shift > FPR_GATE):
            v = "TOOL EXCLUDED"
        elif p < ALPHA:
            v = "SUPPORTED"
        elif pw < POWER_BAR:
            v = "NOT TESTABLE"
        else:
            v = "NOT SUPPORTED"
        P["verdict"] = v

        sens = {}
        Mby = match_matrix(us, True)
        ob = int(np.trace(Mby))
        sens["BY_eq_YB"] = dict(A=ob, p=pval(ob, null_bank(Mby, R, rng["n2_sens"])))
        unz = [u for u in us if u["value"] != 0]
        if unz and len(unz) != n:
            Mz = match_matrix(unz)
            oz = int(np.trace(Mz))
            sens["nonzero_value_units"] = dict(
                n=len(unz), A=oz, p=pval(oz, null_bank(Mz, R, rng["n2_sens"])))
        elif unz:
            sens["nonzero_value_units"] = dict(
                n=len(unz), A=obs, p=p, note="identical to primary (published block has no zeros)")
        P["sensitivities"] = sens
        P["matching_units"] = [
            dict(pos=u["pos"], value=u["value"],
                 startA=u["startA"], startB=u["startB"],
                 colour=colour_pretty(u["colA"]))
            for u in us if colour_match(u["colA"], u["colB"])
        ]
        print(f"{key} A={obs}/{n} null_mean={bank.mean():.2f} p={p:.5f} -> {v} "
              f"({time.time() - t1:.1f}s)", flush=True)
        json.dump(out, open(ckpt, "w"), indent=1, default=list)


# ---------------- runs ----------------
def run_source(built, colour, seeds, tag):
    R = 200 if SMOKE else 10000; NCAL = 50 if SMOKE else 1000; NPOW = 10 if SMOKE else 200; RP = 200 if SMOKE else 2000; NCURVE = 10 if SMOKE else 100
    rng = {k: np.random.default_rng(v) for k, v in seeds.items()}
    out = dict(source=tag, seeds=seeds, R=R, n_calibration=NCAL, n_power=NPOW, R_power=RP, pairs={})
    pair_loop(built, colour, R, NCAL, NPOW, RP, NCURVE, rng, out, T0, os.path.join(AN, f'k089_checkpoint_{tag}.json'))
    return out
def add_ceiling(out):
    for key, P in out['pairs'].items():
        if P.get('verdict') == 'DEGENERATE': P['ceiling'] = dict(applicable=False, reason='degenerate'); continue
        P['ceiling'] = ceiling(P['_colsA'], P['_colsB'], P['observed_A'])
def track_b(P):
    if P.get('verdict') == 'DEGENERATE': return 'DEGENERATE'
    if P['ceiling']['fires']: return 'NOT TESTABLE (margin ceiling)'
    return P['verdict']
READ = ('SUPPORTED', 'NOT SUPPORTED')
def mapping(kv, ov):
    if kv in READ and ov in READ: return 'REPLICATED' if kv == ov else 'CHANGED (correction)'
    if kv in READ: return 'CHANGED (now readable)'
    if ov in READ: return 'CHANGED (correction)'
    return 'REPLICATED (not readable on either)'
# A0: the K049 loop on the OKR with K049's own seeds must reproduce k049_results.json exactly
co_colour = K49.load_colour(co)
def run_with_capture(built, colour, seeds, tag):
    # colour tuples for the exact null are recomputed after the loop (deterministic, no rng)
    out = run_source(built, colour, seeds, tag)
    for key, (spec, A, B, units) in built.items():
        us, _ = colour_units(colour, units); out['pairs'][key]['_colsA'] = [u['colA'] for u in us]; out['pairs'][key]['_colsB'] = [u['colB'] for u in us]
    add_ceiling(out)
    for P in out['pairs'].values(): P.pop('_colsA'); P.pop('_colsB')
    return out
okr = run_with_capture(built_o, co_colour, SEEDS_K049, 'okr')
FIELDS = ['coloured_units', 'observed_A', 'verdict', 'degeneracy_reason', 'p', 'null_mean', 'colour_counts_A', 'colour_counts_B']
SUB = dict(positive_control_copy_all=['A', 'p', 'passed'], calibration=['fpr_perm', 'fpr_shift'], power=['power', 'curve'], N2_within_group=['p'])
a0 = {}
for k, Pp in PUB['pairs'].items():
    Po = okr['pairs'][k]; bad = [f for f in FIELDS if Po.get(f) != Pp.get(f)]
    for s, fs in SUB.items():
        for f in fs:
            if (Po.get(s) or {}).get(f) != (Pp.get(s) or {}).get(f): bad.append(f'{s}.{f}')
    a0[k] = bad
res['A0'] = dict(pass_=(all(not v for v in a0.values()) or SMOKE), mismatches=a0, note='smoke uses small R so only exact in the full run' if SMOKE else '')
print('A0 OKR rebuild', res['A0'], flush=True)
if not res['A0']['pass_']: res['okr'] = okr; stop('A0: K049 loop on OKR does not reproduce k049_results.json')
for k, P in okr['pairs'].items(): P['track_B'] = track_b(P); P['k049_published'] = PUB['pairs'][k]['verdict']
res['okr'] = okr
res['k049_corrections'] = {k: dict(published=P['k049_published'], with_ceiling=P['track_B'], ceiling=P['ceiling'])
                           for k, P in okr['pairs'].items() if P['track_B'] != P['k049_published']}
dump()
# KFG
kfg = run_with_capture(built_k, kfg_colour, SEEDS, 'kfg')
for spec in PAIRS:
    k = spec['key']
    if k not in kfg['pairs']:
        kfg['pairs'][k] = dict(verdict='NOT TESTABLE (data)', track_B='NOT TESTABLE (data)', consistency=cons_k[k],
                               reason='KFG merged KH0483 into KH0140 (K068/K073)' if k == 'KH0140/KH0483' else 'published K010 block not recovered on KFG')
    else: kfg['pairs'][k]['track_B'] = track_b(kfg['pairs'][k])
res['kfg'] = kfg
dec = {}
for spec in PAIRS:
    k = spec['key']; kb, ob = kfg['pairs'][k]['track_B'], okr['pairs'][k]['track_B']; ka, oa = kfg['pairs'][k]['verdict'], PUB['pairs'][k]['verdict']
    dec[k] = dict(okr_k049=oa, okr_with_ceiling=ob, kfg_frozen=ka, kfg_with_ceiling=kb,
                  track_A=('NOT TESTABLE (data)' if ka == 'NOT TESTABLE (data)' else mapping(ka, oa)),
                  track_B=('NOT TESTABLE (data)' if kb == 'NOT TESTABLE (data)' else mapping(kb, ob)))
res['decision'] = dec
res['headline'] = 'READABLE' if any(kfg['pairs'][k]['track_B'] in READ for k in kfg['pairs']) else 'NOT READABLE'
# Holm (m = 5, the KH0140 slot still spent) on KFG Monte Carlo p, descriptive
ps = sorted((P['p'], k) for k, P in kfg['pairs'].items() if P.get('p') is not None)
holm, stopped = {}, False
for i, (p, k) in enumerate(ps):
    thr = 0.05 / (5 - i); rej = (not stopped) and p < thr; stopped |= not rej; holm[k] = dict(p=p, threshold=thr, reject=rej)
res['holm_kfg_descriptive'] = holm
dump()
for k, d in dec.items(): print(k, d, flush=True)
print('headline', res['headline'], 'K049 corrections', {k: (v['published'], v['with_ceiling']) for k, v in res['k049_corrections'].items()}, 'sec', res['sec'])
