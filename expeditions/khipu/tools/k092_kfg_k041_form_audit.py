#!/usr/bin/env python3
"""K092 - KFG re-audit (README line 9): K041's form-audit of the line-2 leftover whole-group-sum hits
(H1 layout concentration pi, H2 singleton-total share q, H3 side balance r; Bonferroni x3) re-run on
Khipu Field Guide data. Pre-registered in case-file/K092-kfg-k041-form-audit.md.
Statistic, null, calibration, power plant and decision rule copied from tools/k041_leftover_form_audit.py;
KFG pendants/groups exactly as tools/k072_kfg_line2_corpus.py (K071 loader, hash-checked xlsx CordGroups).
Arm A0 re-runs K041 verbatim on the OKR (seeds 4141-4143) and must reproduce analysis/k041_results.json exactly.
Usage: python3 tools/k092_kfg_k041_form_audit.py data/khipu.db [--smoke | --a0only]
--smoke: R 200 / N 10, KFG values shuffled (plumbing only); A0 mismatch not fatal. --a0only: full A0 on OKR, then exit (no KFG statistic).
Seeds 6490 (KFG nulls), 6491 (KFG calibration), 6492 (KFG power). Next free 6493."""
import sqlite3, json, sys, re, glob, zipfile, hashlib, time
import numpy as np, xml.etree.ElementTree as ET
from collections import Counter, defaultdict
T0 = time.time(); KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
OKR_DB = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'data/khipu.db'
SMOKE = '--smoke' in sys.argv; A0ONLY = '--a0only' in sys.argv
OUT = 'analysis/k092_smoke.json' if SMOKE else '/workspace/k092/k092_a0only.json' if A0ONLY else 'analysis/k092_results.json'
CKPT = 'analysis/k092_smoke_checkpoint.json' if SMOKE else 'analysis/k092_checkpoint.json'
OKR_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
DISC = ('KH0359', 'KH0405')
R = 200 if SMOKE else 10000; N_CAL = 10 if SMOKE else 200; N_POW = 10 if SMOKE else 200
M_PLANT = 9; ALPHA = 0.05 / 3; GATE = 0.08; POWER_BAR = 0.5; MIN_N = 1 if SMOKE else 30; WALL = 520
SEEDS_A0 = dict(nulls=4141, calib=4142, power=4143); SEEDS = dict(nulls=6490, calib=6491, power=6492); NEXT_FREE = 6493
K041 = json.load(open('analysis/k041_results.json'))
res = dict(design=dict(seeds=SEEDS, seeds_A0=SEEDS_A0, next_free_seed=NEXT_FREE, R=R, N_cal=N_CAL, N_pow=N_POW,
                       m=M_PLANT, alpha=ALPHA, gate=GATE, power_bar=POWER_BAR, smoke=SMOKE, wall_per_arm=WALL))
def dump():
    res['secs'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1, default=str)
def stop(reason):
    res['decision'] = dict(excluded=True, reason=reason); dump(); print('EXCLUDED:', reason, flush=True); sys.exit(0)

# ---------------- K041 engine (verbatim logic) ----------------
def groups_of(cl):
    g, last = [], object()
    for i, x in enumerate(cl):
        if x != last: g.append([i, i + 1]); last = x
        else: g[-1][1] = i + 1
    return [(s, e) for s, e in g]
def prep(cl, n):
    pairs = []
    for s, e in groups_of(cl):
        if e - s < 2: continue
        if s - 1 >= 0: pairs.append((s - 1, s, e))
        if e < n: pairs.append((e, s, e))
    return np.array(pairs, np.int64).reshape(-1, 3)
def pair_forms(cl, pr):
    csz = np.zeros(len(cl), np.int64)
    for s, e in groups_of(cl): csz[s:e] = e - s
    return [('L' if int(i) < int(s) else 'R', int(e - s), bool(csz[int(i)] == 1)) for i, s, e in pr]
def hit_mask(V, pr):
    if len(pr) == 0: return np.zeros((V.shape[0], 0), bool)
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    Z = np.zeros((B, n + 1), np.int64); Z[:, 1:] = np.cumsum(V > 0, 1)
    i, s, e = pr[:, 0], pr[:, 1], pr[:, 2]; vi = V[:, i]
    return (vi >= 10) & (vi == P[:, e] - P[:, s]) & ((Z[:, e] - Z[:, s]) >= 2)
def perm(v, B, rng): return v[np.argsort(rng.random((B, len(v))), 1)]
def p_ge(o, nl): nl = np.asarray(nl, float); return float((1 + (nl >= o).sum()) / (1 + len(nl)))
def p_two(o, nl):
    nl = np.asarray(nl, float); pu = (1 + (nl >= o).sum()) / (1 + len(nl)); pl = (1 + (nl <= o).sum()) / (1 + len(nl))
    return float(min(1.0, 2.0 * min(pu, pl)))
def summarize(fl):
    n = len(fl)
    if n == 0: return dict(n=0, modal_count=0, modal_share=0.0, modal_key=None, q_sing=0.0, r_left=0.5, n_left=0, n_sing=0)
    c = Counter((s, g) for s, g, _ in fl); mk, mc = c.most_common(1)[0]
    ns = int(sum(1 for f in fl if f[2])); nl = int(sum(1 for f in fl if f[0] == 'L'))
    return dict(n=n, modal_count=int(mc), modal_share=float(mc / n), modal_key=[mk[0], int(mk[1])], q_sing=float(ns / n),
                r_left=float(nl / n), n_left=nl, n_sing=ns, layout_counts={f'{s}:{g}': int(v) for (s, g), v in c.most_common()})
def extract_forms(v, e):
    m = hit_mask(v[None], e['pr'])[0]; return [e['forms'][k] for k in range(len(e['forms'])) if m[k]]
def plant_one_pair(x, i, s, e, rng):
    x = x.copy(); blk = x[s:e].copy()
    if (blk > 0).sum() < 2: blk[:2] = np.maximum(blk[:2], rng.integers(1, 30, 2))
    if int(blk.sum()) < 10: blk[0] += 10 - int(blk.sum())
    x[s:e] = blk; x[i] = int(blk.sum()); return x
def capacity(ho, pred):
    n = 0
    for e in ho:
        used = set()
        for k, f in enumerate(e['forms']):
            if not pred(f): continue
            i, s, ee = [int(x) for x in e['pr'][k]]; span = set(range(s, ee)) | {i}
            if used & span: continue
            used |= span; n += 1
    return n
def plant_corpus(ho, rng, m, pred):
    xs = {e['kid']: rng.permutation(e['v']) for e in ho}
    cands = [(e['kid'], k, *[int(x) for x in e['pr'][k]]) for e in ho for k, f in enumerate(e['forms']) if pred(f)]
    if not cands: return xs, 0
    order = rng.permutation(len(cands)); used = defaultdict(set); planted = 0
    for idx in order:
        kid, _k, i, s, ee = cands[idx]; span = set(range(s, ee)) | {i}
        if used[kid] & span: continue
        xs[kid] = plant_one_pair(xs[kid], i, s, ee, rng); used[kid] |= span; planted += 1
        if planted >= m: break
    return xs, planted
def forms_from_xs(ho, xs):
    out = []
    for e in ho: out.extend(extract_forms(xs[e['kid']], e))
    return out
def distinct(ho, xs):  # Kryptos-style D2 collapse: distinct total pendants, singleton share (descriptive)
    nd = ns = 0
    for e in ho:
        m = hit_mask(xs[e['kid']][None], e['pr'])[0]; ii = {int(e['pr'][k, 0]) for k in np.flatnonzero(m)}
        nd += len(ii); ns += sum(1 for i in ii if e['csz'][i] == 1)
    return nd, ns

def audit(ho, seeds, label):
    t0 = time.time(); out = dict()
    # observed catalogue
    rows = []
    for e in ho:
        m = hit_mask(e['v'][None], e['pr'])[0]; byi = defaultdict(list)
        for k in np.flatnonzero(m): byi[int(e['pr'][k, 0])].append(int(k))
        for k in np.flatnonzero(m):
            i, s, ee = [int(x) for x in e['pr'][k]]; side, gl, sg = e['forms'][k]
            rows.append(dict(khipu=e['name'], in_okr=e.get('okr_shared'), pendant_index=i, value=int(e['v'][i]), side=side,
                             group_len=gl, singleton_total=sg, group_start=s, group_end=ee, both_sides=len(byi[i]) > 1))
    obs = summarize([(r['side'], r['group_len'], r['singleton_total']) for r in rows])
    obs['G_distinct'] = len({(r['khipu'], r['pendant_index']) for r in rows}); obs['n_both'] = len({(r['khipu'], r['pendant_index']) for r in rows if r['both_sides']})
    nd, ns = distinct(ho, {e['kid']: e['v'] for e in ho}); obs['D_distinct'] = dict(n=nd, n_sing=ns, q_d=ns / nd if nd else 0.0)
    out['observed'] = obs; out['catalogue'] = rows
    print(label, 'observed', {k: v for k, v in obs.items() if k != 'layout_counts'}, flush=True)
    # nulls
    rng = np.random.default_rng(seeds['nulls']); ctr = [Counter() for _ in range(R)]
    nn = np.zeros(R, np.int64); nsg = np.zeros(R, np.int64); nlf = np.zeros(R, np.int64); nG = np.zeros(R, np.int64)
    dn = np.zeros(R, np.int64); ds = np.zeros(R, np.int64)
    for j, e in enumerate(ho):
        if time.time() - t0 > WALL: out['capped'] = 'nulls'; return out
        V = perm(e['v'], R, rng); m = hit_mask(V, e['pr'])
        if m.size:
            H = np.zeros((R, len(e['v'])), bool)
            for k in range(len(e['pr'])): H[:, int(e['pr'][k, 0])] |= m[:, k]
            nG += H.sum(1); dn += H.sum(1); ds += H[:, e['csz'] == 1].sum(1)
        for k, (side, gl, sg) in enumerate(e['forms']):
            reps = np.flatnonzero(m[:, k])
            if len(reps) == 0: continue
            for r in reps: ctr[r][(side, gl)] += 1
            nn[reps] += 1
            if sg: nsg[reps] += 1
            if side == 'L': nlf[reps] += 1
        if (j + 1) % 20 == 0 or j + 1 == len(ho):
            json.dump(dict(arm=label, reached=j + 1, n=len(ho), secs=round(time.time() - t0, 1)), open(CKPT, 'w'))
    npi = np.array([(max(c.values()) / n) if n else 0.0 for c, n in zip(ctr, nn)])
    nq = np.array([(s / n) if n else 0.0 for s, n in zip(nsg, nn)]); nr = np.array([(L / n) if n else 0.5 for L, n in zip(nlf, nn)])
    nqd = np.array([(s / n) if n else 0.0 for s, n in zip(ds, dn)])
    p1, p2, p3 = p_ge(obs['modal_share'], npi), p_ge(obs['q_sing'], nq), p_two(obs['r_left'], nr)
    out['null'] = dict(pi_mean=float(npi.mean()), pi_sd=float(npi.std()), q_mean=float(nq.mean()), q_sd=float(nq.std()),
                       r_mean=float(nr.mean()), r_sd=float(nr.std()), G_mean=float(nG.mean()), n_pairs_mean=float(nn.mean()),
                       q_d_mean=float(nqd.mean()), q_d_sd=float(nqd.std()),
                       rank_q=int((nq >= obs['q_sing']).sum()), rank_pi=int((npi >= obs['modal_share']).sum()))
    out['p'] = dict(p1=p1, p2=p2, p3=p3, p_q_d_descriptive=p_ge(obs['D_distinct']['q_d'], nqd))
    print(label, 'p', out['p'], out['null'], round(time.time() - t0, 1), flush=True)
    sc = lambda st: dict(p1=p_ge(st['modal_share'], npi), p2=p_ge(st['q_sing'], nq), p3=p_two(st['r_left'], nr))
    # calibration
    cal = dict(capped=False, n=0); rc = np.random.default_rng(seeds['calib']); fl = dict(H1=0, H2=0, H3=0, any=0)
    for j in range(N_CAL):
        if time.time() - t0 > WALL: cal['capped'] = True; break
        xs = {e['kid']: rc.permutation(e['v']) for e in ho}; s = sc(summarize(forms_from_xs(ho, xs)))
        f1, f2, f3 = s['p1'] <= ALPHA, s['p2'] <= ALPHA, s['p3'] <= ALPHA
        fl['H1'] += int(f1); fl['H2'] += int(f2); fl['H3'] += int(f3); fl['any'] += int(f1 or f2 or f3); cal['n'] = j + 1
    if cal['n']: cal.update({f'fpr_{h}': fl[h] / cal['n'] for h in ('H1', 'H2', 'H3', 'any')})
    out['calibration'] = cal; print(label, 'calib', cal, round(time.time() - t0, 1), flush=True)
    # power
    kc = {}
    for e in ho:
        ub = defaultdict(set)
        for k, (side, gl, _) in enumerate(e['forms']):
            key = (side, gl); i, s, ee = [int(x) for x in e['pr'][k]]; span = frozenset(list(range(s, ee)) + [i])
            if ub[key] & span: continue
            ub[key] |= span; kc[key] = kc.get(key, 0) + 1
    h1k = max(kc.items(), key=lambda kv: (kv[1], kv[0][1], kv[0][0]))[0] if kc else None
    rp = np.random.default_rng(seeds['power'])
    def power_for(pred, lab):
        rec = dict(n=0, hits=0, skipped=0, capped=False, rate=None)
        if time.time() - t0 > WALL: rec['capped'] = True; return rec
        hits = ok = sk = att = 0
        while ok < N_POW and att < N_POW * 5:
            if time.time() - t0 > WALL: rec['capped'] = True; break
            att += 1; xs, got = plant_corpus(ho, rp, M_PLANT, pred)
            if got < M_PLANT: sk += 1; continue
            ok += 1; hits += sc(summarize(forms_from_xs(ho, xs)))[lab] <= ALPHA
        rec.update(n=ok, hits=hits, skipped=sk, rate=hits / ok if ok else None, attempts=att); return rec
    pw = dict(H1=power_for(lambda f: h1k is not None and (f[0], f[1]) == h1k, 'p1'))
    pw['H1'].update(plant_key=[h1k[0], int(h1k[1])] if h1k else None, capacity=int(kc.get(h1k, 0)) if h1k else 0)
    pw['H2'] = power_for(lambda f: f[2], 'p2'); pw['H2']['capacity'] = capacity(ho, lambda f: f[2])
    pw['H3'] = power_for(lambda f: f[0] == 'L', 'p3'); pw['H3']['capacity'] = capacity(ho, lambda f: f[0] == 'L')
    out['power'] = pw; print(label, 'power', {h: (v['rate'], v['n']) for h, v in pw.items()}, round(time.time() - t0, 1), flush=True)
    def decide(nm, p, fpr, pr):
        if cal.get('capped') or cal.get('n', 0) < N_CAL:
            return 'excluded' if fpr is not None and fpr > GATE else 'not testable'
        if fpr is not None and fpr > GATE: return 'excluded'
        if pr.get('capped') or (pr.get('n') or 0) < MIN_N: return 'not testable'
        if (pr.get('rate') or 0) < POWER_BAR: return 'not testable'
        return 'supported' if p <= ALPHA else 'not supported'
    out['verdicts'] = {h: decide(h, out['p'][f'p{j}'], cal.get(f'fpr_{h}'), pw[h]) for j, h in ((1, 'H1'), (2, 'H2'), (3, 'H3'))}
    ps = sorted((out['p'][f'p{j}'], h) for j, h in ((1, 'H1'), (2, 'H2'), (3, 'H3'))); holm = {}; go = True
    for r_, (p, h) in enumerate(ps):
        go = go and p <= 0.05 / (3 - r_); holm[h] = bool(go)
    out['holm_reject_info'] = holm; out['secs'] = round(time.time() - t0, 1)
    return out

# ---------------- OKR (arm A0: K041 verbatim) ----------------
h = hashlib.sha256(open(OKR_DB, 'rb').read()).hexdigest()
if h != OKR_SHA: stop('OKR hash mismatch ' + h)
c = sqlite3.connect(OKR_DB)
dups = {r[0] for r in c.execute('select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1')}
okrname = {r[0]: r[1] or '' for r in c.execute('select KHIPU_ID, OKR_NUM from khipu_main')}
okr_set = {v for v in okrname.values() if v}
val = defaultdict(int)
for cid, v in c.execute('select CORD_ID, knot_value_type from knot'):
    if v is not None: val[cid] += int(v)
okr_kh = defaultdict(list)
for kid, cid, cl in c.execute('select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL'):
    if kid in dups: continue
    okr_kh[kid].append((val.get(cid, 0), cl))
def mk(kid, name, v, cl, okr_shared=None):
    pr = prep(cl, len(v)); csz = np.zeros(len(v), np.int64)
    for s, e in groups_of(cl): csz[s:e] = e - s
    return dict(kid=kid, name=name, v=v, cl=cl, pr=pr, forms=pair_forms(cl, pr), csz=csz, okr_shared=okr_shared)
okr_elig = []
for kid, cords in okr_kh.items():
    cl = [x[1] for x in cords]
    if len(groups_of(cl)) < 4: continue
    v = np.array([x[0] for x in cords], np.int64); pr = prep(cl, len(v))
    if len(pr) == 0 or (v >= 10).sum() == 0: continue
    okr_elig.append(mk(kid, okrname[kid], v, cl, True))
okr_ho = [e for e in okr_elig if e['name'] not in DISC]
res['A0_counts'] = dict(n_eligible=len(okr_elig), n_holdout=len(okr_ho))
if (len(okr_elig), len(okr_ho)) != (369, 367): stop('A0 OKR counts differ from K041 369/367')
A0 = audit(okr_ho, SEEDS_A0, 'A0')
pub = dict(n=K041['observed']['n'], modal_share=K041['observed']['modal_share'], q_sing=K041['observed']['q_sing'],
           r_left=K041['observed']['r_left'], p1=K041['decision']['H1']['p'], p2=K041['decision']['H2']['p'], p3=K041['decision']['H3']['p'],
           fpr=[K041['calibration'][f'fpr_H{j}'] for j in (1, 2, 3)], power=[K041['power'][f'H{j}']['rate'] for j in (1, 2, 3)],
           verdicts=[K041['decision'][f'H{j}']['verdict'] for j in (1, 2, 3)])
got = dict(n=A0['observed']['n'], modal_share=A0['observed']['modal_share'], q_sing=A0['observed']['q_sing'], r_left=A0['observed']['r_left'],
           p1=A0['p']['p1'], p2=A0['p']['p2'], p3=A0['p']['p3'], fpr=[A0['calibration'].get(f'fpr_H{j}') for j in (1, 2, 3)],
           power=[A0['power'][f'H{j}']['rate'] for j in (1, 2, 3)], verdicts=[A0['verdicts'][f'H{j}'] for j in (1, 2, 3)])
A0.pop('catalogue', None)
res['A0'] = dict(published=pub, rebuilt=got, exact=(pub == got), detail=A0); dump()
print('A0 exact', pub == got, flush=True)
if pub != got and not SMOKE: stop('A0: K041 not rebuilt exactly on OKR')
if A0ONLY: print('A0-only run done', res['secs']); sys.exit(0)

# ---------------- KFG (K071/K072 loader verbatim, pendant values + CordGroups) ----------------
k = sqlite3.connect(KFG_DB); sha = dict(k.execute('select name, sha256 from khipu'))
PEN = re.compile(r'^p(\d+)$'); pend = defaultdict(list)
for kh, nm, v in k.execute('select khipu, cord_name, value from cord order by khipu, idx'):
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
    if n and [p for p, _ in L] == list(range(1, n + 1)) and [p for a, b in spans for p in range(a, b + 1)] == list(range(1, n + 1)):
        groups[kh] = [(a - 1, b) for a, b in spans]
    elif n: g1_bad.append(kh)
gates = dict(G0_hash_mismatch=len(g0_bad), G1_partition_rate=len(groups) / max(1, len(groups) + len(g1_bad)))
gates['pass_data'] = gates['G0_hash_mismatch'] == 0 and gates['G1_partition_rate'] >= 0.95
res['gates'] = gates; print('gates', gates, flush=True)
if not gates['pass_data']: stop('KFG data gate G0/G1 failed')
SMOKE_RNG = np.random.default_rng(0); elig = []
for kh in sorted(groups):
    gs = groups[kh]
    if len(gs) < 4: continue
    v = np.array([x for _, x in pend[kh]], np.int64)
    cl = np.repeat(np.arange(len(gs)), [b - a for a, b in gs]).tolist(); pr = prep(cl, len(v))
    if SMOKE: v = SMOKE_RNG.permutation(v)  # smoke = plumbing on shuffled KFG values only
    if len(pr) == 0 or (v >= 10).sum() == 0: continue
    elig.append(mk(kh, kh, v, cl, kh in okr_set))
ho = [e for e in elig if e['name'] not in DISC]
res['data'] = dict(n_eligible=len(elig), n_holdout=len(ho), n_holdout_okr_shared=sum(e['okr_shared'] for e in ho),
                   n_holdout_kfg_only=sum(not e['okr_shared'] for e in ho), discovery_present=all(any(e['name'] == d for e in elig) for d in DISC))
print('data', res['data'], flush=True)
if not res['data']['discovery_present'] or (not SMOKE and (len(elig), len(ho)) != (428, 426)): stop('KFG counts differ from K072 428/426')
KF = audit(ho, SEEDS, 'KFG')
if not SMOKE and KF['observed']['G_distinct'] != 71: stop('KFG holdout G differs from K072 (71)')
# descriptive splits (no verdict)
cat = KF['catalogue']
for lab, sel in (('okr_shared', True), ('kfg_only', False)):
    rr = [r for r in cat if r['in_okr'] == sel]
    KF['observed'][lab] = dict(n=len(rr), n_sing=sum(r['singleton_total'] for r in rr), n_left=sum(r['side'] == 'L' for r in rr))
# D-CUR: on khipus whose pendant value vectors are identical on both sources, is each KFG singleton-total pendant also singleton in OKR clusters?
okr_by_name = {okrname[kid]: cords for kid, cords in okr_kh.items() if okrname[kid]}
dc = dict(rows_identical_values=0, kfg_singleton=0, okr_singleton_too=0, okr_not_singleton=0, okr_hit_too=0)
for r in cat:
    o = okr_by_name.get(r['khipu']); e = next(x for x in ho if x['name'] == r['khipu'])
    if not o or [x[0] for x in o] != e['v'].tolist(): continue
    dc['rows_identical_values'] += 1
    ocl = [x[1] for x in o]; ocsz = np.zeros(len(ocl), np.int64)
    for s, ee in groups_of(ocl): ocsz[s:ee] = ee - s
    if r['singleton_total']:
        dc['kfg_singleton'] += 1; dc['okr_singleton_too' if ocsz[r['pendant_index']] == 1 else 'okr_not_singleton'] += 1
    ope = mk(0, '', np.array([x[0] for x in o], np.int64), ocl); om = hit_mask(ope['v'][None], ope['pr'])[0]
    dc['okr_hit_too'] += int(any(int(ope['pr'][kk, 0]) == r['pendant_index'] for kk in np.flatnonzero(om)))
KF['observed']['D_CUR'] = dc
res['KFG'] = KF
PUBV = dict(H1='not testable', H2='supported', H3='not testable')
rep = {}
for hh in ('H1', 'H2', 'H3'):
    kv = KF['verdicts'][hh]
    if kv == 'excluded': rep[hh] = 'EXCLUDED'
    elif kv == 'not testable': rep[hh] = 'REPLICATED (not testable)' if PUBV[hh] == 'not testable' else 'NOT TESTABLE'
    else: rep[hh] = 'REPLICATED' if kv == PUBV[hh] else 'CHANGED'
res['replication'] = rep; dump()
print('verdicts', KF['verdicts'], 'replication', rep, 'secs', res['secs'], flush=True)
