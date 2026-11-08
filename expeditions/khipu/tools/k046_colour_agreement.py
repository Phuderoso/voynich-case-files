#!/usr/bin/env python3
"""K046 - cross-khipu colour agreement on the three K019 pairs (README line 6).
Pre-registered in case-file/K046-colour-agreement.md (prereg pushed before any pair-colour number).

Units: non-leader cords of K018/K019 matched groups, aligned by the exact value LCS (traceback),
both sides coloured. Statistic A = number of units whose colours match (primary rule).
Null N1: permute side B's colour tuples among the pair's units (within-khipu; keeps both sides'
colour frequencies on the analysed units; never uses the other khipu's colours).

Usage (from expeditions/khipu/):
  python3 tools/k046_colour_agreement.py fixture      # match-function fixture only (no data)
  python3 tools/k046_colour_agreement.py run [--smoke]  # full run -> analysis/k046_results.json
Seeds: N1 4646, calibration 4647, power 4648, N2 (within-group, descriptive) 4649, sensitivities 4650.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04.
"""
import hashlib, json, math, os, sqlite3, sys, time
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.join(HERE, "..", "analysis")
DB_CANDIDATES = [os.path.join(HERE, "..", "khipu.db"), os.path.join(HERE, "..", "data", "khipu.db")]
SHA = "607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db"
PAIRS = (("KH0097", "KH0586"), ("KH0192", "KH0470"), ("KH0192", "KH0469"))
# K019 published value results (consistency gate; values only, no colour field is read)
K019 = {"KH0097/KH0586": (13, 89), "KH0192/KH0470": (14, 37), "KH0192/KH0469": (15, 36)}
ALPHA = 0.05 / 3            # Bonferroni x3 over the named pairs
FPR_GATE = 0.08             # expedition bar (K034/K037/K040-K042)
POWER_BAR = 0.5             # readability bar (K040-K042)
F_PLANT = 0.25              # pre-registered copy rate for the power verdict
F_CURVE = (0.10, 0.15, 0.25, 0.40)  # descriptive power curve
SEEDS = dict(null=4646, calib=4647, power=4648, n2=4649, sens=4650)
WALL = 540.0


# ------------------------------------------------------------------ match function
def norm(x):
    return None if x is None else str(x).strip()


def colour_match(a, b, by_eq_yb=False):
    """a, b = (components tuple, operators tuple) in Ascher/OKR order; None = no usable colour.
    Primary: identical operator sequence ('-' is not ':'), identical ordered components,
    PK on either side never matches, BY != YB. Sensitivity by_eq_yb maps BY -> YB first."""
    if a is None or b is None:
        return False
    (ca, oa), (cb, ob) = a, b
    if "PK" in ca or "PK" in cb:
        return False
    if tuple(oa) != tuple(ob) or len(ca) != len(cb):
        return False
    if by_eq_yb:
        f = lambda t: tuple("YB" if x == "BY" else x for x in t)
        ca, cb = f(ca), f(cb)
    return tuple(ca) == tuple(cb)


def run_fixture():
    W = (("W",), ())
    cases = [
        ("identical plain", W, W, False, True),
        ("different plain", W, (("AB",), ()), False, False),
        ("PK both sides never matches", (("PK",), ()), (("PK",), ()), False, False),
        ("PK inside mottle never matches", (("PK", "W"), (":",)), (("PK", "W"), (":",)), False, False),
        ("barber pole '-' is not mottled ':'", (("AB", "W"), ("-",)), (("AB", "W"), (":",)), False, False),
        ("identical barber pole matches", (("AB", "W"), ("-",)), (("AB", "W"), ("-",)), False, True),
        ("identical mottled matches", (("MB", "W"), (":",)), (("MB", "W"), (":",)), False, True),
        ("identical three-part MB-MB:W matches", (("MB", "MB", "W"), ("-", ":")), (("MB", "MB", "W"), ("-", ":")), False, True),
        ("order matters (no re-sort)", (("AB", "W"), ("-",)), (("W", "AB"), ("-",)), False, False),
        ("BY != YB (primary)", (("BY",), ()), (("YB",), ()), False, False),
        ("BY == YB (sensitivity only)", (("BY",), ()), (("YB",), ()), True, True),
        ("BY:W == YB:W (sensitivity only)", (("BY", "W"), (":",)), (("YB", "W"), (":",)), True, True),
        ("no colour never matches", None, W, False, False),
        ("different length", (("AB", "W"), ("-",)), (("AB",), ()), False, False),
    ]
    out, ok = [], True
    for name, a, b, s, want in cases:
        got = colour_match(a, b, s)
        out.append({"case": name, "expected": want, "got": got})
        ok &= got == want
    return ok, out


# ------------------------------------------------------------------ K019 structures (copied)
def lcs_table(a, b):
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = D[i-1][j-1] + 1 if a[i-1] == b[j-1] else max(D[i-1][j], D[i][j-1])
    return D


def lcs_traceback(a, b):
    """Deterministic traceback (pre-registered): from (n, m), take the diagonal when a[i-1]==b[j-1]
    and D[i][j]==D[i-1][j-1]+1; else move up if D[i-1][j] >= D[i][j-1], else left."""
    D = lcs_table(a, b); i, j, pr = len(a), len(b), []
    while i and j:
        if a[i-1] == b[j-1] and D[i][j] == D[i-1][j-1] + 1:
            pr.append((i-1, j-1)); i -= 1; j -= 1
        elif D[i-1][j] >= D[i][j-1]:
            i -= 1
        else:
            j -= 1
    return pr[::-1], D[-1][-1]


def load(c):
    dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
    okr = {r[0]: r[1] for r in c.execute("select KHIPU_ID, OKR_NUM from khipu_main")}
    val = defaultdict(int)
    for cid, v in c.execute("select CORD_ID, knot_value_type from knot"):
        if v is not None: val[cid] += int(v)

    def place_(v):
        p = 0
        while v % 10 == 0: v //= 10; p += 1
        return p
    clpl = defaultdict(set); clcd = {}
    for cid_, cl_, t_, v_ in c.execute("select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"):
        t_ = (t_ or '').strip()
        if t_ in ('S', 'L', 'E') and v_: clpl[cl_].add(place_(int(v_)) if t_ == 'S' else 0)
        clcd[cl_] = cid_
    ordn_ = {r[0]: r[1] for r in c.execute("select CLUSTER_ID, ORDINAL from knot_cluster")}
    bc_ = defaultdict(dict)
    for cl_, pl_ in clpl.items():
        if len(pl_) == 1 and ordn_.get(cl_) is not None: bc_[clcd[cl_]][ordn_[cl_]] = next(iter(pl_))
    R5 = {cd for cd, d in bc_.items() if len(d) >= 2 and not all(
        a > b for a, b in zip([d[o] for o in sorted(d)], [d[o] for o in sorted(d)][1:]))}
    kh = defaultdict(list); grp = defaultdict(list); cid_of = defaultdict(list)
    for khid, cid, cl in c.execute("select KHIPU_ID, CORD_ID, CLUSTER_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
        if not cid_of[khid] or cid_of[khid][-1][0] != cl: cid_of[khid].append([cl, []])
        cid_of[khid][-1][1].append(cid)
        if khid in dups: continue
        v = 0 if cid in R5 else val.get(cid, 0); kh[khid].append(v)
        if not grp[khid] or grp[khid][-1][0] != cl: grp[khid].append([cl, []])
        grp[khid][-1][1].append(v)
    ids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]
    LD = {k: [g[1][0] for g in grp[k] if len(g[1]) >= 5 and g[1][0] > 0] for k in ids}
    lf = Counter(x for k in ids for x in LD[k]); lt = sum(lf.values())
    WL = {v: -math.log2(n / lt) for v, n in lf.items()}
    byokr = {okr[k]: k for k in ids}

    def lgroups(k):
        return [(g[1], cid_of[k][i][1]) for i, g in enumerate(grp[k]) if len(g[1]) >= 5 and g[1][0] > 0]

    def walign(a, b):
        n, m = len(a), len(b); D = [[0.0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                D[i][j] = max(D[i-1][j], D[i][j-1], D[i-1][j-1] + WL[a[i-1]] if a[i-1] == b[j-1] else -1)
        i, j, pr = n, m, []
        while i and j:
            if a[i-1] == b[j-1] and abs(D[i][j] - (D[i-1][j-1] + WL[a[i-1]])) < 1e-9: pr.append((i-1, j-1)); i -= 1; j -= 1
            elif D[i-1][j] >= D[i][j-1]: i -= 1
            else: j -= 1
        return pr[::-1]

    # Colour (K045/K021 field): row with smallest RANGE_BEG, ties smallest color_id; all rows.
    first = {}
    rows = c.execute("select color_id, CORD_ID, RANGE_BEG, FULL_COLOR, COLOR_CD_1, COLOR_CD_2, COLOR_CD_3, COLOR_CD_4, COLOR_CD_5, "
                     "OPERATOR_1, OPERATOR_2, OPERATOR_3, OPERATOR_4, OPERATOR_5 from ascher_cord_color").fetchall()
    for r in sorted(rows, key=lambda r: (r[1], r[2] if r[2] is not None else 1e18, r[0])):
        first.setdefault(r[1], r)

    def colour(cid):
        r = first.get(cid)
        if r is None: return None, "no_colour_row"
        if not norm(r[3]): return None, "empty_full_color"
        comps = tuple(norm(x) for x in r[4:9] if norm(x))
        ops = tuple(norm(x) for x in r[9:14] if norm(x))
        if not comps: return None, "no_components"
        return (comps, ops), "ok"
    return dict(byokr=byokr, lgroups=lgroups, walign=walign, colour=colour, okr=okr)


# ------------------------------------------------------------------ units
def build_units(S, a, b):
    GA, GB = S["lgroups"](S["byokr"][a]), S["lgroups"](S["byokr"][b])
    pr = S["walign"]([g[0][0] for g in GA], [g[0][0] for g in GB])
    units, leaders, Vs = [], [], []
    for gi, (i, j) in enumerate(pr):
        va, vb = GA[i][0][1:], GB[j][0][1:]
        ca, cb = GA[i][1][1:], GB[j][1][1:]
        al, V = lcs_traceback(va, vb); Vs.append(V)
        assert len(al) == V and all(va[x] == vb[y] for x, y in al)
        for x, y in al:
            units.append(dict(group_pair=gi, gA=i, gB=j, posA=x + 1, posB=y + 1, value=va[x], cidA=ca[x], cidB=cb[y]))
        leaders.append(dict(group_pair=gi, gA=i, gB=j, posA=0, posB=0, value=GA[i][0][0], cidA=GA[i][1][0], cidB=GB[j][1][0]))
    return pr, Vs, units, leaders


def colour_units(S, units):
    keep, excl = [], Counter()
    for u in units:
        ca, sa = S["colour"](u["cidA"]); cb, sb = S["colour"](u["cidB"])
        if ca is None or cb is None:
            excl[f"A:{sa}|B:{sb}"] += 1; continue
        keep.append({**u, "colA": ca, "colB": cb})
    return keep, excl


def match_matrix(us, by_eq_yb=False):
    n = len(us)
    M = np.zeros((n, n), dtype=np.int8)
    for i in range(n):
        for j in range(n):
            M[i, j] = colour_match(us[i]["colA"], us[j]["colB"], by_eq_yb)
    return M


def null_bank(M, R, rng, blocks=None, chunk=2000):
    """A under permutation of B's colours among units (blocks: permute only within each block)."""
    n = M.shape[0]; out = np.empty(R, dtype=np.int32); idx = np.arange(n)
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


def plant_power(us, f, Nrep, Rp, rng):
    """Base = random permutation of B's colours (no residual real signal); then on a random
    fraction f of units set B's colour := A's colour. p from a fresh N1 bank of the planted data."""
    n = len(us); hits = 0; ps = []
    colA = [u["colA"] for u in us]; colB = [u["colB"] for u in us]
    k = int(round(f * n))
    for _ in range(Nrep):
        perm = rng.permutation(n); B = [colB[p] for p in perm]
        for s in rng.choice(n, size=k, replace=False): B[s] = colA[s]
        uu = [{"colA": colA[i], "colB": B[i]} for i in range(n)]
        M = match_matrix(uu); obs = int(np.trace(M))
        p = pval(obs, null_bank(M, Rp, rng)); ps.append(p); hits += p < ALPHA
    return hits / Nrep, float(np.median(ps)), k


def main(smoke=False):
    t0 = time.time()
    ok, fx = run_fixture()
    if not ok:
        print(json.dumps(fx, indent=1)); sys.exit("REFUSED: match-function fixture failed; no results written")
    db = next((p for p in DB_CANDIDATES if os.path.exists(p)), None)
    if db is None: sys.exit("EXCLUDED: khipu.db not found")
    h = hashlib.sha256(open(db, "rb").read()).hexdigest()
    if h != SHA: sys.exit(f"EXCLUDED: khipu.db hash {h} != {SHA}")
    c = sqlite3.connect(f"file:{os.path.realpath(db)}?mode=ro", uri=True)
    S = load(c); print(f"loaded {time.time()-t0:.1f}s", flush=True)
    R = 200 if smoke else 10000; NCAL = 50 if smoke else 1000
    NPOW = 10 if smoke else 200; RP = 200 if smoke else 2000
    NCURVE = 10 if smoke else 100
    rng = {k: np.random.default_rng(v) for k, v in SEEDS.items()}
    out = dict(cycle="K046", db=f"OKR khipu.db @ 4039ca5 sha256 {h}", smoke=smoke, alpha=ALPHA, fpr_gate=FPR_GATE,
               power_bar=POWER_BAR, f_plant=F_PLANT, seeds=SEEDS, R=R, n_calibration=NCAL, n_power=NPOW, R_power=RP,
               fixture_passed=ok, fixture=fx, pairs={})
    # --- consistency gate (values only) before any colour is touched
    built = {}
    for a, b in PAIRS:
        key = f"{a}/{b}"; pr, Vs, units, leaders = build_units(S, a, b)
        if (len(pr), sum(Vs)) != K019[key]:
            sys.exit(f"EXCLUDED: K019 drift on {key}: {(len(pr), sum(Vs))} != {K019[key]}")
        built[key] = (pr, Vs, units, leaders)
    print("K019 consistency ok", {k: (len(v[0]), sum(v[1])) for k, v in built.items()}, flush=True)
    # --- positive control on real structure: copy all A colours onto B
    for key, (pr, Vs, units, leaders) in built.items():
        us, excl = colour_units(S, units)
        cp = [{**u, "colB": u["colA"]} for u in us]
        Mc = match_matrix(cp); obs_c = int(np.trace(Mc))
        want = sum("PK" not in u["colA"][0] for u in us)
        pc = pval(obs_c, null_bank(Mc, 2000, np.random.default_rng(SEEDS["power"] + 100)))
        out["pairs"].setdefault(key, {})["positive_control_copy_all"] = dict(A=obs_c, expected=want, p=pc,
                                                                           passed=bool(obs_c == want and pc < ALPHA))
        if not (obs_c == want and pc < ALPHA):
            out["pairs"][key]["positive_control_note"] = "copy-all control not recovered"
    print("positive controls", {k: v["positive_control_copy_all"] for k, v in out["pairs"].items()}, flush=True)
    for key, (pr, Vs, units, leaders) in built.items():
        P = out["pairs"][key]; t1 = time.time()
        us, excl = colour_units(S, units)
        n = len(us)
        P.update(matched_groups=len(pr), group_pairs=[list(x) for x in pr], V=Vs, V_tot=sum(Vs),
                 aligned_nonleader_units=len(units), coloured_units=n, excluded_units=dict(excl))
        # power and calibration first (do not depend on the real match count)
        M = match_matrix(us)
        bank = null_bank(M, R, rng["null"])
        cal = []
        for _ in range(NCAL):
            perm = rng["calib"].permutation(n); cal.append(pval(int(M[np.arange(n), perm].sum()), bank))
        fpr_perm = float(np.mean(np.array(cal) < ALPHA))
        lo = math.ceil(0.1 * n); shifts = [k for k in range(1, n) if min(k, n - k) >= lo]
        sp = [pval(int(M[np.arange(n), (np.arange(n) + k) % n].sum()), bank) for k in shifts]
        fpr_shift = float(np.mean(np.array(sp) < ALPHA)) if sp else None
        pw, pmed, kpl = plant_power(us, F_PLANT, NPOW, RP, rng["power"])
        curve = {}
        for f in F_CURVE:
            if time.time() - t0 > WALL * 0.8: curve[str(f)] = "cut_by_wall"; continue
            curve[str(f)] = plant_power(us, f, NCURVE, RP, rng["power"])[0]
        print(f"{key} n={n} fpr_perm={fpr_perm:.4f} fpr_shift={fpr_shift} power={pw:.3f} ({time.time()-t1:.1f}s)", flush=True)
        # real statistic
        obs = int(np.trace(M)); p = pval(obs, bank)
        bank_n2 = null_bank(M, R, rng["n2"], blocks=[[i for i, u in enumerate(us) if u["group_pair"] == g] for g in range(len(pr))])
        P.update(observed_A=obs, rate=obs / n if n else None, null_mean=float(bank.mean()), null_sd=float(bank.std()),
                 null_q95=float(np.quantile(bank, 0.95)), null_max=int(bank.max()), p=p,
                 calibration=dict(fpr_perm=fpr_perm, n=NCAL, shift_offsets=len(shifts), min_offset=lo, fpr_shift=fpr_shift,
                                  shift_p_min=min(sp) if sp else None),
                 power=dict(f=F_PLANT, k_planted=kpl, power=pw, median_p=pmed, n=NPOW, curve=curve, curve_n=NCURVE),
                 N2_within_group=dict(null_mean=float(bank_n2.mean()), p=pval(obs, bank_n2), note="descriptive, not a verdict"))
        if not P["positive_control_copy_all"]["passed"] or fpr_perm > FPR_GATE or (fpr_shift is not None and fpr_shift > FPR_GATE):
            v = "TOOL EXCLUDED"
        elif pw < POWER_BAR:
            v = "NOT TESTABLE"
        elif p < ALPHA:
            v = "SUPPORTED"
        else:
            v = "NOT SUPPORTED"
        P["verdict"] = v
        # sensitivities (disclosed, not verdicts)
        sens = {}
        Mby = match_matrix(us, True); ob = int(np.trace(Mby))
        sens["BY_eq_YB"] = dict(A=ob, p=pval(ob, null_bank(Mby, R, rng["sens"])))
        ul, _ = colour_units(S, units + leaders)
        Ml = match_matrix(ul); ol = int(np.trace(Ml))
        sens["with_leaders"] = dict(n=len(ul), A=ol, p=pval(ol, null_bank(Ml, R, rng["sens"])))
        unz = [u for u in us if u["value"] != 0]
        if unz:
            Mz = match_matrix(unz); oz = int(np.trace(Mz))
            sens["nonzero_value_units"] = dict(n=len(unz), A=oz, p=pval(oz, null_bank(Mz, R, rng["sens"])))
        P["sensitivities"] = sens
        P["colour_counts_A"] = dict(Counter(":".join(u["colA"][0]) + "|" + "".join(u["colA"][1]) for u in us).most_common())
        P["colour_counts_B"] = dict(Counter(":".join(u["colB"][0]) + "|" + "".join(u["colB"][1]) for u in us).most_common())
        P["matching_units"] = [dict(gA=u["gA"], gB=u["gB"], posA=u["posA"], posB=u["posB"], value=u["value"],
                                    colour="".join(x for t in zip(u["colA"][0], u["colA"][1] + ("",)) for x in t))
                               for u in us if colour_match(u["colA"], u["colB"])]
        print(f"{key} A={obs}/{n} null_mean={bank.mean():.2f} p={p:.5f} -> {v} ({time.time()-t1:.1f}s)", flush=True)
        json.dump(out, open(os.path.join(AN, "k046_checkpoint.json"), "w"), indent=1, default=list)
    out["sec"] = round(time.time() - t0, 1)
    fn = "k046_smoke.json" if smoke else "k046_results.json"
    json.dump(out, open(os.path.join(AN, fn), "w"), indent=1, default=list)
    print("wrote", fn, out["sec"], "s")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "fixture":
        ok, fx = run_fixture(); print(json.dumps(fx, indent=1)); sys.exit(0 if ok else 1)
    elif mode == "run":
        main(smoke="--smoke" in sys.argv)
    else:
        sys.exit(__doc__)
