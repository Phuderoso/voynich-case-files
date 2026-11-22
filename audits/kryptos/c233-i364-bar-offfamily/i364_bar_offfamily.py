#!/usr/bin/env python3
"""i364_bar_offfamily.py -- FROZEN tool for Voynich's I-364 / I-356 audit of Kryptos cycle 233.

Off-family check of the adopted case-218 NC bar (PREREG232 / PREREG233 Part B) on gn217 decrypts.
Two stages:
  check  <cycle233_dir>  : testability preconditions T1-T4 (FROZEN.txt). Reads only line TYPES and counts
                           (H / T lines, which scopes, how many null texts); never parses an NC value.
  test   <units.tsv>     : if T1-T4 hold, per-text false-pass rate of the bar on null texts
                           (columns: set text scope nq N nc), exact binomial vs 1/21, Wilson 95 %, distance, label.
  selftest               : synthetic checks of the bar, Wilson, binomial and labels.
No seed is used (exact binomial, no resampling).
-- Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
"""
import sys, os, re, math, json

A, B1, B2, C, K_TEXT = -6.8417, 0.0786, 0.00027, -0.0192, 0.879   # PREREG233 Part B, verbatim
TARGET = 1.0 / 21.0          # k_text = max over 20 calibration texts -> exchangeable new text exceeds w.p. 1/21
ALPHA = 0.05
MIN_NULLS = 12               # I-356: >= 12 fresh nulls
NQ_DOM, N_DOM = (10, 64), (10, 5.3e6)

def bar(nq, N):
    N = max(10.0, float(N)); x = math.log(N)
    return A + B1 * x + B2 * x * x + C * nq + K_TEXT

def in_domain(nq, N):
    return NQ_DOM[0] <= nq <= NQ_DOM[1] and max(10.0, N) <= N_DOM[1]

def wilson(x, n, z=1.959963984540054):
    if n == 0: return (0.0, 1.0)
    p = x / n; d = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - h) / d), min(1.0, (c + h) / d))

def binom_two_sided(x, n, p):
    """exact two-sided binomial p (sum of probabilities <= P(x), relative tolerance 1e-7)."""
    pm = [math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(n + 1)]
    return min(1.0, sum(q for q in pm if q <= pm[x] * (1 + 1e-7)))

def label(p, side_main, side_rep=None):
    """PREREG232 distance rule: d = alpha/p if rejected else p/alpha; 0.5 <= d <= 2 (i.e. p/alpha in [0.5, 2]) -> FRONTEIRA;
    robusto only if d >= 2 AND same side on the fresh-null replicate set."""
    rej = p <= ALPHA
    d = ALPHA / p if rej else p / ALPHA
    ratio = p / ALPHA
    if 0.5 <= ratio <= 2.0: lab = "FRONTEIRA"
    elif d >= 2.0 and side_rep is not None and side_rep == side_main: lab = "robusto"
    else: lab = "FRONTEIRA (no fresh replicate / side not kept)" if d >= 2.0 else "FRONTEIRA"
    return rej, d, ratio, lab

def verdict(x, n):
    lo, hi = wilson(x, n); p = binom_two_sided(x, n, TARGET)
    if p <= ALPHA: v = "LENIENT (false-pass rate above 1/21)" if x / n > TARGET else "STRICT (false-pass rate below 1/21)"
    else: v = "CONSISTENT with 1/21 (not rejected)"
    return dict(x=x, n=n, rate=x / n if n else None, wilson95=[lo, hi], p_binom=p, verdict=v,
                side=(1 if (n and x / n > TARGET) else -1))

def check(d):
    R = os.path.join(d, "R"); out = {"dir": d, "files": {}}
    for fn in sorted(os.listdir(R)):
        nh = nt = 0
        with open(os.path.join(R, fn), errors="replace") as f:
            for line in f:
                if line.startswith("H "): nh += 1
                elif line.startswith("T "): nt += 1
        out["files"][fn] = {"H_lines": nh, "T_lines": nt}
    texts = sorted({re.split(r"_", fn)[0] for fn in out["files"]})
    nulls = [t for t in texts if t.startswith("null")]
    nh_null = sum(v["H_lines"] for k, v in out["files"].items() if k.startswith("null"))
    # T1: a hit-rich crib-subset surrogate exists = a file/label marked as crib-subset; gn217 has no subset option,
    #     so any surrogate must appear as separately named files. Detected by name only.
    surro = [k for k in out["files"] if re.search(r"subset|surrog|crib\d|short", k, re.I)]
    out["T1_crib_subset_files"] = surro
    out["T1_pass"] = len(surro) > 0
    out["T2_null_texts"] = nulls; out["T2_pass"] = len(nulls) >= MIN_NULLS
    out["null_H_lines_total"] = nh_null
    out["T3_decrypt_material"] = "H lines carry indices only (perm dir ix X Y form w agree); NC needs alpha.bin/bank.bin/all.bin/themed144.bin/keys233.bin + quadgrams.json"
    out["T4_note"] = "N per scope = max(10, #H lines decrypted in that scope); available iff H lines exist"
    out["testable"] = bool(out["T1_pass"] and out["T2_pass"] and nh_null > 0)
    return out

def test(tsv):
    rows = [l.rstrip("\n").split("\t") for l in open(tsv) if l.strip() and not l.startswith("#")]
    sets = {}
    for s, t, sc, nq, N, nc in rows:
        nq, N, nc = int(nq), float(N), float(nc)
        if not in_domain(nq, N): continue
        sets.setdefault(s, {}).setdefault(t, False)
        if nc >= bar(nq, N): sets[s][t] = True
    res = {}
    for s, tx in sets.items(): res[s] = verdict(sum(tx.values()), len(tx))
    keys = sorted(res)
    if keys:
        m = res[keys[0]]; rep = res[keys[1]] if len(keys) > 1 else None
        rej, dist, ratio, lab = label(m["p_binom"], m["side"], rep["side"] if rep else None)
        res["_label"] = dict(main=keys[0], replicate=keys[1] if rep else None, rejected=rej, distance=dist, p_over_alpha=ratio, label=lab)
    return res

def selftest():
    ok = True
    def t(c, msg):
        nonlocal ok; print(("PASS " if c else "FAIL ") + msg); ok &= c
    t(abs(bar(11, 300) - (-6.8417 + 0.0786 * math.log(300) + 0.00027 * math.log(300) ** 2 - 0.0192 * 11 + 0.879)) < 1e-12, "bar formula verbatim")
    t(abs(bar(64, 10) - (-7.010)) < 0.0015, "most lenient bar at (nq 64, N 10) = -7.010 (case 218 recount)")
    t(bar(10, 1) == bar(10, 10), "N floor 10")
    lo, hi = wilson(0, 73); t(abs(hi - 0.0500) < 5e-4, "Wilson hi(0/73) = 0.0500")
    lo, hi = wilson(23, 24); t(abs(lo - 0.798) < 1e-3 and abs(hi - 0.993) < 1e-3, "Wilson 23/24 = 0.798-0.993")
    t(abs(binom_two_sided(1, 21, TARGET) - 1.0) < 1e-9, "binom 1/21 at target -> p 1")
    t(binom_two_sided(10, 21, TARGET) < 1e-4, "binom 10/21 rejects")
    t(label(0.08, 1, 1)[3] == "FRONTEIRA", "p/alpha 1.6 -> FRONTEIRA")
    t(label(0.001, 1, 1)[3] == "robusto" and label(0.001, 1, -1)[3] != "robusto", "robusto needs same side on replicate")
    t(label(0.5, -1, None)[3].startswith("FRONTEIRA"), "no replicate -> never robusto")
    print("SELFTEST", "ALL PASS" if ok else "FAILED"); return ok

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "selftest": sys.exit(0 if selftest() else 1)
    elif cmd == "check": print(json.dumps(check(sys.argv[2]), indent=1))
    elif cmd == "test": print(json.dumps(test(sys.argv[2]), indent=1))
