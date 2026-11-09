"""RR006 - calibrated isolation for copies with ONE insertion or deletion (a dropped or extra sign).
Statistic Mg(x, y) = most matched head signs in a run of exact matches that may contain at most one gap of one sign
(one sign skipped in x, or one in y), counted as matched signs. Null: RR001's order-1 Markov surrogate of y, R = 999,
Holm over the same 25 cross-object pairs. Gates: Hr-Qr and Hr-Pr p <= 0.002; reversed-line y: 0 Holm detections,
<= 3 unadjusted hits. Power: plant x[i:i+L] into y with one interior sign dropped (half the plants) or one random sign
of y inserted (other half), L = 5..16, 100 plants; lg* = smallest L with power >= 0.80 at 0.002.
Verdicts: DETECTED / NOT DETECTED (gates pass, lg* <= 12) / NOT TESTABLE. Heads normalised as in RR005. Seed 6006.
Usage: python3 rr006_indel_isolation.py corpus.json out.json [--seed S]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, random, itertools, time
import numpy as np
sys.path.insert(0, '.')
import rr005_fuzzy_isolation as F   # installs head_norm into rr001_isolation
import rr001_isolation as R1
SIDES = R1.SIDES; POS = R1.POS; ELLS = list(range(5, 17)); R = 999; P = 100
enc = F.enc; pval = F.pval

def mg_batch(x, Y):
    """x (n,), Y (K, m). E0 = exact run ending at (i,j); E1 = run ending at (i,j) with one 1-sign gap.
    E1[i,j] = match ? max(E1[i-1,j-1], E0[i-1,j-2], E0[i-2,j-1]) + 1 : 0 (gap terms only when that cell matched)."""
    K, m = Y.shape
    z = lambda: np.zeros((K, m + 2), np.int32)
    E0p, E1p, E0pp = z(), z(), z(); best = np.zeros(K, np.int32)
    for xi in x:
        match = (Y == xi)
        d0 = E0p[:, 1:m + 1]; d1 = E1p[:, 1:m + 1]; gy = E0p[:, 0:m]; gx = E0pp[:, 1:m + 1]
        g = np.maximum(np.where(gy > 0, gy, 0), np.where(gx > 0, gx, 0))
        n0 = np.where(match, d0 + 1, 0)
        n1 = np.where(match, np.maximum(np.where(d1 > 0, d1, 0), g) + 1, 0)
        n1 = np.where(match & (n1 == 1), 0, n1)  # a fresh start is not a gapped run; exact runs are in n0
        E0pp = E0p; E0p = z(); E1p = z(); E0p[:, 2:] = n0; E1p[:, 2:] = n1
        best = np.maximum(best, np.maximum(n0.max(axis=1), n1.max(axis=1)))
    return best

def main(cp, op, seed=6006):
    t0 = time.time(); rng = random.Random(seed)
    corpus = json.load(open(cp)); seqs = {s: R1.side_seq(corpus, s) for s in set(SIDES) | {a for p in POS for a in p}}
    table = {}; sur = lambda ys, k: F.surrogates(ys, k, rng, table)
    pairs = [(a, b) for a, b in itertools.combinations(SIDES, 2) if a[0] != b[0]]; bonf = 0.05 / len(pairs)
    pos = []
    for a, b in POS:
        x = enc(seqs[a], table, -1); nd = mg_batch(x, sur(seqs[b], R)); M = int(mg_batch(x, enc(seqs[b], table, -2)[None, :])[0])
        pos.append(dict(pair=f'{a}-{b}', Mg=M, null_max=int(nd.max()), p=pval(M, nd), passes=pval(M, nd) <= bonf))
    print('POSITIVE', pos, flush=True)
    rev_p = []; per = {}
    for a, b in pairs:
        x = enc(seqs[a], table, -1); ys = seqs[b]; y = enc(ys, table, -2)
        yr = []
        for l in sorted(k for k in corpus if k[:2] == b): yr += [R1.head(u, ('r', l, i)) for i, u in enumerate(corpus[l])][::-1]
        ndr = mg_batch(x, sur(yr, R)); rev_p.append(pval(int(mg_batch(x, enc(yr, table, -2)[None, :])[0]), ndr))
        nd = mg_batch(x, sur(ys, R)); ysym = y[y >= 0]; power = {}
        for L in ELLS:
            rows = []
            for r in range(P):
                i = rng.randrange(len(x) - L + 1); seg = list(np.where(x[i:i + L] == -1, -2, x[i:i + L])); q = rng.randrange(1, L - 1)
                if r % 2 == 0: del seg[q]
                else: seg.insert(q, int(ysym[rng.randrange(len(ysym))]))
                j = rng.randrange(len(y) - len(seg) + 1); yp = y.copy(); yp[j:j + len(seg)] = seg; rows.append(yp)
            st = mg_batch(x, np.stack(rows)); power[L] = float(np.mean([pval(int(s), nd) <= bonf for s in st]))
        lstar = next((L for L in ELLS if power[L] >= 0.80), None)
        per[(a, b)] = dict(nd=nd, power=power, lstar=lstar)
        print(a, b, 'lg*', lstar, f'{time.time()-t0:.0f}s', flush=True)
    rr = R1.holm(rev_p); unadj = sum(p <= 0.05 for p in rev_p)
    gates = dict(positive_controls_pass=all(p['passes'] for p in pos), reversed_holm_detections=sum(rr),
                 reversed_unadjusted_hits=unadj, gate_reversed_ok=(sum(rr) == 0 and unadj <= 3))
    print('GATES', gates, flush=True)
    res = []; ps = []
    for a, b in pairs:
        d = per[(a, b)]; M = int(mg_batch(enc(seqs[a], table, -1), enc(seqs[b], table, -2)[None, :])[0]); p = pval(M, d['nd']); ps.append(p)
        res.append(dict(pair=f'{a}-{b}', Mg=M, null_median=int(np.median(d['nd'])), null_max=int(d['nd'].max()), p=p, lgstar=d['lstar'], power=d['power']))
    rej = R1.holm(ps); ok = gates['positive_controls_pass'] and gates['gate_reversed_ok']
    for r, k in zip(res, rej):
        r['verdict'] = ('NOT TESTABLE (instrument gate)' if not ok else 'DETECTED' if k else
                        f'NOT DETECTED (one-indel copy of >= {r["lgstar"]} signs would be seen)' if r['lgstar'] and r['lgstar'] <= 12 else 'NOT TESTABLE (power)')
    json.dump(dict(seed=seed, R=R, plants=P, bonferroni_alpha=bonf, positive=pos, gates=gates, reversed_p=rev_p, results=res,
                   runtime_s=round(time.time() - t0, 1)), open(op, 'w'), indent=1)
    for r in res: print(r['pair'], r['Mg'], r['null_max'], round(r['p'], 4), r['lgstar'], r['verdict'])

if __name__ == '__main__':
    a = sys.argv; main(a[1], a[2], int(a[a.index('--seed') + 1]) if '--seed' in a else 6006)
