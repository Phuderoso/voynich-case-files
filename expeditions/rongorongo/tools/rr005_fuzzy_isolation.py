"""RR005 - calibrated isolation for FUZZY copies (one substitution allowed).
Statistic M1(x, y) = longest aligned run (same offset, no shifts) between side x and side y with at most ONE mismatched
position; illegible units never match (they can be the one mismatch). Null: order-1 Markov surrogate of side y
(RR001's generator, illegible positions kept), R = 999. Holm over the same 25 cross-object pairs as RR001.
Gates as RR001: positive controls Hr-Qr, Hr-Pr (must reach p <= 0.05/25); reversed-side negative control (0 Holm
detections, <= 3 unadjusted hits of 25). Power: plant x[i:i+L] into y with one interior position replaced by a random
sign of y, L in 5..16, 100 plants; l1* = smallest L with power >= 0.80 at 0.05/25. Verdicts: DETECTED (Holm),
NOT DETECTED (gates pass and l1* <= 12: a one-substitution copy of >= l1* signs would be seen), NOT TESTABLE otherwise.
Seed 5005. Usage: python3 rr005_fuzzy_isolation.py corpus.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, random, itertools, time
import numpy as np
sys.path.insert(0, '.')
import rr001_isolation as R1, re
def head_norm(u, k):
    """RR001 head with code normalisation (RR004): the leading digit run of the first component is padded to three
    digits ('4.120a' -> '004'). Units with '!' (illegible) or ')' (marker) stay unique non-matching, as in RR001."""
    if ('!' in u and not R1.BANG_AS_SIGN) or ')' in u: return ('ILL', k)
    m = re.match(r'(\d{1,3})', re.split(r"[.:;']", u.replace('!', ''))[0])
    if not m or int(m.group(1)) == 0: return ('ILL', k)
    return m.group(1).zfill(3)
R1.head = head_norm
SIDES = R1.SIDES; POS = R1.POS; ELLS = list(range(5, 17)); R = 999; P = 100

def enc(seq, table, ill):
    return np.array([ill if isinstance(s, tuple) else table.setdefault(s, len(table)) for s in seq], dtype=np.int32)

def m1_batch(x, Y):
    """x: (n,), Y: (K, m). Longest diagonal run with <= 1 mismatch, for every row of Y. DP over rows of x."""
    K, m = Y.shape
    E0 = np.zeros((K, m + 1), np.int32); E1 = np.zeros((K, m + 1), np.int32); best = np.zeros(K, np.int32)
    for xi in x:
        match = (Y == xi)
        n0 = np.where(match, E0[:, :-1] + 1, 0)
        n1 = np.where(match, E1[:, :-1] + 1, E0[:, :-1] + 1)
        E0[:, 1:] = n0; E1[:, 1:] = n1; E0[:, 0] = 0; E1[:, 0] = 0
        best = np.maximum(best, n1.max(axis=1))
    return best

def surrogates(y_seq, k, rng, table):
    return np.stack([enc(R1.markov1(y_seq, rng), table, -2) for _ in range(k)])

def pval(M, nd): return (1 + int((nd >= M).sum())) / (len(nd) + 1)

def main(cp, op):
    t0 = time.time(); rng = random.Random(5005); nrng = np.random.default_rng(5005)
    corpus = json.load(open(cp)); seqs = {s: R1.side_seq(corpus, s) for s in set(SIDES) | {a for p in POS for a in p}}
    table = {}
    pairs = [(a, b) for a, b in itertools.combinations(SIDES, 2) if a[0] != b[0]]; bonf = 0.05 / len(pairs)
    pos = []
    for a, b in POS:
        x = enc(seqs[a], table, -1); nd = m1_batch(x, surrogates(seqs[b], R, rng, table))
        M = int(m1_batch(x, enc(seqs[b], table, -2)[None, :])[0])
        pos.append(dict(pair=f'{a}-{b}', M1=M, null_max=int(nd.max()), p=pval(M, nd), passes=pval(M, nd) <= bonf))
    print('POSITIVE', pos, f'{time.time()-t0:.0f}s', flush=True)
    rev_p = []; per = {}
    for a, b in pairs:
        x = enc(seqs[a], table, -1); ys = seqs[b]; y = enc(ys, table, -2)
        lines = sorted(k for k in corpus if k[:2] == b); yrev_s = []
        for l in lines: yrev_s += [R1.head(u, ('r', l, i)) for i, u in enumerate(corpus[l])][::-1]
        ndr = m1_batch(x, surrogates(yrev_s, R, rng, table)); Mr = int(m1_batch(x, enc(yrev_s, table, -2)[None, :])[0])
        rev_p.append(pval(Mr, ndr))
        nd = m1_batch(x, surrogates(ys, R, rng, table))
        thr = next((v for v in range(0, 400) if pval(v, nd) <= bonf), None)
        power = {}
        ysym = y[y >= 0]
        for L in ELLS:
            if L > min(len(x), len(y)): power[L] = None; continue
            Yp = np.tile(y, (P, 1))
            for r in range(P):
                i = rng.randrange(len(x) - L + 1); j = rng.randrange(len(y) - L + 1)
                seg = x[i:i + L].copy(); q = rng.randrange(1, L - 1); seg[q] = int(ysym[rng.randrange(len(ysym))])
                seg = np.where(seg == -1, -2, seg)
                Yp[r, j:j + L] = seg
            st = m1_batch(x, Yp); power[L] = float(np.mean([pval(int(s), nd) <= bonf for s in st]))
        lstar = next((L for L in ELLS if power[L] is not None and power[L] >= 0.80), None)
        per[(a, b)] = dict(nd=nd, power=power, lstar=lstar, thr=thr, Mrev=Mr)
        print(a, b, len(x), len(y), 'l1*', lstar, 'thr', thr, f'{time.time()-t0:.0f}s', flush=True)
    rev_rej = R1.holm(rev_p); unadj = sum(p <= 0.05 for p in rev_p)
    gates = dict(positive_controls_pass=all(p['passes'] for p in pos), reversed_holm_detections=sum(rev_rej),
                 reversed_unadjusted_hits=unadj, gate_reversed_ok=(sum(rev_rej) == 0 and unadj <= 3))
    print('GATES', gates, flush=True)
    res = []; ps = []
    for a, b in pairs:
        d = per[(a, b)]; M = int(m1_batch(enc(seqs[a], table, -1), enc(seqs[b], table, -2)[None, :])[0])
        p = pval(M, d['nd']); ps.append(p)
        res.append(dict(pair=f'{a}-{b}', M1=M, null_median=int(np.median(d['nd'])), null_max=int(d['nd'].max()), p=p,
                        bonf_threshold_M1=d['thr'], l1star=d['lstar'], power=d['power'], reversed_M1=d['Mrev']))
    rej = R1.holm(ps); ok = gates['positive_controls_pass'] and gates['gate_reversed_ok']
    for r, k in zip(res, rej):
        if not ok: r['verdict'] = 'NOT TESTABLE (instrument gate)'
        elif k: r['verdict'] = 'DETECTED'
        elif r['l1star'] is not None and r['l1star'] <= 12: r['verdict'] = f'NOT DETECTED (one-substitution copy of >= {r["l1star"]} signs would be seen)'
        else: r['verdict'] = 'NOT TESTABLE (power)'
    out = dict(seed=5005, R=R, plants=P, pairs=len(pairs), bonferroni_alpha=bonf, positive=pos, gates=gates,
               reversed_p=rev_p, results=res, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open(op, 'w'), indent=1)
    for r in res: print(r['pair'], r['M1'], r['null_max'], round(r['p'], 4), r['l1star'], r['verdict'])

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
