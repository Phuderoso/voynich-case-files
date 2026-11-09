"""RR013 audit J - settle audit I's edge case: RR008 pair Ab-Cb, power of the shared-trigram test (RR007 statistic,
RR008 H/P/Q-learned equivalences, Markov-1 null on mapped Cb, planted 4-sign excerpts of Ab, alpha 0.05/25) at
k = 1..6 with 400 plants per k. Because the integer statistic's rejection threshold depends on the null draw, power is
estimated (a) against 5 independent R 999 nulls (seeds 13008-13012, the variation RR008/audit I were exposed to) and
(b) against one R 9999 null (seed 13013), which pins the threshold; (b) decides k*. Wilson 95% intervals reported.
Usage: python3 rr013_auditJ_abcb.py corpus.json rr008_equivalences.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, random, math; sys.path.insert(0, '.')
import rr005_fuzzy_isolation  # installs head_norm
import rr001_isolation as R1
cmap = json.load(open(sys.argv[2]))['map']; _h = R1.head
def head_mapped(u, k):
    h = _h(u, k); return h if isinstance(h, tuple) else cmap.get(h, h)
R1.head = head_mapped
import rr007_shared_trigrams as T
A, B = 'Ab', 'Cb'; KS = range(1, 7); PL = 400; ALPHA = 0.05 / 25
def wilson(h, n, z=1.96):
    p = h / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; w = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - w, 3), round(c + w, 3)]
def power_vs(null, x, gx, y, rng):
    res = {}
    for k in KS:
        hit = 0
        for _ in range(PL):
            yp = list(y); slots = rng.sample(range(len(y) // 4), k)
            for s in slots:
                i = rng.randrange(len(x) - 3); yp[4 * s:4 * s + 4] = x[i:i + 4]
            hit += T.pval(T.T(gx, yp), null) <= ALPHA
        res[k] = dict(power=hit / PL, ci95=wilson(hit, PL))
    return res
def thr(null):  # smallest integer t with p(t) <= ALPHA
    for t in range(0, max(null) + 2):
        if T.pval(t, null) <= ALPHA: return t
def main(cp, op):
    corpus = json.load(open(cp)); x = R1.side_seq(corpus, A); y = R1.side_seq(corpus, B); gx = T.grams(x)
    out = dict(pair=f'{A}-{B}', plants=PL, alpha=ALPHA, observed_T=T.T(gx, y), runs={})
    for sd in list(range(13008, 13013)) + [13013]:
        rng = random.Random(sd); Rn = 9999 if sd == 13013 else 999
        null = [T.T(gx, R1.markov1(y, rng)) for _ in range(Rn)]
        pw = power_vs(null, x, gx, y, rng)
        ks = next((k for k in KS if pw[k]['power'] >= 0.80), None)
        out['runs'][sd] = dict(R=Rn, null_max=max(null), reject_threshold_T=thr(null), power=pw, kstar=ks)
        print(sd, Rn, 'thr', thr(null), 'k*', ks, {k: pw[k]['power'] for k in KS}, flush=True)
    out['kstar_reference_R9999'] = out['runs'][13013]['kstar']
    json.dump(out, open(op, 'w'), indent=1)
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[3])
