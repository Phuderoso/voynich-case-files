#!/usr/bin/env python3
"""K007 - exact audit of knot_value_type against the decimal rules. Pre-registered in case-file/K007-decoding-audit.md.
Usage: python3 tools/k007_decoding_audit.py data/khipu.db"""
import sqlite3, sys, json, math, random
from collections import defaultdict, Counter
c = sqlite3.connect(sys.argv[1])
dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
okr = {r[0]: (r[1], r[2]) for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM from khipu_main")}
cord_kh = {r[0]: r[1] for r in c.execute("select CORD_ID, KHIPU_ID from cord")}
K = [dict(cord=r[0], t=(r[1] or '').strip(), v=r[2], cl=r[3], kid=r[4], clo=r[5], turns=r[6])
     for r in c.execute("select CORD_ID, TYPE_CODE, knot_value_type, CLUSTER_ID, KNOT_ID, CLUSTER_ORDINAL, NUM_TURNS from knot")]
K = [k for k in K if cord_kh.get(k['cord']) not in dups]
# Fix 2 (disclosed): knot.CLUSTER_ORDINAL is the knot's position inside its cluster, not the cluster's position on the
# cord. The cluster's position is knot_cluster.ORDINAL. TOTAL_VALUE is used for the exploratory check R8.
KC = {r[0]: (r[1], r[2], r[3]) for r in c.execute("select CLUSTER_ID, CORD_ID, ORDINAL, TOTAL_VALUE from knot_cluster")}
for k in K: k['clo'] = KC.get(k['cl'], (None, None, None))[1]
def place(v):
    if v is None or v <= 0: return None
    p = 0
    while v % 10 == 0: v //= 10; p += 1
    return p
def is_pow10(v): return v is not None and v > 0 and 10 ** place(v) == v
def audit(K, direction=None):
    viol = defaultdict(list); n = Counter()
    for k in K:
        if k['t'] == 'E': n['R1'] += 1; (k['v'] != 1) and viol['R1'].append(k['kid'])
        elif k['t'] == 'L':
            tr = k['turns']
            if tr is None: n['R2_no_turns'] += 1; continue  # Fix 3 (disclosed): turns not recorded = not auditable
            n['R2'] += 1
            if not (tr is not None and 2 <= tr <= 9 and k['v'] == int(tr)): viol['R2'].append(k['kid'])
        elif k['t'] == 'S': n['R3'] += 1; (not is_pow10(k['v'])) and viol['R3'].append(k['kid'])
        else: n['unknown_type'] += 1
    bycl = defaultdict(list)
    for k in K: bycl[k['cl']].append(k)
    clplace = {}
    for cl, ks in bycl.items():
        pl = {place(k['v']) if k['t'] == 'S' else 0 for k in ks if k['t'] in 'SLE' and k['t'] and k['v']}
        if len(ks) >= 2: n['R4'] += 1; (len(pl) > 1) and viol['R4'].append(cl)
        if len(pl) == 1: clplace[cl] = pl.pop()
        n['R7c'] += 1
        if len(ks) > 9 and all(k['t'] == 'S' for k in ks): viol['R7'].append(cl)
    bycord = defaultdict(dict)
    for k in K:
        if k['clo'] is None: n['no_cluster_ordinal'] += 1; continue
        if k['cl'] in clplace: bycord[k['cord']][k['clo']] = clplace[k['cl']]
    seqs = {cd: [d[o] for o in sorted(d)] for cd, d in bycord.items() if len(d) >= 2}
    dec = sum(all(a > b for a, b in zip(s, s[1:])) for s in seqs.values()); inc = sum(all(a < b for a, b in zip(s, s[1:])) for s in seqs.values())
    if direction is None: direction = 'decreasing' if dec >= inc else 'increasing'
    for cd, s in seqs.items():
        n['R5'] += 1; ok = all((a > b) if direction == 'decreasing' else (a < b) for a, b in zip(s, s[1:]))
        if not ok: viol['R5'].append(cd)
    le = defaultdict(list)
    for k in K:
        if k['t'] in ('L', 'E'): le[k['cord']].append(k)
    for cd, ks in le.items():
        n['R6'] += 1; n['R7cords'] += 1
        pls = [p for p in bycord.get(cd, {}).values()]
        if pls and any(clplace.get(k['cl'], 0) != min(pls) or clplace.get(k['cl'], 0) != 0 for k in ks): viol['R6'].append(cd)
        if len(ks) > 1: viol['R7'].append(cd)
    n['R7'] = n['R7c'] + n['R7cords']
    sums = defaultdict(int)
    for k in K:
        if k['v'] is not None: sums[k['cl']] += k['v']
    for cl in bycl:
        tv = KC.get(cl, (None, None, None))[2]
        if tv is None: continue
        n['R8'] += 1
        if tv != sums[cl]: viol['R8'].append(cl)
    return viol, n, direction, dec, inc
viol, n, direction, dec, inc = audit(K)
# planted control: 50 violations per rule on a copy
random.seed(7007); P = [dict(k) for k in K]; planted = {}
E = [k for k in P if k['t'] == 'E' and k['v'] == 1]; L = [k for k in P if k['t'] == 'L' and k['turns'] and 2 <= k['turns'] <= 9 and k['v'] == int(k['turns'])]
S = [k for k in P if k['t'] == 'S' and is_pow10(k['v'])]
for k in random.sample(E, 50): k['v'] = 2
for k in random.sample(L, 50): k['v'] = int(k['turns']) + 1 if k['turns'] < 9 else 7
for k in random.sample(S, 50): k['v'] = k['v'] * 3
pv, _, _, _, _ = audit(P, direction)
ctrl = {r: len(set(pv[r]) - set(viol[r])) for r in ('R1', 'R2', 'R3')}
rate = {r: (len(viol[r]), n[r if r != 'R7' else 'R7'], round(len(viol[r]) / max(n[r], 1), 5)) for r in ('R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8')}
khcount = {r: Counter(okr.get(cord_kh.get(x) if r in ('R5', 'R6', 'R7') else None, ('?', '?'))[0] for x in viol[r]) for r in ()}
# per-khipu violations
kid_cord = {k['kid']: k['cord'] for k in K}; cl_cord = {k['cl']: k['cord'] for k in K}
def kh_of(r, x):
    cd = kid_cord.get(x) if r in ('R1', 'R2', 'R3') else (cl_cord.get(x) if r in ('R4', 'R8') else x)
    if r == 'R7' and x in cl_cord and x not in cord_kh: cd = cl_cord[x]
    return okr.get(cord_kh.get(cd), ('?', '?'))
perkh = defaultdict(Counter)
for r, xs in viol.items():
    for x in xs: perkh[kh_of(r, x)][r] += 1
top = sorted(perkh.items(), key=lambda kv: -sum(kv[1].values()))[:25]
named = ['KH0349', 'KH0140', 'KH0483', 'KH0362', 'KH0049', 'KH0305', 'KH0301', 'KH0304', 'KH0303', 'KH0128', 'KH0137']
out = dict(n_knots=len(K), counts=dict(n), direction=direction, monotone_dec=dec, monotone_inc=inc, rates=rate,
           planted_found_of_50=ctrl, khipus_with_any_violation=len(perkh),
           top_khipus=[dict(okr=a[0], inv=a[1], **dict(b)) for a, b in top],
           named=[dict(okr=a[0], inv=a[1], **dict(b)) for a, b in perkh.items() if a[0] in named],
           examples={r: [x for x in viol[r][:10]] for r in viol})
json.dump(out, open('analysis/k007_results.json', 'w'), indent=1, default=str)
print(json.dumps({k: out[k] for k in ('n_knots', 'counts', 'direction', 'monotone_dec', 'monotone_inc', 'rates', 'planted_found_of_50', 'khipus_with_any_violation', 'named')}, indent=1, default=str))
for t in out['top_khipus'][:12]: print(t)
