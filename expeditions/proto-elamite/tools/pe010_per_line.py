#!/usr/bin/env python3
"""PE010 - Is the reverse number on grain (capacity, CAP) tablets a PER-LINE amount (one entry, the largest entry, or
the mean entry sum/n) rather than a total? Tested on FRESH tablets never used by PE004-PE009.

Pre-registered in case-file/PE010-per-line-grain.md (committed with this tool BEFORE any match, gate or null number on
these tablets was computed). Usage (from expeditions/proto-elamite/, after `python3 tools/pe001_totals.py fetch`):
    python3 tools/pe010_per_line.py inventory  # label-free: set sizes, eligibility, strata (entries/shape only)
    python3 tools/pe010_per_line.py gates      # FPR gate (stratified total permutation) + planted power gate
    python3 tools/pe010_per_line.py test       # T1-T3, Holm over 3, verdicts; descriptive/exposed sets after
    python3 tools/pe010_per_line.py audit      # PE009 audit (scratch re-run + independent re-count)
Pure Python 3 (random.Random), exact integer arithmetic in N39C units (Englund C table, N01 = 120).

READABLE numeral slot: intact, or damaged but COMPLETELY read by the editor (PE006 rule `pe006_cap.complete`).
CAP: a capacity sub-unit sign (N39B, N24, N30C, N30D, N39C) in any readable slot (PE005 definition).
EXCLUDED from both sets: every tablet of the PE004/PE005 intact set and of the PE006 fresh set (so PE009's A and B).
SETS (fixed before looking; membership uses shape and readability only, never a total-vs-entry comparison):
  D1 (single-total, fresh)  exactly 1 reverse numeral slot, readable and valid in C; >= 2 obverse slots; >= 2 readable
                            obverse entries valid in C (damaged-unread entries and broken/primed surfaces ALLOWED: the
                            entry list may be partial). Entries = readable C entries in order. complete = shape_ok
                            (no broken $-line, no primed line) and every obverse slot readable in C.
  D2 (multi-line reverse)   >= 2 reverse numeral slots, shape_ok, every obverse slot readable and valid in C (>= 2);
                            candidate total = the LAST reverse numeral slot, readable and valid in C.
  PE002 published (descriptively, all systems pooled) that 78-183 multi-line reverse lines equal a single obverse
  entry (lists continuing onto the reverse); hence ENTRY on D2 is EXPOSED and confounded -> descriptive only.
TESTS (Holm over 3 at 0.05):
  T1 ENTRY  on D1: value_C(total) == value_C(e) for some entry e.            eligible: all D1 (>= 2 entries)
  T2 MAX    on D2: value_C(total) == max entry value.                        eligible: all D2 (complete)
  T3 MEAN   on D2: the mean entry within one N39C, |n * value_C(total) - sum_C| < n (exact means included).
                                                                             eligible: all D2 (complete)
  (Exact MEAN, n * total == sum, is eligible on only 7 D2 tablets (< 8): descriptive only, declared here.)
Statistic: number of eligible tablets that match.
NULL (structure-preserving): totals permuted WITHIN magnitude strata = quartiles of the tablet's largest readable
  entry value (ties never split; 4 strata if the set has >= 40 tablets, else 2), so a total only moves to
  tablets of similar scale. R = 1999, seed 1001.
GATES (per test): FPR - 100 datasets with totals stratified-permuted, R = 299 each, rate p <= 0.05 must be <= 0.06
  (seed 1002). Power - 100 datasets, each eligible tablet (prob 0.5) gets total := canonical C notation of its own
  hypothesised quantity (T1 a random entry, T2 the max, T3 floor(sum/n)); R = 299; rate p <= 0.05/3 must be >= 0.80 (seed
  1003); plant 0.8 descriptive. Size >= 8 eligible.
VERDICTS: NOT TESTABLE (a gate fails) / NOT DETECTED (Holm p > 0.05) / EXCLUDED (NOT DETECTED and one-sided CP95
  upper bound of matched/eligible < 0.25) / SUPPORTED (gates pass, Holm p <= 0.05).
DESCRIPTIVE (no decision weight, after the test): T1 shifted control (total +/- one unit of its smallest sign);
  ENTRY on D2 (exposed); MAX/MEAN on complete D1; ENTRY/MAX/MEAN on PE009's exposed A (15) and B (25) with the same
  null; exact MEAN on D2.
"""
import json, os, sys, time, random, shutil, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe001_totals as P, pe004_restore as Q, pe006_cap as T, pe008_grain_totals as G

C = P.c_table(); SUB = P.C_SUB_SIGNS
R_NULL, SEED_NULL = 1999, 1001
N_FPR, R_IN, SEED_FPR = 100, 299, 1002
N_POW, SEED_POW, PLANT, PLANT_HI = 100, 1003, 0.5, 0.8
ALPHA, FPR_MAX, POWER_MIN, MIN_ELIG, EXCL_UB, N_STRATA = 0.05, 0.06, 0.80, 8, 0.25, 4
TESTS = (("T1_ENTRY", "D1", "ENTRY"), ("T2_MAX", "D2", "MAX"), ("T3_MEAN", "D2", "MEAN_ROUND"))
ALPHA_POW = ALPHA / len(TESTS)

def cv(c): return P.value(c, C) if Q.valid(c) else None

def readable(l): return T.complete(Q.numpart(l["body"])) if l["dmg"] else Q.notation(l["nums"])

def build_sets():
    tabs = Q.parse(os.path.join("data", "pe.atf"))
    used = {t["pid"] for t in Q.calibration_set(tabs)} | {t["pid"] for t in T.fresh_set(tabs)[0]}
    D1, D2 = [], []
    for t in tabs:
        if t["pid"] in used: continue
        o, r = Q.slots(t)
        if len(o) < 2 or not r: continue
        on = [readable(l) for l in o]; rn = [readable(l) for l in r]
        signs = set().union(*[set(c) for c in on + rn if c])
        if not signs & SUB: continue
        ents = [c for c in on if cv(c) is not None and cv(c) > 0]
        allread = len(ents) == len(o)
        if len(r) == 1:
            if cv(rn[0]) is None or len(ents) < 2: continue
            D1.append({"pid": t["pid"], "entries": ents, "total": rn[0], "complete": Q.shape_ok(t) and allread,
                       "n_slots": len(o)})
        else:
            if not (Q.shape_ok(t) and allread) or cv(rn[-1]) is None: continue
            D2.append({"pid": t["pid"], "entries": ents, "total": rn[-1], "complete": True, "n_slots": len(o),
                       "n_rev": len(r)})
    return {"D1": D1, "D2": D2}

def exposed_sets():
    S = G.target_sets()
    return {"A_PE009": [{**t, "complete": True} for t in S["R"]], "B_PE009": [{**t, "complete": True} for t in S["P"]]}

def vals(t): return [cv(e) for e in t["entries"]]

def eligible(t, h):
    vs = vals(t)
    if None in vs or len(vs) < 2: return False
    if h == "ENTRY": return True
    if not t["complete"]: return False
    if h in ("MAX", "MEAN_ROUND"): return True
    return sum(vs) % len(vs) == 0                         # exact MEAN (descriptive)

def match(t, total, h, shift=0):
    v = cv(total)
    if v is None: return False
    v += shift; vs = vals(t)
    if h == "ENTRY": return v in vs
    if h == "MAX": return v == max(vs)
    if h == "MEAN": return v * len(vs) == sum(vs)
    if h == "MEAN_ROUND": return abs(v * len(vs) - sum(vs)) < len(vs)   # |v - sum/n| < 1 N39C
    raise KeyError(h)

def strata(tabs):
    ns = N_STRATA if len(tabs) >= 40 else 2
    keys = [max(vals(t)) for t in tabs]; order = sorted(range(len(tabs)), key=lambda i: keys[i]); n = len(tabs)
    first = {}; g = [0] * n
    for rank, i in enumerate(order): first.setdefault(keys[i], rank)
    for i in range(n): g[i] = min(ns - 1, first[keys[i]] * ns // n)
    return g

def stat(tabs, h, totals=None, shift=0):
    return sum(match(t, t["total"] if totals is None else totals[i], h, shift)
               for i, t in enumerate(tabs) if eligible(t, h))

def shuffle_within(tots, g, rng):
    out = tots[:]
    for s in set(g):
        idx = [i for i in range(len(g)) if g[i] == s]; sub = [tots[i] for i in idx]; rng.shuffle(sub)
        for i, x in zip(idx, sub): out[i] = x
    return out

def null_p(tabs, h, R, rng):
    g = strata(tabs); obs = stat(tabs, h); tots = [t["total"] for t in tabs]; ge = 0; nl = []
    for _ in range(R):
        m = stat(tabs, h, shuffle_within(tots, g, rng)); nl.append(m); ge += m >= obs
    return obs, (1 + ge) / (1 + R), nl

def destroy(tabs, rng):
    tots = shuffle_within([t["total"] for t in tabs], strata(tabs), rng)
    return [{**t, "total": x} for t, x in zip(tabs, tots)]

def plant(tabs, h, rng, prob):
    out = []
    for t in tabs:
        tot = t["total"]
        if eligible(t, h) and rng.random() < prob:
            vs = vals(t)
            v = vs[rng.randrange(len(vs))] if h == "ENTRY" else max(vs) if h == "MAX" else sum(vs) // len(vs)
            x = P.canonical(v, C)
            if x: tot = x
        out.append({**t, "total": tot})
    return out

def inventory():
    S = build_sets(); out = {}
    for name, tabs in S.items():
        g = strata(tabs)
        out[name] = {"tablets": len(tabs), "eligible": {h: sum(eligible(t, h) for t in tabs) for h in ("ENTRY", "MAX", "MEAN_ROUND", "MEAN")},
                     "complete": sum(t["complete"] for t in tabs),
                     "entries_per_tablet": sorted(len(t["entries"]) for t in tabs),
                     "stratum_sizes": [g.count(s) for s in sorted(set(g))], "pids": [t["pid"] for t in tabs]}
    json.dump(out, open("analysis/pe010_inventory.json", "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "pids"} for k, v in out.items()}, indent=1))

def gates():
    t0 = time.time(); S = build_sets(); out = {}
    for tid, sname, h in TESTS:
        tabs = S[sname]; ne = sum(eligible(t, h) for t in tabs)
        rng = random.Random(SEED_FPR); fp = 0
        for _ in range(N_FPR): fp += null_p(destroy(tabs, rng), h, R_IN, rng)[1] <= ALPHA
        rng = random.Random(SEED_POW); hit = hit_hi = 0
        for _ in range(N_POW): hit += null_p(plant(tabs, h, rng, PLANT), h, R_IN, rng)[1] <= ALPHA_POW
        for _ in range(N_POW // 2): hit_hi += null_p(plant(tabs, h, rng, PLANT_HI), h, R_IN, rng)[1] <= ALPHA_POW
        out[tid] = {"set": sname, "eligible": ne, "FPR": fp / N_FPR, "FPR_ok": fp / N_FPR <= FPR_MAX,
                    "power_p05": hit / N_POW, "power_ok": hit / N_POW >= POWER_MIN,
                    "power_p08_descriptive": hit_hi / (N_POW // 2), "size_ok": ne >= MIN_ELIG}
        print(tid, out[tid], round(time.time() - t0, 1), flush=True)
    out["params"] = {"N_FPR": N_FPR, "R_IN": R_IN, "SEED_FPR": SEED_FPR, "N_POW": N_POW, "SEED_POW": SEED_POW,
                     "PLANT": PLANT, "ALPHA_POW": ALPHA_POW, "N_STRATA": N_STRATA}
    out["runtime_s"] = round(time.time() - t0, 1)
    json.dump(out, open("analysis/pe010_gates.json", "w"), indent=1)

def one(tabs, h, seed=SEED_NULL, R=R_NULL):
    rng = random.Random(seed); obs, p, nl = null_p(tabs, h, R, rng); ne = sum(eligible(t, h) for t in tabs)
    return {"eligible": ne, "matched": obs, "null_mean": round(sum(nl) / len(nl), 3), "null_max": max(nl), "p": p,
            "cp95_upper": G.cp_high(obs, ne) if ne else None,
            "matched_pids": [t["pid"] for t in tabs if eligible(t, h) and match(t, t["total"], h)]}

def test():
    t0 = time.time(); g = json.load(open("analysis/pe010_gates.json")); S = build_sets(); res = {}
    for tid, sname, h in TESTS: res[tid] = one(S[sname], h)
    adj = G.holm([res[tid]["p"] for tid, _, _ in TESTS]); verdict = {}
    for (tid, _, _), a in zip(TESTS, adj):
        gg = g[tid]; res[tid]["p_holm"] = a
        if not (gg["FPR_ok"] and gg["power_ok"] and gg["size_ok"]): v = "NOT TESTABLE"
        elif a > ALPHA: v = "EXCLUDED" if res[tid]["cp95_upper"] < EXCL_UB else "NOT DETECTED"
        else: v = "SUPPORTED"
        verdict[tid] = v
    # descriptive, after the decision
    d1 = S["D1"]; sh = {}
    for s in (-1, 1):
        sh[str(s)] = sum(1 for t in d1 if eligible(t, "ENTRY") and match(t, t["total"], "ENTRY", shift=s * min(C[x] for x in t["total"])))
    desc = {"T1_shifted_control": {"exact": res["T1_ENTRY"]["matched"], "shift_-1": sh["-1"], "shift_+1": sh["1"]},
            "D2_ENTRY_exposed": one(S["D2"], "ENTRY"), "D2_MEAN_exact": one(S["D2"], "MEAN"),
            "D1_complete_MAX": one([t for t in d1 if t["complete"]], "MAX") if sum(t["complete"] for t in d1) >= 2 else None,
            "D1_complete_MEAN": one([t for t in d1 if t["complete"]], "MEAN") if sum(t["complete"] for t in d1) >= 2 else None}
    for name, tabs in exposed_sets().items():
        for h in ("ENTRY", "MAX", "MEAN", "MEAN_ROUND"): desc[f"{name}_{h}"] = one(tabs, h)
    out = {"verdicts": verdict, "results": res, "gates": g, "descriptive_no_decision_weight": desc,
           "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe010_results.json", "w"), indent=1)
    print(json.dumps({"verdicts": verdict, "results": res, "descriptive": desc}, indent=1))

def audit():
    """PE009 audit: (1) re-run `pe009_other_quantity.py test` in a scratch copy with the published gates and compare
    every field except run time; (2) independently re-count PE009's A H4 (count of lines, 0/15) and A H1 match
    (P008825, ratio 1/30) with a literal C table and plain integer sums (no P.value / pe009 code)."""
    here = os.getcwd(); tmp = tempfile.mkdtemp()
    try:
        shutil.copytree("tools", os.path.join(tmp, "tools")); os.makedirs(os.path.join(tmp, "analysis"))
        os.symlink(os.path.join(here, "data"), os.path.join(tmp, "data"))
        shutil.copy("analysis/pe009_gates.json", os.path.join(tmp, "analysis"))
        subprocess.run([sys.executable, "tools/pe009_other_quantity.py", "test"], cwd=tmp, check=True, capture_output=True)
        a = json.load(open("analysis/pe009_results.json")); b = json.load(open(os.path.join(tmp, "analysis/pe009_results.json")))
        def strip(d):
            if isinstance(d, dict): return {k: strip(v) for k, v in d.items() if "time" not in k and "runtime" not in k}
            if isinstance(d, list): return [strip(x) for x in d]
            return d
        out = {"pe009_results_identical_except_time": strip(a) == strip(b)}
        LIT = {"N39C": 1, "N30D": 2, "N30C": 4, "N24": 12, "N39B": 24, "N01": 120, "N14": 720, "N45": 7200,
               "N34": 21600, "N48": 216000}
        LS = {"N01": 1, "N14": 10, "N34": 60, "N45": 600, "N48": 3600}
        A = G.target_sets()["R"]; h4 = 0; h1 = []
        for t in A:
            if all(s in LS for s in t["total"]) and sum(LS[s] * k for s, k in t["total"].items()) == len(t["entries"]): h4 += 1
            if all(s in LIT for e in t["entries"] for s in e) and all(s in LIT for s in t["total"]):
                sm = sum(LIT[s] * k for e in t["entries"] for s, k in e.items()); tv = sum(LIT[s] * k for s, k in t["total"].items())
                if t["pid"] == "P008825": h1.append({"pid": t["pid"], "total": tv, "sum": sm, "ratio_is_1_30": tv * 30 == sm})
        out["A_H4_recount"] = {"matched": h4, "of": len(A), "published": "0/15", "match": h4 == 0 and len(A) == 15}
        out["A_H1_P008825"] = h1
        json.dump(out, open("analysis/pe010_pe009_audit.json", "w"), indent=1); print(json.dumps(out, indent=1))
    finally: shutil.rmtree(tmp)

if __name__ == "__main__":
    {"inventory": inventory, "gates": gates, "test": test, "audit": audit}[sys.argv[1]]()
