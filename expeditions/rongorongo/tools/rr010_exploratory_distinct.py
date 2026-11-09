"""RR010 exploratory (NOT pre-registered): S1 counting each distinct bare unit once (Qr03 600a is the bare side of two
disagreements), same null, R 999, seed 10011. Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, random, sys
from rr010_loose_strokes import disagreements, lines_of, shuffle
c = json.load(open(sys.argv[1])); D = disagreements(c); L = lines_of(c, D)
def s1u(L):
    n = 0
    for it in L.values():
        for p, (t, v) in enumerate(it):
            if t != 'U' or not v: continue
            want = set().union(*(set(D[i]['want']) for i in v))
            n += any(it[q][0] == 'F' and it[q][1] & want for q in (p - 1, p + 1) if 0 <= q < len(it))
    return n
rng = random.Random(10011); obs = s1u(L); null = [s1u(shuffle(L, rng)) for _ in range(999)]
print(dict(S1_distinct=obs, distinct_bare_units=len({d['bare'][:3] for d in D}), null_mean=sum(null) / 999,
           null_max=max(null), p=(1 + sum(x >= obs for x in null)) / 1000))
