"""RR014 audit K - RR010 S1/S2 with R 9 999 (audit J lesson: R >= 9 999 when alpha is near 1/(R + 1)).
Data, disagreements, lines, score, shuffle and plant are RR010's (imported unchanged). Seed 14010.
Reports: observed S1, S2 (must equal RR010's 8 and 10); p with R 9 999; Holm over {S1, S2}; the null critical value
c(alpha) = smallest c with P0(S >= c) <= alpha for alpha 0.025 and 0.05, from R 999 (RR010 seed 10010 null, first 999
draws, recomputed) and from R 9 999; power of S1 at f in {0.10, 0.15, f_rep 0.1586, 0.20} with 400 plants each, each
judged against the fixed R 9 999 critical value c(0.025) of the UNPLANTED null (cheaper than RR010's per-plant null;
disclosed as a design difference) and also with RR010's own per-plant null R 199 at f 0.15.
Stability rule (fixed before running): RR010 S1 is 'stable' if p(R 9 999) <= 0.025 (Holm step 1) and f*(S1) under
the per-plant rule stays 0.15 (power >= 0.80 at 0.15).
Usage: python3 rr014_auditK.py corpus.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, random
import rr010_loose_strokes as r10
F_REP = (8 - 1.4984984984984986) / 41
def crit(null, c, a):
    vals = sorted({n[c] for n in null} | {max(n[c] for n in null) + 1})
    for v in vals:
        if sum(n[c] >= v for n in null) / len(null) <= a: return v
def main(cp, op):
    corpus = json.load(open(cp)); D = r10.disagreements(corpus); L = r10.lines_of(corpus, D)
    obs = r10.score(L, D)
    n999 = r10.nulls(L, D, random.Random(10010), 999)
    rng = random.Random(14010); big = r10.nulls(L, D, rng, 9999)
    p = [r10.pv(obs, big, c) for c in (0, 1)]; ph = r10.holm(p)
    cr = {f'R999_a{a}': [crit(n999, c, a) for c in (0, 1)] for a in (0.025, 0.05)}
    cr.update({f'R9999_a{a}': [crit(big, c, a) for c in (0, 1)] for a in (0.025, 0.05)})
    c0 = cr['R9999_a0.025'][0]
    pw_fixed = {}
    for f in (0.10, 0.15, F_REP, 0.20):
        hit = sum(r10.score(r10.plant(L, D, f, rng), D)[0] >= c0 for _ in range(400)); pw_fixed[round(f, 4)] = hit / 400
    hit = 0
    for _ in range(400):
        Lp = r10.plant(L, D, 0.15, rng); o = r10.score(Lp, D); hit += r10.pv(o, r10.nulls(Lp, D, rng, 199), 0) <= 0.025
    pw_rr010 = hit / 400
    res = dict(seed=14010, D=len(D), S1=obs[0], S2=obs[1], R=9999, p=p, p_holm=ph,
               null_mean=[sum(n[c] for n in big) / 9999 for c in (0, 1)],
               null_max=[max(n[c] for n in big) for c in (0, 1)],
               P0_S1_ge_obs=sum(n[0] >= obs[0] for n in big) / 9999, critical_values=cr,
               power_S1_fixed_c=pw_fixed, power_S1_at_015_rr010_rule_400plants=pw_rr010,
               stable=(p[0] <= 0.025 and pw_rr010 >= 0.8))
    json.dump(res, open(op, 'w'), indent=1); print(res)
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
