"""RR002 - do free strokes (1,2,3,4,9) keep a fixed order when side by side? Exact binomial per pair, Holm over 10,
power gate (theta=2/3 at 0.005 >= 0.80), copies (P, Q, K) removed, within-line shuffle negative control (R=200,
seed 3002), positive control {700, 600}. Usage: python3 rr002_stroke_order.py corpus.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, random, itertools
from math import comb
STROKES = ['001', '002', '003', '004', '009']
COPIES = ('P', 'Q', 'K')

def free_head(u, allowed, merge=None):
    if re.search(r"[.:;'!?]", u): return None
    m = re.match(r'(\d{3})', u)
    if not m: return None
    h = m.group(1)
    if merge and h in merge: h = merge[h]
    return h if h in allowed else None

def pmf(n, k, t): return comb(n, k) * t**k * (1 - t)**(n - k)

def binom_two_sided(k, n):
    if n == 0: return 1.0
    p0 = pmf(n, k, 0.5)
    return min(1.0, sum(pmf(n, i, 0.5) for i in range(n + 1) if pmf(n, i, 0.5) <= p0 * (1 + 1e-9)))

def power(n, alpha=0.005, t=2/3):
    if n == 0: return 0.0
    rej = [i for i in range(n + 1) if binom_two_sided(i, n) <= alpha]
    return sum(pmf(n, i, t) for i in rej)

def counts(lines, allowed, merge=None):
    c = {}
    for us in lines:
        hs = [free_head(u, allowed, merge) for u in us]
        for a, b in zip(hs, hs[1:]):
            if a and b and a != b: c[(a, b)] = c.get((a, b), 0) + 1
    return c

def holm(ps, alpha=0.05):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); rej = [False] * len(ps)
    for r, i in enumerate(order):
        if ps[i] <= alpha / (len(ps) - r): rej[i] = True
        else: break
    return rej

def test(lines, signs, merge=None, gate=True):
    c = counts(lines, set(signs), merge); res = []
    for x, y in itertools.combinations(signs, 2):
        k, n = c.get((x, y), 0), c.get((x, y), 0) + c.get((y, x), 0)
        res.append(dict(pair=f'{x}-{y}', k_x_first=k, n=n, power=round(power(n), 4), p=binom_two_sided(k, n)))
    rej = holm([r['p'] for r in res])
    for r, h in zip(res, rej):
        testable = r['power'] >= 0.80
        r['verdict'] = ('DETECTED' if h else 'NOT DETECTED') if testable else 'NOT TESTABLE'
        if r['verdict'] == 'DETECTED':
            x, y = r['pair'].split('-'); r['direction'] = f'{x} before {y}' if r['k_x_first'] * 2 > r['n'] else f'{y} before {x}'
        r['holm_reject_raw'] = h
    return res

def main(cp, op):
    corpus = json.load(open(cp))
    prim = [corpus[k] for k in sorted(corpus) if k[0] not in COPIES]
    full = [corpus[k] for k in sorted(corpus)]
    out = {'seed': 3002, 'n_lines_primary': len(prim), 'n_lines_full': len(full)}
    # gates first: n per pair (orientation-blind) and power
    out['gate_primary'] = [(r['pair'], r['n'], r['power']) for r in test(prim, STROKES)]
    print('GATE', out['gate_primary'])
    pc = test(prim, ['600', '700'])[0]; out['positive_control'] = pc; print('POSITIVE', pc)
    rng = random.Random(3002); fw = 0
    for _ in range(200):
        sh = []
        for us in prim:
            v = list(us); rng.shuffle(v); sh.append(v)
        if any(r['holm_reject_raw'] and r['power'] >= 0.80 for r in test(sh, STROKES)): fw += 1
    out['negative_familywise'] = fw / 200; out['negative_pass'] = fw / 200 <= 0.10
    print('NEGATIVE familywise', fw, '/200')
    out['primary'] = test(prim, STROKES)
    if not out['negative_pass']:
        for r in out['primary']: r['verdict'] = 'NOT TESTABLE (negative control failed)'
    for r in out['primary']: print('PRIMARY', r)
    out['secondary_full'] = test(full, STROKES)
    for r in out['secondary_full']: print('FULL', r)
    out['secondary_merge22'] = [r for r in test(prim, STROKES, merge={'022': '004'}) if r['pair'] == '002-004']
    print('MERGE22', out['secondary_merge22'])
    json.dump(out, open(op, 'w'), indent=1)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
