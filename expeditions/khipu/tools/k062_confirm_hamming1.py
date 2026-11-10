#!/usr/bin/env python3
"""K062 part 2 - pre-registered, POST-SELECTION confirmation of the K061 lead KH0132 (UR1118) . KH0456 (UR218) with a
one-cord-tolerant statistic and a selection-adjusted null.
Statistic T(pair) = longest aligned run (same offset on both run-collapsed level-1 sequences, K012 corpus and R5 mask) that
contains at most ONE non-matching position; T counts the matching positions (match = equal and > 0). C kernel tools/k062_hamming1.c.
Selection adjustment: single-step max-T over the whole K060/K061 family F_prov (4 039 within-provenance pairs):
p_adj = (1 + #{reference nulls whose family max T >= T_obs}) / (1 + R). The pair was selected by K061 inside F_prov with the exact
statistic, so p_adj is valid whichever pair of F_prov had been picked. Alpha 0.025 = 0.05 / 2 (tolerances {0, 1}; tolerance 1
was suggested by K061's post-hoc look, disclosed).
Null: K012/K061 within-khipu run permutation of raw level-1 sequences, then run-collapse (K061 verbatim).
Gates: G0 brute-force fixture (seed 6204, 20 corpora); audit of K061 (5 within-family discoveries and the pair's p 4.86699140653952e-06);
G1 FPR on 40 fresh nulls (seed 6202): share of corpora whose own family max reaches p_adj <= 0.025 must be <= 0.10;
G2 power (seed 6203, 200 plants): 8-cord near-copies (source window 8 non-zero, 8 distinct values, one interior cord altered by
delta in {-3..-1, 1..3}), planted in a random F_prov pair; recovered iff the planted pair's p_adj <= 0.025; power >= 0.80 else NOT TESTABLE.
Reference null R = 1000 (seed 6201). Usage: python3 tools/k062_confirm_hamming1.py data/khipu.db full   [gates = no observed T]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sqlite3, json, sys, time, math, os, ctypes, hashlib, subprocess, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); MODE = sys.argv[2] if len(sys.argv) > 2 else 'gates'
SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
if hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest() != SHA: sys.exit('EXCLUDED: khipu.db hash differs from MANIFEST')
c = sqlite3.connect('file:' + sys.argv[1] + '?mode=ro', uri=True); CAP = 300; Q = 0.05; ALPHA = 0.025
RREF, NFPR, NPL = (int(x) for x in os.environ.get('K062_SMOKE', '1000,40,200').split(','))
OUT = 'analysis/k062_confirm_results.json' if 'K062_SMOKE' not in os.environ else '/tmp/k062/smoke.json'
HERE = os.path.dirname(os.path.abspath(__file__)); SO = '/tmp/k062/k062_hamming1.so'; os.makedirs('/tmp/k062', exist_ok=True)
subprocess.run(['cc', '-O2', '-shared', '-fPIC', '-o', SO, os.path.join(HERE, 'k062_hamming1.c')], check=True)
lib = ctypes.CDLL(SO); P64 = np.ctypeslib.ndpointer(np.int64, flags='C_CONTIGUOUS')
lib.ham1.argtypes = [P64, P64, P64, P64, ctypes.c_int64, P64, P64, P64]
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
TA, TB = okr2k['KH0132'], okr2k['KH0456']; TKEY = (min(TA, TB), max(TA, TB)); TIDX = FAM.index(TKEY)
log('N', N, 'family', MF, 'target index', TIDX)
def ham(S, pa=PA, pb=PB):
    off = np.zeros(len(S) + 1, np.int64); off[1:] = np.cumsum([len(s) for s in S]); cat = np.ascontiguousarray(np.concatenate(S).astype(np.int64))
    n = len(pa); T = np.zeros(n, np.int64); I = np.zeros(n, np.int64); J = np.zeros(n, np.int64)
    lib.ham1(cat, off, np.ascontiguousarray(pa), np.ascontiguousarray(pb), n, T, I, J); return T, I, J
# ---------------- G0 brute-force fixture ----------------
def brute_T(A, B):
    best = 0
    for d in range(-(len(B) - 1), len(A)):
        pos = [(i, i - d) for i in range(len(A)) if 0 <= i - d < len(B)]
        m = [A[i] == B[j] and A[i] > 0 for i, j in pos]
        for s in range(len(m)):
            for e in range(s, len(m)):
                seg = m[s:e + 1]
                if len(seg) - sum(seg) <= 1: best = max(best, sum(seg))
    return best
rng_fx = np.random.default_rng(6204); fx = []
for t in range(20):
    S = [collapse(rng_fx.integers(0, 4, int(rng_fx.integers(5, 15))).astype(np.int64)) for _ in range(int(rng_fx.integers(3, 6)))]
    pa = np.array([a for a in range(len(S)) for b in range(a + 1, len(S))], np.int64); pb = np.array([b for a in range(len(S)) for b in range(a + 1, len(S))], np.int64)
    got = ham(S, pa, pb)[0].tolist(); want = [brute_T(S[a], S[b]) for a, b in zip(pa, pb)]
    fx.append(dict(pairs=len(want), ok=got == want, max_T=max(want)))
G0 = all(x['ok'] for x in fx); log('G0', sum(x['ok'] for x in fx), '/ 20')
# ---------------- audit of K061 (real exact scan inside F_prov) ----------------
def longest(S):  # K012 verbatim
    idx = defaultdict(list)
    for a, s in enumerate(S):
        for i in range(len(s) - 2):
            if s[i] > 0 and s[i + 1] > 0 and s[i + 2] > 0: idx[(s[i], s[i + 1], s[i + 2])].append((a, i))
    best = {}
    for g, occ in idx.items():
        if len(occ) > CAP or len(occ) < 2: continue
        for x in range(len(occ)):
            a, i = occ[x]
            for y in range(x + 1, len(occ)):
                b, j = occ[y]
                if a == b: continue
                sa, sb = S[a], S[b]
                if i > 0 and j > 0 and sa[i - 1] == sb[j - 1] and sa[i - 1] > 0: continue
                L = 3
                while i + L < len(sa) and j + L < len(sb) and sa[i + L] == sb[j + L] and sa[i + L] > 0: L += 1
                key = (a, b) if a < b else (b, a); ia, ib = (i, j) if a < b else (j, i)
                if L > best.get(key, (0,))[0]: best[key] = (L, ia, ib)
    return best
def pvals_k012(S, best):
    P = {}; dist = [Counter(int(x) for x in s) for s in S]
    for (a, b), (L, i, j) in best.items():
        na, nb = len(S[a]), len(S[b]); da, db = dist[a], dist[b]
        q = sum((k / na) * (db[v] / nb) for v, k in da.items() if v > 0 and v in db)
        P[(a, b)] = -math.expm1(-(1 - q) * q ** L * (na - L + 1) * (nb - L + 1))
    return P
def bh(P, MM):
    items = sorted(P.items(), key=lambda kv: kv[1]); k = 0
    for r, (key, p) in enumerate(items, 1):
        if p <= r * Q / MM: k = r
    return {key for key, p in items[:k]}
cs = [collapse(s) for s in seqs]; FAMS = set(FAM)
Pf = {k: v for k, v in pvals_k012(cs, longest(cs)).items() if k in FAMS}; D = bh(Pf, MF)
k61 = json.load(open('analysis/k061_results.json'))['H1']['discoveries']
want = {frozenset((r['a'], r['b'])): r['p'] for r in k61}; got = {frozenset((meta[ids[a]]['okr'], meta[ids[b]]['okr'])): Pf[(a, b)] for a, b in D}
audit = dict(k061_discoveries=len(want), reproduced_discoveries=len(got), same_set=set(want) == set(got),
             target_p=Pf.get(TKEY), target_p_published=4.86699140653952e-06)
audit['reproduced'] = bool(audit['same_set'] and abs(audit['target_p'] / audit['target_p_published'] - 1) < 1e-9
                           and all(abs(got[k] / want[k] - 1) < 1e-9 for k in want)); log('audit K061', audit['reproduced'])
# ---------------- reference null (seed 6201) ----------------
rng = np.random.default_rng(6201); ref_max = []; ref_target = []
for r in range(RREF):
    Sx = [collapse(runperm(k, rng)) for k in range(N)]; T = ham(Sx)[0]; ref_max.append(int(T.max())); ref_target.append(int(T[TIDX]))
    if r % 200 == 199: log('ref', r + 1)
ref_max = np.array(ref_max); ref_target = np.array(ref_target)
def padj(t): return float((1 + (ref_max >= t).sum()) / (1 + RREF))
# ---------------- G1 FPR on fresh nulls (seed 6202) ----------------
rng = np.random.default_rng(6202); fpr_p = []
for r in range(NFPR):
    Sx = [collapse(runperm(k, rng)) for k in range(N)]; fpr_p.append(padj(int(ham(Sx)[0].max())))
FPR = float(np.mean([p <= ALPHA for p in fpr_p])); G1 = bool(FPR <= 0.10); log('G1 FPR', FPR)
# ---------------- G2 power (seed 6203) ----------------
rng = np.random.default_rng(6203); pl = []; DELTAS = np.array([-3, -2, -1, 1, 2, 3])
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
    Cx = [collapse(x) for x in Sx]; T = int(ham(Cx, np.array([min(a, b)], np.int64), np.array([max(a, b)], np.int64))[0][0])
    pl.append(dict(T=T, p_adj=padj(T), hit=padj(T) <= ALPHA, prov=prov[ids[a]], tries=tries))
    if t % 50 == 49: log('plant', t + 1)
POWER = float(np.mean([x['hit'] for x in pl])); G2 = bool(POWER >= 0.80); log('G2 power', POWER)
def wilson(x, n, z=1.959964):
    ph = x / n; den = 1 + z * z / n; ctr = (ph + z * z / (2 * n)) / den; hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [ctr - hw, ctr + hw]
qs = {str(t): float((ref_max >= t).mean()) for t in range(int(ref_max.min()), int(ref_max.max()) + 2)}
out = dict(N=N, family_pairs=MF, target=dict(a='KH0132', b='KH0456', fam_index=TIDX), alpha=ALPHA, G0_fixture=G0, G0_n=sum(x['ok'] for x in fx),
           audit_K061=audit, reference=dict(R=RREF, seed=6201, max_T_counts={int(k): int(v) for k, v in Counter(ref_max.tolist()).items()},
           survival=qs, target_T_counts={int(k): int(v) for k, v in Counter(ref_target.tolist()).items()}),
           G1=dict(seed=6202, nulls=NFPR, share_padj_le_alpha=FPR, p_adj=fpr_p, passed=G1),
           G2=dict(seed=6203, plants=NPL, power=POWER, wilson95=wilson(sum(x['hit'] for x in pl), NPL), T_counts={int(k): int(v) for k, v in Counter(x['T'] for x in pl).items()}, passed=G2),
           fixtures=fx)
if G0 and audit['reproduced'] and G1 and G2 and MODE == 'full':
    T, I, J = ham(cs); t_obs = int(T[TIDX]); a, b = TKEY
    seg_a = [int(x) for x in cs[a][I[TIDX]:I[TIDX] + t_obs + 1]]; seg_b = [int(x) for x in cs[b][J[TIDX]:J[TIDX] + t_obs + 1]]
    top = sorted(range(MF), key=lambda k: -T[k])[:10]
    out['H1'] = dict(run=True, T_obs=t_obs, p_adj=padj(t_obs), p_pair_alone_selected=float((1 + (ref_target >= t_obs).sum()) / (1 + RREF)),
                     segment_a=seg_a, segment_b=seg_b, verdict=('CONFIRMED (post-selection, family-adjusted)' if padj(t_obs) <= ALPHA else 'NOT CONFIRMED'),
                     real_family_max=int(T.max()), real_top10=[dict(a=meta[ids[FAM[k][0]]]['okr'], b=meta[ids[FAM[k][1]]]['okr'], T=int(T[k]), p_adj=padj(int(T[k]))) for k in top])
else:
    out['H1'] = dict(run=False, reason=('gate failed' if MODE == 'full' else 'gates mode'),
                     verdict=('NOT TESTABLE (power)' if (G0 and G1 and not G2) else 'EXCLUDED (tool)' if not (G0 and G1) else 'not run'))
out['seconds'] = round(time.time() - t0, 1)
json.dump(out, open(OUT, 'w'), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k not in ('fixtures',)}, default=float)[:4000])
