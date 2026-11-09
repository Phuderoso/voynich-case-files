#!/usr/bin/env python3
"""PE013 - Subscripts (open line 5c): does the closing non-numeral line (the editors' '(subscript)') predict the number
system (H1) and the size (H2) of the obverse entries, and does it repeat the header (H3)?

Pre-registered in case-file/PE013-subscripts.md (committed with this tool, the label-free inventory and the rehearsal
on destroyed/planted data BEFORE any observed subscript-label or subscript-header association is computed). Usage (from
expeditions/proto-elamite/, after `python3 tools/pe001_totals.py fetch`):
    python3 tools/pe013_subscript.py inventory   # label-free: set sizes, key counts, label marginals, strata
    python3 tools/pe013_subscript.py rehearsal   # gates on destroyed/planted data, power curve, smoke run on shuffle 1399
    python3 tools/pe013_subscript.py test        # gates re-run (must reproduce), observed H1/H2/H3, Holm over the runnable tests
    python3 tools/pe013_subscript.py audit       # PE012 audit: H1 SYSTEM null re-drawn with new seed 1305, R 9999
Pure Python 3 (random.Random), exact integer counts.

SUBSCRIPT (editorial, fixed before looking): a numbered line immediately followed by the ATF translation comment
'#tr.en: (subscript)' (CDLI editors' own marking), no numeral on it (98 in the corpus, all numeral-free). Subscript KEY
= its first token normalised exactly as the PE012 header key: damage marks [ ] # ? ! * removed, |A+B...| -> A, variant
suffix ~x removed; 'x', '...' or anything not M<digits>[a-z]? -> no key.
ENTRIES / SYSTEM / SIZE: as PE012 (obverse numeral slots, numeral part intact, Englund S/D/B/C signs; SYSTEM C/I/MIX by
Born et al. bundling readings; SIZE 0 C fractions / 1 N01 / 2 N14 / 3 higher). Header line has no numeral so it is
never an entry. Tablets need >= 1 intact entry.
SETS: H1 = tablets with a subscript key and a SYSTEM label whose key occurs on >= 3 tablets of the set; H2 likewise
with SIZE. H3 = tablets with both a PE012 header key and a subscript key (no key-frequency filter).
STATISTICS: H1 G over subscript key x SYSTEM; H2 between-key SS of SIZE (PE012 functions). H3 M = number of tablets
whose subscript key equals their header key.
NULL: H1/H2 subscript keys permuted within strata (H1 entries bin; H2 entries bin x SYSTEM), as PE012. H3 subscript keys
permuted across the H3 tablets (header keys fixed), no strata. R 9999, seed 1301; p = (1 + #null >= obs)/(1 + R).
GATES: FPR 40 destroyed datasets, R 299, rate p <= 0.05 must be <= 0.10 (seed 1302). Power 100 datasets: destroy, then
H1/H2 plant 0.5 (PE012 rule: each key one target label, tablet takes it with prob 0.5); H3 plant 0.3 (each tablet's
subscript key is set to its header key with prob 0.3); R 299, rate p <= alpha/k must be >= 0.80, k = number of tests
that pass every gate (Holm's first level, conservative) (seed 1303). Size: H1/H2 >= 30 tablets in >= 3 keys; H3 >= 20.
VERDICTS: NOT TESTABLE (a gate fails; that test is NOT RUN on observed data) / SUPPORTED (Holm p <= 0.05) / NOT DETECTED.
"""
import json, os, re, sys, time, random
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe004_restore as Q, pe008_grain_totals as G
import pe011_closure_system as E
import pe012_header as H

R_NULL, SEED_NULL = 9999, 1301
N_FPR, R_IN, SEED_FPR, FPR_MAX = 40, 299, 1302, 0.10
N_POW, SEED_POW, POWER_MIN = 100, 1303, 0.80
PLANT = {"H1": 0.5, "H2": 0.5, "H3": 0.3}
SEED_CURVE, CURVE = 1304, (0.1, 0.2, 0.3, 0.5)
SEED_SHUFFLE, SEED_AUDIT = 1399, 1305
ALPHA, MIN_KEY = 0.05, 3
MIN_N = {"H1": 30, "H2": 30, "H3": 20}
TESTS = ("H1", "H2", "H3")

def norm(tok):
    tok = re.sub(r"[\[\]#?!*]", "", tok)
    if tok.startswith("|"): tok = re.split(r"[+.&x]", tok.strip("|"))[0]
    tok = re.sub(r"~.*$", "", tok)
    return tok if re.fullmatch(r"M\d+[a-z]?", tok) else None

def subscript_keys(path):
    keys, raw = {}, Counter()
    for d in open(path).read().split("\n\n"):
        d = d.strip()
        if not d.startswith("&P"): continue
        pid = d.split()[0][1:]; L = [x.strip() for x in d.split("\n")]
        for i, l in enumerate(L):
            if i + 1 < len(L) and L[i + 1].startswith("#tr.en: (subscript)") and re.match(r"^\d+'?\.\s", l):
                raw["subscript lines"] += 1
                if re.search(r"\d+\(|n\(", l): raw["with numeral (dropped)"] += 1; continue
                body = re.sub(r"^\d+'?\.\s*", "", l).split(",")[0].strip(); t = body.split()
                k = norm(t[0]) if t else None
                if k is None: raw["no key (first token unreadable)"] += 1; continue
                if pid in keys: raw["second subscript on tablet (first kept)"] += 1; continue
                keys[pid] = k
    return keys, raw

def build():
    path = os.path.join("data", "pe.atf"); tabs = Q.parse(path)
    sk, raw = subscript_keys(path); hk = H.header_keys(path); rows = []; why = Counter()
    for t in tabs:
        k = sk.get(t["pid"])
        if not k: continue
        ents = [c for c in (H.entry_ok(l) for l in t["lines"] if l["surf"] == "o" and l["nums"]) if c is not None]
        cl = [E.cls2(E.readings(c, E.ENG)) for c in ents]; hasC, hasI = "C" in cl, "I" in cl
        sysl = "MIX" if hasC and hasI else "C" if hasC else "I" if hasI else None
        rows.append({"pid": t["pid"], "key": k, "head": hk.get(t["pid"]), "n": len(ents), "sys": sysl,
                     "size": max(H.rank(c) for c in ents) if ents else None})
        if not ents: why["no intact entry"] += 1
    return rows, raw, why

def make(rows, test):
    if test == "H3":
        R = [r for r in rows if r["head"]]
        return [r["key"] for r in R], [r["head"] for r in R], [0] * len(R), [r["pid"] for r in R]
    R = [r for r in rows if r["n"] > 0]
    if test == "H1":
        R = [r for r in R if r["sys"]]; lab = lambda r: r["sys"]; st = lambda r: H.lenbin(r["n"])
    else:
        lab = lambda r: r["size"]; st = lambda r: (H.lenbin(r["n"]), str(r["sys"]))
    kc = Counter(r["key"] for r in R); R = [r for r in R if kc[r["key"]] >= MIN_KEY]
    return [r["key"] for r in R], [lab(r) for r in R], [st(r) for r in R], [r["pid"] for r in R]

def match(keys, heads): return sum(a == b for a, b in zip(keys, heads))
STAT = {"H1": H.gstat, "H2": H.ssb, "H3": match}

def null_p(test, keys, labs, pm, R, rng):
    f = STAT[test]; obs = f(keys, labs); ge = 0; nl = []
    for _ in range(R):
        v = f(pm.shuffle(keys, rng), labs); nl.append(v); ge += v >= obs - 1e-9
    return obs, (1 + ge) / (1 + R), nl

def plant(test, keys, labs, f, rng):
    if test == "H3":   # subscript repeats the header with prob f (labs = header keys)
        return [h if rng.random() < f else k for k, h in zip(keys, labs)], labs
    return keys, H.plant(keys, labs, f, rng)

def size_ok(test, keys):
    return len(keys) >= MIN_N[test] and (test == "H3" or len(set(keys)) >= 3)

def gates(rows):
    out = {}
    pre = {t: size_ok(t, make(rows, t)[0]) for t in TESTS}
    k = max(1, sum(pre.values()))
    for test in TESTS:
        keys, labs, st, _ = make(rows, test); pm = H.Perm(st); t0 = time.time(); off = TESTS.index(test) * 10000
        if not pre[test]:
            out[test] = {"n": len(keys), "levels": len(set(keys)), "size_ok": False, "FPR": None, "power": None,
                         "FPR_ok": False, "power_ok": False}
            print(test, out[test], flush=True); continue
        rng = random.Random(SEED_FPR + off); fp = 0
        for _ in range(N_FPR): fp += null_p(test, pm.shuffle(keys, rng), labs, pm, R_IN, rng)[1] <= ALPHA
        rng = random.Random(SEED_POW + off); hit = 0
        for _ in range(N_POW):
            kd = pm.shuffle(keys, rng); kp, lp = plant(test, kd, labs, PLANT[test], rng)
            hit += null_p(test, kp, lp, pm, R_IN, rng)[1] <= ALPHA / k
        out[test] = {"n": len(keys), "levels": len(set(keys)), "FPR": fp / N_FPR, "FPR_ok": fp / N_FPR <= FPR_MAX,
                     "power": hit / N_POW, "power_ok": hit / N_POW >= POWER_MIN, "size_ok": True, "alpha_power": ALPHA / k,
                     "seconds": round(time.time() - t0, 1)}
        print(test, out[test], flush=True)
    return out

def inventory():
    rows, raw, why = build()
    out = {"subscript_parse": dict(raw), "tablets_with_subscript_key": len(rows), "excluded_by": dict(why),
           "subscript_key_counts_all": dict(Counter(r["key"] for r in rows).most_common()),
           "with_header_key": sum(1 for r in rows if r["head"])}
    for test in TESTS:
        keys, labs, st, pids = make(rows, test)
        d = {"n": len(keys), "levels": len(set(keys)), "key_counts": dict(Counter(keys).most_common()), "pids": pids}
        if test != "H3":
            d["label_marginal"] = {str(x): v for x, v in Counter(labs).items()}
            d["strata"] = {str(x): v for x, v in Counter(st).items()}
        else:
            d["header_key_counts"] = dict(Counter(labs).most_common())
        out[test] = d
    json.dump(out, open("analysis/pe013_inventory.json", "w"), indent=1)
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "pids"} if isinstance(v, dict) else v) for k, v in out.items()}, indent=1))

def rehearsal():
    t0 = time.time(); rows, *_ = build(); g = gates(rows); out = {"gates": g}; curve = {}
    for test in TESTS:
        if not g[test]["size_ok"]: continue
        keys, labs, st, _ = make(rows, test); pm = H.Perm(st); curve[test] = {}
        for f in CURVE:
            rng = random.Random(SEED_CURVE + int(f * 100) + TESTS.index(test) * 10000); hit = 0
            for _ in range(40):
                kd = pm.shuffle(keys, rng); kp, lp = plant(test, kd, labs, f, rng)
                hit += null_p(test, kp, lp, pm, R_IN, rng)[1] <= g[test]["alpha_power"]
            curve[test][str(f)] = hit / 40
    out["power_curve_40"] = curve; smoke = {}
    for test in TESTS:
        if not g[test]["size_ok"]: continue
        keys, labs, st, _ = make(rows, test); pm = H.Perm(st)
        ks = pm.shuffle(keys, random.Random(SEED_SHUFFLE))
        obs, p, nl = null_p(test, ks, labs, pm, R_NULL, random.Random(SEED_NULL))
        smoke[test] = {"stat_on_registered_shuffle": round(obs, 4), "p": p, "null_mean": round(sum(nl) / len(nl), 4)}
    out["smoke_registered_shuffle_1399"] = smoke; out["runtime_s"] = round(time.time() - t0, 1)
    json.dump(out, open("analysis/pe013_rehearsal.json", "w"), indent=1); print(json.dumps(out, indent=1))

def test():
    t0 = time.time(); rows, *_ = build(); g = gates(rows); res = {}; run = []
    for test in TESTS:
        gg = g[test]
        if not (gg["size_ok"] and gg["FPR_ok"] and gg["power_ok"]):
            res[test] = {"n": gg["n"], "status": "NOT RUN (gate failed)"}; continue
        keys, labs, st, pids = make(rows, test); pm = H.Perm(st)
        obs, p, nl = null_p(test, keys, labs, pm, R_NULL, random.Random(SEED_NULL + TESTS.index(test) * 10000)); nl.sort()
        res[test] = {"n": len(keys), "levels": len(set(keys)), "stat": round(obs, 4), "null_mean": round(sum(nl) / len(nl), 4),
                     "null_q95": round(nl[int(0.95 * len(nl))], 4), "null_max": round(nl[-1], 4), "p": p}; run.append(test)
    adj = G.holm([res[t]["p"] for t in run]) if run else []; verdict = {}
    for test in TESTS:
        if test in run:
            a = adj[run.index(test)]; res[test]["p_holm"] = a
            verdict[test] = "SUPPORTED" if a <= ALPHA else "NOT DETECTED"
        else: verdict[test] = "NOT TESTABLE"
    desc = {}
    for test in TESTS:
        keys, labs, st, _ = make(rows, test); tab = defaultdict(Counter)
        for k, l in zip(keys, labs): tab[k][str(l)] += 1
        desc[test + "_table"] = {k: dict(v) for k, v in sorted(tab.items(), key=lambda kv: -sum(kv[1].values()))}
    out = {"verdicts": verdict, "results": res, "gates": g, "descriptive_no_decision_weight": desc,
           "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe013_results.json", "w"), indent=1); print(json.dumps(out, indent=1))

def audit():
    t0 = time.time(); rows, *_ = H.build(); keys, labs, st, _ = H.make(rows, "H1"); pm = H.Perm(st)
    obs, p, nl = H.null_p("H1", keys, labs, pm, 9999, random.Random(SEED_AUDIT))
    pub = json.load(open("analysis/pe012_results.json"))["results"]["H1"]
    out = {"PE012_H1_new_seed": SEED_AUDIT, "R": 9999, "n": len(keys), "G": round(obs, 4), "p": p,
           "null_mean": round(sum(nl) / len(nl), 4), "published": {k: pub[k] for k in ("n", "stat", "null_mean", "p")},
           "verdict_unchanged": len(keys) == pub["n"] and abs(obs - pub["stat"]) < 1e-3 and p > 0.05,
           "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe013_pe012_audit.json", "w"), indent=1); print(json.dumps(out, indent=1))

if __name__ == "__main__":
    {"inventory": inventory, "rehearsal": rehearsal, "test": test, "audit": audit}[sys.argv[1]]()
