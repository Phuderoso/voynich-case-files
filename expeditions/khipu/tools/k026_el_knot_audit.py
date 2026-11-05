#!/usr/bin/env python3
"""K026 - concentration (H1) and field classification (H2) of K007's E/L knot violations.
Pre-registered in case-file/K026-el-knot-audit.md. Usage: python3 tools/k026_el_knot_audit.py khipu.db"""
import sqlite3, sys, json, re
import numpy as np
from collections import Counter, defaultdict
c = sqlite3.connect(sys.argv[1])
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
meta = {r[0]: (r[1], r[2] or '') for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
cord_kh = {r[0]: r[1] for r in c.execute("select CORD_ID, KHIPU_ID from cord")}
KC = {r[0]: (r[1], r[2]) for r in c.execute("select CLUSTER_ID, CORD_ID, ORDINAL from knot_cluster")}
maxord = defaultdict(lambda: -1)
for cl, (cd, o) in KC.items():
    if o is not None: maxord[cd] = max(maxord[cd], o)
A = []  # audited knots
for cd, t, v, cl, kid, tr in c.execute("select CORD_ID, TYPE_CODE, knot_value_type, CLUSTER_ID, KNOT_ID, NUM_TURNS from knot"):
    kh = cord_kh.get(cd)
    if kh is None or kh in dups: continue
    t = (t or '').strip()
    if t == 'E': viol = v != 1
    elif t == 'L' and tr is not None: viol = not (2 <= tr <= 9 and v == int(tr))
    else: continue
    A.append(dict(kid=kid, kh=kh, t=t, v=v, tr=tr, cd=cd, cl=cl, viol=viol))
print('audited', len(A), 'violations', sum(a['viol'] for a in A))
def series(inv):
    m = re.match(r'[A-Za-z]+', inv.strip()); return m.group(0).upper() if m else '?'
khs = sorted({a['kh'] for a in A}); khi = {k: i for i, k in enumerate(khs)}
sers = sorted({series(meta[k][1]) for k in khs}); sei = {s: i for i, s in enumerate(sers)}
gk = np.array([khi[a['kh']] for a in A]); gs = np.array([sei[series(meta[a['kh']][1])] for a in A])
typ = np.array([a['t'] == 'E' for a in A]); lab = np.array([a['viol'] for a in A])
def expected(g, ng):
    e = np.zeros(ng)
    for tmask in (typ, ~typ):
        nv = lab[tmask].sum(); cnt = np.bincount(g[tmask], minlength=ng)
        e += nv * cnt / tmask.sum()
    return e
def Gstat(labels, g, ng, e):
    o = np.bincount(g[labels], minlength=ng).astype(float); m = o > 0
    return 2 * np.sum(o[m] * np.log(o[m] / e[m]))
rng = np.random.default_rng(26026)
idxE = np.where(typ)[0]; idxL = np.where(~typ)[0]; nE = lab[typ].sum(); nL = lab[~typ].sum()
def null_labels():
    L = np.zeros(len(A), bool); L[rng.choice(idxE, nE, replace=False)] = True; L[rng.choice(idxL, nL, replace=False)] = True; return L
R = 10000; res = {}
for name, g, ng in (('khipu', gk, len(khs)), ('series', gs, len(sers))):
    e = expected(g, ng); obs = Gstat(lab, g, ng, e)
    nulls = np.array([Gstat(null_labels(), g, ng, e) for _ in range(R)])
    p = (1 + np.sum(nulls >= obs)) / (R + 1)
    res[name] = dict(G_obs=float(obs), null_mean=float(nulls.mean()), null_q99=float(np.quantile(nulls, 0.99)), p=float(p), supported=bool(p < 0.025))
    # power: 50 extra violations into 3 random khipus (relabel valid knots there)
    if name == 'khipu':
        q975 = np.quantile(nulls, 1 - 0.025); hits = 0
        for _ in range(100):
            L = null_labels(); pick = rng.choice(len(khs), 3, replace=False)
            cand = np.where(np.isin(gk, pick) & ~L)[0]
            if len(cand) < 50: cand = np.where(~L)[0]
            L[rng.choice(cand, min(50, len(cand)), replace=False)] = True
            hits += Gstat(L, gk, len(khs), expected(gk, len(khs))) > q975
        res[name]['power_50_in_3'] = hits / 100
    o = np.bincount(g[lab], minlength=ng); keys = khs if name == 'khipu' else sers
    top = sorted(range(ng), key=lambda i: -(o[i] - e[i]))[:12]
    res[name]['top_excess'] = [dict(group=(meta[keys[i]][0] + ' ' + meta[keys[i]][1]) if name == 'khipu' else keys[i], obs=int(o[i]), exp=round(float(e[i]), 2)) for i in top]
# H2
def p10(v):
    if not v or v <= 0: return None
    k = 0
    while v % 10 == 0: v //= 10; k += 1
    return k if v == 1 else None
cat = defaultdict(list)
for a in A:
    if not a['viol']: continue
    v, tr = a['v'], a['tr']
    if a['t'] == 'E':
        k = p10(v)
        if not v: cat['E-zero'].append(a)
        elif k and k >= 1:
            last = KC.get(a['cl'], (None, None))[1] == maxord[a['cd']]
            cat['E-value' if last else 'E-type'].append(a)
        else: cat['E-other'].append(a)
    else:
        if 2 <= tr <= 9:
            if not v: cat['L-zero'].append(a)
            elif v % int(tr) == 0 and p10(v // int(tr)) and v != tr: cat['L-shift'].append(a)
            elif abs(v - tr) == 1: cat['L-off1'].append(a)
            else: cat['L-other'].append(a)
        elif tr == 1: cat['L-turn1'].append(a)
        elif tr == 0: cat['L-turn0'].append(a)
        else: cat['L-turn10+'].append(a)
h2 = {k: dict(n=len(v), noteworthy=len(v) >= 20, khipus=Counter(meta[a['kh']][0] + ' ' + meta[a['kh']][1] for a in v).most_common(5),
              values=Counter((a['v'], a['tr']) for a in v).most_common(5), examples=[a['kid'] for a in v[:8]]) for k, v in sorted(cat.items())}
out = dict(n_audited=len(A), n_violations=int(lab.sum()), nE_viol=int(nE), nL_viol=int(nL), H1=res, H2=h2)
json.dump(out, open('analysis/k026_results.json', 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:6000])
