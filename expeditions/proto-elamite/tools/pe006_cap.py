#!/usr/bin/env python3
"""PE006 - Fresh-sample test of the PE005 capacity lead: do capacity (grain) single-total tablets balance less often?

Pre-registered in case-file/PE006-capacity-fresh-sample.md (committed with this tool BEFORE any balance label of the
new tablets was computed). Usage (from expeditions/proto-elamite/, after `python3 tools/pe001_totals.py fetch`):
    python3 tools/pe006_cap.py inventory  # label-free: the new (fresh) set, CAP prevalence, R/H split, editions
    python3 tools/pe006_cap.py gates      # FPR gate (CAP permutation) + planted-feature power gate on the new set
    python3 tools/pe006_cap.py test       # primary H1 + descriptive pooled / sensitivity / edition-stratified
    python3 tools/pe006_cap.py audit      # PE005 audit: re-run `pe005_balance.py test` in a scratch dir, compare
Pure Python (exact Fisher by hypergeometric enumeration), numpy only via the imported PE004 tool.

FRESH SET (disjoint from the 43 PE005 tablets): single-total tablets that pass the PE004 shape rules (no broken
$-line on obverse/reverse, no primed line, >= 2 obverse numeral slots, exactly 1 reverse numeral slot) and have
>= 1 damaged numeral part ([ ] # ? in the numeral part), where EVERY damaged numeral part is COMPLETELY read by the
editor: after removing [ ] # ? the part has no '...', no n(...), no x, and every notation maps to S/D/B/C.
Classes: R = at least one numeral part carries an editor restoration in [ ]; H = only #/? flags (signs damaged
but read). Tablets whose signs admit no common system are excluded (cannot balance by construction).
CAP = capacity sub-unit signs (N39B, N24, N30C, N30D, N39C) present in the entries or total (PE005 definition).
Label: balances = sum(entries) == total in >= 1 admitted system (pe001_totals.balances, Englund sub-units).
"""
import json, os, re, sys, time, random, shutil, subprocess, tempfile, csv
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe004_restore as Q
import pe005_balance as F
import pe001_totals as P

ALPHA = 0.05
R_FPR, SEED_FPR = 2000, 601
R_POW, SEED_POW, W_PLANT = 2000, 602, 4.0
R_STRAT, SEED_STRAT = 20000, 603
FPR_MAX, POWER_MIN = 0.06, 0.80

def clean(np_):
    return Q.outer(np_).replace("[", " ").replace("]", " ").replace("#", "").replace("?", "")

def complete(np_):
    if "..." in np_ or re.search(r"(^|[\s\[])n\(|(^|\s)x(\s|$)", np_): return None
    c = Q.notation(Q.NUM.findall(clean(np_)))
    return c if Q.valid(c) else None

def fresh_set(tabs):
    old = {t["pid"] for t in Q.calibration_set(tabs)}; out = []; why = Counter()
    for t in tabs:
        if t["pid"] in old: continue
        if not Q.shape_ok(t): continue
        o, r = Q.slots(t)
        if len(o) < 2 or len(r) != 1: continue
        dl = [l for l in o + r if l["dmg"]]
        if not dl: why["intact but not mapped / not in PE005 set"] += 1; continue
        ns = []; ok = True
        for l in o + r:
            c = complete(Q.numpart(l["body"])) if l["dmg"] else Q.notation(l["nums"])
            if not Q.valid(c): ok = False; break
            ns.append(c)
        if not ok: why["damaged numeral not completely read"] += 1; continue
        cls = "R" if any("[" in Q.numpart(l["body"]) or "]" in Q.numpart(l["body"]) for l in dl) else "H"
        out.append({"pid": t["pid"], "entries": ns[:-1], "total": ns[-1], "cls": cls, "n_damaged": len(dl)})
    return out, why

def editions():
    csv.field_size_limit(10**9); ed = {}
    for row in csv.DictReader(open(os.path.join("data", "cdli_cat.csv"), encoding="utf-8", errors="replace")):
        if row["id_text"].strip().isdigit():
            pp = (row.get("primary_publication") or "").strip()
            m = re.match(r"([A-Za-z]+\s*\d+[A-Za-z]?)", pp); ed["P%06d" % int(row["id_text"])] = m.group(1) if m else (pp or "?")
    return ed

def load():
    path = os.path.join("data", "pe.atf"); tabs = Q.parse(path); byid = {t["pid"]: t for t in tabs}
    raw = F.raw_blocks(path); fs, why = fresh_set(tabs); rows = []; nocover = []
    for t in fs:
        f, nsys = F.features(t, raw[t["pid"]], byid[t["pid"]])
        if nsys == 0: nocover.append(t["pid"]); continue
        rows.append({"pid": t["pid"], "cap": f["CAP"], "cls": t["cls"], "t": t})
    return rows, nocover, why

def label(r): return bool(P.balances(r["t"]["entries"], r["t"]["total"]))

def inventory():
    rows, nocover, why = load(); ed = editions()
    out = {"fresh_set": len(rows), "no_common_system": nocover, "excluded_counts": dict(why),
           "class_R": sum(r["cls"] == "R" for r in rows), "class_H": sum(r["cls"] == "H" for r in rows),
           "CAP": sum(r["cap"] for r in rows), "CAP_in_R": sum(r["cap"] and r["cls"] == "R" for r in rows),
           "CAP_in_H": sum(r["cap"] and r["cls"] == "H" for r in rows),
           "editions": dict(Counter(ed.get(r["pid"], "?") for r in rows).most_common()),
           "pids": [r["pid"] for r in rows]}
    json.dump(out, open("analysis/pe006_inventory.json", "w"), indent=1); print(json.dumps({k: v for k, v in out.items() if k != "pids"}, indent=1))

def p_less(x, y): return F.fisher(x, y)[5]   # one-sided: feature -> fewer balancing tablets

def gates():
    rows, _, _ = load(); y = [label(r) for r in rows]; x = [r["cap"] for r in rows]; n = len(rows); k = sum(x)
    rng = random.Random(SEED_FPR); fp = 0
    for _ in range(R_FPR):
        xs = x[:]; rng.shuffle(xs); fp += p_less(xs, y) <= ALPHA
    rng = random.Random(SEED_POW); hit = 0; hit9 = 0
    def plant(w):
        idx = list(range(n)); wt = [w if not y[i] else 1.0 for i in idx]; ch = set()
        for _ in range(k):
            tot = sum(wt[i] for i in idx if i not in ch); u = rng.random() * tot; acc = 0
            for i in idx:
                if i in ch: continue
                acc += wt[i]
                if acc >= u: ch.add(i); break
        return [i in ch for i in idx]
    for _ in range(R_POW): hit += p_less(plant(W_PLANT), y) <= ALPHA
    for _ in range(R_POW): hit9 += p_less(plant(9.0), y) <= ALPHA
    out = {"n": n, "CAP_prevalence": k, "n_balance": sum(y), "FPR": fp / R_FPR, "FPR_ok": fp / R_FPR <= FPR_MAX,
           "power_w4": hit / R_POW, "power_ok": hit / R_POW >= POWER_MIN, "power_w9_descriptive": hit9 / R_POW,
           "seeds": [SEED_FPR, SEED_POW]}
    json.dump(out, open("analysis/pe006_gates.json", "w"), indent=1); print(json.dumps(out, indent=1))

def strat_p(x, y, g, R, seed):
    """Edition-stratified permutation: CAP shuffled within each edition; statistic = CAP & balancing count (low = effect)."""
    obs = sum(a and b for a, b in zip(x, y)); rng = random.Random(seed); groups = {}
    for i, gi in enumerate(g): groups.setdefault(gi, []).append(i)
    le = 0
    for _ in range(R):
        xs = x[:]
        for idx in groups.values():
            v = [x[i] for i in idx]; rng.shuffle(v)
            for i, vi in zip(idx, v): xs[i] = vi
        le += sum(a and b for a, b in zip(xs, y)) <= obs
    return (1 + le) / (1 + R)

def table(x, y):
    a, b, c, d, two, less, more = F.fisher(x, y); return {"a_cap_bal": a, "b_cap_not": b, "c_nocap_bal": c, "d_nocap_not": d,
            "p_one_sided_less": less, "p_two_sided": two}

def test():
    g = json.load(open("analysis/pe006_gates.json")); rows, _, _ = load(); ed = editions()
    y = [label(r) for r in rows]; x = [r["cap"] for r in rows]
    h1 = table(x, y)
    if not (g["FPR_ok"] and g["power_ok"]): verdict = "NOT TESTABLE"
    elif h1["p_one_sided_less"] <= ALPHA: verdict = "SUPPORTED"
    else: verdict = "NOT DETECTED"
    Hi = [i for i, r in enumerate(rows) if r["cls"] == "H"]; Ri = [i for i, r in enumerate(rows) if r["cls"] == "R"]
    _, old, _ = F.load(); yo = [F.label(r) for r in old]; xo = [r["f"]["CAP"] for r in old]
    out = {"verdict_H1": verdict, "H1_fresh": h1, "gates": g,
           "S1_H_only": table([x[i] for i in Hi], [y[i] for i in Hi]),
           "S1b_R_only": table([x[i] for i in Ri], [y[i] for i in Ri]),
           "pooled_PE005_plus_fresh_descriptive": table(xo + x, yo + y),
           "edition_stratified_p_descriptive": strat_p(x, y, [ed.get(r["pid"], "?") for r in rows], R_STRAT, SEED_STRAT),
           "per_tablet": [{"pid": r["pid"], "cls": r["cls"], "cap": r["cap"], "balances": yi, "edition": ed.get(r["pid"], "?")}
                          for r, yi in zip(rows, y)]}
    json.dump(out, open("analysis/pe006_results.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "per_tablet"}, indent=1))

def audit():
    here = os.getcwd(); tmp = tempfile.mkdtemp()
    try:
        shutil.copytree("tools", os.path.join(tmp, "tools")); os.makedirs(os.path.join(tmp, "analysis"))
        os.symlink(os.path.join(here, "data"), os.path.join(tmp, "data"))
        shutil.copy("analysis/pe005_gates.json", os.path.join(tmp, "analysis"))
        subprocess.run([sys.executable, "tools/pe005_balance.py", "test"], cwd=tmp, check=True, capture_output=True)
        a = json.load(open("analysis/pe005_results.json")); b = json.load(open(os.path.join(tmp, "analysis/pe005_results.json")))
        strip = lambda d: {k: v for k, v in d.items() if "time" not in k}
        same = strip(a) == strip(b)
        def find(d):  # locate the CAP block wherever it sits in the results tree (fix after first run: key path)
            if isinstance(d, dict):
                if "CAP" in d and isinstance(d["CAP"], dict) and "table_a_b_c_d" in d["CAP"]: return d["CAP"]
                for v in d.values():
                    r = find(v)
                    if r: return r
            return None
        cap = find(b)
        out = {"pe005_results_identical_except_time": same, "CAP_recomputed": cap}
        json.dump(out, open("analysis/pe006_pe005_audit.json", "w"), indent=1); print(json.dumps(out, indent=1))
    finally: shutil.rmtree(tmp)

if __name__ == "__main__":
    {"inventory": inventory, "gates": gates, "test": test, "audit": audit}[sys.argv[1]]()
