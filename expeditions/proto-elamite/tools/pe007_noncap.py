#!/usr/bin/env python3
"""PE007 - Grand-total restoration re-scored on NON-capacity tablets only (consequence of PE006).

Pre-registered in case-file/PE007-restoration-noncap.md (committed with this tool BEFORE any precision, gate or
null number on these sets was computed). Usage (from expeditions/proto-elamite/, after `python3 tools/pe001_totals.py fetch`):
    python3 tools/pe007_noncap.py inventory  # label-free: set sizes and task counts only
    python3 tools/pe007_noncap.py gates      # FPR gate (total-permutation null) + planted-balance power gate, per set/target
    python3 tools/pe007_noncap.py test       # leave-one-out scoring (PE004 rule, unchanged), G1-G4, Holm, verdicts
    python3 tools/pe007_noncap.py apply      # stage 2, only for VALIDATED targets: damaged non-CAP tablets
    python3 tools/pe007_noncap.py audit      # PE006 audit: re-run `pe006_cap.py test` in scratch, compare, re-check p
Sets (non-CAP = no capacity sub-unit sign N39B/N24/N30C/N30D/N39C in entries or total; PE005 definition):
  A  PE004/PE005 calibration tablets (intact single-total, common system exists) that are non-CAP: the re-score
     announced in README open line 8 (in-sample for the CAP split: these tablets generated the PE005 lead).
  B  PE006 fresh set, non-CAP, class H only (damaged-but-read '#'/'?' numerals, NO editor restoration in [ ]):
     out of sample for restoration. Class R is excluded because an editor may restore a numeral FROM the total,
     which makes leave-one-out circular.
Rule, tasks, baseline, metrics: PE004 (tools/pe004_restore.py) unchanged.
"""
import json, os, sys, time, math, random, shutil, subprocess, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe004_restore as Q
import pe005_balance as F
import pe006_cap as T
import pe001_totals as P

ALPHA = 0.05
R_FPR, SEED_FPR = 999, 701
R_POW, SEED_POW, P_PLANT = 200, 702, 0.90
R_NULL, SEED_NULL = 4999, 703
FPR_MAX, POWER_MIN = 0.06, 0.80
TARGETS = ("entry", "total")

def sets():
    _, rows5, _ = F.load()
    A = [r["t"] for r in rows5 if not r["f"]["CAP"]]
    rows6, _, _ = T.load()
    B = [r["t"] for r in rows6 if not r["cap"] and r["cls"] == "H"]
    return {"A": A, "B": B}

def stats(rows, kind):
    R = [r for r in rows if r["kind"] == kind]; n = len(R); u = sum(r["unique"] for r in R)
    uc = sum(r["unique_correct"] for r in R); return n, u, uc, R

def g2(n, u, uc):
    return u >= Q.MIN_UNIQUE and (uc / u if u else 0) >= Q.PREC_MIN and (Q.cp_low(uc, u) if u else 0) >= Q.PREC_CP_LOW

def mcnemar(R):
    n10 = sum(r["unique_correct"] and not r["baseline_correct"] for r in R)
    n01 = sum(r["baseline_correct"] and not r["unique_correct"] for r in R)
    return n10, n01, (Q.binom_sf(n10, n10 + n01) if n10 + n01 else 1.0)

def cp_high(k, n, a=0.05):
    """Exact one-sided Clopper-Pearson upper bound."""
    if k == n: return 1.0
    return 1 - Q.cp_low(n - k, n, a)

def force_balance(cal, rng):
    """Plant: each tablet independently, with prob P_PLANT, gets total := canonical(sum of entries) in a random
    system admitted by its entries' signs (entries untouched); otherwise its real total is kept."""
    out = []
    for t in cal:
        tot = t["total"]
        if rng.random() < P_PLANT:
            signs = set().union(*[set(e) for e in t["entries"]])
            adm = [X for X in Q.ORDER if signs <= set(Q.SYS[X])]
            if adm:
                X = adm[rng.integers(len(adm))]; tb = Q.SYS[X]
                c = P.canonical(sum(P.value(e, tb) for e in t["entries"]), tb)
                if c is not None: tot = c
        out.append({**t, "total": tot})
    return out

def inventory():
    S = sets(); out = {}
    for k, cal in S.items():
        tk = Q.tasks(cal)
        out[k] = {"tablets": len(cal), "tasks_entry": sum(t["kind"] == "entry" for t in tk),
                  "tasks_total": sum(t["kind"] == "total" for t in tk), "pids": [t["pid"] for t in cal]}
    json.dump(out, open("analysis/pe007_inventory.json", "w"), indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "pids"} for k, v in out.items()}, indent=1))

def gates():
    t0 = time.time(); S = sets(); out = {}
    for k, cal in S.items():
        # FPR gate: totals permuted among the set's tablets (entries, notations, sizes kept; arithmetic destroyed)
        rng = np.random.default_rng(SEED_FPR); tots = [t["total"] for t in cal]; fp = {x: 0 for x in TARGETS}
        for _ in range(R_FPR):
            perm = rng.permutation(len(cal)); rows = Q.score(cal, [tots[j] for j in perm])
            for x in TARGETS:
                n, u, uc, _ = stats(rows, x); fp[x] += g2(n, u, uc)
        # Power gate: planted balance (90 % of tablets forced to balance); G1, G2, G3 (unadjusted alpha) must pass
        rng = np.random.default_rng(SEED_POW); hit = {x: 0 for x in TARGETS}; prec = {x: [] for x in TARGETS}
        for _ in range(R_POW):
            pc = force_balance(cal, rng); rows = Q.score(pc, with_base=True)
            for x in TARGETS:
                n, u, uc, R = stats(rows, x); _, _, pm = mcnemar(R)
                hit[x] += (n >= Q.MIN_TASKS) and g2(n, u, uc) and pm <= ALPHA
                if u: prec[x].append(uc / u)
        out[k] = {x: {"FPR_G2_pass_rate": fp[x] / R_FPR, "FPR_ok": fp[x] / R_FPR <= FPR_MAX,
                      "power_G1G2G3": hit[x] / R_POW, "power_ok": hit[x] / R_POW >= POWER_MIN,
                      "planted_mean_precision": float(np.mean(prec[x])) if prec[x] else None} for x in TARGETS}
        print(k, round(time.time() - t0, 1), flush=True)
    out["params"] = {"R_FPR": R_FPR, "SEED_FPR": SEED_FPR, "R_POW": R_POW, "SEED_POW": SEED_POW, "P_PLANT": P_PLANT}
    out["runtime_s"] = round(time.time() - t0, 1)
    json.dump(out, open("analysis/pe007_gates.json", "w"), indent=1); print(json.dumps(out, indent=1))

def test():
    t0 = time.time(); g = json.load(open("analysis/pe007_gates.json")); S = sets(); res = {}; mc = {}
    for k, cal in S.items():
        rows = Q.score(cal, with_base=True); tots = [t["total"] for t in cal]
        rng = np.random.default_rng(SEED_NULL); null = {x: [] for x in TARGETS}
        for _ in range(R_NULL):
            perm = rng.permutation(len(cal)); nr = Q.score(cal, [tots[j] for j in perm])
            for x in TARGETS: null[x].append(stats(nr, x)[2])
        res[k] = {}
        for x in TARGETS:
            n, u, uc, R = stats(rows, x); n10, n01, pm = mcnemar(R); mc[(k, x)] = pm
            nl = np.array(null[x])
            res[k][x] = {"tasks": n, "unique": u, "unique_correct": uc, "recovery": uc / n if n else None,
                         "precision": uc / u if u else None, "cp95_low": Q.cp_low(uc, u) if u else 0.0,
                         "cp95_high": cp_high(uc, u) if u else 1.0,
                         "no_candidate": sum(r["n_cand"] == 0 for r in R),
                         "baseline_correct": sum(r["baseline_correct"] for r in R),
                         "mcnemar": {"rule_only": n10, "baseline_only": n01, "p": pm},
                         "null": {"R": R_NULL, "seed": SEED_NULL, "mean": float(nl.mean()), "max": int(nl.max()),
                                  "p": (1 + int((nl >= uc).sum())) / (1 + R_NULL)}}
        res[k]["rows"] = rows
    order = sorted(mc, key=mc.get); holm = {}
    for i, kk in enumerate(order): holm[kk] = all(mc[order[j]] <= ALPHA / (len(order) - j) for j in range(i + 1))
    for k in S:
        for x in TARGETS:
            r = res[k][x]; gx = g[k][x]
            G = {"FPR_gate": gx["FPR_ok"], "power_gate": gx["power_ok"], "G1_tasks": r["tasks"] >= Q.MIN_TASKS,
                 "G2_precision": g2(r["tasks"], r["unique"], r["unique_correct"]), "G3_baseline_holm4": holm[(k, x)],
                 "G4_null": r["null"]["p"] <= ALPHA}
            r["gates"] = G
            if not (G["FPR_gate"] and G["power_gate"] and G["G1_tasks"]): v = "NOT TESTABLE"
            elif G["G2_precision"] and G["G3_baseline_holm4"] and G["G4_null"]: v = "VALIDATED"
            elif r["unique"] >= Q.MIN_UNIQUE and r["cp95_high"] < Q.PREC_MIN: v = "EXCLUDED (precision >= 0.80 excluded at 95 %)"
            else: v = "NOT VALIDATED"
            r["verdict"] = v
    final = {}
    for x in TARGETS:
        a, b = res["A"][x]["verdict"], res["B"][x]["verdict"]
        final[x] = "VALIDATED" if a == b == "VALIDATED" else (a if a == b else f"A: {a}; B: {b}")
    out = {"final_verdict": final, "sets": res, "gates": g, "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe007_results.json", "w"), indent=1)
    print(json.dumps({"final_verdict": final, **{k: {x: {kk: vv for kk, vv in res[k][x].items()} for x in TARGETS} for k in S}}, indent=1))

def apply():
    r = json.load(open("analysis/pe007_results.json")); ok = {x: r["final_verdict"][x] == "VALIDATED" for x in TARGETS}
    out = {"targets_validated": ok, "tablets": []}
    if any(ok.values()):
        tabs = Q.parse(os.path.join("data", "pe.atf"))
        for d in Q.damaged_set(tabs):
            if not ok[d["kind"]]: continue
            signs = set(d["visible"]).union(*[set(e) for e in d["entries"]]) | (set(d["total"]) if d["total"] else set())
            if signs & P.C_SUB_SIGNS: continue
            c = Q.solve(d["entries"], d["total"], d["kind"], d["visible"])
            out["tablets"].append({"pid": d["pid"], "slot": d["kind"], "line": d["label"], "atf_numerals": Q.numpart(d["line"]).strip(),
                                   "candidates": c, "n_candidates": len(c), "editor_reading": Q.key(d["editor"]) if d["editor"] else None})
    json.dump(out, open("analysis/pe007_restorations.json", "w"), indent=1); print(json.dumps({"validated": ok, "n": len(out["tablets"])}))

def audit():
    here = os.getcwd(); tmp = tempfile.mkdtemp()
    try:
        shutil.copytree("tools", os.path.join(tmp, "tools"), ignore=shutil.ignore_patterns("__pycache__")); os.makedirs(os.path.join(tmp, "analysis"))
        os.symlink(os.path.join(here, "data"), os.path.join(tmp, "data"))
        for f in ("pe006_gates.json", "pe005_gates.json"): shutil.copy(os.path.join("analysis", f), os.path.join(tmp, "analysis"))
        subprocess.run([sys.executable, "tools/pe006_cap.py", "test"], cwd=tmp, check=True, capture_output=True)
        a = json.load(open("analysis/pe006_results.json")); b = json.load(open(os.path.join(tmp, "analysis/pe006_results.json")))
        h = b["H1_fresh"]; tab = [[h["a_cap_bal"], h["b_cap_not"]], [h["c_nocap_bal"], h["d_nocap_not"]]]
        # independent re-check of the one-sided Fisher p by direct hypergeometric sum (no PE005 code)
        a1, b1, c1, d1 = tab[0] + tab[1]; n = a1 + b1 + c1 + d1; r1 = a1 + b1; k1 = a1 + c1
        p = sum(math.comb(k1, j) * math.comb(n - k1, r1 - j) for j in range(0, a1 + 1)) / math.comb(n, r1)
        out = {"pe006_results_identical": a == b, "H1_table": tab, "p_one_sided_recomputed_independently": p,
               "matches_published_0.0049": round(p, 4) == 0.0049}
        json.dump(out, open("analysis/pe007_pe006_audit.json", "w"), indent=1); print(json.dumps(out, indent=1))
    finally: shutil.rmtree(tmp)

if __name__ == "__main__":
    os.makedirs("analysis", exist_ok=True)
    {"inventory": inventory, "gates": gates, "test": test, "apply": apply, "audit": audit}[sys.argv[1]]()
