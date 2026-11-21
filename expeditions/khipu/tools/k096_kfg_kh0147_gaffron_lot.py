#!/usr/bin/env python3
"""K096 - KFG line 9 follow-up of K094's secondary lead KH0147 (Berlin VA42510, Pachacamac) x the Basel Gaffron lot
(Museum der Kulturen IVc.366.03 = KH0682..KH0691, KFG provenance 'Eduard Gaffron'). Registered in case-file/K096-*.md before any
new W was computed. Engine: K094's loader, R5 port, full-corpus rarity weights and Hamming-1 W (k065_wham1.c) imported verbatim by
exec of tools/k094_kfg_k065_rescue_family.py up to the P-unit definition (sha256 checked).
H1 (primary, held-out): T_ho = max W(KH0147, c) over the 8 lot members NOT named by K094 (c != KH0689, KH0690).
H2 (secondary, selected): T_sel = min(W(KH0147,KH0689), W(KH0147,KH0690)).
Null: P-unit permutation of KH0147 only (lot sequences fixed), R 2000, seed 6506. p = (1 + #{T_null >= T_obs}) / (1 + R).
Holm over H1, H2 at alpha 0.01. Gates: A0 (K094's two W rebuilt to 1e-9), G1 FPR (40 P-unit copies of KH0147, seed 6507, share p_H1<=0.01
must be <= 0.10), G2 power (100 plants, seed 6508: an 8-token all-nonzero distinct window of a random held-out lot member copied into a
P-unit copy of KH0147 at a random place, one interior token +-1..3, re-collapsed; power = share p_H1 <= 0.01 must be >= 0.80).
Descriptive: positions of the K094 hits in KH0147 (disjoint?), within-lot W matrix, rank of KH0147 among all eligible non-lot khipus by
max W vs the whole lot. Usage: python3 tools/k096_kfg_kh0147_gaffron_lot.py data/khipu.db {smoke|full}
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sys, os, hashlib, json, time, numpy as np
MODE96 = sys.argv[2] if len(sys.argv) > 2 else 'smoke'
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(HERE, 'k094_kfg_k065_rescue_family.py')
K094_SHA = hashlib.sha256(open(SRC, 'rb').read()).hexdigest()
src = open(SRC).read(); cut = src.index('UN = [units(x) for x in cs]') + len('UN = [units(x) for x in cs]')
sys.argv = [sys.argv[0], sys.argv[1], 'smoke' if MODE96 == 'smoke' else 'full']
g = {'__file__': SRC, '__name__': 'k094_engine'}; exec(compile(src[:cut], SRC, 'exec'), g)
ids, cs, UN, collapse, wham, wvF, log, okr2k, KH = g['ids'], g['cs'], g['UN'], g['collapse'], g['wham'], g['wvF'], g['log'], g['okr2k'], g['kh']
SMOKE = MODE96 == 'smoke'; ALPHA = 0.01; EPS = 1e-9
R, NFPR, NPL = (50, 4, 4) if SMOKE else (2000, 40, 100)
SEED_REF, SEED_FPR, SEED_PL = 6506, 6507, 6508
OUT = '/tmp/k096/smoke.json' if SMOKE else 'analysis/k096_results.json'; os.makedirs('/tmp/k096', exist_ok=True)
A = 'KH0147'; LOT = ['KH%04d' % i for i in range(682, 692)]; SEL = ['KH0689', 'KH0690']; HO = [x for x in LOT if x not in SEL]
elig = {x: x in okr2k for x in [A] + LOT}   # K094 >=10-nonzero rule (reported); H1 uses every lot member present in KFG
LS = {x: collapse(KH[x]) for x in LOT if x in KH}
if not all(elig[x] for x in [A] + SEL): sys.exit('NOT TESTABLE: lead khipu not eligible ' + json.dumps(elig))
HOe = [x for x in HO if x in LS]
ka = okr2k[A]; LOTe = [x for x in LOT if x in LS]
def Wpairs(a_seq, others):
    S = [a_seq] + [LS[x] for x in others]; n = len(others)
    pa = np.zeros(n, np.int64); pb = np.arange(1, n + 1, dtype=np.int64)
    return wham(S, pa, pb)
def stats(a_seq):
    W, I, J, K = Wpairs(a_seq, LOTe); d = dict(zip(LOTe, W))
    return max(d[x] for x in HOe), min(d[x] for x in SEL), d, (I, J, K)
def punit_a(rng):
    u = UN[ka]; o = rng.permutation(len(u)); return collapse(np.concatenate([u[i] for i in o]))
# A0: K094 W values of KH0147 x KH0689 / KH0690 (published analysis/k094_results.json)
k94 = json.load(open('analysis/k094_results.json'))
ref94 = {}
def walk(o):
    if isinstance(o, dict):
        if o.get('a') == A and o.get('b') in SEL and 'W' in o: ref94[o['b']] = o['W']
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(k94)
T_ho, T_sel, Wobs, (I, J, K) = stats(cs[ka])
A0 = dict(k094_W=ref94, rebuilt={x: float(Wobs[x]) for x in SEL})
A0['passed'] = (not SMOKE) and len(ref94) == 2 and all(abs(ref94[x] - Wobs[x]) < 1e-9 for x in SEL)
if not SMOKE and not A0['passed']: sys.exit('EXCLUDED: A0 failed ' + json.dumps(A0))
rng = np.random.default_rng(SEED_REF)
NH, NS = np.zeros(R), np.zeros(R)
for r in range(R):
    h, s, _, _ = stats(punit_a(rng)); NH[r], NS[r] = h, s
def pv(t, null): return float((1 + (null >= t - EPS).sum()) / (1 + len(null)))
log('reference done', R)
rf = np.random.default_rng(SEED_FPR); FP = [pv(stats(punit_a(rf))[0], NH) for _ in range(NFPR)]
FPR = sum(p <= ALPHA for p in FP) / NFPR; G1 = FPR <= 0.10
PLM = [x for x in HOe if any((LS[x][i:i+8] > 0).all() and len(set(LS[x][i:i+8].tolist())) == 8 for i in range(len(LS[x]) - 7))]
rp = np.random.default_rng(SEED_PL); PL = []
for _ in range(NPL):
    for tries in range(1000):
        c = PLM[rp.integers(len(PLM))]; s = LS[c]
        if len(s) < 8: continue
        st = int(rp.integers(len(s) - 7)); w = s[st:st + 8].copy()
        if (w > 0).all() and len(set(w.tolist())) == 8: break
    w = w.copy(); j = int(rp.integers(1, 7)); d = int(rp.integers(1, 4)) * (1 if rp.random() < 0.5 else -1)
    w[j] = w[j] + d if w[j] + d > 0 else w[j] + abs(d)
    base = punit_a(rp); pos = int(rp.integers(len(base) + 1))
    sq = collapse(np.concatenate([base[:pos], w, base[pos:]]))
    p = pv(stats(sq)[0], NH); PL.append(dict(member=c, start=st, p=p, hit=p <= ALPHA))
POWER = sum(x['hit'] for x in PL) / NPL; G2 = POWER >= 0.80
def wilson(x, n, z=1.959964):
    ph = x / n; den = 1 + z * z / n; c = (ph + z * z / (2 * n)) / den; h = z * ((ph * (1 - ph) / n + z * z / (4 * n * n)) ** 0.5) / den
    return [c - h, c + h]
gates = A0['passed'] and G1 and G2 if not SMOKE else G1 and G2
p1, p2 = pv(T_ho, NH), pv(T_sel, NS)
order = sorted([('H1', p1), ('H2', p2)], key=lambda t: t[1]); holm = {}; alive = True
for i, (nm, p) in enumerate(order):
    thr = ALPHA / (2 - i); ok = alive and p <= thr; holm[nm] = dict(p=p, threshold=thr, rejected=ok); alive = ok
# descriptive
pos = {LOTe[t]: dict(i_in_A=int(I[t]), j_in_c=int(J[t]), K=int(K[t]), W=float(Wobs[LOTe[t]])) for t in range(len(LOTe))}
within = {}
for x in range(len(LOTe)):
    for y in range(x + 1, len(LOTe)):
        S = [LS[LOTe[x]], LS[LOTe[y]]]; Wv = wham(S, np.array([0], np.int64), np.array([1], np.int64))[0][0]; within[LOTe[x] + '·' + LOTe[y]] = float(Wv)
allmax = []
for k in range(len(ids)):
    if ids[k] in LS: continue
    allmax.append((float(Wpairs(cs[k], LOTe)[0].max()), ids[k]))
allmax.sort(reverse=True); rankA = [nm for _, nm in allmax].index(A) + 1
res = dict(source='KFG /workspace/kfg/kfg_20261111.db via K094 loader', mode=MODE96, k094_tool_sha256=K094_SHA, N=len(ids),
           lot=LOT, eligible_k094_rule=elig, lot_lengths={x: int(len(LS[x])) for x in LOTe}, held_out=HOe, plant_donors=PLM, selected=SEL, alpha=ALPHA, seeds=dict(reference=SEED_REF, fpr=SEED_FPR, plants=SEED_PL, next_free=6509),
           A0=A0, reference=dict(R=R, H1_null_q={q: float(np.quantile(NH, q)) for q in (0.5, 0.95, 0.99)}, H2_null_q={q: float(np.quantile(NS, q)) for q in (0.5, 0.95, 0.99)}),
           G1=dict(nulls=NFPR, share=FPR, passed=G1), G2=dict(plants=NPL, power=POWER, wilson95=wilson(sum(x['hit'] for x in PL), NPL), passed=G2),
           gates_passed=bool(gates))
if gates:
    res.update(H1=dict(T_ho=float(T_ho), p=p1), H2=dict(T_sel=float(T_sel), p=p2), holm=holm, W_vs_lot=pos, within_lot_W=within,
               rank_of_KH0147_by_max_W_vs_lot=dict(rank=rankA, of=len(allmax), top5=allmax[:5]))
else:
    res['note'] = 'gate failed: H1/H2 NOT TESTABLE, observed statistics not reported'
res['seconds'] = round(time.time() - g['t0'], 1)
json.dump(res, open(OUT, 'w'), indent=1); log('wrote', OUT, 'gates', gates)
