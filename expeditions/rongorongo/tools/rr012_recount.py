"""RR012 independent recount (own parser, no import of RR009/RR010/RR012 code): units, aligned pairs, eligible pairs,
disagreements D, S1, S2 and S1max for the (Gr, K = Kr+Kv) pair, from raw CEIPP lines. The alignment rule is the
registered one (difflib SequenceMatcher on host sequences, autojunk off, 'equal' blocks), re-coded here.
Usage: python3 rr012_recount.py corpus.json [tool_results.json]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys, difflib
ST = {1, 2, 3, 4, 9}
def parts(u):
    out = []
    for c in filter(None, re.split(r'[.:]', u)):
        m = re.match(r'(\d+)', c)
        out.append((int(m.group(1)) if m else None, any(ch in c for ch in '!?)')))
    return out
def unit(u):
    host, fl = None, False
    for n, bad in parts(u):
        if n in ST:
            fl = fl or not bad
        elif host is None:
            if n is None or bad or n == 0: return None
            host = n
    return (host, fl) if host is not None else None
def free(u):
    ps = parts(u)
    if not ps or any(n not in ST for n, _ in ps): return None
    return {n for n, bad in ps if not bad}
def bound(u): return {n for n, bad in parts(u) if n in ST and not bad}
c = json.load(open(sys.argv[1]))
def seq(pref):
    out = []
    for k in sorted(k for k in c if k[:2] in pref):
        for p, u in enumerate(c[k]):
            x = unit(u)
            if x: out.append((x[0], x[1], k, p))
    return out
G, K = seq(('Gr',)), seq(('Kr', 'Kv'))
sm = difflib.SequenceMatcher(None, [x[0] for x in G], [x[0] for x in K], autojunk=False)
links = [(G[i + d], K[j + d]) for i, j, n in sm.get_matching_blocks() for d in range(n)]
elig = [(a, b) for a, b in links if a[1] or b[1]]
D = [(a, b) if a[1] else (b, a) for a, b in elig if a[1] != b[1]]
s1 = s2 = smax = 0
for f, b in D:
    want = bound(c[f[2]][f[3]]); line = c[b[2]]; p = b[3]
    nb = [free(line[q]) for q in (p - 1, p + 1) if 0 <= q < len(line)]; nb = [x for x in nb if x is not None]
    s2 += any(nb); s1 += any(x & want for x in nb)
    smax += any((free(u) or set()) & want for u in line)
out = dict(units={'Gr': len(G), 'K': len(K)}, aligned=len(links), eligible=len(elig), disagreements=len(D), S1max=smax)
if len(sys.argv) > 2:
    r = json.load(open(sys.argv[2])); out.update(S1=s1, S2=s2)
    keys = [k for k in out if k in r]; out['tool'] = {k: r[k] for k in keys}; out['match'] = all(out[k] == r[k] for k in keys)
print(out)
