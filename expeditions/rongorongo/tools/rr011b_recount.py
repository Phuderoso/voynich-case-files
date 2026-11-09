"""RR011b independent recount: K from the raw lines (own parser), side rates recounted from non-H/P/Q tablets, and p by
brute-force enumeration of all 2^n outcomes (no shared code with rr011b_loose_side.py).
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, sys, itertools, re
c = json.load(open(sys.argv[1])); res = json.load(open(sys.argv[2])); out = json.load(open(sys.argv[3]))
ST = ('001', '002', '003', '004', '009')
def norm(u): return [(re.match(r'\d+', p).group().zfill(3) if re.match(r'\d+', p) else None, any(ch in p for ch in '!?)')) for p in re.split('[.:]', u) if p]
def hostpos(ps):
    for i, (b, bad) in enumerate(ps):
        if b not in ST: return i if (b and not bad and b != '000') else None
def sides(u, w):
    ps = norm(u); h = hostpos(ps)
    if h is None: return None, set()
    return ps[h][0], {'B' if i < h else 'A' for i, (b, bad) in enumerate(ps) if b == w and not bad}
cnt = {}
for k, line in c.items():
    if k[0] in 'HPQ': continue
    for u in line:
        for w in ST:
            h, s = sides(u, w)
            if h and len(s) == 1: cnt.setdefault((w, h), []).append(s.pop())
probs = []; K = 0
for d in res['disagreement_list']:
    line = c[d['bare'][1]]; p = d['bare'][2]; want = set(d['want']); hit = {}
    for sd, q in (('B', p - 1), ('A', p + 1)):
        if 0 <= q < len(line):
            ps = norm(line[q])
            if ps and all(b in ST for b, _ in ps):
                s = {b for b, bad in ps if not bad} & want
                if s: hit[sd] = s
    if len(hit) != 1: continue
    sd, s = next(iter(hit.items()))
    if len(s) != 1: continue
    w = s.pop(); h, fs = sides(d['fused'][3], w)
    if len(fs) != 1: continue
    fs = fs.pop(); lst = cnt.get((w, h), [])
    if len(lst) < 5: lst = [x for (ww, _), v in cnt.items() if ww == w for x in v]
    rb = (lst.count('B') + 0.5) / (len(lst) + 1); probs.append(rb if fs == 'B' else 1 - rb); K += sd == fs
p = 0.0
for o in itertools.product((0, 1), repeat=len(probs)):
    if sum(o) >= K:
        q = 1.0
        for x, pi in zip(o, probs): q *= pi if x else 1 - pi
        p += q
print(dict(informative=len(probs), K=K, p=p, tool_K=out['K'], tool_p=out['p'], match=K == out['K'] and abs(p - out['p']) < 1e-12))
