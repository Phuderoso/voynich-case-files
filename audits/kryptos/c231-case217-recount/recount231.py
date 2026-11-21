#!/usr/bin/env python3
"""Blind recount of Kryptos cycle 231 (case 217): bsk230 fresh-null replicate (I-344), plus my replica nulls.
Usage: python3 recount231.py   (cwd = this dir; reads out/fresh, out/replica, out/plants, c230 K4 + old-null files named below)
Writes res/counts231.tsv, res/summary231.txt, res/rederive231.txt, res/plants231_recount.txt.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import os, re, sys, math, hashlib, random
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
N = 97; C1, C2 = 'EASTNORTHEAST', 'BERLINCLOCK'
POS = [21 + j for j in range(13)] + [63 + j for j in range(11)]; PT = [ord(c) - 65 for c in C1 + C2]
alpha = np.fromfile('w/alpha.bin', np.uint8).reshape(-1, 26); themed = np.fromfile('w/themed144.bin', np.uint8).reshape(-1, 26)
bank = np.fromfile('w/bank.bin', np.int16).reshape(-1, N); allb = np.fromfile('w/all.bin', np.int16).reshape(-1, N)
K4 = open('src/k4.txt').read().strip()
OLD = '/workspace/k230-bsk-recount/out'   # my published c230 recount outputs (K4 + 10 old nulls); same tool binary 52c8d591
def rd(p): return [l.strip() for l in open(p)]
SETS = {  # name: (dir, texts, scale per scope, n texts per scope)
 'fresh':   ('out/fresh',   rd('src/nulls231.txt'),      {'direct': 5,  'bank': 20, 'all': 20}, {'direct': 8,  'bank': 20, 'all': 20}),
 'replica': ('out/replica', rd('nulls_replica.txt'),     {'direct': 5,  'bank': 20, 'all': 20}, {'direct': 8,  'bank': 20, 'all': 20}),
 'old':     (OLD,           rd('src/nulls230_old.txt'),  {'direct': 20, 'bank': 20, 'all': 20}, {'direct': 10, 'bank': 10, 'all': 10}),
}
SCOPES = ('direct', 'bank', 'all'); CRITS = (9, 10); RULES = ('raw', 'cells', 'i291r')
LINE = re.compile(r'S perm=(-?\d+) dir=(\d) X=(\d+) Y=(\d+) form=(\d) w=(\d+) pop=(\d+) k=([A-Z]{24})')
def inv(a): r = np.empty(len(a), int); r[a] = np.arange(len(a)); return r
def kof(f, y, x): return (y - x) % 26 if f == 0 else ((x - y) % 26 if f == 1 else (y + x) % 26)
def parse(path):
    S = []; T = None
    for l in open(path):
        m = LINE.match(l)
        if m: S.append(tuple(int(x) for x in m.groups()[:7]) + (m.group(8),))
        elif l.startswith('T '): T = l.strip()
    return S, T
def minarc(kv):
    s = sorted(set(kv)); gaps = [((s[(i + 1) % len(s)] - s[i]) % 26) or 26 for i in range(len(s))]
    return (26 - max(gaps) + 1 if len(s) > 1 else 1), gaps, s
def layer(scope, q, d, ct):
    if scope == 'direct': return [ord(ct[i]) - 65 for i in range(N)]
    P = (bank if scope == 'bank' else allb)[q]; Pi = inv(P)
    return [ord(ct[(P if d == 0 else Pi)[i]]) - 65 for i in range(N)]
def rederive(scope, line, ct):
    q, d, x, y, f, w, pop, k = line; A = alpha if scope == 'direct' else themed
    cc = layer(scope, q, d, ct); cc = [cc[p] for p in POS]
    Ai, Bi = inv(A[x]), inv(A[y])
    ks = ''.join(chr(65 + kof(f, Bi[c], Ai[p])) for c, p in zip(cc, PT)); mism = []
    if ks != k: mism.append('k')
    kv = [ord(c) - 65 for c in k]
    if len(set(kv)) != pop: mism.append('pop')
    if minarc(kv)[0] != w: mism.append('w')
    return mism
def profile(scope, line, ct, crit):   # house rule: identical 97-position decrypt profile
    q, d, x, y, f, w, pop, k = line; A = alpha if scope == 'direct' else themed
    cc = layer(scope, q, d, ct); kv = [ord(c) - 65 for c in k]
    if crit == 'D': K = sorted(set(kv))
    else:
        w2, gaps, s = minarc(kv); gi = int(np.argmax(gaps)); start = s[(gi + 1) % len(s)]; K = [(start + t) % 26 for t in range(w2)]
    Ai, Bi = inv(A[x]), inv(A[y]); masks = []
    for i in range(N):
        yc = Bi[cc[i]]; m = 0
        for kk in K:
            xp = (yc - kk) % 26 if f == 0 else ((yc + kk) % 26 if f == 1 else (kk - yc) % 26)
            m |= 1 << int(A[x][xp])
        masks.append(m)
    return hashlib.sha256(np.array(masks, np.uint32).tobytes()).hexdigest()[:16]
def neg(k): return [(-v) % 26 for v in k]
def i291r(sel):   # her I-291, reconstructed: single linkage, link iff the 24-shift strings agree at >=16/24 positions, k or negated k
    n = len(sel); par = list(range(n)); kv = [[ord(c) - 65 for c in l[7]] for l in sel]; ng = [neg(v) for v in kv]
    def f(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(n):
        for j in range(i + 1, n):
            a = sum(u == v for u, v in zip(kv[i], kv[j])); b = sum(u == v for u, v in zip(ng[i], kv[j]))
            if max(a, b) >= 16: par[f(i)] = f(j)
    return len({f(i) for i in range(n)})
def count(scope, S, ct, W):
    sel = [l for l in S if l[5] <= W]
    return {'raw': len(sel), 'cells': len({profile(scope, l, ct, 'W') for l in sel}), 'i291r': i291r(sel) if sel else 0}
def wilson(k, n, z=1.959964):
    if n == 0: return (0.0, 1.0)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))
SL = {'direct': 5, 'bank': 20, 'all': 20}
def slice_of(scope, l): return l[2] % 5 if scope == 'direct' else l[0] % 20
def dist_wilson(o_hits, S, m, n):
    L, U = wilson(m, n); o = o_hits / S; o0 = max(o, 0.5 / S)
    if o > U: return 'above', o / U, (L, U), o
    if o < L: return 'below', L / o0, (L, U), o
    return 'inside', min(U / o0, (o0 / L) if L > 0 else float('inf')), (L, U), o
def rank_label(kmean, ns, mf):
    mx, mn = max(ns), min(ns)
    lit = 'EXCESS' if kmean > mx else ('INSUFFICIENT-DISCRIMINATION' if mf < 3 else ('NO-SIGNAL' if mn <= kmean <= mx else 'BELOW-MIN'))
    prim = 'INSUFFICIENT-DISCRIMINATION' if mf < 3 else ('EXCESS' if kmean > mx else ('NO-SIGNAL' if mn <= kmean <= mx else 'BELOW-MIN'))
    return prim, lit
def boot(vals, scale, B=20000, seed=231):
    r = random.Random(seed); n = len(vals); xs = sorted(sum(vals[r.randrange(n)] for _ in range(n)) * scale / n for _ in range(B))
    return xs[int(0.025 * B)], xs[int(0.975 * B)]
def main():
    rows = []; log = []; data = {}
    # K4 (c230 files: tool/binary identical, no re-selection)
    k4 = {}
    for sc in SCOPES:
        S, T = parse(f'{OLD}/k4_{sc}.txt'); bad = [l for l in S if rederive(sc, l, K4)]
        for l in bad: log.append(f'MISMATCH k4 {sc} {l[:7]}')
        k4[sc] = S
        for W in CRITS:
            c = count(sc, S, K4, W); data[('k4', sc, W)] = c
            rows.append(('k4', sc, W, 0, T, c['raw'], c['cells'], c['i291r']))
    nul = {}
    for nm, (d, texts, scale, nn) in SETS.items():
        for sc in SCOPES:
            for i in range(nn[sc]):
                S, T = parse(f'{d}/null{i}_{sc}.txt')
                for l in S:
                    mm = rederive(sc, l, texts[i])
                    if mm: log.append(f'MISMATCH {nm} null{i} {sc} {l[:7]} {mm}')
                for W in CRITS:
                    c = count(sc, S, texts[i], W); nul[(nm, sc, W, i)] = c
                    rows.append((f'{nm}:null{i}', sc, W, len([l for l in S if l[5] <= W]) > 0, T, c['raw'], c['cells'], c['i291r']))
    with open('res/counts231.tsv', 'w') as f:
        f.write('text\tscope\tW\thit\tT_line\traw\tcells_house\tclusters_I291R\n')
        for r in rows: f.write('\t'.join(str(x) for x in r) + '\n')
    open('res/rederive231.txt', 'w').write('\n'.join(log) + ('\n' if log else '') + f'mismatch lines: {len(log)}\n')
    out = []; P = out.append
    P('# summary231 (my counts; all numbers from my own bsk230 outputs; K4 = my c230 K4 files, same binary)')
    for sc in SCOPES:
        for W in CRITS:
            kc = data[('k4', sc, W)]; Sk = SL[sc]; scale = SETS['fresh'][2][sc]
            ks = [l for l in k4[sc] if l[5] <= W]; k_slices = {slice_of(sc, l) for l in ks}
            P(f'\n## {sc} W<={W}: K4 raw {kc["raw"]} cells(house) {kc["cells"]} clusters(I-291R) {kc["i291r"]}; K4 occupied slices {len(k_slices)}/{Sk}')
            res = {}
            for nm in ('fresh', 'replica'):
                n = SETS[nm][3][sc]; hits = [nul[(nm, sc, W, i)] for i in range(n)]; m = sum(h['raw'] > 0 for h in hits)
                side, dw, (L, U), o = dist_wilson(len(k_slices), Sk, m, n)
                s1, d1, _, _ = dist_wilson(1 if ks else 0, 1, m, n)
                P(f'  [{nm}] single-text reading (K4 = one text, hit indicator {1 if ks else 0}): side {s1}, Wilson distance {d1:.2f}x')
                P(f'  [{nm}] n={n} scale x{scale}; texts with >=1 line {m}/{n} (null hit rate {m/n:.3f}, Wilson95 [{L:.3f},{U:.3f}]); K4 slice-hit rate {o:.3f} -> side {side}, Wilson distance {dw:.2f}x')
                for rule in RULES:
                    ns = [h[rule] for h in hits]; NE = sum(ns) * scale / n; lo, hi = boot(ns, scale)
                    kmean = kc[rule] / scale; prim, lit = rank_label(kmean, ns, m)
                    cmax = max(ns); cd = (kmean / cmax if kmean > cmax and cmax > 0 else (cmax / kmean if kmean > 0 and cmax > 0 else float('inf')))
                    hc = [x for x in ns if x > 0]; cph = (sum(hc) / len(hc)) if hc else 0.0
                    P(f'    {rule:6s}: per-null {ns} sum {sum(ns)} NE=sum*{scale}/{n}={NE:.2f} (boot95 {lo:.1f}-{hi:.1f}); clusters/hit-text {cph:.2f}; K4 {kc[rule]} (per-slice {kmean:.2f}, null max {cmax}); rank label {prim} (literal-order {lit}); count-distance {cd:.2f}x')
                    res[(nm, rule)] = (prim, lit, NE)
                res[(nm, 'wil')] = (side, dw)
            for rule in RULES:
                a = res[('fresh', rule)][0]; b = res[('replica', rule)][0]
                sf, df = res[('fresh', 'wil')]; sr, dr = res[('replica', 'wil')]
                rob = (df >= 2 and sf == sr)
                P(f'  LABEL[{rule}] fresh {a} / replica {b}; Wilson side {sf}/{sr}, distance {df:.2f}x / {dr:.2f}x -> {a}{"" if (rob and a == b) else "-FRONTEIRA"}{" (robusto)" if (rob and a == b) else ""}')
            # pooled with old 10 nulls (descriptive): mean over texts of count_i / fraction_i
            for rule in RULES:
                vals = [nul[('old', sc, W, i)][rule] * 20 for i in range(10)] + [nul[('fresh', sc, W, i)][rule] * SETS['fresh'][2][sc] for i in range(SETS['fresh'][3][sc])]
                th = sum(nul[('old', sc, W, i)]['raw'] > 0 for i in range(10)) + sum(nul[('fresh', sc, W, i)]['raw'] > 0 for i in range(SETS['fresh'][3][sc]))
                P(f'  POOLED old10+fresh{SETS["fresh"][3][sc]} [{rule}]: NE {sum(vals)/len(vals):.2f}, texts with a line {th}/{len(vals)}')
    open('res/summary231.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out)); print('rederive mismatches:', len(log))
if __name__ == '__main__': main()
