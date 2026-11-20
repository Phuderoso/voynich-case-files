# POST-COMPARISON diagnostic (after reading case 212): why does my null max (-6.43) differ from hers (-6.68)?
# Variant TIE-FIRST: a 1-vs-1 residue class takes the first-voted key value in crib order (what Counter.most_common does in analyze223.py)
# instead of '?'. Representative: first hit of each D2 class (files sorted, line order).
import sys, glob, json, collections, statistics as st
import numpy as np
import nc_recount as n
from recount209 import perm_maps, excess, N, CRP, CRS, AI, INV
texts = dict(l.rstrip('\n').split('\t') for l in open(f'{n.WORK}/texts.tsv'))
def hit2(ct, ln):
    a, b = ln.split('|'); f = a.split()
    w, mode, dr, al, be, model, p, e, pi = n.decrypt(ct, f)
    sig, inv = perm_maps(w, pi)[mode]; S = inv if dr else sig
    j = [S[x] for x in CRP]
    votes = collections.OrderedDict()
    for t in range(24):
        c = AI[al][ct[j[t]]]; x = AI[al][CRS[t]]
        r = (j[t] if model else CRP[t]) % p
        votes.setdefault(r, collections.Counter())[(c + x) % 26 if be else (c - x) % 26] += 1
    key = {r: v.most_common(1)[0][0] for r, v in votes.items()}
    P = []
    for i in range(N):
        r = (S[i] if model else i) % p
        if r in key:
            c = AI[al][ct[S[i]]]; k = key[r]; P.append(INV[al][(k - c) % 26 if be else (c - k) % 26])
        else: P.append('?')
    P = ''.join(P); sc = []
    for i in range(94):
        if n.WIN[i]['overlap']: continue
        q = P[i:i+4]
        if '?' in q: continue
        sc.append(float(n.qg[n.qi(*[ord(ch)-65 for ch in q])]))
    nc = sum(sc)/len(sc) if len(sc) >= 10 else None
    return p, (al, be, model, p, tuple(j)), 97 - P.count('?'), nc, len(sc)
her = json.load(open('kryptos-main/data/cycle226/posthoc209.json'))['null_max_nc']
out = {}
for lab in texts:
    seen = set(); mx_first = None; mx_any = None; mx_first_p = {20: None, 21: None}; npass = 0
    for fn in sorted(glob.glob(f'{n.WORK}/out/{lab}/*.raw')):
        for ln in open(fn):
            if not ln.startswith('H '): continue
            p, d2, known, nc, nq = hit2(texts[lab], ln)
            if p not in (20, 21) or nc is None: first = d2 not in seen; seen.add(d2); continue
            first = d2 not in seen; seen.add(d2)
            mx_any = nc if mx_any is None else max(mx_any, nc)
            if first: mx_first = nc if mx_first is None else max(mx_first, nc)
            if first and p==21: mx_first_p[21] = nc if mx_first_p[21] is None else max(mx_first_p[21], nc)
            if first and p==20: mx_first_p[20] = nc if mx_first_p[20] is None else max(mx_first_p[20], nc)
            if nc >= -6.0 and known >= 49: npass += 1
    out[lab] = (mx_first, mx_any, npass, mx_first_p)
nl = {k: v for k, v in out.items() if k != 'K4'}
print('K4 tie-first: first-rep max', out['K4'][0], 'any-hit max', out['K4'][1], 'p20 first-rep', out['K4'][3][20], 'p21 first-rep', out['K4'][3][21], 'passes', out['K4'][2])
print('nulls tie-first: first-rep max', max(v[0] for v in nl.values() if v[0] is not None), 'any-hit max', max(v[1] for v in nl.values() if v[1] is not None), 'null passes', sum(v[2] > 0 for v in nl.values()))
print('median of first-rep maxima', round(st.median(v[0] for v in nl.values() if v[0] is not None), 3), 'hers', round(st.median(her.values()), 3))
eq = sum(abs(nl[k][0] - her[k]) < 0.0015 for k in her if nl[k][0] is not None); print('texts where first-rep max equals hers within rounding:', eq, 'of', len(her))
top = sorted(nl.items(), key=lambda kv: -kv[1][0])[:3]; print('top3 first-rep', [(k, round(v[0], 3), her[k]) for k, v in top])
print('median of any-hit maxima', round(st.median(v[1] for v in nl.values() if v[1] is not None), 3))
eq2 = sum(abs(nl[k][1] - her[k]) < 0.0015 for k in her if nl[k][1] is not None); print('texts where any-hit max equals hers:', eq2)
