#!/usr/bin/env python3
"""PE012 - Header structure (open line 5): does the sign of the editorial HEADER line predict the number system
(H1) and the size (H2) of the obverse entries?

Pre-registered in case-file/PE012-header-structure.md (committed with this tool, the label-free inventory and the
rehearsal on registered shuffles BEFORE any observed header-label association is computed). Usage (from
expeditions/proto-elamite/, after `python3 tools/pe001_totals.py fetch`):
    python3 tools/pe012_header.py inventory   # label-free: set sizes, header counts, label marginals, strata
    python3 tools/pe012_header.py rehearsal   # gates on destroyed/planted data + smoke run on registered shuffle 1299
    python3 tools/pe012_header.py test        # gates re-run (must reproduce), observed H1/H2, Holm over 2, verdicts
    python3 tools/pe012_header.py audit       # PE011 audit: H1 OBJECT null re-drawn with new seed 1205, R 9999
Pure Python 3 (random.Random), exact integer counts; G uses math.log on exact counts.

HEADER (editorial, fixed before looking): obverse line labelled '1.' immediately followed by the ATF comment
'# header' (the CDLI editors' own marking), with no numeral. Header KEY = first token of that line, damage marks
[ ] # ? ! * removed; a complex grapheme |A+B...| is reduced to its first component A; the variant suffix ~x is
removed (M157~a -> M157). Tokens 'x', '...' or not of the form M<digits> -> no header.
ENTRIES: obverse numeral slots other than the header line, numeral part intact (no [ ] # ? ...), no n(...),
every sign in Englund's tables S/D/B/C (PE001). Tablets need >= 1 such entry. Breaks elsewhere allowed.
LABELS: SYSTEM (H1) = C if >= 1 entry is valid with bundling only in C (Born et al. 2023 readings, as PE011) and
none only in S/D/B; I the reverse; MIX if both; none (excluded from H1) if every entry is ambiguous.
SIZE (H2) = largest unit order over the entries: 0 only C fractions (N39B N24 N30C N30D N39C), 1 N01, 2 N14,
3 anything higher (N34 N45 N48 N23 N51 N54).
SETS: H1 = tablets with a SYSTEM label whose header key occurs on >= 3 tablets of the H1 set (iterated once:
keys counted on the labelled set). H2 likewise with SIZE.
STATISTICS: H1 G = 2 sum O ln(O/E) over header key x SYSTEM. H2 between-header sum of squares
sum_h n_h (mean_h - mean)^2 of SIZE.
NULL (structure-preserving): header keys permuted across tablets WITHIN strata. H1 strata = number of entries
(1 / 2-3 / 4-7 / >= 8). H2 strata = number of entries x SYSTEM label (C/I/MIX/none), so H2 asks for size
information beyond the system. R = 9999, seed 1201; p = (1 + #null >= obs)/(1 + R); floor 1e-4.
GATES: FPR - 40 destroyed datasets (keys permuted within strata), R 299, rate p <= 0.05 must be <= 0.10 (seed
1202). Power - 100 datasets: destroy, then each header key gets one target label drawn from the set's labels and each
tablet (prob 0.5; 0.3 failed in rehearsal v1, disclosed) takes its key's target; R 299, rate p <= 0.025 (Holm level) must be >= 0.80 (seed 1203).
Size - >= 30 tablets in >= 3 header keys.
VERDICTS: NOT TESTABLE (a gate fails) / SUPPORTED (Holm p <= 0.05) / NOT DETECTED (powered, Holm p > 0.05).
"""
import json, math, os, re, sys, time, random
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe001_totals as P, pe004_restore as Q, pe008_grain_totals as G
import pe011_closure_system as E

R_NULL, SEED_NULL = 9999, 1201
N_FPR, R_IN, SEED_FPR, FPR_MAX = 40, 299, 1202, 0.10
N_POW, SEED_POW, PLANT, POWER_MIN = 100, 1203, 0.5, 0.80
SEED_CURVE, CURVE = 1204, (0.1, 0.2, 0.3, 0.5)
SEED_SHUFFLE, SEED_AUDIT = 1299, 1205
ALPHA, MIN_KEY, MIN_N, MIN_LEVELS = 0.05, 3, 30, 3
ALPHA_POW = ALPHA / 2
SUB = {"N39B", "N24", "N30C", "N30D", "N39C"}
HIGH = {"N34", "N45", "N48", "N23", "N51", "N54"}
KNOWN = set().union(*[set(t) for t in E.ENG.values()])

def header_keys(path):
    keys = {}
    for d in open(path).read().split("\n\n"):
        d = d.strip()
        if not d.startswith("&P"): continue
        pid = d.split()[0][1:]; L = [x.strip() for x in d.split("\n")]; surf = None
        for i, l in enumerate(L):
            if l.startswith("@obverse"): surf = "o"; continue
            if l.startswith("@reverse"): surf = "r"; continue
            if surf == "o" and re.match(r"^1\.\s", l):
                if i + 1 < len(L) and L[i + 1].startswith("# header"):
                    body = l[2:].strip(); head = body.split(",")[0].strip() if "," in body else body
                    if "," in body and re.search(r"\d+\(|n\(", body.split(",", 1)[1]): break
                    tok = head.split()[0] if head.split() else ""
                    tok = re.sub(r"[\[\]#?!*]", "", tok)
                    if tok.startswith("|"): tok = re.split(r"[+.&x]", tok.strip("|"))[0]
                    tok = re.sub(r"~.*$", "", tok)
                    if re.fullmatch(r"M\d+[a-z]?", tok): keys[pid] = tok
                break
    return keys

def entry_ok(l):
    if l["dmg"]: return None
    c = Q.notation(l["nums"])
    if c is None or not c or not set(c) <= KNOWN: return None
    return c

def rank(c):
    s = set(c)
    return 3 if s & HIGH else 2 if "N14" in s else 1 if "N01" in s else 0

def build():
    tabs = Q.parse(os.path.join("data", "pe.atf")); keys = header_keys(os.path.join("data", "pe.atf"))
    rows = []; why = Counter()
    for t in tabs:
        k = keys.get(t["pid"])
        if not k: why["no editorial header key"] += 1; continue
        ob = [l for l in t["lines"] if l["surf"] == "o"]
        o = [l for l in ob[1:] if l["nums"]]   # first obverse line = the header (no numeral)
        ents = [c for c in (entry_ok(l) for l in o) if c is not None]
        if not ents: why["no intact entry"] += 1; continue
        cl = [E.cls2(E.readings(c, E.ENG)) for c in ents]
        hasC, hasI = "C" in cl, "I" in cl
        sysl = "MIX" if hasC and hasI else "C" if hasC else "I" if hasI else None
        rows.append({"pid": t["pid"], "key": k, "n": len(ents), "sys": sysl, "size": max(rank(c) for c in ents)})
    return rows, why, len(tabs), len(keys)

def lenbin(n): return 0 if n == 1 else 1 if n <= 3 else 2 if n <= 7 else 3

def make(rows, test):
    if test == "H1":
        R = [r for r in rows if r["sys"]]; lab = lambda r: r["sys"]; st = lambda r: lenbin(r["n"])
    else:
        R = rows; lab = lambda r: r["size"]; st = lambda r: (lenbin(r["n"]), str(r["sys"]))
    kc = Counter(r["key"] for r in R); R = [r for r in R if kc[r["key"]] >= MIN_KEY]
    return [r["key"] for r in R], [lab(r) for r in R], [st(r) for r in R], [r["pid"] for r in R]

def gstat(keys, labs):
    O = Counter(zip(keys, labs)); nk = Counter(keys); nl = Counter(labs); n = len(keys); g = 0.0
    for (k, l), o in O.items(): g += o * math.log(o * n / (nk[k] * nl[l]))
    return 2 * g

def ssb(keys, labs):
    s = defaultdict(int); c = Counter(keys); n = len(keys); m = sum(labs) / n
    for k, l in zip(keys, labs): s[k] += l
    return sum(c[k] * (s[k] / c[k] - m) ** 2 for k in c)

STAT = {"H1": gstat, "H2": ssb}

class Perm:
    def __init__(self, strata):
        self.idx = defaultdict(list)
        for i, s in enumerate(strata): self.idx[s].append(i)
    def shuffle(self, keys, rng):
        out = keys[:]
        for ix in self.idx.values():
            sub = [keys[i] for i in ix]; rng.shuffle(sub)
            for i, x in zip(ix, sub): out[i] = x
        return out

def null_p(test, keys, labs, pm, R, rng):
    f = STAT[test]; obs = f(keys, labs); ge = 0; nl = []
    for _ in range(R):
        v = f(pm.shuffle(keys, rng), labs); nl.append(v); ge += v >= obs - 1e-9
    return obs, (1 + ge) / (1 + R), nl

def plant(keys, labs, f, rng):
    tgt = {k: rng.choice(labs) for k in sorted(set(keys))}
    return [tgt[k] if rng.random() < f else l for k, l in zip(keys, labs)]

def gates(rows):
    out = {}
    for test in ("H1", "H2"):
        keys, labs, st, _ = make(rows, test); pm = Perm(st); t0 = time.time()
        rng = random.Random(SEED_FPR + (0 if test == "H1" else 10000)); fp = 0
        for _ in range(N_FPR): fp += null_p(test, pm.shuffle(keys, rng), labs, pm, R_IN, rng)[1] <= ALPHA
        rng = random.Random(SEED_POW + (0 if test == "H1" else 10000)); hit = 0
        for _ in range(N_POW):
            kd = pm.shuffle(keys, rng); hit += null_p(test, kd, plant(kd, labs, PLANT, rng), pm, R_IN, rng)[1] <= ALPHA_POW
        n = len(keys); lv = len(set(keys))
        out[test] = {"n": n, "levels": lv, "FPR": fp / N_FPR, "FPR_ok": fp / N_FPR <= FPR_MAX, "power": hit / N_POW,
                     "power_ok": hit / N_POW >= POWER_MIN, "size_ok": n >= MIN_N and lv >= MIN_LEVELS,
                     "seconds": round(time.time() - t0, 1)}
        print(test, out[test], flush=True)
    return out

def inventory():
    rows, why, ntab, nkeys = build(); out = {"corpus_texts": ntab, "editorial_header_keys": nkeys, "eligible": len(rows),
                                             "excluded_by": dict(why)}
    for test in ("H1", "H2"):
        keys, labs, st, pids = make(rows, test)
        out[test] = {"n": len(keys), "levels": len(set(keys)), "key_counts": dict(Counter(keys).most_common()),
                     "label_marginal": {str(k): v for k, v in Counter(labs).items()},
                     "strata": {str(k): v for k, v in Counter(st).items()}, "pids": pids}
    json.dump(out, open("analysis/pe012_inventory.json", "w"), indent=1)
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "pids"} if isinstance(v, dict) else v) for k, v in out.items()}, indent=1))

def rehearsal():
    t0 = time.time(); rows, *_ = build(); out = {"gates": gates(rows)}
    curve = {}
    for test in ("H1", "H2"):
        keys, labs, st, _ = make(rows, test); pm = Perm(st); curve[test] = {}
        for f in CURVE:
            rng = random.Random(SEED_CURVE + int(f * 100) + (0 if test == "H1" else 10000)); hit = 0
            for _ in range(40):
                kd = pm.shuffle(keys, rng); hit += null_p(test, kd, plant(kd, labs, f, rng), pm, R_IN, rng)[1] <= ALPHA_POW
            curve[test][str(f)] = hit / 40
    out["power_curve_40"] = curve
    smoke = {}
    for test in ("H1", "H2"):
        keys, labs, st, _ = make(rows, test); pm = Perm(st)
        ks = pm.shuffle(keys, random.Random(SEED_SHUFFLE))
        obs, p, nl = null_p(test, ks, labs, pm, R_NULL, random.Random(SEED_NULL))
        smoke[test] = {"stat_on_registered_shuffle": round(obs, 4), "p": p, "null_mean": round(sum(nl) / len(nl), 4),
                       "null_q95": round(sorted(nl)[int(0.95 * len(nl))], 4)}
    out["smoke_registered_shuffle_1299"] = smoke; out["runtime_s"] = round(time.time() - t0, 1)
    json.dump(out, open("analysis/pe012_rehearsal.json", "w"), indent=1); print(json.dumps(out, indent=1))

def test():
    t0 = time.time(); rows, *_ = build(); g = gates(rows); res = {}
    for test in ("H1", "H2"):
        keys, labs, st, pids = make(rows, test); pm = Perm(st)
        obs, p, nl = null_p(test, keys, labs, pm, R_NULL, random.Random(SEED_NULL))
        nl.sort()
        res[test] = {"n": len(keys), "levels": len(set(keys)), "stat": round(obs, 4), "null_mean": round(sum(nl) / len(nl), 4),
                     "null_q95": round(nl[int(0.95 * len(nl))], 4), "null_max": round(nl[-1], 4), "p": p}
    adj = G.holm([res["H1"]["p"], res["H2"]["p"]]); verdict = {}
    for test, a in zip(("H1", "H2"), adj):
        gg = g[test]; res[test]["p_holm"] = a
        verdict[test] = ("NOT TESTABLE" if not (gg["FPR_ok"] and gg["power_ok"] and gg["size_ok"])
                         else "SUPPORTED" if a <= ALPHA else "NOT DETECTED")
    # descriptive after the decision: contingency tables per header key
    desc = {}
    for test in ("H1", "H2"):
        keys, labs, st, _ = make(rows, test); tab = defaultdict(Counter)
        for k, l in zip(keys, labs): tab[k][str(l)] += 1
        desc[test + "_table"] = {k: dict(v) for k, v in sorted(tab.items(), key=lambda kv: -sum(kv[1].values()))}
    out = {"verdicts": verdict, "results": res, "gates": g, "descriptive_no_decision_weight": desc,
           "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe012_results.json", "w"), indent=1); print(json.dumps(out, indent=1))

def audit():
    t0 = time.time(); _, _, D, _ = E.setup(); E.label_all(D); pr = E.pairs(D, "obj")
    r = E.one(pr, seed=SEED_AUDIT, R=9999); pub = json.load(open("analysis/pe011_results.json"))["results"]["H1_OBJECT"]
    out = {"PE011_H1_new_seed": SEED_AUDIT, "R": 9999, **r, "published": {k: pub[k] for k in ("n", "agree", "null_mean", "p")},
           "verdict_unchanged": r["agree"] == pub["agree"] and r["n"] == pub["n"] and r["p"] > 0.05,
           "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe012_pe011_audit.json", "w"), indent=1); print(json.dumps(out, indent=1))

if __name__ == "__main__":
    {"inventory": inventory, "rehearsal": rehearsal, "test": test, "audit": audit}[sys.argv[1]]()
