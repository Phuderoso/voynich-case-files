"""RR014 independent recount (own parser, own run finder by dynamic programming; no import of RR009/RR010/RR014
code): side pairs, passages (maximal exact common host runs >= 5), aligned links, eligible links, disagreements D,
relevant bare lines, free strokes there, and (only with --observed) S1, S2.
Usage: python3 rr014_recount.py corpus.json [--observed]
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04"""
import json, re, sys
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
        if n in ST: fl = fl or not bad
        elif host is None:
            if n is None or bad or n == 0: return None
            host = n
    return (host, fl) if host is not None else None
def free(u):
    ps = parts(u)
    if not ps or any(n not in ST for n, _ in ps): return None
    return {n for n, bad in ps if not bad}
def bound(u): return {n for n, bad in parts(u) if n in ST and not bad}
corpus = json.load(open(sys.argv[1])); obs = '--observed' in sys.argv
S = sorted({k[:2] for k in corpus}); seq = {}
for s in S:
    seq[s] = [(k, p, unit(u)) for k in sorted(k for k in corpus if k[:2] == s) for p, u in enumerate(corpus[k]) if unit(u)]
def ok(a, b):
    if a[0] == b[0]: return False
    for fam in ('HPQ', 'GK'):
        if a[0] in fam and b[0] in fam: return False
    return True
P = [(a, b) for i, a in enumerate(S) for b in S[i + 1:] if ok(a, b)]
npass = 0; links = []
for a, b in P:
    x = [t[2][0] for t in seq[a]]; y = [t[2][0] for t in seq[b]]; inrun = set()
    rows = [[0] * (len(y) + 1)]                      # rows[i][j] = common suffix length of x[:i], y[:j]
    for i in range(1, len(x) + 1):
        pr = rows[-1]; xi = x[i - 1]
        rows.append([0] + [pr[j - 1] + 1 if xi == y[j - 1] else 0 for j in range(1, len(y) + 1)])
    for i in range(1, len(x) + 1):
        for j in range(1, len(y) + 1):
            n = rows[i][j]
            if n >= 5 and (i == len(x) or j == len(y) or rows[i + 1][j + 1] == 0):   # run ends here: maximal
                npass += 1
                for d in range(n): inrun.add((i - 1 - d, j - 1 - d))
    links += [(a, i, b, j) for i, j in sorted(inrun)]
elig = [(a, i, b, j) for a, i, b, j in links if seq[a][i][2][1] or seq[b][j][2][1]]
D = []
for a, i, b, j in elig:
    fa, fb = seq[a][i][2][1], seq[b][j][2][1]
    if fa == fb: continue
    f, bare = (seq[a][i], seq[b][j]) if fa else (seq[b][j], seq[a][i])
    D.append((f, bare))
lines = sorted({bare[0] for _, bare in D})
nfree = sum(free(u) is not None for k in lines for u in corpus[k])
out = dict(side_pairs=len(P), passages=npass, aligned=len(links), eligible=len(elig), disagreements=len(D),
           relevant_lines=len(lines), free_strokes_in_relevant_lines=nfree)
if obs:
    s1 = s2 = 0
    for f, (k, p, _) in D:
        want = bound(corpus[f[0]][f[1]]); line = corpus[k]
        nb = [free(line[q]) for q in (p - 1, p + 1) if 0 <= q < len(line)]
        nb = [x for x in nb if x is not None]
        s1 += any(x & want for x in nb); s2 += any(len(x) > 0 for x in nb)
    out.update(S1=s1, S2=s2)
print(json.dumps(out))
