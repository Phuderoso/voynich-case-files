#!/usr/bin/env python3
"""PE008 - How are grain (capacity, CAP) totals built? Partial-total conventions vs upper capacity factors,
tested on the non-balancing CAP single-total tablets.

Pre-registered in case-file/PE008-grain-totals.md (committed with this tool BEFORE any convention match, gate or null
number was computed). Usage (from expeditions/proto-elamite/, after `python3 tools/pe001_totals.py fetch`):
    python3 tools/pe008_grain_totals.py inventory   # label-free structure of the target sets (sizes, eligibility)
    python3 tools/pe008_grain_totals.py gates       # FPR gate + planted-convention power gate, per set x convention
    python3 tools/pe008_grain_totals.py test        # observed counts, nulls, Holm (primary), replication, verdicts
    python3 tools/pe008_grain_totals.py audit       # PE007 audit: re-run `pe007_noncap.py test` in scratch, compare
Pure Python 3 (random.Random), exact integer arithmetic in each system's smallest unit.

TARGETS (non-balancing CAP tablets; CAP = N39B/N24/N30C/N30D/N39C in entries or total; balance = pe001 `balances`):
  P (primary)     PE006 fresh set, CAP and not balancing (25 tablets).
  R (replication) PE005/PE004 calibration set, CAP and not balancing (15 tablets).
Entries in ATF line order (reading order of the obverse). Admitted systems for a tablet = those of S/D/B/C in which
every entry and the total are valid (as in pe001 `balances`).

CONVENTION FAMILY (fixed before looking; a tablet 'matches' if ANY admitted system satisfies the convention):
  K1 PREFIX   total = sum of the first k entries, 2 <= k <= n-1                 (eligible: n >= 3)
  K2 RUN      total = sum of a contiguous run of entries, length 2 .. n-1       (eligible: n >= 3)
  K3 NONSUB   total = sum of the entries WITHOUT sub-unit signs ("non-grain lines"; 1 <= |J| <= n-1)
  K4 SUBONLY  total = sum of the entries WITH sub-unit signs (1 <= |K| <= n-1)  (complement of K3)
  K5 UPPER    total = sum of ALL entries under a variant C table with ONE upper capacity factor changed
              (Englund: N14 = 6 N01, N45 = 10 N14, N34 = 3 N45, N48 = 10 N34; variants N14:N01 in {5,10},
              N45:N14 in {5,6}, N34:N45 in {2,6}, N48:N34 in {6}); the rival explanation (factors, not partial totals).
Statistic: number of eligible target tablets that match.
NULLS (structure-preserving):
  K1, K2: line-order shuffle (entries permuted within each tablet; entries, values and totals kept), R = 1999, seed 801.
  K3, K4, K5 (order-invariant): totals permuted among the target tablets of the set, R = 1999, seed 801.
  p = (1 + #null >= obs) / (1 + R).
GATES (per set x convention):
  FPR: 100 destroyed-signal datasets (K1/K2 one line-order shuffle; K3-K5 one total permutation), each tested with
       R = 299 inner nulls; rate of p <= 0.05 must be <= 0.06. Seed 802.
  Power: 100 planted datasets: each eligible target independently (prob 0.5) gets total := canonical notation of the
       convention's own sum (K1 random k, K2 random run, K3 J-sum, K4 K-sum, K5 full sum under a random variant table)
       in a random admitted system; test with R = 299; rate of p <= 0.01 (Holm worst case 0.05/5) must be >= 0.80.
       Seed 803. Plant probability 0.8 reported (descriptive).
  Size: >= 8 eligible targets.
DECISION: primary set P, Holm over K1..K5 at 0.05. Replication set R is tested only as confirmation (unadjusted 0.05)
for conventions that pass on P. Verdicts: NOT TESTABLE (a P gate fails) / NOT DETECTED (gates pass, Holm p > 0.05) /
EXCLUDED (NOT DETECTED and one-sided CP95 upper bound of matched/eligible < 0.25) / SUPPORTED (P passes AND R gates
pass AND R p <= 0.05) / LEAD (P passes, R not testable) / NOT CONFIRMED (P passes, R gates pass, R p > 0.05).
"""
import json, os, sys, time, random, math, shutil, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe001_totals as P
import pe004_restore as Q
import pe005_balance as F
import pe006_cap as T

SUB = P.C_SUB_SIGNS
SYS = dict(Q.SYS)                     # S, D, B, C (Englund)
R_NULL, SEED_NULL = 1999, 801
N_FPR, R_IN, SEED_FPR = 100, 299, 802
N_POW, SEED_POW, PLANT, PLANT_HI = 100, 803, 0.5, 0.8
ALPHA, ALPHA_POW, FPR_MAX, POWER_MIN, MIN_ELIG, EXCL_UB = 0.05, 0.01, 0.06, 0.80, 8, 0.25
KS = ("K1_PREFIX", "K2_RUN", "K3_NONSUB", "K4_SUBONLY", "K5_UPPER")
ORDER_KS = ("K1_PREFIX", "K2_RUN")

def c_upper(f1=6, f2=10, f3=3, f4=10):
    v = dict(P.c_table()); base = v["N01"]
    v["N14"] = base * f1; v["N45"] = v["N14"] * f2; v["N34"] = v["N45"] * f3; v["N48"] = v["N34"] * f4
    return v
VARIANTS = [c_upper(f1=5), c_upper(f1=10), c_upper(f2=5), c_upper(f2=6), c_upper(f3=2), c_upper(f3=6), c_upper(f4=6)]
assert c_upper() == P.c_table()

def target_sets():
    rows6, _, _ = T.load(); rows5 = F.load()[1]
    Pset = [r["t"] for r in rows6 if r["cap"] and not T.label(r)]
    Rset = [r["t"] for r in rows5 if r["f"]["CAP"] and not F.label(r)]
    nP = [r["t"] for r in rows6 if not r["cap"] and not T.label(r)]
    nR = [r["t"] for r in rows5 if not r["f"]["CAP"] and not F.label(r)]
    return {"P": Pset, "R": Rset, "nonCAP_P": nP, "nonCAP_R": nR}

def hassub(e): return any(s in SUB for s in e)

def eligible(t, k):
    n = len(t["entries"]); j = sum(not hassub(e) for e in t["entries"])
    if k in ORDER_KS: return n >= 3
    if k in ("K3_NONSUB", "K4_SUBONLY"): return 1 <= j <= n - 1
    return all(P.value(e, SYS["C"]) is not None for e in t["entries"]) and P.value(t["total"], SYS["C"]) is not None

def match(entries, total, k):
    """entries: list of notations in order; total: notation."""
    if k == "K5_UPPER":
        for tb in VARIANTS:
            vs = [P.value(e, tb) for e in entries]; vt = P.value(total, tb)
            if vt is not None and None not in vs and sum(vs) == vt: return True
        return False
    n = len(entries); sub = [hassub(e) for e in entries]
    for tb in SYS.values():
        vt = P.value(total, tb)
        if vt is None: continue
        vs = [P.value(e, tb) for e in entries]
        if None in vs: continue
        if k == "K1_PREFIX":
            s = vs[0]
            for i in range(1, n - 1):
                s += vs[i]
                if s == vt: return True
        elif k == "K2_RUN":
            for a in range(n):
                s = vs[a]
                for b in range(a + 1, n):
                    s += vs[b]
                    if b - a + 1 <= n - 1 and s == vt: return True
        elif k == "K3_NONSUB":
            if sum(v for v, sb in zip(vs, sub) if not sb) == vt: return True
        elif k == "K4_SUBONLY":
            if sum(v for v, sb in zip(vs, sub) if sb) == vt: return True
    return False

def stat(tabs, k, totals=None, orders=None):
    c = 0
    for i, t in enumerate(tabs):
        if not eligible(t, k): continue
        e = t["entries"] if orders is None else [t["entries"][j] for j in orders[i]]
        c += match(e, t["total"] if totals is None else totals[i], k)
    return c

def null_p(tabs, k, R, rng):
    obs = stat(tabs, k); ge = 0; nl = []
    tots = [t["total"] for t in tabs]
    for _ in range(R):
        if k in ORDER_KS:
            orders = []
            for t in tabs:
                o = list(range(len(t["entries"]))); rng.shuffle(o); orders.append(o)
            m = stat(tabs, k, orders=orders)
        else:
            sh = tots[:]; rng.shuffle(sh); m = stat(tabs, k, totals=sh)
        nl.append(m); ge += m >= obs
    return obs, (1 + ge) / (1 + R), nl

def destroy(tabs, k, rng):
    if k in ORDER_KS:
        out = []
        for t in tabs:
            e = t["entries"][:]; rng.shuffle(e); out.append({**t, "entries": e})
        return out
    tots = [t["total"] for t in tabs]; rng.shuffle(tots)
    return [{**t, "total": x} for t, x in zip(tabs, tots)]

def conv_sum(t, k, tb, rng):
    vs = [P.value(e, tb) for e in t["entries"]]
    if None in vs: return None
    n = len(vs)
    if k == "K1_PREFIX": return sum(vs[:rng.randint(2, n - 1)])
    if k == "K2_RUN":
        runs = [(a, b) for a in range(n) for b in range(a + 1, n) if b - a + 1 <= n - 1]; a, b = runs[rng.randrange(len(runs))]
        return sum(vs[a:b + 1])
    sub = [hassub(e) for e in t["entries"]]
    if k == "K3_NONSUB": return sum(v for v, s in zip(vs, sub) if not s)
    if k == "K4_SUBONLY": return sum(v for v, s in zip(vs, sub) if s)
    return sum(vs)

def plant(tabs, k, rng, prob):
    out = []
    for t in tabs:
        tot = t["total"]
        if eligible(t, k) and rng.random() < prob:
            if k == "K5_UPPER": tb = VARIANTS[rng.randrange(len(VARIANTS))]
            else:
                adm = [X for X in Q.ORDER if all(P.value(e, SYS[X]) is not None for e in t["entries"])]
                tb = SYS[adm[rng.randrange(len(adm))]] if adm else None
            if tb is not None:
                v = conv_sum(t, k, tb, rng)
                if v: tot = P.canonical(v, tb)
        out.append({**t, "total": tot})
    return out

def inventory():
    S = target_sets(); out = {}
    for name, tabs in S.items():
        out[name] = {"tablets": len(tabs), "eligible": {k: sum(eligible(t, k) for t in tabs) for k in KS},
                     "entries_per_tablet": sorted(len(t["entries"]) for t in tabs), "pids": [t["pid"] for t in tabs]}
    json.dump(out, open("analysis/pe008_inventory.json", "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "pids"} for k, v in out.items()}, indent=1))

def gates():
    t0 = time.time(); S = target_sets(); out = {}
    for name in ("P", "R"):
        tabs = S[name]; out[name] = {}
        for k in KS:
            ne = sum(eligible(t, k) for t in tabs)
            rng = random.Random(SEED_FPR); fp = 0
            for _ in range(N_FPR):
                d = destroy(tabs, k, rng); fp += null_p(d, k, R_IN, rng)[1] <= ALPHA
            rng = random.Random(SEED_POW); hit = 0; hit_hi = 0
            for _ in range(N_POW):
                d = plant(tabs, k, rng, PLANT); hit += null_p(d, k, R_IN, rng)[1] <= ALPHA_POW
            for _ in range(N_POW // 2):
                d = plant(tabs, k, rng, PLANT_HI); hit_hi += null_p(d, k, R_IN, rng)[1] <= ALPHA_POW
            out[name][k] = {"eligible": ne, "FPR": fp / N_FPR, "FPR_ok": fp / N_FPR <= FPR_MAX,
                            "power_p05": hit / N_POW, "power_ok": hit / N_POW >= POWER_MIN,
                            "power_p08_descriptive": hit_hi / (N_POW // 2), "size_ok": ne >= MIN_ELIG}
            print(name, k, out[name][k], round(time.time() - t0, 1), flush=True)
    out["params"] = {"N_FPR": N_FPR, "R_IN": R_IN, "SEED_FPR": SEED_FPR, "N_POW": N_POW, "SEED_POW": SEED_POW,
                     "PLANT": PLANT, "ALPHA_POW": ALPHA_POW}
    out["runtime_s"] = round(time.time() - t0, 1)
    json.dump(out, open("analysis/pe008_gates.json", "w"), indent=1)

def cp_high(k, n, a=0.05):
    if k == n: return 1.0
    return 1 - Q.cp_low(n - k, n, a)

def holm(ps):
    m = len(ps); order = sorted(range(m), key=lambda i: ps[i]); adj = [0.0] * m; run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * ps[i])); adj[i] = run
    return adj

def test():
    t0 = time.time(); g = json.load(open("analysis/pe008_gates.json")); S = target_sets(); res = {}
    for name in ("P", "R", "nonCAP_P", "nonCAP_R"):
        tabs = S[name]; res[name] = {}
        for k in KS:
            rng = random.Random(SEED_NULL); obs, p, nl = null_p(tabs, k, R_NULL, rng)
            ne = sum(eligible(t, k) for t in tabs)
            d = {"eligible": ne, "matched": obs, "null_mean": sum(nl) / len(nl), "null_max": max(nl), "p": p,
                 "cp95_upper_matched_fraction": cp_high(obs, ne) if ne else None,
                 "matched_pids": [t["pid"] for t in tabs if eligible(t, k) and match(t["entries"], t["total"], k)]}
            if k in ORDER_KS:   # descriptive: same statistic against the total-permutation null
                rng = random.Random(SEED_NULL + 1); tots = [t["total"] for t in tabs]; ge = 0
                for _ in range(R_NULL):
                    sh = tots[:]; rng.shuffle(sh); ge += stat(tabs, k, totals=sh) >= obs
                d["p_total_permutation_descriptive"] = (1 + ge) / (1 + R_NULL)
            res[name][k] = d
    adj = holm([res["P"][k]["p"] for k in KS]); verdict = {}
    for k, a in zip(KS, adj):
        gp, gr = g["P"][k], g["R"][k]; res["P"][k]["p_holm"] = a
        okP = gp["FPR_ok"] and gp["power_ok"] and gp["size_ok"]; okR = gr["FPR_ok"] and gr["power_ok"] and gr["size_ok"]
        if not okP: v = "NOT TESTABLE"
        elif a > ALPHA:
            ub = res["P"][k]["cp95_upper_matched_fraction"]; v = "EXCLUDED" if ub is not None and ub < EXCL_UB else "NOT DETECTED"
        elif not okR: v = "LEAD (replication NOT TESTABLE)"
        elif res["R"][k]["p"] <= ALPHA: v = "SUPPORTED"
        else: v = "NOT CONFIRMED"
        verdict[k] = v
    # descriptive overlap on P: tablets explained by any partial-total convention vs by the upper-factor rival
    tabs = S["P"]; part = set(); up = set()
    for t in tabs:
        if any(eligible(t, k) and match(t["entries"], t["total"], k) for k in KS[:4]): part.add(t["pid"])
        if eligible(t, "K5_UPPER") and match(t["entries"], t["total"], "K5_UPPER"): up.add(t["pid"])
    out = {"verdicts": verdict, "results": res, "gates": g,
           "overlap_P": {"partial_any": sorted(part), "upper": sorted(up), "both": sorted(part & up),
                         "unexplained": len(tabs) - len(part | up), "of": len(tabs)},
           "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe008_results.json", "w"), indent=1)
    print(json.dumps({"verdicts": verdict, "overlap_P": out["overlap_P"],
                      "P": {k: {kk: vv for kk, vv in v.items() if kk != "matched_pids"} for k, v in res["P"].items()},
                      "R": {k: {kk: vv for kk, vv in v.items() if kk != "matched_pids"} for k, v in res["R"].items()}}, indent=1))

def audit():
    """PE007 audit: re-run `pe007_noncap.py test` in a scratch copy with the published gates; compare every field
    except run time; re-check one number independently (set B entry precision 28/... from per-task rows)."""
    here = os.getcwd(); tmp = tempfile.mkdtemp()
    try:
        shutil.copytree("tools", os.path.join(tmp, "tools")); os.makedirs(os.path.join(tmp, "analysis"))
        os.symlink(os.path.join(here, "data"), os.path.join(tmp, "data"))
        shutil.copy("analysis/pe007_gates.json", os.path.join(tmp, "analysis"))
        subprocess.run([sys.executable, "tools/pe007_noncap.py", "test"], cwd=tmp, check=True, capture_output=True)
        a = json.load(open("analysis/pe007_results.json")); b = json.load(open(os.path.join(tmp, "analysis/pe007_results.json")))
        def strip(d):
            if isinstance(d, dict): return {k: strip(v) for k, v in d.items() if "time" not in k}
            if isinstance(d, list): return [strip(x) for x in d]
            return d
        out = {"pe007_results_identical_except_time": strip(a) == strip(b)}
        # independent re-check: fresh set B entry precision from a direct leave-one-out with the PE004 solver
        import pe007_noncap as N
        B = N.sets()["B"]; rows = Q.score(B, with_base=True)
        E = [r for r in rows if r["kind"] == "entry"]; u = sum(r["unique"] for r in E); uc = sum(r["unique_correct"] for r in E)
        out["B_entry_recomputed"] = {"tasks": len(E), "unique": u, "unique_correct": uc, "precision": uc / u if u else None}
        json.dump(out, open("analysis/pe008_pe007_audit.json", "w"), indent=1); print(json.dumps(out, indent=1))
    finally: shutil.rmtree(tmp)

if __name__ == "__main__":
    {"inventory": inventory, "gates": gates, "test": test, "audit": audit}[sys.argv[1]]()
