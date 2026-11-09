#!/usr/bin/env python3
"""PE013 exact recount of H3 REPEAT (written after the registered run; independent of the Monte Carlo null).
Under a uniform random permutation of the subscript keys over the H3 tablets (header keys fixed), the number M of
tablets with subscript key == header key has an exact distribution given by rook theory: the 'match board' is a
disjoint union of full blocks a_s x b_s (a_s tablets with header s, b_s tablets with subscript s); its rook numbers
r_j are the coefficients of prod_s sum_j C(a_s,j) C(b_s,j) j! x^j, and
    #perms with exactly k matches = sum_{j>=k} (-1)^(j-k) C(j,k) r_j (n-j)!.
Exact rational p = P(M >= observed). Also exact expectation E[M] = sum_s a_s b_s / n. Pure Python, Fractions.
Reads analysis/pe013_inventory.json (pids) and recomputes keys with its own small parser (no imports from tools/)."""
import json, re, math
from fractions import Fraction
from collections import Counter

def norm(tok):
    tok = re.sub(r"[\[\]#?!*]", "", tok)
    if tok.startswith("|"): tok = re.split(r"[+.&x]", tok.strip("|"))[0]
    tok = re.sub(r"~.*$", "", tok)
    return tok if re.fullmatch(r"M\d+[a-z]?", tok) else None

head, sub = {}, {}
for d in open("data/pe.atf").read().split("\n\n"):
    d = d.strip()
    if not d.startswith("&P"): continue
    pid = d.split()[0][1:]; L = [x.strip() for x in d.split("\n")]; surf = None; hd = False
    for i, l in enumerate(L):
        nxt = L[i + 1] if i + 1 < len(L) else ""
        if l.startswith("@obverse"): surf = "o"
        elif l.startswith("@reverse"): surf = "r"
        if not hd and surf == "o" and re.match(r"^1\.\s", l):
            hd = True
            if nxt.startswith("# header"):
                body = l[2:].strip()
                if not ("," in body and re.search(r"\d+\(|n\(", body.split(",", 1)[1])):
                    t = (body.split(",")[0].strip() if "," in body else body).split()
                    k = norm(t[0]) if t else None
                    if k: head[pid] = k
        if nxt.startswith("#tr.en: (subscript)") and re.match(r"^\d+'?\.\s", l) and pid not in sub:
            if re.search(r"\d+\(|n\(", l): continue
            t = re.sub(r"^\d+'?\.\s*", "", l).split(",")[0].split()
            k = norm(t[0]) if t else None
            if k: sub[pid] = k

inv = json.load(open("analysis/pe013_inventory.json"))["H3"]["pids"]
pids = [p for p in inv]
assert all(p in head and p in sub for p in pids)
n = len(pids); A = Counter(head[p] for p in pids); B = Counter(sub[p] for p in pids)
obs = sum(head[p] == sub[p] for p in pids)
poly = [1]
for s in set(A) & set(B):
    a, b = A[s], B[s]; blk = [math.comb(a, j) * math.comb(b, j) * math.factorial(j) for j in range(min(a, b) + 1)]
    new = [0] * (len(poly) + len(blk) - 1)
    for i, x in enumerate(poly):
        for j, y in enumerate(blk): new[i + j] += x * y
    poly = new
N = [sum((-1) ** (j - k) * math.comb(j, k) * poly[j] * math.factorial(n - j) for j in range(k, len(poly))) for k in range(len(poly))]
assert sum(N) == math.factorial(n)
pex = Fraction(sum(N[obs:]), math.factorial(n))
EM = Fraction(sum(A[s] * B[s] for s in set(A) & set(B)), n)
out = {"n": n, "observed_M": obs, "shared_keys": {s: [A[s], B[s]] for s in sorted(set(A) & set(B))},
       "exact_E_M": float(EM), "exact_P_M_ge_obs": float(pex),
       "exact_distribution": {k: float(Fraction(N[k], math.factorial(n))) for k in range(len(N))}}
json.dump(out, open("analysis/pe013_exact.json", "w"), indent=1); print(json.dumps(out, indent=1))
