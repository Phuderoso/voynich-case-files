"""RR011 (line 2) - are Keiti's (tablet E) refrains strophic, i.e. do repeated sign pairs recur at more regular
distances than a structure-preserving shuffle gives?
Text: CEIPP corpus.json, tablet E, sides Er (Er01-Er09) and Ev (Ev01-Ev08) in line-id order. Token = whole CEIPP unit
with '?', '!' and ')' removed; units whose first component is 000 (illegible) become unique tokens (never match).
Refrain = token bigram inside one line (never across a line end), no illegible unit, occurring >= 4 times on the whole
tablet (overlapping starts counted). Analysis unit u = (refrain, side) with >= 3 starts on that side in the observed text
(>= 2 gaps); the unit set U is fixed from the observed text. Positions = index in the side's concatenated stream;
gaps = differences of consecutive starts.
T1 = gap-weighted mean over U of CV_u = population SD / mean of the gaps (low = periodic; one-sided lower tail).
T2 = mean over U of max_{P=4..60} Z_u(P), Z = |sum_k exp(2 pi i s_k / P)|^2 / n_u (Rayleigh; high = phase-locked;
one-sided upper tail).
Null (structure-preserving): per side, line order permuted uniformly; inside each line, the line is cut into blocks =
maximal runs of positions covered by any occurrence of any refrain (all refrains, not only U) plus single tokens, and
the blocks are put in uniformly random order. Keeps every line's length and sign multiset, every refrain occurrence,
and the side. Starts are rescanned in each null text. R 999, p = (1 + #null as or more extreme)/(R + 1).
Decision: Holm over {T1, T2}, family alpha 0.05.
Power: in a null text a new bigram (PL1 PL2) is overwritten 5 times per side at starts round(o + i*P) + U[-j, j],
P = side length / 5, o ~ U[0, P - 2] (moved left by 1 if it would straddle a line end); the plant joins the refrain
set and U; p against a fresh null of the planted text (R 199); power = share of 100 plants with p <= 0.025; j* =
largest jitter in {0,1,2,4,6,8,12} with power >= 0.80. Negative control: 20 fresh null texts scored as observed,
<= 3 rejections at 0.05 per statistic. NOT TESTABLE if |U| < 4, total gaps < 15, power(j = 0) < 0.80 or the negative
control fails (per statistic for the power gate).
Seed 11011. Usage: python3 rr011_refrain_period.py corpus.json out.json [--counts] [--smoke]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, random, math, cmath
from collections import Counter
from multiprocessing import Pool
SEED = 11011; R = 999; RP = 199; PLANTS = 100; JGRID = [0, 1, 2, 4, 6, 8, 12]; PER = range(4, 61); MINOCC = 4
SIDES = ('Er', 'Ev')
def tokens(corpus):
    out = {}; n = 0
    for s in SIDES:
        lines = []
        for k in sorted(k for k in corpus if k[:2] == s):
            ln = []
            for u in corpus[k]:
                t = re.sub(r'[?!)]', '', u)
                if re.fullmatch(r'0+', re.split(r'[.:]', t)[0]):
                    n += 1; t = f'#ILL{n}'
                ln.append(t)
            lines.append(ln)
        out[s] = lines
    return out
def refrains(T, extra=()):
    c = Counter()
    for s in SIDES:
        for ln in T[s]:
            for i in range(len(ln) - 1):
                if not (ln[i].startswith('#') or ln[i + 1].startswith('#')): c[(ln[i], ln[i + 1])] += 1
    return {g for g, v in c.items() if v >= MINOCC} | set(extra)
def starts(lines, rf):
    pos = {}; off = 0
    for ln in lines:
        for i in range(len(ln) - 1):
            g = (ln[i], ln[i + 1])
            if g in rf: pos.setdefault(g, []).append(off + i)
        off += len(ln)
    return pos
def units(T, rf):
    U = []
    for s in SIDES:
        for g, p in sorted(starts(T[s], rf).items()):
            if len(p) >= 3: U.append((g, s))
    return U
def cv(p):
    g = [b - a for a, b in zip(p, p[1:])]; m = sum(g) / len(g)
    return math.sqrt(sum((x - m) ** 2 for x in g) / len(g)) / m, len(g)
def ray(p):
    n = len(p); return max(abs(sum(cmath.exp(2j * math.pi * x / P) for x in p)) ** 2 / n for P in PER)
def score(T, rf, U):
    st = {s: starts(T[s], rf) for s in SIDES}; num = den = 0.0; z = 0.0
    for g, s in U:
        p = st[s].get(g, [])
        if len(p) < 3: return None
        c, w = cv(p); num += c * w; den += w; z += ray(p)
    return num / den, z / len(U)
def blocks(ln, rf):
    cov = [False] * len(ln); link = [False] * len(ln)  # link[i]: i and i+1 in same block
    for i in range(len(ln) - 1):
        if (ln[i], ln[i + 1]) in rf: link[i] = True
    out = []; cur = [ln[0]] if ln else []
    for i in range(1, len(ln)):
        if link[i - 1]: cur.append(ln[i])
        else: out.append(cur); cur = [ln[i]]
    if cur: out.append(cur)
    return out
def shuffle(T, rf, rng):
    out = {}
    for s in SIDES:
        L = [blocks(ln, rf) for ln in T[s]]; rng.shuffle(L); new = []
        for b in L:
            b = b[:]; rng.shuffle(b); new.append([t for x in b for t in x])
        out[s] = new
    return out
def nulls(T, rf, U, rng, n):
    return [score(shuffle(T, rf, rng), rf, U) for _ in range(n)]
def pv(o, null):
    n = len(null)
    return ((1 + sum(x[0] <= o[0] for x in null)) / (n + 1), (1 + sum(x[1] >= o[1] for x in null)) / (n + 1))
def holm(p):
    o = sorted(range(len(p)), key=lambda i: p[i]); out = [0] * len(p); run = 0
    for r, i in enumerate(o): run = max(run, min(1, (len(p) - r) * p[i])); out[i] = run
    return out
PL = ('PL1', 'PL2')
def plant(T, rf, rng, j):
    Tn = shuffle(T, rf, rng); out = {}
    for s in SIDES:
        lines = [ln[:] for ln in Tn[s]]; flat = [(a, b) for a, ln in enumerate(lines) for b in range(len(ln))]
        N = len(flat); P = N / 5; o = rng.uniform(0, P - 2)
        for i in range(5):
            x = min(max(0, round(o + i * P) + rng.randint(-j, j)), N - 2)
            a, b = flat[x]
            if b == len(lines[a]) - 1: b -= 1
            lines[a][b], lines[a][b + 1] = PL
        out[s] = lines
    return out
def power_task(args):
    j, k = args; rng = random.Random(SEED * 1000 + j * 1000003 + k)
    global _T, _rf, _U
    Tp = plant(_T, _rf, rng, j); rfp = _rf | {PL}; Up = _U + [(PL, s) for s in SIDES]
    o = score(Tp, rfp, Up)
    if o is None: return (0, 0)
    nl = [x for x in nulls(Tp, rfp, Up, rng, RP)]
    p = pv(o, nl); return (p[0] <= 0.025, p[1] <= 0.025)
def init(T, rf, U):
    global _T, _rf, _U; _T, _rf, _U = T, rf, U
def main(cp, op, counts=False, smoke=False):
    corpus = json.load(open(cp)); T = tokens(corpus); rf = refrains(T); U = units(T, rf)
    rng = random.Random(SEED)
    if smoke:  # I-116-style smoke: score a registered shuffle (seed 11999), never the observed text
        T = shuffle(T, rf, random.Random(11999)); U = units(T, rf)
    st = {s: starts(T[s], rf) for s in SIDES}
    gaps = sum(len(st[s][g]) - 1 for g, s in U)
    info = dict(tokens={s: sum(map(len, T[s])) for s in SIDES}, lines={s: len(T[s]) for s in SIDES},
                refrains=sorted(' '.join(g) for g in rf), units=len(U), total_gaps=gaps)
    print(info)
    if counts: return
    obs = score(T, rf, U)
    unit_detail = [dict(refrain=' '.join(g), side=s, starts=st[s][g],
                        gaps=[b - a for a, b in zip(st[s][g], st[s][g][1:])], cv=cv(st[s][g])[0], rayleigh_max=ray(st[s][g]))
                   for g, s in U]
    null = nulls(T, rf, U, rng, R); p = list(pv(obs, null)); ph = holm(p)
    neg = [0, 0]
    for _ in range(20):
        x = score(shuffle(T, rf, rng), rf, U); q = pv(x, null)
        neg[0] += q[0] <= 0.05; neg[1] += q[1] <= 0.05
    with Pool(8, initializer=init, initargs=(T, rf, U)) as pool:
        res = pool.map(power_task, [(j, k) for j in JGRID for k in range(PLANTS)])
    power = {0: {}, 1: {}}
    for a, j in enumerate(JGRID):
        chunk = res[a * PLANTS:(a + 1) * PLANTS]
        for c in (0, 1): power[c][j] = sum(r[c] for r in chunk) / PLANTS
    jstar = [max((j for j in JGRID if power[c][j] >= 0.8), default=None) for c in (0, 1)]
    nt_all = len(U) < 4 or gaps < 15 or max(neg) > 3
    verdict = []
    for c, name in ((0, 'T1 gap regularity (weighted CV)'), (1, 'T2 phase-locking (max Rayleigh)')):
        if nt_all or power[c][0] < 0.8: v = 'NOT TESTABLE'
        elif ph[c] <= 0.05: v = 'DETECTED'
        else: v = f'NOT DETECTED (a planted periodic refrain with jitter <= {jstar[c]} would be seen)'
        verdict.append(f'{name}: {v}')
    out = dict(seed=SEED, smoke=smoke, R=R, R_plant=RP, plants=PLANTS, **info, T1=obs[0], T2=obs[1],
               null_mean=[sum(n[c] for n in null) / R for c in (0, 1)],
               null_range=[[min(n[c] for n in null), max(n[c] for n in null)] for c in (0, 1)],
               p=p, p_holm=ph, power={'T1': power[0], 'T2': power[1]}, jstar=jstar,
               negative_control_rejections=neg, verdict=verdict, unit_detail=unit_detail)
    json.dump(out, open(op, 'w'), indent=1)
    print({k: v for k, v in out.items() if k not in ('unit_detail', 'refrains')})
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], '--counts' in sys.argv, '--smoke' in sys.argv)
