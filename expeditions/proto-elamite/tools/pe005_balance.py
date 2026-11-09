#!/usr/bin/env python3
"""PE005 - Which visible features predict whether an intact single-total tablet balances?

Pre-registered in case-file/PE005-balance-predictor.md (committed with this tool before any association between a
feature and balance was computed). Usage (from expeditions/proto-elamite/, after `python3 tools/pe001_totals.py fetch`):
    python3 tools/pe005_balance.py features  # label-free inventory: feature prevalences only (no balance labels)
    python3 tools/pe005_balance.py gates     # FPR gate (feature-permutation null) + planted-feature power gate
    python3 tools/pe005_balance.py test      # real features vs balance: Fisher, BH, parity-split confirmation, lift
    python3 tools/pe005_balance.py audit     # PE004 audit: re-run PE004 calibrate + post hoc in a scratch dir
Pure Python (exact Fisher by hypergeometric enumeration); numpy only through the imported PE004 tool.

Analysis set: PE004 calibration tablets (45 intact single-total tablets) minus those whose signs admit no common
system (they cannot balance by construction; reported separately). Label: balances = sum(entries) == total in at least
one system admitted by the signs (pe001_totals.balances, Englund's capacity sub-units).
Features (binary, fixed in advance, each readable on a damaged tablet without doing the sum):
  EDGE   numerals written on a surface other than obverse/reverse (@top/@bottom/@left/@right/@edge...): the PE001-PE004
         parser ignores those lines, so an un-summed edge entry or an edge total breaks balance mechanically.
  CAP    capacity sub-unit signs (N39B, N24, N30C, N30D, N39C) present: the C sub-unit factors are the least secure
         part of the value tables (Dahl et al. CDLJ 2005:3; PE001 H2 could not test them).
  LONG   more than 6 obverse numeral entries (6 = median of the 45, label-free): long lists invite sub-accounts and
         un-summed lines (PE001: total < sum on 16 of 19 non-balancing tablets).
  MULTI  the tablet's signs are valid in >= 2 of S, D, B, C (only shared signs like N01, N14): more readings to try,
         and the ambiguity PE004 measured.
  UNREAD an unread sign 'x' or lost signs '[...]' in a non-numeral part (legibility / damage outside the numbers).
"""
import json, os, re, sys, time, math, random, shutil, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe004_restore as Q
import pe001_totals as P

FEATS = ("EDGE", "CAP", "LONG", "MULTI", "UNREAD")
LONG_CUT = 6
Q_BH, ALPHA_CONF = 0.05, 0.10
R_FPR, SEED_FPR = 2000, 501
R_POW, SEED_POW, W_PLANT, W_DESC = 2000, 502, 4.0, 9.0
FPR_MAX, POWER_MIN = 0.06, 0.80
NONMAIN = re.compile(r"^@(top|bottom|left|right|edge|side|surface|seal|envelope)", re.I)

def raw_blocks(path):
    out = {}
    for d in open(path).read().split("\n\n"):
        d = d.strip()
        if d.startswith("&P"): out[d.split()[0][1:]] = d
    return out

def features(t, raw, parsed):
    edge = False; surf = None
    for l in raw.split("\n"):
        l = l.strip()
        if l.startswith("@"): surf = l; continue
        if surf and NONMAIN.match(surf) and re.match(r"^\d", l) and re.search(r"(\d+|n)\(N", l): edge = True
    signs = set(t["total"]).union(*[set(e) for e in t["entries"]])
    nsys = sum(signs <= set(tb) for tb in Q.SYS.values())
    unread = False
    for l in parsed["lines"]:
        if l["surf"] not in ("o", "r"): continue
        sp = l["body"].rsplit(",", 1)[0] if "," in l["body"] else ""
        if re.search(r"(^|\s)[xX](\s|$)|\[\.\.\.\]", sp): unread = True
    return {"EDGE": edge, "CAP": bool(signs & P.C_SUB_SIGNS), "LONG": len(t["entries"]) > LONG_CUT,
            "MULTI": nsys >= 2, "UNREAD": unread}, nsys

def load():
    path = os.path.join("data", "pe.atf"); tabs = Q.parse(path); byid = {t["pid"]: t for t in tabs}
    raw = raw_blocks(path); cal = Q.calibration_set(tabs); rows = []; nocover = []
    for t in cal:
        f, nsys = features(t, raw[t["pid"]], byid[t["pid"]])
        if nsys == 0: nocover.append(t["pid"]); continue
        rows.append({"pid": t["pid"], "f": f, "t": t})
    return cal, rows, nocover

def label(r): return bool(P.balances(r["t"]["entries"], r["t"]["total"]))

def fisher(x, y):
    """Exact Fisher test on two boolean lists. Returns (a, b, c, d, two-sided p, one-sided p for 'x -> not y',
    one-sided p for 'x -> y'); a = x & y."""
    a = sum(1 for i, j in zip(x, y) if i and j); b = sum(1 for i, j in zip(x, y) if i and not j)
    c = sum(1 for i, j in zip(x, y) if not i and j); d = len(x) - a - b - c
    r1, c1, n = a + b, a + c, len(x)
    lo, hi = max(0, r1 + c1 - n), min(r1, c1)
    pr = {k: math.comb(c1, k) * math.comb(n - c1, r1 - k) / math.comb(n, r1) for k in range(lo, hi + 1)}
    p0 = pr[a]; two = sum(v for v in pr.values() if v <= p0 * (1 + 1e-9))
    less = sum(v for k, v in pr.items() if k <= a); more = sum(v for k, v in pr.items() if k >= a)
    return a, b, c, d, min(1.0, two), less, more

def bh(ps, q):
    m = len(ps); order = sorted(range(m), key=lambda i: ps[i]); k = 0
    for r, i in enumerate(order, 1):
        if ps[i] <= q * r / m: k = r
    rej = [False] * m
    for r, i in enumerate(order, 1):
        if r <= k: rej[i] = True
    return rej

def odd(pid): return int(pid[1:]) % 2 == 1

def pipeline(X, y, par):
    """X: dict feat -> bool list; y: labels; par: parity list (True = odd). Returns per-feature verdict dict.
    SUPPORTED = full-sample two-sided Fisher BH-rejected (q 0.05 over the features given);
    CONFIRMED = SUPPORTED and, in each parity half, one-sided Fisher in the full-sample direction p <= 0.10."""
    names = list(X); full = {k: fisher(X[k], y) for k in names}
    rej = bh([full[k][4] for k in names], Q_BH); out = {}
    for k, rj in zip(names, rej):
        a, b, c, d = full[k][:4]
        direction = "less_balance" if a * d < b * c else "more_balance"
        halves = {}
        for h in (True, False):
            idx = [i for i in range(len(y)) if par[i] == h]
            fh = fisher([X[k][i] for i in idx], [y[i] for i in idx])
            halves["odd" if h else "even"] = fh[5] if direction == "less_balance" else fh[6]
        out[k] = {"table_a_b_c_d": [a, b, c, d], "p_two_sided": full[k][4], "direction": direction,
                  "bh_reject": rj, "half_p_one_sided": halves,
                  "confirmed": rj and all(p <= ALPHA_CONF for p in halves.values())}
    return out

def inventory():
    cal, rows, nocover = load()
    out = {"calibration_tablets": len(cal), "no_common_system": nocover, "analysis_set": len(rows),
           "odd_P": sum(odd(r["pid"]) for r in rows),
           "prevalence": {k: sum(r["f"][k] for r in rows) for k in FEATS}}
    json.dump(out, open("analysis/pe005_features.json", "w"), indent=1); print(json.dumps(out, indent=1))

def plant(y, m, w, rng):
    """Planted feature with prevalence m: m tablets drawn without replacement, weight w for non-balancing and 1 for
    balancing (sequential weighted draws). Direction: feature -> less balance."""
    idx = list(range(len(y))); chosen = set()
    for _ in range(m):
        ws = [(w if not y[i] else 1.0) for i in idx if i not in chosen]; pool = [i for i in idx if i not in chosen]
        u = rng.random() * sum(ws); acc = 0
        for i, wi in zip(pool, ws):
            acc += wi
            if acc >= u: chosen.add(i); break
    return [i in chosen for i in idx]

def gates():
    t0 = time.time(); cal, rows, nocover = load(); y = [label(r) for r in rows]; par = [odd(r["pid"]) for r in rows]
    X0 = {k: [r["f"][k] for r in rows] for k in FEATS}
    # FPR: every feature permuted independently across tablets (prevalence kept, link to balance destroyed)
    rng = random.Random(SEED_FPR); fw_sup = fw_conf = 0; per = {k: [0, 0] for k in FEATS}
    for _ in range(R_FPR):
        X = {}
        for k in FEATS: v = X0[k][:]; rng.shuffle(v); X[k] = v
        res = pipeline(X, y, par)
        fw_sup += any(v["bh_reject"] for v in res.values()); fw_conf += any(v["confirmed"] for v in res.values())
        for k in FEATS: per[k][0] += res[k]["bh_reject"]; per[k][1] += res[k]["confirmed"]
    fpr = {"familywise_supported": fw_sup / R_FPR, "familywise_confirmed": fw_conf / R_FPR,
           "per_feature_supported": {k: per[k][0] / R_FPR for k in FEATS},
           "per_feature_confirmed": {k: per[k][1] / R_FPR for k in FEATS}}
    # power: feature k replaced by a planted feature with its own prevalence; the other features permuted (null)
    rng = random.Random(SEED_POW); powr = {}
    for k in FEATS:
        m = sum(X0[k]); res_w = {}
        for w in (W_PLANT, W_DESC):
            s = c = 0
            for _ in range(R_POW):
                X = {}
                for j in FEATS:
                    if j == k: X[j] = plant(y, m, w, rng)
                    else: v = X0[j][:]; rng.shuffle(v); X[j] = v
                res = pipeline(X, y, par)[k]; s += res["bh_reject"]; c += res["confirmed"]
            res_w[f"w{w:g}"] = {"supported": s / R_POW, "confirmed": c / R_POW}
        powr[k] = {"prevalence": m, **res_w,
                   "testable": res_w[f"w{W_PLANT:g}"]["confirmed"] >= POWER_MIN}
    out = {"n": len(rows), "balancing": sum(y), "fpr": fpr, "fpr_gate_pass": fpr["familywise_supported"] <= FPR_MAX,
           "power": powr, "seeds": [SEED_FPR, SEED_POW], "R": [R_FPR, R_POW], "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe005_gates.json", "w"), indent=1); print(json.dumps(out, indent=1))

def test():
    t0 = time.time(); cal, rows, nocover = load(); y = [label(r) for r in rows]; par = [odd(r["pid"]) for r in rows]
    G = json.load(open("analysis/pe005_gates.json"))
    X = {k: [r["f"][k] for r in rows] for k in FEATS}; res = pipeline(X, y, par)
    for k in FEATS:
        tst = G["fpr_gate_pass"] and G["power"][k]["testable"]
        v = res[k]
        if not tst: verdict = "NOT TESTABLE"
        elif v["confirmed"]: verdict = "CONFIRMED"
        elif v["bh_reject"]: verdict = "SUPPORTED, NOT CONFIRMED"
        else: verdict = "NOT DETECTED"
        v["verdict"] = verdict
    # descriptive lift: PE004 leave-one-out precision restricted to tablets on the balance-favouring side of each
    # feature (in-sample; no decision weight)
    sc = Q.score(cal); fpid = {r["pid"]: r["f"] for r in rows}; lift = {}
    for k in FEATS:
        side = False if res[k]["direction"] == "less_balance" else True
        keep = {p for p, f in fpid.items() if f[k] == side}
        d = {}
        for kind in ("entry", "total"):
            R = [r for r in sc if r["kind"] == kind and r["pid"] in keep]; u = sum(r["unique"] for r in R)
            uc = sum(r["unique_correct"] for r in R)
            d[kind] = {"tablets": len(keep), "unique": u, "unique_correct": uc, "precision": uc / u if u else None,
                       "cp95_low": Q.cp_low(uc, u) if u else 0.0}
        lift[k] = {"kept_side": side, **d}
    out = {"n": len(rows), "balancing": sum(y), "no_common_system_excluded": nocover, "results": res,
           "lift_descriptive": lift, "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe005_results.json", "w"), indent=1); print(json.dumps(out, indent=1))

def audit():
    """PE004 audit: re-run PE004 calibrate and post hoc on a scratch copy; compare every field (run time excluded)."""
    here = os.getcwd(); tmp = tempfile.mkdtemp(prefix="pe005-audit-")
    for sub in ("tools", "data", "analysis"):
        shutil.copytree(os.path.join(here, sub), os.path.join(tmp, sub), ignore=shutil.ignore_patterns("__pycache__"))
    out = {}
    for cmd, fn in ((["tools/pe004_restore.py", "calibrate"], "pe004_calibration.json"),
                    (["tools/pe004_posthoc.py"], "pe004_posthoc.json")):
        subprocess.run([sys.executable] + cmd, cwd=tmp, check=True, capture_output=True)
        new = json.load(open(os.path.join(tmp, "analysis", fn))); old = json.load(open(os.path.join("analysis", fn)))
        def strip(x):
            if isinstance(x, dict): return {k: strip(v) for k, v in x.items() if k not in ("runtime_s", "elapsed_s")}
            if isinstance(x, list): return [strip(v) for v in x]
            return x
        out[fn] = {"identical_except_runtime": strip(new) == strip(old)}
    json.dump(out, open("analysis/pe005_pe004_audit.json", "w"), indent=1); print(out); shutil.rmtree(tmp)

if __name__ == "__main__":
    os.makedirs("analysis", exist_ok=True)
    {"features": inventory, "gates": gates, "test": test, "audit": audit}[sys.argv[1]]()
