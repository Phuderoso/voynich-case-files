#!/usr/bin/env python3
"""PE014 - Ratio accounts (open line 4): do paired numerical notations stand in exact small rational ratios more often
than under a structure-preserving shuffle null?

Pre-registered in case-file/PE014-ratio-accounts.md, committed with this tool, the label-free inventory and the rehearsal
on destroyed/planted data BEFORE any observed ratio is computed. Usage (from expeditions/proto-elamite/, after
`python3 tools/pe001_totals.py fetch`):
    python3 tools/pe014_ratio.py inventory   # label-free: set sizes, strata; no ratio is computed on observed data
    python3 tools/pe014_ratio.py rehearsal   # gates on destroyed/planted data (two independent power batches), curve, smoke
    python3 tools/pe014_ratio.py test        # gates re-run (must reproduce), observed statistics, Holm over runnable tests
    python3 tools/pe014_ratio.py audit       # PE013 audit: H3 REPEAT null re-drawn with new seed 1405, R 9999
Pure Python 3 (random.Random, fractions.Fraction): exact rational arithmetic, exact integer counts.

H1 IN-LINE (the literal reading of line 4: two notations inside one entry): a line (obverse or reverse) whose numeral
tokens, after compound graphemes |...| are collapsed (PE004 `outer`), form >= 2 maximal runs separated by a readable
token (a sign M..., or the comma), with no damage mark ([ ] # ? ...), no n(...), no 'x' on the line, every sign known.
PAIR = the first two runs. Size gate: >= 30 pairs, else NOT TESTABLE (dead on arrival; NOT RUN).
H2 ADJACENT (the corpus' own form of paired notations, Born et al. 2023 sec. 4.1.2 and App. A: one entry per notation, the
pair sits in consecutive entries): consecutive intact obverse entries (PE012 `entry_ok`, numeral-bearing obverse lines in
order, a damaged numeral line breaks the chain) on one tablet, BOTH notations INFORMATIVE (>= 2 distinct numeral signs,
so a small whole count like 2(N01) vs 1(N01) cannot carry the result). Tablets named in Born et al. 2023 for ratios
(P008212; P008791, P008796-P008802, P008804, P008805, P008810) are EXCLUDED (known results are not new; the full set
is reported descriptively after the decision).
VALUE of a notation: every reading the notation is valid in (PE011 `readings`, Englund S/D/B/C), each converted to
N01 units exactly (C fractions as Fractions of N01).
HIT: some pair of readings (one per notation) gives a ratio a/b in RSET = {p/q : 1 <= p, q <= 6, gcd 1, p != q}
(ratio 1 excluded: repeated notations are not ratio accounts). Statistic T = number of HIT pairs (H1 likewise).
NULL (structure-preserving): notations permuted across all slots of the set (H2 slots = every informative intact
obverse entry of the non-excluded tablets, paired or not; H1 slots = the two runs of each pair) within strata = (top sign, reading set,
number of distinct signs capped at 3) - order of magnitude, system ambiguity and notation complexity are kept, tablet
structure (chains, pair positions) kept; only which digits sit next to which changes. R 9999, seed 1401;
p = (1 + #null >= obs)/(1 + R), one-sided.
GATES: FPR on 40 destroyed datasets (one null shuffle each), R 299: rate p <= 0.05 must be <= 0.10 (seed 1402).
POWER (plant strength fixed by the effect of interest BEFORE gating: a ratio convention on 20 % of informative pairs,
Born's M056~f/M288 class is ~1 % of the corpus' pairs, so this is the smallest convention worth a corpus-wide claim):
destroy, then each pair with prob 0.2 gets its second notation replaced by the canonical notation (same system as a
reading of the first) of value(first) / r, r drawn from PLANT_R = (2, 3, 5/2, 3/2, 4, 1/2), if that value is
representable with >= 2 distinct signs (else left); R 299; rate p <= alpha/k must be >= 0.80 in BOTH independent
batches of 100 (seeds 1403 and 1404: C094/Kryptos I-182 second-batch rule), k = number of tests passing the size gate.
H2W WITHIN-TABLET CONFOUND CONTROL (second decision test): same pairs and statistic, but notations permuted only among
the informative slots of the SAME tablet (keeps each tablet's magnitudes, system and repertoire; only the order changes,
so a tablet whose entries are merely similar in size scores the same under the null). Two-slot tablets cannot move T
(RSET is closed under inversion), so the power comes from tablets with >= 3 informative entries. Gates as H2 (FPR and
two power batches on within-tablet-destroyed data). INTERPRETATION RULE (fixed now): "ratio accounts SUPPORTED" needs
H2 AND H2W Holm p <= 0.05; H2 alone = exact ratios beyond the magnitude-matched null but not beyond tablet-level
similarity (reported as such, no ratio-account claim); H2W alone = ordering effect without a corpus-level excess.
VERDICTS: NOT TESTABLE (a gate fails; NOT RUN on observed data) / SUPPORTED (Holm p <= 0.05) / NOT DETECTED.
"""
import json, os, re, sys, time, random
from fractions import Fraction as F
from math import gcd
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe004_restore as Q, pe001_totals as P
import pe011_closure_system as E
import pe012_header as H

R_NULL, SEED_NULL = 9999, 1401
N_FPR, R_IN, SEED_FPR, FPR_MAX = 40, 299, 1402, 0.10
N_POW, SEED_POW1, SEED_POW2, POWER_MIN, PLANT_F = 100, 1403, 1404, 0.80, 0.2
CURVE = (0.1, 0.2, 0.3, 0.5)
SEED_SHUFFLE, SEED_AUDIT = 1499, 1405
ALPHA = 0.05
MIN_N = {"H1": 30, "H2": 60, "H2W": 60}
TESTS = ("H1", "H2", "H2W")
BORN = {"P008212", "P008791", "P008796", "P008797", "P008798", "P008799", "P008800", "P008801", "P008802",
        "P008804", "P008805", "P008810"}
RSET = {F(p, q) for p in range(1, 7) for q in range(1, 7) if p != q and gcd(p, q) == 1}
PLANT_R = (F(2), F(3), F(5, 2), F(3, 2), F(4), F(1, 2))
CT = P.c_table(); C01 = CT["N01"]
TABLES = {k: ({s: F(v, C01) for s, v in t.items()} if k == "C" else {s: F(v) for s, v in t.items()}) for k, t in E.ENG.items()}
NUMTOK = re.compile(r"^(\d+)\(([^)]+)\)$")

_V, _HIT = {}, {}
def ck(c): return tuple(sorted(c.items()))
def values(c):
    k = ck(c)
    if k not in _V: _V[k] = {x: sum(TABLES[x][s] * n for s, n in c.items()) for x in E.readings(c, E.ENG)}
    return _V[k]

def hit(a, b):
    key = (ck(a), ck(b))
    if key not in _HIT:
        va, vb = values(a), values(b)
        _HIT[key] = any(x / y in RSET for x in va.values() for y in vb.values() if y)
    return _HIT[key]

ORDER = ["N48", "N45", "N34", "N54", "N51", "N23", "N14", "N01", "N39B", "N24", "N30C", "N30D", "N39C"]
def top(c): return min((ORDER.index(s) if s in ORDER else 99) for s in c)
def stratum(c): return (top(c), tuple(sorted(E.readings(c, E.ENG))), min(len(c), 3))
def informative(c): return len(c) >= 2

def canonical(v, sysk):
    tb = TABLES[sysk]; out = Counter(); rest = v
    for s in sorted(tb, key=lambda s: -tb[s]):
        if rest >= tb[s]:
            n = rest // tb[s]; out[s] = int(n); rest -= n * tb[s]
    if rest != 0 or not out: return None
    return out

# ---------------------------------------------------------------- sets
def inline_pairs(path):
    out, why = [], Counter()
    for d in open(path).read().split("\n\n"):
        d = d.strip()
        if not d.startswith("&P"): continue
        pid = d.split()[0][1:]
        for l in d.split("\n")[1:]:
            m = Q.LINE.match(l.strip())
            if not m: continue
            toks = Q.outer(m.group(3)).replace(",", " , ").split(); runs = []; cur = None
            for t in toks:
                mm = NUMTOK.match(t)
                if mm:
                    if cur is None: cur = Counter(); runs.append(cur)
                    cur[P.norm(mm.group(2))] += int(mm.group(1))
                else: cur = None
            if len(runs) < 2: continue
            why["lines with >= 2 numeral runs"] += 1
            if re.search(r"[\[\]#?]|\.\.\.|\bn\b|\bn\(|\bx\b", m.group(3)): why["damaged / n / x (dropped)"] += 1; continue
            if not all(set(r) <= H.KNOWN for r in runs[:2]): why["unknown sign (dropped)"] += 1; continue
            out.append({"pid": pid, "a": runs[0], "b": runs[1]})
    return out, why

def adjacent_pairs(tabs, exclude=BORN):
    slots, pairs, why, grp = [], [], Counter(), []
    for t in tabs:
        if t["pid"] in exclude: why["Born-named tablet (excluded)"] += 1; continue
        prev = None
        for l in t["lines"]:
            if l["surf"] != "o" or not (l["nums"] or l["dmg"]): continue
            c = H.entry_ok(l)
            if c is None or not informative(c):
                prev = None; continue
            slots.append(c); grp.append(t["pid"]); i = len(slots) - 1
            if prev is not None: pairs.append((prev, i))
            prev = i
    why["informative slots"] = len(slots); why["adjacent informative pairs"] = len(pairs)
    adjacent_pairs.grp = grp
    return slots, pairs, why

def build(test, tabs=None, exclude=BORN):
    """Return slots (notations), pairs (index pairs), strata."""
    if test == "H1":
        L, why = inline_pairs(os.path.join("data", "pe.atf")); slots = []; pairs = []
        for r in L: slots += [r["a"], r["b"]]; pairs.append((len(slots) - 2, len(slots) - 1))
        return slots, pairs, why
    tabs = tabs or Q.parse(os.path.join("data", "pe.atf"))
    slots, pairs, why = adjacent_pairs(tabs, exclude)
    return slots, pairs, why

def T(slots, pairs): return sum(hit(slots[i], slots[j]) for i, j in pairs)

class Shuf:
    def __init__(self, slots, test="H2"):
        self.pm = H.Perm(adjacent_pairs.grp if test == "H2W" else [stratum(c) for c in slots])
    def __call__(self, slots, rng): return self.pm.shuffle(slots, rng)

def null_p(slots, pairs, sh, R, rng):
    obs = T(slots, pairs); ge = 0; nl = []
    for _ in range(R):
        v = T(sh(slots, rng), pairs); nl.append(v); ge += v >= obs
    return obs, (1 + ge) / (1 + R), nl

def plant(slots, pairs, f, rng):
    s = slots[:]; planted = 0
    for i, j in pairs:
        if rng.random() >= f: continue
        r = rng.choice(PLANT_R); vs = values(s[i])
        if not vs: continue
        k = rng.choice(sorted(vs)); c = canonical(vs[k] / r, k)
        if c is None or not informative(c) or not set(c) <= H.KNOWN: continue
        s[j] = c; planted += 1
    return s, planted

def gates(cache):
    pre = {t: len(cache[t][1]) >= MIN_N[t] for t in TESTS}; k = max(1, sum(pre.values())); out = {}
    for test in TESTS:
        slots, pairs, _ = cache[test]; t0 = time.time()
        if not pre[test]:
            out[test] = {"pairs": len(pairs), "size_ok": False, "FPR": None, "power": None, "FPR_ok": False, "power_ok": False}
            print(test, out[test], flush=True); continue
        sh = Shuf(slots, test); off = TESTS.index(test) * 10000
        rng = random.Random(SEED_FPR + off); fp = 0
        for _ in range(N_FPR): fp += null_p(sh(slots, rng), pairs, sh, R_IN, rng)[1] <= ALPHA
        pw = []
        for seed in (SEED_POW1, SEED_POW2):
            rng = random.Random(seed + off); hits = 0; npl = 0
            for _ in range(N_POW):
                sp, n = plant(sh(slots, rng), pairs, PLANT_F, rng); npl += n
                hits += null_p(sp, pairs, sh, R_IN, rng)[1] <= ALPHA / k
            pw.append({"seed": seed + off, "power": hits / N_POW, "mean_planted_pairs": npl / N_POW})
        out[test] = {"pairs": len(pairs), "slots": len(slots), "size_ok": True, "FPR": fp / N_FPR, "FPR_ok": fp / N_FPR <= FPR_MAX,
                     "power_batches": pw, "power": min(b["power"] for b in pw),
                     "power_ok": all(b["power"] >= POWER_MIN for b in pw), "alpha_power": ALPHA / k,
                     "seconds": round(time.time() - t0, 1)}
        print(test, out[test], flush=True)
    return out

def all_sets():
    tabs = Q.parse(os.path.join("data", "pe.atf"))
    c = {t: build(t, tabs) for t in ("H1", "H2")}; c["H2W"] = c["H2"]
    return c, tabs

def inventory():
    cache, tabs = all_sets(); out = {}
    for t in ("H1", "H2"):
        slots, pairs, why = cache[t]
        out[t] = {"pairs": len(pairs), "slots": len(slots), "parse": dict(why),
                  "strata": len(set(stratum(c) for c in slots)),
                  "readings_marginal": dict(Counter(",".join(sorted(E.readings(c, E.ENG))) or "none" for c in slots))}
    full = build("H2", tabs, exclude=set())
    out["H2"]["full_set_incl_Born_pairs"] = len(full[1])
    out["H1"]["pids"] = sorted({r["pid"] for r in inline_pairs(os.path.join("data", "pe.atf"))[0]})
    json.dump(out, open("analysis/pe014_inventory.json", "w"), indent=1); print(json.dumps(out, indent=1))

def rehearsal():
    t0 = time.time(); cache, _ = all_sets(); g = gates(cache); out = {"gates": g}; curve = {}; smoke = {}
    for test in TESTS:
        if not g[test]["size_ok"]: continue
        slots, pairs, _ = cache[test]; sh = Shuf(slots, test); curve[test] = {}
        for f in CURVE:
            rng = random.Random(SEED_POW2 + 500 + int(f * 100) + TESTS.index(test) * 10000); h = 0
            for _ in range(40):
                sp, _n = plant(sh(slots, rng), pairs, f, rng); h += null_p(sp, pairs, sh, R_IN, rng)[1] <= g[test]["alpha_power"]
            curve[test][str(f)] = h / 40
        ss = sh(slots, random.Random(SEED_SHUFFLE)); obs, p, nl = null_p(ss, pairs, sh, 999, random.Random(SEED_NULL))
        smoke[test] = {"T_on_registered_shuffle_1499": obs, "p_R999": p, "null_mean": round(sum(nl) / len(nl), 3)}
    out["power_curve_40"] = curve; out["smoke_shuffle_1499"] = smoke; out["runtime_s"] = round(time.time() - t0, 1)
    json.dump(out, open("analysis/pe014_rehearsal.json", "w"), indent=1); print(json.dumps(out, indent=1))

def test():
    t0 = time.time(); cache, tabs = all_sets(); g = gates(cache); res = {}; run = []
    for test in TESTS:
        gg = g[test]
        if not (gg["size_ok"] and gg["FPR_ok"] and gg["power_ok"]):
            res[test] = {"pairs": gg["pairs"], "status": "NOT RUN (gate failed)"}; continue
        slots, pairs, _ = cache[test]; sh = Shuf(slots, test)
        obs, p, nl = null_p(slots, pairs, sh, R_NULL, random.Random(SEED_NULL + TESTS.index(test) * 10000)); nl.sort()
        res[test] = {"pairs": len(pairs), "T": obs, "null_mean": round(sum(nl) / len(nl), 3), "null_q95": nl[int(0.95 * len(nl))],
                     "null_max": nl[-1], "p": p}; run.append(test)
    import pe008_grain_totals as G
    adj = G.holm([res[t]["p"] for t in run]) if run else []; verdict = {}
    for test in TESTS:
        if test in run:
            a = adj[run.index(test)]; res[test]["p_holm"] = a; verdict[test] = "SUPPORTED" if a <= ALPHA else "NOT DETECTED"
        else: verdict[test] = "NOT TESTABLE"
    out = {"verdicts": verdict, "results": res, "gates": g, "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe014_results.json", "w"), indent=1); print(json.dumps(out, indent=1))

def audit():
    import pe013_subscript as S
    t0 = time.time(); rows, *_ = S.build(); keys, labs, st, _ = S.make(rows, "H3"); pm = H.Perm(st)
    obs, p, nl = S.null_p("H3", keys, labs, pm, 9999, random.Random(SEED_AUDIT))
    pub = json.load(open("analysis/pe013_results.json"))["results"]["H3"]
    out = {"PE013_H3_new_seed": SEED_AUDIT, "R": 9999, "n": len(keys), "M": obs, "p": p,
           "null_mean": round(sum(nl) / len(nl), 4), "published": {k: pub[k] for k in ("n", "stat", "null_mean", "p")},
           "exact_published": json.load(open("analysis/pe013_exact.json")) if os.path.exists("analysis/pe013_exact.json") else None,
           "verdict_unchanged": len(keys) == pub["n"] and obs == pub["stat"] and p > 0.05, "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe014_pe013_audit.json", "w"), indent=1); print(json.dumps(out, indent=1))

if __name__ == "__main__":
    {"inventory": inventory, "rehearsal": rehearsal, "test": test, "audit": audit}[sys.argv[1]]()
