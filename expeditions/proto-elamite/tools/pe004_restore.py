#!/usr/bin/env python3
"""PE004 - Restoring damaged numerals with the grand-total rule (constraint solving), calibrated first by
leave-one-out on intact single-total tablets.

Pre-registered in case-file/PE004-restoration.md (committed with this tool before any calibration number).
Usage (from expeditions/proto-elamite/, after `python3 tools/pe001_totals.py fetch`):
    python3 tools/pe004_restore.py inventory   # structural counts only (tablets, slots); no accuracy, no candidate
    python3 tools/pe004_restore.py calibrate   # stage 1: solver plant G0, leave-one-out, baseline, null, gates
    python3 tools/pe004_restore.py apply       # stage 2: damaged tablets, only for targets whose gates passed
    python3 tools/pe004_restore.py audit       # PE003 audit: re-run PE003 stage 2 + post hoc in a scratch dir
Needs numpy. Exact integer arithmetic (each system's smallest unit).

Rule (the grand-total convention validated by PE003): total = sum of all obverse entries. For a hidden/damaged
slot and each system X in which every intact notation (and every visible sign of the slot) is valid:
  entry slot: v = total - sum(other entries), admissible iff v > 0;  total slot: v = sum(entries).
Candidate = greedy canonical notation of v in X, kept only if it contains the visible signs of the slot (lower
bounds). Candidate set = distinct notations over admissible systems; 'unique' iff exactly one.
"""
import json, os, re, sys, time, shutil, subprocess, tempfile, math
from collections import Counter
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe001_totals as P

SYS = {**P.SYSTEMS, "C": P.c_table()}
ALLSIGNS = set().union(*[set(t) for t in SYS.values()])
ORDER = ("S", "D", "B", "C")
MIN_TASKS, MIN_UNIQUE = 30, 10
PREC_MIN, PREC_CP_LOW = 0.80, 0.60
ALPHA = 0.05
R_NULL, SEED_NULL, SEED_PLANT, N_PLANT = 9999, 404, 401, 2000
LINE = re.compile(r"^(\d+[A-Za-z]?)('?)\.\s*(.*)$")
NUM = re.compile(r"(\d+|n)\(([^)]+)\)")

def numpart(body): return body.rsplit(",", 1)[-1]
def numdmg(body): return bool(re.search(r"[\[\]#?]|\.\.\.", numpart(body)))
def outer(s): return re.sub(r"\|[^|]*\|", "G", s)

def parse(path):
    """Like PE001's parser, plus line labels, primes (lost beginning) and numeral-part damage."""
    tabs = []
    for d in open(path).read().split("\n\n"):
        d = d.strip()
        if not d.startswith("&P"): continue
        pid = d.split()[0][1:]; surf = None; lines = []; broken = {"o": False, "r": False}
        for raw in d.split("\n")[1:]:
            l = raw.strip()
            if not l: continue
            if l.startswith("@"):
                tag = l.split()[0]
                if tag == "@obverse": surf = "o"
                elif tag == "@reverse": surf = "r"
                elif tag in ("@column", "@tablet", "@object", "@surface"): pass
                else: surf = "x"
                continue
            if l.startswith("$"):
                if surf in ("o", "r") and re.search(r"broken|missing|effaced|illegible|traces|lost", l): broken[surf] = True
                continue
            m = LINE.match(l)
            if not m or surf not in ("o", "r"): continue
            body = m.group(3); np_ = numpart(body)
            lines.append({"surf": surf, "label": m.group(1) + m.group(2), "primed": bool(m.group(2)), "body": body,
                          "nums": NUM.findall(outer(np_)), "dmg": numdmg(body)})
        tabs.append({"pid": pid, "lines": lines, "broken": broken})
    return tabs

def notation(nums):
    c = Counter()
    for n, s in nums:
        if n == "n": return None
        c[P.norm(s)] += int(n)
    return c

def visible(np_):
    """Lower bounds from the readable part of a damaged numeral part: bracketed (restored/lost) material removed;
    '#'/'?' signs are read and kept; n(X) gives X >= 1."""
    s = re.sub(r"\[[^\]]*\]?", " ", outer(np_)); s = re.sub(r"^[^\[]*\]", " ", s)
    c = Counter()
    for n, sg in NUM.findall(s): c[P.norm(sg)] += 1 if n == "n" else int(n)
    return c

def editor_reading(np_):
    """Editor's full reading (brackets removed) if it is complete (no '...', no n, no x); else None."""
    if "[" not in np_ or "..." in np_ or re.search(r"\bn\(|\bx\b", np_): return None
    s = outer(np_).replace("[", " ").replace("]", " ")
    c = notation(NUM.findall(s)); return c if c else None

def key(c):
    tb = {}
    for t in SYS.values(): tb.update(t)
    return " ".join(f"{c[s]}({s})" for s in sorted((s for s in c if c[s]), key=lambda s: (-max(t.get(s, 0) for t in SYS.values()), s)))

def slots(t):
    o = [l for l in t["lines"] if l["surf"] == "o" and (l["nums"] or l["dmg"])]
    r = [l for l in t["lines"] if l["surf"] == "r" and (l["nums"] or l["dmg"])]
    return o, r

def shape_ok(t):
    return not (t["broken"]["o"] or t["broken"]["r"]) and not any(l["primed"] for l in t["lines"])

def valid(c): return c is not None and len(c) > 0 and set(c) <= ALLSIGNS

def calibration_set(tabs):
    """Intact single-total tablets: no numeral-part damage on obverse/reverse, no broken $-line, no primed line,
    >= 2 obverse numeral lines, exactly 1 reverse numeral line, every notation parsed and mapped."""
    out = []
    for t in tabs:
        if not shape_ok(t) or any(l["dmg"] for l in t["lines"]): continue
        o, r = slots(t)
        if len(o) < 2 or len(r) != 1: continue
        e = [notation(l["nums"]) for l in o]; tot = notation(r[0]["nums"])
        if not all(valid(x) for x in e + [tot]): continue
        out.append({"pid": t["pid"], "entries": e, "total": tot, "labels": [l["label"] for l in o]})
    return out

def damaged_set(tabs):
    """Single-total tablets with exactly one damaged numeral slot (an obverse entry or the reverse total); all other
    obverse/reverse numeral parts intact and mapped; no broken $-line, no primed line."""
    out = []
    for t in tabs:
        if not shape_ok(t): continue
        dl = [l for l in t["lines"] if l["dmg"]]
        if len(dl) != 1: continue
        o, r = slots(t); tgt = dl[0]
        if len(r) != 1 or len(o) < 2: continue
        ints = [l for l in o + r if l is not tgt]
        ns = [notation(l["nums"]) for l in ints]
        if not all(valid(x) for x in ns): continue
        vis = visible(numpart(tgt["body"]))
        if vis and not set(vis) <= ALLSIGNS: continue
        kind = "total" if tgt["surf"] == "r" else "entry"
        e = [notation(l["nums"]) for l in o if l is not tgt]
        tot = None if kind == "total" else notation(r[0]["nums"])
        out.append({"pid": t["pid"], "kind": kind, "label": tgt["label"], "line": tgt["body"], "visible": vis,
                    "editor": editor_reading(numpart(tgt["body"])), "entries": e, "total": tot, "n_entries_total": len(o)})
    return out

def solve(entries, total, kind, vis=None):
    """Candidates {notation key: [systems]} for the missing slot. entries = intact entries (Counters);
    total = Counter (kind 'entry') or None (kind 'total')."""
    vis = vis or Counter(); cands = {}
    for X in ORDER:
        tb = SYS[X]; signs = set(vis).union(*[set(e) for e in entries]) | (set(total) if total else set())
        if not signs <= set(tb): continue
        s = sum(P.value(e, tb) for e in entries)
        v = s if kind == "total" else P.value(total, tb) - s
        if v <= 0: continue
        c = P.canonical(v, tb)
        if c is None or any(c[g] < k for g, k in vis.items()): continue
        cands.setdefault(key(c), []).append(X)
    return cands

def tasks(cal, totals=None):
    """Leave-one-out tasks: each obverse entry hidden in turn, and the total hidden. totals overrides the totals
    (null)."""
    out = []
    for i, t in enumerate(cal):
        tot = t["total"] if totals is None else totals[i]
        for k in range(len(t["entries"])):
            out.append({"i": i, "kind": "entry", "k": k, "truth": key(t["entries"][k]),
                        "entries": t["entries"][:k] + t["entries"][k + 1:], "total": tot})
        out.append({"i": i, "kind": "total", "truth": key(tot), "entries": t["entries"], "total": None})
    return out

def baseline(cal, task):
    """Frequency guess. Entry: mode of the tablet's other entries (ties: frequency among all other calibration
    tablets' entries, then lexical). Total: mode of the other calibration tablets' totals (ties lexical)."""
    i = task["i"]
    if task["kind"] == "entry":
        corp = Counter(key(e) for j, t in enumerate(cal) if j != i for e in t["entries"])
        loc = Counter(key(e) for e in task["entries"])
        return min(loc, key=lambda s: (-loc[s], -corp[s], s))
    corp = Counter(key(t["total"]) for j, t in enumerate(cal) if j != i)
    return min(corp, key=lambda s: (-corp[s], s))

def score(cal, totals=None, with_base=False):
    rows = []
    for tk in tasks(cal, totals):
        c = solve(tk["entries"], tk["total"], tk["kind"])
        r = {"pid": cal[tk["i"]]["pid"], "kind": tk["kind"], "slot": tk.get("k", "total"), "truth": tk["truth"],
             "n_cand": len(c), "unique": len(c) == 1, "covered": tk["truth"] in c,
             "unique_correct": len(c) == 1 and tk["truth"] in c}
        if with_base:
            r["baseline"] = baseline(cal, tk); r["baseline_correct"] = r["baseline"] == tk["truth"]; r["candidates"] = c
        rows.append(r)
    return rows

def binom_sf(k, n, p=0.5):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))

def cp_low(k, n, a=0.05):
    """Exact one-sided Clopper-Pearson lower bound (bisection on the binomial tail)."""
    if k == 0: return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(60):
        m = (lo + hi) / 2
        if binom_sf(k, n, m) < a: lo = m
        else: hi = m
    return lo

def plant_gate():
    """G0: synthetic tablets in a random system with canonical entries and the canonical total; every hidden slot's
    truth must be among the candidates (solver correctness)."""
    rng = np.random.default_rng(SEED_PLANT); bad = n = 0
    for _ in range(N_PLANT):
        X = ORDER[rng.integers(4)]; tb = SYS[X]; top = max(tb.values())
        ents = [P.canonical(int(rng.integers(1, max(2, top // 3))), tb) for _ in range(int(rng.integers(2, 9)))]
        tot = P.canonical(sum(P.value(e, tb) for e in ents), tb)
        for k in range(len(ents)):
            n += 1; bad += key(ents[k]) not in solve(ents[:k] + ents[k + 1:], tot, "entry")
        n += 1; bad += key(tot) not in solve(ents, None, "total")
    return {"synthetic_tablets": N_PLANT, "slots": n, "missed": bad, "pass": bad == 0, "seed": SEED_PLANT}

def inventory():
    tabs = parse(os.path.join("data", "pe.atf")); cal = calibration_set(tabs); dam = damaged_set(tabs)
    tk = tasks(cal)
    out = {"calibration_tablets": len(cal), "tasks_entry": sum(t["kind"] == "entry" for t in tk),
           "tasks_total": sum(t["kind"] == "total" for t in tk),
           "damaged_tablets": len(dam), "damaged_entry_slots": sum(d["kind"] == "entry" for d in dam),
           "damaged_total_slots": sum(d["kind"] == "total" for d in dam),
           "damaged_with_visible_signs": sum(bool(d["visible"]) for d in dam),
           "damaged_with_complete_editor_reading": sum(d["editor"] is not None for d in dam)}
    print(json.dumps(out, indent=1)); json.dump(out, open("analysis/pe004_inventory.json", "w"), indent=1)

def calibrate():
    t0 = time.time(); tabs = parse(os.path.join("data", "pe.atf")); cal = calibration_set(tabs)
    res = {"calibration_tablets": len(cal), "G0_solver_plant": plant_gate()}
    rows = score(cal, with_base=True)
    rng = np.random.default_rng(SEED_NULL); obs = {}; null = {"entry": [], "total": []}
    for kind in ("entry", "total"):
        obs[kind] = sum(r["unique_correct"] for r in rows if r["kind"] == kind)
    tots = [t["total"] for t in cal]
    for rep in range(R_NULL):
        perm = rng.permutation(len(cal)); sh = [tots[j] for j in perm]
        nr = score(cal, sh)
        for kind in ("entry", "total"): null[kind].append(sum(r["unique_correct"] for r in nr if r["kind"] == kind))
        if rep % 2000 == 0: print("null rep", rep, round(time.time() - t0, 1), flush=True)
    mc = {}
    for kind in ("entry", "total"):
        R = [r for r in rows if r["kind"] == kind]; n = len(R); u = sum(r["unique"] for r in R)
        uc = sum(r["unique_correct"] for r in R); b = sum(r["baseline_correct"] for r in R)
        n10 = sum(r["unique_correct"] and not r["baseline_correct"] for r in R)
        n01 = sum(r["baseline_correct"] and not r["unique_correct"] for r in R)
        p_mc = binom_sf(n10, n10 + n01) if n10 + n01 else 1.0; mc[kind] = p_mc
        nl = np.array(null[kind]); p_null = (1 + int((nl >= uc).sum())) / (1 + R_NULL)
        res[kind] = {"tasks": n, "unique": u, "unique_correct": uc, "covered": sum(r["covered"] for r in R),
                     "mean_candidates": sum(r["n_cand"] for r in R) / n if n else None,
                     "no_candidate": sum(r["n_cand"] == 0 for r in R),
                     "recovery_rate": uc / n if n else None, "precision_unique": uc / u if u else None,
                     "precision_cp95_low": cp_low(uc, u) if u else 0.0, "baseline_correct": b,
                     "baseline_rate": b / n if n else None, "mcnemar": {"rule_only": n10, "baseline_only": n01, "p": p_mc},
                     "null": {"R": R_NULL, "seed": SEED_NULL, "mean": float(nl.mean()), "max": int(nl.max()), "p": p_null}}
    # Holm over the two McNemar tests
    order = sorted(mc, key=mc.get); holm = {}
    for i, k in enumerate(order):
        holm[k] = all(mc[order[j]] <= ALPHA / (len(order) - j) for j in range(i + 1))
    for kind in ("entry", "total"):
        r = res[kind]
        g = {"G0_solver": res["G0_solver_plant"]["pass"], "G1_tasks": r["tasks"] >= MIN_TASKS,
             "G2_precision": r["unique"] >= MIN_UNIQUE and (r["precision_unique"] or 0) >= PREC_MIN and r["precision_cp95_low"] >= PREC_CP_LOW,
             "G3_beats_baseline_holm": holm[kind], "G4_beats_null": r["null"]["p"] <= ALPHA}
        r["gates"] = g; r["verdict"] = "VALIDATED" if all(g.values()) else "NOT VALIDATED"
    res["rows"] = [{k: v for k, v in r.items() if k != "candidates"} | {"candidates": r["candidates"]} for r in rows]
    res["runtime_s"] = round(time.time() - t0, 1)
    json.dump(res, open("analysis/pe004_calibration.json", "w"), indent=1)
    print(json.dumps({k: (v if k == "G0_solver_plant" else {kk: vv for kk, vv in v.items()} if isinstance(v, dict) else v)
                      for k, v in res.items() if k != "rows"}, indent=1))

def apply():
    cal = json.load(open("analysis/pe004_calibration.json")); tabs = parse(os.path.join("data", "pe.atf"))
    ok = {k: cal[k]["verdict"] == "VALIDATED" for k in ("entry", "total")}; out = {"targets_validated": ok, "tablets": []}
    for d in damaged_set(tabs):
        if not ok[d["kind"]]: continue
        c = solve(d["entries"], d["total"], d["kind"], d["visible"])
        ed = key(d["editor"]) if d["editor"] else None
        out["tablets"].append({"pid": d["pid"], "slot": d["kind"], "line": d["label"], "atf_numerals": numpart(d["line"]).strip(),
                               "visible_lower_bounds": key(d["visible"]) if d["visible"] else "", "candidates": c,
                               "n_candidates": len(c), "editor_reading": ed,
                               "editor_in_candidates": (ed in c) if ed else None})
    T = out["tablets"]
    out["summary"] = {"tablets": len(T), "unique": sum(t["n_candidates"] == 1 for t in T),
                      "ambiguous": sum(t["n_candidates"] > 1 for t in T), "no_candidate": sum(t["n_candidates"] == 0 for t in T),
                      "with_editor_reading": sum(t["editor_reading"] is not None for t in T),
                      "editor_in_candidates": sum(bool(t["editor_in_candidates"]) for t in T),
                      "editor_equals_unique": sum(t["n_candidates"] == 1 and t["editor_reading"] in t["candidates"] for t in T if t["editor_reading"])}
    json.dump(out, open("analysis/pe004_restorations.json", "w"), indent=1); print(json.dumps(out["summary"], indent=1))

def audit():
    """PE003 audit: re-run PE003 stage 2 (seed 302) and post hoc (seed 305) on a scratch copy; compare with the
    committed JSON (every field)."""
    here = os.getcwd(); tmp = tempfile.mkdtemp()
    for sub in ("tools", "data", "analysis"): shutil.copytree(os.path.join(here, sub), os.path.join(tmp, sub), ignore=shutil.ignore_patterns("__pycache__"))
    out = {}
    for cmd, fn in ((["tools/pe003_contrast.py", "test"], "pe003_results.json"), (["tools/pe003_posthoc.py"], "pe003_posthoc.json")):
        subprocess.run([sys.executable] + cmd, cwd=tmp, check=True, capture_output=True)
        new = json.load(open(os.path.join(tmp, "analysis", fn))); old = json.load(open(os.path.join("analysis", fn)))
        strip = lambda x: {k: v for k, v in x.items() if k != "runtime_s"} if isinstance(x, dict) else x
        out[fn] = {"identical_except_runtime": strip(new) == strip(old)}
    json.dump(out, open("analysis/pe004_pe003_audit.json", "w"), indent=1); print(out); shutil.rmtree(tmp)

if __name__ == "__main__":
    os.makedirs("analysis", exist_ok=True)
    {"inventory": inventory, "calibrate": calibrate, "apply": apply, "audit": audit}[sys.argv[1]]()
