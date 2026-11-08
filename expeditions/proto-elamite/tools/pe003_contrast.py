#!/usr/bin/env python3
"""PE003 - Exact-vs-shifted contrast: is a reverse numeral line equal to a sum of its own tablet's obverse entries
MORE often than the same line moved by +/- one unit of its smallest sign? Single-total and multi-line tablets pooled.

Pre-registered in case-file/PE003-exact-vs-shifted.md (committed with this tool before any observed statistic).
Usage (from expeditions/proto-elamite/, after `python3 tools/pe001_totals.py fetch`):
    python3 tools/pe003_contrast.py inventory  # structural counts only (lines/tablets per test), no match counts
    python3 tools/pe003_contrast.py curve      # stage 1: FPR, near-sum specificity, power curve (no observed statistic)
    python3 tools/pe003_contrast.py test       # stage 2: observed contrast, gates read from stage 1, BH
    python3 tools/pe003_contrast.py audit      # PE002 audit: re-run PE002 stage 2 in a scratch dir, compare JSON
Needs numpy. Exact integer arithmetic (values in each system's smallest unit).
"""
import json, os, sys, time, shutil, subprocess, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe001_totals as P

SYS = {**P.SYSTEMS, "C": P.c_table()}
ALLSIGNS = set().union(*[set(t) for t in SYS.values()])
SYSTEMS = ("S", "D", "B", "C"); METRICS = ("full", "subset")
SUBSET_CAP = 12; MIN_LINES = 20; N_STRATA = 5
F_GRID = (0.0, 0.10, 0.20, 0.30); F_GATE = 0.20; F_NEAR = 0.20
ALPHA_GATE = 0.05 / 8
REPS, R_CURVE, R_TEST = 500, 999, 9999
SEED_CURVE, SEED_TEST = 303, 302

def load():
    """Tablets with >= 2 intact obverse numeral lines and >= 1 intact reverse numeral line (single-total and
    multi-line pooled). Line-level damage rule of PE002. 'obv_whole' = no damaged obverse numeral line and no
    broken/missing obverse $-line (needed for the 'full' metric)."""
    out = []
    for t in P.parse(os.path.join("data", "pe.atf")):
        obs = [l for l in t["lines"] if l["surf"] == "o" and l["nums"]]
        rev = [l for l in t["lines"] if l["surf"] == "r" and l["nums"]]
        good = lambda L: [x for x in (P.notation(l["nums"]) for l in L if not l["strict_bad"]) if x is not None and set(x) <= ALLSIGNS]
        e, r = good(obs), good(rev)
        whole = (not t["broken"]["o"]) and all(not l["strict_bad"] for l in obs) and len(e) == len(obs)
        if len(e) >= 2 and r:
            out.append({"pid": t["pid"], "entries": e, "rev": r, "obv_whole": whole, "n_rev_all": len(rev)})
    return out

def unit(v, tb):
    """Shift unit of a value: value of the smallest sign in its greedy canonical notation in the system
    (a function of the value alone, so it travels with the value under permutation and planting)."""
    c = P.canonical(v, tb)
    return min(tb[s] for s in c) if c else min(tb.values())

def reach(vals, metric):
    v = [x for x in vals if x is not None]
    if metric == "full": return {sum(v)}
    one, two = set(), set()
    for x in v:
        two |= {a + x for a in two} | {a + x for a in one}
        one.add(x)
    return two

def build(tabs, X, metric):
    tb = SYS[X]; pos_tab, vals, reaches, ents, pids, single = [], [], [], [], [], []
    for t in tabs:
        ev = [P.value(e, tb) for e in t["entries"]]; nv = sum(x is not None for x in ev)
        if nv < 2: continue
        if metric == "full" and (not t["obv_whole"] or nv != len(ev)): continue
        if metric == "subset" and nv > SUBSET_CAP: continue
        rv = [P.value(r, tb) for r in t["rev"]]; rv = [x for x in rv if x is not None and x > 0]
        if not rv: continue
        ti = len(reaches); reaches.append(reach(ev, metric)); ents.append([x for x in ev if x is not None]); pids.append(t["pid"])
        for x in rv: pos_tab.append(ti); vals.append(x); single.append(t["n_rev_all"] == 1)
    return {"X": X, "metric": metric, "pos_tab": np.array(pos_tab, dtype=int), "vals": np.array(vals, dtype=object),
            "reaches": reaches, "ents": ents, "pids": pids, "single": np.array(single, dtype=bool)}

def tie_strata(vals):
    """Magnitude classes by cumulative count; equal values never split (PE002 D2 fix)."""
    v = np.array([float(x) for x in vals]); u = np.unique(v)
    order = np.searchsorted(u, v); cnt = np.bincount(order); cum = np.cumsum(cnt) - cnt
    return ((cum * N_STRATA) // len(v))[order]

def kmatrix(d, vals):
    """K[i, j] = 2*[v_j in reach_i] - [v_j - u_j in reach_i] - [v_j + u_j in reach_i]; row = position (tablet),
    column = value. Trace/2 = exact matches minus mean shifted matches."""
    tb = SYS[d["X"]]; n = len(vals); T = len(d["reaches"]); K = np.zeros((n, n), dtype=np.int8)
    for j, v in enumerate(vals):
        u = unit(v, tb); a, b = v - u, v + u
        kt = np.array([2 * (v in R) - (a in R) - (b in R) for R in d["reaches"]], dtype=np.int8)
        K[:, j] = kt[d["pos_tab"]]
    return K

def perm_null(K, st, R, rng):
    groups = [np.where(st == s)[0] for s in np.unique(st)]; tot = np.zeros(R, dtype=np.int64)
    for g in groups:
        perm = g[np.argsort(rng.random((R, len(g))), axis=1)]
        tot += K[g[None, :], perm].sum(axis=1)
    return tot

def ptest(K, st, R, rng):
    obs = int(np.trace(K)); null = perm_null(K, st, R, rng)
    return obs, (1 + int((null >= obs).sum())) / (1 + R), null

def destroy(d, rng):
    """Destroy any line-tablet link: permute values within tie-aware magnitude classes (keeps magnitudes)."""
    v = d["vals"].copy(); st = tie_strata(v)
    for s in np.unique(st):
        g = np.where(st == s)[0]; v[g] = v[g[rng.permutation(len(g))]]
    return v

def planted_sum(d, i, rng):
    ev = d["ents"][d["pos_tab"][i]]
    if d["metric"] == "full": return sum(ev)
    k = int(rng.integers(2, len(ev) + 1)); return sum(ev[j] for j in rng.choice(len(ev), k, replace=False))

def plant(d, f, rng, near=False):
    """Exact plant: a fraction f of positions get the sum of a random admissible set (full: all entries) of their own
    tablet. Near plant (specificity control for unit/range likeness): the same sum moved by +/- its own unit."""
    v = destroy(d, rng); n = len(v); tb = SYS[d["X"]]
    for i in rng.choice(n, int(round(f * n)), replace=False):
        s = planted_sum(d, i, rng)
        if near:
            u = unit(s, tb); s = s + u if (s - u <= 0 or rng.random() < 0.5) else s - u
        v[i] = s
    return v

def tests():
    return [(X, m) for m in METRICS for X in SYSTEMS]

def inventory():
    tabs = load(); out = {"n_tablets": len(tabs), "single_total_tablets": sum(t["n_rev_all"] == 1 for t in tabs), "tests": {}}
    for X, m in tests():
        d = build(tabs, X, m)
        out["tests"][f"{X}-{m}"] = {"lines": len(d["vals"]), "tablets": len(d["reaches"]), "lines_on_single_total_tablets": int(d["single"].sum())}
    print(json.dumps(out, indent=1)); json.dump(out, open("analysis/pe003_inventory.json", "w"), indent=1)

def curve_one(args):
    idx, X, m = args; tabs = load(); rng = np.random.default_rng(SEED_CURVE * 100 + idx); t0 = time.time()
    d = build(tabs, X, m); n = len(d["vals"]); key = f"{X}-{m}"
    row = {"lines": n, "tablets": len(d["reaches"]), "seed": SEED_CURVE * 100 + idx}
    if n < MIN_LINES: row["status"] = "EXCLUDED (< %d lines)" % MIN_LINES; return key, row
    pw = {}
    conds = [(str(f), f, False) for f in F_GRID] + [("near_%s" % F_NEAR, F_NEAR, True)]
    for name, f, near in conds:
        h05 = hg = 0
        for _ in range(REPS):
            v = plant(d, f, rng, near); K = kmatrix(d, v)
            _, p, _ = ptest(K, tie_strata(v), R_CURVE, rng); h05 += p <= 0.05; hg += p <= ALPHA_GATE
        pw[name] = {"rate_p_le_0.05": h05 / REPS, "rate_p_le_gate": hg / REPS}
        print(key, name, pw[name], round(time.time() - t0), flush=True)
    f80 = next((f for f in F_GRID[1:] if pw[str(f)]["rate_p_le_gate"] >= 0.8), None)
    fpr_ok = pw["0.0"]["rate_p_le_0.05"] <= 0.08 and pw["0.0"]["rate_p_le_gate"] <= 0.02
    spec_ok = pw["near_%s" % F_NEAR]["rate_p_le_0.05"] <= 0.08
    pow_ok = pw[str(F_GATE)]["rate_p_le_gate"] >= 0.8
    row.update({"curve": pw, "f80": f80, "gate_FPR": fpr_ok, "gate_specificity_near": spec_ok, "gate_power": pow_ok,
                "status": "TESTABLE" if fpr_ok and spec_ok and pow_ok else "NOT TESTABLE (gate)",
                "runtime_s": round(time.time() - t0, 1)})
    return key, row

def curve():
    from multiprocessing import Pool
    t0 = time.time(); jobs = [(i, X, m) for i, (X, m) in enumerate(tests())]
    with Pool(8) as pool: rows = pool.map(curve_one, jobs)
    json.dump({"tests": dict(rows), "runtime_s": round(time.time() - t0, 1)}, open("analysis/pe003_curve.json", "w"), indent=1)

def test():
    t0 = time.time(); cur = json.load(open("analysis/pe003_curve.json")); tabs = load()
    rng = np.random.default_rng(SEED_TEST); res = {"n_tablets": len(tabs), "tests": {}}; pv = {}
    for X, m in tests():
        key = f"{X}-{m}"; c = cur["tests"][key]; d = build(tabs, X, m); v = d["vals"]; tb = SYS[X]
        row = {"lines": len(v), "status_stage1": c["status"]}
        if len(v) < MIN_LINES: row["verdict"] = c["status"]; res["tests"][key] = row; continue
        K = kmatrix(d, v); obs, p, null = ptest(K, tie_strata(v), R_TEST, rng)
        E = [int(v[i] in d["reaches"][d["pos_tab"][i]]) for i in range(len(v))]
        O = [((v[i] - unit(v[i], tb)) in d["reaches"][d["pos_tab"][i]]) + ((v[i] + unit(v[i], tb)) in d["reaches"][d["pos_tab"][i]]) for i in range(len(v))]
        sg = d["single"]
        row.update({"exact": sum(E), "shifted_mean": sum(O) / 2, "contrast": obs / 2, "null_contrast_mean": float(null.mean()) / 2,
                    "null_contrast_max": int(null.max()) / 2, "p": p,
                    "descr_single_total_lines": {"n": int(sg.sum()), "exact": int(sum(e for e, s in zip(E, sg) if s)), "shifted_mean": sum(o for o, s in zip(O, sg) if s) / 2},
                    "descr_multi_line_lines": {"n": int((~sg).sum()), "exact": int(sum(e for e, s in zip(E, sg) if not s)), "shifted_mean": sum(o for o, s in zip(O, sg) if not s) / 2},
                    "exact_pids": sorted({d["pids"][d["pos_tab"][i]] for i in range(len(v)) if E[i]})})
        if c["status"] == "TESTABLE": pv[key] = p
        res["tests"][key] = row; print(key, {k: row[k] for k in ("exact", "shifted_mean", "contrast", "null_contrast_mean", "p")}, flush=True)
    ks = sorted(pv, key=pv.get); M = len(ks); kmax = 0
    for i, k in enumerate(ks, 1):
        if pv[k] <= 0.05 * i / M: kmax = i
    for i, k in enumerate(ks, 1): res["tests"][k]["verdict"] = "SUPPORTED" if i <= kmax else "NOT DETECTED"
    for row in res["tests"].values(): row.setdefault("verdict", row["status_stage1"])
    res["BH_m"] = M; res["runtime_s"] = round(time.time() - t0, 1)
    json.dump(res, open("analysis/pe003_results.json", "w"), indent=1)

def audit():
    """PE002 audit: re-run PE002 stage 2 (seed 202) on a scratch copy; compare every matched count and p with the
    committed analysis/pe002_results.json."""
    here = os.getcwd(); tmp = tempfile.mkdtemp()
    for sub in ("tools", "data", "analysis"): shutil.copytree(os.path.join(here, sub), os.path.join(tmp, sub), ignore=shutil.ignore_patterns("__pycache__"))
    subprocess.run([sys.executable, "tools/pe002_multiline.py", "test"], cwd=tmp, check=True, capture_output=True)
    new = json.load(open(os.path.join(tmp, "analysis/pe002_results.json"))); old = json.load(open("analysis/pe002_results.json"))
    diff = {k: {f: (old["tests"][k].get(f), new["tests"][k].get(f)) for f in ("matched", "p", "verdict") if old["tests"][k].get(f) != new["tests"][k].get(f)} for k in old["tests"]}
    diff = {k: v for k, v in diff.items() if v}
    out = {"pe002_stage2_rerun_identical": not diff, "differences": diff}
    json.dump(out, open("analysis/pe003_pe002_audit.json", "w"), indent=1); print(out); shutil.rmtree(tmp)

if __name__ == "__main__":
    os.makedirs("analysis", exist_ok=True)
    {"inventory": inventory, "curve": curve, "test": test, "audit": audit}[sys.argv[1]]()
