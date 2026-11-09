"""RR004 post hoc (labelled, not pre-registered): (1) top stroke x host cells, (2) type-level version: each distinct
normalised compound counted once, labels permuted globally (R 999), (3) leave-the-host-380-out token test.
Seed 4005. Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, random, re
from collections import Counter
sys.path.insert(0, '.')
import rr004_stroke_hosts as T
c = json.load(open(sys.argv[1])); keys = [k for k in c if k[0] not in T.COPIES]; rng = random.Random(4005)
sl = T.slots(c, keys); D = T.Data(sl)
tab = Counter(zip(D.host, D.st)); hc = Counter(D.host); sc = Counter(D.st); n = len(D.st)
cells = sorted(((o, o / (hc[h] * sc[s] / n), h, s) for (h, s), o in tab.items() if hc[h] >= 15), key=lambda x: -x[1])
print('TOP_LIFT', [(h, s, o, round(l, 2)) for o, l, h, s in cells[:10]])
print('SIDE', sorted(Counter(zip(D.st, D.side)).items()))
# type level
types = set()
for k in keys:
    for u in c[k]:
        cs = T.comps(u)
        if len(cs) >= 2: types.add('.'.join(cs))
fake = {'X': [t for t in sorted(types)]}
slt = T.slots(fake, ['X'])
st = [s for _, s, _, _ in slt]; hc2 = Counter(h for _, _, h, _ in slt)
host = [h if hc2[h] >= 3 else 'other' for _, _, h, _ in slt]; side = [d for _, _, _, d in slt]
o1 = T.mi(list(zip(st, host))); o2 = T.mi(list(zip(st, side)))
n1 = []; n2 = []
for _ in range(999):
    p = list(st); rng.shuffle(p); n1.append(T.mi(list(zip(p, host)))); n2.append(T.mi(list(zip(p, side))))
print('TYPE_LEVEL n_slots', len(st), 'H1', round(o1, 4), 'null_max', round(max(n1), 4), 'p', T.pval(o1, n1),
      'H2', round(o2, 4), 'null_max', round(max(n2), 4), 'p', T.pval(o2, n2))
# drop host 380
keep = [i for i, h in enumerate(D.host) if h != '380']
sub = [sl[i] for i in keep]; D2 = T.Data(sub)
o = D2.stats(D2.st); nn = [D2.stats(D2.perm(D2.st, rng)) for _ in range(999)]
print('NO380 n', len(sub), 'H1', round(o[0], 4), 'nullmax', round(max(a for a, _ in nn), 4), 'p', T.pval(o[0], [a for a, _ in nn]),
      'H2', round(o[1], 4), 'p', T.pval(o[1], [b for _, b in nn]))
