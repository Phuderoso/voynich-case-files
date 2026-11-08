#!/usr/bin/env python3
"""K042 — does the leftover count excess live in singleton-total pairs? (line 2).
Pre-registered in case-file/K042-singleton-count.md.
Discovery set KH0359/UR119 and KH0405/UR166 held out of every test.
Hit definition, singleton_total and plant copied from tools/k040_holdout_wholegroup.py
and tools/k041_leftover_form_audit.py.
Usage: python3 tools/k042_singleton_count.py khipu.db [--smoke]
"""
import hashlib, json, os, sqlite3, sys, time
from collections import defaultdict
import numpy as np

t0 = time.time()
DB = sys.argv[1]
SMOKE = '--smoke' in sys.argv
EXPECTED_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
DISCOVERY = frozenset({'KH0359', 'KH0405'})
K025_JSON = 'analysis/k025_results.json'
EXPECTED_N_ALL = 369
EXPECTED_N_HOLDOUT = 367
EXPECTED_G_HOLDOUT = 23
EXPECTED_G_S = 10
EXPECTED_G_NS = 13
R = 200 if SMOKE else 10000
N_CAL = 10 if SMOKE else 200
N_POW = 10 if SMOKE else 200
M_PLANT = 9
ALPHA_FAM = 0.05
N_H = 2
ALPHA = ALPHA_FAM / N_H
GATE = 0.08
POWER_BAR = 0.5
SEEDS = dict(nulls=4242, calib=4243, power=4244)
WALL = 520
MIN_N = 1 if SMOKE else 30
OUT = 'analysis/k042_smoke.json' if SMOKE else 'analysis/k042_results.json'
CKPT = 'analysis/k042_smoke_checkpoint.json' if SMOKE else 'analysis/k042_checkpoint.json'


def stop_excluded(reason, extra=None):
    res = dict(decision=dict(excluded=True, reason=reason,
                             H1=dict(verdict='excluded'),
                             H2=dict(verdict='excluded')),
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


def pendant_sing(cl):
    n = len(cl)
    sing = np.zeros(n, bool)
    for s, e in groups_of(cl):
        if e - s == 1:
            sing[s:e] = True
    return sing


def pair_forms(cl, pr):
    n = len(cl)
    csz = np.zeros(n, np.int64)
    for s, e in groups_of(cl):
        csz[s:e] = e - s
    out = []
    for i, s, e in pr:
        i, s, e = int(i), int(s), int(e)
        side = 'L' if i < s else 'R'
        out.append((side, int(e - s), bool(csz[i] == 1)))
    return out


def hit_mask(V, pr):
    if len(pr) == 0:
        return np.zeros((V.shape[0], 0), bool)
    B, n = V.shape
    P = np.zeros((B, n + 1), np.int64)
    P[:, 1:] = np.cumsum(V, 1)
    Z = np.zeros((B, n + 1), np.int64)
    Z[:, 1:] = np.cumsum(V > 0, 1)
    i, s, e = pr[:, 0], pr[:, 1], pr[:, 2]
    vi = V[:, i]
    return (vi >= 10) & (vi == P[:, e] - P[:, s]) & ((Z[:, e] - Z[:, s]) >= 2)


def G_split(V, pr, sing):
    """Distinct-pendant whole-group-sum counts, split by singleton_total."""
    B, n = V.shape
    if len(pr) == 0:
        z = np.zeros(B, np.int64)
        return z, z.copy()
    mask = hit_mask(V, pr)
    H = np.zeros((B, n), bool)
    for k in range(len(pr)):
        H[:, int(pr[k, 0])] |= mask[:, k]
    gs = H[:, sing].sum(1).astype(np.int64)
    gns = H[:, ~sing].sum(1).astype(np.int64)
    return gs, gns


def perm(v, B, rng):
    return v[np.argsort(rng.random((B, len(v))), 1)]


def p_ge(obs, nulls):
    nulls = np.asarray(nulls, float)
    return float((1 + (nulls >= obs).sum()) / (1 + len(nulls)))


def extract_catalog(v, e):
    mask = hit_mask(v[None], e['pr'])[0]
    rows = []
    seen_i = set()
    both_i = set()
    hits_by_i = defaultdict(list)
    for k in np.flatnonzero(mask):
        i, s, ee = [int(x) for x in e['pr'][k]]
        hits_by_i[i].append(k)
    for i, ks in hits_by_i.items():
        if len(ks) > 1:
            both_i.add(i)
    for k in np.flatnonzero(mask):
        i, s, ee = [int(x) for x in e['pr'][k]]
        side, glen, sing = e['forms'][k]
        rows.append(dict(
            okr=e['okr'], inv=e['inv'],
            pendant_index=i,
            cord_ordinal=int(e['ordinals'][i]),
            cord_id=int(e['cids'][i]),
            value=int(v[i]),
            side=side,
            group_len=int(glen),
            singleton_total=bool(sing),
            group_start=s,
            group_end=int(ee),
            both_sides=i in both_i,
        ))
        seen_i.add(i)
    return rows, seen_i, both_i


def distinct_hits(rows):
    """One record per pendant (K040 G convention). First pair kept if both sides."""
    out = []
    seen = set()
    for r in rows:
        key = (r['okr'], r['pendant_index'])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def plant_one_pair(x, i, s, e, rng):
    x = x.copy()
    blk = x[s:e].copy()
    if (blk > 0).sum() < 2:
        blk[:2] = np.maximum(blk[:2], rng.integers(1, 30, 2))
    if int(blk.sum()) < 10:
        blk[0] += 10 - int(blk.sum())
    x[s:e] = blk
    x[i] = int(blk.sum())
    return x


def capacity(holdout, pred):
    n = 0
    for e in holdout:
        used = set()
        for k, form in enumerate(e['forms']):
            if not pred(form):
                continue
            i, s, ee = [int(x) for x in e['pr'][k]]
            span = set(range(s, ee))
            span.add(i)
            if used & span:
                continue
            used |= span
            n += 1
    return n


def plant_corpus(holdout, rng, m, pred):
    xs = {e['kid']: rng.permutation(e['v']) for e in holdout}
    cands = []
    for e in holdout:
        for k, form in enumerate(e['forms']):
            if pred(form):
                i, s, ee = [int(x) for x in e['pr'][k]]
                cands.append((e['kid'], k, i, s, ee))
    if not cands:
        return xs, 0
    order = rng.permutation(len(cands))
    used = defaultdict(set)
    planted = 0
    for idx in order:
        kid, _k, i, s, ee = cands[idx]
        span = set(range(s, ee))
        span.add(i)
        if used[kid] & span:
            continue
        xs[kid] = plant_one_pair(xs[kid], i, s, ee, rng)
        used[kid] |= span
        planted += 1
        if planted >= m:
            break
    return xs, planted


def counts_from_xs(holdout, xs):
    gs_tot = 0
    gns_tot = 0
    for e in holdout:
        gs, gns = G_split(xs[e['kid']][None], e['pr'], e['sing'])
        gs_tot += int(gs[0])
        gns_tot += int(gns[0])
    return gs_tot, gns_tot


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
for khid, cid, cl, cord_ord in c.execute(
        'select KHIPU_ID, CORD_ID, CLUSTER_ID, CORD_ORDINAL from cord '
        'where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL'):
    if khid in dups:
        continue
    kh[khid].append((val.get(cid, 0), cl, cid, cord_ord))

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
    forms = pair_forms(cl, pr)
    sing = pendant_sing(cl)
    eligible.append(dict(
        kid=kid, okr=okr, inv=inv, v=v, pr=pr, cl=cl, forms=forms, sing=sing,
        cids=np.array([x[2] for x in cords], np.int64),
        ordinals=np.array([x[3] for x in cords], np.int64),
        n_pend=len(v), n_groups=len(groups_of(cl)), n_pairs=len(pr),
    ))

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

obs_rows = []
obs_ids = set()
obs_both = set()
for e in holdout:
    rows, seen, both = extract_catalog(e['v'], e)
    obs_rows.extend(rows)
    obs_ids |= {e['okr'] + f':{i}' for i in seen}
    obs_both |= {e['okr'] + f':{i}' for i in both}
obs_hits = distinct_hits(obs_rows)
obs_G = len(obs_hits)
obs_Gs_rows = [r for r in obs_hits if r['singleton_total']]
obs_Gns_rows = [r for r in obs_hits if not r['singleton_total']]
obs_Gs = len(obs_Gs_rows)
obs_Gns = len(obs_Gns_rows)
consistency.update(dict(
    G_holdout=obs_G,
    G_s=obs_Gs,
    G_ns=obs_Gns,
    n_pairs=len(obs_rows),
    n_both=len(obs_both),
    G_s_plus_G_ns=obs_Gs + obs_Gns,
))
if obs_G != EXPECTED_G_HOLDOUT:
    stop_excluded(f'holdout G is {obs_G}, expected {EXPECTED_G_HOLDOUT}',
                  extra=dict(consistency=consistency))
if obs_Gs != EXPECTED_G_S:
    stop_excluded(f'holdout G_s is {obs_Gs}, expected {EXPECTED_G_S}',
                  extra=dict(consistency=consistency))
if obs_Gns != EXPECTED_G_NS:
    stop_excluded(f'holdout G_ns is {obs_Gns}, expected {EXPECTED_G_NS}',
                  extra=dict(consistency=consistency))

print(json.dumps(dict(smoke=SMOKE, R=R, N_CAL=N_CAL, N_POW=N_POW, seeds=SEEDS,
                      alpha=ALPHA, consistency=consistency), indent=1), flush=True)

# --- Nulls (seed 4242) ---
rng_n = np.random.default_rng(SEEDS['nulls'])
tot_s = np.zeros(R, np.int64)
tot_ns = np.zeros(R, np.int64)
for i, e in enumerate(holdout):
    if time.time() - t0 > WALL:
        stop_excluded('wall hit before nulls finished',
                      extra=dict(consistency=consistency, power_khipus_reached=i))
    gs, gns = G_split(perm(e['v'], R, rng_n), e['pr'], e['sing'])
    tot_s += gs
    tot_ns += gns
    if (i + 1) % 20 == 0 or i + 1 == len(holdout):
        json.dump(dict(reached=i + 1, n=len(holdout),
                       secs=round(time.time() - t0, 1)), open(CKPT, 'w'))
        print(f'nulls {i + 1}/{len(holdout)} {time.time() - t0:.1f}s', flush=True)

tot_G = tot_s + tot_ns
p1 = p_ge(obs_Gs, tot_s)
p2 = p_ge(obs_Gns, tot_ns)
print(json.dumps(dict(
    G=obs_G, G_s=obs_Gs, G_ns=obs_Gns,
    null_G_mean=float(tot_G.mean()), null_G_sd=float(tot_G.std()),
    null_Gs_mean=float(tot_s.mean()), null_Gs_sd=float(tot_s.std()),
    null_Gns_mean=float(tot_ns.mean()), null_Gns_sd=float(tot_ns.std()),
    p1=p1, p2=p2,
), indent=1), flush=True)

# --- Calibration (seed 4243) ---
calib = dict(capped=False, n=0)
if time.time() - t0 > WALL:
    calib['capped'] = True
else:
    rng_c = np.random.default_rng(SEEDS['calib'])
    false = dict(H1=0, H2=0, any=0)
    for j in range(N_CAL):
        if time.time() - t0 > WALL:
            calib['capped'] = True
            break
        xs = {e['kid']: rng_c.permutation(e['v']) for e in holdout}
        gs_tot, gns_tot = counts_from_xs(holdout, xs)
        f1 = p_ge(gs_tot, tot_s) <= ALPHA
        f2 = p_ge(gns_tot, tot_ns) <= ALPHA
        false['H1'] += int(f1)
        false['H2'] += int(f2)
        false['any'] += int(f1 or f2)
        calib['n'] = j + 1
    if calib['n']:
        calib.update(dict(
            fpr_H1=false['H1'] / calib['n'],
            fpr_H2=false['H2'] / calib['n'],
            fpr_any=false['any'] / calib['n'],
        ))
    print(json.dumps(calib, indent=1), flush=True)

# --- Power (seed 4244) ---
h1_capacity = capacity(holdout, lambda f: f[2])
h2_capacity = capacity(holdout, lambda f: not f[2])
rng_p = np.random.default_rng(SEEDS['power'])


def power_for(pred, which):
    rec = dict(which=which, n=0, hits=0, skipped=0, capped=False, rate=None)
    if time.time() - t0 > WALL:
        rec['capped'] = True
        return rec
    hits = 0
    n_ok = 0
    skipped = 0
    attempts = 0
    while n_ok < N_POW and attempts < N_POW * 5:
        if time.time() - t0 > WALL:
            rec['capped'] = True
            break
        attempts += 1
        xs, got = plant_corpus(holdout, rng_p, M_PLANT, pred)
        if got < M_PLANT:
            skipped += 1
            continue
        gs_tot, gns_tot = counts_from_xs(holdout, xs)
        stat = gs_tot if which == 'H1' else gns_tot
        nulls = tot_s if which == 'H1' else tot_ns
        n_ok += 1
        if p_ge(stat, nulls) <= ALPHA:
            hits += 1
    rec.update(dict(n=n_ok, hits=hits, skipped=skipped,
                    rate=(hits / n_ok) if n_ok else None,
                    attempts=attempts))
    return rec


power = {}
power['H1'] = power_for(lambda f: f[2], 'H1')
power['H1']['capacity'] = int(h1_capacity)
print('power H1', power['H1'], flush=True)
power['H2'] = power_for(lambda f: not f[2], 'H2')
power['H2']['capacity'] = int(h2_capacity)
print('power H2', power['H2'], flush=True)


def decide(name, p, fpr, powrec):
    out = dict(p=p, fpr=fpr, power=powrec.get('rate'), power_n=powrec.get('n'),
               alpha=ALPHA)
    if calib.get('capped') or calib.get('n', 0) < N_CAL:
        if fpr is not None and fpr > GATE:
            out['verdict'] = 'excluded'
            out['reason'] = f'{name} FPR > 0.08 (partial calibration)'
        else:
            out['verdict'] = 'not testable'
            out['reason'] = 'calibration capped or n too small'
        return out
    if fpr is not None and fpr > GATE:
        out['verdict'] = 'excluded'
        out['reason'] = f'{name} FPR > 0.08'
        return out
    if powrec.get('capped') or (powrec.get('n') or 0) < MIN_N:
        out['verdict'] = 'not testable'
        out['reason'] = 'm=9 power capped or n < 30'
        return out
    if (powrec.get('rate') or 0) < POWER_BAR:
        out['verdict'] = 'not testable'
        out['reason'] = 'm=9 plant power < 0.5'
        return out
    if p <= ALPHA:
        out['verdict'] = 'supported'
        out['reason'] = f'p <= {ALPHA:.6f}; calibrated and powered at m=9'
    else:
        out['verdict'] = 'not supported'
        out['reason'] = f'p > {ALPHA:.6f} with readable power at m=9'
    return out


h1 = decide('H1', p1, calib.get('fpr_H1'), power['H1'])
h1.update(dict(stat='G_s', obs=obs_Gs,
               null_mean=float(tot_s.mean()), null_sd=float(tot_s.std()),
               capacity=int(h1_capacity)))
h2 = decide('H2', p2, calib.get('fpr_H2'), power['H2'])
h2.update(dict(stat='G_ns', obs=obs_Gns,
               null_mean=float(tot_ns.mean()), null_sd=float(tot_ns.std()),
               capacity=int(h2_capacity)))

v1, v2 = h1['verdict'], h2['verdict']
if v1 == 'supported' and v2 == 'not supported':
    reading = 'leftover count excess lives in the singleton-total pairs'
elif v1 == 'supported' and v2 == 'supported':
    reading = 'leftover excess is broader than the singleton-total form'
elif v1 == 'not supported' and v2 == 'supported':
    reading = 'leftover excess lives outside singleton-totals'
elif v1 == 'not supported' and v2 == 'not supported':
    reading = 'count excess not recovered when split'
else:
    reading = f'partial: H1={v1}, H2={v2}'

decision = dict(excluded=False, H1=h1, H2=h2, reading=reading)
gs_cat = sorted(obs_Gs_rows, key=lambda r: (r['okr'], r['pendant_index'], r['side']))
gns_cat = sorted(obs_Gns_rows, key=lambda r: (r['okr'], r['pendant_index'], r['side']))
res = dict(
    design=dict(discovery=sorted(DISCOVERY), R=R, N_CAL=N_CAL, N_POW=N_POW,
                seeds=SEEDS, alpha_fam=ALPHA_FAM, n_h=N_H, alpha=ALPHA,
                gate=GATE, m_plant=M_PLANT, smoke=SMOKE, wall=WALL,
                expected_sha=EXPECTED_SHA),
    consistency=consistency,
    inherited_from=dict(
        note=('same holdout and G=23 as K040; G_s=10 matches K041 singleton-total '
              'pairs (n_both=0 so pairs=pendants); K042 decomposes the leftover count, '
              'it is not an independent replication'),
        G_holdout=EXPECTED_G_HOLDOUT,
        G_s=EXPECTED_G_S,
        G_ns=EXPECTED_G_NS,
    ),
    observed=dict(
        G=obs_G, G_s=obs_Gs, G_ns=obs_Gns,
        n_pairs=len(obs_rows), n_both=len(obs_both),
        G_s_plus_G_ns=obs_Gs + obs_Gns,
        catalogue_Gs=gs_cat,
        catalogue_Gns=gns_cat,
        Gs_khipus=sorted({r['okr'] for r in gs_cat}),
        Gns_khipus=sorted({r['okr'] for r in gns_cat}),
    ),
    null=dict(
        G_mean=float(tot_G.mean()), G_sd=float(tot_G.std()),
        Gs_mean=float(tot_s.mean()), Gs_sd=float(tot_s.std()),
        Gns_mean=float(tot_ns.mean()), Gns_sd=float(tot_ns.std()),
        p1=p1, p2=p2,
    ),
    calibration=calib,
    power=power,
    decision=decision,
    secs=round(time.time() - t0, 1),
)
json.dump(res, open(OUT, 'w'), indent=1)
print(json.dumps(dict(decision=decision, secs=res['secs']), indent=1), flush=True)
