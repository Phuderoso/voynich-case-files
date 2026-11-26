#!/usr/bin/env python3
"""Blind check of Kryptos case 223 (cycle 237): look-and-say lengths S18 via
Conway's published 92-element table (Wikipedia 'Look-and-say sequence',
table 'All atomic elements', sourced there to Conway 1987 / Martin 2006).
Independent of her las_exact.py (never opened). Stdlib only.
Usage: s18_conway.py WIKI_RAW OEIS_BFILE KEYS237_TSV [KEYS237_BIN]
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI wrote this)."""
import sys, re, hashlib

def say(s):
    out = []; i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]: j += 1
        out.append(str(j - i)); out.append(s[i]); i = j
    return "".join(out)

def parse_table(raw):
    # rows between '|-' lines: number, symbol, sequence, decays, abundance
    t = raw[raw.index("All \"atomic elements\""):]
    t = t[:t.index("\n|}")]
    rows = [r.strip().split("\n") for r in t.split("\n|-")[2:]]
    el = {}
    for r in rows:
        cells = [c.lstrip("|").strip() for c in r if c.startswith("|")]
        if len(cells) < 4 or not cells[0].isdigit(): continue
        n, sym, seq, dec = int(cells[0]), cells[1], cells[2], cells[3]
        if n > 92 or not re.fullmatch(r"[123]+", seq): continue
        el[sym] = (n, seq, dec.split("."))
    return el

def main():
    raw = open(sys.argv[1], encoding="utf-8").read()
    el = parse_table(raw)
    print("TABLE elements parsed:", len(el), "sha256(raw):", hashlib.sha256(raw.encode()).hexdigest()[:16])
    assert len(el) == 92, "expected 92 elements"
    # T1: each element's look-and-say equals the concatenation of its decay products
    bad = [s for s, (n, q, d) in el.items() if say(q) != "".join(el[x][1] for x in d)]
    print("T1 decay identity failures:", len(bad), bad[:5])
    # direct strings to N0 for validation
    NDIR = 45
    strs = ["1"]
    while len(strs) < NDIR: strs.append(say(strs[-1]))
    # decompose term n0 into elements by DP (shortest-path over element strings)
    by_seq = {q: s for s, (n, q, d) in el.items()}
    def decompose(s):
        best = {0: []}
        for i in range(len(s)):
            if i not in best: continue
            for q, sy in by_seq.items():
                if s.startswith(q, i) and (i + len(q)) not in best:
                    best[i + len(q)] = best[i] + [sy]
        return best.get(len(s))
    n0 = None
    for cand in range(8, 30):
        dec = decompose(strs[cand - 1])
        if dec is None: continue
        # validate by evolving counts vs direct lengths to NDIR
        cnt = {}
        for sy in dec: cnt[sy] = cnt.get(sy, 0) + 1
        ok = True; c = dict(cnt)
        for n in range(cand, NDIR + 1):
            L = sum(k * len(el[sy][1]) for sy, k in c.items())
            if L != len(strs[n - 1]): ok = False; break
            nc = {}
            for sy, k in c.items():
                for x in el[sy][2]: nc[x] = nc.get(x, 0) + k
            c = nc
        if ok: n0 = cand; start = cnt; break
    print("T2 start term n0 =", n0, "elements:", sum(start.values()), "(lengths match direct strings for n0..%d)" % NDIR)
    NMAX = 3000
    S = [None, 1]
    for n in range(2, n0): S.append(len(strs[n - 1]))
    c = dict(start)
    for n in range(n0, NMAX + 1):
        S.append(sum(k * len(el[sy][1]) for sy, k in c.items()))
        nc = {}
        for sy, k in c.items():
            for x in el[sy][2]: nc[x] = nc.get(x, 0) + k
        c = nc
    # T3: fresh OEIS b-file
    b = {}
    for line in open(sys.argv[2]):
        p = line.split()
        if len(p) == 2 and not line.startswith("#"): b[int(p[0])] = int(p[1])
    common = [n for n in b if 1 <= n <= NMAX]
    mm = [n for n in common if b[n] != S[n]]
    print("T3 OEIS A005341 terms compared:", len(common), "mismatches:", len(mm), mm[:5])
    for n in (10, 42, 43, 100, 136): print("  S18(%d) = %d" % (n, S[n]))
    # windows per PREREG237 definition, in keys237.tsv order
    rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[3]) if l.strip()]
    W = []
    for a, name, o, cc, d in rows:
        a, o, cc = int(a), int(o), int(cc)
        if d == "fwd": v = [S[1 + o + i] + cc for i in range(97)]
        else: v = [S[1 + o + 96 - i] + cc for i in range(97)]
        W.append(bytes((a * (x % 26)) % 26 for x in v))
    blob = b"".join(W)
    print("WINDOWS", len(W), "blob sha256:", hashlib.sha256(blob).hexdigest())
    seats = list(range(21, 34)) + list(range(63, 74))
    sk = [bytes(w[s] for s in seats) for w in W]
    print("  windows constant on 24 seats:", sum(len(set(x)) == 1 for x in sk), "| distinct seat patterns:", len(set(sk)), "| distinct windows:", len(set(W)))
    if len(sys.argv) > 4:
        her = open(sys.argv[4], "rb").read()
        print("HER keys237.bin size", len(her), "sha256", hashlib.sha256(her).hexdigest())
        if len(her) == len(blob):
            diff = [i for i in range(len(W)) if her[97*i:97*i+97] != W[i]]
            print("COMPARE uint8 960x97 row-major: windows differing:", len(diff), diff[:10])
        else:
            print("COMPARE: size differs from 960x97 (layout to be read from her writer, disclosed)")

if __name__ == "__main__":
    main()
