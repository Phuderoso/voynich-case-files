"""RR003 - do free strokes cluster, and do they sit at the edges of 380.1-delimited list entries?
H1 adjacent stroke-stroke pairs vs within-line shuffle; H2 entry-final / H3 entry-initial strokes vs within-entry
shuffle. R=999, Holm over 3, planted power (m*), null-as-observed negative control (20 replicates). Seed 3003.
Usage: python3 rr003_stroke_clustering.py corpus.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, random
COPIES = ('P', 'Q', 'K'); R = 999; PLANTS = 100
M1 = [2, 4, 6, 8, 10, 15, 20, 30, 40]; M2 = [2, 3, 4, 5, 6, 8, 10, 15, 20]

def is_stroke(u):
    return not re.search(r"[.:;'!?]", u) and re.match(r'00[12349]', u) is not None
def is_delim(u): return u.startswith('380.001')

def s1(lines): return sum(1 for us in lines for a, b in zip(us, us[1:]) if is_stroke(a) and is_stroke(b))
def entries(corpus, keys):
    out = []
    for side in sorted(set(k[:2] for k in keys)):
        seq = [u for k in sorted(k for k in keys if k[:2] == side) for u in corpus[k]]
        idx = [i for i, u in enumerate(seq) if is_delim(u)]
        for a, b in zip(idx, idx[1:]):
            if b - a > 1: out.append(seq[a + 1:b])
    return out
def s2(es): return sum(1 for e in es if is_stroke(e[-1]))
def s3(es): return sum(1 for e in es if is_stroke(e[0]))
def shuf(groups, rng):
    o = []
    for g in groups:
        v = list(g); rng.shuffle(v); o.append(v)
    return o
def pval(obs, null): return (1 + sum(1 for x in null if x >= obs)) / (len(null) + 1)

def plant1(lines, m, rng):
    L = [list(l) for l in lines]; done = 0
    cand = [(i, j) for i, l in enumerate(L) for j, u in enumerate(l) if is_stroke(u)]
    rng.shuffle(cand)
    for i, j in cand:
        if done >= m: break
        l = L[i]
        if (j > 0 and is_stroke(l[j - 1])) or (j + 1 < len(l) and is_stroke(l[j + 1])): continue
        others = [t for t, u in enumerate(l) if is_stroke(u) and t != j and abs(t - j) > 1]
        if not others: continue
        t = rng.choice(others); dest = t + 1 if t + 1 < len(l) and t + 1 != j else t - 1
        if dest < 0 or dest == j or is_stroke(l[dest]): continue
        l[j], l[dest] = l[dest], l[j]; done += 1
    return L, done
def plant2(es, m, rng, final=True):
    E = [list(e) for e in es]; done = 0
    cand = [i for i, e in enumerate(E) if not is_stroke(e[-1 if final else 0]) and any(is_stroke(u) for u in e)]
    rng.shuffle(cand)
    for i in cand[:m]:
        e = E[i]; j = rng.choice([t for t, u in enumerate(e) if is_stroke(u)]); k = len(e) - 1 if final else 0
        e[j], e[k] = e[k], e[j]; done += 1
    return E, done

def analyse(lines, es, rng):
    n1 = [s1(shuf(lines, rng)) for _ in range(R)]
    n2, n3 = [], []
    for _ in range(R):
        sh = shuf(es, rng); n2.append(s2(sh)); n3.append(s3(sh))
    return n1, n2, n3
def holm(ps, a=0.05):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); rej = [False] * len(ps)
    for r, i in enumerate(o):
        if ps[i] <= a / (len(ps) - r): rej[i] = True
        else: break
    return rej

def main(cp, op):
    corpus = json.load(open(cp)); rng = random.Random(3003)
    keys = [k for k in corpus if k[0] not in COPIES]
    lines = [corpus[k] for k in sorted(keys)]; es = entries(corpus, keys)
    out = {'seed': 3003, 'R': R, 'n_lines': len(lines), 'n_entries': len(es),
           'n_strokes': sum(is_stroke(u) for l in lines for u in l),
           'entries_with_stroke': sum(any(is_stroke(u) for u in e) for e in es)}
    print('SIZES', out)
    n1, n2, n3 = analyse(lines, es, rng)
    nulls = {'H1': n1, 'H2': n2, 'H3': n3}
    # gates first: planted power on null replicates, alpha for power = Bonferroni 0.05/3
    pw = {}
    for H, grid in (('H1', M1), ('H2', M2), ('H3', M2)):
        pw[H] = []
        for m in grid:
            hit = 0; got = []
            for _ in range(PLANTS):
                if H == 'H1':
                    P, d = plant1(shuf(lines, rng), m, rng); st = s1(P)
                else:
                    P, d = plant2(shuf(es, rng), m, rng, final=(H == 'H2')); st = s2(P) if H == 'H2' else s3(P)
                got.append(d); hit += pval(st, nulls[H]) <= 0.05 / 3
            pw[H].append((m, hit / PLANTS, min(got)))
        print('POWER', H, pw[H])
    out['power'] = pw
    mstar = {H: next((m for m, p, _ in pw[H] if p >= 0.80), None) for H in pw}
    out['mstar'] = mstar; print('MSTAR', mstar)
    # negative control: a fresh null replicate treated as observed, 20 times
    neg = 0
    for _ in range(20):
        L = shuf(lines, rng); E = shuf(es, rng)
        ps = [pval(s1(L), n1), pval(s2(E), n2), pval(s3(E), n3)]
        neg += any(r and mstar[H] for r, H in zip(holm(ps), ('H1', 'H2', 'H3')))
    out['negative_familywise'] = neg; out['negative_pass'] = neg <= 2; print('NEGATIVE', neg, '/20')
    obs = {'H1': s1(lines), 'H2': s2(es), 'H3': s3(es)}
    ps = [pval(obs[H], nulls[H]) for H in ('H1', 'H2', 'H3')]; rej = holm(ps); res = {}
    for (H, p), r in zip(zip(('H1', 'H2', 'H3'), ps), rej):
        if not out['negative_pass']: v = 'NOT TESTABLE (negative control failed)'
        elif mstar[H] is None: v = 'NOT TESTABLE'
        else: v = 'DETECTED' if r else 'NOT DETECTED'
        nm = sum(nulls[H]) / R
        res[H] = dict(obs=obs[H], null_mean=round(nm, 2), null_max=max(nulls[H]), excess=round(obs[H] - nm, 2),
                      p=p, mstar=mstar[H], verdict=v)
        print('RESULT', H, res[H])
    out['results'] = res
    json.dump(out, open(op, 'w'), indent=1)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
