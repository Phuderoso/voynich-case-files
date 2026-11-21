#!/usr/bin/env python3
"""Blind recount of cycle 230 bsk230 survivors: parse tool output, re-derive shifts / width / pop, cluster by decrypt profile.
Usage: python3 bsk_recount.py OUTDIR  (reads OUTDIR/{k4,null0..9}_{direct,bank,all}.txt, writes counts_cells.tsv, rederive.txt, summary_bsk.txt)
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import sys, re, os, hashlib
import numpy as np
W = os.path.dirname(os.path.abspath(__file__)) + '/w/'
K4 = open(os.path.dirname(os.path.abspath(__file__)) + '/kryptos-main/data/cycle230/k4.txt').read().strip()
N = 97; C1, C2 = 'EASTNORTHEAST', 'BERLINCLOCK'
POS = [21 + j for j in range(13)] + [63 + j for j in range(11)]; PT = [ord(c) - 65 for c in C1 + C2]
alpha = np.fromfile(W + 'alpha.bin', np.uint8).reshape(-1, 26); themed = np.fromfile(W + 'themed144.bin', np.uint8).reshape(-1, 26)
bank = np.fromfile(W + 'bank.bin', np.int16).reshape(-1, N); allb = np.fromfile(W + 'all.bin', np.int16).reshape(-1, N)
def inv(a): r = np.empty(len(a), int); r[a] = np.arange(len(a)); return r
LINE = re.compile(r'S perm=(-?\d+) dir=(\d) X=(\d+) Y=(\d+) form=(\d) w=(\d+) pop=(\d+) k=([A-Z]{24})')
def kof(f, y, x): return (y - x) % 26 if f == 0 else ((x - y) % 26 if f == 1 else (y + x) % 26)
def parse(path):
    S = []; T = None
    for l in open(path):
        m = LINE.match(l)
        if m: S.append(tuple(int(x) for x in m.groups()[:7]) + (m.group(8),))
        elif l.startswith('T '): T = l.strip()
    return S, T
def rederive(scope, line, ct):
    q, d, x, y, f, w, pop, k = line; mism = []
    A, B = (alpha, alpha) if scope == 'direct' else (themed, themed)
    if scope == 'direct': cc = [ord(ct[p]) - 65 for p in POS]
    else:
        P = (bank if scope == 'bank' else allb)[q]; Pi = inv(P)
        cc = [ord(ct[(P if d == 0 else Pi)[p]]) - 65 for p in POS]
    Ai, Bi = inv(A[x]), inv(B[y])
    ks = ''.join(chr(65 + kof(f, Bi[c], Ai[p])) for c, p in zip(cc, PT))
    if ks != k: mism.append('k')
    kv = [ord(c) - 65 for c in k]; pop2 = len(set(kv))
    # minimal circular window covering all values
    s = sorted(set(kv)); gaps = [((s[(i + 1) % len(s)] - s[i]) % 26) or 26 for i in range(len(s))]
    w2 = 26 - max(gaps) + 1 if len(s) > 1 else 1
    if pop2 != pop: mism.append('pop')
    if w2 != w: mism.append('w')
    return mism
def profile(scope, line, ct, crit):
    q, d, x, y, f, w, pop, k = line
    A = alpha if scope == 'direct' else themed; B = A
    if scope == 'direct': cc = [ord(ct[i]) - 65 for i in range(N)]
    else:
        P = (bank if scope == 'bank' else allb)[q]; Pi = inv(P)
        cc = [ord(ct[(P if d == 0 else Pi)[i]]) - 65 for i in range(N)]
    kv = [ord(c) - 65 for c in k]
    if crit == 'D': K = sorted(set(kv))
    else:
        s = sorted(set(kv)); gaps = [((s[(i + 1) % len(s)] - s[i]) % 26) or 26 for i in range(len(s))]
        gi = int(np.argmax(gaps)); start = s[(gi + 1) % len(s)]; K = [(start + t) % 26 for t in range(w)]
        assert set(kv) <= set(K)
    Ai, Bi = inv(A[x]), inv(B[y]); masks = []
    for i in range(N):
        yc = Bi[cc[i]]; m = 0
        for kk in K:
            xp = (yc - kk) % 26 if f == 0 else ((yc + kk) % 26 if f == 1 else (kk - yc) % 26)
            m |= 1 << int(A[x][xp])
        masks.append(m)
    return hashlib.sha256(np.array(masks, np.uint32).tobytes()).hexdigest()[:16]
def main(out):
    nulls = [l.strip() for l in open(os.path.dirname(os.path.abspath(__file__)) + '/nulls230_mine.txt')]
    rows = []; log = []; summ = {}
    for scope in ('direct', 'bank', 'all'):
        for name, ct in [('k4', K4)] + [(f'null{i}', nulls[i]) for i in range(10)]:
            S, T = parse(f'{out}/{name}_{scope}.txt'); bad = 0
            for ln in S:
                mm = rederive(scope, ln, ct)
                if mm: bad += 1; log.append(f'MISMATCH {scope} {name} {ln[:7]} {mm}')
            for crit, sel in (('W9', [l for l in S if l[5] <= 9]), ('D6', [l for l in S if l[6] <= 6])):
                cells = {profile(scope, l, ct, crit[0]) for l in sel}; xy = {(l[2], l[3]) for l in sel}
                rows.append((scope, crit, name, len(S), len(sel), len(cells), len(xy), T, bad))
    with open(out + '/../counts_cells.tsv', 'w') as f:
        f.write('scope\tcriterion\ttext\ttool_lines_all\traw_lines_in_criterion\tcells_my_rule\tdistinct_XY\tT_line\trederive_mismatch_lines\n')
        for r in rows: f.write('\t'.join(str(x) for x in r) + '\n')
    open(out + '/../rederive.txt', 'w').write('\n'.join(log) + ('\n' if log else '') + f'mismatch lines: {len(log)}\n')
    lines = []
    for scope in ('direct', 'bank', 'all'):
        for crit in ('W9', 'D6'):
            k = [r for r in rows if r[0] == scope and r[1] == crit and r[2] == 'k4'][0]
            ns = [r for r in rows if r[0] == scope and r[1] == crit and r[2] != 'k4']
            c = [r[5] for r in ns]; raw = [r[4] for r in ns]
            lines.append(f'{scope:6s} {crit}: K4 raw {k[4]} cells {k[5]} (XY {k[6]}) | nulls cells {c} sum {sum(c)} mean/null {sum(c)/10:.2f} NE=(sum*20)/10={sum(c)*20/10:.1f} | nulls with >=1 cell {sum(x>0 for x in c)}/10 | raw lines per null {raw}')
    open(out + '/../summary_bsk.txt', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines)); print('rederive mismatches:', len(log))
if __name__ == '__main__': main(sys.argv[1])
