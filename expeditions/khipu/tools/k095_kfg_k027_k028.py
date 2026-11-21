#!/usr/bin/env python3
"""K095 - KFG re-audit of K027 (template) and K028 (doublet-null lead). Pre-registered in case-file/K095-kfg-k027-k028-lead.md
(commit 5df8589, before any KFG statistic). K027/K028 engines are copied with only the data source and RNG objects parameterised.
Modes: a0    - OKR only, original seeds 27027/28028, no caps; must reproduce analysis/k027_results.json and k028_results.json
               (except secs) -> analysis/k095_a0.json
       smoke - KFG values shuffled within each khipu, tiny R; plumbing only; output in /tmp
       full  - registered KFG run (needs analysis/k095_a0.json passed) -> analysis/k095_results.json
Usage: python3 tools/k095_kfg_k027_k028.py data/khipu.db {a0|smoke|full}
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sqlite3, sys, json, time, re, hashlib, math, random, os, numpy as np
from collections import defaultdict, Counter
t0 = time.time(); MODE = sys.argv[2] if len(sys.argv) > 2 else 'smoke'
OKR_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
KFG_DB = '/workspace/kfg/kfg_20261111.db'; KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'
def log(*a): print(*a, round(time.time() - t0, 1), flush=True)
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
if sha(sys.argv[1]) != OKR_SHA: sys.exit('EXCLUDED: khipu.db hash differs')
if sha(KFG_DB) != KFG_SHA: sys.exit('EXCLUDED: KFG hash differs')
if MODE == 'full' and not json.load(open('analysis/k095_a0.json'))['passed']: sys.exit('EXCLUDED: A0 failed')
SMOKE = MODE == 'smoke'
P = (1, 2, 1, 2, 3, 1, 2, 1, 3)
def place_(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
def runs(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; return np.split(s, b)
def collapse(s):
    b = np.flatnonzero(np.diff(s) != 0) + 1; return s[np.concatenate([[0], b])].tolist()
# ---------------- data: OKR (K027/K028 loader verbatim) ----------------
def load_okr():
    c = sqlite3.connect(sys.argv[1])
    dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
    meta = {r[0]: (r[1], r[2]) for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
    val = defaultdict(int)
    for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
        if v is not None: val[cid] += int(v)
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
    ids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]
    seqs = [np.array(kh[k], np.int64) for k in ids]
    return [meta[k][0] for k in ids], [meta[k][1] for k in ids], seqs
# ---------------- data: KFG (K094 loader) ----------------
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
def load_kfg():
    kc = sqlite3.connect('file:' + KFG_DB + '?mode=ro', uri=True)
    names = {r[0]: (r[1] or '').strip() for r in kc.execute('select name, aliases from khipu')}
    pend = defaultdict(list)
    for khn, nm, v, kn in kc.execute('select khipu, cord_name, value, knots from cord order by khipu, idx'):
        m = PEN.match(str(nm or ''))
        if not m: continue
        try: x = int(float(v)) if v not in (None, '') else 0
        except Exception: x = 0
        pend[khn].append((int(m.group(1)), 0 if kfg_r5(kn) else x))
    kh = {k: np.array([x for _, x in sorted(L)], np.int64) for k, L in pend.items()}
    if SMOKE:
        rsm = np.random.default_rng(1); kh = {k: rsm.permutation(v) for k, v in kh.items()}
    ids = sorted(k for k, v in kh.items() if (v > 0).sum() >= 10)
    return ids, [names.get(k, '') for k in ids], [kh[k] for k in ids], names, kh
# ---------------- K027 engine ----------------
def contains(cs, pat):
    n = len(pat); return any(tuple(cs[i:i + n]) == pat for i in range(len(cs) - n + 1))
def t_stats(CS, LEAD):
    n1 = sum(contains(cs, P) for k, cs in enumerate(CS) if k not in LEAD)
    grams = defaultdict(set)
    for k, cs in enumerate(CS):
        for i in range(len(cs) - 8):
            g = tuple(cs[i:i + 9])
            if all(1 <= x <= 3 for x in g): grams[g].add(k)
    pairs = set()
    for g, ks in grams.items():
        ks = sorted(ks)
        for a in range(len(ks)):
            for b in range(a + 1, len(ks)): pairs.add((ks[a], ks[b]))
    pairs.discard(tuple(sorted(LEAD)))
    return n1, len(pairs), pairs
def make_nullCS(RUNS):
    def nullCS(rng): return [collapse(np.concatenate([r[i] for i in rng.permutation(len(r))])) for r in RUNS]
    return nullCS
def write(cs, block, rng):
    i = rng.integers(0, max(1, len(cs) - len(block))); cs = list(cs); cs[i:i + len(block)] = list(block)
    return [x for j, x in enumerate(cs) if j == 0 or x != cs[j - 1]]
def rand_block(rng):
    blk = [int(rng.integers(1, 4))]
    while len(blk) < 9:
        x = int(rng.integers(1, 4))
        if x != blk[-1]: blk.append(x)
    return blk
def t_null(RUNS, LEAD, rng, R):
    nullCS = make_nullCS(RUNS); N1, N2 = [], []
    for rep in range(R):
        a, b, _ = t_stats(nullCS(rng), LEAD); N1.append(a); N2.append(b)
    return np.array(N1), np.array(N2)
def t_power(RUNS, LEAD, others, rng, TR, q1, q2):
    nullCS = make_nullCS(RUNS); pw1 = pw2 = 0
    for t in range(TR):
        CS = nullCS(rng)
        for k in rng.choice(others, 3, replace=False): CS[k] = write(CS[k], P, rng)
        pw1 += t_stats(CS, LEAD)[0] > q1
        CS = nullCS(rng)
        for _ in range(5):
            blk = rand_block(rng); a, b = rng.choice(others, 2, replace=False); CS[a] = write(CS[a], blk, rng); CS[b] = write(CS[b], blk, rng)
        pw2 += t_stats(CS, LEAD)[1] > q2
    return pw1, pw2
# ---------------- K028 engine ----------------
class Dsh:
    def __init__(self, CS0, rnd):
        self.CS0 = CS0; self.rnd = rnd; self.EDGES = []
        for cs in CS0:
            out = defaultdict(list)
            for a, b in zip(cs, cs[1:]): out[a].append(b)
            self.EDGES.append(out)
    def shuffle(self, k):
        cs = self.CS0[k]; rnd = self.rnd
        if len(cs) < 3: return list(cs)
        out = self.EDGES[k]; last = cs[-1]; intree = {last}; nxt = {}
        for v in list(out):
            u = v
            while u not in intree:
                nxt[u] = rnd.choice(out[u]); u = nxt[u]
            u = v
            while u not in intree:
                intree.add(u); u = nxt[u]
        lists = {}
        for v, tg in out.items():
            t = list(tg)
            if v != last:
                t.remove(nxt[v]); rnd.shuffle(t); t.append(nxt[v])
            else: rnd.shuffle(t)
            lists[v] = t
        ptr = defaultdict(int); seq = [cs[0]]; u = cs[0]
        for _ in range(len(cs) - 1):
            w = lists[u][ptr[u]]; ptr[u] += 1; seq.append(w); u = w
        return seq
    def corpus(self): return [self.shuffle(k) for k in range(len(self.CS0))]
def dub(cs): return Counter(zip(cs, cs[1:]))
def shuf_check(D):
    CS0 = D.CS0; bad = 0; differ = 0; elig = 0
    for k in range(len(CS0)):
        d0 = dub(CS0[k]); dif = False
        for _ in range(20):
            s = D.shuffle(k)
            if s[0] != CS0[k][0] or s[-1] != CS0[k][-1] or dub(s) != d0 or len(s) != len(CS0[k]): bad += 1
            if s != CS0[k]: dif = True
        if len(set(zip(CS0[k], CS0[k][1:]))) >= 3: elig += 1; differ += dif
    return dict(violations=bad, differ_share=round(differ / max(elig, 1), 4), eligible=elig, passed=bad == 0 and differ / max(elig, 1) >= 0.9)
def npairs_set(CS):
    grams = defaultdict(set)
    for k, cs in enumerate(CS):
        for i in range(len(cs) - 8):
            g = tuple(cs[i:i + 9])
            if all(1 <= x <= 3 for x in g): grams[g].add(k)
    pairs = set()
    for ks in grams.values():
        ks = sorted(ks)
        for a in range(len(ks)):
            for b in range(a + 1, len(ks)): pairs.add((ks[a], ks[b]))
    return pairs
def npairs(CS): return len(npairs_set(CS))
def longest(x, y):
    best = 0; prev = [0] * (len(y) + 1)
    for i in range(1, len(x) + 1):
        cur = [0] * (len(y) + 1)
        for j in range(1, len(y) + 1):
            if x[i - 1] == y[j - 1] and x[i - 1] > 0: cur[j] = prev[j - 1] + 1; best = max(best, cur[j])
        prev = cur
    return best
def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round((c - h) / d, 3), round((c + h) / d, 3))
def rt(o): return json.loads(json.dumps(o, default=str))
# ======================= A0 =======================
if MODE == 'a0':
    okr, inv, seqs = load_okr(); ids_n = len(seqs); LEAD = {okr.index('KH0240'), okr.index('KH0496')}; A, B = okr.index('KH0240'), okr.index('KH0496')
    RUNS = [runs(s) for s in seqs]; CS0 = [collapse(s) for s in seqs]
    # K027
    rng = np.random.default_rng(27027); R, TR = 2000, 100
    n1, n2, pairs = t_stats(CS0, LEAD)
    N1, N2 = t_null(RUNS, LEAD, rng, R); Rr = len(N1)
    p1 = (1 + np.sum(N1 >= n1)) / (Rr + 1); p2 = (1 + np.sum(N2 >= n2)) / (Rr + 1)
    q1, q2 = np.quantile(N1, 0.975), np.quantile(N2, 0.975)
    others = [k for k in range(len(seqs)) if k not in LEAD]
    pw1, pw2 = t_power(RUNS, LEAD, others, rng, TR, q1, q2)
    k027 = dict(n_khipus=ids_n, R=Rr, T1=dict(obs=n1, null_mean=float(N1.mean()), q975=float(q1), p=float(p1), power=pw1 / TR),
                T2=dict(obs=n2, null_mean=float(N2.mean()), q975=float(q2), p=float(p2), power=pw2 / TR,
                        pairs=[(okr[a] + ' ' + inv[a], okr[b] + ' ' + inv[b]) for a, b in sorted(pairs)][:40]),
                P_holders=[okr[k] + ' ' + inv[k] for k, cs in enumerate(CS0) if contains(cs, P)], trials=TR)
    log('A0 K027 done')
    # K028
    rnd = random.Random(28028); D = Dsh(CS0, rnd)
    check = shuf_check(D)
    S_obs = npairs(CS0); D_obs = longest(CS0[A], CS0[B])
    NS = np.array([npairs(D.corpus()) for _ in range(1000)]); pS = (1 + np.sum(NS >= S_obs)) / (len(NS) + 1)
    ND = np.array([longest(D.shuffle(A), D.shuffle(B)) for _ in range(20000)]); pD = (1 + np.sum(ND >= D_obs)) / (len(ND) + 1)
    k028 = dict(n_khipus=ids_n, check=check, S=dict(obs=S_obs, R=len(NS), null_dist=dict(Counter(NS.tolist())), p=float(pS), survives=bool(pS < 0.05 and check['passed'])),
                D=dict(obs=D_obs, R=len(ND), null_dist=dict(sorted(Counter(ND.tolist()).items())), p=float(pD)),
                lead_seqs={okr[A]: CS0[A], okr[B]: CS0[B]})
    pub27 = json.load(open('analysis/k027_results.json')); pub28 = json.load(open('analysis/k028_results.json'))
    pub27.pop('secs'); pub28.pop('secs')
    d27 = [k for k in pub27 if rt(k027).get(k) != pub27[k]]; d28 = [k for k in pub28 if rt(k028).get(k) != pub28[k]]
    # field-level detail for any difference
    detail = {}
    for nm, mine, pub, dd in (('k027', rt(k027), pub27, d27), ('k028', rt(k028), pub28, d28)):
        for k in dd:
            if isinstance(pub[k], dict): detail[nm + '.' + k] = [s for s in pub[k] if mine[k].get(s) != pub[k][s]]
    out = dict(passed=not d27 and not d28, differing_fields_k027=d27, differing_fields_k028=d28, detail=detail,
               k027_rebuilt=rt(k027), k028_rebuilt=rt(k028), seconds=round(time.time() - t0, 1))
    json.dump(out, open('analysis/k095_a0.json', 'w'), indent=1)
    log('A0 passed =', out['passed'], d27, d28, detail); sys.exit(0 if out['passed'] else 1)
# ======================= KFG run =======================
ids, inv, seqs, names, khall = load_kfg()
N = len(seqs)
G_LEAD = dict(KH0240_in_KFG='KH0240' in names, KH0496_in_KFG='KH0496' in names,
              KH0240_eligible='KH0240' in ids, KH0496_eligible='KH0496' in ids)
G_LEAD['passed'] = all(G_LEAD.values())
OUT = '/tmp/k095_smoke.json' if SMOKE else 'analysis/k095_results.json'
if not G_LEAD['passed']:
    json.dump(dict(mode=MODE, n_khipus=N, G_LEAD=G_LEAD, verdict=dict(K027='NOT TESTABLE (G-LEAD)', K028='NOT TESTABLE (G-LEAD)')), open(OUT, 'w'), indent=1)
    log('NOT TESTABLE: lead missing', G_LEAD); sys.exit(0)
A, B = ids.index('KH0240'), ids.index('KH0496'); LEAD = {A, B}
RT, RS, NFPR, NPL, RD = (30, 20, 8, 6, 200) if SMOKE else (2000, 1000, 200, 100, 20000)
RUNS = [runs(s) for s in seqs]; CS0 = [collapse(s) for s in seqs]
others = [k for k in range(N) if k not in LEAD]
log('KFG khipus', N)
# input deltas (descriptive)
okr_n, okr_inv, okr_seqs = load_okr(); oi = {k: i for i, k in enumerate(okr_n)}
okr_CS = {k: collapse(okr_seqs[oi[k]]) for k in ('KH0240', 'KH0496')}
delta = dict(eligible_kfg=N, eligible_okr=len(okr_n),
             lead={nm: dict(identical_to_okr=CS0[ids.index(nm)] == okr_CS[nm], identical_reversed=CS0[ids.index(nm)] == okr_CS[nm][::-1],
                            contains_P=contains(CS0[ids.index(nm)], P), n_pend=int(len(seqs[ids.index(nm)])), collapsed_len=len(CS0[ids.index(nm)]),
                            collapsed_head=CS0[ids.index(nm)][:30]) for nm in ('KH0240', 'KH0496')},
             only_in_kfg=sorted(set(ids) - set(okr_n)), only_in_okr=sorted(set(okr_n) - set(ids)))
# observed
n1, n2, tpairs = t_stats(CS0, LEAD); S_set = npairs_set(CS0); S_obs = len(S_set); D_obs = longest(CS0[A], CS0[B])
lead_pair_shares = tuple(sorted(LEAD)) in S_set
obs = dict(N1=n1, N2=n2, S=S_obs, D=D_obs, lead_pair_shares_9block=lead_pair_shares,
           N1_holders=[ids[k] for k, cs in enumerate(CS0) if contains(cs, P) and k not in LEAD],
           T2_pairs=[(ids[a], inv[a], ids[b], inv[b]) for a, b in sorted(tpairs)][:40], S_pairs=[(ids[a], inv[a], ids[b], inv[b]) for a, b in sorted(S_set)][:40])
log('observed (KFG)', {k: obs[k] for k in ('N1', 'N2', 'S', 'D', 'lead_pair_shares_9block')})
# ---- T side
rngT = np.random.default_rng(6499); N1n, N2n = t_null(RUNS, LEAD, rngT, RT); Rr = len(N1n)
pv = lambda arr, o: float((1 + np.sum(arr >= o)) / (len(arr) + 1))
p1, p2 = pv(N1n, n1), pv(N2n, n2); q1, q2 = float(np.quantile(N1n, 0.975)), float(np.quantile(N2n, 0.975))
log('T null done', p1, p2)
nullCS = make_nullCS(RUNS); rngF = np.random.default_rng(6500); f1 = f2 = 0
for _ in range(NFPR):
    a, b, _ = t_stats(nullCS(rngF), LEAD); f1 += pv(N1n, a) < 0.025; f2 += pv(N2n, b) < 0.025
rngP = np.random.default_rng(6501); pw1, pw2 = t_power(RUNS, LEAD, others, rngP, NPL, q1, q2)
log('T gates done')
# ---- S side
rndS = random.Random(6502); DS = Dsh(CS0, rndS); NS = np.array([npairs(DS.corpus()) for _ in range(RS)]); pS = pv(NS, S_obs)
log('S null done', pS)
rndG = random.Random(6505); DG = Dsh(CS0, rndG); chk = shuf_check(DG)
ND = np.array([longest(DG.shuffle(A), DG.shuffle(B)) for _ in range(RD)]); pD = pv(ND, D_obs)
rndF = random.Random(6503); DF = Dsh(CS0, rndF); fS = 0
for _ in range(NFPR): fS += pv(NS, npairs(DF.corpus())) < 0.05
sstar = next((s for s in range(0, 50) if (1 + np.sum(NS >= s)) / (len(NS) + 1) < 0.05), None)
rngQ = np.random.default_rng(6504); DQ = Dsh(CS0, random.Random(6504)); pwS = 0
for _ in range(NPL):
    CS = DQ.corpus(); blk = rand_block(rngQ); a, b = rngQ.choice(others, 2, replace=False); CS[a] = write(CS[a], blk, rngQ); CS[b] = write(CS[b], blk, rngQ)
    pwS += sstar is not None and npairs(CS) >= sstar
log('S gates done')
# ---- gates, decisions
G = dict(G_LEAD=G_LEAD, G_SHUF=dict(chk, passed=chk['passed']),
         G_FPR=dict(T1=dict(rate=f1 / NFPR, wilson=wilson(f1, NFPR), passed=f1 / NFPR <= 0.05), T2=dict(rate=f2 / NFPR, wilson=wilson(f2, NFPR), passed=f2 / NFPR <= 0.05),
                    S=dict(rate=fS / NFPR, wilson=wilson(fS, NFPR), passed=fS / NFPR <= 0.075), n=NFPR),
         G_POW=dict(T1=dict(power=pw1 / NPL, wilson=wilson(int(pw1), NPL), passed=pw1 / NPL >= 0.8), T2=dict(power=pw2 / NPL, wilson=wilson(int(pw2), NPL), passed=pw2 / NPL >= 0.8),
                    S=dict(power=pwS / NPL, wilson=wilson(int(pwS), NPL), passed=pwS / NPL >= 0.8, s_star=sstar), trials=NPL))
def holm(ps, alpha=0.05):
    order = sorted(ps, key=lambda k: ps[k]); rej = {}; m = len(ps); stop = False
    for i, k in enumerate(order):
        ok = (not stop) and ps[k] < alpha / (m - i); rej[k] = bool(ok); stop = stop or not ok
    return rej
H2 = holm(dict(T1=p1, T2=p2)); H3 = holm(dict(T1=p1, T2=p2, S=pS)); bonf2 = dict(T1=p1 < 0.025, T2=p2 < 0.025)
tgate = G['G_FPR']['T1']['passed'] and G['G_FPR']['T2']['passed'] and G['G_POW']['T1']['passed'] and G['G_POW']['T2']['passed']
if any(H2.values()): v27 = 'CHANGED (template/family supported on KFG)'
elif tgate: v27 = 'REPLICATED (template not supported)'
else: v27 = 'NOT TESTABLE (gates)'
sgate = G['G_SHUF']['passed'] and G['G_FPR']['S']['passed'] and G['G_POW']['S']['passed']
if not sgate: v28 = 'NOT TESTABLE (gates)'
elif pS < 0.05 and S_obs >= 1: v28 = 'REPLICATED (survives)' + ('' if H3['S'] else '; fails Holm-3')
else: v28 = 'CHANGED (explained by transition habits on KFG)'
out = dict(mode=MODE, n_khipus=N, input_delta=delta, observed=obs, gates=G,
           T1=dict(obs=n1, null_mean=float(N1n.mean()), q975=q1, p=p1, R=Rr), T2=dict(obs=n2, null_mean=float(N2n.mean()), q975=q2, p=p2, R=Rr),
           S=dict(obs=S_obs, R=len(NS), null_dist=dict(sorted(Counter(NS.tolist()).items())), p=pS),
           D=dict(obs=D_obs, R=len(ND), null_dist=dict(sorted(Counter(ND.tolist()).items())), p=pD),
           holm=dict(T1_T2_alpha05=H2, T1_T2_S_alpha05=H3, bonferroni_T=bonf2),
           verdict=dict(K027=v27, K028=v28), seeds=dict(T_null=6499, T_fpr=6500, T_plants=6501, S_null=6502, S_fpr=6503, S_plants=6504, check_D=6505, next_free=6506),
           lead_seqs={'KH0240': CS0[A], 'KH0496': CS0[B]}, seconds=round(time.time() - t0, 1))
json.dump(rt(out), open(OUT, 'w'), indent=1)
log('verdict', out['verdict'])
