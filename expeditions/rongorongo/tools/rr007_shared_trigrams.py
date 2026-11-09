"""RR007 - shared short formulae: how many distinct head-sign trigrams do two objects share, beyond an order-1 Markov
text? RR001/RR005/RR006 test for one LONG shared run; catalogued parallels (e.g. Horley's lists) are many SHORT ones.
Statistic T(x, y) = number of distinct 3-grams of head signs (no illegible unit inside) present in both sides.
Null: RR001's order-1 Markov surrogate of y (keeps y's sign frequencies and bigrams, so a DETECTED result means shared
structure beyond bigrams: formulae, lists or copying, not distinguished here). R = 999, Holm over the same 25 pairs.
Gates: Hr-Qr, Hr-Pr p <= 0.002; reversed-line y: 0 Holm detections and <= 3 unadjusted hits of 25.
Power: plant k excerpts of 4 consecutive head signs of x into y at random non-overlapping places, k = 1..12, 100
plants; k* = smallest k with power >= 0.80 at 0.002. Verdicts: DETECTED / NOT DETECTED (gates pass, k* <= 8) / NOT
TESTABLE. Heads normalised as in RR005. Seed 7007.
Usage: python3 rr007_shared_trigrams.py corpus.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, random, itertools, time
sys.path.insert(0, '.')
import rr005_fuzzy_isolation  # installs head_norm
import rr001_isolation as R1
SIDES = R1.SIDES; POS = R1.POS; KS = list(range(1, 13)); R = 999; P = 100; N = 3

def grams(s):
    return {tuple(s[i:i + N]) for i in range(len(s) - N + 1) if not any(isinstance(t, tuple) for t in s[i:i + N])}

def T(gx, y): return len(gx & grams(y))
def pval(M, nd): return (1 + sum(v >= M for v in nd)) / (len(nd) + 1)

def main(cp, op):
    t0 = time.time(); rng = random.Random(7007)
    corpus = json.load(open(cp)); seqs = {s: R1.side_seq(corpus, s) for s in set(SIDES) | {a for p in POS for a in p}}
    pairs = [(a, b) for a, b in itertools.combinations(SIDES, 2) if a[0] != b[0]]; bonf = 0.05 / len(pairs)
    nullf = lambda gx, y: [T(gx, R1.markov1(y, rng)) for _ in range(R)]
    pos = []
    for a, b in POS:
        gx = grams(seqs[a]); nd = nullf(gx, seqs[b]); M = T(gx, seqs[b])
        pos.append(dict(pair=f'{a}-{b}', T=M, null_max=max(nd), p=pval(M, nd), passes=pval(M, nd) <= bonf))
    print('POSITIVE', pos, flush=True)
    rev_p = []; res = []; ps = []
    for a, b in pairs:
        x, y = seqs[a], seqs[b]; gx = grams(x)
        yr = []
        for l in sorted(k for k in corpus if k[:2] == b): yr += [R1.head(u, ('r', l, i)) for i, u in enumerate(corpus[l])][::-1]
        ndr = nullf(gx, yr); rev_p.append(pval(T(gx, yr), ndr))
        nd = nullf(gx, y); power = {}
        for k in KS:
            hit = 0
            for _ in range(P):
                yp = list(y); slots = rng.sample(range(len(y) // 4), k)
                for s in slots:
                    i = rng.randrange(len(x) - 3); yp[4 * s:4 * s + 4] = x[i:i + 4]
                hit += pval(T(gx, yp), nd) <= bonf
            power[k] = hit / P
        kstar = next((k for k in KS if power[k] >= 0.80), None)
        M = T(gx, y); p = pval(M, nd); ps.append(p)
        res.append(dict(pair=f'{a}-{b}', T=M, null_mean=round(sum(nd) / R, 2), null_max=max(nd), p=p, kstar=kstar, power=power,
                        shared=sorted(' '.join(g) for g in gx & grams(y))))
        print(a, b, 'T', M, 'null max', max(nd), 'p', p, 'k*', kstar, f'{time.time()-t0:.0f}s', flush=True)
    rr = R1.holm(rev_p); unadj = sum(q <= 0.05 for q in rev_p)
    gates = dict(positive_controls_pass=all(q['passes'] for q in pos), reversed_holm_detections=sum(rr),
                 reversed_unadjusted_hits=unadj, gate_reversed_ok=(sum(rr) == 0 and unadj <= 3))
    print('GATES', gates, flush=True)
    rej = R1.holm(ps); ok = gates['positive_controls_pass'] and gates['gate_reversed_ok']
    for r, k in zip(res, rej):
        r['verdict'] = ('NOT TESTABLE (instrument gate)' if not ok else 'DETECTED' if k else
                        f'NOT DETECTED ({r["kstar"]} shared 4-sign excerpts would be seen)' if r['kstar'] and r['kstar'] <= 8 else 'NOT TESTABLE (power)')
    json.dump(dict(seed=7007, R=R, plants=P, n=N, bonferroni_alpha=bonf, positive=pos, gates=gates, reversed_p=rev_p,
                   results=res, runtime_s=round(time.time() - t0, 1)), open(op, 'w'), indent=1)
    for r in res: print(r['pair'], r['T'], r['null_max'], round(r['p'], 4), r['kstar'], r['verdict'])

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
