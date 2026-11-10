#!/usr/bin/env python3
"""K065 - pre-registered CONFIRMATION of K064's three new cross-provenance leads under a PERIODICITY-PRESERVING null.
Null P-unit (new): each run-collapsed level-1 sequence is cut greedily into units - a maximal stretch with period 2 or 3 of length
>= two full periods is one unit, every other token is its own unit - and the units are permuted uniformly, then collapsed again.
Without periodic stretches this is exactly K064's run permutation; a periodic stretch (e.g. `3 2 3 2 ...`, the K064 false alarm
KH0309.KH0293) moves as one block, so two periodic khipus keep their periodic alignment under the null.
(Rejected in the disclosed smoke before this commit: an exact doublet-preserving Eulerian shuffle - it also preserves every chain of
unique values, so the corpus's real copies survive in the null; reference max = 121.0, the K010 pair; a broken meter.)
Data, R5 mask, collapse, family F_x (89,489 pairs), full-corpus weight table, kernel W: K064 verbatim.
Confirmation rule: single-step max-W over F_x, p_adj = (1 + #{null F_x max >= W_obs}) / (1 + R), R = 1000 P-unit nulls (seed 6405);
Holm over the 3 leads at alpha 0.025. Diagnostic D (registered, not in Holm): KH0309.KH0293. Secondary (registered): step-down
max-W list under P-unit, up to 15 steps (each null keeps its 40 largest pair scores).
Gates: S0 unit fixture (seed 6408, 20 random sequences: units concatenate back exactly; no periodic stretch -> all singletons; an
inserted `97 98` x4 block stays one unit); G0 W fixture (K064's, seed 6404) 20/20; A0 audit of K064: run-permutation null seed 6401
R 500 on F_x must reproduce K064's critical W 25.502133284010203 and median 20.321479515837176 (|diff| < 1e-9); G1 FPR (seed 6406,
40 P-unit nulls): share whose own F_x max reaches p_adj <= 0.025 must be <= 0.10; G2 power (seed 6407, 100 plants, K064 plant
design - 8 distinct non-zero cords, one interior cord +-1..3 - planted into a P-unit-null corpus): recovered iff p_adj <= 0.025;
power >= 0.80 else NOT TESTABLE (no observed p read).
Usage: python3 tools/k065_periodic_unit_confirm.py data/khipu.db full
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sqlite3, json, sys, time, math, os, ctypes, hashlib, subprocess, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); MODE = sys.argv[2] if len(sys.argv) > 2 else 'gates'
SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
if hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest() != SHA: sys.exit('EXCLUDED: khipu.db hash differs from MANIFEST')
c = sqlite3.connect('file:' + sys.argv[1] + '?mode=ro', uri=True); ALPHA = 0.025; EPS = 1e-9
RREF, NFPR, NPL, NA0 = (int(x) for x in os.environ.get('K065_SMOKE', '1000,40,100,500').split(','))
OUT = 'analysis/k065_results.json' if 'K065_SMOKE' not in os.environ else '/tmp/k065/smoke.json'
HERE = os.path.dirname(os.path.abspath(__file__)); SO = '/tmp/k065/k065_wham1.so'; os.makedirs('/tmp/k065', exist_ok=True)
subprocess.run(['cc', '-O2', '-shared', '-fPIC', '-o', SO, os.path.join(HERE, 'k065_wham1.c')], check=True)
lib = ctypes.CDLL(SO); P64 = np.ctypeslib.ndpointer(np.int64, flags='C_CONTIGUOUS'); PF = np.ctypeslib.ndpointer(np.float64, flags='C_CONTIGUOUS')
lib.wham1.argtypes = [P64, PF, P64, P64, P64, ctypes.c_int64, PF, P64, P64, P64]
def log(*a): print(*a, round(time.time() - t0, 1), flush=True)
# ---------------- data exactly as K064 ----------------
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
meta = {r[0]: dict(okr=r[1] or '', inv=r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
def place_(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
clpl = defaultdict(set); clcd = {}
for cid_, cl_, t_, v_ in c.execute("select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
    t_ = (t_ or '').strip()
    if t_ in ('S', 'L', 'E') and v_: clpl[cl_].add(place_(int(v_)) if t_ == 'S' else 0)
    clcd[cl_] = cid_
ordn_ = {r[0]: r[1] for r in c.execute("select CLUSTER_ID, ORDINAL from knot_cluster")}
bc_ = defaultdict(dict)
for cl_, pl_ in clpl.items():
    if len(pl_) == 1 and ordn_.get(cl_) is not None: bc_[clcd[cl_]][ordn_[cl_]] = next(iter(pl_))
R5 = {cd for cd, d in bc_.items() if len(d) >= 2 and not all(a > b for a, b in zip([d[o] for o in sorted(d)], [d[o] for o in sorted(d)][1:]))}
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: kh[khid].append(0 if cid in R5 else val.get(cid, 0))
ids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]; seqs = [np.array(kh[k], np.int64) for k in ids]
N = len(seqs)
def runs(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; return np.split(s, b)
RUNS = [runs(s) for s in seqs]
def runperm(k, rng):
    r = RUNS[k]; o = rng.permutation(len(r)); return np.concatenate([r[i] for i in o])
def collapse(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; st = np.concatenate([[0], b]); return s[st]
prov = {r[0]: (r[1] or '').strip().casefold() for r in c.execute("select KHIPU_ID, PROVENANCE from khipu_main")}
grp = defaultdict(list)
for k, kid in enumerate(ids):
    p = prov.get(kid, '')
    if p and p != 'unknown': grp[p].append(k)
FPROV = {(min(a, b), max(a, b)) for g in grp.values() for x, a in enumerate(g) for b in g[x + 1:]}
FX = [(a, b) for a in range(N) for b in range(a + 1, N) if (a, b) not in FPROV]; MX = len(FX)
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
okr2k = {meta[kid]['okr']: k for k, kid in enumerate(ids)}
def fxidx(x, y):
    a, b = okr2k[x], okr2k[y]; return FX.index((min(a, b), max(a, b)))
LEADS = dict(L1=('KH0143', 'KH0591'), L2=('KH0156', 'KH0432'), L3=('KH0377', 'KH0590'))
DIAG = ('KH0309', 'KH0293')
LI = {nm: fxidx(*p) for nm, p in LEADS.items()}; DI = fxidx(*DIAG)
log('N', N, 'F_x', MX, 'weights', NTF, VF, 'lead idx', LI, 'diag idx', DI)
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
    A0L = np.array(pool.map(a0_top, kids(6401, NA0))); log('A0 nulls done', NA0)
    REF = pool.map(pu_top, kids(6405, RREF)); log('P-unit reference done', RREF)
    FPRT = pool.map(pu_top, kids(6406, NFPR)); log('P-unit fpr nulls done', NFPR)
    PL = pool.map(plant_one, kids(6407, NPL)); log('plants done', NPL)
A0crit = float(np.sort(A0L)[::-1][int(math.floor(0.025 * (1 + NA0))) - 1]) if NA0 >= 40 else None; A0med = float(np.quantile(A0L, 0.5))
A0 = bool(A0crit is not None and abs(A0crit - 25.502133284010203) < 1e-9 and abs(A0med - 20.321479515837176) < 1e-9); log('A0 audit K064', A0, A0crit, A0med)
ref_max = np.array([t[0][1] for t in REF])
def padj(w): return float((1 + (ref_max >= w - EPS).sum()) / (1 + RREF))
fpr_p = [padj(t[0][1]) for t in FPRT]; FPR = float(np.mean([p <= ALPHA for p in fpr_p])); G1 = bool(FPR <= 0.10); log('G1 FPR', FPR)
for x in PL: x['p_adj'] = padj(x['W']); x['hit'] = x['p_adj'] <= ALPHA
POWER = float(np.mean([x['hit'] for x in PL])); G2 = bool(POWER >= 0.80); log('G2 power', POWER)
def wilson(x, n, z=1.959964):
    ph = x / n; den = 1 + z * z / n; ctr = (ph + z * z / (2 * n)) / den; hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [ctr - hw, ctr + hw]
crit = float(np.sort(ref_max)[::-1][int(math.floor(ALPHA * (1 + RREF))) - 1]) if RREF >= 40 else None
out = dict(N=N, F_x=MX, alpha=ALPHA, null='P-unit: periodicity-preserving unit permutation (period-2/3 stretches of >= 2 periods move as blocks), then collapse',
           S0_unit_fixture=dict(seed=6408, passed_cases=f'{sum(s0)}/20', passed=S0), G0_fixture=G0,
           A0_audit_K064=dict(target_crit=25.502133284010203, target_median=20.321479515837176, crit=A0crit, median=A0med, reproduced=A0),
           reference=dict(R=RREF, seed=6405, critical_W_at_alpha=crit, max_W_quantiles={q: float(np.quantile(ref_max, q)) for q in (0.5, 0.9, 0.95, 0.975, 0.99)}),
           G1=dict(seed=6406, nulls=NFPR, share=FPR, p_adj=fpr_p, passed=G1),
           G2=dict(seed=6407, plants=NPL, power=POWER, wilson95=wilson(sum(x['hit'] for x in PL), NPL),
                   W_quantiles={q: float(np.quantile([x['W'] for x in PL], q)) for q in (0.05, 0.2, 0.5, 0.8)}, passed=G2))
if S0 and G0 and A0 and G1 and G2 and MODE == 'full':
    W, I, J, K = wham(cs)
    def row(ix):
        a, b = FX[ix]; ka, kb = ids[a], ids[b]; i, j, k = int(I[ix]), int(J[ix]), int(K[ix])
        return dict(a=meta[ka]['okr'], b=meta[kb]['okr'], inv_a=meta[ka]['inv'], inv_b=meta[kb]['inv'], W=float(W[ix]), K=k, p_adj=padj(float(W[ix])),
                    seg_a=cs[a][max(i - 1, 0):i + k + 2].tolist(), seg_b=cs[b][max(j - 1, 0):j + k + 2].tolist())
    leads = {nm: row(ix) for nm, ix in LI.items()}
    order = sorted(leads, key=lambda nm: leads[nm]['p_adj']); m = len(order); hold = True
    for r_, nm in enumerate(order):
        thr = ALPHA / (m - r_); leads[nm]['holm_threshold'] = thr
        hold = hold and leads[nm]['p_adj'] <= thr + 1e-15; leads[nm]['confirmed'] = bool(hold)
    diag = row(DI); diag['significant_single_step'] = bool(diag['p_adj'] <= ALPHA)
    # registered secondary: step-down max-W under P-unit (exact while < 40 removed)
    rank = np.argsort(-W); removed = set(); sd = []; pmax = 0.0
    for step in range(15):
        ix = int(rank[step]); removed.add(ix)
        mx = np.array([next(w for i_, w in t if i_ not in removed - {ix}) for t in REF])
        p = float((1 + (mx >= W[ix] - EPS).sum()) / (1 + RREF)); pmax = max(pmax, p)
        r = row(ix); r['p_stepdown'] = pmax; r['significant'] = bool(pmax <= ALPHA); sd.append(r)
        if pmax > ALPHA: break
    out['H1'] = dict(run=True, leads=leads, diagnostic_KH0309_KH0293=diag, stepdown_Punit=sd,
                     verdict='; '.join(f"{nm} {'CONFIRMED' if leads[nm]['confirmed'] else 'NOT CONFIRMED'}" for nm in LEADS))
else:
    out['H1'] = dict(run=False, verdict=('NOT TESTABLE (power)' if (S0 and G0 and A0 and G1 and not G2) else 'EXCLUDED (tool/audit)' if not (S0 and G0 and A0 and G1) else 'not run'))
out['seconds'] = round(time.time() - t0, 1)
json.dump(out, open(OUT, 'w'), indent=1, default=float)
print(json.dumps(out, default=float)[:5000])
