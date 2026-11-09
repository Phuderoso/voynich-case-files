"""RR001 - calibrated isolation of the near-isolated rongorongo texts.
Longest common run of head signs between two sides of different objects, against an order-1 Markov surrogate
of the second side (R = 999), Holm over 25 pairs, planted-copy power curve, reversed-side negative control,
Hr-Qr / Hr-Pr positive controls. Seed 3001.
Usage: python3 rr001_isolation.py corpus.json out.json [--R 999] [--plants 100]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, random, itertools, time
SIDES = ['Aa', 'Ab', 'Br', 'Bv', 'Ca', 'Cb', 'Er', 'Ia']
POS = [('Hr', 'Qr'), ('Hr', 'Pr')]
ELLS = list(range(4, 16))

def head(u, k):
    if '!' in u: return ('ILL', k)          # illegible: unique, never matches
    m = re.match(r'(\d{3})', re.split(r"[.:;']", u)[0])
    if not m or m.group(1) == '000': return ('ILL', k)
    return m.group(1)

def side_seq(corpus, s):
    lines = sorted(k for k in corpus if k[:2] == s)
    out = []; c = 0
    for l in lines:
        for u in corpus[l]:
            out.append(head(u, (l, c))); c += 1
    return out

def lcs_len(x, y):
    """Longest common contiguous run (exact), by binary search on k with k-gram sets."""
    def has(k):
        if k == 0: return True
        if k > min(len(x), len(y)): return False
        S = {tuple(x[i:i + k]) for i in range(len(x) - k + 1)}
        return any(tuple(y[j:j + k]) in S for j in range(len(y) - k + 1))
    lo, hi = 0, 1
    while has(hi): lo, hi = hi, hi * 2
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if has(mid): lo = mid
        else: hi = mid
    return lo

def markov1(y, rng):
    sym = [s for s in y if not (isinstance(s, tuple))]
    if not sym: return list(y)
    nxt = {}
    for a, b in zip(sym, sym[1:]): nxt.setdefault(a, []).append(b)
    out = [sym[0]]; ill = 0
    for t in range(1, len(y)):
        if isinstance(y[t], tuple):               # keep illegible positions where they are
            out.append(('ILLs', ill)); ill += 1; continue
        prev = out[-1] if not isinstance(out[-1], tuple) else rng.choice(sym)
        choices = nxt.get(prev)
        out.append(rng.choice(choices) if choices else rng.choice(sym))
    return out

def null_dist(x, y, R, rng):
    return [lcs_len(x, markov1(y, rng)) for _ in range(R)]

def pval(M, nd): return (1 + sum(v >= M for v in nd)) / (len(nd) + 1)

def holm(ps, a=0.05):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); rej = [False] * len(ps); m = len(ps)
    for r, i in enumerate(order):
        if ps[i] <= a / (m - r): rej[i] = True
        else: break
    return rej

def main(cp, outp, R=999, P=100):
    t0 = time.time(); rng = random.Random(3001)
    corpus = json.load(open(cp)); seq = {s: side_seq(corpus, s) for s in set(SIDES) | {a for p in POS for a in p}}
    pairs = [(a, b) for a, b in itertools.combinations(SIDES, 2) if a[0] != b[0]]
    m = len(pairs); bonf = 0.05 / m
    res = []
    # gates first: positive controls, reversed-side negative control, power curve; then observed statistics
    pos = []
    for a, b in POS:
        nd = null_dist(seq[a], seq[b], R, rng); M = lcs_len(seq[a], seq[b])
        pos.append(dict(pair=f'{a}-{b}', M=M, null_max=max(nd), p=pval(M, nd), passes=pval(M, nd) <= bonf))
    print('POSITIVE CONTROLS', pos, flush=True)
    rev_p = []; per = {}
    for a, b in pairs:
        x, y = seq[a], seq[b]
        lines = sorted(k for k in corpus if k[:2] == b)
        yrev = []; c = 0
        for l in lines:
            seg = [head(u, ('r', l, i)) for i, u in enumerate(corpus[l])]; yrev += seg[::-1]
        ndr = null_dist(x, yrev, R, rng); Mr = lcs_len(x, yrev); rev_p.append(pval(Mr, ndr))
        nd = null_dist(x, y, R, rng)
        thr = min(v for v in range(0, 200) if pval(v, nd) <= bonf) if any(pval(v, nd) <= bonf for v in range(200)) else None
        power = {}
        for L in ELLS:
            hit = 0
            for _ in range(P):
                i = rng.randrange(len(x) - L + 1); j = rng.randrange(len(y) - L + 1)
                yp = y[:j] + x[i:i + L] + y[j + L:]
                hit += pval(lcs_len(x, yp), nd) <= bonf
            power[L] = hit / P
        lstar = next((L for L in ELLS if power[L] >= 0.80), None)
        per[(a, b)] = dict(nd=nd, power=power, lstar=lstar, thr=thr, Mrev=Mr)
        print(a, b, 'lstar', lstar, 'thr', thr, f'{time.time()-t0:.0f}s', flush=True)
    rev_rej = holm(rev_p); fpr_unadj = sum(p <= 0.05 for p in rev_p)
    gates = dict(positive_controls_pass=all(p['passes'] for p in pos), reversed_holm_detections=sum(rev_rej),
                 reversed_unadjusted_hits=fpr_unadj, gate_reversed_ok=(sum(rev_rej) == 0 and fpr_unadj <= 3))
    print('GATES', gates, flush=True)
    ps = []
    for a, b in pairs:
        M = lcs_len(seq[a], seq[b]); d = per[(a, b)]; p = pval(M, d['nd']); ps.append(p)
        res.append(dict(pair=f'{a}-{b}', M=M, null_median=sorted(d['nd'])[R // 2], null_max=max(d['nd']), p=p,
                        bonf_threshold_M=d['thr'], lstar=d['lstar'], power=d['power'], reversed_M=d['Mrev']))
    rej = holm(ps)
    for r, k in zip(res, rej):
        ok = gates['positive_controls_pass'] and gates['gate_reversed_ok']
        if not ok: r['verdict'] = 'NOT TESTABLE (instrument gate)'
        elif k: r['verdict'] = 'DETECTED'
        elif r['lstar'] is not None and r['lstar'] <= 10: r['verdict'] = f'NOT DETECTED (copy of >= {r["lstar"]} signs would be seen)'
        else: r['verdict'] = 'NOT TESTABLE (power)'
    out = dict(seed=3001, R=R, plants=P, pairs=m, bonferroni_alpha=bonf, positive=pos, gates=gates,
               reversed_p=rev_p, results=res, runtime_s=round(time.time() - t0, 1))
    json.dump(out, open(outp, 'w'), indent=1)
    for r in res: print(r['pair'], r['M'], r['null_max'], round(r['p'], 4), r['lstar'], r['verdict'])

if __name__ == '__main__':
    a = sys.argv; R = int(a[a.index('--R') + 1]) if '--R' in a else 999; P = int(a[a.index('--plants') + 1]) if '--plants' in a else 100
    main(a[1], a[2], R, P)
