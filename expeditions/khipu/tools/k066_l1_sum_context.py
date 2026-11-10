#!/usr/bin/env python3
"""K066 - pre-registered test: does the K065-confirmed cross-site segment L1 (KH0143.KH0591, `226 115 124 200|357 161`) sit inside
K001-style adjacent summing structure in either khipu, more than a within-khipu permutation predicts?
Data: OKR khipu.db (sha256 in MANIFEST), K064 level-1 pipeline verbatim (duplicates out, R5 mask -> 0), UNcollapsed level-1 order.
Segment S = the 5 aligned positions in each khipu (226, 115, 124, 200|357, 161), 10 positions in total.
Sum relation (K001 verbatim): a level-1 cord c with value v >= 10 such that, for some k in 2..12, the k cords immediately to the right,
or immediately to the left, sum to v with at least 2 of them nonzero. A position is SUM-INVOLVED if it is such a total, or lies inside
(and is nonzero within) such a summing window of some total.
H1 (primary): T = number of sum-involved positions among the 10 segment positions. Null N1 (K001): permute each khipu's level-1 value
vector independently (R 5000, seed 6409); p = (1 + #{T_null >= T_obs}) / (1 + R); SUPPORTED iff p <= 0.05.
Gates: G1 FPR (seed 6410): 200 N1 permutations treated as observed, share with p <= 0.05 must be <= 0.10.
G2 power (seed 6411): 200 plants; in an N1 permutation of each khipu, one segment position per khipu (uniform among positions with
3 cords to its right) is overwritten with the sum of the next 3 cords, which are first forced nonzero by drawing from that khipu's
nonzero values if needed, and must reach >= 10 (else redraw); recovered iff p <= 0.05; power >= 0.80 else NOT TESTABLE.
Blind-spot count (I-228, Kryptos): plants that leave T unchanged are reported.
A1 audit of K065: K065's tool re-run in smoke mode at registered size must reproduce analysis/k065_results.json exactly (done by the runner).
H2 (secondary, exploratory, DISCLOSED-MOTIVATED: the raw values were looked at before registration and a 55 at offset -4 in both khipus
was noticed): F = sum of K064 full-corpus weights of exact nonzero matches on the L1 diagonal of the COLLAPSED sequences, outside the
segment and its two immediate neighbours. Null: uniform permutation of KH0591's collapsed tokens outside that block (KH0143 fixed),
R 5000, seed 6412. Reported as exploratory whatever p is.
Smoke: K066_SMOKE=1 (R 200, 20 FPR, 20 plants; writes /tmp only; never computes T_obs or F_obs).
Usage: python3 tools/k066_l1_sum_context.py data/khipu.db
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sqlite3, json, sys, time, math, hashlib, numpy as np
from collections import defaultdict, Counter
t0 = time.time()
SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
if hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest() != SHA: sys.exit('EXCLUDED: khipu.db hash differs from MANIFEST')
c = sqlite3.connect('file:' + sys.argv[1] + '?mode=ro', uri=True); ALPHA = 0.05; KMAX = 12
import os
SMOKE = 'K066_SMOKE' in os.environ
R, NF, NP, RH2 = (200, 20, 20, 0) if SMOKE else (5000, 200, 200, 5000)
OUT = sys.argv[2] if len(sys.argv) > 2 else 'analysis/k066_results.json'
def log(*a): print(*a, round(time.time() - t0, 1), flush=True)
# ---- data: K064 pipeline verbatim ----
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
def collapse(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; st = np.concatenate([[0], b]); return s[st]
cs = [collapse(s) for s in seqs]
cntF = Counter(int(v) for s in cs for v in s if v > 0); NTF = sum(cntF.values()); VF = len(cntF); DENF = NTF + VF + 1
def wF(v): return -math.log((cntF.get(int(v), 0) + 1) / DENF) if v > 0 else 0.0
okr2k = {meta[kid]['okr']: k for k, kid in enumerate(ids)}
A, B = seqs[okr2k['KH0143']], seqs[okr2k['KH0591']]
def find(s, pat):
    h = [i for i in range(len(s) - len(pat) + 1) if s[i:i + len(pat)].tolist() == pat]; assert len(h) == 1, (pat, h); return h[0]
ia = find(A, [226, 115, 124, 200, 161]); ib = find(B, [226, 115, 124, 357, 161])
SA = list(range(ia, ia + 5)); SB = list(range(ib, ib + 5))
log('KH0143 n', len(A), 'seg at', ia, A[ia - 5:ia + 8].tolist(), '| KH0591 n', len(B), 'seg at', ib, B[ib - 5:ib + 8].tolist())
# ---- K001 sum relations, with involvement ----
def involved(V):
    n = len(V); P = np.zeros(n + 1, np.int64); P[1:] = np.cumsum(V); NZ = np.zeros(n + 1, np.int64); NZ[1:] = np.cumsum(V > 0)
    inv = np.zeros(n, bool); rel = []
    for i in range(n):
        if V[i] < 10: continue
        for k in range(2, KMAX + 1):
            if i + k < n and P[i + k + 1] - P[i + 1] == V[i] and NZ[i + k + 1] - NZ[i + 1] >= 2:
                inv[i] = True; w = np.arange(i + 1, i + k + 1); inv[w[V[w] > 0]] = True; rel.append((i, 'R', k))
            if i - k >= 0 and P[i] - P[i - k] == V[i] and NZ[i] - NZ[i - k] >= 2:
                inv[i] = True; w = np.arange(i - k, i); inv[w[V[w] > 0]] = True; rel.append((i, 'L', k))
    return inv, rel
def T(Va, Vb): return int(involved(Va)[0][SA].sum() + involved(Vb)[0][SB].sum())
# ---- H1 reference ----
rng = np.random.default_rng(6409); ref = np.array([T(rng.permutation(A), rng.permutation(B)) for _ in range(R)]); log('reference done', R)
def pval(t): return float((1 + (ref >= t).sum()) / (1 + R))
rng = np.random.default_rng(6410); fp = [pval(T(rng.permutation(A), rng.permutation(B))) for _ in range(NF)]
FPR = float(np.mean([p <= ALPHA for p in fp])); G1 = FPR <= 0.10; log('G1 FPR', FPR)
rng = np.random.default_rng(6411)
nzA, nzB = A[A > 0], B[B > 0]
def plant(V, S, nz):
    V = V.copy(); base = T_one(V, S)
    cand = [i for i in S if i + 3 < len(V)]
    while True:
        i = int(rng.choice(cand)); w = V[i + 1:i + 4].copy()
        for t in range(3):
            if w[t] == 0: w[t] = int(rng.choice(nz))
        if w.sum() >= 10: break
    V[i + 1:i + 4] = w; V[i] = int(w.sum()); return V, base
def T_one(V, S): return int(involved(V)[0][S].sum())
pl = []; blind = 0
for _ in range(NP):
    Va, ba = plant(rng.permutation(A), SA, nzA); Vb, bb = plant(rng.permutation(B), SB, nzB)
    t = T(Va, Vb); blind += int(t <= ba + bb); pl.append(dict(T=t, base=ba + bb, p=pval(t)))
POWER = float(np.mean([x['p'] <= ALPHA for x in pl])); G2 = POWER >= 0.80; log('G2 power', POWER, 'blind', blind)
out = dict(segment=dict(KH0143=dict(start=ia, n=len(A), window=A[max(ia - 6, 0):ia + 8].tolist()), KH0591=dict(start=ib, n=len(B), window=B[max(ib - 6, 0):ib + 8].tolist())),
           reference=dict(R=R, seed=6409, T_quantiles={q: float(np.quantile(ref, q)) for q in (0.5, 0.9, 0.95, 0.99)}, T_hist={int(k): int(v) for k, v in Counter(ref.tolist()).items()}),
           G1=dict(seed=6410, n=NF, share=FPR, passed=bool(G1)), G2=dict(seed=6411, plants=NP, power=POWER, blind_spot_plants=blind, passed=bool(G2),
           T_quantiles={q: float(np.quantile([x['T'] for x in pl], q)) for q in (0.05, 0.2, 0.5)}))
if SMOKE:
    json.dump(out, open('/tmp/k066/smoke.json', 'w'), indent=1); log('smoke only: no observed value computed'); sys.exit(0)
if G1 and G2:
    ivA, relA = involved(A); ivB, relB = involved(B); Tobs = int(ivA[SA].sum() + ivB[SB].sum()); p = pval(Tobs)
    out['H1'] = dict(T_obs=Tobs, per_khipu=dict(KH0143=int(ivA[SA].sum()), KH0591=int(ivB[SB].sum())), p=p,
                     verdict='SUPPORTED' if p <= ALPHA else 'NOT SUPPORTED',
                     relations_touching_segment=dict(KH0143=[r for r in relA if any(x in SA for x in [r[0]] + list(range(r[0] + 1, r[0] + r[2] + 1) if r[1] == 'R' else range(r[0] - r[2], r[0])))],
                                                     KH0591=[r for r in relB if any(x in SB for x in [r[0]] + list(range(r[0] + 1, r[0] + r[2] + 1) if r[1] == 'R' else range(r[0] - r[2], r[0])))]),
                     all_relations=dict(KH0143=len(relA), KH0591=len(relB)))
else:
    out['H1'] = dict(verdict='NOT TESTABLE' if G1 else 'EXCLUDED')
log('H1', out['H1'])
# ---- H2 exploratory flank matches on the collapsed L1 diagonal ----
ca, cb = cs[okr2k['KH0143']], cs[okr2k['KH0591']]
ja = find(ca, [226, 115, 124, 200, 161]); jb = find(cb, [226, 115, 124, 357, 161]); d = ja - jb
blkB = set(range(jb - 1, jb + 6)); flankB = [j for j in range(len(cb)) if j not in blkB]
def F(cbx):
    s = 0.0; m = []
    for j in flankB:
        i = j + d
        if 0 <= i < len(ca) and cbx[j] > 0 and cbx[j] == ca[i]: s += wF(cbx[j]); m.append((int(i), int(j), int(cbx[j])))
    return s, m
Fobs, Mobs = F(cb); rng = np.random.default_rng(6412); fl = cb[flankB]; nullF = []
for _ in range(RH2):
    x = cb.copy(); x[flankB] = rng.permutation(fl); nullF.append(F(x)[0])
nullF = np.array(nullF); pH2 = float((1 + (nullF >= Fobs - 1e-12).sum()) / (1 + RH2))
out['H2_exploratory'] = dict(offset=d, F_obs=Fobs, matches=Mobs, p=pH2, null_share_F_gt_0=float((nullF > 0).mean()), label='exploratory, disclosed-motivated')
log('H2', out['H2_exploratory'])
out['runtime_s'] = round(time.time() - t0, 1); json.dump(out, open(OUT, 'w'), indent=1); log('wrote', OUT)
