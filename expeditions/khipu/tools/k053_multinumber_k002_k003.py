#!/usr/bin/env python3
"""K053 - R5 multi-number-cord sensitivity of the FROZEN K002 detector D2 and K003 detector D5 (README line 8).
Pre-registered here and in case-file/K053-multinumber-k002-k003.md BEFORE any gate or corpus number was computed.
Usage (run from expeditions/khipu):  python3 tools/k053_multinumber_k002_k003.py /workspace/khipu/khipu.db {fixture|all}
  fixture = hash / R5-count / eligible-set / reproduction checks only (no gate, no corpus p-value).
  all     = fixture, then gates (seed 5353), masked D2 corpus (seed 5354), masked D5 corpus (seed 5355), summary.
  Each phase is checkpointed in analysis/k053_checkpoint.json; a rerun resumes finished phases unchanged.

QUESTION. Do the published K002 (D2, 16 BH names) and K003 (D5, 20 BH names) corpus detections survive when R5
multi-number cords are masked as in K008?

DATA. OKR khipu.db @ 4039ca5 (sha256 607913034a0f...c4db), level-1 pendants in CORD_ORDINAL order, duplicate-flagged
khipus removed, cord value = sum of knot values (as K002/K003). Universe = the 457 khipus of K002/K003 (>= 10 nonzero
pendants). A khipu is TESTABLE if it keeps >= 10 nonzero UNMASKED pendants; otherwise NOT TESTABLE (not lost).

R5 CORD (K007/K008). >= 2 knot clusters with a single decimal place, and those places, read in knot_cluster.ORDINAL
order, are not strictly decreasing. Expected count in the DB: 3069 (fixture gate).

MASK (K008, structure-preserving). An R5 pendant keeps its position but is never a sum target and never part of a
summand block (any k-block containing an R5 position is invalid). Null N1 = within-khipu permutation of the non-R5
values among the non-R5 positions. Everything else is frozen: D2 = sum of log10(v) over targets v >= 10 equal to an
adjacent left or right k-block sum, k = 2..6, block with >= 2 nonzero summands; D5 = min-p over W_2..W_12 (per-k
log-weighted hit scores), min-p calibrated against its own null exactly as in K003 (always-zero scores dropped).
No Stage 1/2 detector selection is rerun; line 1 (D5w / K036 F1 list) is not reopened.

CORPUS PROCEDURE (as K002/K003). For every testable khipu: K = 1000; if p <= 0.01, a fresh K = 20000 whose p
replaces the first; p = (1 + #null >= obs) / (1 + K) (for D5: #null min-p <= observed min-p). BH-FDR q = 0.05 over
all testable khipus, separately for D2 (seed 5354) and D5 (seed 5355). Khipus without any R5 pendant are recomputed
with the new seed too (same data, same statistic, fresh null).

GATES (seed 5353, one shared null per khipu for both detectors, K = 1000):
  G1 calibration FPR: for each testable khipu one masked shuffle (non-R5 values permuted) treated as real; rate of
     p <= 0.05. Gate: rate <= 0.05 per detector (the original K002/K003 rule). If G1 fails for a detector, its H1
     (survival) and H2 (new candidates) are NOT TESTABLE. Also reported: number of BH flags on the calibration p's.
  G2 planted recovery, spec A of K001/K002: on a masked shuffle of each testable khipu with >= 20 pendants, two
     targets are set to the sum of the next 3 pendants, where target and the 3 summands are all non-R5 and
     contiguous (a block the masked detector can see); if a block has < 2 nonzero values it gets values 1..29,
     if its sum < 10 the first summand is raised (as K002). Khipus with no such 4-window are skipped (reported).
     Power = rate of p <= 0.05. Binary gate: power >= 0.50 per detector. Failing G2 does not block reporting;
     it marks the detector UNDERPOWERED, so its drops are read only as "no longer established".
  G0 fixture: DB hash; R5 count == 3069; universe == K002's 457 khipu ids; with an all-False mask the masked
     scores reproduce K002 D2 'stat' for all 457 and K003's original per-k scores; with the real mask, khipus with
     0 R5 pendants reproduce K002's D2 stat. Any G0 failure stops the run.

DECISION RULES. A published K002 name SURVIVES if BH-significant under masked D2; a published K003 name SURVIVES if
BH-significant under masked D5. A name that drops is NO LONGER ESTABLISHED (masking cut or weakened the signal), not
excluded. Fewer than 10 nonzero unmasked pendants: NOT TESTABLE. A BH name absent from the original list is a NEW
CANDIDATE, reported but not claimed (same-data sensitivity). The fate of K001's 10 (KH0359, KH0405, KH0491, KH0492,
KH0503, KH0504, KH0506, KH0507, KH0513, KH0514) is reported under both detectors. Same-data caveat: reanalysis of
the same pinned corpus, not an independent replication.
"""
import sqlite3, sys, json, time, os, hashlib, numpy as np
from collections import defaultdict
DB, MODE = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'fixture')
SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
CK = 'analysis/k053_checkpoint.json'; OUT = 'analysis/k053_results.json'
SEED_G, SEED_D2, SEED_D5 = 5353, 5354, 5355
K1, K2, KG, MINP = 1000, 20000, 1000, 10
K001_10 = ['KH0359', 'KH0405', 'KH0491', 'KH0492', 'KH0503', 'KH0504', 'KH0506', 'KH0507', 'KH0513', 'KH0514']
t0 = time.time()
c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
val = defaultdict(int)
for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
    if v is not None: val[cid] += int(v)
# --- R5 definition, copied verbatim from K008 ---
def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
clplaces = defaultdict(set); clcord = {}
for cid, cl, t, v in c.execute("select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
    t = (t or '').strip()
    if t in ('S', 'L', 'E') and v: clplaces[cl].add(place(int(v)) if t == 'S' else 0)
    clcord[cl] = cid
ordn = {r[0]: r[1] for r in c.execute("select CLUSTER_ID, ORDINAL from knot_cluster")}
bycord = defaultdict(dict)
for cl, pl in clplaces.items():
    if len(pl) == 1 and ordn.get(cl) is not None: bycord[clcord[cl]][ordn[cl]] = next(iter(pl))
R5 = set()
for cd, d in bycord.items():
    s = [d[o] for o in sorted(d)]
    if len(s) >= 2 and not all(a > b for a, b in zip(s, s[1:])): R5.add(cd)
kh = defaultdict(list)
for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
    if khid in dups: continue
    kh[khid].append(cid)
data = []  # universe: K002/K003 rule (>= 10 nonzero pendants, unmasked)
for khid, cids in kh.items():
    v = np.array([val.get(x, 0) for x in cids], np.int64)
    if (v > 0).sum() < 10: continue
    data.append((khid, v, np.array([x in R5 for x in cids])))

def scores(V, bad):
    """Masked K003 scores. V (B,n), bad (n,) -> W (B,11) per-k log-weighted hits k=2..12, D2 (B,) (k<=6)."""
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    BD = np.zeros(n + 1, np.int64); BD[1:] = np.cumsum(bad)
    idx = np.arange(n); tgt = (V >= 10) & ~bad[None, :]; w = np.where(tgt, np.log10(np.maximum(V, 1)), 0.0)
    W = np.zeros((B, 11)); hs = np.zeros((B, n), bool)
    for k in range(2, 13):
        hk = np.zeros((B, n), bool)
        i = idx[idx + k < n]; ok = (BD[i + k + 1] - BD[i + 1]) == 0
        hk[:, i] |= ((P[:, i + k + 1] - P[:, i + 1]) == V[:, i]) & ((NZ[:, i + k + 1] - NZ[:, i + 1]) >= 2) & ok
        i = idx[idx - k >= 0]; ok = (BD[i] - BD[i - k]) == 0
        hk[:, i] |= ((P[:, i] - P[:, i - k]) == V[:, i]) & ((NZ[:, i] - NZ[:, i - k]) >= 2) & ok
        hk &= tgt; W[:, k - 2] = (w * hk).sum(1)
        if k <= 6: hs |= hk
    return W, (w * hs).sum(1)

def scores_orig(V):  # K003 scores(), verbatim logic, for the G0 reproduction check
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    NZ = np.zeros((B, n + 1), np.int64); NZ[:, 1:] = np.cumsum(V > 0, 1)
    idx = np.arange(n); big = V >= 10; w = np.where(big, np.log10(np.maximum(V, 1)), 0.0)
    W = np.zeros((B, 11)); hs = np.zeros((B, n), bool)
    for k in range(2, 13):
        hk = np.zeros((B, n), bool)
        i = idx[idx + k < n]
        hk[:, i] |= ((P[:, i + k + 1] - P[:, i + 1]) == V[:, i]) & ((NZ[:, i + k + 1] - NZ[:, i + 1]) >= 2)
        i = idx[idx - k >= 0]
        hk[:, i] |= ((P[:, i] - P[:, i - k]) == V[:, i]) & ((NZ[:, i] - NZ[:, i - k]) >= 2)
        hk &= big; W[:, k - 2] = (w * hk).sum(1)
        if k <= 6: hs |= hk
    return W, (w * hs).sum(1)

def colrank_p(N, x):
    Ns = np.sort(N, 0); K = N.shape[0]
    return np.stack([(K - np.searchsorted(Ns[:, j], x[:, j] - 1e-9, 'left')) / K for j in range(N.shape[1])], 1)
def permmask(rng, v, bad, B):
    free = np.where(~bad)[0]; out = np.tile(v, (B, 1))
    out[:, free] = v[free][rng.random((B, len(free))).argsort(1)]
    return out
def null_scores(rng, v, bad, B, chunk=2000):
    Ws, ds = [], []
    for s in range(0, B, chunk):
        W, d = scores(permmask(rng, v, bad, min(chunk, B - s)), bad); Ws.append(W); ds.append(d)
    return np.concatenate(Ws), np.concatenate(ds)
def p_both(x, bad, Wn, dn):
    """p for D2 and D5 of observed row x against null scores (Wn, dn)."""
    Wo, do = scores(x[None], bad); K = len(dn)
    p2 = (1 + (dn >= do[0] - 1e-9).sum()) / (1 + K)
    live = (Wn.max(0) > 0) | (Wo[0] > 0)
    if not live.any(): p5 = 1.0
    else:
        Nn, No = Wn[:, live], Wo[:, live]
        pn = colrank_p(Nn, Nn).min(1); po = colrank_p(Nn, No).min(1)[0]
        p5 = (1 + (pn <= po + 1e-12).sum()) / (1 + K)
    return float(p2), float(p5), float(do[0])
def bh(ps, q=0.05):
    ps = np.asarray(ps); m = len(ps); o = np.argsort(ps); thr = q * np.arange(1, m + 1) / m
    ok = ps[o] <= thr; kk = np.max(np.where(ok)[0]) + 1 if ok.any() else 0
    s = np.zeros(m, bool); s[o[:kk]] = True; return s
def plantA(rng, v, bad):
    pl = permmask(rng, v, bad, 1)[0]; n = len(pl)
    good = np.array([st for st in range(n - 3) if not bad[st:st + 4].any()])
    if len(good) == 0: return None
    for _ in range(2):
        st = int(rng.choice(good)); sl = slice(st + 1, st + 4); blk = pl[sl]
        if (blk > 0).sum() < 2: blk[:] = np.maximum(blk, rng.integers(1, 30, len(blk)))
        s = int(blk.sum())
        if s < 10: blk[0] += 10 - s; s = int(blk.sum())
        pl[sl] = blk; pl[st] = s
    return pl
ck = json.load(open(CK)) if os.path.exists(CK) else {}
def save(): json.dump(ck, open(CK, 'w'), indent=1)
testable = [(k, v, b) for k, v, b in data if ((v > 0) & ~b).sum() >= MINP]
# ---------------- G0 fixture ----------------
h = hashlib.sha256(open(DB, 'rb').read()).hexdigest()
k2 = {r['khipu_id']: r for r in json.load(open('analysis/k002_corpus.json'))['rows']}
k3 = {r['khipu_id']: r for r in json.load(open('analysis/k003_corpus.json'))['rows']}
rep_d2 = rep_w = rep_d2_masked0 = 0; n0 = 0
for khid, v, b in data:
    W0, d0 = scores(v[None], np.zeros(len(v), bool)); Wo, do = scores_orig(v[None])
    rep_d2 += int(abs(d0[0] - k2[khid]["stat"]) < 1e-9); rep_w += bool(np.allclose(W0, Wo))
    if not b.any():
        n0 += 1; rep_d2_masked0 += int(abs(scores(v[None], b)[1][0] - k2[khid]["stat"]) < 1e-9)
g0 = dict(sha256=h, sha_ok=h == SHA, n_r5=len(R5), r5_ok=len(R5) == 3069, n_universe=len(data),
          universe_ok=bool({k for k, _, _ in data} == set(k2) == set(k3) and len(data) == 457),
          d2_unmasked_reproduces=f'{rep_d2}/{len(data)}', w_unmasked_reproduces_k003=f'{rep_w}/{len(data)}',
          d2_zero_r5_reproduces=f'{rep_d2_masked0}/{n0}',
          n_with_r5=int(sum(b.any() for _, _, b in data)), n_testable=len(testable), n_not_testable=len(data) - len(testable),
          not_testable=[names[k][0] + '/' + names[k][1] for k, v, b in data if ((v > 0) & ~b).sum() < MINP])
g0['pass'] = bool(g0['sha_ok'] and g0['r5_ok'] and g0['universe_ok'] and rep_d2 == len(data) and rep_w == len(data)
                  and rep_d2_masked0 == n0)
print('G0', json.dumps({k: g0[k] for k in g0 if k != 'not_testable'}), flush=True)
if not g0['pass']: sys.exit('G0 fixture failed - stop')
if MODE == 'fixture':
    # synthetic smoke of the masked machinery (no real-data p-value): planted window on a toy khipu
    r = np.random.default_rng(0); v = r.integers(0, 40, 30); b = np.zeros(30, bool); b[[5, 6]] = True
    v[10] = v[11:14].sum() + (10 if v[11:14].sum() < 10 else 0); v[11] += v[10] - v[11:14].sum()
    W, d = scores(v[None], b); print('smoke toy D2', round(float(d[0]), 3), 'W>0 at k', list(np.where(W[0] > 0)[0] + 2))
    sys.exit(0)
ck['G0'] = g0
# ---------------- G1/G2 gates ----------------
if 'gates' not in ck:
    rng = np.random.default_rng(SEED_G); cal2, cal5, pw2, pw5, skipped = [], [], [], [], []
    for khid, v, b in testable:
        x = permmask(rng, v, b, 1)[0]; Wn, dn = null_scores(rng, x, b, KG)
        a, e, _ = p_both(x, b, Wn, dn); cal2.append(a); cal5.append(e)
        if len(v) >= 20:
            x = plantA(rng, v, b)
            if x is None: skipped.append(names[khid][0]); continue
            Wn, dn = null_scores(rng, x, b, KG); a, e, _ = p_both(x, b, Wn, dn); pw2.append(a); pw5.append(e)
    G = dict(seed=SEED_G, K=KG, calib_n=len(cal2), fpr_D2=float(np.mean(np.array(cal2) <= 0.05)),
             fpr_D5=float(np.mean(np.array(cal5) <= 0.05)), calib_bh_flags_D2=int(bh(cal2).sum()),
             calib_bh_flags_D5=int(bh(cal5).sum()), plant_n=len(pw2), plant_skipped_no_window=skipped,
             power_D2=float(np.mean(np.array(pw2) <= 0.05)), power_D5=float(np.mean(np.array(pw5) <= 0.05)))
    G['G1_D2'] = G['fpr_D2'] <= 0.05; G['G1_D5'] = G['fpr_D5'] <= 0.05
    G['G2_D2'] = G['power_D2'] >= 0.50; G['G2_D5'] = G['power_D5'] >= 0.50
    G['seconds'] = round(time.time() - t0, 1); ck['gates'] = G; save()
print('gates', json.dumps(ck['gates']), flush=True)
# ---------------- corpus scans ----------------
def corpus(det, seed):
    rng = np.random.default_rng(seed); rows = []; j = 0 if det == 'D2' else 1
    for khid, v, b in testable:
        Wn, dn = null_scores(rng, v, b, K1); r1 = p_both(v, b, Wn, dn); p1 = r1[j]; p = p1; kk = None
        if p1 <= 0.01:
            Wn, dn = null_scores(rng, v, b, K2); p = p_both(v, b, Wn, dn)[j]; kk = K2
        rows.append(dict(khipu_id=khid, okr=names[khid][0], inv=names[khid][1], n_pend=len(v), n_r5=int(b.sum()),
                         stat_D2=r1[2], p_stage1=p1, p=p, K2=kk))
    sig = bh([r['p'] for r in rows])
    for r, s in zip(rows, sig): r['bh_sig'] = bool(s)
    return rows
for det, seed in (('D2', SEED_D2), ('D5', SEED_D5)):
    if det not in ck:
        t1 = time.time(); ck[det] = dict(seed=seed, rows=corpus(det, seed), seconds=round(time.time() - t1, 1)); save()
    print(det, 'done', ck[det]['seconds'], flush=True)
# ---------------- summary ----------------
def summarise(det, orig):
    rows = {r['khipu_id']: r for r in ck[det]['rows']}; G = ck['gates']
    old = {k for k, r in orig.items() if r['bh_sig']}; new = {k for k, r in rows.items() if r['bh_sig']}
    lab = lambda k: names[k][0] + '/' + names[k][1]
    fate = {}
    for k in sorted(old, key=lambda k: names[k][0]):
        if k not in rows: fate[lab(k)] = 'not testable'
        else: fate[lab(k)] = 'survives' if rows[k]['bh_sig'] else 'no longer established'
    detail = [dict(name=lab(k), n_r5=rows[k]['n_r5'] if k in rows else None, p_orig=orig[k]['p'],
                   p_masked=rows[k]['p'] if k in rows else None, stat_D2_orig=k2[k]['stat'],
                   stat_D2_masked=rows[k]['stat_D2'] if k in rows else None, fate=fate[lab(k)])
              for k in sorted(old, key=lambda k: names[k][0])]
    gate_ok = G['G1_' + det]
    return dict(detector=det, n_tested=len(rows), n_p01=sum(r['p_stage1'] <= 0.01 for r in rows.values()),
                n_bh=len(new), orig_n_bh=len(old), survive=sum(v == 'survives' for v in fate.values()),
                lost=sum(v == 'no longer established' for v in fate.values()),
                not_testable=sum(v == 'not testable' for v in fate.values()),
                new_candidates=sorted(lab(k) for k in new - old), gate_G1=gate_ok, gate_G2=G['G2_' + det],
                verdict=('H1/H2 NOT TESTABLE (G1 failed)' if not gate_ok else
                         ('UNDERPOWERED (G2 failed)' if not G['G2_' + det] else 'gates pass')),
                names=detail)
S = dict(D2=summarise('D2', k2), D5=summarise('D5', k3))
okr = {names[k][0]: k for k in names}
S['k001_10'] = {n: dict(D2=next((d['fate'] for d in S['D2']['names'] if d['name'].startswith(n)), 'not in list'),
                        D5=next((d['fate'] for d in S['D5']['names'] if d['name'].startswith(n)), 'not in list'))
                for n in K001_10}
json.dump(dict(cycle='K053', db=f'OKR khipu.db @ 4039ca5 sha256 {h}', G0=ck['G0'], gates=ck['gates'], summary=S,
               rows_D2=ck['D2']['rows'], rows_D5=ck['D5']['rows'], seconds_total_this_run=round(time.time() - t0, 1)),
          open(OUT, 'w'), indent=1, default=str)
print(json.dumps({d: {k: S[d][k] for k in S[d] if k != 'names'} for d in ('D2', 'D5')}, indent=1))
for d in ('D2', 'D5'):
    for r in S[d]['names']: print(d, r)
print(json.dumps(S['k001_10'], indent=1)); print('seconds', round(time.time() - t0, 1))
