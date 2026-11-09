"""RR009 (line 4b) - is a fused stroke kept when the H/P/Q scribes copy the same sign?
Unit host = base of the first non-stroke legible component (codes padded as RR004); flag = the unit also holds a
legible stroke component (001 002 003 004 009), i.e. a bound stroke. Units with no non-stroke component, or whose
host is illegible/uncertain ('!' '?' ')'), are skipped. For each copy pair (Hr-Pr, Hr-Qr, Pr-Qr, Hv-Pv, Hv-Qv, Pv-Qv)
the host sequences are aligned with difflib SequenceMatcher (autojunk off); inside 'equal' blocks every aligned unit
pair has the same host. Eligible pair = at least one of the two is flagged.
Statistic A = number of eligible aligned pairs whose flags DIFFER (one copy fused, other bare), pooled over 6 pairs.
Null: flags permuted among units of the SAME host WITHIN each side (keeps every host's fusion rate per side, and the
alignment), R 999, p = (1 + #null A <= obs)/(R + 1) (one-sided: conservation). Single test, alpha 0.05.
Power: on null replicates, for a fraction f of the aligned same-host pairs the second copy's flag is set equal to the
first's; f* = smallest f in the grid with power >= 0.80. Negative control: 20 fresh null replicates scored as
observed, rejections must be <= 3. NOT TESTABLE if eligible pairs < 30, f* undefined or the negative control fails.
Seed 9009. Usage: python3 rr009_fusion_conservation.py corpus.json out.json [--counts]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, random, difflib
from collections import defaultdict, Counter
STROKES = {'001', '002', '003', '004', '009'}; R = 999; PLANTS = 200
PAIRS = [('Hr', 'Pr'), ('Hr', 'Qr'), ('Pr', 'Qr'), ('Hv', 'Pv'), ('Hv', 'Qv'), ('Pv', 'Qv')]
FGRID = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]
def pad(c):
    m = re.match(r'(\d+)(.*)', c); return (m.group(1).zfill(3) + m.group(2)) if m else c
def base(c):
    m = re.match(r'(\d{3})', c); return m.group(1) if m else None
def unit(u):
    cs = [pad(c) for c in re.split(r'[.:]', u) if c]
    host = None; flag = False
    for c in cs:
        b = base(c); bad = bool(re.search(r"[!?)]", c))
        if b in STROKES:
            if not bad: flag = True
        elif host is None:
            if b is None or bad or b == '000': return None
            host = b
    return (host, flag) if host else None
def side(corpus, s):
    return [x for k in sorted(k for k in corpus if k[:2] == s) for x in map(unit, corpus[k]) if x]
def build(corpus):
    sides = {s: side(corpus, s) for p in PAIRS for s in p}
    links = []  # (side_a, i, side_b, j)
    for a, b in PAIRS:
        x = [h for h, _ in sides[a]]; y = [h for h, _ in sides[b]]
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, x, y, autojunk=False).get_opcodes():
            if tag == 'equal': links += [(a, i1 + d, b, j1 + d) for d in range(i2 - i1)]
    return sides, links
def A_stat(fl, links):
    e = [(fl[a][i], fl[b][j]) for a, i, b, j in links if fl[a][i] or fl[b][j]]
    return sum(p != q for p, q in e), len(e)
def permute(sides, rng):
    out = {}
    for s, us in sides.items():
        g = defaultdict(list)
        for i, (h, _) in enumerate(us): g[h].append(i)
        f = [fl for _, fl in us]
        for idx in g.values():
            v = [f[i] for i in idx]; rng.shuffle(v)
            for i, x in zip(idx, v): f[i] = x
        out[s] = f
    return out
def main(cp, op, counts=False):
    corpus = json.load(open(cp)); sides, links = build(corpus)
    obs_fl = {s: [f for _, f in us] for s, us in sides.items()}
    A, N = A_stat(obs_fl, links)
    info = dict(units={s: len(u) for s, u in sides.items()}, flagged={s: sum(f for _, f in u) for s, u in sides.items()},
                aligned=len(links), eligible=N)
    print(info)
    if counts: return
    rng = random.Random(9009)
    null = sorted(A_stat(permute(sides, rng), links)[0] for _ in range(R))
    pv = lambda a: (1 + sum(n <= a for n in null)) / (R + 1)
    p = pv(A)
    neg = [pv(A_stat(permute(sides, rng), links)[0]) for _ in range(20)]
    power = {}
    for f in FGRID:
        hit = 0
        for _ in range(PLANTS):
            fl = permute(sides, rng)
            for a, i, b, j in links:
                if rng.random() < f: fl[b][j] = fl[a][i]
            hit += pv(A_stat(fl, links)[0]) <= 0.05
        power[f] = hit / PLANTS
    fstar = next((f for f in FGRID if power[f] >= 0.8), None)
    negrej = sum(x <= 0.05 for x in neg)
    if N < 30 or fstar is None or negrej > 3: verdict = 'NOT TESTABLE'
    elif p <= 0.05: verdict = 'DETECTED (fusion conserved across copies beyond the per-host rate)'
    else: verdict = f'NOT DETECTED (conservation on >= {fstar:.0%} of aligned pairs would be seen)'
    by = Counter()
    for a, i, b, j in links:
        p1, p2 = obs_fl[a][i], obs_fl[b][j]
        if p1 or p2: by[(sides[a][i][0], p1 == p2)] += 1
    res = dict(seed=9009, R=R, plants=PLANTS, **info, A=A, null_mean=sum(null) / R, null_min=null[0], null_max=null[-1],
               p=p, power=power, fstar=fstar, negative_control_rejections=negrej, verdict=verdict,
               by_host={f'{h} {"same" if s else "diff"}': c for (h, s), c in by.most_common()})
    json.dump(res, open(op, 'w'), indent=1)
    print({k: v for k, v in res.items() if k != 'by_host'}); print(by.most_common(20))
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], '--counts' in sys.argv)
