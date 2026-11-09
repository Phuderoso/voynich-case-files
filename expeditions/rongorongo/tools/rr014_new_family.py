"""RR014 (line 4f) - does RR010's 'loose beside the bare host' spelling appear in a NEW parallel family: the short
shared passages BETWEEN objects outside the copy families already used (H/P/Q, G/K)?
Family N (fixed before any count): every pair of sides (two-letter CEIPP side codes, as RR009 side()) from DIFFERENT
objects (first letter), except pairs with both sides in {H,P,Q} or both in {G,K}. Passage = a maximal exact common
run of >= LMIN = 5 host signs (RR009 unit(): host = first non-stroke legible base, flag = bound legible stroke) between
the two sides' host sequences; LMIN 5 is rochal/rongorongo's 'strict 5+' parallel threshold. Every aligned position
(i, j) inside such a run is one link (a set per side pair, so overlapping runs do not double-count a position).
Disagreement, free stroke, S1, S2, the per-line free-stroke position shuffle and the plant are EXACTLY RR010's
(imported rr010_loose_strokes functions). S1 is the single confirmatory statistic (one-sided, excess), alpha 0.05;
S2 is descriptive only.
Gates (computed without the observed S1): G1 D >= 10 disagreements (checked FIRST, by --counts); G2 >= 10 free
strokes in the relevant bare lines; G3 power(S1) >= 0.80 at f_rep = (8 - 1.4985)/41 = 0.1586 (RR010's observed excess
rate), alpha 0.05, 200 plants, plant null R 199; G4 attainable floor P0(S1 >= S1max) <= 0.05 (null R 19999);
G5 negative control 40 null replicates scored as data, <= 5 rejections at 0.05. Any gate fails -> NOT TESTABLE.
Observed (only if all gates pass): R 9999 (audit J lesson), p = (1 + #null >= obs)/(R + 1).
Seed 14014; smoke shuffle seed 14099.
Usage: python3 rr014_new_family.py corpus.json out.json [--counts | --smoke]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, random
from collections import defaultdict
import rr009_fusion_conservation as r9
import rr010_loose_strokes as r10
SEED = 14014; SMOKE = 14099; LMIN = 5; R = 9999; RP = 199; PLANTS = 200; RFLOOR = 19999; NEG = 40; ALPHA = 0.05
F_REP = (8 - 1.4984984984984986) / 41
FGRID = [0.05, 0.1, F_REP, 0.2, 0.3, 0.5, 1.0]
EXCL = [set('HPQ'), set('GK')]
def all_sides(corpus): return sorted({k[:2] for k in corpus})
def pairs(sides):
    out = []
    for i, a in enumerate(sides):
        for b in sides[i + 1:]:
            if a[0] == b[0] or any(a[0] in e and b[0] in e for e in EXCL): continue
            out.append((a, b))
    return out
def runs(x, y, lmin=LMIN):
    """maximal exact common runs (i, j, length) of x and y with length >= lmin"""
    pos = defaultdict(list)
    for j in range(len(y) - lmin + 1): pos[tuple(y[j:j + lmin])].append(j)
    out = []
    for i in range(len(x) - lmin + 1):
        for j in pos.get(tuple(x[i:i + lmin]), ()):
            if i > 0 and j > 0 and x[i - 1] == y[j - 1]: continue   # not left-maximal
            n = lmin
            while i + n < len(x) and j + n < len(y) and x[i + n] == y[j + n]: n += 1
            out.append((i, j, n))
    return out
def build(corpus):
    S = all_sides(corpus); sides = {s: r9.side(corpus, s) for s in S}; links = []; passages = []
    for a, b in pairs(S):
        x = [h for h, _ in sides[a]]; y = [h for h, _ in sides[b]]; seen = set()
        for i, j, n in runs(x, y):
            passages.append((a, i, b, j, n))
            for d in range(n):
                if (i + d, j + d) not in seen: seen.add((i + d, j + d)); links.append((a, i + d, b, j + d))
    return sides, links, passages
def disagreements(corpus):
    sides, links, passages = build(corpus); idx = {s: r10.index(corpus, s) for s in sides}; D = []
    for a, i, b, j in links:
        fa, fb = sides[a][i][1], sides[b][j][1]
        if fa == fb: continue
        (fs, fi), (bs, bi) = ((a, i), (b, j)) if fa else ((b, j), (a, i))
        fk, fp = idx[fs][fi]; bk, bp = idx[bs][bi]
        D.append(dict(fused=(fs, fk, fp, corpus[fk][fp]), bare=(bs, bk, bp, corpus[bk][bp]),
                      want=sorted(r10.bound_strokes(corpus[fk][fp]))))
    return sides, links, passages, D
def s1max(L, D):
    m = 0
    for items in L.values():
        F = [v for t, v in items if t == 'F']
        for t, v in items:
            if t == 'U':
                for d_id in v: m += any(x & set(D[d_id]['want']) for x in F)
    return m
def main(cp, op, mode):
    corpus = json.load(open(cp)); sides, links, passages, D = disagreements(corpus); L = r10.lines_of(corpus, D)
    nF = sum(t == 'F' for it in L.values() for t, _ in it)
    eligible = sum(1 for a, i, b, j in links if sides[a][i][1] or sides[b][j][1])
    pp = sorted({(a, b) for a, _, b, _, _ in passages})
    info = dict(side_pairs=len(pairs(all_sides(corpus))), passages=len(passages), pairs_with_passage=len(pp),
                longest=max((n for *_, n in passages), default=0), aligned=len(links), eligible=eligible,
                disagreements=len(D), relevant_lines=len(L), free_strokes_in_relevant_lines=nF,
                units_in_relevant_lines=sum(map(len, L.values())),
                passage_list=[f'{a}[{i}] {b}[{j}] len {n}' for a, i, b, j, n in passages])
    print({k: v for k, v in info.items() if k != 'passage_list'})
    if mode == 'counts':
        info['G1_D_ge_10'] = len(D) >= 10; json.dump(info, open(op, 'w'), indent=1); return
    rng = random.Random(SEED)
    smax = s1max(L, D); fl = r10.nulls(L, D, rng, RFLOOR)
    floor = (1 + sum(n[0] >= smax for n in fl)) / (RFLOOR + 1) if smax > 0 else 1.0
    null = r10.nulls(L, D, rng, R)
    neg = [0, 0]
    for _ in range(NEG):
        x = r10.score(r10.shuffle(L, rng), D)
        for c in (0, 1): neg[c] += r10.pv(x, null, c) <= ALPHA
    power = {0: {}, 1: {}}
    for f in FGRID:
        hit = [0, 0]
        for _ in range(PLANTS):
            Lp = r10.plant(L, D, f, rng); o = r10.score(Lp, D); nl = r10.nulls(Lp, D, rng, RP)
            for c in (0, 1): hit[c] += r10.pv(o, nl, c) <= ALPHA
        for c in (0, 1): power[c][round(f, 4)] = hit[c] / PLANTS
    prep = power[0][round(F_REP, 4)]
    gates = dict(G1_D_ge_10=len(D) >= 10, G2_free_ge_10=nF >= 10, G3_power_at_f_rep_ge_080=prep >= 0.8,
                 G4_floor_le_005=floor <= ALPHA, G5_negctrl_S1_le_5_of_40=neg[0] <= 5)
    res = dict(seed=SEED, R=R, R_plant=RP, plants=PLANTS, R_floor=RFLOOR, f_rep=F_REP, **info, S1max=smax,
               p_floor=floor, power={'S1': power[0], 'S2': power[1]}, power_S1_at_f_rep=prep,
               negative_control_rejections_of_40=neg, gates=gates, testable=all(gates.values()))
    if mode == 'smoke':
        sm = r10.score(r10.shuffle(L, random.Random(SMOKE)), D)
        res.update(mode=f'smoke (observed replaced by registered shuffle seed {SMOKE})', S1_shuffle=sm[0],
                   S2_shuffle=sm[1], p_shuffle=[r10.pv(sm, null, c) for c in (0, 1)])
    else:
        obs = r10.score(L, D); p = [r10.pv(obs, null, c) for c in (0, 1)]
        res.update(mode='observed', S1=obs[0], S2=obs[1], null_mean=[sum(n[c] for n in null) / R for c in (0, 1)],
                   null_range=[[min(n[c] for n in null), max(n[c] for n in null)] for c in (0, 1)], p=p,
                   verdict=('NOT TESTABLE' if not res['testable'] else 'DETECTED' if p[0] <= ALPHA else 'NOT DETECTED (powered)'),
                   disagreement_list=[dict(fused=d['fused'], bare=d['bare'], want=d['want']) for d in D])
    json.dump(res, open(op, 'w'), indent=1)
    print({k: v for k, v in res.items() if k not in ('disagreement_list', 'passage_list')})
if __name__ == '__main__':
    m = 'counts' if '--counts' in sys.argv else 'smoke' if '--smoke' in sys.argv else 'observed'
    main(sys.argv[1], sys.argv[2], m)
