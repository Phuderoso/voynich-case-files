#!/usr/bin/env python3
"""PE002 - Do the reverse lines of multi-line proto-Elamite accounts equal sums of obverse entries,
one number system at a time, beyond a magnitude-stratified line-shuffle null?

Pre-registered in case-file/PE002-multiline-reverses.md (committed with this tool before any observed match count).
Usage (from expeditions/proto-elamite/, after `python3 tools/pe001_totals.py fetch`):
    python3 tools/pe002_multiline.py curve   # stage 1: FPR + power curve per test (no observed statistic)
    python3 tools/pe002_multiline.py audit   # PE001 audit: power curve of PE001's own H1 design
    python3 tools/pe002_multiline.py test    # stage 2: observed statistics, gates read from stage 1, BH
Needs numpy. Exact integer arithmetic throughout (values in each system's smallest unit).
"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe001_totals as P

SYS = {**P.SYSTEMS, "C": P.c_table()}
ALLSIGNS = set().union(*[set(t) for t in SYS.values()])
METRICS = ("subset", "run")
SUBSET_CAP = 12          # subset metric only on tablets with <= 12 entries valid in the system
MIN_LINES = 20           # fewer testable reverse lines -> EXCLUDED
N_STRATA = 5             # magnitude strata (quintiles of line value) for the primary null
F_GRID = (0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50)
F_GATE = 0.25            # power gate is read at this plant fraction
ALPHA_GATE = 0.05 / 8    # per-test threshold for the power gate (Bonferroni over 8 tests; BH is less strict)
REPS, R_CURVE, R_TEST = 200, 999, 9999
SEED_CURVE, SEED_TEST, SEED_AUDIT = 203, 202, 204

def load():
    """Tablets with >= 2 reverse numeral lines (any state). Line-level damage rule: only lines whose numerals are
    intact (pe001 'strict_bad' false) are used; entries = intact obverse numeral lines; candidate totals = intact
    reverse numeral lines. Lines with 'n' counts or unmapped signs are dropped."""
    tabs = P.parse(os.path.join("data", "pe.atf")); out = []
    for t in tabs:
        obs = [l for l in t["lines"] if l["surf"] == "o" and l["nums"]]
        rev = [l for l in t["lines"] if l["surf"] == "r" and l["nums"]]
        if len(rev) < 2: continue
        ok = lambda l: (not l["strict_bad"])
        e = [P.notation(l["nums"]) for l in obs if ok(l)]; e = [x for x in e if x is not None and set(x) <= ALLSIGNS]
        r = [P.notation(l["nums"]) for l in rev if ok(l)]; r = [x for x in r if x is not None and set(x) <= ALLSIGNS]
        if len(e) >= 2 and r: out.append({"pid": t["pid"], "entries": e, "rev": r})
    return out

def reach(vals, metric):
    """Set of sums of >= 2 entries: any subset (subset) or contiguous run (run). vals = list of int or None
    (None = entry not valid in this system; breaks runs, absent from subsets)."""
    if metric == "run":
        s = set()
        for i in range(len(vals)):
            acc = 0; k = 0
            for j in range(i, len(vals)):
                if vals[j] is None: break
                acc += vals[j]; k += 1
                if k >= 2: s.add(acc)
        return s
    v = [x for x in vals if x is not None]
    one, two = set(), set()
    for x in v:
        two |= {a + x for a in two} | {a + x for a in one}
        one.add(x)
    return two

def build(tabs, X, metric):
    tb = SYS[X]; pos_tab, line_val, reaches, ents, pids = [], [], [], [], []
    for t in tabs:
        vals = [P.value(e, tb) for e in t["entries"]]
        nvalid = sum(v is not None for v in vals)
        if nvalid < 2: continue
        if metric == "subset" and nvalid > SUBSET_CAP: continue
        rv = [P.value(r, tb) for r in t["rev"]]; rv = [v for v in rv if v is not None and v > 0]
        if not rv: continue
        ti = len(reaches); reaches.append(reach(vals, metric)); ents.append(vals); pids.append(t["pid"])
        for v in rv: pos_tab.append(ti); line_val.append(v)
    return {"pos_tab": np.array(pos_tab, dtype=int), "vals": np.array(line_val, dtype=object),
            "reaches": reaches, "ents": ents, "pids": pids}

def strata(vals):
    v = np.array([float(x) for x in vals]); r = np.argsort(np.argsort(v, kind="stable"), kind="stable")
    return (r * N_STRATA) // len(v)

def hitmatrix(d, vals):
    n = len(vals); H = np.zeros((n, n), dtype=np.int8)
    for j, v in enumerate(vals):
        for i in range(n): H[i, j] = v in d["reaches"][d["pos_tab"][i]]
    return H

def perm_stats(H, st, R, rng, stratified=True):
    n = H.shape[0]; groups = [np.where(st == s)[0] for s in np.unique(st)] if stratified else [np.arange(n)]
    tot = np.zeros(R, dtype=np.int64)
    for g in groups:
        keys = rng.random((R, len(g))); perm = g[np.argsort(keys, axis=1)]
        tot += H[g[None, :], perm].sum(axis=1)
    return tot

def ptest(H, st, R, rng, stratified=True):
    obs = int(np.trace(H)); null = perm_stats(H, st, R, rng, stratified)
    return obs, (1 + int((null >= obs).sum())) / (1 + R), null

def plant(d, f, rng, metric):
    """Destroy signal (shuffle all lines once), then plant in a fraction f of positions the canonical sum of a
    random admissible >= 2-entry subset / run of that position's own tablet. Returns new value array."""
    vals = list(d["vals"][rng.permutation(len(d["vals"]))]); n = len(vals)
    for i in rng.choice(n, int(round(f * n)), replace=False):
        ev = d["ents"][d["pos_tab"][i]]
        if metric == "run":
            runs = []
            for a in range(len(ev)):
                for b in range(a + 2, len(ev) + 1):
                    if all(x is not None for x in ev[a:b]): runs.append(sum(ev[a:b]))
            if runs: vals[i] = runs[rng.integers(len(runs))]
        else:
            v = [x for x in ev if x is not None]; k = int(rng.integers(2, len(v) + 1))
            vals[i] = sum(v[j] for j in rng.choice(len(v), k, replace=False))
    return np.array(vals, dtype=object)

def tests(tabs):
    return [(X, m) for m in METRICS for X in ("S", "D", "B", "C")]

def curve_one(args):
    idx, X, m = args; tabs = load(); rng = np.random.default_rng(SEED_CURVE * 100 + idx); t0 = time.time()
    d = build(tabs, X, m); n = len(d["vals"]); key = f"{X}-{m}"
    row = {"lines": n, "tablets": len(d["reaches"]), "seed": SEED_CURVE * 100 + idx}
    if n < MIN_LINES: row["status"] = "EXCLUDED (< %d lines)" % MIN_LINES; return key, row
    pw = {}
    for f in F_GRID:
        hits05 = hitsg = 0
        for _ in range(REPS):
            v = plant(d, f, rng, m); H = hitmatrix(d, v)
            _, p, _ = ptest(H, strata(v), R_CURVE, rng); hits05 += p <= 0.05; hitsg += p <= ALPHA_GATE
        pw[str(f)] = {"rate_p_le_0.05": hits05 / REPS, "rate_p_le_gate": hitsg / REPS}
        print(key, f, pw[str(f)], round(time.time() - t0), flush=True)
    f80 = next((f for f in F_GRID[1:] if pw[str(f)]["rate_p_le_gate"] >= 0.8), None)
    fpr_ok = pw["0.0"]["rate_p_le_0.05"] <= 0.08 and pw["0.0"]["rate_p_le_gate"] <= 0.02
    pow_ok = pw[str(F_GATE)]["rate_p_le_gate"] >= 0.8
    row.update({"curve": pw, "f80": f80, "gate_FPR": fpr_ok, "gate_power": pow_ok,
                "status": "TESTABLE" if fpr_ok and pow_ok else "NOT TESTABLE (gate)"})
    return key, row

def curve():
    """Stage 1, one process per test (seed 203*100 + test index)."""
    from multiprocessing import Pool
    t0 = time.time(); tabs = load(); jobs = [(i, X, m) for i, (X, m) in enumerate(tests(tabs))]
    with Pool(8) as pool: rows = pool.map(curve_one, jobs)
    res = {"n_tablets": len(tabs), "tests": dict(rows), "runtime_s": round(time.time() - t0, 1)}
    json.dump(res, open("analysis/pe002_curve.json", "w"), indent=1)

def audit():
    """PE001 audit: power curve of PE001's own H1 design (strict 38, total shuffle, R=499, p<=0.025)."""
    t0 = time.time(); tabs = P.parse(os.path.join("data", "pe.atf")); S, _ = P.candidates(tabs, "strict")
    rng = np.random.default_rng(SEED_AUDIT); n = len(S)
    def canon(i):
        for name in ["C", "S", "D", "B"]:
            tb = SYS[name]; vs = [P.value(e, tb) for e in S[i]["entries"]]
            if any(v is None for v in vs): continue
            c = P.canonical(sum(vs), tb)
            if c: return c
    out = {}
    for f in (0.10, 0.20, 0.30, 0.40, 0.50):
        det = 0
        for _ in range(REPS):
            tots = [S[j]["total"] for j in rng.permutation(n)]
            for i in rng.choice(n, max(1, int(n * f)), replace=False): tots[i] = canon(i)
            H = np.array([[bool(P.balances(S[i]["entries"], tots[j])) for j in range(n)] for i in range(n)], dtype=np.int8)
            _, p, _ = ptest(H, np.zeros(n, dtype=int), 499, rng, stratified=False); det += p <= 0.025
        out[str(f)] = det / REPS; print("PE001 audit f", f, det / REPS, round(time.time() - t0), flush=True)
    json.dump({"pe001_power_curve": out, "runtime_s": round(time.time() - t0, 1)}, open("analysis/pe002_pe001_audit.json", "w"), indent=1)

def test():
    t0 = time.time(); cur = json.load(open("analysis/pe002_curve.json")); tabs = load()
    rng = np.random.default_rng(SEED_TEST); res = {"n_tablets": len(tabs), "tests": {}}
    pv = {}
    for X, m in tests(tabs):
        key = f"{X}-{m}"; c = cur["tests"][key]; d = build(tabs, X, m); row = {"lines": len(d["vals"]), "status_stage1": c["status"]}
        H = hitmatrix(d, d["vals"]); st = strata(d["vals"])
        obs, p, null = ptest(H, st, R_TEST, rng)
        _, pu, nullu = ptest(H, st, R_TEST, rng, stratified=False)
        singles = sum(int(v in set(x for x in d["ents"][d["pos_tab"][i]] if x is not None)) for i, v in enumerate(d["vals"]))
        fulls = sum(int(v == sum(x for x in d["ents"][d["pos_tab"][i]] if x is not None)) for i, v in enumerate(d["vals"]))
        row.update({"matched": obs, "null_mean": float(null.mean()), "null_max": int(null.max()), "p": p,
                    "unstratified_null_mean": float(nullu.mean()), "p_unstratified": pu,
                    "descr_equal_single_entry": singles, "descr_equal_full_sum": fulls,
                    "matched_pids": sorted({d["pids"][d["pos_tab"][i]] for i in range(len(d["vals"])) if H[i, i]})})
        if c["status"] == "TESTABLE": pv[key] = p
        res["tests"][key] = row
    # BH at q = 0.05 over the TESTABLE tests
    ks = sorted(pv, key=pv.get); m = len(ks); kmax = 0
    for i, k in enumerate(ks, 1):
        if pv[k] <= 0.05 * i / m: kmax = i
    for i, k in enumerate(ks, 1):
        res["tests"][k]["verdict"] = "SUPPORTED" if i <= kmax else "NOT DETECTED"
    for k, row in res["tests"].items():
        row.setdefault("verdict", row["status_stage1"])
    res["BH_m"] = m; res["runtime_s"] = round(time.time() - t0, 1)
    json.dump(res, open("analysis/pe002_results.json", "w"), indent=1)
    print(json.dumps(res, indent=1))

if __name__ == "__main__":
    os.makedirs("analysis", exist_ok=True)
    {"curve": curve, "audit": audit, "test": test}[sys.argv[1]]()
