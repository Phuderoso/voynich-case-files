"""RR004 - are bound (fused) free strokes host-selective?
Bound stroke = component with base 001,002,003,004,009 inside a compound unit (split on '.' and ':') that also holds
a non-stroke component; its host = the nearest non-stroke component in the same unit; side = stroke after (R) or
before (L) the host. Codes are normalised first (leading digit run padded to 3, so '4.120a' -> 004.120a; RR002/RR003
did not pad, audit A below). Copy tablets P, Q, K removed.
H1: MI(stroke type ; host base), hosts with >= 5 bound strokes kept, others pooled as 'other'.
H2: MI(stroke type ; side).
Null for both: stroke-type labels permuted among bound slots WITHIN each tablet (keeps every host's bound-stroke count,
every tablet's stroke mix, and the sides). R = 999, p = (1 + #null >= obs)/(R + 1), Holm over 2 at 0.05.
Power: on null replicates, m slots of one host (the most frequent host, then the 2nd) are re-set to the stroke type
that host uses least; m* = smallest m in the grid with power >= 0.80 at 0.025. Negative control: 20 fresh null
replicates scored as observed; family-wise rejections must be <= 2. Verdict NOT TESTABLE if m* is undefined or the
negative control fails. Audit A: RR003 statistics recomputed with padded codes (descriptive).
Seed 4004. Usage: python3 rr004_stroke_hosts.py corpus.json out.json
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, random, math
from collections import Counter, defaultdict
COPIES = ('P', 'Q', 'K'); R = 999; PLANTS = 100; STROKES = {'001', '002', '003', '004', '009'}
MGRID = [2, 4, 6, 8, 10, 15, 20, 30, 40, 60]

def pad(c):
    m = re.match(r'(\d+)(.*)', c)
    return (m.group(1).zfill(3) + m.group(2)) if m else c
def base(c):
    m = re.match(r'(\d{3})', c); return m.group(1) if m else None
def comps(u): return [pad(c) for c in re.split(r'[.:]', u) if c != '']

def slots(corpus, keys):
    out = []  # (tablet, stroke, host, side)
    for k in sorted(keys):
        for u in corpus[k]:
            cs = comps(u); bs = [base(c) for c in cs]
            if len(cs) < 2: continue
            isS = [b in STROKES and not re.search(r"[!?]", c) for c, b in zip(cs, bs)]
            if all(isS) or not any(isS): continue
            for i, s in enumerate(isS):
                if not s: continue
                left = next((j for j in range(i - 1, -1, -1) if not isS[j]), None)
                right = next((j for j in range(i + 1, len(cs)) if not isS[j]), None)
                if left is not None: h, side = bs[left], 'R'
                else: h, side = bs[right], 'L'
                out.append((k[0], bs[i], h or 'x', side))
    return out

def mi(pairs):
    n = len(pairs); a = Counter(x for x, _ in pairs); b = Counter(y for _, y in pairs); ab = Counter(pairs)
    return sum(c / n * math.log2(c * n / (a[x] * b[y])) for (x, y), c in ab.items())

class Data:
    def __init__(self, sl):
        hc = Counter(h for _, _, h, _ in sl)
        self.keep = {h for h, c in hc.items() if c >= 5}
        self.tab = [t for t, _, _, _ in sl]; self.st = [s for _, s, _, _ in sl]
        self.host = [h if h in self.keep else 'other' for _, _, h, _ in sl]; self.side = [d for _, _, _, d in sl]
        self.groups = defaultdict(list)
        for i, t in enumerate(self.tab): self.groups[t].append(i)
    def perm(self, st, rng):
        o = list(st)
        for idx in self.groups.values():
            v = [st[i] for i in idx]; rng.shuffle(v)
            for i, x in zip(idx, v): o[i] = x
        return o
    def stats(self, st): return mi(list(zip(st, self.host))), mi(list(zip(st, self.side)))

def pval(o, null): return (1 + sum(1 for x in null if x >= o - 1e-12)) / (len(null) + 1)
def holm(ps, a=0.05):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); rej = [False] * len(ps)
    for r, i in enumerate(o):
        if ps[i] <= a / (len(ps) - r): rej[i] = True
        else: break
    return rej

def plant(D, st, m, rng, which):
    hosts = Counter(h for h in D.host if h != 'other').most_common()
    h = hosts[which][0]
    idx = [i for i, x in enumerate(D.host) if x == h]
    use = Counter(st[i] for i in idx); target = min(sorted(STROKES), key=lambda s: use.get(s, 0))
    cand = [i for i in idx if st[i] != target]; rng.shuffle(cand)
    o = list(st)
    for i in cand[:m]: o[i] = target
    return o, min(m, len(cand))

def rr003_audit(corpus, keys):
    def is_stroke(u): return not re.search(r"[.:;'!?]", u) and re.match(r'00[12349]', pad(u)) is not None
    old = lambda u: not re.search(r"[.:;'!?]", u) and re.match(r'00[12349]', u) is not None
    lines = [corpus[k] for k in sorted(keys)]
    n_old = sum(old(u) for l in lines for u in l); n_new = sum(is_stroke(u) for l in lines for u in l)
    adj_old = sum(1 for l in lines for a, b in zip(l, l[1:]) if old(a) and old(b))
    adj_new = sum(1 for l in lines for a, b in zip(l, l[1:]) if is_stroke(a) and is_stroke(b))
    return dict(free_strokes_rr003=n_old, free_strokes_padded=n_new, adjacent_pairs_rr003=adj_old, adjacent_pairs_padded=adj_new)

def main(cp, op, sizes_only=False):
    corpus = json.load(open(cp)); rng = random.Random(4004)
    keys = [k for k in corpus if k[0] not in COPIES]
    sl = slots(corpus, keys); D = Data(sl)
    out = {'seed': 4004, 'R': R, 'n_bound': len(sl), 'stroke_counts': dict(Counter(D.st)),
           'hosts_kept': len(D.keep), 'host_counts': dict(Counter(D.host).most_common()),
           'side_counts': dict(Counter(D.side)), 'tablets': dict(Counter(D.tab)), 'audit_RR003': rr003_audit(corpus, keys)}
    print('SIZES', json.dumps(out))
    if sizes_only: return
    nulls = [D.stats(D.perm(D.st, rng)) for _ in range(R)]
    n1 = [a for a, _ in nulls]; n2 = [b for _, b in nulls]
    pw = {'H1': [], 'H1_host2': []}
    for name, which in (('H1', 0), ('H1_host2', 1)):
        for m in MGRID:
            hit = 0; got = []
            for _ in range(PLANTS):
                P, d = plant(D, D.perm(D.st, rng), m, rng, which); got.append(d)
                hit += pval(D.stats(P)[0], n1) <= 0.025
            pw[name].append((m, hit / PLANTS, min(got)))
        print('POWER', name, pw[name])
    # H2 plant: m slots of the commonest stroke type on side L flipped to stroke type rarest on L
    pw['H2'] = []
    Lidx = [i for i, s in enumerate(D.side) if s == 'L']
    for m in MGRID:
        hit = 0; got = []
        for _ in range(PLANTS):
            st = D.perm(D.st, rng); use = Counter(st[i] for i in Lidx)
            tgt = min(sorted(STROKES), key=lambda s: use.get(s, 0)); cand = [i for i in Lidx if st[i] != tgt]
            rng.shuffle(cand)
            for i in cand[:m]: st[i] = tgt
            got.append(min(m, len(cand))); hit += pval(D.stats(st)[1], n2) <= 0.025
        pw['H2'].append((m, hit / PLANTS, min(got)))
    print('POWER H2', pw['H2'])
    out['power'] = pw
    mstar = {H: next((m for m, p, g in pw[H] if p >= 0.80 and g == m), None) for H in pw}
    out['mstar'] = mstar; print('MSTAR', mstar)
    neg = 0
    for _ in range(20):
        s = D.perm(D.st, rng); a, b = D.stats(s)
        neg += any(holm([pval(a, n1), pval(b, n2)]))
    out['negative_familywise'] = neg; out['negative_pass'] = neg <= 2; print('NEGATIVE', neg, '/20')
    oa, ob = D.stats(D.st); ps = [pval(oa, n1), pval(ob, n2)]; rej = holm(ps); res = {}
    for H, o, null, p, r, ms in (('H1', oa, n1, ps[0], rej[0], mstar['H1']), ('H2', ob, n2, ps[1], rej[1], mstar['H2'])):
        if not out['negative_pass']: v = 'NOT TESTABLE (negative control failed)'
        elif ms is None: v = 'NOT TESTABLE'
        else: v = 'DETECTED' if r else 'NOT DETECTED'
        res[H] = dict(obs=round(o, 4), null_mean=round(sum(null) / R, 4), null_max=round(max(null), 4), p=p, mstar=ms, verdict=v)
        print('RESULT', H, res[H])
    out['results'] = res
    # descriptive table: stroke x host counts for kept hosts
    tab = defaultdict(Counter)
    for s, h in zip(D.st, D.host): tab[h][s] += 1
    out['table'] = {h: dict(c) for h, c in tab.items()}
    json.dump(out, open(op, 'w'), indent=1)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sizes_only=len(sys.argv) > 3)
