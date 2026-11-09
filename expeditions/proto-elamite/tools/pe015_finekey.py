#!/usr/bin/env python3
"""PE015 - Header structure step 3 (open line 5b): does a FINER header key (the full header, variant suffixes and
complex graphemes kept) predict the number system (H1) and size (H2) of the obverse entries, globally (G) and
beyond the coarse PE012 key (W, refinement)?

NOT BLIND: PE012's descriptive tables (coarse key x SYSTEM / SIZE, e.g. M157 C 94 / I 28 / MIX 7) were published at
9be8bf6 and have been seen. Disclosed in case-file/PE015-finer-header-key.md. The W tests permute the fine key only
inside its coarse key, so the coarse association that was seen is held fixed by the null.

Usage (from expeditions/proto-elamite/, data/pe.atf pinned by pe001_totals.py fetch):
    python3 tools/pe015_finekey.py inventory   # label-free: dead-on-arrival counts (set sizes, key counts, marginals)
    python3 tools/pe015_finekey.py rehearsal   # gates on destroyed/planted data + smoke run on registered shuffle 1599
    python3 tools/pe015_finekey.py test        # gates re-run, observed statistics only for runnable tests, Holm
    python3 tools/pe015_finekey.py audit       # PE014 audit: H2 re-drawn with new seed 1505, R 9999

FINE KEY (fixed before looking): header line as in PE012 (obverse '1.' followed by '# header', no numeral); the
text before the first comma; damage marks # ? ! * removed; tokens with '[' ']' or 'x' / 'X' as a whole token or
'...' -> no key (unread or restored); complex graphemes kept whole including X components (|M327+X| stays as
written); variant suffixes kept (M157~a != M157); several tokens joined by a space.
COARSE KEY: PE012's key (pe012_header.header_keys). Rows need both keys and >= 1 intact entry (PE012 build).
LABELS, entries, statistics (G for SYSTEM, between-key SS for SIZE), strata: exactly PE012.
SETS: fine keys with >= 3 tablets in the labelled set (as PE012).
TESTS: H1G/H2G - fine keys permuted within PE012 strata. H1W/H2W - fine keys permuted within PE012 strata x coarse
key (only the information the fine key adds beyond the coarse one). Holm over runnable tests.
GATES (per test): size - G: >= 30 tablets, >= 3 fine keys; W: >= 30 tablets in coarse groups that hold >= 2 fine
keys (informative tablets) and >= 2 such coarse groups. FPR - 40 destroyed datasets (its own null), R 299, rate p
<= 0.05 must be <= 0.10 (seed 1502). Power - TWO independent batches of 100 (seeds 1503, 1504; Kryptos's two-batch
gate I-182): destroy with the test's own null, each fine key gets one target label drawn from the set's labels and
each tablet (prob 0.5, PE012's plant) takes its key's target; R 299, rate p <= 0.05/k (k = tests passing the size
gate) must be >= 0.80 on BOTH batches. A failed gate = NOT TESTABLE, test not run on the real pairing.
R = 9999, null seed 1501 (+ test index x 10000), registered shuffle 1599, audit 1505.
"""
import json, os, re, sys, time, random
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pe012_header as H, pe008_grain_totals as G

R_NULL, SEED_NULL = 9999, 1501
N_FPR, R_IN, SEED_FPR, FPR_MAX = 40, 299, 1502, 0.10
N_POW, SEED_POW1, SEED_POW2, PLANT, POWER_MIN = 100, 1503, 1504, 0.5, 0.80
SEED_SHUFFLE, SEED_AUDIT = 1599, 1505
ALPHA, MIN_KEY, MIN_N, MIN_LEVELS = 0.05, 3, 30, 3
TESTS = ("H1G", "H1W", "H2G", "H2W")

def fine_keys(path):
    keys = {}
    for d in open(path).read().split("\n\n"):
        d = d.strip()
        if not d.startswith("&P"): continue
        pid = d.split()[0][1:]; L = [x.strip() for x in d.split("\n")]; surf = None
        for i, l in enumerate(L):
            if l.startswith("@obverse"): surf = "o"; continue
            if l.startswith("@reverse"): surf = "r"; continue
            if surf == "o" and re.match(r"^1\.\s", l):
                if i + 1 < len(L) and L[i + 1].startswith("# header"):
                    body = l[2:].strip(); head = body.split(",")[0].strip() if "," in body else body
                    if "," in body and re.search(r"\d+\(|n\(", body.split(",", 1)[1]): break
                    toks = head.split()
                    if not toks or any(("[" in t or "]" in t or t in ("x", "X", "...") or "..." in t) for t in toks): break
                    toks = [re.sub(r"[#?!*]", "", t) for t in toks]
                    if all(re.fullmatch(r"\|?M\d+.*", t) for t in toks): keys[pid] = " ".join(toks)
                break
    return keys

def build():
    rows, why, ntab, nk = H.build(); fk = fine_keys(os.path.join("data", "pe.atf")); out = []
    for r in rows:
        if r["pid"] in fk: out.append(dict(r, coarse=r["key"], key=fk[r["pid"]]))
        else: why["coarse key but no fine key (broken/restored header)"] += 1
    return out, why

def make(rows, test):
    h = test[:2]; w = test[2] == "W"
    if h == "H1": R = [r for r in rows if r["sys"]]; lab = lambda r: r["sys"]; st = lambda r: (H.lenbin(r["n"]),)
    else: R = rows; lab = lambda r: r["size"]; st = lambda r: (H.lenbin(r["n"]), str(r["sys"]))
    kc = Counter(r["key"] for r in R); R = [r for r in R if kc[r["key"]] >= MIN_KEY]
    if w:   # keep only coarse groups that hold >= 2 fine keys (others carry no refinement information)
        fk = defaultdict(set)
        for r in R: fk[r["coarse"]].add(r["key"])
        R = [r for r in R if len(fk[r["coarse"]]) >= 2]
        stf = lambda r: st(r) + (r["coarse"],)
    else: stf = st
    return [r["key"] for r in R], [lab(r) for r in R], [stf(r) for r in R], [r["pid"] for r in R], [r["coarse"] for r in R]

STAT = {"H1": H.gstat, "H2": H.ssb}

def null_p(test, keys, labs, pm, R, rng):
    f = STAT[test[:2]]; obs = f(keys, labs); ge = 0; nl = []
    for _ in range(R):
        v = f(pm.shuffle(keys, rng), labs); nl.append(v); ge += v >= obs - 1e-9
    return obs, (1 + ge) / (1 + R), nl

def size_ok(test, keys, coarse):
    if test[2] == "G": return len(keys) >= MIN_N and len(set(keys)) >= MIN_LEVELS
    return len(keys) >= MIN_N and len(set(coarse)) >= 2

def gates(rows):
    pre = {}
    for t in TESTS:
        keys, labs, st, _, co = make(rows, t); pre[t] = size_ok(t, keys, co)
    k = max(1, sum(pre.values())); out = {}
    for t in TESTS:
        keys, labs, st, _, co = make(rows, t); off = TESTS.index(t) * 10000; t0 = time.time()
        base = {"n": len(keys), "fine_keys": len(set(keys)), "coarse_groups": len(set(co)), "size_ok": pre[t]}
        if not pre[t]:
            out[t] = dict(base, FPR=None, power=None, FPR_ok=False, power_ok=False); print(t, out[t], flush=True); continue
        pm = H.Perm(st); rng = random.Random(SEED_FPR + off); fp = 0
        for _ in range(N_FPR): fp += null_p(t, pm.shuffle(keys, rng), labs, pm, R_IN, rng)[1] <= ALPHA
        pw = []
        for seed in (SEED_POW1, SEED_POW2):
            rng = random.Random(seed + off); hit = 0
            for _ in range(N_POW):
                kd = pm.shuffle(keys, rng); hit += null_p(t, kd, H.plant(kd, labs, PLANT, rng), pm, R_IN, rng)[1] <= ALPHA / k
            pw.append({"seed": seed + off, "power": hit / N_POW})
        out[t] = dict(base, FPR=fp / N_FPR, FPR_ok=fp / N_FPR <= FPR_MAX, power_batches=pw,
                      power=min(b["power"] for b in pw), power_ok=all(b["power"] >= POWER_MIN for b in pw),
                      alpha_power=ALPHA / k, seconds=round(time.time() - t0, 1))
        print(t, out[t], flush=True)
    return out

def runnable(g): return [t for t in TESTS if g[t]["size_ok"] and g[t]["FPR_ok"] and g[t]["power_ok"]]

def inventory():
    rows, why = build(); out = {"eligible_rows_with_fine_key": len(rows), "excluded_by": dict(why),
                                "fine_keys_all_rows": len(set(r["key"] for r in rows))}
    for t in TESTS:
        keys, labs, st, pids, co = make(rows, t)
        out[t] = {"n": len(keys), "fine_keys": len(set(keys)), "coarse_groups": len(set(co)), "size_ok": size_ok(t, keys, co),
                  "key_counts": dict(Counter(keys).most_common()), "label_marginal": {str(a): b for a, b in Counter(labs).items()},
                  "pids": pids}
    json.dump(out, open("analysis/pe015_inventory.json", "w"), indent=1)
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "pids"} if isinstance(v, dict) else v) for k, v in out.items()}, indent=1))

def rehearsal():
    t0 = time.time(); rows, _ = build(); g = gates(rows); out = {"gates": g, "runnable": runnable(g)}; smoke = {}
    for t in runnable(g):
        keys, labs, st, _, _ = make(rows, t); pm = H.Perm(st); ks = pm.shuffle(keys, random.Random(SEED_SHUFFLE))
        obs, p, nl = null_p(t, ks, labs, pm, 999, random.Random(SEED_NULL)); nl.sort()
        smoke[t] = {"stat_on_registered_shuffle": round(obs, 4), "p_R999": p, "null_mean": round(sum(nl) / len(nl), 4)}
    out["smoke_registered_shuffle_1599"] = smoke; out["runtime_s"] = round(time.time() - t0, 1)
    json.dump(out, open("analysis/pe015_rehearsal.json", "w"), indent=1); print(json.dumps(out, indent=1))

def test():
    t0 = time.time(); rows, _ = build(); g = gates(rows); run = runnable(g); res = {}
    for t in TESTS:
        if t not in run: res[t] = {"status": "NOT RUN (gate failed)"}; continue
        keys, labs, st, _, _ = make(rows, t); pm = H.Perm(st)
        obs, p, nl = null_p(t, keys, labs, pm, R_NULL, random.Random(SEED_NULL + TESTS.index(t) * 10000)); nl.sort()
        res[t] = {"n": len(keys), "stat": round(obs, 4), "null_mean": round(sum(nl) / len(nl), 4),
                  "null_q95": round(nl[int(0.95 * len(nl))], 4), "p": p}
    adj = G.holm([res[t]["p"] for t in run]) if run else []; verdict = {}
    for t in TESTS:
        if t in run: res[t]["p_holm"] = adj[run.index(t)]; verdict[t] = "SUPPORTED" if adj[run.index(t)] <= ALPHA else "NOT DETECTED"
        else: verdict[t] = "NOT TESTABLE"
    out = {"verdicts": verdict, "results": res, "gates": g, "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe015_results.json", "w"), indent=1); print(json.dumps(out, indent=1))

def audit():
    import pe014_ratio as K
    t0 = time.time(); cache, _ = K.all_sets(); slots, pairs, _ = cache["H2"]; sh = K.Shuf(slots, "H2")
    obs, p, nl = K.null_p(slots, pairs, sh, 9999, random.Random(SEED_AUDIT))
    pub = json.load(open("analysis/pe014_results.json"))["results"]["H2"]
    out = {"PE014_H2_new_seed": SEED_AUDIT, "R": 9999, "pairs": len(pairs), "T": obs, "null_mean": round(sum(nl) / len(nl), 3),
           "p": p, "published": {k: pub[k] for k in ("pairs", "T", "null_mean", "p")},
           "verdict_unchanged": obs == pub["T"] and len(pairs) == pub["pairs"] and p > 0.05, "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open("analysis/pe015_pe014_audit.json", "w"), indent=1); print(json.dumps(out, indent=1))

if __name__ == "__main__":
    {"inventory": inventory, "rehearsal": rehearsal, "test": test, "audit": audit}[sys.argv[1]]()
