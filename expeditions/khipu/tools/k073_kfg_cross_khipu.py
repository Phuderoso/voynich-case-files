#!/usr/bin/env python3
"""K073 - KFG re-audit step 5 (README line 9): line-3 cross-khipu shared runs. K010's engine verbatim
(composition-aware score S, run-preserving null, max over all pairs, R = 1000, 4-fold calibration, 200 planted
6-cord copies, CAP 300, eligibility >= 10 non-zero pendants, R5 multi-number pendants masked to 0) run on Khipu Field
Guide pendants (p-cords in pendant order, KFG value; R5 by the K072 KFG port, agreement gate 0.9963 in K072).
Pre-registered in case-file/K073-kfg-cross-khipu.md. F0: the same engine on OKR reproduces K010's five pair scores.
Usage: python3 tools/k073_kfg_cross_khipu.py data/khipu.db [--smoke]
Seeds 6424 (KFG null + calibration), 6425 (KFG plants). Next free 6426. Smoke: R 20, 5 plants, values shuffled
within each khipu (no real statistic seen)."""
import sqlite3, json, sys, re, time, math, hashlib
import numpy as np
from collections import defaultdict, Counter
T0 = time.time(); KFG_DB = '/workspace/kfg/kfg_20261111.db'
KFG_SHA = '582e548d2bbf04402a01a8446d32268967afeb480330feb47c3a90756742994d'
OKR_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
OKR_DB = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'data/khipu.db'
SMOKE = '--smoke' in sys.argv
OUT = 'analysis/k073_smoke.json' if SMOKE else 'analysis/k073_results.json'
R = 20 if SMOKE else 1000; NPL = 5 if SMOKE else 200; CAP = 300; WALL = 560
SEEDS = dict(null=6424, plants=6425); NEXT_FREE = 6426
OKR_PAIRS = [('KH0362', 'KH0049'), ('KH0128', 'KH0137'), ('KH0140', 'KH0483'), ('KH0304', 'KH0303'), ('KH0305', 'KH0301')]
res = dict(design=dict(R=R, plants=NPL, CAP=CAP, seeds=SEEDS, next_free_seed=NEXT_FREE, smoke=SMOKE, alpha=0.05,
                       calib_range=[0.037, 0.064], short_match_power_rule=0.5))
def dump():
    res['secs'] = round(time.time() - T0, 1); json.dump(res, open(OUT, 'w'), indent=1)
def stop(reason):
    res['decision'] = dict(excluded=True, reason=reason); dump(); print('STOP:', reason, flush=True); sys.exit(0)
def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p

# ---------------- K010 engine (verbatim, wrapped so it can run on either source) ----------------
class Engine:
    def __init__(self, seqs, rng):
        self.seqs, self.rng = seqs, rng
        freq = Counter(int(x) for s in seqs for x in s if x > 0); tot = sum(freq.values())
        self.ginfo = {v: -math.log2(n / tot) for v, n in freq.items()}
        self.lnn = [math.log2(len(s)) for s in seqs]
        self.RUNS = [self.runs(s) for s in seqs]
    @staticmethod
    def runs(s):
        b = np.flatnonzero(np.diff(s) != 0) + 1; return np.split(s, b)
    def runperm(self, k):
        r = self.RUNS[k]; o = self.rng.permutation(len(r)); return np.concatenate([r[i] for i in o])
    def pairstats(self, S, want=None):
        lp = {}; lnn, ginfo = self.lnn, self.ginfo
        for k in (want if want else range(len(S))):
            cn = Counter(int(x) for x in S[k]); lp[k] = {v: -math.log2(m / len(S[k])) for v, m in cn.items()}
        idx = defaultdict(list)
        for a, s in enumerate(S):
            if want and a not in want: continue
            for i in range(len(s) - 2):
                if s[i] > 0 and s[i + 1] > 0 and s[i + 2] > 0: idx[(s[i], s[i + 1], s[i + 2])].append((a, i))
        bS, bI = {}, {}
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
                    blk = [int(v) for v in sa[i:i + L]]
                    Sc = sum(lp[a][v] + lp[b][v] for v in blk) - lnn[a] - lnn[b]
                    I = sum(ginfo.get(v, 20.0) for v in blk)
                    key = (a, b) if a < b else (b, a); ia, ib = (i, j) if a < b else (j, i)
                    if Sc > bS.get(key, (-1e9,))[0]: bS[key] = (Sc, ia, ib, L)
                    if I > bI.get(key, (0,))[0]: bI[key] = (I, ia, ib, L)
        return bS, bI

# ---------------- G0 hashes ----------------
for path, want in ((OKR_DB, OKR_SHA), (KFG_DB, KFG_SHA)):
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    if h != want: stop(f'G0 hash mismatch {path} {h}')
res['G0'] = 'pass'

# ---------------- F0: K010 OKR sequences (verbatim loader) and observed scores ----------------
c = sqlite3.connect(OKR_DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
okrname = {r[0]: r[1] or '' for r in c.execute("select KHIPU_ID, OKR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
clpl = defaultdict(set); clcd = {}
for cid_, cl_, t_, v_ in c.execute("select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
    t_ = (t_ or '').strip()
    if t_ in ('S', 'L', 'E') and v_: clpl[cl_].add(place(int(v_)) if t_ == 'S' else 0)
    clcd[cl_] = cid_
ordn_ = {r[0]: r[1] for r in c.execute("select CLUSTER_ID, ORDINAL from knot_cluster")}
bc_ = defaultdict(dict)
for cl_, pl_ in clpl.items():
    if len(pl_) == 1 and ordn_.get(cl_) is not None: bc_[clcd[cl_]][ordn_[cl_]] = next(iter(pl_))
R5 = {cd for cd, d in bc_.items() if len(d) >= 2 and not all(a > b for a, b in zip([d[o] for o in sorted(d)], [d[o] for o in sorted(d)][1:]))}
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid not in dups: kh[khid].append(0 if cid in R5 else val.get(cid, 0))
oids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]; oseqs = [np.array(kh[k], np.int64) for k in oids]
E0 = Engine(oseqs, np.random.default_rng(0)); oS, _ = E0.pairstats(oseqs)
pubS = json.load(open('analysis/k010_results.json'))['significant_S']
pub = {tuple(sorted((r['a'], r['b']))): r['score'] for r in pubS}
got = {}
for (a, b), (v, i, j, L) in oS.items():
    key = tuple(sorted((okrname[oids[a]], okrname[oids[b]])))
    if key in pub: got[key] = round(v, 2)
F0 = dict(n_R5=len(R5), n_eligible=len(oids), published={'·'.join(k): v for k, v in pub.items()},
          reproduced={'·'.join(k): got.get(k) for k in pub})
F0['pass'] = len(pub) == 5 and all(got.get(k) is not None and abs(got[k] - pub[k]) <= 0.01 for k in pub)
res['F0_engine_on_okr'] = F0; print('F0', F0, flush=True); dump()
if not F0['pass']: stop('F0 engine fixture on OKR failed')

# ---------------- KFG pendants (K071/K072 loader) + KFG R5 (K072 port) ----------------
k = sqlite3.connect(KFG_DB)
meta = {r[0]: dict(aliases=r[1] or '', museum=(r[2] or '').strip(), mnum=(r[3] or '').strip())
        for r in k.execute('select name, aliases, museum_name, museum_number from khipu')}
PEN = re.compile(r'^p(\d+)$'); CLU = re.compile(r'^(\d+)([A-Z]+)\(([-\d.]+),[^)]*\),(-?\d+)$')
def kfg_r5(knots):
    cls = []
    for j, t in enumerate(str(knots or '').split(';')):
        m = CLU.match(t.strip())
        if not m: continue
        typ, pos, v = m.group(2), float(m.group(3)), int(m.group(4))
        if v == 0 or typ[0] not in 'SLE': continue
        cls.append((pos, j, place(v) if typ[0] == 'S' else 0))
    s = [p for _, _, p in sorted(cls)]
    return len(s) >= 2 and not all(a > b for a, b in zip(s, s[1:]))
pend = defaultdict(list); NR5 = [0]
for khn, nm, v, kn in k.execute('select khipu, cord_name, value, knots from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0
    r5 = kfg_r5(kn); NR5[0] += r5
    pend[khn].append((int(m.group(1)), 0 if r5 else x))
kseq = {}
for khn, L in pend.items():
    L = sorted(L); kseq[khn] = np.array([x for _, x in L], np.int64)
ids = sorted(n for n, s in kseq.items() if (s > 0).sum() >= 10); seqs = [kseq[n] for n in ids]
okr_names = {v for v in okrname.values() if v}
res['kfg_corpus'] = dict(n_khipus=len(meta), n_with_pendants=len(kseq), n_eligible=len(ids),
                         n_eligible_also_okr=sum(n in okr_names for n in ids), n_R5_masked=NR5[0])
rng = np.random.default_rng(SEEDS['null'])
if SMOKE:
    seqs = [rng.permutation(s) for s in seqs]
E = Engine(seqs, rng)
obsS, obsI = E.pairstats(seqs); print('KFG pairs with block', len(obsS), round(time.time() - T0, 1), flush=True)
mS, mI = [], []
for r in range(R):
    Sx = [E.runperm(q) for q in range(len(seqs))]; a, b = E.pairstats(Sx)
    mS.append(max((v[0] for v in a.values()), default=0)); mI.append(max((v[0] for v in b.values()), default=0))
    if r % 100 == 99:
        print('rep', r + 1, round(time.time() - T0, 1), flush=True)
        json.dump(dict(null_max_S=[round(x, 3) for x in mS]), open('analysis/k073_checkpoint_nulls.json', 'w'))
    if time.time() - T0 > WALL: stop(f'wall clock exceeded after {r + 1} null corpora')
mS, mI = np.array(mS), np.array(mI); TS = float(np.quantile(mS, .95))
fold = np.arange(R) % 4
def cv(m): return float(np.mean([m[i] > np.quantile(m[fold != fold[i]], .95) for i in range(R)]))
calS = cv(mS); res['null'] = dict(T_S=round(TS, 2), calib_S=calS, calib_ok=bool(0.037 <= calS <= 0.064))
print('calibration', calS, 'T', TS, round(time.time() - T0, 1), flush=True); dump()
prng = np.random.default_rng(SEEDS['plants']); E.rng = prng; rec, plS = [], []
for t in range(NPL):
    Sx = [E.runperm(q) for q in range(len(seqs))]
    while True:
        a, b = (int(x) for x in prng.choice(len(Sx), 2, replace=False)); sa = Sx[a]
        st = [i for i in range(len(sa) - 5) if (sa[i:i + 6] > 0).sum() >= 5]
        if st and len(Sx[b]) >= 8: break
    i = int(prng.choice(st)); j = int(prng.integers(0, len(Sx[b]) - 5)); Sx[b] = Sx[b].copy(); Sx[b][j:j + 6] = sa[i:i + 6]
    ps, _ = E.pairstats(Sx, want={a, b}); kk = (min(a, b), max(a, b))
    s = ps.get(kk, (-1e9,))[0]; rec.append(s > TS); plS.append(s)
    if time.time() - T0 > WALL + 30: stop(f'wall clock exceeded in plants after {t + 1}')
power = float(np.mean(rec)); res['plants'] = dict(n=len(rec), recovery=power, median_S=round(float(np.median(plS)), 2),
                                                 short_matches_testable=power >= 0.5)
def padj(v): return (1 + int((mS >= v).sum())) / (1 + R)
pos = {n: q for q, n in enumerate(ids)}
rows = []
for (a, b), (v, i, j, L) in obsS.items():
    p = padj(v)
    if p > 0.05: continue
    A, B = meta.get(ids[a], {}), meta.get(ids[b], {}); nz = min((seqs[a] > 0).sum(), (seqs[b] > 0).sum())
    same = bool(A.get('mnum') and A.get('mnum') == B.get('mnum') and A.get('museum') == B.get('museum'))
    rows.append(dict(a=ids[a], b=ids[b], score=round(v, 2), block_len=L, block=[int(x) for x in seqs[a][i:i + L]], p_adj=p,
                     a_museum=A.get('museum', '') + ' ' + A.get('mnum', ''), b_museum=B.get('museum', '') + ' ' + B.get('mnum', ''),
                     a_aliases=A.get('aliases', ''), b_aliases=B.get('aliases', ''),
                     a_in_okr=ids[a] in okr_names, b_in_okr=ids[b] in okr_names,
                     cls='probable duplicate record' if (same or L >= nz / 2) else 'inter-khipu match'))
rows.sort(key=lambda r: -r['score']); res['significant_S'] = rows
verd = []
for a, b in OKR_PAIRS:
    if a not in pos or b not in pos:
        miss = [x for x in (a, b) if x not in pos]
        why = {x: ('absent from KFG' if x not in kseq else f'ineligible ({int((kseq[x] > 0).sum())} non-zero pendants)') for x in miss}
        verd.append(dict(pair=f'{a}·{b}', verdict='NOT TESTABLE as a pair', why=why)); continue
    kk = (min(pos[a], pos[b]), max(pos[a], pos[b])); o = obsS.get(kk)
    if o is None: verd.append(dict(pair=f'{a}·{b}', verdict='CHANGED (correction): no shared 3-run on KFG', score=None, p_adj=None)); continue
    p = padj(o[0])
    verd.append(dict(pair=f'{a}·{b}', score=round(o[0], 2), block_len=o[3], p_adj=p,
                     verdict='REPLICATED' if p <= 0.05 else 'CHANGED (correction)'))
res['okr_pair_verdicts'] = verd
okrset = {tuple(sorted(x)) for x in OKR_PAIRS}
res['new_pairs'] = [r for r in rows if tuple(sorted((r['a'], r['b']))) not in okrset]
if not res['null']['calib_ok']:
    res['decision'] = dict(note='calibration outside the registered range: every verdict above is NOT TESTABLE')
dump(); print(json.dumps(dict(null=res['null'], plants=res['plants'], verdicts=verd), indent=1))
for r in rows: print(r['a'], r['b'], r['score'], r['block_len'], r['p_adj'], r['cls'], r['a_museum'], '|', r['b_museum'], r['block'][:10])
