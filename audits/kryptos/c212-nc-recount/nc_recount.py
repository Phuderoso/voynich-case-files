#!/usr/bin/env python3
"""NC recount per RULE.md (sha256 in FROZEN.txt). Reuses only perm_maps/excess logic from my own recount209.py."""
import sys, os, glob, collections, json
import numpy as np
sys.path.insert(0, '/workspace/k209-d2-audit')
from recount209 import perm_maps, excess, N, CRP, CRS, AI, INV
WORK = '/workspace/k209-d2-work'
qg = np.fromfile(f'{WORK}/qg.bin', dtype=np.float32)
def qi(a, b, c, d): return ((a*26+b)*676 + c*26 + d)
CRIBPOS = set(CRP)
WIN = {}
for i in range(94):
    span = range(i, i+4)
    WIN[i] = dict(overlap=any(x in CRIBPOS for x in span), inside=all(x in CRIBPOS for x in span))
# crib-inside: all four letters in one crib (cribs are 21-33 and 63-73, windows cannot span both)
def decrypt(ct, f):
    w, mode, dr, al, be, model, p, e, bad = map(int, f[2:11]); pi = tuple(map(int, f[11:]))
    return w, mode, dr, al, be, model, p, e, pi
cache = {}
def hit(ct, ln):
    a, b = ln.split('|'); f = a.split(); j_pr = list(map(int, b.split()))
    w, mode, dr, al, be, model, p, e, pi = decrypt(ct, f)
    if (w, pi) not in cache: cache[(w, pi)] = perm_maps(w, pi)
    sig, inv = cache[(w, pi)][mode]; S = inv if dr else sig
    j = [S[x] for x in CRP]; assert j == j_pr
    kv = [((AI[al][ct[j[t]]] + AI[al][CRS[t]]) % 26) if be else ((AI[al][ct[j[t]]] - AI[al][CRS[t]]) % 26) for t in range(24)]
    res = [(j[t] if model else CRP[t]) % p for t in range(24)]
    ee, cls = excess(res, kv); assert ee == e and ee <= 1
    kres = {}
    for r, c in cls.items():
        mc = c.most_common()
        if len(mc) == 1 or mc[0][1] > mc[1][1]: kres[r] = mc[0][0]
    P = []
    for i in range(N):
        r = (S[i] if model else i) % p
        if r in kres:
            x = AI[al][ct[S[i]]]; k = kres[r]
            P.append(INV[al][(x-k) % 26 if be == 0 else (k-x) % 26])
        else: P.append('?')
    P = ''.join(P)
    d2 = (al, be, model, p, tuple(j))
    out = {}
    for name, key in (('overlap', 'overlap'), ('inside', 'inside')):
        sc = []
        for i in range(94):
            if WIN[i][key]: continue
            q = P[i:i+4]
            if '?' in q: continue
            sc.append(float(qg[qi(*[ord(ch)-65 for ch in q])]))
        out[name] = (sum(sc)/len(sc) if len(sc) >= 10 else None, len(sc))
    known = 97 - P.count('?')
    return p, d2, known, out, P
def passes(nc, nq, known): return nc is not None and nc >= -6.0 and known >= 49 and nq >= 10
def run():
    texts = dict(l.rstrip('\n').split('\t') for l in open(f'{WORK}/texts.tsv'))
    labs = list(texts)
    rows = []; best = {}
    for lab in labs:
        files = sorted(glob.glob(f'{WORK}/out/{lab}/*.raw'))
        lines = [l for fn in files for l in open(fn) if l.startswith('H ')]
        R = {v: dict(raw=0, d2=set(), pass_hits=0, pass_d2=set(), pass_d2_first=set(), seen_first=set(), mx=None, mx49=None) for v in ('p20p21', 'p21', 'p20', 'inside')}
        for ln in lines:
            p, d2, known, out, P = hit(texts[lab], ln)
            for v in R:
                if v in ('p21', ) and p != 21: continue
                if v == 'p20' and p != 20: continue
                if p not in (20, 21): continue
                kind = 'inside' if v == 'inside' else 'overlap'
                nc, nq = out[kind]; r = R[v]
                r['raw'] += 1; r['d2'].add(d2)
                first = d2 not in r['seen_first']; r['seen_first'].add(d2)
                if nc is not None:
                    r['mx'] = nc if r['mx'] is None else max(r['mx'], nc)
                    if known >= 49: r['mx49'] = nc if r['mx49'] is None else max(r['mx49'], nc)
                if passes(nc, nq, known):
                    r['pass_hits'] += 1; r['pass_d2'].add(d2)
                    if first: r['pass_d2_first'].add(d2)
        for v, r in R.items():
            rows.append((lab, v, r['raw'], len(r['d2']), r['pass_hits'], len(r['pass_d2']), len(r['pass_d2_first']),
                         'NA' if r['mx'] is None else f"{r['mx']:.4f}", 'NA' if r['mx49'] is None else f"{r['mx49']:.4f}"))
        print(lab, flush=True, file=sys.stderr)
    with open('counts_nc.tsv', 'w') as f:
        f.write('text\tvariant\traw_hits\td2_classes\tpass_hits\tpass_d2\tpass_d2_firsthit_rep\tmaxNC\tmaxNC49\n')
        for r in rows: f.write('\t'.join(map(str, r)) + '\n')
    S = []
    for v in ('p20p21', 'p21', 'p20', 'inside'):
        k4 = [r for r in rows if r[0] == 'K4' and r[1] == v][0]
        nl = [r for r in rows if r[0] != 'K4' and r[1] == v]
        npass = sum(r[4] > 0 for r in nl); npassf = sum(r[6] > 0 for r in nl)
        mxs = [float(r[7]) for r in nl if r[7] != 'NA']; mx49 = [float(r[8]) for r in nl if r[8] != 'NA']
        S.append(f"variant {v}: K4 raw {k4[2]} d2 {k4[3]} pass_hits {k4[4]} pass_d2 {k4[5]} (first-hit rep {k4[6]}); K4 maxNC {k4[7]} maxNC49 {k4[8]}; "
                 f"nulls n={len(nl)} with>=1 pass {npass}/{len(nl)} (first-hit rep {npassf}); null maxNC {max(mxs):.4f} (n_with_NC {len(mxs)}) null maxNC49 {max(mx49):.4f} (n {len(mx49)}); "
                 f"null passing D2 total {sum(r[5] for r in nl)}")
    open('summary_nc.txt', 'w').write('\n'.join(S) + '\n'); print('\n'.join(S))
if __name__ == '__main__': run()
