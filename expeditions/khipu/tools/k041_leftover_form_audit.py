#!/usr/bin/env python3
"""K041 — form-audit of the K040 leftover 23 whole-group-sum hits (line 2).
Pre-registered in case-file/K041-leftover-form-audit.md.
Discovery set KH0359/UR119 and KH0405/UR166 held out of every test.
Hit definition and plant copied from tools/k040_holdout_wholegroup.py.
Usage: python3 tools/k041_leftover_form_audit.py khipu.db [--smoke]
"""
import hashlib, json, os, sqlite3, sys, time
from collections import Counter, defaultdict
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
R = 200 if SMOKE else 10000
N_CAL = 10 if SMOKE else 200
N_POW = 10 if SMOKE else 200
M_PLANT = 9
ALPHA_FAM = 0.05
N_H = 3
ALPHA = ALPHA_FAM / N_H
GATE = 0.08
POWER_BAR = 0.5
SEEDS = dict(nulls=4141, calib=4142, power=4143)
WALL = 520
MIN_N = 1 if SMOKE else 30
OUT = 'analysis/k041_smoke.json' if SMOKE else 'analysis/k041_results.json'
CKPT = 'analysis/k041_smoke_checkpoint.json' if SMOKE else 'analysis/k041_checkpoint.json'


def stop_excluded(reason, extra=None):
    res = dict(decision=dict(excluded=True, reason=reason,
                             H1=dict(verdict='excluded'),
                             H2=dict(verdict='excluded'),
                             H3=dict(verdict='excluded')),
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


def G_from_mask(mask, pr):
    if mask.size == 0:
        return np.zeros(mask.shape[0], np.int64)
    B = mask.shape[0]
    n = int(pr[:, 0].max()) + 1 if len(pr) else 0
    H = np.zeros((B, n), bool)
    for k in range(len(pr)):
        H[:, int(pr[k, 0])] |= mask[:, k]
    return H.sum(1)


def perm(v, B, rng):
    return v[np.argsort(rng.random((B, len(v))), 1)]


def p_ge(obs, nulls):
    nulls = np.asarray(nulls, float)
    return float((1 + (nulls >= obs).sum()) / (1 + len(nulls)))


def p_two_sided(obs, nulls):
    nulls = np.asarray(nulls, float)
    pu = (1 + (nulls >= obs).sum()) / (1 + len(nulls))
    pl = (1 + (nulls <= obs).sum()) / (1 + len(nulls))
    return float(min(1.0, 2.0 * min(pu, pl)))


def summarize(form_list):
    n = len(form_list)
    if n == 0:
        return dict(n=0, modal_count=0, modal_share=0.0, modal_key=None,
                    q_sing=0.0, r_left=0.5, n_left=0, n_sing=0)
    keys = [(s, g) for s, g, _sg in form_list]
    c = Counter(keys)
    modal_key, modal_count = c.most_common(1)[0]
    n_sing = int(sum(1 for _s, _g, sg in form_list if sg))
    n_left = int(sum(1 for s, _g, _sg in form_list if s == 'L'))
    return dict(
        n=n,
        modal_count=int(modal_count),
        modal_share=float(modal_count / n),
        modal_key=[modal_key[0], int(modal_key[1])],
        q_sing=float(n_sing / n),
        r_left=float(n_left / n),
        n_left=n_left,
        n_sing=n_sing,
        layout_counts={f'{s}:{g}': int(v) for (s, g), v in c.most_common()},
    )


def extract_forms(v, e):
    mask = hit_mask(v[None], e['pr'])[0]
    return [e['forms'][k] for k in range(len(e['forms'])) if mask[k]]


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


def forms_from_xs(holdout, xs):
    out = []
    for e in holdout:
        out.extend(extract_forms(xs[e['kid']], e))
    return out


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
    eligible.append(dict(
        kid=kid, okr=okr, inv=inv, v=v, pr=pr, cl=cl, forms=forms,
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
obs_G = len(obs_ids)
consistency['G_holdout'] = obs_G
consistency['n_pairs'] = len(obs_rows)
consistency['n_both'] = len(obs_both)
if obs_G != EXPECTED_G_HOLDOUT:
    stop_excluded(f'holdout G is {obs_G}, expected {EXPECTED_G_HOLDOUT}',
                  extra=dict(consistency=consistency))

obs_forms = [(r['side'], r['group_len'], r['singleton_total']) for r in obs_rows]
obs = summarize(obs_forms)
obs['catalogue'] = sorted(obs_rows, key=lambda r: (r['okr'], r['pendant_index'], r['side']))
# descriptive: KH0424's two hits, if present
kh0424 = [r for r in obs_rows if r['okr'] == 'KH0424']
obs['kh0424_n_pairs'] = len(kh0424)
obs['kh0424_share_layout'] = (
    None if len(kh0424) < 2 else
    len({(r['side'], r['group_len']) for r in kh0424}) == 1
)

print(json.dumps(dict(smoke=SMOKE, R=R, N_CAL=N_CAL, N_POW=N_POW, seeds=SEEDS,
                      alpha=ALPHA, consistency=consistency,
                      observed_summary={k: obs[k] for k in obs if k != 'catalogue'}),
                 indent=1), flush=True)

# --- Nulls (seed 4141) ---
rng_n = np.random.default_rng(SEEDS['nulls'])
null_counters = [Counter() for _ in range(R)]
null_n = np.zeros(R, np.int64)
null_sing = np.zeros(R, np.int64)
null_left = np.zeros(R, np.int64)
null_G = np.zeros(R, np.int64)
for i, e in enumerate(holdout):
    if time.time() - t0 > WALL:
        stop_excluded('wall hit before nulls finished',
                      extra=dict(consistency=consistency, power_khipus_reached=i))
    V = perm(e['v'], R, rng_n)
    mask = hit_mask(V, e['pr'])
    null_G += G_from_mask(mask, e['pr'])
    forms = e['forms']
    for k, (side, glen, sing) in enumerate(forms):
        reps = np.flatnonzero(mask[:, k])
        if len(reps) == 0:
            continue
        key = (side, glen)
        for r in reps:
            null_counters[r][key] += 1
        null_n[reps] += 1
        if sing:
            null_sing[reps] += 1
        if side == 'L':
            null_left[reps] += 1
    if (i + 1) % 20 == 0 or i + 1 == len(holdout):
        json.dump(dict(reached=i + 1, n=len(holdout),
                       secs=round(time.time() - t0, 1)), open(CKPT, 'w'))
        print(f'nulls {i + 1}/{len(holdout)} {time.time() - t0:.1f}s', flush=True)

null_pi = np.array([
    ((max(c.values()) / n) if n else 0.0)
    for c, n in zip(null_counters, null_n)
], float)
null_q = np.array([
    ((s / n) if n else 0.0) for s, n in zip(null_sing, null_n)
], float)
null_r = np.array([
    ((L / n) if n else 0.5) for L, n in zip(null_left, null_n)
], float)

p1 = p_ge(obs['modal_share'], null_pi)
p2 = p_ge(obs['q_sing'], null_q)
p3 = p_two_sided(obs['r_left'], null_r)
print(json.dumps(dict(
    obs_pi=obs['modal_share'], p1=p1,
    obs_q=obs['q_sing'], p2=p2,
    obs_r=obs['r_left'], p3=p3,
    null_pi_mean=float(null_pi.mean()),
    null_q_mean=float(null_q.mean()),
    null_r_mean=float(null_r.mean()),
    null_G_mean=float(null_G.mean()),
), indent=1), flush=True)


def score_stats(st):
    return dict(
        p1=p_ge(st['modal_share'], null_pi),
        p2=p_ge(st['q_sing'], null_q),
        p3=p_two_sided(st['r_left'], null_r),
    )


# --- Calibration (seed 4142) ---
calib = dict(capped=False, n=0)
if time.time() - t0 > WALL:
    calib['capped'] = True
else:
    rng_c = np.random.default_rng(SEEDS['calib'])
    false = dict(H1=0, H2=0, H3=0, any=0)
    for j in range(N_CAL):
        if time.time() - t0 > WALL:
            calib['capped'] = True
            break
        xs = {e['kid']: rng_c.permutation(e['v']) for e in holdout}
        st = summarize(forms_from_xs(holdout, xs))
        sc = score_stats(st)
        f1, f2, f3 = sc['p1'] <= ALPHA, sc['p2'] <= ALPHA, sc['p3'] <= ALPHA
        false['H1'] += int(f1)
        false['H2'] += int(f2)
        false['H3'] += int(f3)
        false['any'] += int(f1 or f2 or f3)
        calib['n'] = j + 1
    if calib['n']:
        calib.update(dict(
            fpr_H1=false['H1'] / calib['n'],
            fpr_H2=false['H2'] / calib['n'],
            fpr_H3=false['H3'] / calib['n'],
            fpr_any=false['any'] / calib['n'],
        ))
    print(json.dumps(calib, indent=1), flush=True)

# --- Power (seed 4143) ---
# H1 plant key: most capacious (side, group_len)
key_caps = {}
for e in holdout:
    seen_local = defaultdict(set)
    used_by_key = defaultdict(set)
    for k, (side, glen, _sg) in enumerate(e['forms']):
        key = (side, glen)
        i, s, ee = [int(x) for x in e['pr'][k]]
        span = frozenset(list(range(s, ee)) + [i])
        if used_by_key[key] & span:
            continue
        used_by_key[key] |= span
        key_caps[key] = key_caps.get(key, 0) + 1
h1_key = None
if key_caps:
    h1_key = max(key_caps.items(), key=lambda kv: (kv[1], kv[0][1], kv[0][0]))[0]
h1_capacity = key_caps.get(h1_key, 0) if h1_key else 0
h2_capacity = capacity(holdout, lambda f: f[2])
h3_capacity = capacity(holdout, lambda f: f[0] == 'L')

rng_p = np.random.default_rng(SEEDS['power'])


def power_for(pred, label):
    rec = dict(label=label, n=0, hits=0, skipped=0, capped=False, rate=None)
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
        st = summarize(forms_from_xs(holdout, xs))
        sc = score_stats(st)
        n_ok += 1
        if sc[label] <= ALPHA:
            hits += 1
    rec.update(dict(n=n_ok, hits=hits, skipped=skipped,
                    rate=(hits / n_ok) if n_ok else None,
                    attempts=attempts))
    return rec


power = {}
power['H1'] = power_for(
    (lambda f, key=h1_key: h1_key is not None and (f[0], f[1]) == key),
    'p1')
power['H1']['plant_key'] = [h1_key[0], int(h1_key[1])] if h1_key else None
power['H1']['capacity'] = int(h1_capacity)
print('power H1', power['H1'], flush=True)
power['H2'] = power_for(lambda f: f[2], 'p2')
power['H2']['capacity'] = int(h2_capacity)
print('power H2', power['H2'], flush=True)
power['H3'] = power_for(lambda f: f[0] == 'L', 'p3')
power['H3']['capacity'] = int(h3_capacity)
print('power H3', power['H3'], flush=True)


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
h1.update(dict(stat='modal_share', obs=obs['modal_share'],
               modal_key=obs['modal_key'], modal_count=obs['modal_count'],
               null_mean=float(null_pi.mean()), null_sd=float(null_pi.std()),
               plant_key=power['H1'].get('plant_key')))
h2 = decide('H2', p2, calib.get('fpr_H2'), power['H2'])
h2.update(dict(stat='q_sing', obs=obs['q_sing'],
               null_mean=float(null_q.mean()), null_sd=float(null_q.std())))
h3 = decide('H3', p3, calib.get('fpr_H3'), power['H3'])
h3.update(dict(stat='r_left', obs=obs['r_left'],
               null_mean=float(null_r.mean()), null_sd=float(null_r.std())))

supported = [n for n, h in (('H1', h1), ('H2', h2), ('H3', h3)) if h['verdict'] == 'supported']
not_sup = [n for n, h in (('H1', h1), ('H2', h2), ('H3', h3)) if h['verdict'] == 'not supported']
if supported:
    reading = 'shares shape: ' + ', '.join(supported)
elif not_sup == ['H1', 'H2', 'H3']:
    reading = 'mixed bag'
else:
    reading = 'partial: ' + ', '.join(
        f"{n}={h['verdict']}" for n, h in (('H1', h1), ('H2', h2), ('H3', h3)))

decision = dict(excluded=False, H1=h1, H2=h2, H3=h3, reading=reading)
res = dict(
    design=dict(discovery=sorted(DISCOVERY), R=R, N_CAL=N_CAL, N_POW=N_POW,
                seeds=SEEDS, alpha_fam=ALPHA_FAM, n_h=N_H, alpha=ALPHA,
                gate=GATE, m_plant=M_PLANT, smoke=SMOKE, wall=WALL,
                expected_sha=EXPECTED_SHA),
    consistency=consistency,
    inherited_from_k040=dict(
        note='same holdout and G=23; K041 audits form, not the leftover count',
        G_holdout=EXPECTED_G_HOLDOUT,
    ),
    observed=obs,
    null=dict(
        pi_mean=float(null_pi.mean()), pi_sd=float(null_pi.std()),
        q_mean=float(null_q.mean()), q_sd=float(null_q.std()),
        r_mean=float(null_r.mean()), r_sd=float(null_r.std()),
        G_mean=float(null_G.mean()), G_sd=float(null_G.std()),
        p1=p1, p2=p2, p3=p3,
    ),
    calibration=calib,
    power=power,
    decision=decision,
    secs=round(time.time() - t0, 1),
)
json.dump(res, open(OUT, 'w'), indent=1)
print(json.dumps(dict(decision=decision, secs=res['secs']), indent=1), flush=True)
