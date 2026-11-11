#!/usr/bin/env python3
"""K067 - pre-registered height arbitration of K026's flagged long / figure-eight knots (README line 4, decoding audit).
Question: K026 flagged knots whose value disagrees with their type: L-shift (L knot valued turns x 10^c, c >= 1), L-turn0 (L knot, 0 turns,
valued 10^c) and E-type (E knot valued 10^c in a non-units cluster). Does the knot cluster's PHYSICAL HEIGHT on the cord
(knot_cluster.START_POS) say 'units' (type/turns suspect -> the units reading) or 'claimed place c' (the value's place)?
Data: OKR khipu.db (sha256 in MANIFEST), duplicates out (DUPLICATE_FLAG = 1), top cords (CORD_CLASSIFICATION 'T') out, START_POS > 0.
Flagged knots: K026 classification verbatim (A0: counts must be L-shift 117, L-turn0 186, E-type 43 or the run stops EXCLUDED).
Reference clusters: U = exactly one knot, valid L (2..9 turns, value = turns) or E (value 1); P_c = 1..9 knots, all S, all valued 10^c.
Stratum = (khipu, CORD_LEVEL, claimed place c). Meter: m_u = median U heights, m_c = median P_c heights in the stratum; a cluster at
height h votes UNITS if |h - m_u| < |h - m_c|, CLAIMED if >, abstains on a tie. Stratum READABLE iff n_U >= 5, n_Pc >= 5 and
leave-one-out (LOO) accuracy >= 0.90 on both reference sides (ties count as errors). Per-cluster null rates (add-one, conservative):
e_c = (#P_c LOO votes UNITS + 1) / (n_Pc + 2); e_u = (#U LOO votes CLAIMED + 1) / (n_U + 2).
Per family: V_u = UNITS votes, V_c = CLAIMED votes among flagged clusters (one per cluster) in readable strata.
p_c = P(PoissonBinomial(e_c) >= V_u)  [H0c: they are genuine place-c clusters];  p_u = P(PoissonBinomial(e_u) >= V_c)  [H0u: genuine units].
Exact DP, no seed.
M2 (same-cord ORDER meter, co-primary; added after the smoke showed M1 can read almost no L-shift stratum because KH0103 AS090/N2 has
no clean S-tens clusters): flag B = the cluster has another valued cluster with a higher ORDINAL on its cord (K007: places decrease with
ordinal), i.e. it is NOT the lowest place. Rates per stratum from clean clusters (add-one): e2_u = (#U with B + 1)/(n_U + 2);
e2_c = (#P_c without B + 1)/(n_Pc + 2) (needs n_Pc >= 5). p2_u = P(PoiBin(e2_u) >= #B) [H0u]; p2_c = P(PoiBin(e2_c) >= #lowest) [H0c,
over flagged clusters whose stratum has a P_c reference]. E-type is NOT APPLICABLE under M2 (K026 defines it by cluster order: circular).
Holm over all computed p-values (M1 and M2, at most 10) at alpha 0.05; power bars use alpha/12 (stricter than any Holm step).
Verdicts per family: POSITION SAYS UNITS (H0c rejected, H0u not); POSITION SAYS CLAIMED PLACE (H0u rejected, H0c not); MIXED (both);
NEITHER EXCLUDED (neither, and both directions powered); M2 analogues 'ORDER SAYS ...'; NOT TESTABLE (< 5 flagged clusters in readable strata, or an unrejected
direction whose power < 0.80).
Gates, R = 200 trials per plant set, sizes = observed flagged counts per readable stratum (capped so >= 5 reference clusters remain):
 plant set A (seed 6413): clean P_c clusters removed from the reference and scored as if flagged -> FPR of p_c (share p_c <= 0.05 must be
   <= 0.10) and power of p_u (share p_u <= 0.05/12 must be >= 0.80);
 plant set B (seed 6414): clean U clusters likewise -> FPR of p_u (<= 0.10) and power of p_c (>= 0.80).
 M2: plant set B (seed 6415, clean U) -> FPR p2_u, power p2_c; plant set A (seed 6416, clean P_c) -> FPR p2_c, power p2_u.
 A rejection is only read if its own FPR gate passes; a non-rejection is only read as a negative if its power gate passes.
G0 fixture: PoissonBinomial DP vs brute-force enumeration on 20 random small cases; meter on a synthetic stratum.
A1 audit (runner, not this file): K066's tool re-run must reproduce analysis/k066_results.json bar runtime_s.
Smoke: K067_SMOKE=1 (R 20; writes /tmp/k067 only; never scores the flagged clusters).
Usage: python3 tools/k067_height_arbitration.py data/khipu.db [out.json]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import sqlite3, sys, os, json, time, hashlib, itertools, numpy as np
from collections import defaultdict, Counter
t0 = time.time()
SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
if hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest() != SHA: sys.exit('EXCLUDED: khipu.db hash differs from MANIFEST')
SMOKE = os.environ.get('K067_SMOKE') == '1'
OUT = '/tmp/k067/smoke.json' if SMOKE else (sys.argv[2] if len(sys.argv) > 2 else 'analysis/k067_results.json')
R = 20 if SMOKE else 200; ALPHA = 0.05; NMIN = 5; ACC = 0.90; FAM = ('L-shift', 'L-turn0', 'E-type')
def log(*a): print(*a, round(time.time() - t0, 1), flush=True)
c = sqlite3.connect('file:' + sys.argv[1] + '?mode=ro', uri=True)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
meta = {r[0]: ((r[1] or '') + ' ' + (r[2] or '')).strip() for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
cord = {r[0]: (r[1], r[2], (r[3] or '').strip()) for r in c.execute("select CORD_ID, KHIPU_ID, CORD_LEVEL, CORD_CLASSIFICATION from cord")}
KC = {r[0]: (r[1], r[2], r[3]) for r in c.execute("select CLUSTER_ID, CORD_ID, ORDINAL, START_POS from knot_cluster")}
maxord = defaultdict(lambda: -1)
for cl, (cd, o, h) in KC.items():
    if o is not None: maxord[cd] = max(maxord[cd], o)
def p10(v):
    if not v or v <= 0: return None
    k = 0
    while v % 10 == 0: v //= 10; k += 1
    return k if v == 1 else None
knots_by_cl = defaultdict(list); cat = {}; A0 = Counter()
for cd, t, v, cl, kid, tr in c.execute("select CORD_ID, TYPE_CODE, knot_value_type, CLUSTER_ID, KNOT_ID, NUM_TURNS from knot"):
    if cd not in cord or cord[cd][0] in dups: continue
    t = (t or '').strip(); knots_by_cl[cl].append((t, v, tr))
    # K026 H2 classification verbatim (audited knots only)
    if t == 'E': viol = v != 1
    elif t == 'L' and tr is not None: viol = not (2 <= tr <= 9 and v == int(tr))
    else: continue
    if not viol: continue
    f = None; claimed = None
    if t == 'E':
        k = p10(v)
        if v and k and k >= 1 and KC.get(cl, (None, None, None))[1] != maxord[cd]: f, claimed = 'E-type', k
    else:
        if 2 <= tr <= 9:
            if v and v % int(tr) == 0 and p10(v // int(tr)) and v != tr: f, claimed = 'L-shift', p10(v // int(tr))
        elif tr == 0: f, claimed = 'L-turn0', p10(v)   # None if the value is not a power of ten (counted, unscorable)
    if f: A0[f] += 1; cat.setdefault((f, cl), (claimed, kid))
A0 = dict(A0); log('A0 K026 counts', A0)
if A0 != {'L-shift': 117, 'L-turn0': 186, 'E-type': 43}: sys.exit('EXCLUDED: K026 classification not reproduced')
def place_of(cl):
    ks = knots_by_cl.get(cl, [])
    if len(ks) == 1 and ((ks[0][0] == 'L' and ks[0][2] is not None and 2 <= ks[0][2] <= 9 and ks[0][1] == int(ks[0][2])) or (ks[0][0] == 'E' and ks[0][1] == 1)): return 0
    if 1 <= len(ks) <= 9 and all(k[0] == 'S' for k in ks) and len({k[1] for k in ks}) == 1:
        q = p10(ks[0][1])
        if q is not None and q >= 1: return q
    return None
def usable(cl):
    cd, o, h = KC.get(cl, (None, None, None))
    if cd not in cord or h is None or float(h) <= 0: return None
    kh, lev, cls = cord[cd]
    if kh in dups or cls == 'T': return None
    return kh, lev, float(h)
valued_ords = defaultdict(list)
for cl, (cd, o, h) in KC.items():
    if o is not None and any((k[1] or 0) > 0 for k in knots_by_cl.get(cl, [])): valued_ords[cd].append(o)
def below(cl):
    """M2 order flag: another valued cluster on the same cord with a higher ORDINAL (K007: places decrease with ordinal)."""
    cd, o, h = KC[cl]
    return int(o is not None and any(x > o for x in valued_ords[cd]))
ref = defaultdict(list); ref2 = defaultdict(list)  # (kh, lev, place) -> heights (M1) / below flags (M2)
flagged_cl = {cl for (_, cl) in cat}
for cl in KC:
    if cl in flagged_cl: continue
    u = usable(cl); q = place_of(cl) if u else None
    if q is not None: ref[(u[0], u[1], q)].append(u[2]); ref2[(u[0], u[1], q)].append(below(cl))
FL = defaultdict(list); FL2 = defaultdict(list); scope = Counter()   # family -> [(stratum, height)]
for (f, cl), (claimed, kid) in sorted(cat.items()):
    u = usable(cl)
    if claimed is None: scope[f + ' unscorable value (not a power of ten)'] += 1; continue
    if claimed == 0: scope[f + ' claimed place is units (value 1): position cannot arbitrate'] += 1; continue
    if u is None: scope[f + ' no height / top cord'] += 1; continue
    FL[f].append(((u[0], u[1], claimed), u[2], kid)); FL2[f].append(((u[0], u[1], claimed), below(cl), kid))
def vote(h, mu, mc):
    du, dc = abs(h - mu), abs(h - mc)
    return 'U' if du < dc else ('C' if dc < du else 'T')
def calib(U, P):
    """LOO on both sides; returns (accU, accP, e_u, e_c)."""
    U = np.asarray(U); P = np.asarray(P); mc = np.median(P); mu = np.median(U)
    vu = [vote(U[i], np.median(np.delete(U, i)), mc) for i in range(len(U))]
    vp = [vote(P[i], mu, np.median(np.delete(P, i))) for i in range(len(P))]
    return (sum(v == 'U' for v in vu) / len(U), sum(v == 'C' for v in vp) / len(P),
            (sum(v == 'C' for v in vu) + 1) / (len(U) + 2), (sum(v == 'U' for v in vp) + 1) / (len(P) + 2))
def poibin_tail(ps, k):
    d = np.zeros(len(ps) + 1); d[0] = 1.0
    for p in ps: d[1:] = d[1:] * (1 - p) + d[:-1] * p; d[0] *= (1 - p)
    return float(min(1.0, d[k:].sum()))
# G0 fixture
rng0 = np.random.default_rng(0); g0 = 0
for _ in range(20):
    n = int(rng0.integers(1, 9)); ps = rng0.uniform(0, 0.5, n); k = int(rng0.integers(0, n + 1))
    bf = sum(np.prod([ps[i] if b[i] else 1 - ps[i] for i in range(n)]) for b in itertools.product([0, 1], repeat=n) if sum(b) >= k)
    g0 += abs(bf - poibin_tail(ps, k)) < 1e-12
syn = calib([1.0, 1.2, 0.9, 1.1, 1.05], [5.0, 5.2, 4.9, 5.1, 4.8])
G0 = dict(poibin_fixture=f'{g0}/20', synthetic_stratum_acc=syn[:2], passed=bool(g0 == 20 and syn[0] == 1 and syn[1] == 1))
log('G0', G0)
if not G0['passed']: sys.exit('EXCLUDED: G0 fixture failed')
# readable strata
strata = {}
for f in FAM:
    for (s, h, kid) in FL[f]:
        if s in strata: continue
        kh, lev, q = s; U = ref.get((kh, lev, 0), []); P = ref.get(s, [])
        if len(U) < NMIN or len(P) < NMIN: strata[s] = dict(readable=False, nU=len(U), nP=len(P)); continue
        aU, aP, eu, ec = calib(U, P)
        strata[s] = dict(readable=bool(aU >= ACC and aP >= ACC), nU=len(U), nP=len(P), accU=aU, accP=aP, e_u=eu, e_c=ec,
                         m_u=float(np.median(U)), m_c=float(np.median(P)))
def score(items, Uref, Pref):
    """items: [(stratum, h)]; references per stratum given; returns V_u, V_c, p_c, p_u."""
    vu = vc = 0; pc = []; pu = []
    for s, h in items:
        U = Uref[s]; P = Pref[s]; aU, aP, eu, ec = calib(U, P); v = vote(h, np.median(U), np.median(P))
        vu += v == 'U'; vc += v == 'C'; pc.append(ec); pu.append(eu)
    return vu, vc, poibin_tail(pc, vu), poibin_tail(pu, vc)
read_items = {f: [(s, h) for (s, h, kid) in FL[f] if strata[s]['readable']] for f in FAM}
gates = {}
for f, seed_off in zip(FAM, (0, 1, 2)):
    cnt = Counter(s for s, h in read_items[f]); gates[f] = {}
    if sum(cnt.values()) < NMIN: gates[f] = dict(testable=False, n_readable=sum(cnt.values())); continue
    for setname, seed, side in (('A_true_claimed', 6413, 'P'), ('B_true_units', 6414, 'U')):
        rng = np.random.default_rng([seed, seed_off]); pcs = []; pus = []
        for _ in range(R):
            items = []; Ur = {}; Pr = {}
            for s, n in cnt.items():
                kh, lev, q = s; U = list(ref[(kh, lev, 0)]); P = list(ref[s]); src = P if side == 'P' else U
                m = min(n, len(src) - NMIN)
                if m <= 0: continue
                pick = set(rng.choice(len(src), m, replace=False).tolist())
                planted = [src[i] for i in pick]; rest = [src[i] for i in range(len(src)) if i not in pick]
                if side == 'P': Ur[s], Pr[s] = U, rest
                else: Ur[s], Pr[s] = rest, P
                items += [(s, h) for h in planted]
            vu, vc, pc, pu = score(items, Ur, Pr); pcs.append(pc); pus.append(pu)
        pcs = np.array(pcs); pus = np.array(pus)
        if side == 'P': gates[f][setname] = dict(seed=[seed, seed_off], FPR_pc=float(np.mean(pcs <= ALPHA)), power_pu=float(np.mean(pus <= ALPHA / 12)))
        else: gates[f][setname] = dict(seed=[seed, seed_off], FPR_pu=float(np.mean(pus <= ALPHA)), power_pc=float(np.mean(pcs <= ALPHA / 12)))
    gA, gB = gates[f]['A_true_claimed'], gates[f]['B_true_units']
    gates[f].update(testable=True, n_readable=sum(cnt.values()), FPR_ok=bool(gA['FPR_pc'] <= 0.10 and gB['FPR_pu'] <= 0.10),
                    power_pc_ok=bool(gB['power_pc'] >= 0.80), power_pu_ok=bool(gA['power_pu'] >= 0.80))
    log('gates', f, gates[f])

# ---- M2: same-cord order meter ----
def rates2(Ub, Pb):
    e2u = (sum(Ub) + 1) / (len(Ub) + 2)
    e2c = (sum(1 - b for b in Pb) + 1) / (len(Pb) + 2) if len(Pb) >= NMIN else None
    return e2u, e2c
def score2(items, Uref, Pref):
    """items: [(stratum, below)]. Returns (#below, #lowest, p2_u over all items, p2_c over items with a P_c reference or None)."""
    nb = sum(b for s, b in items); pu = [rates2(Uref[s], Pref[s])[0] for s, b in items]
    ic = [(s, b) for s, b in items if len(Pref[s]) >= NMIN]
    p2u = poibin_tail(pu, nb) if items else None
    p2c = poibin_tail([rates2(Uref[s], Pref[s])[1] for s, b in ic], sum(1 - b for s, b in ic)) if len(ic) >= NMIN else None
    return nb, len(items) - nb, p2u, p2c, len(ic)
read2 = {f: [(s, b) for (s, b, kid) in FL2[f] if len(ref2.get((s[0], s[1], 0), [])) >= NMIN] for f in FAM}
read2['E-type'] = []   # circular: K026 defines E-type as 'not in the last cluster', which is the M2 order flag itself
gates2 = {}
for f, seed_off in zip(FAM, (0, 1, 2)):
    cnt = Counter(s for s, b in read2[f]); g = gates2[f] = dict(n_readable_u=len(read2[f]),
        n_readable_c=sum(1 for s, b in read2[f] if len(ref2.get(s, [])) >= NMIN))
    if len(read2[f]) < NMIN: g['testable'] = False; continue
    for setname, seed, side in (('B_true_units', 6415, 'U'), ('A_true_claimed', 6416, 'P')):
        rng = np.random.default_rng([seed, seed_off]); pus = []; pcs = []
        for _ in range(R):
            items = []; Ur = {}; Pr = {}
            for st, n in cnt.items():
                U = list(ref2[(st[0], st[1], 0)]); P = list(ref2.get(st, [])); src = U if side == 'U' else P
                m = min(n, len(src) - NMIN)
                if m <= 0: continue
                pick = set(rng.choice(len(src), m, replace=False).tolist())
                planted = [src[i] for i in pick]; rest = [src[i] for i in range(len(src)) if i not in pick]
                Ur[st], Pr[st] = (rest, P) if side == 'U' else (U, rest)
                items += [(st, b) for b in planted]
            if len(items) < NMIN: continue
            nb, nl, p2u, p2c, nc = score2(items, Ur, Pr); pus.append(p2u); pcs.append(np.nan if p2c is None else p2c)
        pus = np.array(pus, float); pcs = np.array(pcs, float); ok = ~np.isnan(pcs)
        rec = dict(seed=[seed, seed_off], trials=int(len(pus)))
        if side == 'U': rec.update(FPR_p2u=float(np.mean(pus <= ALPHA)) if len(pus) else None,
                                   power_p2c=float(np.mean(pcs[ok] <= ALPHA / 12)) if ok.any() else None)
        else: rec.update(FPR_p2c=float(np.mean(pcs[ok] <= ALPHA)) if ok.any() else None,
                         power_p2u=float(np.mean(pus <= ALPHA / 12)) if len(pus) else None)
        g[setname] = rec
    gB, gA = g['B_true_units'], g['A_true_claimed']
    g.update(testable=True, FPR_u_ok=bool(gB['FPR_p2u'] is not None and gB['FPR_p2u'] <= 0.10),
             FPR_c_ok=bool(gA['FPR_p2c'] is not None and gA['FPR_p2c'] <= 0.10),
             power_c_ok=bool(gB['power_p2c'] is not None and gB['power_p2c'] >= 0.80),
             power_u_ok=bool(gA['power_p2u'] is not None and gA['power_p2u'] >= 0.80))
    log('gates M2', f, g)
out = dict(A0_K026_counts=A0, gates_M2=gates2, n_flagged_M2_readable={f: len(read2[f]) for f in FAM}, scope_losses=dict(scope), n_flagged_with_height={f: len(FL[f]) for f in FAM},
           n_flagged_readable={f: len(read_items[f]) for f in FAM}, G0=G0, R=R, alpha=ALPHA, gates=gates,
           strata={f'{meta.get(s[0], s[0])} | level {s[1]} | place 10^{s[2]}': v for s, v in strata.items()})
if SMOKE:
    os.makedirs('/tmp/k067', exist_ok=True); json.dump(out, open(OUT, 'w'), indent=1, default=str); log('smoke only: flagged clusters not scored'); sys.exit(0)
# observed
res = {}; res2 = {}; praw = []
for f in FAM:
    it = read_items[f]
    if len(it) < NMIN: res[f] = dict(verdict='NOT TESTABLE', reason='fewer than 5 flagged clusters in readable strata', n=len(it)); continue
    Ur = {s: ref[(s[0], s[1], 0)] for s, h in it}; Pr = {s: ref[s] for s, h in it}
    vu, vc, pc, pu = score(it, Ur, Pr)
    per = Counter((meta.get(s[0], s[0]), vote(h, np.median(Ur[s]), np.median(Pr[s]))) for s, h in it)
    res[f] = dict(n=len(it), V_units=vu, V_claimed=vc, ties=len(it) - vu - vc, p_c=pc, p_u=pu,
                  per_khipu={f'{k} {v}': n for (k, v), n in sorted(per.items())})
    praw += [(pc, f, 'c'), (pu, f, 'u')]
for f in FAM:
    it = read2[f]
    if f == 'E-type': res2[f] = dict(verdict='NOT APPLICABLE', reason='circular: K026 E-type is defined by cluster order'); continue
    if len(it) < NMIN: res2[f] = dict(verdict='NOT TESTABLE', reason='fewer than 5 flagged clusters with a units reference', n=len(it)); continue
    Ur = {st: ref2[(st[0], st[1], 0)] for st, b in it}; Pr = {st: ref2.get(st, []) for st, b in it}
    nb, nl, p2u, p2c, nc = score2(it, Ur, Pr)
    res2[f] = dict(n=len(it), n_with_Pc_reference=nc, below=nb, lowest=nl, p2_u=p2u, p2_c=p2c,
                   per_khipu={f'{k} {"below" if b else "lowest"}': n for (k, b), n in sorted(Counter((meta.get(st[0], st[0]), b) for st, b in it).items())})
    praw.append((p2u, f, 'u2'))
    if p2c is not None: praw.append((p2c, f, 'c2'))
order = sorted(praw); m = len(order); stop = False; rej = set()
for i, (p, f, d) in enumerate(order):
    if not stop and p <= ALPHA / (m - i): rej.add((f, d))
    else: stop = True
for f in FAM:
    if 'verdict' in res[f]: continue
    g = gates[f]; rc = (f, 'c') in rej; ru = (f, 'u') in rej; res[f].update(H0c_rejected=rc, H0u_rejected=ru)
    if not g['FPR_ok']: v = 'NOT TESTABLE (FPR gate failed)'
    elif rc and ru: v = 'MIXED'
    elif rc: v = 'POSITION SAYS UNITS' + ('' if g['power_pu_ok'] else ' (H0u side low-power)')
    elif ru: v = 'POSITION SAYS CLAIMED PLACE' + ('' if g['power_pc_ok'] else ' (H0c side low-power)')
    else: v = 'NEITHER EXCLUDED' if (g['power_pc_ok'] and g['power_pu_ok']) else 'NOT TESTABLE (low power)'
    res[f]['verdict'] = v; log('H', f, res[f])
for f in FAM:
    if 'verdict' in res2[f]: continue
    g = gates2[f]; r = res2[f]; ru = (f, 'u2') in rej; rc = (f, 'c2') in rej; r.update(H0u_rejected=ru, H0c_rejected=rc)
    if ru and not g['FPR_u_ok']: v = 'NOT TESTABLE (FPR gate failed)'
    elif rc and ru: v = 'MIXED'
    elif ru: v = 'ORDER SAYS CLAIMED PLACE' + ('' if (r['p2_c'] is not None and g['power_c_ok']) else ' (H0c side not testable)')
    elif rc and g['FPR_c_ok']: v = 'ORDER SAYS UNITS' + ('' if g['power_u_ok'] else ' (H0u side low-power)')
    else: v = 'NEITHER EXCLUDED' if (g['power_u_ok'] and g['power_c_ok']) else 'NOT TESTABLE (low power)'
    r['verdict'] = v; log('H M2', f, r)
out.update(results=res, results_M2=res2, holm_m=m, runtime_s=round(time.time() - t0, 1))
json.dump(out, open(OUT, 'w'), indent=1, default=str); log('wrote', OUT)
