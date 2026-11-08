#!/usr/bin/env python3
"""K057 - R5 multi-number-cord sensitivity of the FROZEN K021 sum-cord colour
results (primary and secondary H2 shared-colour). Pre-registered in
case-file/K057-multinumber-sum-colour.md.

STATISTIC (frozen, K021). Sum cords = K001 hits: a level-1 pendant with
value >= 10 equal to the sum of the next or previous k = 2..12 pendants,
with at least 2 of them nonzero. Colour = FULL_COLOR of the ascher_cord_color
row with the smallest RANGE_BEG (ties: smallest color_id). T2 = number of
same-colour pairs among the sum cords, summed over khipus. T1 (boundary
count) is computed only for the G0 empty-mask fixture; K021 H1 was a powered
negative and is not retested.

R5 CORD (K007/K008, verbatim as K053-K056). MASK (K008, structure-preserving):
an R5 pendant keeps its position but is never a sum-cord target and never
inside a matching summand window. A K001 window (pendant i, side, k) is legal
iff i is non-R5 and no pendant of that window is R5. Eligible cords for the
redraw null are level-1 pendants with value >= 10, a known colour, and (under
the mask) non-R5. Null: colour sequence untouched; draw the same number of
'sum cords' uniformly from that khipu's eligible cords. With an empty mask
the observed statistics match K021 (G0).

Seeds: primary null 5757, FPR 5758, power 5759; secondary null 5760, FPR 5761,
power 5762.
Usage: python3 tools/k057_multinumber_sum_colour.py khipu.db [--smoke] [--g0-only]
"""
import hashlib, json, sys, time
import numpy as np
from collections import defaultdict, Counter

t0 = time.time()
DB = sys.argv[1]
SMOKE = '--smoke' in sys.argv
G0_ONLY = '--g0-only' in sys.argv
EXPECTED_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
KMAX = 12
R = 500 if SMOKE else 20000
N_CAL = 10 if SMOKE else 200
N_POW = 10 if SMOKE else 200
ALPHA = 0.025
GATE = 0.05
POWER_BAR = 0.5
SEEDS = dict(p_null=5757, p_fpr=5758, p_pow=5759, s_null=5760, s_fpr=5761, s_pow=5762)
WALL = 540
OUT = ('analysis/k057_smoke.json' if SMOKE else
       'analysis/k057_g0.json' if G0_ONLY else 'analysis/k057_results.json')
CKPT = ('analysis/k057_smoke_checkpoint.json' if SMOKE else
        'analysis/k057_g0_checkpoint.json' if G0_ONLY else 'analysis/k057_checkpoint.json')
PUB = dict(
    primary=dict(n_khipus=10, n_sum=95, n_elig=1005, T1=35, T2=416),
    secondary=dict(n_khipus=245, n_sum=724, n_elig=10414, T1=290, T2=782),
    n_colour_cords=53750, n_R5=3069,
)
res = dict(design=dict(seeds=SEEDS, R=R, N_CAL=N_CAL, N_POW=N_POW, alpha=ALPHA,
                       gate=GATE, power_bar=POWER_BAR, smoke=SMOKE, g0_only=G0_ONLY,
                       published=PUB, kmax=KMAX))


def dump():
    res['secs'] = round(time.time() - t0, 1)
    json.dump(res, open(OUT, 'w'), indent=1)
    json.dump(dict(secs=res['secs'], stage=res.get('stage', '')), open(CKPT, 'w'))


def stop(reason):
    res['decision'] = dict(excluded=True, reason=reason)
    res['stage'] = 'excluded'
    dump()
    print('EXCLUDED:', reason, flush=True)
    sys.exit(0)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


got = sha256_file(DB)
if got != EXPECTED_SHA:
    stop(f'hash mismatch {got}')

import sqlite3
c = sqlite3.connect(DB)
dups = {r[0] for r in c.execute('select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1')}
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute(
    'select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main')}
val = defaultdict(int)
for cid, v in c.execute('select CORD_ID, knot_value_type from knot'):
    if v is not None:
        val[cid] += int(v)
col = {}
for cid, fc, rb, i in c.execute(
        'select CORD_ID, FULL_COLOR, RANGE_BEG, color_id from ascher_cord_color '
        'order by CORD_ID, RANGE_BEG, color_id'):
    if cid not in col and fc not in (None, '', "''"):
        col[cid] = fc.strip()
kh = defaultdict(list)
for khid, cid in c.execute(
        'select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 '
        'order by KHIPU_ID, CORD_ORDINAL'):
    if khid not in dups:
        kh[khid].append(cid)
sigk = {r['okr'] for r in json.load(open('analysis/k001_results_K5000.json'))['rows']
        if r.get('bh_sig_N1')}


# --- R5 definition, copied verbatim from K008 / K053 / K054 / K055 / K056 ---
def place(v):
    p = 0
    while v % 10 == 0:
        v //= 10
        p += 1
    return p


clplaces = defaultdict(set)
clcord = {}
for cid, cl, t, v in c.execute(
        "select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
    t = (t or '').strip()
    if t in ('S', 'L', 'E') and v:
        clplaces[cl].add(place(int(v)) if t == 'S' else 0)
    clcord[cl] = cid
ordn = {r[0]: r[1] for r in c.execute("select CLUSTER_ID, ORDINAL from knot_cluster")}
bycord = defaultdict(dict)
for cl, pl in clplaces.items():
    if len(pl) == 1 and ordn.get(cl) is not None:
        bycord[clcord[cl]][ordn[cl]] = next(iter(pl))
R5 = set()
for cd, d in bycord.items():
    s = [d[o] for o in sorted(d)]
    if len(s) >= 2 and not all(a > b for a, b in zip(s, s[1:])):
        R5.add(cd)

if len(R5) != PUB['n_R5']:
    stop(f'R5 count {len(R5)} != {PUB["n_R5"]}')
if len(col) != PUB['n_colour_cords']:
    stop(f'n_colour_cords {len(col)} != {PUB["n_colour_cords"]}')


def hits(V, r5):
    """K001 hits; if r5 is a bool array, illegal windows (target or summand R5) are skipped."""
    n = len(V)
    P = np.r_[0, np.cumsum(V)]
    NZ = np.r_[0, np.cumsum(V > 0)]
    h = np.zeros(n, dtype=bool)
    mask = r5 is not None
    for i in range(n):
        if V[i] < 10:
            continue
        if mask and r5[i]:
            continue
        for k in range(2, KMAX + 1):
            if i + k < n and P[i + k + 1] - P[i + 1] == V[i] and NZ[i + k + 1] - NZ[i + 1] >= 2:
                if (not mask) or (not r5[i + 1:i + k + 1].any()):
                    h[i] = True
                    break
            if i - k >= 0 and P[i] - P[i - k] == V[i] and NZ[i] - NZ[i - k] >= 2:
                if (not mask) or (not r5[i - k:i].any()):
                    h[i] = True
                    break
    return h


def build_units(masked, keep_primary_even_if_empty=False):
    units = []
    dropped_detail = []
    for khid, cids in kh.items():
        V = np.array([val.get(x, 0) for x in cids], np.int64)
        r5 = np.array([x in R5 for x in cids], dtype=bool)
        h_raw = hits(V, None)
        h = hits(V, r5) if masked else h_raw
        C = [col.get(x) for x in cids]
        n = len(cids)
        if masked:
            elig = [i for i in range(n) if V[i] >= 10 and C[i] is not None and not r5[i]]
        else:
            elig = [i for i in range(n) if V[i] >= 10 and C[i] is not None]
        prim = names[khid][0] in sigk
        if not elig:
            if keep_primary_even_if_empty and prim:
                pass
            else:
                continue
        obs = np.array([h[i] for i in elig], dtype=bool) if elig else np.zeros(0, dtype=bool)
        if obs.sum() == 0 and not (keep_primary_even_if_empty and prim):
            continue
        bnd = np.array([all(C[j] != C[i] for j in (i - 1, i + 1) if 0 <= j < n) for i in elig],
                       dtype=bool) if elig else np.zeros(0, dtype=bool)
        cc = [C[i] for i in elig]
        lab = {x: k for k, x in enumerate(sorted(set(cc)))} if cc else {}
        raw_sum = int(h_raw.sum())
        # descriptive: why published (unmasked, colour-eligible) sum cords dropped
        raw_elig = [i for i in range(n) if V[i] >= 10 and C[i] is not None and h_raw[i]]
        n_drop_target = n_drop_window = n_drop_elig = 0
        for i in raw_elig:
            if not h[i]:
                if r5[i]:
                    n_drop_target += 1
                else:
                    n_drop_window += 1
            elif masked and r5[i]:
                n_drop_elig += 1  # shouldn't happen: h[i] false if r5[i]
        units.append(dict(
            khid=khid, okr=names[khid][0], inv=names[khid][1],
            m=int(obs.sum()), ne=len(elig),
            bnd=bnd,
            cl=np.array([lab[x] for x in cc], dtype=int) if cc else np.zeros(0, dtype=int),
            obs=obs, prim=prim,
            n_r5=int(r5.sum()), raw_m=raw_sum,
            n_drop_target=n_drop_target, n_drop_window=n_drop_window,
        ))
        if prim and (n_drop_target or n_drop_window):
            dropped_detail.append(dict(
                okr=names[khid][0], inv=names[khid][1],
                raw_colour_sum=len(raw_elig), masked_m=int(obs.sum()),
                drop_target_R5=n_drop_target, drop_window_R5=n_drop_window,
            ))
    return units, dropped_detail


def pairs(cl):
    if len(cl) == 0:
        return 0
    cnt = np.bincount(cl)
    return int((cnt * (cnt - 1) // 2).sum())


def stats(us, masks):
    t1 = sum(int(u['bnd'][mk].sum()) for u, mk in zip(us, masks) if u['ne'])
    t2 = sum(pairs(u['cl'][mk]) for u, mk in zip(us, masks) if u['ne'])
    return t1, t2


def null(us, Rr, seed):
    rng = np.random.default_rng(seed)
    T1 = np.zeros(Rr, np.int64)
    T2 = np.zeros(Rr, np.int64)
    for u in us:
        ne, m = u['ne'], u['m']
        if m <= 0 or ne <= 0:
            continue
        K = int(u['cl'].max()) + 1 if ne else 0
        idx = np.argsort(rng.random((Rr, ne)), 1)[:, :m]
        T1 += u['bnd'][idx].sum(1)
        oh = np.zeros((Rr, K), np.int64)
        for j in range(m):
            np.add.at(oh, (np.arange(Rr), u['cl'][idx[:, j]]), 1)
        T2 += (oh * (oh - 1) // 2).sum(1)
    return T1, T2


def pv(o, nl):
    return float((1 + (nl >= o).sum()) / (1 + len(nl)))


def run_pop(us, label, seed_null, seed_fpr, seed_pow):
    o1, o2 = stats(us, [u['obs'] for u in us])
    N1, N2 = null(us, R, seed_null)
    out = dict(
        pop=label, n_khipus=len(us), n_sum=int(sum(u['m'] for u in us)),
        n_elig=int(sum(u['ne'] for u in us)),
        T1=o1, T1_null_mean=float(N1.mean()) if len(N1) else None,
        T2=o2, T2_null_mean=float(N2.mean()) if len(N2) else None,
        p2=pv(o2, N2),
    )
    rng_f = np.random.default_rng(seed_fpr)
    rng_p = np.random.default_rng(seed_pow)
    cal2 = pw2 = 0
    n_fpr = n_pow = 0
    for _ in range(N_CAL):
        mk = []
        for u in us:
            if u['ne'] == 0 or u['m'] == 0:
                mk.append(np.zeros(u['ne'], dtype=bool))
            else:
                mk.append(np.isin(np.arange(u['ne']), rng_f.choice(u['ne'], u['m'], replace=False)))
        _a, b = stats(us, mk)
        cal2 += pv(b, N2) <= ALPHA
        n_fpr += 1
    for _ in range(N_POW):
        m2 = []
        for u in us:
            if u['ne'] == 0 or u['m'] == 0:
                m2.append(np.zeros(u['ne'], dtype=bool))
                continue
            base_idx = rng_p.choice(u['ne'], u['m'], replace=False)
            s2 = list(base_idx)
            top = Counter(u['cl'][base_idx]).most_common(1)[0][0]
            taken = set(int(x) for x in base_idx)
            free_c = [i for i in range(u['ne']) if u['cl'][i] == top and i not in taken]
            rng_p.shuffle(free_c)
            for k in range(len(s2)):
                if rng_p.random() < 0.5 and free_c:
                    s2[k] = free_c.pop()
            m2.append(np.isin(np.arange(u['ne']), s2))
        pw2 += pv(stats(us, m2)[1], N2) <= ALPHA
        n_pow += 1
    fpr = cal2 / n_fpr if n_fpr else None
    power = pw2 / n_pow if n_pow else None
    out.update(calib_fpr_H2=fpr, power_H2=power, n_fpr=n_fpr, n_pow=n_pow)
    if fpr is None or fpr > GATE:
        verdict = 'excluded'
    elif out['p2'] <= ALPHA:
        verdict = 'survives'
    elif power is not None and power >= POWER_BAR:
        verdict = 'no longer established'
    else:
        verdict = 'not testable'
    out['verdict_H2'] = verdict
    return out


# --- G0: empty mask must reproduce K021 observed counts ---
res['stage'] = 'g0'
empty, _ = build_units(False)
empty_p = [u for u in empty if u['prim']]
empty_s = empty
g0 = {}
for key, us in (('primary', empty_p), ('secondary', empty_s)):
    o1, o2 = stats(us, [u['obs'] for u in us])
    got_pop = dict(n_khipus=len(us), n_sum=int(sum(u['m'] for u in us)),
                   n_elig=int(sum(u['ne'] for u in us)), T1=o1, T2=o2)
    exp = PUB[key]
    ok = all(got_pop[k] == exp[k] for k in exp)
    g0[key] = dict(got=got_pop, expected=exp, pass_=ok)
    if not ok:
        stop(f'G0 {key} mismatch: got {got_pop} expected {exp}')
res['g0'] = {k: {**v, 'pass': v.pop('pass_')} for k, v in g0.items()}
res['g0']['n_R5'] = len(R5)
res['g0']['pass'] = True
print('G0 pass', json.dumps({k: res['g0'][k]['got'] for k in ('primary', 'secondary')}), flush=True)
dump()
if G0_ONLY:
    print('G0-only done', flush=True)
    sys.exit(0)

# --- masked run ---
res['stage'] = 'masked'
masked_units, drop_detail = build_units(masked=True, keep_primary_even_if_empty=True)
prim = [u for u in masked_units if u['prim']]
# secondary: khipus with at least one masked sum cord (K021 construction)
sec = [u for u in masked_units if u['m'] > 0]
# keep primary at the frozen 10, even if some have m = 0
if len(prim) != 10:
    stop(f'primary population {len(prim)} != 10')

res['r5_load'] = dict(
    n_R5=len(R5),
    primary=[dict(okr=u['okr'], inv=u['inv'], raw_m=u['raw_m'], masked_m=u['m'],
                  n_elig=u['ne'], n_r5=u['n_r5'],
                  drop_target_R5=u['n_drop_target'], drop_window_R5=u['n_drop_window'],
                  pairs_masked=pairs(u['cl'][u['obs']]) if u['ne'] else 0)
             for u in prim],
    dropped_primary=drop_detail,
    secondary_n_khipus_masked=len(sec),
    secondary_n_sum_masked=int(sum(u['m'] for u in sec)),
)

print('masked primary sums:', [(u['okr'], u['raw_m'], u['m']) for u in prim], flush=True)
dump()

if time.time() - t0 > WALL:
    stop('wall before tests')

res['stage'] = 'primary'
res['primary'] = run_pop(prim, 'K001 BH-significant (masked)',
                         SEEDS['p_null'], SEEDS['p_fpr'], SEEDS['p_pow'])
print('primary', res['primary'], flush=True)
dump()

if time.time() - t0 > WALL:
    stop('wall before secondary')

res['stage'] = 'secondary'
res['secondary'] = run_pop(sec, 'all khipus with a masked sum cord',
                           SEEDS['s_null'], SEEDS['s_fpr'], SEEDS['s_pow'])
print('secondary', res['secondary'], flush=True)

verdicts = [res['primary']['verdict_H2'], res['secondary']['verdict_H2']]
n_surv = sum(v == 'survives' for v in verdicts)
n_excl = sum(v == 'excluded' for v in verdicts)
if n_excl:
    overall = 'EXCLUDED'
elif n_surv == 2:
    overall = 'ROBUST'
elif n_surv == 1:
    overall = 'PARTIAL'
elif all(v == 'no longer established' for v in verdicts):
    overall = 'NONE ESTABLISHED'
else:
    overall = 'MIXED'
res['decision'] = dict(
    overall=overall,
    primary=res['primary']['verdict_H2'],
    secondary=res['secondary']['verdict_H2'],
    rule='survives iff masked p2 <= 0.025 and FPR <= 0.05; '
         'no longer established iff p2 > 0.025 and power >= 0.5; '
         'not testable iff p2 > 0.025 and power < 0.5; excluded iff FPR > 0.05. '
         'Both survive -> ROBUST; one -> PARTIAL; both powered negatives -> NONE ESTABLISHED.',
)
res['stage'] = 'done'
dump()
print('OVERALL', overall, 'secs', res['secs'], flush=True)
