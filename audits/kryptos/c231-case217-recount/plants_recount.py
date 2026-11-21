#!/usr/bin/env python3
"""Gate P recount for cycle 231 plants (plants231.tsv, her input). Recovery rule (frozen): a plant is RECOVERED iff its own bsk230 output has a line that is
(strict) exactly the plant's (row, dir, X, Y, form) with w<=size (type w) or pop<=size (type d); or (loose) a line whose decrypt profile (house rule, with the
plant's own criterion W or D) equals the true line's profile. Also independent check: the true key from ct is rebuilt and must satisfy typ/size.
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recount231 as R
out = []; nstrict = nloose = 0
for l in open('src/plants231.tsv'):
    id, fam, q, d, xi, yi, form, typ, size, ct, pt = l.rstrip('\n').split('\t'); q, d, xi, yi, form, size = int(q), int(d), int(xi), int(yi), int(form), int(size)
    sc = fam; off = int(open(f'out/plants/{id}.off').read()) if fam != 'direct' else 0
    S, T = R.parse(f'out/plants/{id}.txt'); S = [(s[0] + off if fam != 'direct' else s[0],) + s[1:] for s in S]
    A = R.alpha if sc == 'direct' else R.themed; cc = R.layer(sc, q, d, ct); Ai, Bi = R.inv(A[xi]), R.inv(A[yi])
    ks = ''.join(chr(65 + R.kof(form, Bi[cc[p]], Ai[ord(pt[p]) - 65])) for p in R.POS); kv = [ord(c) - 65 for c in ks]
    w = R.minarc(kv)[0]; pop = len(set(kv)); ok = (w <= size) if typ == 'w' else (pop <= size)
    true = (q, d, xi, yi, form, w, pop, ks); crit = 'W' if typ == 'w' else 'D'
    strict = any((s[0], s[1], s[2], s[3], s[4]) == (q, d, xi, yi, form) and ((s[5] <= size) if typ == 'w' else (s[6] <= size)) for s in S)
    tp = R.profile(sc, true, ct, crit); loose = any(R.profile(sc, s, ct, crit) == tp for s in S if ((s[5] <= size) if typ == 'w' else (s[6] <= size)))
    nstrict += strict; nloose += loose
    out.append(f'{id} {fam} typ {typ} size {size} true w {w} pop {pop} key-consistent {ok}; survivors {len(S)}; recovered strict {strict} loose {loose}')
lo, hi = R.wilson(nstrict, 20)
out.append(f'PLANTS strict {nstrict}/20 (Wilson95 {lo:.3f}-{hi:.3f}); loose {nloose}/20')
open('res/plants231_recount.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
