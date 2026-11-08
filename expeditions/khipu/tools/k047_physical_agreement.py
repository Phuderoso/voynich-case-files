#!/usr/bin/env python3
"""K047 - cross-khipu physical-feature agreement on the three K019 pairs (README line 6).
Pre-registered in case-file/K047-physical-feature-agreement.md (prereg pushed before any
pair-feature agreement number). Alignment imported from k046_colour_agreement.py.

Primary fields: termination (T), majority knot direction (D). Census-only: twist, attachment.
Disclosed: length Spearman, knot-direction ordered tuple, leaders, nonzero-value units, N2.

Usage (from expeditions/khipu/):
  python3 tools/k047_physical_agreement.py fixture
  python3 tools/k047_physical_agreement.py run [--smoke]
Seeds: N1 4747, calibration 4748, power 4749, N2 4750, sensitivities 4751.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04.
"""
import hashlib, importlib.util, json, math, os, sqlite3, sys, time
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.join(HERE, "..", "analysis")
SHA = "607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db"
ALPHA = 0.05 / 6            # Bonferroni x 3 pairs x 2 primary fields
FPR_GATE = 0.08
POWER_BAR = 0.5
F_PLANT = 0.25
F_CURVE = (0.10, 0.15, 0.25, 0.40)
SEEDS = dict(null=4747, calib=4748, power=4749, n2=4750, sens=4751)
WALL = 540.0
PRIMARY = ("termination", "knot_dir")
CENSUS = ("twist", "attachment")


def norm(x):
    return None if x is None else (str(x).strip() or None)


def load_k046():
    spec = importlib.util.spec_from_file_location(
        "k046", os.path.join(HERE, "k046_colour_agreement.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ match / feature functions
def cat_match(a, b):
    """Identical non-None labels match; None never matches."""
    if a is None or b is None:
        return False
    return a == b


def knot_majority_from(dirs):
    """dirs = iterable of raw DIRECTION values. Returns (label_or_None, reason)."""
    usable = [d for d in (norm(x) for x in dirs) if d in ("S", "Z")]
    if not usable:
        return None, "no_usable_direction"
    ns, nz = usable.count("S"), usable.count("Z")
    if ns > nz:
        return "S", "ok"
    if nz > ns:
        return "Z", "ok"
    return "TIE", "ok"


def knot_tuple_from(dirs):
    usable = [d for d in (norm(x) for x in dirs) if d in ("S", "Z")]
    if not usable:
        return None, "no_usable_direction"
    return tuple(usable), "ok"


def run_fixture():
    cases = [
        ("term identical K", "K", "K", True),
        ("term identical B", "B", "B", True),
        ("term K != B", "K", "B", False),
        ("term K != U", "K", "U", False),
        ("term B != U", "B", "U", False),
        ("term empty never matches", None, "K", False),
        ("term both empty never matches", None, None, False),
        ("twist S == S", "S", "S", True),
        ("twist S != Z", "S", "Z", False),
        ("twist U != S", "U", "S", False),
        ("attach R == R", "R", "R", True),
        ("attach R != V", "R", "V", False),
        ("attach U != R", "U", "R", False),
        ("attach U != V", "U", "V", False),
        ("knot dir S == S", "S", "S", True),
        ("knot dir Z == Z", "Z", "Z", True),
        ("knot dir TIE == TIE", "TIE", "TIE", True),
        ("knot dir S != Z", "S", "Z", False),
        ("knot dir S != TIE", "S", "TIE", False),
        ("knot dir empty never", None, "Z", False),
    ]
    out, ok = [], True
    for name, a, b, want in cases:
        got = cat_match(a, b)
        out.append({"case": name, "expected": want, "got": got})
        ok &= got == want
    maj_cases = [
        ("majority all Z -> Z", ["Z", "Z", "Z"], "Z"),
        ("majority 3S+1Z -> S", ["S", "S", "S", "Z"], "S"),
        ("majority 2S+2Z -> TIE", ["S", "Z", "S", "Z"], "TIE"),
        ("majority ignores U and empty", ["Z", "U", None, "", "Z"], "Z"),
        ("majority no usable -> None", ["U", None, ""], None),
        ("majority single S -> S", ["S"], "S"),
    ]
    for name, dirs, want in maj_cases:
        got, _ = knot_majority_from(dirs)
        out.append({"case": name, "expected": want, "got": got})
        ok &= got == want
    tup, reason = knot_tuple_from(["S", "U", "Z", None, "S"])
    out.append({"case": "tuple drops U/empty keeps order", "expected": ("S", "Z", "S"), "got": tup})
    ok &= tup == ("S", "Z", "S")
    tup2, _ = knot_tuple_from(["U", None])
    out.append({"case": "tuple empty -> None", "expected": None, "got": tup2})
    ok &= tup2 is None
    return ok, out


# ------------------------------------------------------------------ physical fields
def load_physical(c):
    cord = {}
    for cid, tw, at, tm, fib, ln, th, ta in c.execute(
            "select CORD_ID, TWIST, ATTACHMENT_TYPE, TERMINATION, FIBER, "
            "CORD_LENGTH, THICKNESS, TWIST_ANGLE from cord"):
        cord[cid] = dict(twist=norm(tw), attachment=norm(at), termination=norm(tm),
                         fiber=norm(fib), length=ln, thickness=th, twist_angle=ta)
    knots = defaultdict(list)
    for cid, d, ko in c.execute(
            "select CORD_ID, DIRECTION, KNOT_ORDINAL from knot order by CORD_ID, KNOT_ORDINAL"):
        knots[cid].append(d)
    return cord, knots


def get_feat(cord, knots, cid, field):
    if field == "termination":
        v = cord[cid]["termination"]
        return (None, "empty_termination") if v is None else (v, "ok")
    if field == "twist":
        v = cord[cid]["twist"]
        return (None, "empty_twist") if v is None else (v, "ok")
    if field == "attachment":
        v = cord[cid]["attachment"]
        return (None, "empty_attachment") if v is None else (v, "ok")
    if field == "knot_dir":
        return knot_majority_from(knots.get(cid, []))
    if field == "knot_tuple":
        return knot_tuple_from(knots.get(cid, []))
    raise ValueError(field)


def attach(cord, knots, units, field):
    keep, excl = [], Counter()
    for u in units:
        fa, sa = get_feat(cord, knots, u["cidA"], field)
        fb, sb = get_feat(cord, knots, u["cidB"], field)
        if fa is None or fb is None:
            excl[f"A:{sa}|B:{sb}"] += 1
            continue
        keep.append({**u, "featA": fa, "featB": fb})
    return keep, excl


def match_matrix(us):
    n = len(us)
    M = np.zeros((n, n), dtype=np.int8)
    for i in range(n):
        ai = us[i]["featA"]
        for j in range(n):
            M[i, j] = ai == us[j]["featB"]
    return M


def null_bank(M, R, rng, blocks=None, chunk=2000):
    n = M.shape[0]
    out = np.empty(R, dtype=np.int32)
    idx = np.arange(n)
    done = 0
    while done < R:
        k = min(chunk, R - done)
        if blocks is None:
            P = rng.permuted(np.tile(idx, (k, 1)), axis=1)
        else:
            P = np.tile(idx, (k, 1))
            for blk in blocks:
                P[:, blk] = rng.permuted(np.tile(np.array(blk), (k, 1)), axis=1)
        out[done:done + k] = M[idx[None, :], P].sum(axis=1)
        done += k
    return out


def pval(obs, bank):
    return (1 + int((bank >= obs).sum())) / (len(bank) + 1)


def plant_power(us, f, Nrep, Rp, rng, alpha):
    n = len(us)
    hits = 0
    ps = []
    featA = [u["featA"] for u in us]
    featB = [u["featB"] for u in us]
    k = int(round(f * n))
    for _ in range(Nrep):
        perm = rng.permutation(n)
        B = [featB[p] for p in perm]
        if k:
            for s in rng.choice(n, size=k, replace=False):
                B[s] = featA[s]
        uu = [{"featA": featA[i], "featB": B[i]} for i in range(n)]
        M = match_matrix(uu)
        obs = int(np.trace(M))
        p = pval(obs, null_bank(M, Rp, rng))
        ps.append(p)
        hits += p < alpha
    return hits / Nrep, float(np.median(ps)), k


def ranks(x):
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x), dtype=float)
    r[order] = np.arange(1, len(x) + 1, dtype=float)
    xs = x[order]
    i = 0
    n = len(x)
    while i < n:
        j = i + 1
        while j < n and xs[j] == xs[i]:
            j += 1
        if j - i > 1:
            avg = 0.5 * ((i + 1) + j)
            r[order[i:j]] = avg
        i = j
    return r


def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    den = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    if den == 0:
        return 0.0
    return float((ra * rb).sum() / den)


def length_units(cord, units):
    keep, excl = [], Counter()
    for u in units:
        la, lb = cord[u["cidA"]]["length"], cord[u["cidB"]]["length"]
        if la is None or lb is None:
            excl["missing_length"] += 1
            continue
        keep.append({**u, "lenA": float(la), "lenB": float(lb)})
    return keep, excl


def census_block(us, excl, field):
    n = len(us)
    cntA = Counter(str(u["featA"]) for u in us)
    cntB = Counter(str(u["featB"]) for u in us)
    A = sum(u["featA"] == u["featB"] for u in us) if n else 0
    deg = n == 0 or len(cntA) < 2 or len(cntB) < 2
    return dict(field=field, n=n, excluded_units=dict(excl),
                distinct_A=len(cntA), distinct_B=len(cntB),
                counts_A=dict(cntA), counts_B=dict(cntB),
                raw_A=A, degenerate=bool(deg))


def evaluate_categorical(us, excl, field, pr, rng, smoke, t0):
    """Gates + primary statistic for one pair-field. Degenerate pair-fields skip FPR/power."""
    n = len(us)
    rec = census_block(us, excl, field)
    rec["role"] = "primary"
    if n < 10:
        rec["verdict"] = "NOT TESTABLE"
        rec["note"] = "n < 10"
        return rec
    if rec["degenerate"]:
        rec["verdict"] = "DEGENERATE"
        rec["p"] = None
        rec["note"] = "either side has < 2 distinct values on the analysed units; N1 has no variance"
        return rec
    M = match_matrix(us)
    R = 200 if smoke else 10000
    NCAL = 50 if smoke else 1000
    NPOW = 10 if smoke else 200
    RP = 200 if smoke else 2000
    NCURVE = 10 if smoke else 100
    # copy-all
    cp = [{**u, "featB": u["featA"]} for u in us]
    Mc = match_matrix(cp)
    obs_c = int(np.trace(Mc))
    pc = pval(obs_c, null_bank(Mc, RP, np.random.default_rng(SEEDS["power"] + 100)))
    rec["positive_control_copy_all"] = dict(A=obs_c, expected=n, p=pc,
                                            passed=bool(obs_c == n and pc < ALPHA))
    bank = null_bank(M, R, rng["null"])
    cal = []
    for _ in range(NCAL):
        perm = rng["calib"].permutation(n)
        cal.append(pval(int(M[np.arange(n), perm].sum()), bank))
    fpr_perm = float(np.mean(np.array(cal) < ALPHA))
    lo = math.ceil(0.1 * n)
    shifts = [k for k in range(1, n) if min(k, n - k) >= lo]
    sp = [pval(int(M[np.arange(n), (np.arange(n) + k) % n].sum()), bank) for k in shifts]
    fpr_shift = float(np.mean(np.array(sp) < ALPHA)) if sp else None
    pw, pmed, kpl = plant_power(us, F_PLANT, NPOW, RP, rng["power"], ALPHA)
    curve = {}
    for f in F_CURVE:
        if time.time() - t0 > WALL * 0.8:
            curve[str(f)] = "cut_by_wall"
            continue
        curve[str(f)] = plant_power(us, f, NCURVE, RP, rng["power"], ALPHA)[0]
    obs = int(np.trace(M))
    p = pval(obs, bank)
    blocks = [[i for i, u in enumerate(us) if u["group_pair"] == g] for g in range(len(pr))]
    blocks = [b for b in blocks if b]
    bank_n2 = null_bank(M, R, rng["n2"], blocks=blocks) if blocks else bank
    rec.update(observed_A=obs, rate=obs / n if n else None,
               null_mean=float(bank.mean()), null_sd=float(bank.std()),
               null_q95=float(np.quantile(bank, 0.95)), null_max=int(bank.max()),
               null_min=int(bank.min()), p=p,
               calibration=dict(fpr_perm=fpr_perm, n=NCAL, shift_offsets=len(shifts),
                                min_offset=lo, fpr_shift=fpr_shift,
                                shift_p_min=min(sp) if sp else None),
               power=dict(f=F_PLANT, k_planted=kpl, power=pw, median_p=pmed, n=NPOW,
                          curve=curve, curve_n=NCURVE),
               N2_within_group=dict(null_mean=float(bank_n2.mean()), p=pval(obs, bank_n2),
                                    note="descriptive, not a verdict"))
    if not rec["positive_control_copy_all"]["passed"] or fpr_perm > FPR_GATE or (
            fpr_shift is not None and fpr_shift > FPR_GATE):
        v = "TOOL EXCLUDED"
    elif pw < POWER_BAR:
        v = "NOT TESTABLE"
    elif p < ALPHA:
        v = "SUPPORTED"
    else:
        v = "NOT SUPPORTED"
    rec["verdict"] = v
    rec["matching_units"] = [dict(gA=u["gA"], gB=u["gB"], posA=u["posA"], posB=u["posB"],
                                  value=u["value"], feat=str(u["featA"]))
                             for u in us if u["featA"] == u["featB"]]
    return rec


def evaluate_spearman(cord, units, rng, smoke):
    us, excl = length_units(cord, units)
    n = len(us)
    rec = dict(field="cord_length_spearman", role="disclosed", n=n,
               excluded_units=dict(excl), note="disclosed, not a verdict")
    if n < 5:
        rec["verdict_note"] = "n < 5"
        return rec
    a = np.array([u["lenA"] for u in us], dtype=float)
    b = np.array([u["lenB"] for u in us], dtype=float)
    rec["length_var_A"] = float(a.var())
    rec["length_var_B"] = float(b.var())
    rec["length_mean_A"] = float(a.mean())
    rec["length_mean_B"] = float(b.mean())
    if a.var() == 0 or b.var() == 0:
        rec["degenerate"] = True
        rec["rho"] = None
        return rec
    rec["degenerate"] = False
    rho = spearman(a, b)
    R = 200 if smoke else 10000
    bank = np.empty(R)
    rngn = rng["sens"]
    for i in range(R):
        bank[i] = spearman(a, rngn.permutation(b))
    p = (1 + int((bank >= rho).sum())) / (R + 1)
    rec.update(rho=rho, p=p, null_mean=float(bank.mean()), null_sd=float(bank.std()),
               null_q95=float(np.quantile(bank, 0.95)))
    # copy-all sanity
    rec["copy_all_rho"] = spearman(a, a)
    return rec


def main(smoke=False):
    t0 = time.time()
    ok, fx = run_fixture()
    if not ok:
        print(json.dumps(fx, indent=1))
        sys.exit("REFUSED: match-function fixture failed; no results written")
    k046 = load_k046()
    db = next((p for p in k046.DB_CANDIDATES if os.path.exists(p)), None)
    if db is None:
        sys.exit("EXCLUDED: khipu.db not found")
    h = hashlib.sha256(open(db, "rb").read()).hexdigest()
    if h != SHA:
        sys.exit(f"EXCLUDED: khipu.db hash {h} != {SHA}")
    c = sqlite3.connect(f"file:{os.path.realpath(db)}?mode=ro", uri=True)
    S = k046.load(c)
    cord, knots = load_physical(c)
    print(f"loaded {time.time()-t0:.1f}s", flush=True)
    rng = {k: np.random.default_rng(v) for k, v in SEEDS.items()}
    out = dict(cycle="K047", db=f"OKR khipu.db @ 4039ca5 sha256 {h}", smoke=smoke,
               alpha=ALPHA, fpr_gate=FPR_GATE, power_bar=POWER_BAR, f_plant=F_PLANT,
               seeds=SEEDS, primary_fields=list(PRIMARY), census_fields=list(CENSUS),
               fixture_passed=ok, fixture=fx, pairs={})
    built = {}
    for a, b in k046.PAIRS:
        key = f"{a}/{b}"
        pr, Vs, units, leaders = k046.build_units(S, a, b)
        if (len(pr), sum(Vs)) != k046.K019[key]:
            sys.exit(f"EXCLUDED: K019 drift on {key}: {(len(pr), sum(Vs))} != {k046.K019[key]}")
        built[key] = (pr, Vs, units, leaders)
    print("K019 consistency ok", {k: (len(v[0]), sum(v[1])) for k, v in built.items()}, flush=True)

    for key, (pr, Vs, units, leaders) in built.items():
        P = out["pairs"].setdefault(key, {})
        P.update(matched_groups=len(pr), V=Vs, V_tot=sum(Vs),
                 aligned_nonleader_units=len(units))
        t1 = time.time()
        P["census"] = {}
        for field in CENSUS:
            us, excl = attach(cord, knots, units, field)
            P["census"][field] = census_block(us, excl, field)
        P["primary"] = {}
        for field in PRIMARY:
            us, excl = attach(cord, knots, units, field)
            rec = evaluate_categorical(us, excl, field, pr, rng, smoke, t0)
            P["primary"][field] = rec
            print(f"{key} {field} n={rec.get('n')} A={rec.get('observed_A', rec.get('raw_A'))} "
                  f"p={rec.get('p')} -> {rec.get('verdict')} ({time.time()-t1:.1f}s)", flush=True)
        sens = {}
        us_t, excl_t = attach(cord, knots, units, "knot_tuple")
        rec_t = evaluate_categorical(us_t, excl_t, "knot_tuple", pr, rng, smoke, t0)
        rec_t["role"] = "disclosed"
        rec_t["note"] = ("disclosed ordered-tuple knot direction, not a verdict; "
                         + rec_t.get("note", ""))
        sens["knot_tuple"] = rec_t
        for field in PRIMARY:
            us, excl = attach(cord, knots, units + leaders, field)
            if rec0 := P["primary"][field]:
                if rec0.get("verdict") == "DEGENERATE" or rec0.get("n", 0) < 10:
                    # still report raw with-leaders census
                    sens[f"{field}_with_leaders"] = census_block(us, excl, field)
                    sens[f"{field}_with_leaders"]["note"] = "disclosed, not a verdict"
                else:
                    recL = evaluate_categorical(us, excl, field, pr, rng, True, t0)
                    # smoke-sized N for the sensitivity to keep the wall; recompute proper p at full R
                    if recL.get("verdict") not in ("DEGENERATE", "NOT TESTABLE") or recL.get("p") is not None:
                        pass
                    # Always recompute a full-R p when non-degenerate and n>=10
                    if recL.get("degenerate"):
                        sens[f"{field}_with_leaders"] = recL
                        sens[f"{field}_with_leaders"]["note"] = "disclosed, not a verdict"
                    elif len(us) >= 10:
                        M = match_matrix(us)
                        obs = int(np.trace(M))
                        p = pval(obs, null_bank(M, 200 if smoke else 10000, rng["sens"]))
                        sens[f"{field}_with_leaders"] = dict(
                            n=len(us), A=obs, p=p, note="disclosed, not a verdict")
                    else:
                        sens[f"{field}_with_leaders"] = recL
            unz_src = [u for u in units if u["value"] != 0]
            usz, exclz = attach(cord, knots, unz_src, field)
            if P["primary"][field].get("degenerate") or len(usz) < 10:
                sens[f"{field}_nonzero_value_units"] = census_block(usz, exclz, field)
                sens[f"{field}_nonzero_value_units"]["note"] = "disclosed, not a verdict"
            else:
                M = match_matrix(usz)
                obs = int(np.trace(M))
                p = pval(obs, null_bank(M, 200 if smoke else 10000, rng["sens"]))
                sens[f"{field}_nonzero_value_units"] = dict(
                    n=len(usz), A=obs, p=p, note="disclosed, not a verdict")
        sens["cord_length_spearman"] = evaluate_spearman(cord, units, rng, smoke)
        P["sensitivities"] = sens
        print(f"{key} done ({time.time()-t1:.1f}s)", flush=True)
        json.dump(out, open(os.path.join(AN, "k047_checkpoint.json"), "w"), indent=1, default=list)

    out["sec"] = round(time.time() - t0, 1)
    fn = "k047_smoke.json" if smoke else "k047_results.json"
    json.dump(out, open(os.path.join(AN, fn), "w"), indent=1, default=list)
    print("wrote", fn, out["sec"], "s")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "fixture":
        ok, fx = run_fixture()
        print(json.dumps(fx, indent=1))
        sys.exit(0 if ok else 1)
    elif mode == "run":
        main(smoke="--smoke" in sys.argv)
    else:
        sys.exit(__doc__)
