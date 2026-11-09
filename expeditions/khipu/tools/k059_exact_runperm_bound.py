#!/usr/bin/env python3
"""K059 - exact first-moment (declumped Markov) bound for the longest shared run-collapsed block, per pair, + BH.
Pre-registered in case-file/K059-exact-collapsed-block-bound.md.

Statistic (as K012): L_ab = longest aligned block of equal non-zero symbols between collapsed sequences a and b
(from shared 3-symbol seeds, seed cap 300, as K012).
Null for the per-pair p (exact): b's collapsed symbols uniformly permuted (no re-collapse), a fixed.
E_ab(L) = exact expected number of LEFT-MAXIMAL matches of length >= L
        = (n_b-L+1) * sum_i P_L(w_i) - (n_b-L) * sum_i P_{L+1}(w'_i),
  P_L(w) = prod_v (c_v)_(m_v) / (n_b)_L  (falling factorials; c_v = count of v among b's symbols).
P(L_ab >= L) <= E_ab(L)  (Markov on the count of left-maximal matches) -> valid conservative p.
p_ab = min(1, 2*min(E_ab, E_ba)) (Bonferroni over the two directions).
Usage: python3 tools/k059_exact_runperm_bound.py data/khipu.db MODE   (MODE = gates | full)"""
import sqlite3, json, sys, time, math, itertools, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); MODE = sys.argv[2] if len(sys.argv) > 2 else 'gates'
c = sqlite3.connect(sys.argv[1]); CAP = 300; Q = 0.05
import os
NNULL, NP6, NP8 = (int(x) for x in os.environ.get('K059_SMOKE', '40,200,100').split(','))  # smoke override only for timing; registered run uses defaults
rng_null = np.random.default_rng(5959); rng_p6 = np.random.default_rng(5960); rng_p8 = np.random.default_rng(5961); rng_fx = np.random.default_rng(5962)
def log(*a): print(*a, round(time.time() - t0, 1), flush=True)
# ---------------- data exactly as K012 ----------------
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
meta = {r[0]: dict(okr=r[1] or '', inv=r[2] or '', museum=(r[3] or '').strip(), mnum=(r[4] or '').strip())
        for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM, MUSEUM_NAME, MUSEUM_NUM from khipu_main")}
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
    b = np.flatnonzero(np.diff(s) != 0) + 1; st = np.concatenate([[0], b]); ln = np.diff(np.concatenate([st, [len(s)]]))
    return s[st], ln
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
def pvals_k012(S, best):  # K012 Poisson, verbatim (audit + head-to-head)
    P = {}; dist = [Counter(int(x) for x in s) for s in S]
    for (a, b), (L, i, j) in best.items():
        na, nb = len(S[a]), len(S[b]); da, db = dist[a], dist[b]
        q = sum((k / na) * (db[v] / nb) for v, k in da.items() if v > 0 and v in db)
        lam = (1 - q) * q ** L * (na - L + 1) * (nb - L + 1)
        P[(a, b)] = -math.expm1(-lam)
    return P
def bh(P):
    items = sorted(P.items(), key=lambda kv: kv[1]); k = 0
    for r, (key, p) in enumerate(items, 1):
        if p <= r * Q / M: k = r
    return {key for key, p in items[:k]}
# ---------------- exact bound ----------------
def winfo(A, L):
    """windows of length L with all symbols > 0: symbols W (m x L) and occurrences-before O (m x L)"""
    if len(A) < L: return None
    Ws, Os = [], []
    for i in range(len(A) - L + 1):
        w = A[i:i + L]
        if (w > 0).all():
            seen = Counter(); o = []
            for x in w: o.append(seen[int(x)]); seen[int(x)] += 1
            Ws.append(w); Os.append(o)
    if not Ws: return None
    return np.array(Ws), np.array(Os, np.int64)
def sumP(wi, cnt, n, L):
    if wi is None or n < L: return 0.0
    W, O = wi; num = np.array([cnt.get(int(x), 0) for x in W.ravel()], np.float64).reshape(W.shape) - O
    num = np.clip(num, 0, None) / (n - np.arange(L))
    return float(np.prod(num, axis=1).sum())
class Corpus:
    def __init__(s, S): s.S = S; s.cnt = [Counter(int(x) for x in q) for q in S]; s.cache = {}
    def wi(s, a, L):
        k = (a, L)
        if k not in s.cache: s.cache[k] = winfo(s.S[a], L)
        return s.cache[k]
    def E(s, a, b, L):  # a fixed, b permuted
        n = len(s.S[b]); cb = s.cnt[b]
        return (n - L + 1) * sumP(s.wi(a, L), cb, n, L) - ((n - L) * sumP(s.wi(a, L + 1), cb, n, L + 1) if n >= L + 1 else 0.0)
def pvals_exact(S, best):
    C = Corpus(S); P = {}
    for (a, b), (L, i, j) in best.items():
        e = min(C.E(a, b, L), C.E(b, a, L)); P[(a, b)] = min(1.0, 2 * max(e, 0.0))
    return P
# ---------------- G0 fixture: brute force over all permutations ----------------
def lm_count(A, B, L):
    cnt = 0
    for i in range(len(A) - L + 1):
        for j in range(len(B) - L + 1):
            if all(A[i + t] == B[j + t] and A[i + t] > 0 for t in range(L)) and (i == 0 or j == 0 or A[i - 1] != B[j - 1] or A[i - 1] <= 0): cnt += 1
    return cnt
fx = []
for t in range(20):
    A = rng_fx.integers(0, 3, int(rng_fx.integers(4, 9))); B = rng_fx.integers(0, 3, int(rng_fx.integers(3, 8))); L = int(rng_fx.integers(1, 4))
    perms = list(itertools.permutations(B.tolist())); brute = np.mean([lm_count(A, np.array(p), L) for p in perms])
    C = Corpus([A, B]); f = C.E(0, 1, L); fx.append(dict(A=A.tolist(), B=B.tolist(), L=L, brute=float(brute), formula=f, ok=bool(abs(brute - f) < 1e-9)))
G0 = all(x['ok'] for x in fx); log('G0 fixture', sum(x['ok'] for x in fx), '/ 20')
CL = [collapse(x) for x in seqs]; cs = [x[0] for x in CL]
# G0b 'meter honesty' (borrowed from Kryptos c189): exact E vs Monte Carlo mean of left-maximal counts on 30 real pairs
best_real = longest(cs); keys = sorted(best_real)
pick = [keys[k] for k in rng_fx.choice(len(keys), 30, replace=False)]
Cr = Corpus(cs); zs = []
for (a, b) in pick:
    L = 3; e = Cr.E(a, b, L); sims = [lm_count(cs[a], rng_fx.permutation(cs[b]), L) for _ in range(300)]
    m, sd = float(np.mean(sims)), float(np.std(sims, ddof=1)) / math.sqrt(300)
    zs.append(dict(pair=[ids[a], ids[b]], E=e, mc=m, z=(m - e) / sd if sd > 0 else 0.0))
zabs = [abs(z['z']) for z in zs]; G0b = bool(sum(z > 3 for z in zabs) == 0 and abs(sum(z['mc'] for z in zs) / max(1e-12, sum(z['E'] for z in zs)) - 1) < 0.05)
log('G0b meter', G0b, 'max|z|', round(max(zabs), 2))
# ---------------- audit: K012 real discoveries (published 6, 5323 blocks) ----------------
Pk = pvals_k012(cs, best_real); audit = dict(real_blocks=len(best_real), k012_discoveries=len(bh(Pk)), published_blocks=5323, published_discoveries=6)
audit['reproduced'] = audit['real_blocks'] == 5323 and audit['k012_discoveries'] == 6; log('audit K012', audit)
# ---------------- G1 FPR on run-preserving null corpora (K012 null) ----------------
anyd, small, ndisc = 0, 0, []
for r in range(NNULL):
    Sx = [collapse(runperm(k, rng_null))[0] for k in range(N)]; P = pvals_exact(Sx, longest(Sx)); D = bh(P)
    anyd += bool(D); ndisc.append(len(D)); small += sum(p < 0.01 for p in P.values())
    if r % 10 == 9: log('null', r + 1, anyd)
FPR_any = anyd / NNULL; share001 = small / (NNULL * M); G1 = bool(FPR_any <= 0.10 and share001 <= 0.01)
# ---------------- G2 power with planted raw-cord copies (K012 plant design) ----------------
def plant(rng, length):
    Sx = [runperm(k, rng) for k in range(N)]
    while True:
        a, b = (int(x) for x in rng.choice(N, 2, replace=False)); sa = Sx[a]
        st = [i for i in range(len(sa) - length + 1) if (sa[i:i + length] > 0).sum() >= length - 1]
        if st and len(Sx[b]) >= length + 2: break
    i = int(rng.choice(st)); j = int(rng.integers(0, len(Sx[b]) - length + 1)); Sx[b] = Sx[b].copy(); Sx[b][j:j + length] = sa[i:i + length]
    Sx = [collapse(x)[0] for x in Sx]; best = longest(Sx); k = (min(a, b), max(a, b))
    Pe, Pk_ = pvals_exact(Sx, best), pvals_k012(Sx, best)
    return k in bh(Pe), k in bh(Pk_), Pe.get(k, 1.0)
r6 = []
for t in range(NP6):
    r6.append(plant(rng_p6, 6))
    if t % 50 == 49: log('plant6', t + 1, np.mean([x[0] for x in r6]), np.mean([x[1] for x in r6]))
r8 = []
for t in range(NP8):
    r8.append(plant(rng_p8, 8))
    if t % 50 == 49: log('plant8', t + 1, np.mean([x[0] for x in r8]), np.mean([x[1] for x in r8]))
pow6 = float(np.mean([x[0] for x in r6])); pow6_k012 = float(np.mean([x[1] for x in r6]))
pow8 = float(np.mean([x[0] for x in r8])); pow8_k012 = float(np.mean([x[1] for x in r8]))
G2 = pow6 >= 0.80
# H2 McNemar (exact one-sided binomial on discordant plants at 6): exact bound beats K012 Poisson?
bE = sum(1 for x in r6 if x[0] and not x[1]); bK = sum(1 for x in r6 if x[1] and not x[0]); nd = bE + bK
pmc = float(sum(math.comb(nd, k) for k in range(bE, nd + 1)) / 2 ** nd) if nd else 1.0
out = dict(N=N, M=M, G0_fixture=G0, G0_fixture_n=sum(x['ok'] for x in fx), G0b_meter=G0b, G0b_max_abs_z=max(zabs), audit_K012=audit,
           G1=dict(null_corpora=NNULL, any_discovery=FPR_any, mean_discoveries=float(np.mean(ndisc)), share_p_lt_001=share001, passed=G1),
           G2=dict(plants6=NP6, power6_exact=pow6, power6_k012=pow6_k012, plants8=NP8, power8_exact=pow8, power8_k012=pow8_k012,
                   median_p6_exact=float(np.median([x[2] for x in r6])), passed=G2),
           H2_mcnemar=dict(exact_only=bE, k012_only=bK, p_one_sided=pmc),
           fixtures=fx, meter=zs)
if G0 and G1 and G2 and MODE == 'full':
    Pe = pvals_exact(cs, best_real); D = bh(Pe); rows = []
    for key in sorted(D, key=lambda k: Pe[k]):
        a, b = key; L, i, j = best_real[key]
        rows.append(dict(a=meta[ids[a]]['okr'], b=meta[ids[b]]['okr'], L=L, p=Pe[key], block=[int(x) for x in cs[a][i:i + L]]))
    out['H1'] = dict(run=True, discoveries=rows)
else:
    out['H1'] = dict(run=False, reason='gate failed (NOT TESTABLE / EXCLUDED per rule)' if MODE == 'full' else 'gates mode')
out['seconds'] = round(time.time() - t0, 1)
json.dump(out, open('analysis/k059_results.json' if 'K059_SMOKE' not in os.environ else '/tmp/k059_smoke.json', 'w'), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k not in ('fixtures', 'meter')}, indent=1, default=float))
