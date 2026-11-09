#!/usr/bin/env python3
"""PE011 - System disambiguation by sum closure (open line 3): when every obverse entry of a single-total tablet is
ambiguous between the capacity system C and the integer systems S/D/B, does the class picked by SUM CLOSURE
(the reverse total equals the obverse sum in that class only) agree with the class predicted, independently, by the
counted-object sign (H1) or the header sign (H2), learned from notation-unambiguous numerals on OTHER tablets?

Pre-registered in case-file/PE011-closure-system.md (committed with this tool and the label-free inventory BEFORE any
closure label, gate or agreement number is computed). Usage (from expeditions/proto-elamite/, after
`python3 tools/pe001_totals.py fetch`):
    python3 tools/pe011_closure_system.py inventory  # label-free: set size, predictions (notation-only), strata
    python3 tools/pe011_closure_system.py gates      # FPR gate (stratified label permutation) + planted power gate
    python3 tools/pe011_closure_system.py test       # H1, H2, Holm over 2, verdicts; descriptive after the decision
    python3 tools/pe011_closure_system.py audit      # PE010 audit (scratch re-run + independent re-count of T1 2/60)
Pure Python 3 (random.Random), exact integer arithmetic.

EXTERNAL REFERENCE (what is taken from it, nothing else): L. Born, M. W. Monroe, K. Kelley, A. Sarkar,
"Disambiguating Numeral Sequences to Decipher Ancient Accounting Corpora", Proc. Workshop on Computation and Written
Language (CAWL 2023), Toronto, ACL, pp. 71-81, doi:10.18653/v1/2023.cawl-1.9. Taken: (a) the 'readings' idea: a
notation is valid in a system only if every sign exists there AND no sign is repeated as often as the next higher
unit (bundling; their Algorithm 1 / Sec. 3.1); (b) the summary premise of their Sec. 3.2 (a summary is in one system);
(c) the OBJECT feature (sign immediately preceding a numeral) and FIRST_SIGN feature (first sign of the tablet) of
their Table 2; (d) their reported numbers, quoted descriptively only: 8011 intact numerals, 7954 with >= 1 reading,
1919 unambiguous, 5389 readable in all four systems (Table 1); 24 texts disambiguated by summary lines (Sec. 4.2);
2-way C-vs-rest F1 0.90 of their bootstrap classifier on a 48-item expert test set (Tables 3, 5). Factor tables stay
Englund 2004 (as in PE001-PE010); NOTE Born et al.'s Figure 1 gives the decimal system D with factors 10, 6, 10, 6
(N23 = 60 N01), Englund's Fig. 5.4 gives 10, 10, 10, 10 (N23 = 100): Born's D is a descriptive sensitivity only.

DECISION SET (fixed before looking; shape, readability and notation only): tablets of the whole PE corpus with no
broken $-line, no primed line, exactly 1 reverse numeral slot and >= 2 obverse numeral slots, every slot READABLE
(intact, or damaged but completely read by the editor: PE006 rule), every obverse entry 2-WAY AMBIGUOUS (valid with
bundling in C AND in at least one of S/D/B). The total is not restricted (an unambiguous total is Born's propagation
case). All tablets used by PE001-PE010 are allowed: their balance in 'any system' was computed there; the 2-way class
of the closure and its relation to object/header signs were never computed (disclosed in the case file).
CLOSURE LABEL (2-way): C if total == sum in C (all slots valid in C) and in no integer system X in {S,D,B} with all
slots valid in X; I if the reverse; otherwise none (closes in both, or in neither).
PREDICTIONS (notation only, never sums): training occurrences = every intact numeral slot of the corpus on OTHER
tablets whose notation is 2-way unambiguous (valid in C only, or in S/D/B only). A feature value predicts class k if
it has >= 3 training occurrences and share(k) >= 0.80. H1 OBJECT: per slot of the tablet (entries and total) the
sign immediately before the numeral; tablet prediction = strict majority of predicting slots (tie -> none).
H2 HEADER: the first sign of the first obverse line (Born's FIRST_SIGN), counted per training numeral.
TEST (one decision test, alpha 0.05): H1 OBJECT; statistic = number of tablets with a closure label AND an object
prediction where they agree. H2 HEADER is DESCRIPTIVE ONLY: the label-free inventory (computed before this file was
published) gives only 6 header predictions (< 8), declared now.
NULL (structure-preserving): closure labels permuted among those tablets WITHIN strata of obverse list length
(2 / 3-4 / >= 5 entries). R = 1999, seed 1101. p = (1 + #null >= obs) / (1 + R).
GATES: FPR - 100 datasets with labels stratified-permuted, R = 299, rate p <= 0.05 must be <= 0.06 (seed 1102).
Power - 100 datasets, each doubly-labelled tablet (prob 0.5) gets closure label := its prediction, R = 299, rate
p <= 0.05 must be >= 0.80 (seed 1103). Size >= 8 doubly-labelled tablets.
VERDICTS: NOT TESTABLE (a gate fails) / NOT DETECTED (p > 0.05) / EXCLUDED (NOT DETECTED and the one-sided CP95
upper bound of the agreement rate < 0.80, i.e. the two routes cannot be the reliable ~0.9 disambiguators both are
taken to be) / SUPPORTED (gates pass, p <= 0.05).
"""
import json, os, re, sys, time, random, shutil, subprocess, tempfile
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe001_totals as P, pe004_restore as Q, pe006_cap as T, pe008_grain_totals as G

ENG = {**P.SYSTEMS, "C": P.c_table()}
BORN_D = {"N01": 1, "N14": 10, "N23": 60, "N51": 600, "N54": 3600}
INTEGER = ("S", "D", "B")
R_NULL, SEED_NULL = 1999, 1101
N_FPR, R_IN, SEED_FPR = 100, 299, 1102
N_POW, SEED_POW, PLANT = 100, 1103, 0.5
ALPHA, FPR_MAX, POWER_MIN, MIN_N, EXCL_UB = 0.05, 0.06, 0.80, 8, 0.80
MIN_OCC, MIN_SHARE = 3, 0.80
TESTS = (("H1_OBJECT", "obj"),)
DESC_TESTS = (("H2_HEADER", "hdr"),)
ALPHA_POW = ALPHA / len(TESTS)
SIGN = re.compile(r"^\|?M\d")

def limits(tb):
    vs = sorted(set(tb.values())); lim = {}
    for s, v in tb.items():
        hi = [w for w in vs if w > v]
        lim[s] = (hi[0] // v - 1) if hi else 10**9
    return lim

def valid_in(c, tb, lim):
    return c is not None and len(c) > 0 and all(s in tb for s in c) and all(k <= lim[s] for s, k in c.items())

def readings(c, systems):
    return {x for x, tb in systems.items() if valid_in(c, tb, limits(tb))}

def cls2(rd):
    """2-way class of a reading set: 'C', 'I' or None (ambiguous / no reading)."""
    c = "C" in rd; i = bool(rd & set(INTEGER))
    return "C" if c and not i else "I" if i and not c else None

def readable(l): return T.complete(Q.numpart(l["body"])) if l["dmg"] else Q.notation(l["nums"])

def sign_before(body):
    if "," not in body: return None
    toks = body.rsplit(",", 1)[0].split()
    if not toks: return None
    s = re.sub(r"[\[\]#?!*]", "", toks[-1])
    return s if SIGN.match(s) else None

def header(t):
    o = [l for l in t["lines"] if l["surf"] == "o"]
    if not o: return None
    toks = o[0]["body"].split()
    if not toks: return None
    s = re.sub(r"[\[\]#?!*]", "", toks[0])
    return s if SIGN.match(s) else None

def closure(entries, total, systems):
    lab = {}
    for x, tb in systems.items():
        lim = limits(tb)
        if all(valid_in(e, tb, lim) for e in entries) and valid_in(total, tb, lim):
            lab[x] = sum(P.value(e, tb) for e in entries) == P.value(total, tb)
    cC = lab.get("C", False); cI = any(lab.get(x, False) for x in systems if x != "C")
    return ("C" if cC and not cI else "I" if cI and not cC else None), sorted(x for x, v in lab.items() if v)

def corpus(): return Q.parse(os.path.join("data", "pe.atf"))

def training(tabs):
    """(pid, feature kind, value, class) for every intact numeral slot whose notation is 2-way unambiguous."""
    occ = []
    for t in tabs:
        o, r = Q.slots(t); h = header(t)
        for l in o + r:
            if l["dmg"]: continue
            c = Q.notation(l["nums"])
            if c is None: continue
            k = cls2(readings(c, ENG))
            if k is None: continue
            ob = sign_before(l["body"])
            if ob: occ.append((t["pid"], "obj", ob, k))
            if h: occ.append((t["pid"], "hdr", h, k))
    return occ

class Predictor:
    def __init__(self, occ):
        self.tot = defaultdict(Counter); self.by = defaultdict(lambda: defaultdict(Counter))
        for pid, kind, v, k in occ:
            self.tot[(kind, v)][k] += 1; self.by[pid][(kind, v)][k] += 1
    def feat(self, pid, kind, v):
        if v is None: return None
        c = self.tot[(kind, v)] - self.by[pid][(kind, v)]   # leave this tablet out
        n = sum(c.values())
        if n < MIN_OCC: return None
        k, m = c.most_common(1)[0]
        return k if m / n >= MIN_SHARE else None

def build_set(tabs, pred):
    D = []; why = Counter()
    for t in tabs:
        if not Q.shape_ok(t): why["shape"] += 1; continue
        o, r = Q.slots(t)
        if len(o) < 2 or len(r) != 1: why["slots"] += 1; continue
        on = [readable(l) for l in o]; tot = readable(r[0])
        if tot is None or any(e is None for e in on): why["unreadable slot"] += 1; continue
        rds = [readings(e, ENG) for e in on]
        if not all("C" in rd and rd & set(INTEGER) for rd in rds): why["entry not 2-way ambiguous"] += 1; continue
        votes = Counter(p for p in (pred.feat(t["pid"], "obj", sign_before(l["body"])) for l in o + r) if p)
        top = votes.most_common(2)
        obj = top[0][0] if top and (len(top) == 1 or top[0][1] > top[1][1]) else None
        D.append({"pid": t["pid"], "entries": on, "total": tot, "n": len(o),
                  "obj": obj, "hdr": pred.feat(t["pid"], "hdr", header(t)), "header_sign": header(t),
                  "total_class": cls2(readings(tot, ENG))})
    return D, why

def stratum(n): return 0 if n == 2 else 1 if n <= 4 else 2

def label_all(D, systems=ENG):
    for t in D: t["clos"], t["closes_in"] = closure(t["entries"], t["total"], systems)
    return D

def pairs(D, kind):
    return [(t["clos"], t[kind], stratum(t["n"]), t["pid"]) for t in D if t["clos"] and t[kind]]

def agree(pr, labs=None):
    return sum((labs[i] if labs else a) == b for i, (a, b, _, _) in enumerate(pr))

def shuffle_within(labs, g, rng):
    out = labs[:]
    for s in set(g):
        idx = [i for i in range(len(g)) if g[i] == s]; sub = [labs[i] for i in idx]; rng.shuffle(sub)
        for i, x in zip(idx, sub): out[i] = x
    return out

def null_p(pr, R, rng):
    labs = [a for a, _, _, _ in pr]; g = [s for _, _, s, _ in pr]; obs = agree(pr); ge = 0; nl = []
    for _ in range(R):
        m = agree(pr, shuffle_within(labs, g, rng)); nl.append(m); ge += m >= obs
    return obs, (1 + ge) / (1 + R), nl

def destroy(pr, rng):
    labs = shuffle_within([a for a, _, _, _ in pr], [s for _, _, s, _ in pr], rng)
    return [(x, b, s, p) for x, (_, b, s, p) in zip(labs, pr)]

def plant(pr, rng):
    return [((b if rng.random() < PLANT else a), b, s, p) for a, b, s, p in pr]

def setup():
    tabs = corpus(); pred = Predictor(training(tabs)); D, why = build_set(tabs, pred); return tabs, pred, D, why

def inventory():
    tabs, pred, D, why = setup()
    out = {"corpus_texts": len(tabs), "decision_set": len(D), "excluded_by": dict(why),
           "with_object_prediction": sum(1 for t in D if t["obj"]), "object_prediction_mix": dict(Counter(t["obj"] for t in D if t["obj"])),
           "with_header_prediction": sum(1 for t in D if t["hdr"]), "header_prediction_mix": dict(Counter(t["hdr"] for t in D if t["hdr"])),
           "total_notation_class": dict(Counter(str(t["total_class"]) for t in D)),
           "strata_all": dict(Counter(stratum(t["n"]) for t in D)), "pids": [t["pid"] for t in D]}
    json.dump(out, open("analysis/pe011_inventory.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "pids"}, indent=1))

def gates():
    t0 = time.time(); _, _, D, _ = setup(); label_all(D); out = {}
    for tid, kind in TESTS:
        pr = pairs(D, kind); n = len(pr)
        rng = random.Random(SEED_FPR); fp = 0
        for _ in range(N_FPR): fp += null_p(destroy(pr, rng), R_IN, rng)[1] <= ALPHA
        rng = random.Random(SEED_POW); hit = 0
        for _ in range(N_POW): hit += null_p(plant(pr, rng), R_IN, rng)[1] <= ALPHA_POW
        out[tid] = {"doubly_labelled": n, "FPR": fp / N_FPR, "FPR_ok": fp / N_FPR <= FPR_MAX,
                    "power": hit / N_POW, "power_ok": hit / N_POW >= POWER_MIN, "size_ok": n >= MIN_N}
        print(tid, out[tid], round(time.time() - t0, 1), flush=True)
    out["params"] = {"N_FPR": N_FPR, "R_IN": R_IN, "SEED_FPR": SEED_FPR, "N_POW": N_POW, "SEED_POW": SEED_POW,
                     "PLANT": PLANT, "ALPHA_POW": ALPHA_POW}
    out["runtime_s"] = round(time.time() - t0, 1)
    json.dump(out, open("analysis/pe011_gates.json", "w"), indent=1)

def one(pr, seed=SEED_NULL, R=R_NULL):
    rng = random.Random(seed); obs, p, nl = null_p(pr, R, rng); n = len(pr)
    return {"n": n, "agree": obs, "rate": round(obs / n, 3) if n else None, "null_mean": round(sum(nl) / len(nl), 2) if n else None,
            "p": p, "cp95_upper_rate": G.cp_high(obs, n) if n else None,
            "label_mix": dict(Counter(a for a, _, _, _ in pr)), "prediction_mix": dict(Counter(b for _, b, _, _ in pr))}

def test():
    t0 = time.time(); g = json.load(open("analysis/pe011_gates.json")); tabs, pred, D, _ = setup(); label_all(D)
    res = {tid: one(pairs(D, kind)) for tid, kind in TESTS}
    adj = G.holm([res[tid]["p"] for tid, _ in TESTS]); verdict = {}
    for (tid, _), a in zip(TESTS, adj):
        gg = g[tid]; res[tid]["p_holm"] = a
        if not (gg["FPR_ok"] and gg["power_ok"] and gg["size_ok"]): v = "NOT TESTABLE"
        elif a > ALPHA: v = "EXCLUDED" if res[tid]["cp95_upper_rate"] < EXCL_UB else "NOT DETECTED"
        else: v = "SUPPORTED"
        verdict[tid] = v
    # ---- descriptive, after the decision (no decision weight)
    desc = {tid: one(pairs(D, kind)) for tid, kind in DESC_TESTS}
    desc["closure_yield_2way"] = dict(Counter(str(t["clos"]) for t in D))
    four = Counter(len(t["closes_in"]) for t in D); desc["closure_systems_count"] = {str(k): v for k, v in four.items()}
    desc["unique_single_system"] = dict(Counter(t["closes_in"][0] for t in D if len(t["closes_in"]) == 1))
    desc["closure_by_total_notation_class"] = {str(k): dict(Counter(str(t["clos"]) for t in D if t["total_class"] == k)) for k in ("C", "I", None)}
    # numeral-level reading sets over the whole corpus (Born Table 1 analogue: intact numeral slots)
    rs = Counter()
    for t in tabs:
        o, r = Q.slots(t)
        for l in o + r:
            if l["dmg"]: continue
            c = Q.notation(l["nums"])
            rs["n(...) count" if c is None else ",".join(sorted(readings(c, ENG))) or "none"] += 1
    desc["numeral_reading_sets_ours"] = dict(rs.most_common())
    desc["born_table1_quoted"] = {"intact": 8011, "with_reading": 7954, "unambiguous": 1919, "all_four": 5389, "none": 57}
    # sensitivity: Born's decimal factors
    Db = [dict(t) for t in D]; label_all(Db, {**ENG, "D": BORN_D})
    desc["born_D_sensitivity"] = {tid: {k: v for k, v in one(pairs(Db, kind)).items() if k in ("n", "agree", "p", "label_mix")} for tid, kind in TESTS + DESC_TESTS}
    # Born's worked example P008014 (all entries C because the C summary closes) on the full single-total shape
    ex = [t for t in tabs if t["pid"] == "P008014"]
    if ex:
        o, r = Q.slots(ex[0]); on = [readable(l) for l in o]; tot = readable(r[0])
        desc["P008014"] = {"closes_in": closure(on, tot, ENG)[1], "in_decision_set": any(t["pid"] == "P008014" for t in D),
                           "entry_readings": [sorted(readings(e, ENG)) for e in on]}
    # disagreements listed for inspection
    desc["disagreements"] = {tid: [(p, a, b) for a, b, _, p in pairs(D, kind) if a != b] for tid, kind in TESTS}
    out = {"verdicts": verdict, "results": res, "gates": g, "descriptive_no_decision_weight": desc,
           "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe011_results.json", "w"), indent=1)
    print(json.dumps({"verdicts": verdict, "results": res, "descriptive": desc}, indent=1))

def audit():
    """PE010 audit: (1) re-run `pe010_per_line.py test` in a scratch copy with the published gates, compare every
    field except run time; (2) independently re-count T1 (reverse = one readable entry on D1, published 2/60) with a
    literal C table and plain integer sums (no P.value / pe010 match code); pids from the published inventory."""
    here = os.getcwd(); tmp = tempfile.mkdtemp()
    try:
        shutil.copytree("tools", os.path.join(tmp, "tools")); os.makedirs(os.path.join(tmp, "analysis"))
        os.symlink(os.path.join(here, "data"), os.path.join(tmp, "data"))
        shutil.copy("analysis/pe010_gates.json", os.path.join(tmp, "analysis"))
        subprocess.run([sys.executable, "tools/pe010_per_line.py", "test"], cwd=tmp, check=True, capture_output=True)
        a = json.load(open("analysis/pe010_results.json")); b = json.load(open(os.path.join(tmp, "analysis/pe010_results.json")))
        def strip(d):
            if isinstance(d, dict): return {k: strip(v) for k, v in d.items() if "time" not in k and "runtime" not in k}
            if isinstance(d, list): return [strip(x) for x in d]
            return d
        out = {"pe010_results_identical_except_time": strip(a) == strip(b)}
        LIT = {"N39C": 1, "N30D": 2, "N30C": 4, "N24": 12, "N39B": 24, "N01": 120, "N14": 720, "N45": 7200,
               "N34": 21600, "N48": 216000}
        inv = json.load(open("analysis/pe010_inventory.json")); want = set(inv["D1"]["pids"])
        tabs = {t["pid"]: t for t in Q.parse(os.path.join("data", "pe.atf"))}; hits = []
        NUMRE = re.compile(r"(\d+)\(([^)]+)\)")
        def lit(np_):
            s = re.sub(r"\|[^|]*\|", " ", np_).replace("[", " ").replace("]", " ").replace("#", "").replace("?", "")
            if "..." in s or re.search(r"(^|\s)n\(|(^|\s)x(\s|$)", s): return None
            v = 0; seen = False
            for n, sg in NUMRE.findall(s):
                sg = re.sub(r"@[a-z]$", "", sg); sg = {"N1": "N01"}.get(sg, sg)
                if sg not in LIT: return None
                v += int(n) * LIT[sg]; seen = True
            return v if seen else None
        for pid in sorted(want):
            t = tabs[pid]
            o = [l for l in t["lines"] if l["surf"] == "o" and (l["nums"] or l["dmg"])]
            r = [l for l in t["lines"] if l["surf"] == "r" and (l["nums"] or l["dmg"])]
            tv = lit(r[0]["body"].rsplit(",", 1)[-1]); ev = [lit(l["body"].rsplit(",", 1)[-1]) for l in o]
            ev = [x for x in ev if x]
            if tv is not None and tv in ev: hits.append(pid)
        out["T1_recount"] = {"matched": len(hits), "of": len(want), "pids": hits, "published": "2/60",
                             "published_pids": a["results"]["T1_ENTRY"]["matched_pids"],
                             "match": len(hits) == 2 and len(want) == 60 and sorted(hits) == sorted(a["results"]["T1_ENTRY"]["matched_pids"])}
        json.dump(out, open("analysis/pe011_pe010_audit.json", "w"), indent=1); print(json.dumps(out, indent=1))
    finally: shutil.rmtree(tmp)

if __name__ == "__main__":
    {"inventory": inventory, "gates": gates, "test": test, "audit": audit}[sys.argv[1]]()
