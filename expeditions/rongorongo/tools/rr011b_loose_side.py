"""RR011b (line 4d) - does the loose stroke keep the fused stroke's side? Run only if RR011a (line 2) is NOT TESTABLE.
Cases = RR010's S1 cases (bare unit has a free stroke sharing a base with the fused copy's legible bound strokes
immediately before or after it), recomputed here from RR010's disagreement list. Fused side of stroke w in the fused
unit = B if the w component precedes the host component, A if it follows (':' read like '.'). Loose side = B/A
position of the qualifying free stroke next to the bare unit. A case is informative if exactly one side holds a
qualifying loose stroke and the fused side is defined (one w, on one side); K = informative cases where loose side
equals fused side.
Null (conditioned on RR004 side habits, independent of the copies): match probability p_i = r_B or 1 - r_B, where
r_B = (k_B + 0.5)/(n + 1) is the share of fused units with stroke w BEFORE host h on all tablets except H, P, Q
(host-specific if n >= 5, else stroke w over all hosts). Exact Poisson-binomial p = P(K' >= K), one-sided.
Gates: NOT TESTABLE if informative cases < 5, if the all-match floor prod(p_i) > 0.05 (no outcome could reject),
or if exact power at alpha 0.05 under H1 'loose side copies fused side with probability 0.95' is < 0.80.
Negative control: 20 draws from the null, <= 3 rejections at 0.05. Seed 11012.
Usage: python3 rr011b_loose_side.py corpus.json rr010_results.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, random
from collections import Counter
STROKES = {'001', '002', '003', '004', '009'}
def comps(u):
    out = []
    for c in (c for c in re.split(r'[.:]', u) if c):
        m = re.match(r'(\d+)(.*)', c)
        out.append((m.group(1).zfill(3), bool(re.search(r"[!?)]", c))) if m else (None, True))
    return out
def host_idx(cs):
    for i, (b, bad) in enumerate(cs):
        if b not in STROKES:
            return None if (b is None or bad or b == '000') else i
    return None
def side_of(u, w):
    cs = comps(u); h = host_idx(cs)
    if h is None: return None, None
    sides = {('B' if i < h else 'A') for i, (b, bad) in enumerate(cs) if b == w and not bad}
    return cs[h][0], (sides.pop() if len(sides) == 1 else None)
def free(u):
    cs = comps(u)
    if not cs or any(b not in STROKES for b, _ in cs): return None
    return {b for b, bad in cs if not bad}
def rates(corpus):
    hs, ws = Counter(), Counter()
    for k, line in corpus.items():
        if k[0] in 'HPQ': continue
        for u in line:
            for w in STROKES:
                h, s = side_of(u, w)
                if h and s: hs[(w, h, s)] += 1; ws[(w, s)] += 1
    return hs, ws
def rB(hs, ws, w, h):
    n = hs[(w, h, 'B')] + hs[(w, h, 'A')]
    if n >= 5: return (hs[(w, h, 'B')] + 0.5) / (n + 1), n, 'host'
    n = ws[(w, 'B')] + ws[(w, 'A')]; return (ws[(w, 'B')] + 0.5) / (n + 1), n, 'type'
def pb_tail(ps, k):
    d = [1.0]
    for p in ps:
        d = [a * (1 - p) + b * p for a, b in zip(d + [0], [0] + d)]
    return sum(d[k:])
def main(cp, rp, op):
    corpus = json.load(open(cp)); res = json.load(open(rp)); hs, ws = rates(corpus)
    cases = []
    for d in res['disagreement_list']:
        _, bk, bp, _ = d['bare']; line = corpus[bk]; want = set(d['want'])
        loose = {sd: (free(line[q]) or set()) & want for sd, q in (('B', bp - 1), ('A', bp + 1)) if 0 <= q < len(line)}
        hit = {sd for sd, v in loose.items() if v}
        if not hit: continue
        ws_ = set().union(*(loose[s] for s in hit))
        c = dict(fused=d['fused'], bare=d['bare'], loose_sides=sorted(hit), strokes=sorted(ws_))
        if len(hit) == 2 or len(ws_) != 1: c['informative'] = False; cases.append(c); continue
        w = ws_.pop(); h, fs = side_of(d['fused'][3], w)
        if fs is None: c['informative'] = False; cases.append(c); continue
        r, n, src = rB(hs, ws, w, h); ls = hit.pop()
        c.update(informative=True, stroke=w, host=h, fused_side=fs, loose_side=ls, match=ls == fs,
                 rB=r, rate_n=n, rate_source=src, p_match_null=r if fs == 'B' else 1 - r)
        cases.append(c)
    inf = [c for c in cases if c['informative']]; ps = [c['p_match_null'] for c in inf]
    K = sum(c['match'] for c in inf); p = pb_tail(ps, K) if inf else 1.0
    floor = pb_tail(ps, len(ps)) if inf else 1.0
    crit = next((k for k in range(len(ps) + 1) if pb_tail(ps, k) <= 0.05), None)
    power = pb_tail([0.95] * len(ps), crit) if crit is not None else 0.0
    rng = random.Random(11012); neg = 0
    for _ in range(20):
        k = sum(rng.random() < q for q in ps); neg += pb_tail(ps, k) <= 0.05
    nt = len(inf) < 5 or floor > 0.05 or power < 0.8 or neg > 3
    verdict = 'NOT TESTABLE' if nt else ('DETECTED' if p <= 0.05 else 'NOT DETECTED (powered)')
    out = dict(seed=11012, s1_cases=len(cases), informative=len(inf), K=K, null_expected=sum(ps), p=p,
               all_match_floor=floor, critical_k=crit, power_q095=power, negative_control_rejections=neg,
               verdict=verdict, cases=cases)
    json.dump(out, open(op, 'w'), indent=1); print({k: v for k, v in out.items() if k != 'cases'})
if __name__ == '__main__':
    main(*sys.argv[1:4])
