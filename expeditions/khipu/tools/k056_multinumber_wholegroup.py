#!/usr/bin/env python3
"""K056 - R5 multi-number-cord sensitivity of the FROZEN whole-group-sum results
(K025 primary KH0359/UR119 and KH0405/UR166; K040 H1 holdout corpus G; K042 H1
holdout singleton-total count G_s). Pre-registered in case-file/K056-multinumber-wholegroup.md.

STATISTIC (frozen, K025/K040/K042). A whole-group sum is a pendant with value >= 10
equal to the sum of ALL pendants of the group immediately left or right (group >= 2
cords, >= 2 nonzero; pendant not in that group). G counts distinct pendants.
G_s counts those whose own group has size 1 (K042 singleton_total).

R5 CORD (K007/K008, verbatim as K053-K055). MASK (K008, structure-preserving): an R5
pendant keeps its position but is never a target and never inside a summand group;
a candidate pair (i, s, e) is legal iff i is non-R5 and no pendant of s:e is R5.
Null permutes only non-R5 values among non-R5 positions; group ids stay put.
With an empty mask the masked statistic is the published unmasked one (G0).

Seeds: T1/T2 nulls 5650, FPR 5651, power 5652; corpus nulls 5653, FPR 5654,
power G 5655, power G_s 5656.
Usage: python3 tools/k056_multinumber_wholegroup.py khipu.db [--smoke]
"""
import hashlib, json, sys, time
import numpy as np
from collections import defaultdict

t0 = time.time()
DB = sys.argv[1]
SMOKE = '--smoke' in sys.argv
EXPECTED_SHA = '607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db'
DISCOVERY = ('KH0359', 'KH0405')
R_T = 500 if SMOKE else 20000      # K025 primary R
R_C = 200 if SMOKE else 10000      # K040/K042 corpus R
N_CAL = 10 if SMOKE else 200
N_POW = 10 if SMOKE else 200
M_PLANT = 9
ALPHA = dict(KH0359=0.025, KH0405=0.025, G=0.05, G_s=0.025)
GATE = dict(KH0359=0.05, KH0405=0.05, G=0.08, G_s=0.08)
POWER_BAR = 0.5
MIN_N = 1 if SMOKE else 30
SEEDS = dict(t_null=5650, t_fpr=5651, t_pow=5652, c_null=5653, c_fpr=5654, c_powG=5655, c_powGs=5656)
WALL = 540
OUT = 'analysis/k056_smoke.json' if SMOKE else 'analysis/k056_results.json'
CKPT = 'analysis/k056_smoke_checkpoint.json' if SMOKE else 'analysis/k056_checkpoint.json'
PUB = dict(KH0359=dict(G=4, p=4.999750012499375e-05), KH0405=dict(G=4, p=4.999750012499375e-05),
           G=dict(G=23, p=0.0162), G_s=dict(G=10, p=9.999000099990002e-05))
res = dict(design=dict(seeds=SEEDS, R_T=R_T, R_C=R_C, N_CAL=N_CAL, N_POW=N_POW, M_PLANT=M_PLANT,
                       alpha=ALPHA, gate=GATE, power_bar=POWER_BAR, smoke=SMOKE, published=PUB))


def dump():
    res['secs'] = round(time.time() - t0, 1)
    json.dump(res, open(OUT, 'w'), indent=1)


def stop(reason):
    res['decision'] = dict(excluded=True, reason=reason)
    dump(); print('EXCLUDED:', reason, flush=True); sys.exit(0)


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
names = {r[0]: (r[1] or '', r[2] or '') for r in c.execute('select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main')}
val = defaultdict(int)
for cid, v in c.execute('select CORD_ID, knot_value_type from knot'):
    if v is not None:
        val[cid] += int(v)


# --- R5 definition, copied verbatim from K008 / K053 / K054 / K055 ---
def place(v):
    p = 0
    while v % 10 == 0:
        v //= 10
        p += 1
    return p
clplaces = defaultdict(set)
clcord = {}
for cid, cl, t, v in c.execute("select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
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


def groups_of(cl):
    g, last = [], object()
    for i, x in enumerate(cl):
        if x != last:
            g.append([i, i + 1]); last = x
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


def legal(pr, bad):
    if len(pr) == 0:
        return pr
    keep = [k for k in range(len(pr)) if not bad[pr[k, 0]] and not bad[pr[k, 1]:pr[k, 2]].any()]
    return pr[keep].reshape(-1, 3)


def hitH(V, pr):
    B, n = V.shape
    H = np.zeros((B, n), bool)
    if len(pr) == 0:
        return H
    P = np.zeros((B, n + 1), np.int64); P[:, 1:] = np.cumsum(V, 1)
    Z = np.zeros((B, n + 1), np.int64); Z[:, 1:] = np.cumsum(V > 0, 1)
    i, s, e = pr[:, 0], pr[:, 1], pr[:, 2]
    vi = V[:, i]
    hit = (vi >= 10) & (vi == P[:, e] - P[:, s]) & ((Z[:, e] - Z[:, s]) >= 2)
    for k in range(len(pr)):
        H[:, i[k]] |= hit[:, k]
    return H


def stats(V, pr, sing):
    H = hitH(V, pr)
    return H.sum(1).astype(np.int64), H[:, sing].sum(1).astype(np.int64)


def permmask(rng, v, bad, B):
    free = np.where(~bad)[0]
    out = np.tile(v, (B, 1))
    if len(free):
        out[:, free] = v[free][rng.random((B, len(free))).argsort(1)]
    return out


def pv(o, nl):
    nl = np.asarray(nl)
    return float((1 + (nl >= o).sum()) / (1 + len(nl)))


def plant_pair(x, i, s, e, rng):
    x = x.copy(); blk = x[s:e].copy()
    if (blk > 0).sum() < 2:
        blk[:2] = np.maximum(blk[:2], rng.integers(1, 30, 2))
    if int(blk.sum()) < 10:
        blk[0] += 10 - int(blk.sum())
    x[s:e] = blk; x[i] = int(blk.sum())
    return x


kh = defaultdict(list)
for khid, cid, cl in c.execute('select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL'):
    if khid in dups:
        continue
    kh[khid].append((val.get(cid, 0), cl, cid))

eligible = []
for kid, cords in kh.items():
    cl = [x[1] for x in cords]
    if len(groups_of(cl)) < 4:
        continue
    v = np.array([x[0] for x in cords], np.int64)
    pr = prep(cl, len(v))
    if len(pr) == 0 or (v >= 10).sum() == 0:
        continue
    bad = np.array([x[2] in R5 for x in cords])
    sing = np.zeros(len(v), bool)
    for s, e in groups_of(cl):
        if e - s == 1:
            sing[s:e] = True
    eligible.append(dict(kid=kid, okr=names[kid][0], inv=names[kid][1], v=v, pr=pr, prm=legal(pr, bad),
                         bad=bad, sing=sing, cids=[x[2] for x in cords]))
byokr = {e['okr']: e for e in eligible}
holdout = [e for e in eligible if e['okr'] not in DISCOVERY]

# --- G0 fixture ---
empty = {}
for okr in DISCOVERY:
    e = byokr[okr]; empty[okr] = int(stats(e['v'][None], e['pr'], e['sing'])[0][0])
eG = sum(int(stats(e['v'][None], e['pr'], e['sing'])[0][0]) for e in holdout)
eGs = sum(int(stats(e['v'][None], e['pr'], e['sing'])[1][0]) for e in holdout)
g0 = dict(sha256=got, n_r5=len(R5), n_eligible=len(eligible), n_holdout=len(holdout),
          empty_mask=dict(KH0359=empty['KH0359'], KH0405=empty['KH0405'], G=eG, G_s=eGs, G_ns=eG - eGs))
g0['pass'] = bool(len(R5) == 3069 and len(eligible) == 369 and len(holdout) == 367 and empty['KH0359'] == 4
                  and empty['KH0405'] == 4 and eG == 23 and eGs == 10)
res['G0'] = g0
print(json.dumps(g0), flush=True)
if not g0['pass']:
    stop('G0 fixture failed')

# --- descriptive: which published hits touch R5 ---
def touched(e):
    H_un = hitH(e['v'][None], e['pr'])[0]
    rows = []
    for k in range(len(e['pr'])):
        i, s, ee = [int(x) for x in e['pr'][k]]
        vi = int(e['v'][i]); blk = e['v'][s:ee]
        if vi >= 10 and vi == int(blk.sum()) and int((blk > 0).sum()) >= 2:
            rows.append(dict(okr=e['okr'], pendant_index=i, cord_id=int(e['cids'][i]), value=vi, group=[s, ee],
                             target_R5=bool(e['bad'][i]), n_R5_in_group=int(e['bad'][s:ee].sum()),
                             legal=bool(not e['bad'][i] and not e['bad'][s:ee].any()), singleton_total=bool(e['sing'][i])))
    return rows

pub_hits = []
for okr in DISCOVERY:
    pub_hits += touched(byokr[okr])
for e in holdout:
    pub_hits += touched(e)
res['published_hits'] = pub_hits
res['r5_load'] = dict(KH0359=int(byokr['KH0359']['bad'].sum()), KH0405=int(byokr['KH0405']['bad'].sum()),
                      holdout_r5=int(sum(e['bad'].sum() for e in holdout)),
                      holdout_khipus_with_r5=int(sum(e['bad'].any() for e in holdout)),
                      holdout_khipus_no_legal_pair=int(sum(len(e['prm']) == 0 for e in holdout)),
                      pairs_unmasked=dict(KH0359=len(byokr['KH0359']['pr']), KH0405=len(byokr['KH0405']['pr'])),
                      pairs_masked=dict(KH0359=len(byokr['KH0359']['prm']), KH0405=len(byokr['KH0405']['prm'])))
print(json.dumps(res['r5_load']), flush=True)

targets = {}
# --- T1/T2 primary khipus ---
rng_n = np.random.default_rng(SEEDS['t_null']); rng_f = np.random.default_rng(SEEDS['t_fpr']); rng_p = np.random.default_rng(SEEDS['t_pow'])
for okr in DISCOVERY:
    e = byokr[okr]; v, bad, prm, sing = e['v'], e['bad'], e['prm'], e['sing']
    rec = dict(inv=e['inv'], n_pend=len(v), n_r5=int(bad.sum()), pairs_masked=len(prm), alpha=ALPHA[okr], gate=GATE[okr])
    if len(prm) == 0:
        rec.update(verdict='not testable', reason='no masked-legal pair'); targets[okr] = rec; continue
    obs = int(stats(v[None], prm, sing)[0][0])
    nl = np.concatenate([stats(permmask(rng_n, v, bad, 5000), prm, sing)[0] for _ in range(R_T // 5000)]) if R_T >= 5000 \
        else stats(permmask(rng_n, v, bad, R_T), prm, sing)[0]
    p = pv(obs, nl)
    fp = np.mean([pv(int(stats(permmask(rng_f, v, bad, 1), prm, sing)[0][0]), nl) <= ALPHA[okr] for _ in range(N_CAL)])
    hits = 0
    for _ in range(N_POW):
        x = permmask(rng_p, v, bad, 1)[0]
        i, s, ee = [int(t) for t in prm[rng_p.integers(len(prm))]]
        x = plant_pair(x, i, s, ee, rng_p)
        hits += pv(int(stats(x[None], prm, sing)[0][0]), nl) <= ALPHA[okr]
    pw = hits / N_POW
    rec.update(G_masked=obs, null_mean=float(nl.mean()), null_max=int(nl.max()), p=p, fpr=float(fp), power_1planted=pw)
    if fp > GATE[okr]:
        rec['verdict'] = 'excluded'
    elif p <= ALPHA[okr]:
        rec['verdict'] = 'survives'
    elif pw >= POWER_BAR:
        rec['verdict'] = 'no longer established'
    else:
        rec['verdict'] = 'not testable'
    targets[okr] = rec
    print(okr, json.dumps(rec), round(time.time() - t0, 1), flush=True)
res['targets'] = targets; dump()

# --- T3/T4 holdout corpus ---
rng_c = np.random.default_rng(SEEDS['c_null'])
totG = np.zeros(R_C, np.int64); totS = np.zeros(R_C, np.int64)
obsG = obsS = 0
for j, e in enumerate(holdout):
    if time.time() - t0 > WALL:
        stop('wall hit before corpus nulls finished')
    if len(e['prm']) == 0:
        e['nlG'] = np.zeros(R_C, np.int64); e['nlS'] = np.zeros(R_C, np.int64); continue
    g, gs = stats(e['v'][None], e['prm'], e['sing']); obsG += int(g[0]); obsS += int(gs[0])
    nG, nS = stats(permmask(rng_c, e['v'], e['bad'], R_C), e['prm'], e['sing'])
    e['nlG'], e['nlS'] = nG, nS; totG += nG; totS += nS
    if (j + 1) % 60 == 0:
        json.dump(dict(reached=j + 1, G=obsG, G_s=obsS, secs=round(time.time() - t0, 1)), open(CKPT, 'w'))
        print(f'corpus nulls {j + 1}/{len(holdout)} G={obsG} G_s={obsS} {time.time() - t0:.1f}s', flush=True)
pG, pS = pv(obsG, totG), pv(obsS, totS)
print('corpus', obsG, float(totG.mean()), pG, obsS, float(totS.mean()), pS, flush=True)

rng_f = np.random.default_rng(SEEDS['c_fpr']); fG = fS = 0; ncal = 0
act = [e for e in holdout if len(e['prm'])]
for _ in range(N_CAL):
    if time.time() - t0 > WALL:
        break
    sg = ss = 0
    for e in act:
        g, gs = stats(permmask(rng_f, e['v'], e['bad'], 1), e['prm'], e['sing']); sg += int(g[0]); ss += int(gs[0])
    fG += pv(sg, totG) <= ALPHA['G']; fS += pv(ss, totS) <= ALPHA['G_s']; ncal += 1


def power_corpus(seed, pred, alpha, nulls, which):
    rng = np.random.default_rng(seed)
    cands = [(e, int(k)) for e in act for k in range(len(e['prm'])) if pred(e, k)]
    hits = n = att = 0
    while n < N_POW and att < 5 * N_POW and time.time() - t0 <= WALL:
        att += 1
        xs = {e['kid']: permmask(rng, e['v'], e['bad'], 1)[0] for e in act}
        used = defaultdict(set); planted = 0
        for idx in rng.permutation(len(cands)):
            e, k = cands[idx]; i, s, ee = [int(t) for t in e['prm'][k]]
            span = set(range(s, ee)) | {i}
            if used[e['kid']] & span:
                continue
            xs[e['kid']] = plant_pair(xs[e['kid']], i, s, ee, rng); used[e['kid']] |= span; planted += 1
            if planted >= M_PLANT:
                break
        if planted < M_PLANT:
            continue
        st = 0
        for e in act:
            g, gs = stats(xs[e['kid']][None], e['prm'], e['sing']); st += int((g if which == 'G' else gs)[0])
        n += 1; hits += pv(st, nulls) <= alpha
    return dict(n=n, hits=hits, attempts=att, rate=(hits / n) if n else None, capped=n < N_POW)

powG = power_corpus(SEEDS['c_powG'], lambda e, k: True, ALPHA['G'], totG, 'G')
powS = power_corpus(SEEDS['c_powGs'], lambda e, k: bool(e['sing'][e['prm'][k, 0]]), ALPHA['G_s'], totS, 'G_s')
for name, obs, nl, p, f, pw in (('G', obsG, totG, pG, fG, powG), ('G_s', obsS, totS, pS, fS, powS)):
    rec = dict(obs_masked=obs, null_mean=float(nl.mean()), null_sd=float(nl.std()), p=p,
               fpr=(f / ncal) if ncal else None, fpr_n=ncal, power_m9=pw, alpha=ALPHA[name], gate=GATE[name],
               n_active_khipus=len(act))
    if ncal < N_CAL or rec['fpr'] > GATE[name]:
        rec['verdict'] = 'excluded' if ncal and rec['fpr'] > GATE[name] else 'not testable'
    elif p <= ALPHA[name]:
        rec['verdict'] = 'survives'
    elif pw['rate'] is not None and pw['n'] >= MIN_N and pw['rate'] >= POWER_BAR:
        rec['verdict'] = 'no longer established'
    else:
        rec['verdict'] = 'not testable'
    targets[name] = rec
    print(name, json.dumps(rec), flush=True)

v = [targets[k]['verdict'] for k in ('KH0359', 'KH0405', 'G', 'G_s')]
if 'excluded' in v:
    overall = 'EXCLUDED (at least one gate failed; see per-target)'
elif all(x == 'survives' for x in v):
    overall = 'ROBUST'
elif any(x == 'survives' for x in v):
    overall = 'PARTIAL'
elif all(x == 'no longer established' for x in v):
    overall = 'NONE ESTABLISHED'
else:
    overall = 'MIXED (report per target)'
res['decision'] = dict(excluded=False, overall=overall, verdicts=dict(zip(('KH0359', 'KH0405', 'G', 'G_s'), v)))
dump()
print(json.dumps(res['decision']), res['secs'], flush=True)
