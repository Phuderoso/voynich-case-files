"""RR010 (line 4c) - when two H/P/Q copies disagree on a fused stroke, does the bare copy write that stroke loose
right beside the host more often than its free strokes would sit there by chance?
Units, hosts, flags and the copy alignment are exactly those of RR009 (rr009_fusion_conservation.build). A
disagreement = an aligned same-host pair where one copy is fused (bound legible stroke 001/002/003/004/009) and the
other is bare. In the bare copy's raw line (the CEIPP line the unit sits on, all units kept) a FREE STROKE is a unit
whose every component has a stroke base; its stroke set = bases of its legible components (no '!' '?' ')').
S1 (primary) = # disagreements whose bare unit has, immediately before or after it in the same line, a free stroke
whose set shares a base with the fused copy's legible bound strokes. S2 = same with any free stroke (non-empty set).
Null: in every line of the bare sides that holds a disagreement, the free-stroke units are moved to a uniformly random
set of positions (random order); all other units keep their relative order; counts per line kept. R 999,
p = (1 + #null >= obs)/(R + 1), one-sided (excess). Holm over {S1, S2} at 0.05.
Power: in null replicates, for a fraction f of disagreements a free stroke carrying the fused copy's first bound
stroke is inserted right after the bare unit; p recomputed against a fresh null of the planted lines (R 199);
power = share of 200 plants with p <= 0.025 (Holm's first step); f* = smallest f with power >= 0.80, per statistic.
Negative control: 20 null replicates scored as data; <= 3 rejections at 0.05 per statistic.
NOT TESTABLE if disagreements < 30, free strokes in the relevant lines < 10, f*(S1) undefined or a control fails.
Seed 10010. Usage: python3 rr010_loose_strokes.py corpus.json out.json [--counts]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, random
from rr009_fusion_conservation import pad, base, unit, build, PAIRS, STROKES
R = 999; RP = 199; PLANTS = 200; FGRID = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]
def bound_strokes(u):
    return {base(c) for c in map(pad, (c for c in re.split(r'[.:]', u) if c))
            if base(c) in STROKES and not re.search(r"[!?)]", c)}
def free_set(u):
    cs = [pad(c) for c in re.split(r'[.:]', u) if c]
    if not cs or any(base(c) not in STROKES for c in cs): return None
    return frozenset(base(c) for c in cs if not re.search(r"[!?)]", c))
def index(corpus, s):
    """side index (as in RR009 side()) -> (line key, raw position)"""
    out = []
    for k in sorted(k for k in corpus if k[:2] == s):
        for pos, u in enumerate(corpus[k]):
            if unit(u): out.append((k, pos))
    return out
def disagreements(corpus):
    sides, links = build(corpus); idx = {s: index(corpus, s) for s in sides}
    D = []
    for a, i, b, j in links:
        fa, fb = sides[a][i][1], sides[b][j][1]
        if fa == fb: continue
        (fs, fi), (bs, bi) = ((a, i), (b, j)) if fa else ((b, j), (a, i))
        fk, fp = idx[fs][fi]; bk, bp = idx[bs][bi]
        D.append(dict(fused=(fs, fk, fp, corpus[fk][fp]), bare=(bs, bk, bp, corpus[bk][bp]),
                      want=sorted(bound_strokes(corpus[fk][fp]))))
    return D
def lines_of(corpus, D):
    """relevant bare lines as item lists: ('F', set) for free strokes, ('U', [disagreement ids]) otherwise"""
    L = {}
    for d_id, d in enumerate(D):
        _, k, p, _ = d['bare']
        if k not in L: L[k] = [('F', fs) if (fs := free_set(u)) is not None else ('U', []) for u in corpus[k]]
        L[k][p][1].append(d_id)
    return L
def score(L, D):
    s1 = s2 = 0
    for items in L.values():
        for p, (t, v) in enumerate(items):
            if t != 'U' or not v: continue
            nb = [items[q][1] for q in (p - 1, p + 1) if 0 <= q < len(items) and items[q][0] == 'F']
            for d_id in v:
                want = set(D[d_id]['want'])
                s2 += any(len(x) > 0 for x in nb); s1 += any(x & want for x in nb)
    return s1, s2
def shuffle(L, rng):
    out = {}
    for k, items in L.items():
        F = [x for x in items if x[0] == 'F']; U = [x for x in items if x[0] != 'F']
        if not F: out[k] = items; continue
        pos = set(rng.sample(range(len(items)), len(F))); rng.shuffle(F); fi = iter(F); ui = iter(U)
        out[k] = [next(fi) if q in pos else next(ui) for q in range(len(items))]
    return out
def nulls(L, D, rng, r):
    return [score(shuffle(L, rng), D) for _ in range(r)]
def pv(obs, null, c):
    return (1 + sum(n[c] >= obs[c] for n in null)) / (len(null) + 1)
def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0] * len(ps); m = len(ps); run = 0
    for r, i in enumerate(o): run = max(run, min(1, (m - r) * ps[i])); adj[i] = run
    return adj
def plant(L, D, f, rng):
    L = {k: [(t, list(v) if t == 'U' else v) for t, v in it] for k, it in shuffle(L, rng).items()}
    for d_id, d in enumerate(D):
        if rng.random() >= f: continue
        k = d['bare'][1]; items = L[k]
        p = next(q for q, (t, v) in enumerate(items) if t == 'U' and d_id in v)
        items.insert(p + 1, ('F', frozenset([d['want'][0]])))
    return L
def main(cp, op, counts=False):
    corpus = json.load(open(cp)); D = disagreements(corpus); L = lines_of(corpus, D)
    nF = sum(t == 'F' for it in L.values() for t, _ in it)
    info = dict(disagreements=len(D), relevant_lines=len(L), free_strokes_in_relevant_lines=nF,
                units_in_relevant_lines=sum(map(len, L.values())))
    print(info)
    if counts: return
    rng = random.Random(10010)
    obs = score(L, D); null = nulls(L, D, rng, R)
    p = [pv(obs, null, c) for c in (0, 1)]; ph = holm(p)
    neg = [0, 0]
    for _ in range(20):
        x = score(shuffle(L, rng), D)
        for c in (0, 1): neg[c] += pv(x, null, c) <= 0.05
    power = {0: {}, 1: {}}
    for f in FGRID:
        hit = [0, 0]
        for _ in range(PLANTS):
            Lp = plant(L, D, f, rng); o = score(Lp, D); nl = nulls(Lp, D, rng, RP)
            for c in (0, 1): hit[c] += pv(o, nl, c) <= 0.025
        for c in (0, 1): power[c][f] = hit[c] / PLANTS
    fstar = [next((f for f in FGRID if power[c][f] >= 0.8), None) for c in (0, 1)]
    nt = len(D) < 30 or nF < 10 or fstar[0] is None or max(neg) > 3
    verdict = []
    for c, name in ((0, 'S1 same stroke loose beside host'), (1, 'S2 any free stroke beside host')):
        if nt or fstar[c] is None: v = 'NOT TESTABLE'
        elif ph[c] <= 0.05: v = 'DETECTED'
        else: v = f'NOT DETECTED (planted loose spellings on >= {fstar[c]:.0%} of disagreements would be seen)'
        verdict.append(f'{name}: {v}')
    res = dict(seed=10010, R=R, R_plant=RP, plants=PLANTS, **info, S1=obs[0], S2=obs[1],
               null_mean=[sum(n[c] for n in null) / R for c in (0, 1)],
               null_range=[[min(n[c] for n in null), max(n[c] for n in null)] for c in (0, 1)],
               p=p, p_holm=ph, power={'S1': power[0], 'S2': power[1]}, fstar=fstar,
               negative_control_rejections=neg, verdict=verdict,
               disagreement_list=[dict(fused=d['fused'], bare=d['bare'], want=d['want'],
                                      bare_line_neighbours=[corpus[d['bare'][1]][q] for q in (d['bare'][2] - 1, d['bare'][2] + 1)
                                                            if 0 <= q < len(corpus[d['bare'][1]])]) for d in D])
    json.dump(res, open(op, 'w'), indent=1)
    print({k: v for k, v in res.items() if k != 'disagreement_list'})
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], '--counts' in sys.argv)
