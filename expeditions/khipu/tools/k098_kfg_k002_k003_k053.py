#!/usr/bin/env python3
"""K098 - KFG re-audit (README line 9) of K002 (frozen D2), K003 (frozen D5) and their R5 multi-number sensitivity K053.
Pre-registered in case-file/K098-kfg-k002-k003-k053.md BEFORE any KFG D2/D5 statistic was computed.
Engine (scores, null, p, BH, spec-A plant) copied VERBATIM from tools/k053_multinumber_k002_k003.py (an all-False mask
is the unmasked K002/K003 detector, checked in G0 there). KFG pendants and R5 rule verbatim from tools/k080_kfg_k008_r5_mask.py
(K069 universe: KFG pendants p# in idx order, value column, >= 10 nonzero pendants, xlsx hash gate).
Usage (from expeditions/khipu): python3 tools/k098_kfg_k002_k003_k053.py {fixture|a0|all}
  fixture = KFG hashes, universe == K069's, R5 counts, list presence (no KFG D2/D5 statistic)
  a0      = exact OKR anchor rebuild: re-run tools/k053 on OKR in a scratch dir and compare to analysis/k053_results.json
  all     = fixture, gates (6513 unmasked, 6514 masked), scans U-D2 6515, U-D5 6516, M-D2 6517, M-D5 6518, summary.
Checkpoint analysis/k098_checkpoint.json. Next free seed 6519."""
import sqlite3, sys, json, time, os, re, glob, hashlib, shutil, subprocess, numpy as np
from collections import defaultdict
t0 = time.time(); MODE = sys.argv[1] if len(sys.argv) > 1 else 'fixture'
KFG_DB = '/workspace/kfg/kfg_20261111.db'; XLSX = '/workspace/kfg/xlsx'
CK = 'analysis/k098_checkpoint.json'; OUT = 'analysis/k098_results.json'
SEEDS = dict(G_U=6513, G_M=6514, U_D2=6515, U_D5=6516, M_D2=6517, M_D5=6518); NEXT_FREE = 6519
K1, K2, KG, MINP = 1000, 20000, 1000, 10
if MODE == 'a0':
    d = '/tmp/k098_a0'; shutil.rmtree(d, ignore_errors=True); os.makedirs(d + '/analysis'); os.makedirs(d + '/tools')
    for f in ('k002_corpus.json', 'k003_corpus.json'): shutil.copy('analysis/' + f, d + '/analysis/' + f)
    shutil.copy('tools/k053_multinumber_k002_k003.py', d + '/tools/')
    subprocess.run(['timeout', '600', 'python3', 'tools/k053_multinumber_k002_k003.py', '/workspace/khipu/khipu.db', 'all'], cwd=d,
                   check=True, stdout=open(d + '/run.log', 'w'), stderr=subprocess.STDOUT)
    A = json.load(open(d + '/analysis/k053_results.json')); P = json.load(open('analysis/k053_results.json'))
    res = dict(gates_equal=A['gates'] == P['gates'] or {k: (A['gates'][k], P['gates'][k]) for k in P['gates'] if k != 'seconds' and A['gates'][k] != P['gates'][k]} == {},
               rows_D2_equal=A['rows_D2'] == P['rows_D2'], rows_D5_equal=A['rows_D5'] == P['rows_D5'],
               summary_names_equal=all(A['summary'][x]['names'] == P['summary'][x]['names'] for x in ('D2', 'D5')),
               G0_equal={k: v for k, v in A['G0'].items()} == {k: v for k, v in P['G0'].items()})
    res['pass'] = all(res.values()); res['seconds'] = round(time.time() - t0, 1)
    json.dump(res, open('analysis/k098_a0.json', 'w'), indent=1); print(json.dumps(res)); sys.exit(0 if res['pass'] else 1)

# ---------------- engine (K053 verbatim) ----------------
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

# ---------------- KFG loader + R5 (K080 verbatim) ----------------
def place(v):
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
c = sqlite3.connect(KFG_DB); sha = dict(c.execute('select name, sha256 from khipu'))
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
pend = defaultdict(list)
for kh, idx, nm, v, kn in c.execute('select khipu, idx, cord_name, value, knots from cord order by khipu, idx'):
    m = PEN.match(str(nm or ''))
    if not m: continue
    try: x = int(float(v)) if v not in (None, '') else 0
    except Exception: x = 0
    pend[kh].append((int(m.group(1)), x, kfg_r5(kn)))
g0_bad = [f.split('/')[-1][:-5] for f in sorted(glob.glob(f'{XLSX}/*.xlsx'))
          if hashlib.sha256(open(f, 'rb').read()).hexdigest() != sha.get(f.split('/')[-1][:-5])]
data = []
for kh in sorted(pend):
    if kh in g0_bad: continue
    v = np.array([x for _, x, _ in pend[kh]], np.int64)
    if (v > 0).sum() < MINP: continue
    data.append((kh, v, np.array([b for _, _, b in pend[kh]], bool)))
k69 = {r['khipu'] for r in json.load(open('analysis/k069_results.json'))['rows']}
k2 = json.load(open('analysis/k002_corpus.json'))['rows']; k3 = json.load(open('analysis/k003_corpus.json'))['rows']
k53 = json.load(open('analysis/k053_results.json'))['summary']
L_U = dict(D2=sorted(r['okr'] for r in k2 if r['bh_sig']), D5=sorted(r['okr'] for r in k3 if r['bh_sig']))
L_M = {d: {x['name'].split('/')[0]: x['fate'] for x in k53[d]['names']} for d in ('D2', 'D5')}
okr_univ = {r['okr'] for r in k2}
testable = [(k, v, b) for k, v, b in data if ((v > 0) & ~b).sum() >= MINP]
univ = {k for k, _, _ in data}
fx = dict(kfg_xlsx_hash_mismatch=len(g0_bad), n_universe=len(data), universe_eq_k069=univ == k69,
          n_okr_universe_shared=len(univ & okr_univ), n_kfg_only=len(univ - okr_univ), n_okr_not_in_kfg=len(okr_univ - univ),
          r5_pendants=int(sum(b.sum() for _, _, b in data)), khipus_with_r5=int(sum(b.any() for _, _, b in data)),
          n_testable_masked=len(testable),
          lists_absent={a: {d: sorted(set(L[d]) - univ) for d in L} for a, L in (('U', L_U), ('M', L_M))},
          lists_untestable_masked={d: sorted(set(L_M[d]) - {k for k, _, _ in testable}) for d in L_M},
          n_list=dict(U_D2=len(L_U['D2']), U_D5=len(L_U['D5'])))
fx['pass'] = bool(not g0_bad and fx['universe_eq_k069'] and len(L_U['D2']) == 16 and len(L_U['D5']) == 20)
print('FIXTURE', json.dumps(fx), flush=True)
if MODE == 'fixture': sys.exit(0)
if not fx['pass']: json.dump(dict(fixture=fx, verdict='GATE FAIL (fixture)'), open(OUT, 'w'), indent=1); sys.exit('fixture fail')
a0 = json.load(open('analysis/k098_a0.json'))
if not a0['pass']: json.dump(dict(fixture=fx, a0=a0, verdict='GATE FAIL (A0)'), open(OUT, 'w'), indent=1); sys.exit('A0 fail')
ck = json.load(open(CK)) if os.path.exists(CK) else {}
def save(): json.dump(ck, open(CK, 'w'), indent=1)
ARMS = dict(U=[(k, v, np.zeros(len(v), bool)) for k, v, b in data], M=testable)
def gates(arm, seed):
    rng = np.random.default_rng(seed); cal2, cal5, pw2, pw5, skipped = [], [], [], [], []
    for khid, v, b in ARMS[arm]:
        x = permmask(rng, v, b, 1)[0]; Wn, dn = null_scores(rng, x, b, KG)
        a, e, _ = p_both(x, b, Wn, dn); cal2.append(a); cal5.append(e)
        if len(v) >= 20:
            x = plantA(rng, v, b)
            if x is None: skipped.append(khid); continue
            Wn, dn = null_scores(rng, x, b, KG); a, e, _ = p_both(x, b, Wn, dn); pw2.append(a); pw5.append(e)
    G = dict(seed=seed, K=KG, calib_n=len(cal2), fpr_D2=float(np.mean(np.array(cal2) <= 0.05)),
             fpr_D5=float(np.mean(np.array(cal5) <= 0.05)), calib_bh_flags_D2=int(bh(cal2).sum()),
             calib_bh_flags_D5=int(bh(cal5).sum()), plant_n=len(pw2), plant_skipped_no_window=skipped,
             power_D2=float(np.mean(np.array(pw2) <= 0.05)), power_D5=float(np.mean(np.array(pw5) <= 0.05)))
    G['G1_D2'] = G['fpr_D2'] <= 0.05; G['G1_D5'] = G['fpr_D5'] <= 0.05
    G['G2_D2'] = G['power_D2'] >= 0.50; G['G2_D5'] = G['power_D5'] >= 0.50
    return G
def corpus(arm, det, seed):
    rng = np.random.default_rng(seed); rows = []; j = 0 if det == 'D2' else 1
    for khid, v, b in ARMS[arm]:
        Wn, dn = null_scores(rng, v, b, K1); r1 = p_both(v, b, Wn, dn); p1 = r1[j]; p = p1; kk = None
        if p1 <= 0.01:
            Wn, dn = null_scores(rng, v, b, K2); p = p_both(v, b, Wn, dn)[j]; kk = K2
        rows.append(dict(khipu=khid, n_pend=len(v), n_r5=int(b.sum()), stat_D2=r1[2], p_stage1=p1, p=p, K2=kk))
    sig = bh([r['p'] for r in rows])
    for r, s in zip(rows, sig): r['bh_sig'] = bool(s)
    return rows
for arm in ('U', 'M'):
    key = 'gates_' + arm
    if key not in ck:
        t1 = time.time(); ck[key] = gates(arm, SEEDS['G_' + arm]); ck[key]['seconds'] = round(time.time() - t1, 1); save()
    print(key, json.dumps(ck[key]), flush=True)
for arm in ('U', 'M'):
    for det in ('D2', 'D5'):
        key = arm + '_' + det
        if key not in ck:
            t1 = time.time(); ck[key] = dict(seed=SEEDS[key], rows=corpus(arm, det, SEEDS[key]), seconds=round(time.time() - t1, 1)); save()
        print(key, 'done', ck[key]['seconds'], flush=True)
# ---------------- labels (pre-registered) ----------------
S = {}
for arm in ('U', 'M'):
    G = ck['gates_' + arm]
    for det in ('D2', 'D5'):
        rows = {r['khipu']: r for r in ck[arm + '_' + det]['rows']}
        g1, g2 = G['G1_' + det], G['G2_' + det]
        okr = ({n: 'BH' for n in L_U[det]} if arm == 'U' else
               {n: ('BH' if f == 'survives' else 'not BH' if f == 'no longer established' else 'not testable') for n, f in L_M[det].items()})
        out = {}
        for n, o in okr.items():
            r = rows.get(n)
            if not g1 or r is None or o == 'not testable': lab = 'NOT TESTABLE'; k = 'BH' if (r and r['bh_sig']) else ('not BH' if r else 'absent')
            else:
                k = 'BH' if r['bh_sig'] else 'not BH'
                if k == o: lab = 'REPLICATED'
                elif not g2 and o == 'BH': lab = 'NOT TESTABLE (underpowered drop)'
                else: lab = 'CHANGED'
            out[n] = dict(okr=o, kfg=k, label=lab, **({x: r[x] for x in ('n_r5', 'stat_D2', 'p')} if r else {}))
        new = sorted(k for k, r in rows.items() if r['bh_sig'] and k not in okr)
        S[arm + '_' + det] = dict(gate_G1=g1, gate_G2=g2, n_tested=len(rows), n_bh=sum(r['bh_sig'] for r in rows.values()),
                                  bh_bar=max([r['p'] for r in rows.values() if r['bh_sig']], default=None),
                                  n_replicated=sum(x['label'] == 'REPLICATED' for x in out.values()),
                                  n_changed=sum(x['label'] == 'CHANGED' for x in out.values()),
                                  n_not_testable=sum(x['label'].startswith('NOT TESTABLE') for x in out.values()),
                                  new_kfg_names=new, new_kfg_only=[k for k in new if k not in okr_univ], names=out)
json.dump(dict(cycle='K098', db='KFG kfg_20261111.db', fixture=fx, a0=a0, gates={a: ck['gates_' + a] for a in ('U', 'M')}, summary=S,
               seeds=SEEDS, next_free_seed=NEXT_FREE, rows={k: ck[k]['rows'] for k in ('U_D2', 'U_D5', 'M_D2', 'M_D5')},
               seconds=round(time.time() - t0, 1)), open(OUT, 'w'), indent=1, default=str)
for k, v in S.items(): print(k, json.dumps({x: v[x] for x in v if x != 'names'}))
for k, v in S.items():
    for n, x in v['names'].items(): print(k, n, x)
print('seconds', round(time.time() - t0, 1))
