#!/usr/bin/env python3
"""K064 - pre-registered CROSS-PROVENANCE scan (line 3) with the K063 rarity-weighted, one-cord-tolerant statistic W.
Family F_x = every pair of the 433 corpus khipus that is NOT in K060's within-provenance family F_prov (different provenances, or
at least one unknown/blank provenance). Data, R5 mask, run-collapse, null (within-khipu run permutation) and kernel: K063 verbatim.
Weights (fixed before any null/plant/observed value): w(v) = -ln[(n_v+1)/(n_tot+V+1)] from the run-collapsed non-zero level-1
values of ALL 433 corpus khipus (no lead exclusion: no lead exists in F_x; the run permutation leaves each khipu's value multiset
unchanged before collapse, so the table is a fixed scoring function).
Discovery: Westfall-Young step-down max-W over F_x at alpha 0.025, R = 500 reference nulls (seed 6401, one SeedSequence child per
replicate). Each null keeps its 40 largest pair scores, so step-down maxima are exact while fewer than 40 pairs have been removed.
Gates: G0 brute-force fixture (seed 6404, 20 corpora); A0 audit of K063: K063 weights (4 leads excluded), seed 6301, R 1000 on F_prov
must reproduce K063's critical W 26.62082430464733 and median 18.3558702091879 (|diff| < 1e-9); G1 FPR (seed 6402, 40 nulls): share of
nulls whose own F_x max reaches p_adj <= 0.025 must be <= 0.10; G2 power (seed 6403, 100 plants, K062/K063 plant design verbatim but
the planted pair drawn from F_x): recovered iff the pair's single-step p_adj <= 0.025; power >= 0.80 else NOT TESTABLE and no
observed W over F_x is computed.
Usage: python3 tools/k064_cross_provenance_scan.py data/khipu.db full
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sqlite3, json, sys, time, math, os, ctypes, hashlib, subprocess, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); MODE = sys.argv[2] if len(sys.argv) > 2 else 'gates'
SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
if hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest() != SHA: sys.exit('EXCLUDED: khipu.db hash differs from MANIFEST')
c = sqlite3.connect('file:' + sys.argv[1] + '?mode=ro', uri=True); ALPHA = 0.025; EPS = 1e-9
RREF, NFPR, NPL = (int(x) for x in os.environ.get('K064_SMOKE', '500,40,100').split(','))
OUT = 'analysis/k064_results.json' if 'K064_SMOKE' not in os.environ else '/tmp/k064/smoke.json'
HERE = os.path.dirname(os.path.abspath(__file__)); SO = '/tmp/k064/k064_wham1.so'; os.makedirs('/tmp/k064', exist_ok=True)
subprocess.run(['cc', '-O2', '-shared', '-fPIC', '-o', SO, os.path.join(HERE, 'k064_wham1.c')], check=True)
lib = ctypes.CDLL(SO); P64 = np.ctypeslib.ndpointer(np.int64, flags='C_CONTIGUOUS'); PF = np.ctypeslib.ndpointer(np.float64, flags='C_CONTIGUOUS')
lib.wham1.argtypes = [P64, PF, P64, P64, P64, ctypes.c_int64, PF, P64, P64, P64]
def log(*a): print(*a, round(time.time() - t0, 1), flush=True)
# ---------------- data exactly as K012 / K061 ----------------
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
N = len(seqs); M = N * (N - 1) // 2
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
FAM = sorted({(min(a, b), max(a, b)) for g in grp.values() for x, a in enumerate(g) for b in g[x + 1:]}); MF = len(FAM)
PA = np.array([a for a, b in FAM], np.int64); PB = np.array([b for a, b in FAM], np.int64)
okr2k = {meta[kid]['okr']: k for k, kid in enumerate(ids)}
LEADS = dict(A=('KH0132', 'KH0456'), B=('KH0446', 'KH0451'))
LK = {}
for nm, (x, y) in LEADS.items():
    a_, b_ = okr2k[x], okr2k[y]; LK[nm] = FAM.index((min(a_, b_), max(a_, b_)))
EXCL = {okr2k[x] for p in LEADS.values() for x in p}
cs = [collapse(s) for s in seqs]
cnt = Counter(int(v) for k, s in enumerate(cs) if k not in EXCL for v in s if v > 0)
NTOT = sum(cnt.values()); V = len(cnt); DEN = NTOT + V + 1
def wfun(v): return -math.log((cnt.get(int(v), 0) + 1) / DEN)
WMAP = {}
def wvec(s):
    out = np.empty(len(s), np.float64)
    for t, v in enumerate(s.tolist()):
        if v not in WMAP: WMAP[v] = wfun(v) if v > 0 else 0.0
        out[t] = WMAP[v]
    return out
log('N', N, 'family', MF, 'lead index', LK, 'weight source tokens', NTOT, 'distinct', V)
def wham(S, pa=PA, pb=PB, wv=None):
    off = np.zeros(len(S) + 1, np.int64); off[1:] = np.cumsum([len(s) for s in S]); cat = np.ascontiguousarray(np.concatenate(S).astype(np.int64))
    wc = np.ascontiguousarray(np.concatenate([wvec(s) for s in S]) if wv is None else wv(cat))
    n = len(pa); W = np.zeros(n); I = np.zeros(n, np.int64); J = np.zeros(n, np.int64); K = np.zeros(n, np.int64)
    lib.wham1(cat, wc, off, np.ascontiguousarray(pa), np.ascontiguousarray(pb), n, W, I, J, K); return W, I, J, K

UNIT = lambda cat: np.where(cat > 0, 1.0, 0.0)
from multiprocessing import Pool
FPROV = set(FAM)
FX = [(a, b) for a in range(N) for b in range(a + 1, N) if (a, b) not in FPROV]; MX = len(FX)
XA = np.array([a for a, b in FX], np.int64); XB = np.array([b for a, b in FX], np.int64)
cntF = Counter(int(v) for s in cs for v in s if v > 0); NTF = sum(cntF.values()); VF = len(cntF); DENF = NTF + VF + 1
WF = {}
def wF(v): return -math.log((cntF.get(int(v), 0) + 1) / DENF)
def wvF(cat):
    out = np.empty(len(cat), np.float64)
    for t, v in enumerate(cat.tolist()):
        if v not in WF: WF[v] = wF(v) if v > 0 else 0.0
        out[t] = WF[v]
    return out
log('N', N, 'F_prov', MF, 'F_x', MX, 'full weight tokens', NTF, 'distinct', VF)
KNOWN = {('KH0128', 'KH0137'), ('KH0140', 'KH0483'), ('KH0304', 'KH0303'), ('KH0305', 'KH0301'), ('KH0362', 'KH0049'), ('KH0132', 'KH0456')}
KNOWN = {frozenset(p) for p in KNOWN}
# ---- G0 fixture (seed 6404), same exhaustive check as K063 ----
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
# ---- A0 audit of K063 (K063 weights, seed 6301, R 1000, F_prov) ----
NA0 = 1000 if 'K064_SMOKE' not in os.environ else 2
rng = np.random.default_rng(6301); a0 = []
for r in range(NA0):
    Sx = [collapse(runperm(k, rng)) for k in range(N)]; a0.append(float(wham(Sx)[0].max()))
a0 = np.array(a0); A0crit = float(np.sort(a0)[::-1][int(math.floor(0.025 * (1 + NA0))) - 1]) if NA0 >= 40 else None
A0med = float(np.quantile(a0, 0.5))
A0 = bool(A0crit is not None and abs(A0crit - 26.62082430464733) < 1e-9 and abs(A0med - 18.3558702091879) < 1e-9)
log('A0 audit K063', A0, A0crit, A0med)
# ---- parallel null machinery on F_x ----
TOPK = 40
def null_top(seed_child):
    rng = np.random.default_rng(seed_child); Sx = [collapse(runperm(k, rng)) for k in range(N)]
    W = wham(Sx, XA, XB, wv=wvF)[0]; idx = np.argpartition(-W, TOPK)[:TOPK]; idx = idx[np.argsort(-W[idx])]
    return [(int(i), float(W[i])) for i in idx]
def plant_one(seed_child):
    rng = np.random.default_rng(seed_child); Sx = [runperm(k, rng) for k in range(N)]; tries = 0
    while True:
        tries += 1; a, b = FX[int(rng.integers(0, MX))]
        if rng.random() < 0.5: a, b = b, a
        sa = Sx[a]; st = [i for i in range(len(sa) - 7) if (sa[i:i + 8] > 0).all() and len(set(sa[i:i + 8].tolist())) == 8]
        if st and len(Sx[b]) >= 10: break
    i = int(rng.choice(st)); j = int(rng.integers(0, len(Sx[b]) - 8 + 1)); w = sa[i:i + 8].copy()
    pos = int(rng.integers(1, 7)); dl = np.array([-3, -2, -1, 1, 2, 3])[rng.permutation(6)]; nv = next(int(w[pos] + x) for x in dl if w[pos] + x > 0)
    w[pos] = nv; Sx[b] = Sx[b].copy(); Sx[b][j:j + 8] = w
    Cx = [collapse(x) for x in Sx]; Wp, _, _, Kp = wham(Cx, np.array([min(a, b)], np.int64), np.array([max(a, b)], np.int64), wv=wvF)
    return dict(W=float(Wp[0]), K=int(Kp[0]), tries=tries)
def kids(seed, n): return np.random.SeedSequence(seed).spawn(n)
with Pool(8) as pool:
    REF = pool.map(null_top, kids(6401, RREF)); log('ref done', RREF)
    FPRT = pool.map(null_top, kids(6402, NFPR)); log('fpr nulls done', NFPR)
    PL = pool.map(plant_one, kids(6403, NPL)); log('plants done', NPL)
ref_max = np.array([t[0][1] for t in REF])
def padj(w): return float((1 + (ref_max >= w - EPS).sum()) / (1 + RREF))
fpr_p = [padj(t[0][1]) for t in FPRT]; FPR = float(np.mean([p <= ALPHA for p in fpr_p])); G1 = bool(FPR <= 0.10); log('G1 FPR', FPR)
for x in PL: x['p_adj'] = padj(x['W']); x['hit'] = x['p_adj'] <= ALPHA
POWER = float(np.mean([x['hit'] for x in PL])); G2 = bool(POWER >= 0.80); log('G2 power', POWER)
def wilson(x, n, z=1.959964):
    ph = x / n; den = 1 + z * z / n; ctr = (ph + z * z / (2 * n)) / den; hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [ctr - hw, ctr + hw]
crit = float(np.sort(ref_max)[::-1][int(math.floor(ALPHA * (1 + RREF))) - 1]) if RREF >= 40 else None
out = dict(N=N, F_prov=MF, F_x=MX, alpha=ALPHA, weights=dict(source='run-collapsed non-zero level-1 values of all corpus khipus', tokens=NTF, distinct=VF),
           G0_fixture=G0, A0_audit_K063=dict(target_crit=26.62082430464733, target_median=18.3558702091879, crit=A0crit, median=A0med, reproduced=A0),
           reference=dict(R=RREF, seed=6401, critical_W_at_alpha=crit, max_W_quantiles={q: float(np.quantile(ref_max, q)) for q in (0.5, 0.9, 0.95, 0.975, 0.99)}),
           G1=dict(seed=6402, nulls=NFPR, share=FPR, p_adj=fpr_p, passed=G1),
           G2=dict(seed=6403, plants=NPL, power=POWER, wilson95=wilson(sum(x['hit'] for x in PL), NPL),
                   W_quantiles={q: float(np.quantile([x['W'] for x in PL], q)) for q in (0.05, 0.2, 0.5, 0.8)}, passed=G2))
if G0 and A0 and G1 and G2 and MODE == 'full':
    W, I, J, K = wham(cs, XA, XB, wv=wvF); order = np.argsort(-W)[:15]
    removed = set(); disc = []; pprev = 0.0
    for k in order:
        nmax = np.array([next((w for i, w in t if i not in removed), t[-1][1]) for t in REF])
        p = max(pprev, float((1 + (nmax >= W[k] - EPS).sum()) / (1 + RREF))); pprev = p
        a, b = FX[k]; oa, ob = meta[ids[a]]['okr'], meta[ids[b]]['okr']
        seg_a = [int(x) for x in cs[a][max(I[k], 0):max(I[k], 0) + int(K[k]) + 2]]; seg_b = [int(x) for x in cs[b][max(J[k], 0):max(J[k], 0) + int(K[k]) + 2]]
        disc.append(dict(a=oa, b=ob, inv_a=meta[ids[a]]['inv'], inv_b=meta[ids[b]]['inv'], prov_a=prov.get(ids[a], ''), prov_b=prov.get(ids[b], ''),
                         W=float(W[k]), K=int(K[k]), p_single=padj(float(W[k])), p_stepdown=p, significant=p <= ALPHA,
                         known=frozenset((oa, ob)) in KNOWN, seg_a=seg_a, seg_b=seg_b))
        if p > ALPHA: break
        removed.add(int(k))
    out['H1'] = dict(run=True, top=disc, n_significant=sum(d['significant'] for d in disc), n_new=sum(d['significant'] and not d['known'] for d in disc),
                     verdict=('DETECTED: new cross-provenance correspondence(s)' if any(d['significant'] and not d['known'] for d in disc)
                              else 'ONLY KNOWN PAIRS' if any(d['significant'] for d in disc) else 'NOT DETECTED (silence readable at power %.2f)' % POWER))
else:
    out['H1'] = dict(run=False, verdict=('NOT TESTABLE (power)' if (G0 and A0 and G1 and not G2) else 'EXCLUDED (tool/audit)' if not (G0 and A0 and G1) else 'not run'))
out['seconds'] = round(time.time() - t0, 1)
json.dump(out, open(OUT, 'w'), indent=1, default=float)
print(json.dumps(out, default=float)[:6000])
