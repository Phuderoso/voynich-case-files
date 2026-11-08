#!/usr/bin/env python3
"""K051 - colour agreement on the shared run-collapsed block of the unconfirmed lead
KH0240 (UR004, Leymebamba) . KH0496 (UR260, Incahuasi) (README lines 3 and 6).
Pre-registered in case-file/K051-lead-block-colour.md (prereg pushed before any pair-colour number).

Block: the K012/K027/K028 run-collapsed pendant pattern P = 1,2,1,2,3,1,2,1,3 (level-1 pendants in
cord order, DUPLICATE_FLAG khipus omitted, R5 multi-number cords zeroed, >= 10 nonzero; runs collapsed).
Run lengths differ (A 4,1,1,1,1,1,1,1,1; B 1,1,3,1,1,2,1,1,1), so there is no 1-1 cord alignment.
Unit = one collapsed run (n = 9). Unit colour = modal first-colour tuple among the run's coloured
cords (K045/K046 field); tie -> the tied tuple carried by the earliest cord in the run.
Statistic A = number of the 9 runs whose colours match (K046 colour_match, imported).
Null N1: permute side B's 9 run colours among the 9 units. The null distribution is computed EXACTLY
(all 9! permutations, by a subset DP on the 9x9 match matrix); a Monte Carlo bank (R = 10 000) is a
cross-check only.

Usage (from expeditions/khipu/):
  python3 tools/k051_lead_block_colour.py fixture   # match-function fixture only (no data)
  python3 tools/k051_lead_block_colour.py values    # values-only consistency gate (no colour)
  python3 tools/k051_lead_block_colour.py run [--smoke]  # full run -> analysis/k051_results.json
Seeds: MC cross-check 5151, calibration 5152, power 5153, sensitivities 5154, copy-all MC 5155.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04.
"""
import hashlib, importlib.util, json, math, os, sqlite3, sys, time
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.join(HERE, "..", "analysis")
DB_CANDIDATES = [os.path.join(HERE, "..", "khipu.db"), os.path.join(HERE, "..", "data", "khipu.db")]
SHA = "607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db"
ALPHA = 0.05                 # one named pair, one primary hypothesis; no Bonferroni
FPR_GATE = 0.08
POWER_BAR = 0.5
F_PLANT = 0.25
F_CURVE = (0.10, 0.15, 0.25, 0.40, 0.55)
SEEDS = dict(mc=5151, calib=5152, power=5153, sens=5154, copyall=5155)
WALL = 540.0
P = (1, 2, 1, 2, 3, 1, 2, 1, 3)
PAIR = dict(key="KH0240/KH0496", a="KH0240", b="KH0496", a_inv="UR004", b_inv="UR260",
            runlen_a=(4, 1, 1, 1, 1, 1, 1, 1, 1), runlen_b=(1, 1, 3, 1, 1, 2, 1, 1, 1))


def load_k046():
    spec = importlib.util.spec_from_file_location("k046", os.path.join(HERE, "k046_colour_agreement.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


K046 = load_k046()
colour_match = K046.colour_match
norm = K046.norm
run_fixture = K046.run_fixture


# ------------------------------------------------------------------ values (K027/K028 sequences; no colour)
def load_sequences(c):
    dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
    meta = {}
    for r in c.execute("select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM, MUSEUM_NAME, MUSEUM_NUM, "
                       "PROVENANCE, REGION from khipu_main"):
        meta[r[0]] = dict(okr=r[1] or "", inv=r[2] or "", museum=(r[3] or "").strip().strip('"'),
                          mnum=(r[4] or "").strip(), provenance=r[5] or "", region=r[6] or "")
    val = defaultdict(int)
    for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
        if v is not None:
            val[cid] += int(v)

    def place_(v):
        p = 0
        while v % 10 == 0:
            v //= 10
            p += 1
        return p
    clpl = defaultdict(set)
    clcd = {}
    for cid_, cl_, t_, v_ in c.execute("select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
        t_ = (t_ or "").strip()
        if t_ in ("S", "L", "E") and v_:
            clpl[cl_].add(place_(int(v_)) if t_ == "S" else 0)
        clcd[cl_] = cid_
    ordn_ = {r[0]: r[1] for r in c.execute("select CLUSTER_ID, ORDINAL from knot_cluster")}
    bc_ = defaultdict(dict)
    for cl_, pl_ in clpl.items():
        if len(pl_) == 1 and ordn_.get(cl_) is not None:
            bc_[clcd[cl_]][ordn_[cl_]] = next(iter(pl_))
    R5 = {cd for cd, d in bc_.items() if len(d) >= 2 and not all(
        a > b for a, b in zip([d[o] for o in sorted(d)], [d[o] for o in sorted(d)][1:]))}
    kh = defaultdict(list)
    cids = defaultdict(list)
    for khid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 "
                               "order by KHIPU_ID, CORD_ORDINAL"):
        if khid in dups:
            continue
        kh[khid].append(0 if cid in R5 else val.get(cid, 0))
        cids[khid].append(cid)
    ids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]
    byokr = {meta[k]["okr"]: k for k in ids}
    return dict(kh=kh, cids=cids, ids=ids, byokr=byokr, meta=meta, n_R5=len(R5))


def collapse_runs(seq, cid):
    """[(value, [cord ids...], first_cord_index)] in cord order."""
    out = []
    for i, (v, c_) in enumerate(zip(seq, cid)):
        if out and out[-1][0] == v:
            out[-1][1].append(c_)
        else:
            out.append((v, [c_], i))
    return out


def find_block(runs):
    vals = [r[0] for r in runs]
    return [i for i in range(len(vals) - len(P) + 1) if tuple(vals[i:i + len(P)]) == P]


def build_block(S):
    res = dict(n_ids=len(S["ids"]), n_R5=S["n_R5"])
    side = {}
    for tag in ("a", "b"):
        okr = PAIR[tag]
        if okr not in S["byokr"]:
            return dict(ok=False, reason=f"{okr} not eligible"), None
        k = S["byokr"][okr]
        runs = collapse_runs(S["kh"][k], S["cids"][k])
        hits = find_block(runs)
        if len(hits) != 1:
            return dict(ok=False, reason=f"{okr}: P occurs {len(hits)} times (need exactly 1)"), None
        blk = runs[hits[0]:hits[0] + len(P)]
        rl = tuple(len(r[1]) for r in blk)
        side[tag] = dict(khipu_id=k, run_start=hits[0], cord_start_index=blk[0][2],
                         n_collapsed=len(runs), n_pendants=len(S["kh"][k]),
                         runlen=list(rl), runs=blk, meta=S["meta"][k])
        res[tag] = {kk: vv for kk, vv in side[tag].items() if kk != "runs"}
    ok = (tuple(side["a"]["runlen"]) == PAIR["runlen_a"] and tuple(side["b"]["runlen"]) == PAIR["runlen_b"])
    res["ok"] = ok
    res["reason"] = None if ok else "run lengths differ from K012's published values (drift)"
    # Other eligible khipus containing P (K027 T1 says 0)
    res["other_P_holders"] = [S["meta"][k]["okr"] for k in S["ids"]
                              if k not in (side["a"]["khipu_id"], side["b"]["khipu_id"])
                              and find_block(collapse_runs(S["kh"][k], S["cids"][k]))]
    return res, side


# ------------------------------------------------------------------ colour (only after values gate)
def load_colour(c):
    first = {}
    rows = c.execute("select color_id, CORD_ID, RANGE_BEG, FULL_COLOR, COLOR_CD_1, COLOR_CD_2, "
                     "COLOR_CD_3, COLOR_CD_4, COLOR_CD_5, OPERATOR_1, OPERATOR_2, OPERATOR_3, "
                     "OPERATOR_4, OPERATOR_5 from ascher_cord_color").fetchall()
    for r in sorted(rows, key=lambda r: (r[1], r[2] if r[2] is not None else 1e18, r[0])):
        first.setdefault(r[1], r)

    def colour(cid):
        r = first.get(cid)
        if r is None:
            return None, "no_colour_row"
        if not norm(r[3]):
            return None, "empty_full_color"
        comps = tuple(norm(x) for x in r[4:9] if norm(x))
        ops = tuple(norm(x) for x in r[9:14] if norm(x))
        if not comps:
            return None, "no_components"
        return (comps, ops), "ok"
    return colour


def run_colour(colour, cids, rule="modal"):
    """modal: most frequent exact tuple among coloured cords; tie -> earliest cord's tuple among the tied.
    first: the first cord of the run (sensitivity)."""
    cols = [(i, colour(c_)) for i, c_ in enumerate(cids)]
    good = [(i, col) for i, (col, st) in cols if col is not None]
    reasons = Counter(st for _, (col, st) in cols if col is None)
    if rule == "first":
        col, st = colour(cids[0])
        return col, dict(rule="first", status=st)
    if not good:
        return None, dict(rule="modal", status="no_coloured_cord", reasons=dict(reasons))
    cnt = Counter(col for _, col in good)
    top = max(cnt.values())
    tied = {col for col, n in cnt.items() if n == top}
    chosen = next(col for _, col in good if col in tied)
    return chosen, dict(rule="modal", n_cords=len(cids), n_coloured=len(good), top=top,
                        tie=len(tied) > 1, n_tied=len(tied), reasons=dict(reasons))


def pretty(col):
    if col is None:
        return None
    comps, ops = col
    return "".join(x for t in zip(comps, ops + ("",)) for x in t)


# ------------------------------------------------------------------ exact permutation null
def exact_dist(M):
    """Distribution of trace(M[:, perm]) over all n! permutations, exact (subset DP).
    Returns counts c[t] = #perms with exactly t matches (python ints)."""
    n = M.shape[0]
    dp = {0: [1]}
    for i in range(n):
        nd = {}
        for mask, poly in dp.items():
            for j in range(n):
                if mask >> j & 1:
                    continue
                m2 = mask | (1 << j)
                sh = int(M[i, j])
                q = nd.setdefault(m2, [0] * (n + 1))
                for t, v in enumerate(poly):
                    if v:
                        q[t + sh] += v
        dp = nd
    out = dp[(1 << n) - 1]
    return out


def exact_p(obs, dist):
    tot = sum(dist)
    return sum(dist[obs:]) / tot


def mc_bank(M, R, rng):
    n = M.shape[0]
    idx = np.arange(n)
    Pm = rng.permuted(np.tile(idx, (R, 1)), axis=1)
    return M[idx[None, :], Pm].sum(axis=1)


def match_matrix(cA, cB, by=False):
    n = len(cA)
    return np.array([[colour_match(cA[i], cB[j], by) for j in range(n)] for i in range(n)], dtype=np.int8)


def degeneracy_reason(cA, cB):
    if not cA:
        return "no_coloured_units"
    sA, sB = set(cA), set(cB)
    if not any(colour_match(a, b) for a in sA for b in sB):
        return "no_shared_matching_colour"
    if len(sA) < 2:
        return "A_monochromatic"
    if len(sB) < 2:
        return "B_monochromatic"
    return None


def plant_power(cA, cB, f, Nrep, rng):
    n = len(cA)
    k = int(round(f * n))
    hits, ps = 0, []
    for _ in range(Nrep):
        perm = rng.permutation(n)
        B = [cB[p] for p in perm]
        for s in rng.choice(n, size=min(k, n), replace=False):
            B[int(s)] = cA[int(s)]
        M = match_matrix(cA, B)
        p = exact_p(int(np.trace(M)), exact_dist(M))
        ps.append(p)
        hits += p < ALPHA
    return hits / Nrep, float(np.median(ps)), k


def open_db():
    db = next((p for p in DB_CANDIDATES if os.path.exists(p)), None)
    if db is None:
        sys.exit("EXCLUDED: khipu.db not found")
    h = hashlib.sha256(open(db, "rb").read()).hexdigest()
    if h != SHA:
        sys.exit(f"EXCLUDED: khipu.db hash {h} != {SHA}")
    return sqlite3.connect(f"file:{os.path.realpath(db)}?mode=ro", uri=True), h


def exact_selftest():
    """Exact DP vs brute force on small random matrices (no data)."""
    import itertools
    rng = np.random.default_rng(0)
    for n in (3, 4, 5, 6):
        for _ in range(5):
            M = (rng.random((n, n)) < 0.4).astype(np.int8)
            bf = [0] * (n + 1)
            for pm in itertools.permutations(range(n)):
                bf[int(sum(M[i, pm[i]] for i in range(n)))] += 1
            if bf != exact_dist(M):
                return False
    I = np.eye(9, dtype=np.int8)  # derangement check: 133496 perms with 0 fixed points
    d = exact_dist(I)
    return d[0] == 133496 and sum(d) == math.factorial(9)


def values_only():
    ok, fx = run_fixture()
    st = exact_selftest()
    c, h = open_db()
    S = load_sequences(c)
    res, _ = build_block(S)
    out = dict(cycle="K051", db=f"OKR khipu.db @ 4039ca5 sha256 {h}", fixture_passed=ok,
               exact_dp_selftest=st, consistency=res)
    print(json.dumps(out, indent=1, default=str))
    sys.exit(0 if (ok and st and res.get("ok")) else 1)


def main(smoke=False):
    t0 = time.time()
    ok, fx = run_fixture()
    st = exact_selftest()
    if not (ok and st):
        sys.exit("REFUSED: fixture or exact-DP self-test failed; no results written")
    c, h = open_db()
    S = load_sequences(c)
    res, side = build_block(S)
    if not res["ok"]:
        sys.exit(f"EXCLUDED: {res['reason']}")
    print("values consistency ok", res["a"]["runlen"], res["b"]["runlen"], flush=True)

    colour = load_colour(c)  # colour read only after the values gate
    R = 500 if smoke else 10000
    NCAL = 100 if smoke else 1000
    NPOW = 20 if smoke else 200
    NCURVE = 10 if smoke else 100
    rng = {k: np.random.default_rng(v) for k, v in SEEDS.items()}
    out = dict(cycle="K051", db=f"OKR khipu.db @ 4039ca5 sha256 {h}", smoke=smoke, alpha=ALPHA,
               fpr_gate=FPR_GATE, power_bar=POWER_BAR, f_plant=F_PLANT, seeds=SEEDS, R_mc=R,
               n_calibration=NCAL, n_power=NPOW, fixture_passed=ok, fixture=fx,
               exact_dp_selftest=st, consistency=res)

    units = []
    for r in range(len(P)):
        ra, rb = side["a"]["runs"][r], side["b"]["runs"][r]
        ca, ia = run_colour(colour, ra[1])
        cb, ib = run_colour(colour, rb[1])
        fa, _ = run_colour(colour, ra[1], "first")
        fb, _ = run_colour(colour, rb[1], "first")
        units.append(dict(run=r, value=ra[0], lenA=len(ra[1]), lenB=len(rb[1]),
                          colA=ca, colB=cb, firstA=fa, firstB=fb, infoA=ia, infoB=ib,
                          cordsA=[pretty(colour(x)[0]) for x in ra[1]],
                          cordsB=[pretty(colour(x)[0]) for x in rb[1]]))
    out["units"] = [{k: (pretty(v) if k in ("colA", "colB", "firstA", "firstB") else v)
                     for k, v in u.items()} for u in units]
    us = [u for u in units if u["colA"] is not None and u["colB"] is not None]
    out["n_units"] = len(units)
    out["n_coloured_units"] = n = len(us)
    out["excluded_units"] = [u["run"] for u in units if u not in us]
    cA = [u["colA"] for u in us]
    cB = [u["colB"] for u in us]

    # copy-all positive control
    if n:
        Mc = match_matrix(cA, cA)
        oc = int(np.trace(Mc))
        want = sum("PK" not in a[0] for a in cA)
        pc = exact_p(oc, exact_dist(Mc))
        pmc = (1 + int((mc_bank(Mc, 2000, rng["copyall"]) >= oc).sum())) / 2001
        out["copy_all"] = dict(A=oc, expected=want, p_exact=pc, p_mc=pmc,
                               passed=bool(oc == want and pc < ALPHA))
    else:
        out["copy_all"] = dict(passed=False, note="no coloured units")

    deg = degeneracy_reason(cA, cB)
    out["degeneracy_reason"] = deg
    out["colour_counts_A"] = dict(Counter(pretty(x) for x in cA).most_common())
    out["colour_counts_B"] = dict(Counter(pretty(x) for x in cB).most_common())
    M = match_matrix(cA, cB) if n else None
    obs = int(np.trace(M)) if n else 0
    out["observed_A"] = obs
    if deg:
        out.update(p_exact=None, verdict="DEGENERATE",
                   note=f"no colour variation that a shuffle of B can turn into extra matches ({deg})")
    else:
        dist = exact_dist(M)
        tot = sum(dist)
        mean = sum(t * v for t, v in enumerate(dist)) / tot
        pex = exact_p(obs, dist)
        bank = mc_bank(M, R, rng["mc"])
        pmc = (1 + int((bank >= obs).sum())) / (R + 1)
        # calibration FPR: fresh permutations scored with the exact p
        cal = []
        for _ in range(NCAL):
            pm = rng["calib"].permutation(n)
            cal.append(exact_p(int(M[np.arange(n), pm].sum()), dist))
        fpr = float(np.mean(np.array(cal) < ALPHA))
        lo = math.ceil(0.1 * n)
        shifts = [k for k in range(1, n) if min(k, n - k) >= lo]
        sp = [exact_p(int(M[np.arange(n), (np.arange(n) + k) % n].sum()), dist) for k in shifts]
        fprs = float(np.mean(np.array(sp) < ALPHA)) if sp else None
        pw, pmed, kpl = plant_power(cA, cB, F_PLANT, NPOW, rng["power"])
        curve = {}
        for f in F_CURVE:
            if time.time() - t0 > WALL * 0.8:
                curve[str(f)] = "cut_by_wall"
                continue
            curve[str(f)] = plant_power(cA, cB, f, NCURVE, rng["power"])[0]
        crit = next((t for t in range(n + 1) if exact_p(t, dist) < ALPHA), None)
        out.update(null_exact_counts=[int(x) for x in dist], null_mean=mean, p_exact=pex,
                   p_mc=pmc, mc_mean=float(bank.mean()), critical_A=crit,
                   calibration=dict(fpr_perm=fpr, n=NCAL, shift_offsets=len(shifts),
                                    fpr_shift=fprs, shift_p=sp),
                   power=dict(f=F_PLANT, k_planted=kpl, power=pw, median_p=pmed, n=NPOW,
                              curve=curve, curve_n=NCURVE))
        copy_ok = out["copy_all"]["passed"]
        if (not copy_ok) or fpr > FPR_GATE or (fprs is not None and fprs > FPR_GATE):
            v = "TOOL EXCLUDED"
        elif pex < ALPHA:
            v = "SUPPORTED"
        elif pw < POWER_BAR:
            v = "NOT TESTABLE"
        else:
            v = "NOT SUPPORTED"
        out["verdict"] = v
        # sensitivities (not verdicts)
        sens = {}
        Mb = match_matrix(cA, cB, True)
        ob = int(np.trace(Mb))
        sens["BY_eq_YB"] = dict(A=ob, p_exact=exact_p(ob, exact_dist(Mb)))
        fu = [u for u in units if u["firstA"] is not None and u["firstB"] is not None]
        fA, fB = [u["firstA"] for u in fu], [u["firstB"] for u in fu]
        if fu and not degeneracy_reason(fA, fB):
            Mf = match_matrix(fA, fB)
            of = int(np.trace(Mf))
            sens["first_cord_rule"] = dict(n=len(fu), A=of, p_exact=exact_p(of, exact_dist(Mf)))
        else:
            sens["first_cord_rule"] = dict(n=len(fu), degenerate=degeneracy_reason(fA, fB) if fu else "none")
        sens["note"] = "descriptive only, not verdicts"
        out["sensitivities"] = sens
    out["matching_runs"] = [dict(run=u["run"], value=u["value"], colour=pretty(u["colA"]))
                            for u in us if colour_match(u["colA"], u["colB"])]
    out["sec"] = round(time.time() - t0, 1)
    fn = "k051_smoke.json" if smoke else "k051_results.json"
    json.dump(out, open(os.path.join(AN, fn), "w"), indent=1, default=str)
    print(f"A={obs}/{n} p_exact={out.get('p_exact')} verdict={out.get('verdict')} sec={out['sec']}")
    print("wrote", fn)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "fixture":
        ok, fx = run_fixture()
        print(json.dumps(fx, indent=1), "\nexact DP self-test:", exact_selftest())
        sys.exit(0 if ok else 1)
    elif mode == "values":
        values_only()
    elif mode == "run":
        main(smoke="--smoke" in sys.argv)
    else:
        sys.exit(__doc__)
