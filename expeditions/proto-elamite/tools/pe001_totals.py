#!/usr/bin/env python3
"""PE001 - Do proto-Elamite reverse totals balance the obverse entries under Englund's factor tables?

Pre-registered in case-file/PE001-reverse-totals.md (commit made before any H1/H2 number was computed).
Usage (from expeditions/proto-elamite/):
    python3 tools/pe001_totals.py fetch      # download pinned CDLI dump, verify SHA-256, extract PE subset
    python3 tools/pe001_totals.py run        # descriptive + gates + H1 + H2 -> analysis/pe001_results.json
Pure Python 3, no third-party packages.
"""
import csv, hashlib, json, os, random, re, sys, time, urllib.request
from collections import Counter, defaultdict
from fractions import Fraction

PIN = "d66b12b065af39a57d640576b4c7e098db5dac7f"  # cdli-gh/data master, 2023-10-11 (dump of Aug 2022)
FILES = {
    "cdliatf_unblocked.atf": "2896ec253767fa07fcaa5424af6fc25d6a047dc30b99c95f99d57ce75384d836",
    "cdli_cat.csv": "2e3232f75325b61c4d1e788d4d8c074c6230a947aed422110f9f35a6e353d09c",
}
DATA = "data"
SEED = 101

# ---- Numerical systems: Englund 2004 (Fig. 5.4) and Dahl et al., CDLJ 2005:3 (factor diagram) ----
# values as exact integers in each system's smallest unit
SYSTEMS = {
    "S": {"N01": 1, "N14": 10, "N34": 60, "N45": 600, "N48": 3600},
    "D": {"N01": 1, "N14": 10, "N23": 100, "N51": 1000, "N54": 10000},
    "B": {"N01": 1, "N14": 10, "N34": 60, "N51": 120, "N54": 1200},
}
# capacity system C, chain from largest: N48 <-10- N34 <-3- N45 <-10- N14 <-6- N01 <-r1- N39B <-r2- N24 <-r3- N30C <-r4- N30D <-r5- N39C
ENGLUND_SUB = (5, 2, 3, 2, 2)
def c_table(sub=ENGLUND_SUB):
    r1, r2, r3, r4, r5 = sub
    v = {"N39C": 1}
    v["N30D"] = r5; v["N30C"] = r5 * r4; v["N24"] = v["N30C"] * r3; v["N39B"] = v["N24"] * r2
    v["N01"] = v["N39B"] * r1; v["N14"] = v["N01"] * 6; v["N45"] = v["N14"] * 10
    v["N34"] = v["N45"] * 3; v["N48"] = v["N34"] * 10
    return v
C_SUB_SIGNS = {"N39B", "N24", "N30C", "N30D", "N39C"}

def norm(sign):
    s = re.sub(r"@[a-z]$", "", sign)      # framed/derived variants (B#, C#) take the base values
    s = {"N1": "N01", "N8": "N08"}.get(s, s)
    return s

# ---------------------------------------------------------------- fetch
def fetch():
    os.makedirs(DATA, exist_ok=True)
    for fn, sha in FILES.items():
        p = os.path.join(DATA, fn)
        if not os.path.exists(p):
            url = f"https://media.githubusercontent.com/media/cdli-gh/data/{PIN}/{fn}"
            print("downloading", url); urllib.request.urlretrieve(url, p)
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert h == sha, (fn, h)
        print(fn, "sha256 ok")
    csv.field_size_limit(10**9)
    ids = set()
    for row in csv.DictReader(open(os.path.join(DATA, "cdli_cat.csv"), encoding="utf-8", errors="replace")):
        if "Proto-Elamite" in (row.get("period") or "") and row["id_text"].strip().isdigit():
            ids.add(int(row["id_text"]))
    txt = open(os.path.join(DATA, "cdliatf_unblocked.atf"), encoding="utf-8", errors="replace").read()
    out = []
    for d in re.split(r"\n(?=&P\d+)", txt):
        m = re.match(r"&P(\d+)", d)
        if m and int(m.group(1)) in ids:
            out.append(d.rstrip())
    open(os.path.join(DATA, "pe.atf"), "w").write("\n\n".join(out) + "\n")
    print("catalogue PE ids", len(ids), "texts with ATF", len(out),
          "pe.atf sha256", hashlib.sha256(open(os.path.join(DATA, "pe.atf"), "rb").read()).hexdigest())

# ---------------------------------------------------------------- parse
LINE = re.compile(r"^(\d+[A-Za-z]?'?)\.\s*(.*)$")
NUM = re.compile(r"(\d+|n)\(([^)]+)\)")
# damage is judged on the numeral part (after the last ' , ') plus any break bracket anywhere in the line
def damage(body, allow_hash):
    if re.search(r"[\[\]]|\.\.\.", body): return True
    numpart = body.rsplit(",", 1)[-1]
    return bool(re.search(r"[?]" if allow_hash else r"[#?]", numpart))

def parse(path):
    tabs = []
    for d in open(path).read().split("\n\n"):
        d = d.strip()
        if not d.startswith("&P"): continue
        pid = d.split()[0][1:]
        surf = None; lines = []; brokenflag = {"o": False, "r": False}
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
                if surf in ("o", "r") and re.search(r"broken|missing|effaced|illegible|traces|lost", l): brokenflag[surf] = True
                continue
            m = LINE.match(l)
            if not m or surf not in ("o", "r"): continue
            body = m.group(2)
            outer = re.sub(r"\|[^|]*\|", "G", body)  # numerals inside complex graphemes are not counts
            nums = NUM.findall(outer)
            lines.append({"surf": surf, "body": body, "nums": [(n, s) for n, s in nums],
                          "strict_bad": damage(body, False),
                          "lenient_bad": damage(body, True)})
        tabs.append({"pid": pid, "lines": lines, "broken": brokenflag})
    return tabs

def notation(nums):
    c = Counter()
    for n, s in nums:
        if n == "n": return None
        c[norm(s)] += int(n)
    return c

def candidates(tabs, level):
    """Candidate = >=2 obverse numeral lines, exactly 1 reverse numeral line, no damage at `level` on obv/rev,
    no broken-surface $-line, every numeral sign mapped by at least one system."""
    out = []; why = Counter()
    for t in tabs:
        obs = [l for l in t["lines"] if l["surf"] == "o" and l["nums"]]
        rev = [l for l in t["lines"] if l["surf"] == "r" and l["nums"]]
        if len(obs) < 2: why["shape: <2 obverse numeral lines"] += 1; continue
        if len(rev) != 1: why["shape: reverse numeral lines != 1 (%s)" % ("0" if not rev else ">1")] += 1; continue
        key = "strict_bad" if level == "strict" else "lenient_bad"
        if any(l[key] for l in t["lines"]) or t["broken"]["o"] or t["broken"]["r"]: why["damage"] += 1; continue
        ents = [notation(l["nums"]) for l in obs]; tot = notation(rev[0]["nums"])
        if tot is None or any(e is None for e in ents): why["n-count"] += 1; continue
        signs = set(tot).union(*[set(e) for e in ents])
        allsigns = set(c_table()).union(*[set(v) for v in SYSTEMS.values()])
        if not signs <= allsigns: why["unmapped sign"] += 1; continue
        out.append({"pid": t["pid"], "entries": ents, "total": tot})
    return out, why

def value(c, table):
    if any(s not in table for s in c): return None
    return sum(table[s] * k for s, k in c.items())

def balances(entries, total, csub=ENGLUND_SUB):
    """Return list of systems under which sum(entries) == total exactly."""
    tabs = dict(SYSTEMS); tabs["C"] = c_table(csub)
    ok = []
    for name, tb in tabs.items():
        vs = [value(e, tb) for e in entries]; vt = value(total, tb)
        if vt is None or any(v is None for v in vs): continue
        if sum(vs) == vt: ok.append(name)
    return ok

def count_bal(cands, totals, csub=ENGLUND_SUB):
    return sum(1 for c, t in zip(cands, totals) if balances(c["entries"], t, csub))

def perm_test(cands, totals, R, rng):
    obs = count_bal(cands, totals)
    ge = 0; null = []
    for _ in range(R):
        sh = totals[:]; rng.shuffle(sh)
        m = count_bal(cands, sh); null.append(m); ge += m >= obs
    return obs, (1 + ge) / (1 + R), null

def canonical(val, table):
    """Greedy notation of an integer value in a system table (largest units first)."""
    c = Counter()
    for s, v in sorted(table.items(), key=lambda kv: -kv[1]):
        if val >= v: c[s] = val // v; val -= v * c[s]
    return c if val == 0 else None

def run():
    t0 = time.time()
    rng = random.Random(SEED)
    tabs = parse(os.path.join(DATA, "pe.atf"))
    res = {"seed": SEED, "pin": PIN}
    # descriptive
    signc = Counter(); nlines = 0
    for t in tabs:
        for l in t["lines"]:
            nlines += 1
            for n, s in l["nums"]: signc[norm(s)] += 1
    res["descriptive"] = {"texts": len(tabs), "obv_rev_lines": nlines, "numeral_tokens_by_sign": dict(signc.most_common())}
    sets = {}
    for lev in ("strict", "lenient"):
        cands, why = candidates(tabs, lev); sets[lev] = cands
        res["descriptive"][f"candidates_{lev}"] = len(cands); res["descriptive"][f"rejected_{lev}"] = dict(why)
    S = sets["strict"]; L = sets["lenient"]
    # ---- Gate P0 (valuation/parser): planted correct totals must all balance
    planted_ok = 0; plantable = 0
    for c in S:
        for name in ["S", "D", "B", "C"]:
            tb = SYSTEMS.get(name) or c_table()
            vs = [value(e, tb) for e in c["entries"]]
            if any(v is None for v in vs): continue
            can = canonical(sum(vs), tb)
            if can is None: continue
            plantable += 1; planted_ok += bool(balances(c["entries"], can)); break
    res["gate_P0"] = {"plantable": plantable, "recovered": planted_ok, "pass": plantable > 0 and planted_ok == plantable}
    # ---- Gate P1 (one-unit perturbation must not balance in the same system)
    off = 0; tested = 0
    for c in S:
        b = balances(c["entries"], c["total"])
        if not b: continue
        tot = Counter(c["total"]); smallest = min(tot, key=lambda s: (c_table() if b[0] == "C" else SYSTEMS[b[0]])[s])
        tot[smallest] += 1; tested += 1
        off += bool(balances(c["entries"], tot))
    res["gate_P1_offby1"] = {"tested": tested, "still_balanced": off}
    totals = [c["total"] for c in S]
    # ---- Gate FPR: destroyed-signal datasets (totals shuffled once), full test with R=499
    fr = random.Random(SEED + 1); hits = 0; NF = 200
    for _ in range(NF):
        sh = totals[:]; fr.shuffle(sh)
        _, p, _ = perm_test(S, sh, 499, fr); hits += p <= 0.025
    res["gate_FPR"] = {"replicates": NF, "rate_p_le_0.025": hits / NF, "pass": hits / NF <= 0.05}
    # ---- Gate power: plant correct totals in 10% of tablets (rest shuffled), R=499
    pr = random.Random(SEED + 2); det = 0; NP = 200
    for _ in range(NP):
        sh = totals[:]; pr.shuffle(sh)
        for i in pr.sample(range(len(S)), max(1, len(S) // 10)):
            for name in ["C", "S", "D", "B"]:
                tb = SYSTEMS.get(name) or c_table(); vs = [value(e, tb) for e in S[i]["entries"]]
                if any(v is None for v in vs): continue
                can = canonical(sum(vs), tb)
                if can: sh[i] = can; break
        _, p, _ = perm_test(S, sh, 499, pr); det += p <= 0.025
    res["gate_power"] = {"replicates": NP, "plant_fraction": 0.10, "power": det / NP, "pass": det / NP >= 0.8}
    gates = res["gate_P0"]["pass"] and res["gate_FPR"]["pass"] and res["gate_power"]["pass"]
    res["gates_pass"] = gates
    # ---- H1
    obs, p, null = perm_test(S, totals, 9999, rng)
    res["H1"] = {"n": len(S), "balanced": obs, "null_mean": sum(null) / len(null), "null_max": max(null), "p": p,
                 "verdict": ("NOT TESTABLE (gates)" if not gates else ("SUPPORTED" if p <= 0.025 else "NOT DETECTED"))}
    bl = [{"pid": c["pid"], "systems": balances(c["entries"], c["total"])} for c in S]
    res["H1_balanced_list"] = [b for b in bl if b["systems"]]
    res["H1_unbalanced_strict"] = []
    for c in S:
        if balances(c["entries"], c["total"]): continue
        diffs = {}
        for name in ["S", "D", "B", "C"]:
            tb = SYSTEMS.get(name) or c_table(); vs = [value(e, tb) for e in c["entries"]]; vt = value(c["total"], tb)
            if vt is not None and all(v is not None for v in vs): diffs[name] = vt - sum(vs)
        res["H1_unbalanced_strict"].append({"pid": c["pid"], "total_minus_sum": diffs})
    # lenient, descriptive + same test
    obsL, pL, nullL = perm_test(L, [c["total"] for c in L], 9999, rng)
    res["H1_lenient"] = {"n": len(L), "balanced": obsL, "null_mean": sum(nullL) / len(nullL), "p": pL}
    # ---- H2: sub-N01 capacity factors, per ratio, train even P-number / test odd P-number, lenient set
    Csets = [c for c in L if (set(c["total"]).union(*[set(e) for e in c["entries"]])) & C_SUB_SIGNS]
    train = [c for c in Csets if int(c["pid"][1:]) % 2 == 0]; test = [c for c in Csets if int(c["pid"][1:]) % 2 == 1]
    grid = {0: [4, 5, 6, 10], 1: [2, 3, 4], 2: [2, 3, 4, 5], 3: [2, 3, 4], 4: [2, 3]}
    names = ["N01:N39B", "N39B:N24", "N24:N30C", "N30C:N30D", "N30D:N39C"]
    h2 = {"n_train": len(train), "n_test": len(test), "ratios": {}}
    for k, vals in grid.items():
        row = {}
        for v in vals:
            sub = list(ENGLUND_SUB); sub[k] = v; sub = tuple(sub)
            row[v] = {"train": sum(1 for c in train if "C" in balances(c["entries"], c["total"], sub)),
                      "test": sum(1 for c in test if "C" in balances(c["entries"], c["total"], sub))}
        e = ENGLUND_SUB[k]; et = row[e]["test"]; others = [row[v]["test"] for v in vals if v != e]
        if et > max(others): verdict = "CONFIRMED"
        elif et == max(others): verdict = "NOT TESTABLE (tie)"
        else: verdict = "CONTRADICTED"
        h2["ratios"][names[k]] = {"englund": e, "counts": row, "train_argmax": max(vals, key=lambda v: row[v]["train"]), "verdict": verdict}
    # joint grid, descriptive: best chains on all C tablets
    joint = []
    import itertools
    for sub in itertools.product(*grid.values()):
        joint.append((sum(1 for c in Csets if "C" in balances(c["entries"], c["total"], sub)), sub))
    joint.sort(reverse=True)
    h2["joint_top5_all"] = [{"balanced": b, "chain": s} for b, s in joint[:5]]
    h2["englund_all"] = [b for b, s in joint if s == ENGLUND_SUB][0]
    h2["gates_pass"] = gates
    res["H2"] = h2
    res["runtime_s"] = round(time.time() - t0, 1)
    os.makedirs("analysis", exist_ok=True)
    json.dump(res, open("analysis/pe001_results.json", "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k not in ("H1_balanced_list", "H1_unbalanced_strict")}, indent=1, default=str))

if __name__ == "__main__":
    {"fetch": fetch, "run": run}[sys.argv[1]]()
