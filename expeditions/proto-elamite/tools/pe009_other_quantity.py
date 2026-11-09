#!/usr/bin/env python3
"""PE009 - Is the reverse number on non-balancing grain (capacity, CAP) tablets a DIFFERENT QUANTITY rather than a
total? Mixed-system readings and exact metrological ratios, tested against a total-permutation null.

Pre-registered in case-file/PE009-grain-other-quantity.md (committed with this tool BEFORE any H1-H4 match, gate or
null number was computed). Usage (from expeditions/proto-elamite/, after `python3 tools/pe001_totals.py fetch`):
    python3 tools/pe009_other_quantity.py inventory  # label-free: set sizes, eligibility per hypothesis (entries only)
    python3 tools/pe009_other_quantity.py gates      # FPR gate + planted-quantity power gate, per set x hypothesis
    python3 tools/pe009_other_quantity.py test       # observed counts, nulls, Holm on A, replication on B, verdicts
    python3 tools/pe009_other_quantity.py audit      # PE008 audit: re-run `pe008_grain_totals.py test` in scratch
Pure Python 3 (random.Random), exact integer / rational arithmetic.

SETS (labels exactly as published by PE005/PE006; built with pe008_grain_totals.target_sets):
  A (PRIMARY, decision)  PE005/PE004 intact set, CAP and not balancing: 15 tablets. Never inspected for ratios or for
                         cross-system readings (PE001 looked only at the direction total < sum, PE008 at partial sums).
  B (REPLICATION)        PE006 fresh set, CAP and not balancing: 25 tablets. EXPOSED for H1: PE008 post hoc published
                         their 25 total/sum ratios in C (median 0.242; one equals 0.5). Clean for H2-H4.
All values in C are in units of N39C (Englund's C table: N01 = 120, N14 = 720, N45 = 7200, ...); 'in N01' = / 120.

HYPOTHESIS FAMILY (fixed before looking; sources: Englund 2004 Fig. 5.4 tables; Dahl et al. CDLJ 2005:3):
  H1 RATIO_METRO  value_C(total) / sum_C(entries) = v_a / v_b for two DIFFERENT signs a, b of the C table
                  (the obverse sum written one or more units up/down: a unit conversion). The list is derived
                  mechanically from the C sign values, NOT from any observed ratio.     eligible: entries valid in C
  H2 MIX_EQ       the total read in S, B or D (in N01 units, discrete-count systems) equals the grain sum in N01
                  units: 120 * value_X(total) == sum_C, X in {S, B, D}.               eligible: entries valid in C and
                  sum_C a whole number of N01 (sum_C % 120 == 0)
  H3 PER_HEAD     the total read in S (Englund: S counts people and discrete objects) is a head-count k >= 1 and the
                  grain sum is exactly k standard rations: sum_C == k * u, u in U = {single C sign values below N01:
                  1, 2, 4, 12, 24} U {60 = 2 1/2 N39B, Englund's 2004 ration example} U {720, 7200 (N14, N45)};
                  u = 120 (one N01 per head) is H2's S case and is left to H2.       eligible: entries valid in C and
                  some u in U divides sum_C
  H4 COUNT_LINES  the total read in S equals the number of obverse entries n.          eligible: n >= 2 (all)
Statistic: number of eligible targets in the set that match.
NULL (structure-preserving): totals permuted among the targets of the set (entries, the set's totals kept; only the
  tablet-total link destroyed). R = 1999, seed 901. p = (1 + #null >= obs) / (1 + R).
GATES (per set x hypothesis, computed after the pre-registration is published, before the test):
  FPR: 100 total-permuted datasets, each tested with R = 299; rate of p <= 0.05 must be <= 0.06. Seed 902.
  Power: 100 planted datasets; each eligible target independently (prob 0.5) gets total := canonical notation of the
    hypothesis' own quantity (H1 sum * v_a/v_b in C for a random sign pair giving a whole positive value with a
    canonical C notation; H2 sum/120 in a random X of S/B/D; H3 sum/u in S for a random dividing u; H4 n in S);
    tested with R = 299; rate of p <= 0.0125 (Holm worst case 0.05/4) must be >= 0.80. Seed 903. Plant 0.8 descriptive.
  Size: >= 8 eligible targets.
DECISION: A, Holm over H1-H4 at 0.05. B only as confirmation (unadjusted 0.05) for hypotheses passing on A.
  NOT TESTABLE (an A gate fails) / NOT DETECTED (A gates pass, Holm p > 0.05) / EXCLUDED (NOT DETECTED and one-sided
  CP95 upper bound of matched/eligible on A < 0.25) / SUPPORTED (A passes, B gates pass, B p <= 0.05; for H1 labelled
  'replication exposed') / LEAD (A passes, B not testable) / NOT CONFIRMED (A passes, B gates pass, B p > 0.05).
EXPLORATORY (no decision weight, run after the test): generic small fractions E = {1/2, 1/3, 2/3, 1/4, 3/4, 1/5,
  2/5, 1/6, 1/8, 1/10} for total/sum in C on A and B, with the same permutation null as a scale.
"""
import json, os, sys, time, random, shutil, subprocess, tempfile
from fractions import Fraction as Fr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe001_totals as P
import pe008_grain_totals as G

C = P.c_table(); N01 = C["N01"]; SYSN = {k: P.SYSTEMS[k] for k in ("S", "B", "D")}
RATIOS = sorted({Fr(C[a], C[b]) for a in C for b in C if a != b})        # H1 list (metrological, a priori)
U = (1, 2, 4, 12, 24, 60, 720, 7200)                                    # H3 ration units (N39C units)
EXPL = (Fr(1, 2), Fr(1, 3), Fr(2, 3), Fr(1, 4), Fr(3, 4), Fr(1, 5), Fr(2, 5), Fr(1, 6), Fr(1, 8), Fr(1, 10))
R_NULL, SEED_NULL = 1999, 901
N_FPR, R_IN, SEED_FPR = 100, 299, 902
N_POW, SEED_POW, PLANT, PLANT_HI = 100, 903, 0.5, 0.8
ALPHA, ALPHA_POW, FPR_MAX, POWER_MIN, MIN_ELIG, EXCL_UB = 0.05, 0.0125, 0.06, 0.80, 8, 0.25
HS = ("H1_RATIO_METRO", "H2_MIX_EQ", "H3_PER_HEAD", "H4_COUNT_LINES")

def sets():
    S = G.target_sets(); return {"A": S["R"], "B": S["P"]}

def csum(t):
    vs = [P.value(e, C) for e in t["entries"]]
    return None if None in vs else sum(vs)

def eligible(t, h):
    s = csum(t)
    if h == "H4_COUNT_LINES": return len(t["entries"]) >= 2
    if s is None or s <= 0: return False
    if h == "H1_RATIO_METRO": return True
    if h == "H2_MIX_EQ": return s % N01 == 0
    return any(s % u == 0 for u in U)

def match(t, total, h, ratios=RATIOS):
    s = csum(t)
    if h == "H4_COUNT_LINES": return P.value(total, P.SYSTEMS["S"]) == len(t["entries"])
    if s is None or s <= 0: return False
    if h in ("H1_RATIO_METRO", "EXPL"):
        vt = P.value(total, C)
        return vt is not None and Fr(vt, s) in set(ratios)
    if h == "H2_MIX_EQ":
        return any(P.value(total, tb) is not None and N01 * P.value(total, tb) == s for tb in SYSN.values())
    k = P.value(total, P.SYSTEMS["S"])
    return bool(k) and k >= 1 and any(k * u == s for u in U)

def stat(tabs, h, totals=None, ratios=RATIOS):
    return sum(match(t, t["total"] if totals is None else totals[i], h, ratios)
               for i, t in enumerate(tabs) if (h == "EXPL" and csum(t)) or (h != "EXPL" and eligible(t, h)))

def null_p(tabs, h, R, rng, ratios=RATIOS):
    obs = stat(tabs, h, ratios=ratios); tots = [t["total"] for t in tabs]; ge = 0; nl = []
    for _ in range(R):
        sh = tots[:]; rng.shuffle(sh); m = stat(tabs, h, sh, ratios); nl.append(m); ge += m >= obs
    return obs, (1 + ge) / (1 + R), nl

def destroy(tabs, rng):
    tots = [t["total"] for t in tabs]; rng.shuffle(tots); return [{**t, "total": x} for t, x in zip(tabs, tots)]

def planted_total(t, h, rng):
    s = csum(t)
    if h == "H4_COUNT_LINES": return P.canonical(len(t["entries"]), P.SYSTEMS["S"])
    if h == "H1_RATIO_METRO":
        opts = [r for r in RATIOS if (s * r).denominator == 1 and s * r > 0 and P.canonical(int(s * r), C)]
        return P.canonical(int(s * opts[rng.randrange(len(opts))]), C) if opts else None
    if h == "H2_MIX_EQ":
        tb = list(SYSN.values())[rng.randrange(3)]; return P.canonical(s // N01, tb)
    us = [u for u in U if s % u == 0]; return P.canonical(s // us[rng.randrange(len(us))], P.SYSTEMS["S"])

def plant(tabs, h, rng, prob):
    out = []
    for t in tabs:
        tot = t["total"]
        if eligible(t, h) and rng.random() < prob:
            x = planted_total(t, h, rng)
            if x: tot = x
        out.append({**t, "total": tot})
    return out

def inventory():
    S = sets(); out = {}
    for name, tabs in S.items():
        out[name] = {"tablets": len(tabs), "eligible": {h: sum(eligible(t, h) for t in tabs) for h in HS},
                     "entries_per_tablet": sorted(len(t["entries"]) for t in tabs), "pids": [t["pid"] for t in tabs]}
    out["H1_list_size"] = len(RATIOS); out["H3_U"] = U
    json.dump(out, open("analysis/pe009_inventory.json", "w"), indent=1)
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "pids"} if isinstance(v, dict) else v)
                      for k, v in out.items()}, indent=1))

def gates():
    t0 = time.time(); S = sets(); out = {}
    for name in ("A", "B"):
        tabs = S[name]; out[name] = {}
        for h in HS:
            ne = sum(eligible(t, h) for t in tabs)
            rng = random.Random(SEED_FPR); fp = 0
            for _ in range(N_FPR): fp += null_p(destroy(tabs, rng), h, R_IN, rng)[1] <= ALPHA
            rng = random.Random(SEED_POW); hit = hit_hi = 0
            for _ in range(N_POW): hit += null_p(plant(tabs, h, rng, PLANT), h, R_IN, rng)[1] <= ALPHA_POW
            for _ in range(N_POW // 2): hit_hi += null_p(plant(tabs, h, rng, PLANT_HI), h, R_IN, rng)[1] <= ALPHA_POW
            out[name][h] = {"eligible": ne, "FPR": fp / N_FPR, "FPR_ok": fp / N_FPR <= FPR_MAX,
                            "power_p05": hit / N_POW, "power_ok": hit / N_POW >= POWER_MIN,
                            "power_p08_descriptive": hit_hi / (N_POW // 2), "size_ok": ne >= MIN_ELIG}
            print(name, h, out[name][h], round(time.time() - t0, 1), flush=True)
    out["params"] = {"N_FPR": N_FPR, "R_IN": R_IN, "SEED_FPR": SEED_FPR, "N_POW": N_POW, "SEED_POW": SEED_POW,
                     "PLANT": PLANT, "ALPHA_POW": ALPHA_POW}
    out["runtime_s"] = round(time.time() - t0, 1)
    json.dump(out, open("analysis/pe009_gates.json", "w"), indent=1)

def test():
    t0 = time.time(); g = json.load(open("analysis/pe009_gates.json")); S = sets(); res = {}
    for name in ("A", "B"):
        tabs = S[name]; res[name] = {}
        for h in HS:
            rng = random.Random(SEED_NULL); obs, p, nl = null_p(tabs, h, R_NULL, rng)
            ne = sum(eligible(t, h) for t in tabs)
            res[name][h] = {"eligible": ne, "matched": obs, "null_mean": sum(nl) / len(nl), "null_max": max(nl), "p": p,
                            "cp95_upper_matched_fraction": G.cp_high(obs, ne) if ne else None,
                            "matched_pids": [t["pid"] for t in tabs if eligible(t, h) and match(t, t["total"], h)]}
    adj = G.holm([res["A"][h]["p"] for h in HS]); verdict = {}
    for h, a in zip(HS, adj):
        ga, gb = g["A"][h], g["B"][h]; res["A"][h]["p_holm"] = a
        okA = ga["FPR_ok"] and ga["power_ok"] and ga["size_ok"]; okB = gb["FPR_ok"] and gb["power_ok"] and gb["size_ok"]
        if not okA: v = "NOT TESTABLE"
        elif a > ALPHA:
            ub = res["A"][h]["cp95_upper_matched_fraction"]; v = "EXCLUDED" if ub is not None and ub < EXCL_UB else "NOT DETECTED"
        elif not okB: v = "LEAD (replication NOT TESTABLE)"
        elif res["B"][h]["p"] <= ALPHA: v = "SUPPORTED" + (" (replication exposed)" if h == "H1_RATIO_METRO" else "")
        else: v = "NOT CONFIRMED"
        verdict[h] = v
    expl = {}
    for name in ("A", "B"):
        rng = random.Random(SEED_NULL + 7); obs, p, nl = null_p(S[name], "EXPL", 999, rng, ratios=EXPL)
        expl[name] = {"matched": obs, "of": sum(1 for t in S[name] if csum(t)), "perm_mean": sum(nl) / len(nl),
                      "perm_rate_ge_obs": p, "pids": [t["pid"] for t in S[name] if csum(t) and match(t, t["total"], "EXPL", EXPL)]}
    union = {name: sorted({pid for h in HS for pid in res[name][h]["matched_pids"]}) for name in ("A", "B")}
    out = {"verdicts": verdict, "results": res, "gates": g, "exploratory_small_fractions": expl,
           "explained_any_H": {n: {"pids": union[n], "count": len(union[n]), "of": len(S[n])} for n in union},
           "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe009_results.json", "w"), indent=1)
    print(json.dumps({"verdicts": verdict, "A": res["A"], "B": res["B"], "expl": expl,
                      "explained": out["explained_any_H"]}, indent=1))

def audit():
    """PE008 audit: re-run `pe008_grain_totals.py test` in a scratch copy with the published gates, compare every field
    except run time; independently re-compute the PE008 post-hoc median total/sum ratio in C on P (published 0.242)
    with a literal C table written here (not P.c_table) and plain integer sums."""
    here = os.getcwd(); tmp = tempfile.mkdtemp()
    try:
        shutil.copytree("tools", os.path.join(tmp, "tools")); os.makedirs(os.path.join(tmp, "analysis"))
        os.symlink(os.path.join(here, "data"), os.path.join(tmp, "data"))
        shutil.copy("analysis/pe008_gates.json", os.path.join(tmp, "analysis"))
        subprocess.run([sys.executable, "tools/pe008_grain_totals.py", "test"], cwd=tmp, check=True, capture_output=True)
        a = json.load(open("analysis/pe008_results.json")); b = json.load(open(os.path.join(tmp, "analysis/pe008_results.json")))
        def strip(d):
            if isinstance(d, dict): return {k: strip(v) for k, v in d.items() if "time" not in k}
            if isinstance(d, list): return [strip(x) for x in d]
            return d
        out = {"pe008_results_identical_except_time": strip(a) == strip(b)}
        LIT = {"N39C": 1, "N30D": 2, "N30C": 4, "N24": 12, "N39B": 24, "N01": 120, "N14": 720, "N45": 7200,
               "N34": 21600, "N48": 216000}
        rs = []
        for t in G.target_sets()["P"]:
            ok = all(s in LIT for e in t["entries"] for s in e) and all(s in LIT for s in t["total"])
            if not ok: continue
            sm = sum(LIT[s] * k for e in t["entries"] for s, k in e.items()); tv = sum(LIT[s] * k for s, k in t["total"].items())
            rs.append(tv / sm)
        rs.sort(); out["P_ratio_recomputed"] = {"n": len(rs), "median": round(rs[len(rs) // 2], 3),
                                                "published_median": 0.242, "match": round(rs[len(rs) // 2], 3) == 0.242}
        json.dump(out, open("analysis/pe009_pe008_audit.json", "w"), indent=1); print(json.dumps(out, indent=1))
    finally: shutil.rmtree(tmp)

if __name__ == "__main__":
    {"inventory": inventory, "gates": gates, "test": test, "audit": audit}[sys.argv[1]]()
