#!/usr/bin/env python3
"""PE012 independent recount: rebuilds the H1/H2 sets, labels and the two observed statistics from the raw pinned
pe.atf with its own parser and literal factor tables (imports nothing from tools/). Usage (from
expeditions/proto-elamite/):  python3 tools/pe012_recount.py [--counts-only]
"""
import math, re, sys
from collections import Counter, defaultdict
TB = {"S": {"N01": 1, "N14": 10, "N34": 60, "N45": 600, "N48": 3600},
      "D": {"N01": 1, "N14": 10, "N23": 100, "N51": 1000, "N54": 10000},
      "B": {"N01": 1, "N14": 10, "N34": 60, "N51": 120, "N54": 1200},
      "C": {"N39C": 1, "N30D": 2, "N30C": 4, "N24": 12, "N39B": 24, "N01": 120, "N14": 720, "N45": 7200,
            "N34": 21600, "N48": 216000}}
ALL = set().union(*TB.values())
def ok(c, t):
    vs = sorted(set(t.values()))
    for s, k in c.items():
        if s not in t: return False
        hi = [v for v in vs if v > t[s]]
        if hi and k > hi[0] // t[s] - 1: return False
    return True
def cls(c):
    r = {x for x, t in TB.items() if ok(c, t)}
    a, b = "C" in r, bool(r - {"C"})
    return "C" if a and not b else "I" if b and not a else None
def size(c):
    s = set(c)
    if s & {"N34", "N45", "N48", "N23", "N51", "N54"}: return 3
    return 2 if "N14" in s else 1 if "N01" in s else 0
rows = []
for blk in open("data/pe.atf").read().split("\n\n"):
    blk = blk.strip()
    if not blk.startswith("&P"): continue
    L = [x.strip() for x in blk.split("\n")]; pid = L[0].split()[0][1:]
    surf = None; first = None; ents = []; key = None
    for i, l in enumerate(L):
        if l.startswith("@"):
            w = l.split()[0]
            surf = "o" if w == "@obverse" else "r" if w == "@reverse" else surf if w in ("@column", "@tablet", "@object", "@surface") else "x"
            continue
        m = re.match(r"^(\d+[A-Za-z]?)('?)\.\s*(.*)$", l)
        if surf != "o" or not m: continue
        if first is None:
            first = l
            if m.group(1) == "1" and not m.group(2) and i + 1 < len(L) and L[i + 1].startswith("# header"):
                body = m.group(3)
                if not re.search(r"\d+\(|n\(", body.split(",", 1)[1] if "," in body else ""):
                    tok = (body.split(",")[0].split() or [""])[0]
                    tok = re.sub(r"[\[\]#?!*]", "", tok)
                    if tok.startswith("|"): tok = re.split(r"[+.&x]", tok.strip("|"))[0]
                    tok = tok.split("~")[0]
                    if re.fullmatch(r"M\d+[a-z]?", tok): key = tok
            continue
        npart = m.group(3).rsplit(",", 1)[-1]
        npart2 = re.sub(r"\|[^|]*\|", "G", npart)
        nums = re.findall(r"(\d+|n)\(([^)]+)\)", npart2)
        if not nums: continue
        if re.search(r"[\[\]#?]|\.\.\.", npart): continue
        if any(n == "n" for n, _ in nums): continue
        c = Counter()
        for n, s in nums:
            s = re.sub(r"@[a-z]$", "", s); s = {"N1": "N01", "N8": "N08"}.get(s, s); c[s] += int(n)
        if set(c) <= ALL: ents.append(c)
    if key and ents:
        k = [cls(c) for c in ents]
        sy = "MIX" if "C" in k and "I" in k else "C" if "C" in k else "I" if "I" in k else None
        rows.append((pid, key, len(ents), sy, max(size(c) for c in ents)))
def keep(R): kc = Counter(r[1] for r in R); return [r for r in R if kc[r[1]] >= 3]
H1 = keep([r for r in rows if r[3]]); H2 = keep(rows)
print("eligible", len(rows), "H1 n", len(H1), "levels", len({r[1] for r in H1}), "H2 n", len(H2), "levels", len({r[1] for r in H2}))
print("H1 marginal", dict(Counter(r[3] for r in H1)), "H2 marginal", dict(Counter(r[4] for r in H2)))
if "--counts-only" in sys.argv: sys.exit()
O = Counter((r[1], r[3]) for r in H1); nk = Counter(r[1] for r in H1); nl = Counter(r[3] for r in H1); n = len(H1)
G = 2 * sum(o * math.log(o * n / (nk[k] * nl[l])) for (k, l), o in O.items())
m = sum(r[4] for r in H2) / len(H2); s = defaultdict(list)
for r in H2: s[r[1]].append(r[4])
SS = sum(len(v) * (sum(v) / len(v) - m) ** 2 for v in s.values())
print("H1 G", round(G, 4), "H2 SSB", round(SS, 4))
