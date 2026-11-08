#!/usr/bin/env python3
"""K048 - rare-label concordance on the three K019 pairs (README line 6).
Pre-registered in case-file/K048-rare-label-concordance.md (prereg pushed before any
pair-field dual-rare count). Alignment imported from k046_colour_agreement.py.
Feature extraction reused from K047 (termination trim; majority knot direction S/Z/TIE).

Primary: H_T = dual TERMINATION 'B' (broken); H_D = dual majority knot direction 'S'.
Statistic A = count of usable units where BOTH sides carry the rare label
(NOT overall equality — K047 already ran that).
Null N1: permute side B's feature labels among the pair-field's n usable units.

Usage (from expeditions/khipu/):
  python3 tools/k048_rare_label_concordance.py fixture
  python3 tools/k048_rare_label_concordance.py run [--smoke]
Seeds: N1 4848, calibration 4849, power 4850, N2 4851, sensitivities 4852.
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
F_PLANT = 0.50              # share of A's rare marks planted onto B
F_CURVE = (0.25, 0.50, 0.75, 1.00)  # descriptive rare-share curve
SEEDS = dict(null=4848, calib=4849, power=4850, n2=4851, sens=4852)
WALL = 540.0
PRIMARY = ("termination", "knot_dir")
RARE = {"termination": "B", "knot_dir": "S"}


def norm(x):
    return None if x is None else (str(x).strip() or None)


def load_k046():
    spec = importlib.util.spec_from_file_location(
        "k046", os.path.join(HERE, "k046_colour_agreement.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ match / feature functions
def is_dual_rare(a, b, rare):
    """Both sides defined and both equal to the rare label. None/empty never matches."""
    if a is None or b is None:
        return False
    return a == rare and b == rare


def dual_rare_count(As, Bs, rare):
    if len(As) != len(Bs):
        raise ValueError("label lists must be the same length")
    return sum(is_dual_rare(a, b, rare) for a, b in zip(As, Bs))


def knot_majority_from(dirs):
    """dirs = iterable of raw DIRECTION values. Returns (label_or_None, reason).
    Same rule as K047: usable S/Z only; empty → no_feature (unit excluded)."""
    usable = [d for d in (norm(x) for x in dirs) if d in ("S", "Z")]
    if not usable:
        return None, "no_usable_direction"
    ns, nz = usable.count("S"), usable.count("Z")
    if ns > nz:
        return "S", "ok"
    if nz > ns:
        return "Z", "ok"
    return "TIE", "ok"


def run_fixture():
    cases = [
        ("term B=B matches", "B", "B", "B", True),
        ("term K != B", "K", "B", "B", False),
        ("term B != K", "B", "K", "B", False),
        ("term K=K is not dual-rare", "K", "K", "B", False),
        ("term U != B", "U", "B", "B", False),
        ("term empty excluded not matched", None, "B", "B", False),
        ("term B vs empty not matched", "B", None, "B", False),
        ("term both empty not matched", None, None, "B", False),
        ("dir S=S matches", "S", "S", "S", True),
        ("dir Z != S", "Z", "S", "S", False),
        ("dir S != Z", "S", "Z", "S", False),
        ("dir TIE != S", "TIE", "S", "S", False),
        ("dir S != TIE", "S", "TIE", "S", False),
        ("dir Z=Z is not dual-rare", "Z", "Z", "S", False),
        ("dir TIE=TIE is not dual-rare", "TIE", "TIE", "S", False),
        ("dir empty excluded not matched", None, "S", "S", False),
    ]
    out, ok = [], True
    for name, a, b, rare, want in cases:
        got = is_dual_rare(a, b, rare)
        out.append({"case": name, "expected": want, "got": got})
        ok &= got == want

    # Dual-rare count on a tiny hand example (no data):
    # A: B K B K B   (rares at 0,2,4)     B: B B K K B   (rares at 0,1,4)
    # dual-rare positions: 0 and 4 → A = 2
    hand_A = ["B", "K", "B", "K", "B"]
    hand_B = ["B", "B", "K", "K", "B"]
    hand = dual_rare_count(hand_A, hand_B, "B")
    out.append({"case": "hand example dual-rare count", "expected": 2, "got": hand})
    ok &= hand == 2
    # Non-rare equalities in the hand example must not inflate A
    hand_eq = sum(a == b for a, b in zip(hand_A, hand_B))
    out.append({"case": "hand example equality != dual-rare", "expected": 3, "got": hand_eq})
    ok &= hand_eq == 3 and hand == 2

    # Hypergeometric edge: 0 rares on A → A = 0 regardless of B
    edge = dual_rare_count(["K", "K", "K"], ["B", "K", "B"], "B")
    out.append({"case": "hypergeometric edge 0 rares on A -> A=0", "expected": 0, "got": edge})
    ok &= edge == 0
    edgeB = dual_rare_count(["B", "K", "B"], ["K", "K", "K"], "B")
    out.append({"case": "hypergeometric edge 0 rares on B -> A=0", "expected": 0, "got": edgeB})
    ok &= edgeB == 0
    # All-rare on A: A equals n_rare_B (fixed by margins)
    allA = dual_rare_count(["B", "B", "B"], ["B", "K", "B"], "B")
    out.append({"case": "all-rare on A -> A = n_rare_B", "expected": 2, "got": allA})
    ok &= allA == 2

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
    return ok, out


# ------------------------------------------------------------------ physical fields (K047)
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
    if field == "knot_dir":
        return knot_majority_from(knots.get(cid, []))
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


def rare_match_matrix(us, rare):
    """M[i, j] = 1 iff A[i] is rare AND B[j] is rare. Trace = dual-rare count."""
    n = len(us)
    A_rare = np.array([u["featA"] == rare for u in us], dtype=np.int8)
    B_rare = np.array([u["featB"] == rare for u in us], dtype=np.int8)
    return np.outer(A_rare, B_rare).astype(np.int8)


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


def plant_rare_power(us, f, Nrep, Rp, rng, alpha, rare):
    """Base = a random N1 permutation of B. Then, among units where A is rare,
    overwrite B to the rare label on a random subset of size
    max(1, round(f * n_rare_A)). p from a fresh N1 bank (margins after planting)."""
    n = len(us)
    featA = [u["featA"] for u in us]
    featB = [u["featB"] for u in us]
    rareA_idx = [i for i, a in enumerate(featA) if a == rare]
    n_rare_A = len(rareA_idx)
    if n_rare_A < 1:
        return None, None, 0
    k = max(1, int(round(f * n_rare_A)))
    k = min(k, n_rare_A)
    hits = 0
    ps = []
    for _ in range(Nrep):
        perm = rng.permutation(n)
        B = [featB[p] for p in perm]
        chosen = rng.choice(np.array(rareA_idx), size=k, replace=False)
        for s in chosen:
            B[int(s)] = rare
        uu = [{"featA": featA[i], "featB": B[i]} for i in range(n)]
        M = rare_match_matrix(uu, rare)
        obs = int(np.trace(M))
        p = pval(obs, null_bank(M, Rp, rng))
        ps.append(p)
        hits += p < alpha
    return hits / Nrep, float(np.median(ps)), k


def margins(us, rare):
    n = len(us)
    nA = sum(u["featA"] == rare for u in us)
    nB = sum(u["featB"] == rare for u in us)
    A = sum(is_dual_rare(u["featA"], u["featB"], rare) for u in us)
    return n, nA, nB, A


def is_degenerate(n, nA, nB):
    """Either side has 0 rares, or either side is all-rare: A is fixed by the margins."""
    if n == 0:
        return True
    return nA == 0 or nB == 0 or nA == n or nB == n


def census_rares(us, excl, field, rare):
    n, nA, nB, A = margins(us, rare)
    cntA = Counter(str(u["featA"]) for u in us)
    cntB = Counter(str(u["featB"]) for u in us)
    return dict(field=field, rare_label=rare, n=n,
                n_rare_A=nA, n_rare_B=nB, observed_A=A,
                excluded_units=dict(excl),
                counts_A=dict(cntA), counts_B=dict(cntB),
                degenerate=bool(is_degenerate(n, nA, nB)))


def copy_all_units(us, rare):
    """B_rare[i] := A_rare[i] for all i, so rare-status margins match exactly.
    Implemented by copying A's feature label (rare or not) onto B."""
    return [{**u, "featB": u["featA"]} for u in us]


def evaluate(us, excl, field, pr, rng, smoke, t0):
    rare = RARE[field]
    rec = census_rares(us, excl, field, rare)
    rec["role"] = "primary"
    n, nA, nB, A = rec["n"], rec["n_rare_A"], rec["n_rare_B"], rec["observed_A"]
    rec["expected_hypergeometric"] = (nA * nB / n) if n else None

    if is_degenerate(n, nA, nB):
        rec["verdict"] = "DEGENERATE"
        rec["p"] = None
        rec["note"] = ("either side has 0 rares or is all-rare on the n units; "
                       "A is fixed by the margins and N1 has max = min")
        return rec

    R = 200 if smoke else 10000
    NCAL = 50 if smoke else 1000
    NPOW = 10 if smoke else 200
    RP = 200 if smoke else 2000
    NCURVE = 10 if smoke else 100

    # copy-all: B_rare := A_rare; A must equal n_rare_A and p < α
    cp = copy_all_units(us, rare)
    Mc = rare_match_matrix(cp, rare)
    obs_c = int(np.trace(Mc))
    pc = pval(obs_c, null_bank(Mc, RP, np.random.default_rng(SEEDS["power"] + 100)))
    rec["positive_control_copy_all"] = dict(
        A=obs_c, expected=nA, p=pc, passed=bool(obs_c == nA and pc < ALPHA))

    M = rare_match_matrix(us, rare)
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
    pw, pmed, kpl = plant_rare_power(us, F_PLANT, NPOW, RP, rng["power"], ALPHA, rare)
    curve = {}
    for f in F_CURVE:
        if time.time() - t0 > WALL * 0.8:
            curve[str(f)] = "cut_by_wall"
            continue
        curve[str(f)] = plant_rare_power(us, f, NCURVE, RP, rng["power"], ALPHA, rare)[0]
    assert A == int(np.trace(M))
    p = pval(A, bank)
    blocks = [[i for i, u in enumerate(us) if u["group_pair"] == g] for g in range(len(pr))]
    blocks = [b for b in blocks if b]
    bank_n2 = null_bank(M, R, rng["n2"], blocks=blocks) if blocks else bank
    rec.update(null_mean=float(bank.mean()), null_sd=float(bank.std()),
               null_q95=float(np.quantile(bank, 0.95)), null_max=int(bank.max()),
               null_min=int(bank.min()), p=p,
               calibration=dict(fpr_perm=fpr_perm, n=NCAL, shift_offsets=len(shifts),
                                min_offset=lo, fpr_shift=fpr_shift,
                                shift_p_min=min(sp) if sp else None),
               power=dict(f=F_PLANT, k_planted=kpl, power=pw, median_p=pmed, n=NPOW,
                          curve=curve, curve_n=NCURVE,
                          note="50% sharing plant of A's rare marks; curve is descriptive"),
               N2_within_group=dict(null_mean=float(bank_n2.mean()), p=pval(A, bank_n2),
                                    note="descriptive, not a verdict"))

    copy_fail = not rec["positive_control_copy_all"]["passed"]
    fpr_fail = fpr_perm > FPR_GATE or (fpr_shift is not None and fpr_shift > FPR_GATE)
    if copy_fail or fpr_fail:
        v = "TOOL EXCLUDED"
    elif n < 10 or (nA + nB) < 2 or (pw is not None and pw < POWER_BAR):
        v = "NOT TESTABLE"
    elif p < ALPHA:
        v = "SUPPORTED"
    else:
        v = "NOT SUPPORTED"
    rec["verdict"] = v
    rec["matching_units"] = [dict(gA=u["gA"], gB=u["gB"], posA=u["posA"], posB=u["posB"],
                                  value=u["value"], featA=str(u["featA"]), featB=str(u["featB"]))
                             for u in us if is_dual_rare(u["featA"], u["featB"], rare)]
    return rec


def sensitivity_block(us, excl, field, rare, rng, smoke):
    rec = census_rares(us, excl, field, rare)
    rec["note"] = "disclosed, not a verdict"
    n, nA, nB, A = rec["n"], rec["n_rare_A"], rec["n_rare_B"], rec["observed_A"]
    if is_degenerate(n, nA, nB) or n < 2:
        rec["p"] = None
        return rec
    M = rare_match_matrix(us, rare)
    R = 200 if smoke else 10000
    rec["p"] = pval(A, null_bank(M, R, rng["sens"]))
    rec["null_mean"] = float((nA * nB / n) if n else 0)
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
    out = dict(cycle="K048", db=f"OKR khipu.db @ 4039ca5 sha256 {h}", smoke=smoke,
               alpha=ALPHA, fpr_gate=FPR_GATE, power_bar=POWER_BAR, f_plant=F_PLANT,
               seeds=SEEDS, primary_fields=list(PRIMARY), rare_labels=dict(RARE),
               fixture_passed=ok, fixture=fx, pairs={})
    built = {}
    for a, b in k046.PAIRS:
        key = f"{a}/{b}"
        pr, Vs, units, leaders = k046.build_units(S, a, b)
        if (len(pr), sum(Vs)) != k046.K019[key]:
            sys.exit(f"EXCLUDED: K019 drift on {key}: {(len(pr), sum(Vs))} != {k046.K019[key]}")
        # traceback length == V is asserted inside k046.build_units (assert len(al) == V)
        built[key] = (pr, Vs, units, leaders)
    print("K019 consistency ok", {k: (len(v[0]), sum(v[1])) for k, v in built.items()}, flush=True)

    for key, (pr, Vs, units, leaders) in built.items():
        P = out["pairs"].setdefault(key, {})
        P.update(matched_groups=len(pr), V=Vs, V_tot=sum(Vs),
                 aligned_nonleader_units=len(units))
        t1 = time.time()
        P["primary"] = {}
        for field in PRIMARY:
            us, excl = attach(cord, knots, units, field)
            rec = evaluate(us, excl, field, pr, rng, smoke, t0)
            P["primary"][field] = rec
            print(f"{key} {field} n={rec.get('n')} nA={rec.get('n_rare_A')} "
                  f"nB={rec.get('n_rare_B')} A={rec.get('observed_A')} "
                  f"p={rec.get('p')} -> {rec.get('verdict')} ({time.time()-t1:.1f}s)",
                  flush=True)
        sens = {}
        for field in PRIMARY:
            rare = RARE[field]
            usL, exclL = attach(cord, knots, units + leaders, field)
            sens[f"{field}_with_leaders"] = sensitivity_block(
                usL, exclL, field, rare, rng, smoke)
            unz_src = [u for u in units if u["value"] != 0]
            usz, exclz = attach(cord, knots, unz_src, field)
            sens[f"{field}_nonzero_value_units"] = sensitivity_block(
                usz, exclz, field, rare, rng, smoke)
        P["sensitivities"] = sens
        print(f"{key} done ({time.time()-t1:.1f}s)", flush=True)
        os.makedirs(AN, exist_ok=True)
        json.dump(out, open(os.path.join(AN, "k048_checkpoint.json"), "w"), indent=1, default=list)

    out["sec"] = round(time.time() - t0, 1)
    fn = "k048_smoke.json" if smoke else "k048_results.json"
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
