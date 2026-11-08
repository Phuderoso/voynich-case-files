#!/usr/bin/env python3
"""K040 - held-out corpus-wide whole-group detector (line 2 leftover).
Pre-registered in case-file/K040-holdout-wholegroup.md.
Discovery set KH0359/UR119 and KH0405/UR166 held out of every test.
Statistic G, plant and filters copied from tools/k025_whole_group_sums.py.
Usage: python3 tools/k040_holdout_wholegroup.py khipu.db [--smoke]
"""
import hashlib, json, os, sqlite3, sys, time
import numpy as np
from collections import defaultdict

t0 = time.time()
DB = sys.argv[1]
SMOKE = '--smoke' in sys.argv
EXPECTED_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
DISCOVERY = frozenset({'KH0359', 'KH0405'})
K025_JSON = 'analysis/k025_results.json'
EXPECTED_N_ALL = 369
EXPECTED_N_HOLDOUT = 367
EXPECTED_G_HOLDOUT = 23
R = 200 if SMOKE else 10000
N_CAL = 10 if SMOKE else 200
N_POW = 10 if SMOKE else 200
MS = (5, 9, 15)
M_PRIMARY = 9
ALPHA = 0.05
GATE = 0.08
POWER_BAR = 0.5
SEEDS = dict(nulls=4040, calib=4041, power=4042)
WALL = 520
OUT = 'analysis/k040_smoke.json' if SMOKE else 'analysis/k040_results.json'
CKPT = 'analysis/k040_smoke_checkpoint.json' if SMOKE else 'analysis/k040_checkpoint.json'


def stop_excluded(reason, extra=None):
    res = dict(decision=dict(excluded=True, reason=reason,
                             H1=dict(verdict='excluded'), H2=dict(verdict='excluded')),
               secs=round(time.time() - t0, 1))
    if extra:
        res.update(extra)
    json.dump(res, open(OUT, 'w'), indent=1)
    print('EXCLUDED:', reason, flush=True)
    sys.exit(0)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def groups_of(cl):
    g, last = [], object()
    for i, x in enumerate(cl):
        if x != last:
            g.append([i, i + 1])
            last = x
        else:
            g[-1][1] = i + 1
    return [(s, e) for s, e in g]


def prep(cl, n):
    pairs = []
    for s, e in groups_of(cl):
        if e - s < 2:
            continue
        if s - 1 >= 0:
            pairs.append((s - 1, s, e))
        if e < n:
            pairs.append((e, s, e))
    return np.array(pairs, np.int64).reshape(-1, 3)


def G(V, pr):
    if len(pr) == 0:
        return np.zeros(V.shape[0], np.int64)
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64)
    P[:, 1:] = np.cumsum(V, 1)
    Z = np.zeros((B, n + 1), np.int64)
    Z[:, 1:] = np.cumsum(V > 0, 1)
    i, s, e = pr[:, 0], pr[:, 1], pr[:, 2]
    vi = V[:, i]
    hit = (vi >= 10) & (vi == P[:, e] - P[:, s]) & ((Z[:, e] - Z[:, s]) >= 2)
    H = np.zeros((B, n), bool)
    for k in range(len(pr)):
        H[:, i[k]] |= hit[:, k]
    return H.sum(1)


def perm(v, B, rng):
    return v[np.argsort(rng.random((B, len(v))), 1)]


def pv(o, nl):
    return float((1 + (nl >= o).sum()) / (1 + len(nl)))


def bh(ps, q=0.05):
    ps = np.asarray(ps, float)
    m = len(ps)
    o = np.argsort(ps)
    ok = ps[o] <= q * np.arange(1, m + 1) / m
    kk = int(np.max(np.where(ok)[0]) + 1) if ok.any() else 0
    s = np.zeros(m, bool)
    s[o[:kk]] = True
    return s


def plant_one(x, pr, rng):
    x = x.copy()
    i, s, e = [int(v) for v in pr[rng.integers(len(pr))]]
    blk = x[s:e].copy()
    if (blk > 0).sum() < 2:
        blk[:2] = np.maximum(blk[:2], rng.integers(1, 30, 2))
    if int(blk.sum()) < 10:
        blk[0] += 10 - int(blk.sum())
    x[s:e] = blk
    x[i] = int(blk.sum())
    return x


def plant_k(x, pr, k, rng):
    x = x.copy()
    used = set()
    order = rng.permutation(len(pr))
    planted = 0
    for idx in order:
        i, s, e = [int(v) for v in pr[idx]]
        span = set(range(s, e))
        span.add(i)
        if used & span:
            continue
        blk = x[s:e].copy()
        if (blk > 0).sum() < 2:
            blk[:2] = np.maximum(blk[:2], rng.integers(1, 30, 2))
        if int(blk.sum()) < 10:
            blk[0] += 10 - int(blk.sum())
        x[s:e] = blk
        x[i] = int(blk.sum())
        used |= span
        planted += 1
        if planted >= k:
            break
    return x, planted


# --- Rule 1: hash, K025 file, data ---
got_sha = sha256_file(DB)
if got_sha != EXPECTED_SHA:
    stop_excluded(f'database hash mismatch: {got_sha}')

if not os.path.exists(K025_JSON):
    stop_excluded('k025_results.json missing')
try:
    k025 = json.load(open(K025_JSON))
except Exception as exc:  # noqa: BLE001
    stop_excluded(f'k025_results.json unreadable: {exc}')
k025_n = (k025.get('secondary') or {}).get('n_khipus')
if k025_n != EXPECTED_N_ALL:
    stop_excluded(f'K025 secondary n_khipus is {k025_n}, expected {EXPECTED_N_ALL}')
if 'KH0359' not in (k025.get('primary') or {}) or 'KH0405' not in k025['primary']:
    stop_excluded('K025 primary is missing KH0359 or KH0405')

c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute('select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1')}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute(
    'select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main')}
val = defaultdict(int)
for cid, v in c.execute('select CORD_ID, knot_value_type from knot'):
    if v is not None:
        val[cid] += int(v)
kh = defaultdict(list)
for khid, cid, cl in c.execute(
        'select KHIPU_ID, CORD_ID, CLUSTER_ID from cord '
        'where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL'):
    if khid in dups:
        continue
    kh[khid].append((val.get(cid, 0), cl))

eligible = []
for kid, cords in kh.items():
    cl = [x[1] for x in cords]
    if len(groups_of(cl)) < 4:
        continue
    v = np.array([x[0] for x in cords], np.int64)
    pr = prep(cl, len(v))
    if len(pr) == 0 or (v >= 10).sum() == 0:
        continue
    okr, inv = names[kid]
    eligible.append(dict(kid=kid, okr=okr, inv=inv, v=v, pr=pr,
                         n_pend=len(v), n_groups=len(groups_of(cl)),
                         n_pairs=len(pr)))

holdout = [e for e in eligible if e['okr'] not in DISCOVERY]
found_disc = sorted({e['okr'] for e in eligible if e['okr'] in DISCOVERY})
consistency = dict(
    sha256=got_sha,
    n_eligible=len(eligible),
    n_holdout=len(holdout),
    discovery_found=found_disc,
    k025_n_khipus=k025_n,
)
if len(eligible) != EXPECTED_N_ALL or len(holdout) != EXPECTED_N_HOLDOUT:
    stop_excluded(f'eligible/holdout counts {len(eligible)}/{len(holdout)} '
                  f'do not match {EXPECTED_N_ALL}/{EXPECTED_N_HOLDOUT}',
                  extra=dict(consistency=consistency))
if set(found_disc) != DISCOVERY:
    stop_excluded(f'discovery set incomplete: {found_disc}', extra=dict(consistency=consistency))

obs_G = int(sum(G(e['v'][None], e['pr'])[0] for e in holdout))
consistency['G_holdout'] = obs_G
if obs_G != EXPECTED_G_HOLDOUT:
    stop_excluded(f'holdout G is {obs_G}, expected {EXPECTED_G_HOLDOUT}',
                  extra=dict(consistency=consistency))

print(json.dumps(dict(smoke=SMOKE, R=R, N_CAL=N_CAL, N_POW=N_POW, seeds=SEEDS,
                      consistency=consistency), indent=1), flush=True)

# --- Nulls (seed 4040) ---
rng_n = np.random.default_rng(SEEDS['nulls'])
tot_n = np.zeros(R, np.int64)
rows = []
for i, e in enumerate(holdout):
    if time.time() - t0 > WALL:
        stop_excluded('wall hit before nulls finished',
                      extra=dict(consistency=consistency, power_khipus_reached=i))
    o = int(G(e['v'][None], e['pr'])[0])
    nl = G(perm(e['v'], R, rng_n), e['pr'])
    e['nl'] = nl
    e['G'] = o
    p = pv(o, nl)
    rows.append(dict(okr=e['okr'], inv=e['inv'], G=o, null_mean=float(nl.mean()), p=p,
                     n_pend=e['n_pend'], n_groups=e['n_groups'], n_pairs=e['n_pairs']))
    tot_n += nl
    if (i + 1) % 20 == 0 or i + 1 == len(holdout):
        json.dump(dict(reached=i + 1, n=len(holdout), G_so_far=int(sum(r['G'] for r in rows)),
                       secs=round(time.time() - t0, 1)), open(CKPT, 'w'))
        print(f'nulls {i + 1}/{len(holdout)} G={sum(r["G"] for r in rows)} '
              f'{time.time() - t0:.1f}s', flush=True)

p_corpus = pv(obs_G, tot_n)
sig = bh([r['p'] for r in rows])
for r, s in zip(rows, sig):
    r['bh'] = bool(s)
bh_khipus = [r for r in rows if r['bh']]
print(json.dumps(dict(G=obs_G, null_mean=float(tot_n.mean()), p_corpus=p_corpus,
                      n_bh=int(sig.sum()), bh_khipus=bh_khipus)), flush=True)

# --- Calibration (seed 4041) ---
calib = dict(capped=False, n=0)
if time.time() - t0 > WALL:
    calib['capped'] = True
else:
    rng_c = np.random.default_rng(SEEDS['calib'])
    n_false_corpus = 0
    n_false_bh = 0
    bh_false_counts = []
    for j in range(N_CAL):
        if time.time() - t0 > WALL:
            calib['capped'] = True
            break
        cal_tot = 0
        cal_ps = []
        for e in holdout:
            g_sh = int(G(rng_c.permutation(e['v'])[None], e['pr'])[0])
            cal_tot += g_sh
            cal_ps.append(pv(g_sh, e['nl']))
        if pv(cal_tot, tot_n) <= ALPHA:
            n_false_corpus += 1
        n_disc = int(bh(cal_ps).sum())
        bh_false_counts.append(n_disc)
        if n_disc:
            n_false_bh += 1
        calib['n'] = j + 1
    if calib['n']:
        calib.update(dict(
            fpr=n_false_corpus / calib['n'],
            bh_gate=n_false_bh / calib['n'],
            bh_false_mean=float(np.mean(bh_false_counts)) if bh_false_counts else None,
        ))
    print(json.dumps({k: calib[k] for k in calib if k != 'bh_false_counts'}, indent=1), flush=True)

# --- Power (seed 4042) ---
rng_p = np.random.default_rng(SEEDS['power'])
plantable = [e for e in holdout if len(e['pr']) > 0]
cand4 = [e for e in holdout if len(e['pr']) >= 4]
power = {}
for m in MS:
    rec = dict(m=m, n=0, hits=0, capped=False, rate=None)
    if time.time() - t0 > WALL:
        rec['capped'] = True
        power[str(m)] = rec
        continue
    hits = 0
    n_ok = 0
    for j in range(N_POW):
        if time.time() - t0 > WALL:
            rec['capped'] = True
            break
        if len(plantable) < m:
            break
        chosen = set(int(x) for x in rng_p.choice(len(plantable), size=m, replace=False))
        chosen_kids = {plantable[ix]['kid'] for ix in chosen}
        tot = 0
        for e in holdout:
            x = rng_p.permutation(e['v'])
            if e['kid'] in chosen_kids:
                x = plant_one(x, e['pr'], rng_p)
            tot += int(G(x[None], e['pr'])[0])
        n_ok += 1
        if pv(tot, tot_n) <= ALPHA:
            hits += 1
    rec.update(dict(n=n_ok, hits=hits, rate=(hits / n_ok) if n_ok else None))
    power[str(m)] = rec
    print(f'power m={m} {rec}', flush=True)


def h2_power(n_plant, n_rep):
    rec = dict(n_plant=n_plant, n=0, hits=0, skipped=0, capped=False, rate=None)
    if time.time() - t0 > WALL:
        rec['capped'] = True
        return rec
    pool = cand4 if n_plant >= 4 else plantable
    if not pool:
        return rec
    hits = 0
    n_ok = 0
    skipped = 0
    attempts = 0
    # redraw failed 4-plants; cap attempts so a stubborn wall cannot loop
    while n_ok < n_rep and attempts < n_rep * 5:
        if time.time() - t0 > WALL:
            rec['capped'] = True
            break
        attempts += 1
        e0 = pool[int(rng_p.integers(len(pool)))]
        x0 = rng_p.permutation(e0['v'])
        if n_plant >= 2:
            x0, got = plant_k(x0, e0['pr'], n_plant, rng_p)
            if got < n_plant:
                skipped += 1
                continue
        else:
            x0 = plant_one(x0, e0['pr'], rng_p)
        ps = []
        idx = None
        for j, e in enumerate(holdout):
            if e['kid'] == e0['kid']:
                g = int(G(x0[None], e['pr'])[0])
                idx = j
            else:
                g = int(G(rng_p.permutation(e['v'])[None], e['pr'])[0])
            ps.append(pv(g, e['nl']))
        n_ok += 1
        if idx is not None and bool(bh(ps)[idx]):
            hits += 1
    rec.update(dict(n=n_ok, hits=hits, skipped=skipped,
                    rate=(hits / n_ok) if n_ok else None))
    return rec


power_h2_4 = h2_power(4, N_POW)
print('H2 4-plant', power_h2_4, flush=True)
power_h2_1 = h2_power(1, N_POW)
print('H2 1-plant', power_h2_1, flush=True)

# --- Verdicts ---
h1 = dict(p=p_corpus, G=obs_G, null_mean=float(tot_n.mean()),
          fpr=calib.get('fpr'), power_m9=power[str(M_PRIMARY)].get('rate'),
          power_m9_n=power[str(M_PRIMARY)].get('n'),
          power_m5=power['5'].get('rate'), power_m15=power['15'].get('rate'))
if calib.get('capped') or calib.get('n', 0) < N_CAL or power[str(M_PRIMARY)].get('capped') \
        or (power[str(M_PRIMARY)].get('n') or 0) < (30 if not SMOKE else 1):
    if calib.get('fpr') is not None and calib['fpr'] > GATE:
        h1['verdict'] = 'excluded'
        h1['reason'] = 'corpus FPR > 0.08'
    elif calib.get('capped') or power[str(M_PRIMARY)].get('capped') \
            or (power[str(M_PRIMARY)].get('n') or 0) < (30 if not SMOKE else 1):
        h1['verdict'] = 'not testable'
        h1['reason'] = 'calibration or m=9 power capped or n too small'
    else:
        h1['verdict'] = 'not testable'
        h1['reason'] = 'insufficient calibration or power'
else:
    h1['meets_fpr'] = calib['fpr'] <= GATE
    h1['meets_power'] = power[str(M_PRIMARY)]['rate'] >= POWER_BAR
    h1['meets_alpha'] = p_corpus <= ALPHA
    if calib['fpr'] > GATE:
        h1['verdict'] = 'excluded'
        h1['reason'] = 'corpus FPR > 0.08'
    elif power[str(M_PRIMARY)]['rate'] < POWER_BAR:
        h1['verdict'] = 'not testable'
        h1['reason'] = 'm=9 plant power < 0.5'
    elif p_corpus <= ALPHA:
        h1['verdict'] = 'supported'
        h1['reason'] = 'p_corpus <= 0.05; calibrated and powered at m=9'
    else:
        h1['verdict'] = 'not supported'
        h1['reason'] = 'p_corpus > 0.05 with readable power at m=9'

h2 = dict(n_bh=int(sig.sum()), bh_khipus=bh_khipus,
          bh_gate=calib.get('bh_gate'),
          power_4plant=power_h2_4.get('rate'), power_4plant_n=power_h2_4.get('n'),
          power_1plant=power_h2_1.get('rate'), power_1plant_n=power_h2_1.get('n'))
min_n = 30 if not SMOKE else 1
if calib.get('capped') or calib.get('n', 0) < N_CAL:
    h2['verdict'] = 'not testable'
    h2['reason'] = 'BH calibration capped'
elif calib.get('bh_gate') is not None and calib['bh_gate'] > GATE:
    h2['verdict'] = 'excluded'
    h2['reason'] = 'BH-gate > 0.08'
elif int(sig.sum()) >= 1:
    h2['verdict'] = 'supported'
    h2['reason'] = 'at least one holdout BH discovery; gate passed'
elif power_h2_4.get('capped') or (power_h2_4.get('n') or 0) < min_n:
    h2['verdict'] = 'not testable'
    h2['reason'] = '4-plant power capped or n < 30'
elif (power_h2_4.get('rate') or 0) >= POWER_BAR:
    h2['verdict'] = 'not supported'
    h2['reason'] = 'no BH discoveries; readable against a 4-plant (UR119-strength) extra'
else:
    h2['verdict'] = 'not testable'
    h2['reason'] = 'no BH discoveries and 4-plant power < 0.5'

decision = dict(excluded=False, H1=h1, H2=h2)
res = dict(
    design=dict(discovery=sorted(DISCOVERY), R=R, N_CAL=N_CAL, N_POW=N_POW,
                seeds=SEEDS, alpha=ALPHA, gate=GATE, m_primary=M_PRIMARY, ms=list(MS),
                smoke=SMOKE, wall=WALL, expected_sha=EXPECTED_SHA),
    consistency=consistency,
    inherited_from_k025=dict(
        source=K025_JSON,
        primary_G={k: k025['primary'][k]['G'] for k in DISCOVERY},
        secondary_n=k025_n,
        posthoc_holdout_G=EXPECTED_G_HOLDOUT,
        note='same data and G; K040 is not an independent replication',
    ),
    observed=dict(G=obs_G, null_mean=float(tot_n.mean()), null_std=float(tot_n.std()),
                  p_corpus=p_corpus, n_holdout=len(holdout),
                  n_bh=int(sig.sum()),
                  top=sorted(rows, key=lambda r: (r['p'], -r['G']))[:15]),
    calibration=calib,
    power=power,
    power_h2_4plant=power_h2_4,
    power_h2_1plant=power_h2_1,
    decision=decision,
    secs=round(time.time() - t0, 1),
)
json.dump(res, open(OUT, 'w'), indent=1)
print(json.dumps(dict(decision=decision, secs=res['secs']), indent=1), flush=True)
