#!/usr/bin/env python3
"""K093 - KFG re-audit step 22 (README line 9): K065's periodicity-preserving (P-unit) confirmation of the K064 cross-provenance
leads, re-run on Khipu Field Guide data. Engine verbatim from tools/k065_periodic_unit_confirm.py (units, P-unit null, collapse,
full-corpus rarity weights, Hamming-1 kernel W = k065_wham1.c, single-step max-W over the cross-provenance family F_x, Holm over
L1-L3 at alpha 0.025, diagnostic KH0309.KH0293, step-down secondary up to 15 steps, S0/G0 fixtures with K065's seeds 6408/6404).
Changed only: the data source (KFG p<n> pendants in pendant order, KFG value, R5 masked to 0 by the K072/K073 KFG port,
eligibility >= 10 non-zero pendants, provenance = KFG field stripped of spaces and double quotes, casefolded; '' / 'unknown' = no
group) and the seeds of the random arms (reference 6493, FPR 6494, plants 6495; next free 6496).
Modes:  a0   - run tools/k065_periodic_unit_confirm.py VERBATIM on OKR (K065_SMOKE=1000,40,100,500 -> /tmp/k065/smoke.json) and
               require every published field of analysis/k065_results.json except 'seconds' to be reproduced exactly.
        smoke- KFG values shuffled within each khipu, R 20 / FPR 4 / plants 4; plumbing only (output in /tmp).
        full - the registered KFG run (requires analysis/k093_a0.json passed).
Usage: python3 tools/k093_kfg_k065_punit.py data/khipu.db {a0|smoke|full}
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sqlite3, json, sys, time, math, os, re, ctypes, hashlib, subprocess, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); MODE = sys.argv[2] if len(sys.argv) > 2 else 'smoke'
OKR_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
KFG_DB = '/workspace/kfg/kfg_20261111.db'; KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'
HERE = os.path.dirname(os.path.abspath(__file__))
def log(*a): print(*a, round(time.time() - t0, 1), flush=True)
if hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest() != OKR_SHA: sys.exit('EXCLUDED: khipu.db hash differs from MANIFEST')
if MODE == 'a0':
    env = dict(os.environ, K065_SMOKE='1000,40,100,500')
    subprocess.run([sys.executable, os.path.join(HERE, 'k065_periodic_unit_confirm.py'), sys.argv[1], 'full'], env=env, check=True,
                   stdout=subprocess.DEVNULL)
    got = json.load(open('/tmp/k065/smoke.json')); want = json.load(open('analysis/k065_results.json'))
    got.pop('seconds', None); want.pop('seconds', None)
    diff = [k for k in want if json.dumps(want[k], sort_keys=True) != json.dumps(got.get(k), sort_keys=True)]
    res = dict(A0_K065_rebuilt=dict(passed=not diff, differing_fields=diff, ref_crit=got['reference']['critical_W_at_alpha'],
               leads={k: dict(W=v['W'], p_adj=v['p_adj'], confirmed=v['confirmed']) for k, v in got['H1']['leads'].items()},
               G1=got['G1']['share'], G2=got['G2']['power']), seconds=round(time.time() - t0, 1))
    json.dump(res, open('analysis/k093_a0.json', 'w'), indent=1); print(json.dumps(res)); sys.exit(0)
if hashlib.sha256(open(KFG_DB, 'rb').read()).hexdigest() != KFG_SHA: sys.exit('EXCLUDED: KFG store hash differs (G-DATA)')
if MODE == 'full' and not json.load(open('analysis/k093_a0.json'))['A0_K065_rebuilt']['passed']: sys.exit('EXCLUDED: A0 failed')
SMOKE = MODE != 'full'; ALPHA = 0.025; EPS = 1e-9
RREF, NFPR, NPL = (20, 4, 4) if SMOKE else (1000, 40, 100)
SEED_REF, SEED_FPR, SEED_PL = 6493, 6494, 6495
OUT = '/tmp/k093/smoke.json' if SMOKE else 'analysis/k093_results.json'
SO = '/tmp/k093/k065_wham1.so'; os.makedirs('/tmp/k093', exist_ok=True)
subprocess.run(['cc', '-O2', '-shared', '-fPIC', '-o', SO, os.path.join(HERE, 'k065_wham1.c')], check=True)
lib = ctypes.CDLL(SO); P64 = np.ctypeslib.ndpointer(np.int64, flags='C_CONTIGUOUS'); PF = np.ctypeslib.ndpointer(np.float64, flags='C_CONTIGUOUS')
lib.wham1.argtypes = [P64, PF, P64, P64, P64, ctypes.c_int64, PF, P64, P64, P64]
# ---------------- KFG data (K071/K072/K073 loader + K072 R5 port) ----------------
def place_(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
kc = sqlite3.connect('file:' + KFG_DB + '?mode=ro', uri=True)
meta = {r[0]: dict(okr=r[0], inv=(r[1] or '').strip(), museum=((r[2] or '').strip() + ' ' + (r[3] or '').strip()).strip())
        for r in kc.execute('select name, aliases, museum_name, museum_number from khipu')}
PEN = re.compile(r'^p(\d+)$'); CLU = re.compile(r'^(\d+)([A-Z]+)\(([-\d.]+),[^)]*\),(-?\d+)$')
def kfg_r5(knots):
    cls = []
    for j, t in enumerate(str(knots or '').split(';')):
        m = CLU.match(t.strip())
        if not m: continue
        typ, pos, v = m.group(2), float(m.group(3)), int(m.group(4))
        if v == 0 or typ[0] not in 'SLE': continue
        cls.append((pos, j, place_(v) if typ[0] == 'S' else 0))
    s = [p for _, _, p in sorted(cls)]
    return len(s) >= 2 and not all(a > b for a, b in zip(s, s[1:]))
pend = defaultdict(list); NR5 = 0
for khn, nm, v, kn in kc.execute('select khipu, cord_name, value, knots from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0
    r5 = kfg_r5(kn); NR5 += r5
    pend[khn].append((int(m.group(1)), 0 if r5 else x))
kh = {khn: np.array([x for _, x in sorted(L)], np.int64) for khn, L in pend.items()}
if SMOKE:   # plumbing only: values shuffled within each khipu, no real statistic seen
    rsm = np.random.default_rng(1); kh = {k: rsm.permutation(v) for k, v in kh.items()}
ids = sorted(k for k, v in kh.items() if (v > 0).sum() >= 10); seqs = [kh[k] for k in ids]
N = len(seqs)
def runs(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; return np.split(s, b)
RUNS = [runs(s) for s in seqs]
def runperm(k, rng):
    r = RUNS[k]; o = rng.permutation(len(r)); return np.concatenate([r[i] for i in o])
def collapse(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; st = np.concatenate([[0], b]); return s[st]

prov = {r[0]: (r[1] or '').strip().strip('"').strip().casefold() for r in kc.execute('select name, provenance from khipu')}
grp = defaultdict(list)
for k, kid in enumerate(ids):
    p = prov.get(kid, '')
    if p and p != 'unknown': grp[p].append(k)
FPROV = {(min(a, b), max(a, b)) for g in grp.values() for x, a in enumerate(g) for b in g[x + 1:]}
FX = [(a, b) for a in range(N) for b in range(a + 1, N) if (a, b) not in FPROV]; MX = len(FX)
FXI = {p: i for i, p in enumerate(FX)}
XA = np.array([a for a, b in FX], np.int64); XB = np.array([b for a, b in FX], np.int64)
cs = [collapse(s) for s in seqs]
cntF = Counter(int(v) for s in cs for v in s if v > 0); NTF = sum(cntF.values()); VF = len(cntF); DENF = NTF + VF + 1
WF = {}
def wvF(cat):
    out = np.empty(len(cat), np.float64)
    for t, v in enumerate(cat.tolist()):
        if v not in WF: WF[v] = -math.log((cntF.get(int(v), 0) + 1) / DENF) if v > 0 else 0.0
        out[t] = WF[v]
    return out
def wham(S, pa=XA, pb=XB, wv=wvF):
    off = np.zeros(len(S) + 1, np.int64); off[1:] = np.cumsum([len(s) for s in S]); cat = np.ascontiguousarray(np.concatenate(S).astype(np.int64))
    wc = np.ascontiguousarray(wv(cat))
    n = len(pa); W = np.zeros(n); I = np.zeros(n, np.int64); J = np.zeros(n, np.int64); K = np.zeros(n, np.int64)
    lib.wham1(cat, wc, off, np.ascontiguousarray(pa), np.ascontiguousarray(pb), n, W, I, J, K); return W, I, J, K

okr2k = {kid: k for k, kid in enumerate(ids)}
def fxidx(x, y):
    if x not in okr2k or y not in okr2k: return None
    a, b = okr2k[x], okr2k[y]; return FXI.get((min(a, b), max(a, b)))
LEADS = dict(L1=('KH0143', 'KH0591'), L2=('KH0156', 'KH0432'), L3=('KH0377', 'KH0590'))
DIAG = ('KH0309', 'KH0293')
LI_all = {nm: fxidx(*p) for nm, p in LEADS.items()}; DI = fxidx(*DIAG)
LI = {nm: ix for nm, ix in LI_all.items() if ix is not None}
NOT_IN_FX = {nm: dict(pair='·'.join(LEADS[nm]), eligible=[x in okr2k for x in LEADS[nm]],
                      provenance=[prov.get(x, '') for x in LEADS[nm]]) for nm, ix in LI_all.items() if ix is None}
log('KFG N', N, 'F_x', MX, 'R5 masked', NR5, 'weights', NTF, VF, 'lead idx', LI_all, 'diag idx', DI)
# ---------------- P-unit null (new): periodicity-preserving unit permutation ----------------
# Each run-collapsed sequence is cut greedily (left to right) into UNITS: at position i, the longest stretch s[i..e] with
# s[t] == s[t-p] for all t in i+p..e, for p in {2, 3}, of length >= 2p (two full periods), is one unit (ties: smaller p);
# otherwise the single token s[i] is a unit. The null permutes the units uniformly and collapses again (adjacent equal values merge).
# With no periodic stretch every unit is one token and the null is exactly K064's run permutation; a periodic stretch
# (e.g. `3 2 3 2 3 2`) moves as one block, so two periodic khipus keep their periodic alignment under the null.
def units(s):
    s = [int(x) for x in s]; n = len(s); out = []; i = 0
    while i < n:
        best = (0, 0)
        for p in (2, 3):
            e = i + p
            while e < n and s[e] == s[e - p]: e += 1
            L = e - i
            if L >= 2 * p and L > best[0]: best = (L, p)
        L = best[0] if best[0] else 1; out.append(np.array(s[i:i + L], np.int64)); i += L
    return out
def punit(k, rng):
    u = UN[k]; o = rng.permutation(len(u)); return collapse(np.concatenate([u[i] for i in o]))
UN = [units(x) for x in cs]
log('units: sequences with >= 1 periodic unit', sum(any(len(v) > 1 for v in u) for u in UN))
# ---- S0 unit fixture (seed 6408) ----
rs = np.random.default_rng(6408); s0 = []
for t in range(20):
    x = collapse(rs.integers(1, 30, int(rs.integers(10, 40))).astype(np.int64)); xl = x.tolist()
    per = any(xl[t_] == xl[t_ - 2] for t_ in range(2, len(xl))) or any(xl[t_] == xl[t_ - 3] for t_ in range(3, len(xl)))
    u = units(x); cat_ok = np.concatenate(u).tolist() == xl
    single_ok = per or all(len(v) == 1 for v in u)
    blk = np.array([97, 98] * 4, np.int64); y = np.concatenate([x[:5], blk, x[5:]]); uy = units(y)
    blk_ok = any(len(v) >= 8 and v[:8].tolist() == blk.tolist() for v in uy) or any(v.tolist()[:8] == blk.tolist() for v in uy)
    s0.append(bool(cat_ok and single_ok and blk_ok))
S0 = all(s0); log('S0 units fixture', sum(s0), '/ 20')
# ---- G0 W fixture (K064 verbatim, seed 6404) ----
def brute_W(A, B, wd):
    best = 0.0
    for d in range(-(len(B) - 1), len(A)):
        pos = [(i, i - d) for i in range(len(A)) if 0 <= i - d < len(B)]
        m = [A[i] == B[j] and A[i] > 0 for i, j in pos]; wt = [wd[int(A[i])] for i, j in pos]
        for s in range(len(m)):
            for e in range(s, len(m)):
                if (e - s + 1) - sum(m[s:e + 1]) <= 1: best = max(best, sum(w for w, mm in zip(wt[s:e + 1], m[s:e + 1]) if mm))
    return best
rng_fx = np.random.default_rng(6404); fx = []
for t in range(20):
    S = [collapse(rng_fx.integers(0, 5, int(rng_fx.integers(5, 15))).astype(np.int64)) for _ in range(int(rng_fx.integers(3, 6)))]
    wd = {0: 0.0, **{v: float(rng_fx.uniform(0.1, 5.0)) for v in range(1, 5)}}
    pa = np.array([a for a in range(len(S)) for b in range(a + 1, len(S))], np.int64); pb = np.array([b for a in range(len(S)) for b in range(a + 1, len(S))], np.int64)
    got = wham(S, pa, pb, wv=lambda cat: np.array([wd[int(v)] for v in cat], np.float64))[0].tolist(); want = [brute_W(S[a], S[b], wd) for a, b in zip(pa, pb)]
    fx.append(bool(all(abs(g - w) < 1e-9 for g, w in zip(got, want))))
G0 = all(fx); log('G0', sum(fx), '/ 20')
TOPK = 40
def a0_top(seed_child):
    rng = np.random.default_rng(seed_child); Sx = [collapse(runperm(k, rng)) for k in range(N)]
    return float(wham(Sx)[0].max())
def pu_top(seed_child):
    rng = np.random.default_rng(seed_child); Sx = [punit(k, rng) for k in range(N)]
    W = wham(Sx)[0]; idx = np.argpartition(-W, TOPK)[:TOPK]; idx = idx[np.argsort(-W[idx])]
    return [(int(i), float(W[i])) for i in idx]
def plant_one(seed_child):
    rng = np.random.default_rng(seed_child); Sx = [punit(k, rng) for k in range(N)]; tries = 0
    while True:
        tries += 1; a, b = FX[int(rng.integers(0, MX))]
        if rng.random() < 0.5: a, b = b, a
        sa = Sx[a]; st = [i for i in range(len(sa) - 7) if (sa[i:i + 8] > 0).all() and len(set(sa[i:i + 8].tolist())) == 8]
        if st and len(Sx[b]) >= 10: break
    i = int(rng.choice(st)); j = int(rng.integers(0, len(Sx[b]) - 8 + 1)); w = sa[i:i + 8].copy()
    pos = int(rng.integers(1, 7)); dl = np.array([-3, -2, -1, 1, 2, 3])[rng.permutation(6)]; nv = next(int(w[pos] + x) for x in dl if w[pos] + x > 0)
    w[pos] = nv; Sx[b] = Sx[b].copy(); Sx[b][j:j + 8] = w
    Cx = [collapse(x) for x in Sx]; Wp, _, _, Kp = wham(Cx, np.array([min(a, b)], np.int64), np.array([max(a, b)], np.int64))
    return dict(W=float(Wp[0]), K=int(Kp[0]), tries=tries)
def kids(seed, n): return np.random.SeedSequence(seed).spawn(n)
from multiprocessing import Pool
with Pool(8) as pool:
    REF = pool.map(pu_top, kids(SEED_REF, RREF)); log('P-unit reference done', RREF)
    FPRT = pool.map(pu_top, kids(SEED_FPR, NFPR)); log('P-unit fpr nulls done', NFPR)
    PL = pool.map(plant_one, kids(SEED_PL, NPL)); log('plants done', NPL)
A0 = True   # A0 = K065 rebuilt verbatim on OKR, checked in mode a0 (analysis/k093_a0.json); full mode refuses to run otherwise
ref_max = np.array([t[0][1] for t in REF])
def padj(w): return float((1 + (ref_max >= w - EPS).sum()) / (1 + RREF))
fpr_p = [padj(t[0][1]) for t in FPRT]; FPR = float(np.mean([p <= ALPHA for p in fpr_p])); G1 = bool(FPR <= 0.10); log('G1 FPR', FPR)
for x in PL: x['p_adj'] = padj(x['W']); x['hit'] = x['p_adj'] <= ALPHA
POWER = float(np.mean([x['hit'] for x in PL])); G2 = bool(POWER >= 0.80); log('G2 power', POWER)
def wilson(x, n, z=1.959964):
    ph = x / n; den = 1 + z * z / n; ctr = (ph + z * z / (2 * n)) / den; hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [ctr - hw, ctr + hw]
crit = float(np.sort(ref_max)[::-1][int(math.floor(ALPHA * (1 + RREF))) - 1]) if RREF >= 40 else None
out = dict(source='KFG kfg_20261111.db (sha256 582e548d...)', mode=MODE, N=N, F_x=MX, n_R5_masked=NR5, alpha=ALPHA,
           seeds=dict(reference=SEED_REF, fpr=SEED_FPR, plants=SEED_PL, S0_fixture=6408, G0_fixture=6404, next_free=6496),
           null='P-unit (K065 verbatim)', S0_unit_fixture=dict(seed=6408, passed_cases=f'{sum(s0)}/20', passed=S0), G0_fixture=G0,
           A0='K065 rebuilt verbatim on OKR: analysis/k093_a0.json', leads_not_in_family=NOT_IN_FX,
           reference=dict(R=RREF, seed=SEED_REF, critical_W_at_alpha=crit, max_W_quantiles={q: float(np.quantile(ref_max, q)) for q in (0.5, 0.9, 0.95, 0.975, 0.99)}),
           G1=dict(seed=SEED_FPR, nulls=NFPR, share=FPR, p_adj=fpr_p, passed=G1),
           G2=dict(seed=SEED_PL, plants=NPL, power=POWER, wilson95=wilson(sum(x['hit'] for x in PL), NPL),
                   W_quantiles={q: float(np.quantile([x['W'] for x in PL], q)) for q in (0.05, 0.2, 0.5, 0.8)}, passed=G2))
if S0 and G0 and A0 and G1 and G2:
    W, I, J, K = wham(cs)
    def row(ix):
        a, b = FX[ix]; ka, kb = ids[a], ids[b]; i, j, k = int(I[ix]), int(J[ix]), int(K[ix])
        return dict(a=meta[ka]['okr'], b=meta[kb]['okr'], inv_a=meta[ka]['inv'], inv_b=meta[kb]['inv'], W=float(W[ix]), K=k, p_adj=padj(float(W[ix])),
                    seg_a=cs[a][max(i - 1, 0):i + k + 2].tolist(), seg_b=cs[b][max(j - 1, 0):j + k + 2].tolist())
    leads = {nm: row(ix) for nm, ix in LI.items()}
    order = sorted(leads, key=lambda nm: leads[nm]['p_adj']); m = len(LEADS); hold = True  # Holm m fixed at 3 (K065)
    for r_, nm in enumerate(order):
        thr = ALPHA / (m - r_); leads[nm]['holm_threshold'] = thr
        hold = hold and leads[nm]['p_adj'] <= thr + 1e-15; leads[nm]['confirmed'] = bool(hold)
    diag = row(DI) if DI is not None else dict(not_in_family=True)
    if DI is not None: diag['significant_single_step'] = bool(diag['p_adj'] <= ALPHA)
    # registered secondary: step-down max-W under P-unit (exact while < 40 removed)
    rank = np.argsort(-W); removed = set(); sd = []; pmax = 0.0
    for step in range(15):
        ix = int(rank[step]); removed.add(ix)
        mx = np.array([next(w for i_, w in t if i_ not in removed - {ix}) for t in REF])
        p = float((1 + (mx >= W[ix] - EPS).sum()) / (1 + RREF)); pmax = max(pmax, p)
        r = row(ix); r['p_stepdown'] = pmax; r['significant'] = bool(pmax <= ALPHA); sd.append(r)
        if pmax > ALPHA: break
    out['H1'] = dict(run=True, leads=leads, diagnostic_KH0309_KH0293=diag, stepdown_Punit=sd,
                     verdict='; '.join(f"{nm} {'CONFIRMED' if leads[nm]['confirmed'] else 'NOT CONFIRMED'}" for nm in LI) + ''.join(f'; {nm} NOT TESTABLE as a pair (not in F_x)' for nm in NOT_IN_FX))
else:
    out['H1'] = dict(run=False, verdict=('NOT TESTABLE (power)' if (S0 and G0 and A0 and G1 and not G2) else 'EXCLUDED (tool/audit)' if not (S0 and G0 and A0 and G1) else 'not run'))
out['seconds'] = round(time.time() - t0, 1)
json.dump(out, open(OUT, 'w'), indent=1, default=float)
print(json.dumps(out, default=float)[:6000])
