#!/usr/bin/env python3
"""K063 - pre-registered, POST-SELECTION confirmation of the K061 lead A KH0132 (UR1118) . KH0456 (UR218) with a RARITY-WEIGHTED,
one-cord-tolerant statistic and a selection-adjusted (family max) null. Lead B KH0446 (UR208) . KH0451 (UR213) is read with the
same statistic and the same family-max null (single-step max-W controls the family-wise error over all 4 039 F_prov pairs at once).
Statistic W(pair) = max over aligned segments (same offset on both run-collapsed level-1 sequences, K012 corpus and R5 mask, K061
verbatim) containing at most ONE non-matching position of SUM over matching positions of w(v), match = equal and > 0.
Weights (fixed before any null / plant / observed value): w(v) = -ln[(n_v + 1) / (n_tot + V + 1)], n_v = count of non-zero value v in
the run-collapsed real sequences of the N corpus khipus EXCLUDING the four lead khipus KH0132, KH0456, KH0446, KH0451 (no leakage of
the leads' own values), n_tot = sum n_v, V = number of distinct values; values absent from that source get w = -ln[1/(n_tot+V+1)].
The same weight table is used for every null, plant and the observed corpus. C kernel tools/k063_wham1.c.
p_adj = (1 + #{reference nulls whose family max W >= W_obs - 1e-9}) / (1 + R). Alpha 0.025 (as K062).
Null: K012/K061 within-khipu run permutation of raw level-1 sequences, then run-collapse (K061/K062 verbatim).
Gates: G0 brute-force fixture (seed 6304, 20 corpora, random weights); A0 audit of K062: unit weights + K062 seed 6201 must reproduce
K062's published reference max-T counts exactly {4: 7, 5: 621, 6: 329, 7: 40, 8: 3}; G1 FPR on 40 fresh nulls (seed 6302): share of
corpora whose own family max reaches p_adj <= 0.025 must be <= 0.10; G2 power (seed 6303, 200 plants, K062 plant design verbatim):
8-cord near-copies (source window 8 non-zero, 8 distinct values, one interior cord altered by the first positive of a random order of
{-3..-1, 1..3}) planted in a random F_prov pair; recovered iff the planted pair's p_adj <= 0.025; power >= 0.80 else NOT TESTABLE and
the observed W is not computed. Reference R = 1000 (seed 6301).
Usage: python3 tools/k063_rarity_weighted_confirm.py data/khipu.db full   [gates = no observed W]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sqlite3, json, sys, time, math, os, ctypes, hashlib, subprocess, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); MODE = sys.argv[2] if len(sys.argv) > 2 else 'gates'
SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
if hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest() != SHA: sys.exit('EXCLUDED: khipu.db hash differs from MANIFEST')
c = sqlite3.connect('file:' + sys.argv[1] + '?mode=ro', uri=True); ALPHA = 0.025; EPS = 1e-9
RREF, NFPR, NPL = (int(x) for x in os.environ.get('K063_SMOKE', '1000,40,200').split(','))
OUT = 'analysis/k063_results.json' if 'K063_SMOKE' not in os.environ else '/tmp/k063/smoke.json'
HERE = os.path.dirname(os.path.abspath(__file__)); SO = '/tmp/k063/k063_wham1.so'; os.makedirs('/tmp/k063', exist_ok=True)
subprocess.run(['cc', '-O2', '-shared', '-fPIC', '-o', SO, os.path.join(HERE, 'k063_wham1.c')], check=True)
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
# ---------------- G0 brute-force fixture (seed 6304) ----------------
def brute_W(A, B, wd):
    best = 0.0
    for d in range(-(len(B) - 1), len(A)):
        pos = [(i, i - d) for i in range(len(A)) if 0 <= i - d < len(B)]
        m = [A[i] == B[j] and A[i] > 0 for i, j in pos]; wt = [wd[int(A[i])] for i, j in pos]
        for s in range(len(m)):
            for e in range(s, len(m)):
                if (e - s + 1) - sum(m[s:e + 1]) <= 1: best = max(best, sum(w for w, mm in zip(wt[s:e + 1], m[s:e + 1]) if mm))
    return best
rng_fx = np.random.default_rng(6304); fx = []
for t in range(20):
    S = [collapse(rng_fx.integers(0, 5, int(rng_fx.integers(5, 15))).astype(np.int64)) for _ in range(int(rng_fx.integers(3, 6)))]
    wd = {0: 0.0, **{v: float(rng_fx.uniform(0.1, 5.0)) for v in range(1, 5)}}
    pa = np.array([a for a in range(len(S)) for b in range(a + 1, len(S))], np.int64); pb = np.array([b for a in range(len(S)) for b in range(a + 1, len(S))], np.int64)
    got = wham(S, pa, pb, wv=lambda cat: np.array([wd[int(v)] for v in cat], np.float64))[0].tolist(); want = [brute_W(S[a], S[b], wd) for a, b in zip(pa, pb)]
    fx.append(dict(pairs=len(want), ok=all(abs(g - w) < 1e-9 for g, w in zip(got, want)), max_W=max(want)))
G0 = all(x['ok'] for x in fx); log('G0', sum(x['ok'] for x in fx), '/ 20')
# ---------------- A0 audit of K062: unit weights, K062 seed 6201 ----------------
K062_COUNTS = {4: 7, 5: 621, 6: 329, 7: 40, 8: 3}
rng = np.random.default_rng(6201); a0 = []
for r in range(1000 if 'K063_SMOKE' not in os.environ else 2):
    Sx = [collapse(runperm(k, rng)) for k in range(N)]; a0.append(int(round(wham(Sx, wv=UNIT)[0].max())))
A0c = {int(k): int(v) for k, v in sorted(Counter(a0).items())}; A0 = A0c == K062_COUNTS; log('A0 audit K062', A0, A0c)
# ---------------- reference null (seed 6301) ----------------
rng = np.random.default_rng(6301); ref_max = []; ref_lead = {nm: [] for nm in LK}; ref_argmax_K = []
for r in range(RREF):
    Sx = [collapse(runperm(k, rng)) for k in range(N)]; W, I, J, K = wham(Sx); m = int(W.argmax())
    ref_max.append(float(W[m])); ref_argmax_K.append(int(K[m]))
    for nm, ix in LK.items(): ref_lead[nm].append(float(W[ix]))
    if r % 200 == 199: log('ref', r + 1)
ref_max = np.array(ref_max)
def padj(w): return float((1 + (ref_max >= w - EPS).sum()) / (1 + RREF))
# ---------------- G1 FPR on fresh nulls (seed 6302) ----------------
rng = np.random.default_rng(6302); fpr_p = []
for r in range(NFPR):
    Sx = [collapse(runperm(k, rng)) for k in range(N)]; fpr_p.append(padj(float(wham(Sx)[0].max())))
FPR = float(np.mean([p <= ALPHA for p in fpr_p])); G1 = bool(FPR <= 0.10); log('G1 FPR', FPR)
# ---------------- G2 power (seed 6303, K062 plant design verbatim) ----------------
rng = np.random.default_rng(6303); pl = []; DELTAS = np.array([-3, -2, -1, 1, 2, 3])
for t in range(NPL):
    Sx = [runperm(k, rng) for k in range(N)]; tries = 0
    while True:
        tries += 1; a, b = FAM[int(rng.integers(0, MF))]
        if rng.random() < 0.5: a, b = b, a
        sa = Sx[a]; st = [i for i in range(len(sa) - 7) if (sa[i:i + 8] > 0).all() and len(set(sa[i:i + 8].tolist())) == 8]
        if st and len(Sx[b]) >= 10: break
    i = int(rng.choice(st)); j = int(rng.integers(0, len(Sx[b]) - 8 + 1)); w = sa[i:i + 8].copy()
    pos = int(rng.integers(1, 7)); dl = DELTAS[rng.permutation(6)]; nv = next(int(w[pos] + x) for x in dl if w[pos] + x > 0)
    w[pos] = nv; Sx[b] = Sx[b].copy(); Sx[b][j:j + 8] = w
    Cx = [collapse(x) for x in Sx]; Wp, _, _, Kp = wham(Cx, np.array([min(a, b)], np.int64), np.array([max(a, b)], np.int64))
    pl.append(dict(W=float(Wp[0]), K=int(Kp[0]), p_adj=padj(float(Wp[0])), hit=padj(float(Wp[0])) <= ALPHA, prov=prov[ids[a]], tries=tries,
                   window_weight=float(sum(wfun(v) for v in sa[i:i + 8].tolist()))))
    if t % 50 == 49: log('plant', t + 1)
POWER = float(np.mean([x['hit'] for x in pl])); G2 = bool(POWER >= 0.80); log('G2 power', POWER)
def wilson(x, n, z=1.959964):
    ph = x / n; den = 1 + z * z / n; ctr = (ph + z * z / (2 * n)) / den; hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [ctr - hw, ctr + hw]
crit = float(np.sort(ref_max)[::-1][int(math.floor(ALPHA * (1 + RREF))) - 1])
out = dict(N=N, family_pairs=MF, leads={nm: dict(a=LEADS[nm][0], b=LEADS[nm][1], fam_index=ix) for nm, ix in LK.items()}, alpha=ALPHA,
           weights=dict(source='run-collapsed non-zero level-1 values of the corpus minus the 4 lead khipus', tokens=NTOT, distinct=V,
                        w_min=min(wfun(v) for v in cnt), w_max_seen=max(wfun(v) for v in cnt), w_unseen=-math.log(1 / DEN),
                        examples={str(v): round(wfun(v), 4) for v in (1, 5, 10, 20, 50, 100, 319, 453, 474, 492, 932, 935)}),
           G0_fixture=G0, G0_n=sum(x['ok'] for x in fx), A0_audit_K062=dict(published=K062_COUNTS, reproduced_counts=A0c, reproduced=A0),
           reference=dict(R=RREF, seed=6301, max_W_quantiles={q: float(np.quantile(ref_max, q)) for q in (0.5, 0.9, 0.95, 0.975, 0.99)},
                          critical_W_at_alpha=crit, max_W_K_counts={int(k): int(v) for k, v in Counter(ref_argmax_K).items()},
                          lead_W_quantiles={nm: {q: float(np.quantile(v, q)) for q in (0.5, 0.99, 1.0)} for nm, v in ref_lead.items()}),
           G1=dict(seed=6302, nulls=NFPR, share_padj_le_alpha=FPR, p_adj=fpr_p, passed=G1),
           G2=dict(seed=6303, plants=NPL, power=POWER, wilson95=wilson(sum(x['hit'] for x in pl), NPL),
                   W_quantiles={q: float(np.quantile([x['W'] for x in pl], q)) for q in (0.05, 0.2, 0.5, 0.8)},
                   K_counts={int(k): int(v) for k, v in Counter(x['K'] for x in pl).items()}, passed=G2), fixtures=fx)
if G0 and A0 and G1 and G2 and MODE == 'full':
    W, I, J, K = wham(cs); top = sorted(range(MF), key=lambda k: -W[k])[:10]; H = {}
    for nm, ix in LK.items():
        a, b = FAM[ix]; w_obs = float(W[ix]); k_obs = int(K[ix])
        seg_a = [int(x) for x in cs[a][max(I[ix], 0):max(I[ix], 0) + k_obs + 2]]; seg_b = [int(x) for x in cs[b][max(J[ix], 0):max(J[ix], 0) + k_obs + 2]]
        H[nm] = dict(W_obs=w_obs, K_obs=k_obs, p_adj=padj(w_obs), p_pair_alone_selected=float((1 + (np.array(ref_lead[nm]) >= w_obs - EPS).sum()) / (1 + RREF)),
                     segment_a=seg_a, segment_b=seg_b, verdict=('CONFIRMED (post-selection, family-adjusted)' if padj(w_obs) <= ALPHA else 'NOT CONFIRMED'))
    out['H1'] = dict(run=True, leads=H, real_family_max=float(W.max()),
                     real_top10=[dict(a=meta[ids[FAM[k][0]]]['okr'], b=meta[ids[FAM[k][1]]]['okr'], W=float(W[k]), K=int(K[k]), p_adj=padj(float(W[k]))) for k in top])
else:
    out['H1'] = dict(run=False, reason=('gate failed' if MODE == 'full' else 'gates mode'),
                     verdict=('NOT TESTABLE (power)' if (G0 and A0 and G1 and not G2) else 'EXCLUDED (tool/audit)' if not (G0 and A0 and G1) else 'not run'))
out['seconds'] = round(time.time() - t0, 1)
json.dump(out, open(OUT, 'w'), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k not in ('fixtures',)}, default=float)[:5000])
