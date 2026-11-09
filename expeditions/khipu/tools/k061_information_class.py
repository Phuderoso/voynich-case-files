#!/usr/bin/env python3
"""K061 - line 3, option (b) of K060: power of the K060 within-provenance scan (F_prov, K012 Poisson p, BH q = 0.05 over 4 039 pairs)
against 6-cord planted copies CONDITIONED ON INFORMATION CONTENT: class D_d = source window has >= d distinct non-zero values
(d in {4, 5, 6}; K060 plant design otherwise verbatim: >= 5 of 6 non-zero, pair uniform in F_prov, random direction, raw copy).
Gates: G0 brute-force fixture of the K012 longest-block statistic and of the class filter (seed 6164, 20 corpora);
audit = G1 of K060 re-run verbatim (seed 6060, 40 run-preserving nulls: 0/40, pair share 0.00045) and K012 audit (5 323 / 6);
G2 power curve: 200 plants per class, seeds 6161 (d4), 6162 (d5), 6163 (d6). Readable class d* = smallest d with power >= 0.80.
Observed within-family scan (H1) only if G0, G1 pass and d* exists. Pre-registered in case-file/K061-information-class-plants.md.
Usage: python3 tools/k061_information_class.py data/khipu.db full"""
import sqlite3, json, sys, time, math, itertools, os, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); MODE = sys.argv[2] if len(sys.argv) > 2 else 'gates'
c = sqlite3.connect(sys.argv[1]); CAP = 300; Q = 0.05
NNULL, NPL = (int(x) for x in os.environ.get('K061_SMOKE', '40,200').split(','))  # smoke override for timing only
OUT = 'analysis/k061_results.json' if 'K061_SMOKE' not in os.environ else '/tmp/k061/smoke.json'
rng_null = np.random.default_rng(6060); rng_fx = np.random.default_rng(6164)
SEEDS = {4: 6161, 5: 6162, 6: 6163}
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
def bh(P, MM=None):
    MM = M if MM is None else MM
    items = sorted(P.items(), key=lambda kv: kv[1]); k = 0
    for r, (key, p) in enumerate(items, 1):
        if p <= r * Q / MM: k = r
    return {key for key, p in items[:k]}

def ndistinct(w): return len({int(x) for x in w if x > 0})
# ---------------- G0 fixture: brute force for longest() and the class filter ----------------
def brute_longest(S):
    best = {}
    for a in range(len(S)):
        for b in range(a + 1, len(S)):
            A, B = S[a], S[b]; m = 0
            for i in range(len(A)):
                for j in range(len(B)):
                    L = 0
                    while i + L < len(A) and j + L < len(B) and A[i + L] == B[j + L] and A[i + L] > 0: L += 1
                    m = max(m, L)
            if m >= 3: best[(a, b)] = m
    return best
fx = []
for t in range(20):
    S = []
    for _ in range(int(rng_fx.integers(3, 7))):
        s = rng_fx.integers(0, 4, int(rng_fx.integers(6, 16))); S.append(collapse(s)[0])
    # force at least one shared block so the fixture is not trivially empty
    a, b = 0, 1; L = min(4, len(S[a]), len(S[b]))
    if L >= 3: S[b] = np.concatenate([S[b], S[a][:L]]); S[b] = collapse(S[b])[0]
    got = {k: v[0] for k, v in longest(S).items()}; want = brute_longest(S)
    w = rng_fx.integers(0, 5, 6); nd_b = len(set(int(x) for x in w) - {0})
    fx.append(dict(sizes=[len(x) for x in S], pairs=len(want), ok_longest=got == want, ok_class=ndistinct(w) == nd_b))
G0 = all(x['ok_longest'] and x['ok_class'] for x in fx); log('G0 fixture', sum(x['ok_longest'] and x['ok_class'] for x in fx), '/ 20')
CL = [collapse(x) for x in seqs]; cs = [x[0] for x in CL]
# ---------------- family F_prov from metadata only ----------------
prov = {r[0]: (r[1] or '').strip().casefold() for r in c.execute("select KHIPU_ID, PROVENANCE from khipu_main")}
grp = defaultdict(list)
for k, kid in enumerate(ids):
    p = prov.get(kid, '')
    if p and p != 'unknown': grp[p].append(k)
FAM = {(a, b) for g in grp.values() for x, a in enumerate(g) for b in g[x + 1:]}
FAM = {(min(a, b), max(a, b)) for a, b in FAM}; MF = len(FAM); FAMPAIRS = sorted(FAM)
log('family F_prov', MF, 'pairs in', len(grp), 'provenances')
def fam(P): return {k: v for k, v in P.items() if k in FAM}

best_real = longest(cs)
Pk = pvals_k012(cs, best_real); audit = dict(real_blocks=len(best_real), k012_discoveries=len(bh(Pk)), published_blocks=5323, published_discoveries=6)
audit['reproduced'] = audit['real_blocks'] == 5323 and audit['k012_discoveries'] == 6; log('audit K012', audit)
# ---------------- G1 = audit of K060 G1 (verbatim, seed 6060) ----------------
anyd, small, ndisc = 0, 0, []
for r in range(NNULL):
    Sx = [collapse(runperm(k, rng_null))[0] for k in range(N)]; best = longest(Sx)
    Pk_ = fam(pvals_k012(Sx, best)); D = bh(Pk_, MF); anyd += bool(D); ndisc.append(len(D)); small += sum(p < 0.01 for p in Pk_.values())
    if r % 10 == 9: log('null', r + 1, anyd)
FPR_any = anyd / NNULL; share001 = small / (NNULL * MF); G1 = bool(FPR_any <= 0.10 and share001 <= 0.01)
K060_G1 = dict(any_discovery=0.0, share_p_lt_001=0.0004456548650656103)
g1_repro = bool(FPR_any == K060_G1['any_discovery'] and abs(share001 - K060_G1['share_p_lt_001']) < 1e-12)
# ---------------- coverage (descriptive): eligible source windows in family khipus, real sequences ----------------
famk = sorted({x for p in FAMPAIRS for x in p}); cov = Counter(); tot = 0
for k in famk:
    s = seqs[k]
    for i in range(len(s) - 5):
        w = s[i:i + 6]
        if (w > 0).sum() >= 5: tot += 1; cov[ndistinct(w)] += 1
coverage = {d: (sum(v for kk, v in cov.items() if kk >= d) / tot if tot else None) for d in (4, 5, 6)}
# ---------------- G2 power curve by information class ----------------
def plant(rng, d, length=6):
    Sx = [runperm(k, rng) for k in range(N)]; tries = 0
    while True:
        tries += 1
        a, b = FAMPAIRS[int(rng.integers(0, MF))]
        if rng.random() < 0.5: a, b = b, a
        sa = Sx[a]
        st = [i for i in range(len(sa) - length + 1) if (sa[i:i + length] > 0).sum() >= length - 1 and ndistinct(sa[i:i + length]) >= d]
        if st and len(Sx[b]) >= length + 2: break
    i = int(rng.choice(st)); j = int(rng.integers(0, len(Sx[b]) - length + 1)); Sx[b] = Sx[b].copy(); Sx[b][j:j + length] = sa[i:i + length]
    w = sa[i:i + length]
    Sx = [collapse(x)[0] for x in Sx]; best = longest(Sx); k = (min(a, b), max(a, b))
    Pk_ = fam(pvals_k012(Sx, best))
    return dict(hit=bool(k in bh(Pk_, MF)), p=float(Pk_.get(k, 1.0)), prov=prov[ids[a]], nd=ndistinct(w), tries=tries)
def wilson(x, n, z=1.959964):
    ph = x / n; den = 1 + z * z / n; ctr = (ph + z * z / (2 * n)) / den; hw = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return [ctr - hw, ctr + hw]
curve = {}
for d in (4, 5, 6):
    rng = np.random.default_rng(SEEDS[d]); rr = []
    for t in range(NPL):
        rr.append(plant(rng, d))
        if t % 50 == 49: log('plant d>=%d' % d, t + 1)
    ps = np.sort([x['p'] for x in rr]); q80 = float(ps[int(math.ceil(0.8 * len(ps))) - 1]); x = sum(r['hit'] for r in rr)
    cells = {}
    for pv in sorted({r['prov'] for r in rr}):
        xs = [r for r in rr if r['prov'] == pv]
        if len(xs) >= 30: cells[pv] = dict(plants=len(xs), power=float(np.mean([r['hit'] for r in xs])))
    curve[d] = dict(seed=SEEDS[d], plants=NPL, power=x / NPL, wilson95=wilson(x, NPL), median_p=float(np.median(ps)), p_80th_pct=q80,
                    M_star_descriptive=(int(Q / q80) if q80 > 0 else None), cells_ge30=cells,
                    power_by_exact_nd={int(n): float(np.mean([r['hit'] for r in rr if r['nd'] == n])) for n in sorted({r['nd'] for r in rr})},
                    n_by_exact_nd={int(n): sum(r['nd'] == n for r in rr) for n in sorted({r['nd'] for r in rr})})
    log('class d>=%d power' % d, curve[d]['power'])
DSTAR = next((d for d in (4, 5, 6) if curve[d]['power'] >= 0.80), None)
out = dict(N=N, family=dict(name='F_prov', pairs=MF, provenances=len(grp)), G0_fixture=G0, G0_fixture_n=sum(x['ok_longest'] and x['ok_class'] for x in fx),
           audit_K012=audit, G1=dict(null_corpora=NNULL, any_discovery=FPR_any, mean_discoveries=float(np.mean(ndisc)), share_p_lt_001=share001,
           passed=G1, K060_G1_reproduced=g1_repro), coverage_real_windows=dict(eligible_windows=tot, share_ge_d=coverage, by_nd=dict(cov)),
           G2_curve=curve, d_star=DSTAR, fixtures=fx)
KNOWN = {frozenset(x) for x in [('KH0362', 'KH0049'), ('KH0128', 'KH0137'), ('KH0140', 'KH0483'), ('KH0240', 'KH0496'), ('KH0304', 'KH0303'), ('KH0284', 'KH0285')]}  # K012's six discoveries
if G0 and G1 and DSTAR is not None and MODE == 'full':
    P = fam(pvals_k012(cs, best_real)); D = bh(P, MF); rows = []
    for key in sorted(D, key=lambda k: P[k]):
        a, b = key; L, i, j = best_real[key]
        rows.append(dict(a=meta[ids[a]]['okr'], a_inv=meta[ids[a]]['inv'], b=meta[ids[b]]['okr'], b_inv=meta[ids[b]]['inv'], prov=prov[ids[a]], L=L, p=P[key],
                         block=[int(x) for x in cs[a][i:i + L]], nd_block=ndistinct(cs[a][i:i + L]),
                         known_k012=frozenset((meta[ids[a]]['okr'], meta[ids[b]]['okr'])) in KNOWN))
    out['H1'] = dict(run=True, scope='F_prov; silence readable only for 6-cord copies of class d >= %d' % DSTAR, discoveries=rows,
                     n_family_pairs_with_block=len(P))
else:
    out['H1'] = dict(run=False, reason='gate failed (NOT TESTABLE / EXCLUDED per rule)' if MODE == 'full' else 'gates mode')
out['seconds'] = round(time.time() - t0, 1)
json.dump(out, open(OUT, 'w'), indent=1, default=float)
print(json.dumps({k: v for k, v in out.items() if k not in ('fixtures',)}, indent=1, default=float))
