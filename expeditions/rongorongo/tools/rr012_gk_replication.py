"""RR012 (line 4e) - confirmatory replication of RR010 S1 on FRESH copies: Small Santiago recto (Gr) vs Small London
(K = Kr01-Kr05 then Kv01-Kv05, one reading sequence). Pairing fixed from the published parallel (Gr1-7 = Kr1-Kv5;
kohaumotu.org parallel_GK, Fischer 1997), not from the data. One copy pair: (Gr, K).
Units, hosts, flags, alignment (difflib SequenceMatcher, autojunk off, 'equal' blocks), disagreement, free stroke,
S1/S2 and the per-line free-stroke position shuffle are EXACTLY RR009/RR010's (imported functions), only the side
definition changes. S1 is the single confirmatory statistic (one-sided, excess). S2 is reported, descriptive only.
Family for Holm = {S1, 4d}; 4d (side-keeping) is run by rr012b and enters with p = 1 if NOT TESTABLE.
Gates (all computed without the observed S1): D >= 10 disagreements; free strokes in relevant lines >= 10;
power(S1) >= 0.80 at f_rep = (8 - 1.4985)/41 = 0.1586 (RR010's observed excess rate), alpha 0.025 (Holm step 1),
200 plants, plant null R 199; attainable floor P0(S1 >= S1max) <= 0.025 where S1max = # disagreements whose bare
line holds at least one free stroke sharing a base with the wanted strokes (null R 19999); negative control 40 null
replicates scored as data, <= 5 rejections at 0.05 (Binomial(40, .05) P(X>=6) = 0.014). Fail any -> NOT TESTABLE.
Observed: R 999, p = (1 + #null >= obs)/(R + 1). Seed 12012.
Usage: python3 rr012_gk_replication.py corpus.json out.json [--counts | --smoke]
  --counts: structural counts only (no S1/S2). --smoke: everything except the observed S1/S2; 'observed' replaced by
  one registered null shuffle (seed 12099) to rehearse the gates.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, random, difflib
import rr009_fusion_conservation as r9
import rr010_loose_strokes as r10
SEED = 12012; R = 999; RP = 199; PLANTS = 200; RFLOOR = 19999; NEG = 40
F_REP = (8 - 1.4984984984984986) / 41
FGRID = [0.05, 0.1, F_REP, 0.2, 0.3, 0.5, 1.0]
SIDES = {'Gr': lambda k: k[:2] == 'Gr', 'K': lambda k: k[:2] in ('Kr', 'Kv')}
PAIRS = [('Gr', 'K')]
def keys(corpus, s): return sorted(k for k in corpus if SIDES[s](k))   # Kr.. sorts before Kv..
def side(corpus, s): return [x for k in keys(corpus, s) for x in map(r9.unit, corpus[k]) if x]
def index(corpus, s): return [(k, p) for k in keys(corpus, s) for p, u in enumerate(corpus[k]) if r9.unit(u)]
def build(corpus):
    sides = {s: side(corpus, s) for s in SIDES}; links = []
    for a, b in PAIRS:
        x = [h for h, _ in sides[a]]; y = [h for h, _ in sides[b]]
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, x, y, autojunk=False).get_opcodes():
            if tag == 'equal': links += [(a, i1 + d, b, j1 + d) for d in range(i2 - i1)]
    return sides, links
def disagreements(corpus):
    sides, links = build(corpus); idx = {s: index(corpus, s) for s in sides}; D = []
    for a, i, b, j in links:
        fa, fb = sides[a][i][1], sides[b][j][1]
        if fa == fb: continue
        (fs, fi), (bs, bi) = ((a, i), (b, j)) if fa else ((b, j), (a, i))
        fk, fp = idx[fs][fi]; bk, bp = idx[bs][bi]
        D.append(dict(fused=(fs, fk, fp, corpus[fk][fp]), bare=(bs, bk, bp, corpus[bk][bp]),
                      want=sorted(r10.bound_strokes(corpus[fk][fp]))))
    return sides, links, D
def s1max(L, D):
    m = 0
    for items in L.values():
        F = [v for t, v in items if t == 'F']
        for t, v in items:
            if t == 'U':
                for d_id in v: m += any(x & set(D[d_id]['want']) for x in F)
    return m
def main(cp, op, mode):
    corpus = json.load(open(cp)); sides, links, D = disagreements(corpus); L = r10.lines_of(corpus, D)
    nF = sum(t == 'F' for it in L.values() for t, _ in it)
    eligible = sum(1 for a, i, b, j in links if sides[a][i][1] or sides[b][j][1])
    info = dict(units={s: len(u) for s, u in sides.items()}, aligned=len(links), eligible=eligible,
                disagreements=len(D), relevant_lines=len(L), free_strokes_in_relevant_lines=nF,
                units_in_relevant_lines=sum(map(len, L.values())))
    print(info)
    if mode == 'counts': json.dump(info, open(op, 'w'), indent=1); return
    rng = random.Random(SEED)
    smax = s1max(L, D); fl = r10.nulls(L, D, rng, RFLOOR)
    floor = (1 + sum(n[0] >= smax for n in fl)) / (RFLOOR + 1) if smax > 0 else 1.0
    null = r10.nulls(L, D, rng, R)
    neg = [0, 0]
    for _ in range(NEG):
        x = r10.score(r10.shuffle(L, rng), D)
        for c in (0, 1): neg[c] += r10.pv(x, null, c) <= 0.05
    power = {0: {}, 1: {}}
    for f in FGRID:
        hit = [0, 0]
        for _ in range(PLANTS):
            Lp = r10.plant(L, D, f, rng); o = r10.score(Lp, D); nl = r10.nulls(Lp, D, rng, RP)
            for c in (0, 1): hit[c] += r10.pv(o, nl, c) <= 0.025
        for c in (0, 1): power[c][round(f, 4)] = hit[c] / PLANTS
    prep = power[0][round(F_REP, 4)]
    gates = dict(D_ge_10=len(D) >= 10, free_ge_10=nF >= 10, power_at_f_rep_ge_080=prep >= 0.8,
                 floor_le_0025=floor <= 0.025, negctrl_S1_le_5_of_40=neg[0] <= 5)
    res = dict(seed=SEED, R=R, R_plant=RP, plants=PLANTS, R_floor=RFLOOR, f_rep=F_REP, **info, S1max=smax,
               p_floor=floor, power={'S1': power[0], 'S2': power[1]}, power_S1_at_f_rep=prep,
               negative_control_rejections_of_40=neg, gates=gates, testable=all(gates.values()))
    if mode == 'smoke':
        sm = r10.score(r10.shuffle(L, random.Random(12099)), D)
        res.update(mode='smoke (observed replaced by registered shuffle seed 12099)', S1_shuffle=sm[0], S2_shuffle=sm[1],
                   p_shuffle=[r10.pv(sm, null, c) for c in (0, 1)])
    else:
        obs = r10.score(L, D); p = [r10.pv(obs, null, c) for c in (0, 1)]
        res.update(mode='observed', S1=obs[0], S2=obs[1], null_mean=[sum(n[c] for n in null) / R for c in (0, 1)],
                   null_range=[[min(n[c] for n in null), max(n[c] for n in null)] for c in (0, 1)], p=p,
                   disagreement_list=[dict(fused=d['fused'], bare=d['bare'], want=d['want']) for d in D])
    json.dump(res, open(op, 'w'), indent=1)
    print({k: v for k, v in res.items() if k != 'disagreement_list'})
if __name__ == '__main__':
    m = 'counts' if '--counts' in sys.argv else 'smoke' if '--smoke' in sys.argv else 'observed'
    main(sys.argv[1], sys.argv[2], m)
