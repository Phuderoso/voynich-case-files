#!/usr/bin/env python3
"""C130 audit (Voynich desk): where do the one-error plants of my Kryptos audits sit in the solver's constraint structure,
and what is the floor p of my two-batch gate?  Pre-registered in PREREG.md (same folder) BEFORE this script was run.
No randomness, no seed.  usage: python3 structure130.py VC236_W KCF_PLANTS232 C232_SUMMARY_TXT VCF_ROOT > result130.txt
  VC236_W          = dir with plants236.tsv, keys236.bin, alpha.bin, themed144.bin, bank.bin, all.bin (case 222 audit inputs)
  KCF_PLANTS232    = data/cycle232/plants232.tsv of kryptos-case-files (sha 2f481d6a...)
  C232_SUMMARY_TXT = audits/kryptos/c232-case218-recount/res/summary232_voynich.txt (my published per-plant recovery)
  VCF_ROOT         = voynich-case-files working copy (analysis/C095/C097/C098 results JSON)
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04"""
import sys, os, re, json, math, struct
from collections import Counter
N = 97; POS = list(range(21, 34)) + list(range(63, 74)); CR = 'EASTNORTHEAST' + 'BERLINCLOCK'
A_KEY, B_KEY = set(range(0, 4)), set(range(13, 17))

def wilson(k, n, z=1.959964):
    if n == 0: return (float('nan'), float('nan'))
    p = k / n; c = (p + z * z / (2 * n)) / (1 + z * z / n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, c - h), min(1.0, c + h))

def poisbin(ps):
    d = [1.0]
    for p in ps:
        e = [0.0] * (len(d) + 1)
        for k, v in enumerate(d): e[k] += v * (1 - p); e[k + 1] += v * p
        d = e
    return d

def two_sided(d, k):
    return min(1.0, sum(v for v in d if v <= d[k] * (1 + 1e-12)))

def rec(fn, n): b = open(fn, 'rb').read(); return [b[i:i + n] for i in range(0, len(b), n)]

def part1(W):
    print('== PART 1: case 222 (cycle 236) gate P, gn217 model Q (fixed key window, enumerated X/Y/form/perm) ==')
    print('Constraint multigraph: no unknown is solved from the crib; every seat is a self-check (loop) -> bridges 0, pendant edges 0 by construction.')
    print('Retrieval structure (gn217.c): pass A joins on seats 0-3, pass B on seats 13-16; SINGLE-PATH seat = in A_KEY or B_KEY, else DOUBLE-PATH.')
    K = open(W + '/keys236.bin', 'rb').read(); AL, TH = rec(W + '/alpha.bin', 26), rec(W + '/themed144.bin', 26)
    banks = {s: open(W + f'/{s}.bin', 'rb').read() for s in ('bank', 'all')}
    rows = [l.rstrip('\n').split('\t') for l in open(W + '/plants236.tsv')]
    passes = {}
    for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'c236-case222-blind', 'compare236.txt')):
        m = re.match(r'^(\d+) (direct|bank|all) seat (-?\d+) lines \d+ mismatches=\d+ (PASS|FAIL)', l)
        if m: passes[int(m.group(1))] = m.group(4) == 'PASS'
    out = []
    for pid, scope, ct, qi, dr, ix, x, y, f, w, seat, pt in rows:
        pid, qi, dr, ix, x, y, f, w, seat = map(int, (pid, qi, dr, ix, x, y, f, w, seat))
        if scope == 'direct': S = list(range(N)); X, Y = AL[x], AL[y]
        else:
            b = banks[scope]; P = list(struct.unpack('<97h', b[qi * 194:(qi + 1) * 194])); inv = [0] * N
            for i, v in enumerate(P): inv[v] = i
            S = P if dr == 0 else inv; X, Y = TH[x], TH[y]
        yinv = [0] * 26
        for i, v in enumerate(Y): yinv[v] = i
        kw = K[w * N:(w + 1) * N]; C = [ord(c) - 65 for c in ct]; dec = []
        for i in range(N):
            k = kw[i] if ix == 0 else kw[S[i]]; yy = yinv[C[S[i]]]
            xx = (yy - k) % 26 if f == 0 else (yy + k) % 26 if f == 1 else (k - yy) % 26
            dec.append(chr(65 + X[xx]))
        miss = [j for j in range(24) if dec[POS[j]] != CR[j]]
        pA = all(j not in miss for j in A_KEY); pB = all(j not in miss for j in B_KEY)
        if seat < 0: cat = 'NO-ERROR'
        else: cat = 'SINGLE-PATH-A' if seat in A_KEY else 'SINGLE-PATH-B' if seat in B_KEY else 'DOUBLE-PATH'
        ok = passes.get(pid)
        print(f'plant {pid:2d} {scope:6s} seat {seat:3d} agree {24 - len(miss)} miss {miss} passA {int(pA)} passB {int(pB)} {cat:14s} recovered {ok}')
        out.append((pid, seat, cat, ok, miss, pA, pB))
    one = [o for o in out if o[1] >= 0]
    cons = all(o[4] == [o[1]] for o in one) and all(o[4] == [] for o in out if o[1] < 0)
    print(f'G-CONS1 (planted config misses exactly its bad seat, none on clean plants): {"PASS" if cons else "FAIL"}')
    print(f'one-error plants: {len(one)}; on bridge/pendant edges: 0/{len(one)} (structure has none)')
    for lab, sel in (('SINGLE-PATH', lambda o: o[2].startswith('SINGLE')), ('DOUBLE-PATH', lambda o: o[2] == 'DOUBLE-PATH')):
        s = [o for o in one if sel(o)]; k = sum(1 for o in s if o[3])
        lo, hi = wilson(k, len(s)); print(f'  {lab}: {len(s)} plants, recovered {k}/{len(s)} Wilson95 {lo:.3f}-{hi:.3f}')
    nsp = sum(1 for o in one if o[2].startswith('SINGLE')); d = poisbin([8 / 24] * len(one))
    print(f'  SINGLE-PATH observed {nsp}/{len(one)} vs expected {len(one) * 8 / 24:.2f} under a uniform seat draw (8/24); two-sided exact binomial p {two_sided(d, nsp):.4f}')
    return one

def part2(F232, SUM):
    print('\n== PART 2: case 218 (cycle 232) gate P, kb227/kb229 model Q, periodic key, class r = S[POS[j]] mod p (carved index) ==')
    print('Multigraph H_p: ground node g (alphabets + carved text fixed) + one node per residue class; crib seat j = edge g--r_j.')
    print('Seat category by m = crib seats in its class: PENDANT (m=1: pendant edge = bridge; error invisible, class decrypts wrong),')
    print('TIE (m=2: 2-cycle; error detected, not locatable -> class "?"), MAJ (m>=3: on a >=3-cycle; error outvoted).')
    banks = {s: [list(struct.unpack('<97h', b[i:i + 194])) for i in range(0, len(b), 194)] for s, b in
             (('bank', open(os.environ.get('VC236_W', '/workspace/vc236/w') + '/bank.bin', 'rb').read()),
              ('all', open(os.environ.get('VC236_W', '/workspace/vc236/w') + '/all.bin', 'rb').read()))}
    rec_ = {}
    for l in open(SUM):
        m = re.match(r'\s*plant\s+(\d+) bad=\s*(-?\d+) rec=(\d) H_p=\[([\d, ]*)\] nq=(\d+) nc=(-?[\d.]+) Nref=\d+ bar=(-?[\d.]+) pass=(\d)', l)
        if m: rec_[int(m.group(1))] = dict(bad=int(m.group(2)), rec=int(m.group(3)), Hp=[int(v) for v in m.group(4).split(',') if v.strip()],
                                          nq=int(m.group(5)), nc=float(m.group(6)), bar=float(m.group(7)), ok=int(m.group(8)))
    hdr = None; out = []; cons_fail = []
    for l in open(F232):
        t = l.rstrip('\n').split('\t')
        if hdr is None: hdr = t; continue
        d = dict(zip(hdr, t)); pid = int(d['pid']); p = int(d['p']); bad = int(d['bad'])
        P = banks[d['scope']][int(d['row'])]; inv = [0] * N
        for i, v in enumerate(P): inv[v] = i
        S = P if int(d['dir']) == 0 else inv
        cls = [S[POS[j]] % p for j in range(24)]; mult = Counter(cls)
        cats = ['PENDANT' if mult[c] == 1 else 'TIE' if mult[c] == 2 else 'MAJ' for c in cls]
        share = {c: sum(1 for x in cats if x == c) / 24 for c in ('PENDANT', 'TIE', 'MAJ')}
        cat = cats[bad] if bad >= 0 else 'NO-ERROR'
        # G-CONS2: her predicted decrypt must show the category's signature on the bad seat's class (non-crib positions)
        if bad >= 0:
            r = cls[bad]; posr = [i for i in range(N) if S[i] % p == r and i not in POS]
            dp, pt = d['dec_pred'], d['pt']
            if cat == 'TIE': okc = all(dp[i] == '?' for i in posr)
            elif cat == 'MAJ': okc = all(dp[i] == pt[i] for i in posr)
            else: okc = all(dp[i] != '?' for i in posr) and sum(dp[i] != pt[i] for i in posr) >= max(1, len(posr) - 2)
            if not okc: cons_fail.append(pid)
        rr = rec_.get(pid, {})
        hcat = ''
        if bad >= 0 and rr.get('Hp'):
            hp = rr['Hp'][0]; hc = Counter(S[POS[j]] % hp for j in range(24)); m = hc[S[POS[bad]] % hp]
            hcat = f' | at H_p {hp}: m={m}'
        print(f'plant {pid:2d} {d["scope"]:4s} p {p:2d} bad {bad:3d} m {mult[cls[bad]] if bad >= 0 else "-"} {cat:8s} '
              f'seat-shares P/T/M {share["PENDANT"]:.3f}/{share["TIE"]:.3f}/{share["MAJ"]:.3f} rec {rr.get("rec")} nc {rr.get("nc")} bar {rr.get("bar")} pass {rr.get("ok")}{hcat}')
        out.append(dict(pid=pid, bad=bad, cat=cat, share=share, rec=rr.get('rec'), ok=rr.get('ok')))
    one = [o for o in out if o['bad'] >= 0]
    print(f'G-CONS2 (category signature visible in her predicted decrypt): {"PASS" if not cons_fail else "FAIL " + str(cons_fail)}')
    for cat in ('PENDANT', 'TIE', 'MAJ'):
        s = [o for o in one if o['cat'] == cat]; k = sum(1 for o in s if o['ok']); kr = sum(1 for o in s if o['rec'])
        lo, hi = wilson(k, len(s)); dist = poisbin([o['share'][cat] for o in one])
        print(f'  {cat:8s}: {len(s)}/{len(one)} plants (expected {sum(o["share"][cat] for o in one):.2f}, two-sided Poisson-binomial p {two_sided(dist, len(s)):.4f}); '
              f'found {kr}/{len(s)}, gate pass {k}/{len(s)} Wilson95 {lo:.3f}-{hi:.3f}')
    bp = [o for o in one if o['cat'] == 'PENDANT']; off = [o for o in one if o['cat'] != 'PENDANT']
    for lab, s in (('ON bridge/pendant', bp), ('OFF bridge/pendant', off)):
        k = sum(1 for o in s if o['ok']); lo, hi = wilson(k, len(s)); print(f'  {lab}: gate pass {k}/{len(s)} Wilson95 {lo:.3f}-{hi:.3f}')
    return one

def part3():
    print('\n== PART 3: case 205 / cycle 219 one-error recount (v1e.c): NO plants exist -> plant counts NOT TESTABLE ==')
    print('Census only (model 0 = plaintext index, class = seat mod p; model 1 depends on the transposition, not censused):')
    for p in range(1, 23):
        mult = Counter(POS[j] % p for j in range(24)); c = Counter('P' if mult[POS[j] % p] == 1 else 'T' if mult[POS[j] % p] == 2 else 'M' for j in range(24))
        print(f'  p {p:2d}: pendant seats {c["P"]:2d}/24  tie seats {c["T"]:2d}/24  maj seats {c["M"]:2d}/24')

def part4(root):
    print('\n== PART 4: floor p of the two-batch gate (C095 / C097 / C098; tools/c093_edit_graph.py pt(): two-sided predictive t, df n-1) ==')
    from scipy import stats
    import numpy as np
    n = 20; print(f'predictive-t p is continuous in x: no positive attainable floor (smallest positive double {np.nextafter(0, 1):.3g}; '
                  f'stats.t.sf(1e6, 19)*2 = {2 * stats.t.sf(1e6, 19):.3g}).')
    print(f'rank-scale counterpart (descriptive "above all n"): floor 1/(n+1) = {1 / 21:.4f} per batch of 20; Holm x2 -> {2 / 21:.4f}, x4 -> {4 / 21:.4f}; pooled 40 -> {1 / 41:.4f}')
    print(f'count gates per batch (n 20): G1 <= 1/20 false calls -> Wilson95 upper {wilson(1, 20)[1]:.3f} (0/20: {wilson(0, 20)[1]:.3f}); G2 >= 19/20 -> Wilson95 lower {wilson(19, 20)[0]:.3f}')
    for c in ('C095', 'C097', 'C098'):
        fn = os.path.join(root, 'analysis', f'{c}_results.json')
        if not os.path.exists(fn): print(f'{c}: results file missing'); continue
        J = json.load(open(fn)); found = []
        def walk(o, path):
            if isinstance(o, dict):
                for pk in ('p', 'p_diff'):
                    if pk in o and isinstance(o[pk], (int, float)): found.append((path + ':' + pk, o[pk], o.get('p_holm'), o.get('above_all'), o.get('below_all')))
                for k, v in o.items(): walk(v, path + '/' + str(k))
            elif isinstance(o, list):
                for i, v in enumerate(o): walk(v, path + f'[{i}]')
        walk(J, c)
        ps = [f[1] for f in found]
        print(f'{c}: {len(found)} reported test p values; min raw p {min(ps) if ps else "none"}; any p == 0: {any(v == 0 for v in ps)}')
        for f in found: print(f'   {f[0]}: p {f[1]:.3g} holm {f[2] if f[2] is None else round(f[2], 5)} above_all {f[3]} below_all {f[4]}')

if __name__ == '__main__':
    W, F232, SUM, ROOT = sys.argv[1:5]; os.environ['VC236_W'] = W
    part1(W); part2(F232, SUM); part3(); part4(ROOT)
