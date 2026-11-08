#!/usr/bin/env python3
"""K050 - cross-khipu colour agreement on the K020 pair KH0502·KH0514 (README lines 3 and 6).
Pre-registered in case-file/K050-k020-colour-agreement.md (prereg pushed before any pair-colour number).

Alignment: K020's information-weighted leader LCS (groups ≥ 3, corpus-wide leader weights,
same −1 mismatch penalty and traceback as tools/k020_two_stage.py / k046 walign), then
K046's deterministic lcs_traceback on the non-leader value sequences of each matched group.
Leaders are not in the primary count.

Units: aligned non-leader cords of the 12 K020-matched groups, both sides coloured.
Statistic A = number of units whose colours match (primary rule, imported from K046).
Null N1: permute side B's colour tuples among the pair's units (within-khipu; keeps both sides'
colour frequencies on the analysed units; never uses the other khipu's colours).

Usage (from expeditions/khipu/):
  python3 tools/k050_k020_colour_agreement.py fixture   # match-function fixture only (no data)
  python3 tools/k050_k020_colour_agreement.py values    # consistency gate only (no colour)
  python3 tools/k050_k020_colour_agreement.py run [--smoke]  # full run -> analysis/k050_results.json
Seeds: N1 5050, calibration 5051, power 5052, N2/sensitivities 5053, copy-all 5054.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04.
"""
import hashlib, importlib.util, json, math, os, sqlite3, sys, time
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.join(HERE, "..", "analysis")
DB_CANDIDATES = [os.path.join(HERE, "..", "khipu.db"), os.path.join(HERE, "..", "data", "khipu.db")]
SHA = "607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db"
ALPHA = 0.05                 # one named pair; no Bonferroni
FPR_GATE = 0.08              # expedition bar (K034/K037/K040-K042 / K046/K049)
POWER_BAR = 0.5
F_PLANT = 0.25
F_CURVE = (0.10, 0.15, 0.25, 0.40)
SEEDS = dict(null=5050, calib=5051, power=5052, n2_sens=5053, copyall=5054)
WALL = 540.0
MIN_GROUP = 3                # K020, not K046/K019's ≥ 5

# Single K020-confirmed pair (values only; KH0491·KH0503 failed stage 2 and is out of scope)
PAIR = dict(
    key="KH0502/KH0514", a="KH0502", b="KH0514",
    a_inv="UR266", b_inv="UR275",
    published_matched_groups=12, published_V=13,
    published_W=123.4,  # descriptive check only, not a hard gate
)


def load_k046():
    spec = importlib.util.spec_from_file_location(
        "k046", os.path.join(HERE, "k046_colour_agreement.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


K046 = load_k046()
colour_match = K046.colour_match
match_matrix = K046.match_matrix
null_bank = K046.null_bank
pval = K046.pval
norm = K046.norm
lcs_traceback = K046.lcs_traceback


def run_fixture():
    """Reuse K046's 14 cases exactly so the match function cannot drift."""
    return K046.run_fixture()


# ------------------------------------------------------------------ K020 structures (values; no colour)
def walign(a, b, WL):
    """Information-weighted LCS with −1 mismatch, same DP and traceback as
    tools/k020_two_stage.py and tools/k046_colour_agreement.py walign.
    Returns (pairs, score). Score is descriptive (K020 published W = 123.4)."""
    n, m = len(a), len(b)
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = max(
                D[i - 1][j], D[i][j - 1],
                D[i - 1][j - 1] + WL[a[i - 1]] if a[i - 1] == b[j - 1] else -1,
            )
    i, j, pr = n, m, []
    while i and j:
        if a[i - 1] == b[j - 1] and abs(D[i][j] - (D[i - 1][j - 1] + WL[a[i - 1]])) < 1e-9:
            pr.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif D[i - 1][j] >= D[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return pr[::-1], D[n][m]


def load_structures(c):
    """Rebuild K020's groups (≥ 3, positive leader) and corpus-wide leader weights.
    Weights come from allW / full-corpus leaders (ids with ≥ 10 positive pendants),
    never from this pair alone."""
    dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
    meta = {}
    for r in c.execute(
        "select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM, MUSEUM_NAME, MUSEUM_NUM, "
        "PROVENANCE, REGION, orig_inv_num from khipu_main"
    ):
        meta[r[0]] = dict(
            okr=r[1] or "", inv=r[2] or "",
            museum=(r[3] or "").strip().strip('"'),
            mnum=(r[4] or "").strip(), provenance=r[5] or "",
            region=r[6] or "", orig_inv=r[7] or "",
        )
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
    for cid_, cl_, t_, v_ in c.execute(
        "select CORD_ID, CLUSTER_ID, TYPE_CODE, knot_value_type from knot"
    ):
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
    grp = defaultdict(list)
    cid_of = defaultdict(list)
    for khid, cid, cl in c.execute(
        "select KHIPU_ID, CORD_ID, CLUSTER_ID from cord "
        "where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"
    ):
        if not cid_of[khid] or cid_of[khid][-1][0] != cl:
            cid_of[khid].append([cl, []])
        cid_of[khid][-1][1].append(cid)
        if khid in dups:
            continue
        v = 0 if cid in R5 else val.get(cid, 0)
        kh[khid].append(v)
        if not grp[khid] or grp[khid][-1][0] != cl:
            grp[khid].append([cl, []])
        grp[khid][-1][1].append(v)

    ids = [k for k, v in kh.items() if sum(x > 0 for x in v) >= 10]
    LD = {k: [g[1][0] for g in grp[k] if len(g[1]) >= MIN_GROUP and g[1][0] > 0] for k in ids}
    lf = Counter(x for k in ids for x in LD[k])
    lt = sum(lf.values())
    WL = {v: -math.log2(n / lt) for v, n in lf.items()}
    byokr = {meta[k]["okr"]: k for k in ids}

    def lgroups(k):
        out = []
        for i, g in enumerate(grp[k]):
            if len(g[1]) >= MIN_GROUP and g[1][0] > 0:
                out.append(dict(values=g[1], cids=cid_of[k][i][1], cluster=g[0]))
        return out

    return dict(
        byokr=byokr, lgroups=lgroups, WL=WL, meta=meta,
        n_leaders=lt, n_distinct_leaders=len(lf), n_ids=len(ids),
        n_R5=len(R5), n_dups=len(dups),
    )


def build_alignment(S, a, b):
    """Values-only K020 alignment of one pair. Does not read colour."""
    if a not in S["byokr"]:
        return dict(ok=False, reason=f"OKR {a} not in sequences")
    if b not in S["byokr"]:
        return dict(ok=False, reason=f"OKR {b} not in sequences")
    ka, kb = S["byokr"][a], S["byokr"][b]
    GA, GB = S["lgroups"](ka), S["lgroups"](kb)
    LA = [g["values"][0] for g in GA]
    LB = [g["values"][0] for g in GB]
    pr, W = walign(LA, LB, S["WL"])
    units, leaders, Vs = [], [], []
    for gi, (i, j) in enumerate(pr):
        va, vb = GA[i]["values"][1:], GB[j]["values"][1:]
        ca, cb = GA[i]["cids"][1:], GB[j]["cids"][1:]
        al, V = lcs_traceback(va, vb)
        if not (len(al) == V and all(va[x] == vb[y] for x, y in al)):
            return dict(ok=False, reason=f"traceback length != V in group pair {(i, j)}")
        Vs.append(int(V))
        for x, y in al:
            units.append(dict(
                group_pair=gi, gA=int(i), gB=int(j),
                posA=x + 1, posB=y + 1, value=int(va[x]),
                cidA=ca[x], cidB=cb[y],
                clusterA=GA[i]["cluster"], clusterB=GB[j]["cluster"],
            ))
        leaders.append(dict(
            group_pair=gi, gA=int(i), gB=int(j),
            posA=0, posB=0, value=int(GA[i]["values"][0]),
            cidA=GA[i]["cids"][0], cidB=GB[j]["cids"][0],
            clusterA=GA[i]["cluster"], clusterB=GB[j]["cluster"],
        ))
    V_tot = int(sum(Vs))
    n_matched = len(pr)
    ok = (n_matched == PAIR["published_matched_groups"] and V_tot == PAIR["published_V"])
    reason = None if ok else (
        f"K020 drift: matched_groups={n_matched} V={V_tot} "
        f"!= published {PAIR['published_matched_groups']}/{PAIR['published_V']}"
    )
    return dict(
        ok=ok, reason=reason,
        matched_groups=n_matched, V=V_tot, Vs=Vs, W=float(W),
        group_pairs=[list(x) for x in pr],
        matched_leaders=[int(LA[i]) for i, j in pr],
        n_leader_groups_A=len(GA), n_leader_groups_B=len(GB),
        n_aligned_nonleader_units=len(units),
        n_zero_value_units=sum(1 for u in units if u["value"] == 0),
        units=units, leaders=leaders,
        meta_a=dict(S["meta"][ka]), meta_b=dict(S["meta"][kb]),
    )


def public_alignment(al):
    """Drop cord ids from a values-only report."""
    skip = {"units", "leaders"}
    return {k: v for k, v in al.items() if k not in skip}


# ------------------------------------------------------------------ colour (loaded only after consistency)
def load_colour(c):
    first = {}
    rows = c.execute(
        "select color_id, CORD_ID, RANGE_BEG, FULL_COLOR, COLOR_CD_1, COLOR_CD_2, "
        "COLOR_CD_3, COLOR_CD_4, COLOR_CD_5, OPERATOR_1, OPERATOR_2, OPERATOR_3, "
        "OPERATOR_4, OPERATOR_5 from ascher_cord_color"
    ).fetchall()
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


def colour_units(colour, units):
    keep, excl = [], Counter()
    for u in units:
        ca, sa = colour(u["cidA"])
        cb, sb = colour(u["cidB"])
        if ca is None or cb is None:
            excl[f"A:{sa}|B:{sb}"] += 1
            continue
        keep.append({**u, "colA": ca, "colB": cb})
    return keep, excl


def colkey(col):
    return ":".join(col[0]) + "|" + "".join(col[1])


def colour_pretty(col):
    comps, ops = col
    return "".join(x for t in zip(comps, ops + ("",)) for x in t)


def degeneracy_reason(us):
    """No colour variation that a shuffle of B could turn into extra matches."""
    if not us:
        return "no_coloured_units"
    setA = set(u["colA"] for u in us)
    setB = set(u["colB"] for u in us)
    any_match = any(colour_match(a, b) for a in setA for b in setB)
    if not any_match:
        return "no_shared_matching_colour"
    if len(setA) < 2:
        return "A_monochromatic"
    if len(setB) < 2:
        return "B_monochromatic"
    return None


def n2_blocks(us):
    keys = [(u["clusterA"], u["clusterB"]) for u in us]
    uniq = []
    for k in keys:
        if k not in uniq:
            uniq.append(k)
    if len(uniq) <= 1:
        return None, uniq
    blocks = [[i for i, k in enumerate(keys) if k == uk] for uk in uniq]
    return blocks, uniq


def plant_power(us, f, Nrep, Rp, rng):
    """Base = random permutation of B's colours; then copy A onto a random fraction f of units."""
    n = len(us)
    hits = 0
    ps = []
    colA = [u["colA"] for u in us]
    colB = [u["colB"] for u in us]
    k = int(round(f * n))
    for _ in range(Nrep):
        perm = rng.permutation(n)
        B = [colB[p] for p in perm]
        if k > 0 and n > 0:
            for s in rng.choice(n, size=min(k, n), replace=False):
                B[int(s)] = colA[int(s)]
        uu = [{"colA": colA[i], "colB": B[i]} for i in range(n)]
        M = match_matrix(uu)
        obs = int(np.trace(M))
        p = pval(obs, null_bank(M, Rp, rng))
        ps.append(p)
        hits += p < ALPHA
    return hits / Nrep if Nrep else None, (float(np.median(ps)) if ps else None), k


def open_db():
    db = next((p for p in DB_CANDIDATES if os.path.exists(p)), None)
    if db is None:
        sys.exit("EXCLUDED: khipu.db not found")
    h = hashlib.sha256(open(db, "rb").read()).hexdigest()
    if h != SHA:
        sys.exit(f"EXCLUDED: khipu.db hash {h} != {SHA}")
    c = sqlite3.connect(f"file:{os.path.realpath(db)}?mode=ro", uri=True)
    return c, h


def values_only():
    ok, fx = run_fixture()
    if not ok:
        print(json.dumps(fx, indent=1))
        sys.exit("REFUSED: match-function fixture failed")
    c, h = open_db()
    S = load_structures(c)
    al = build_alignment(S, PAIR["a"], PAIR["b"])
    out = dict(
        cycle="K050", db=f"OKR khipu.db @ 4039ca5 sha256 {h}",
        fixture_passed=ok, consistency_ok=bool(al["ok"]),
        n_R5=S["n_R5"], n_leaders=S["n_leaders"],
        n_distinct_leaders=S["n_distinct_leaders"], n_ids=S["n_ids"],
        pair=public_alignment(al),
        published=dict(matched_groups=PAIR["published_matched_groups"],
                       V=PAIR["published_V"], W=PAIR["published_W"]),
    )
    print(json.dumps(out, indent=1, default=list))
    sys.exit(0 if al["ok"] else 1)


def main(smoke=False):
    t0 = time.time()
    ok, fx = run_fixture()
    if not ok:
        print(json.dumps(fx, indent=1))
        sys.exit("REFUSED: match-function fixture failed; no results written")
    c, h = open_db()
    S = load_structures(c)
    print(f"loaded structures {time.time() - t0:.1f}s R5={S['n_R5']} "
          f"leaders={S['n_leaders']} distinct={S['n_distinct_leaders']}", flush=True)

    # --- consistency gate (values only) before any colour is touched
    al = build_alignment(S, PAIR["a"], PAIR["b"])
    if not al["ok"]:
        sys.exit(f"EXCLUDED: {al['reason']}")
    print("K020 consistency ok",
          f"matched_groups={al['matched_groups']} V={al['V']} "
          f"W={al['W']:.1f} (published {PAIR['published_W']})", flush=True)

    # Colour is read only after the named pair has passed the values gate
    colour = load_colour(c)

    R = 200 if smoke else 10000
    NCAL = 50 if smoke else 1000
    NPOW = 10 if smoke else 200
    RP = 200 if smoke else 2000
    NCURVE = 10 if smoke else 100
    rng = {k: np.random.default_rng(v) for k, v in SEEDS.items()}
    key = PAIR["key"]
    out = dict(
        cycle="K050", db=f"OKR khipu.db @ 4039ca5 sha256 {h}", smoke=smoke,
        alpha=ALPHA, fpr_gate=FPR_GATE, power_bar=POWER_BAR, f_plant=F_PLANT,
        seeds=SEEDS, R=R, n_calibration=NCAL, n_power=NPOW, R_power=RP,
        fixture_passed=ok, fixture=fx, consistency_ok=True,
        consistency=public_alignment(al),
        n_R5=S["n_R5"], n_leaders=S["n_leaders"],
        n_distinct_leaders=S["n_distinct_leaders"], n_ids=S["n_ids"],
        pairs={},
    )

    P = out["pairs"].setdefault(key, {})
    P["alignment"] = public_alignment(al)
    P["census"] = dict(a=al["meta_a"], b=al["meta_b"])
    units = al["units"]
    us, excl = colour_units(colour, units)
    n = len(us)
    P.update(aligned_units=len(units), coloured_units=n, excluded_units=dict(excl))

    # copy-all on real structure (creates shared codes; independent of real inventories)
    if n >= 1:
        cp = [{**u, "colB": u["colA"]} for u in us]
        Mc = match_matrix(cp)
        obs_c = int(np.trace(Mc))
        want = sum("PK" not in u["colA"][0] for u in us)
        pc = pval(obs_c, null_bank(Mc, 2000, rng["copyall"]))
        P["positive_control_copy_all"] = dict(
            A=obs_c, expected=want, p=pc,
            passed=bool(obs_c == want and pc < ALPHA))
    else:
        P["positive_control_copy_all"] = dict(
            A=0, expected=0, p=None, passed=False, note="no coloured units")

    deg = degeneracy_reason(us)
    P["degeneracy_reason"] = deg
    P["colour_counts_A"] = dict(Counter(colkey(u["colA"]) for u in us).most_common())
    P["colour_counts_B"] = dict(Counter(colkey(u["colB"]) for u in us).most_common())

    if deg:
        obs = int(sum(colour_match(u["colA"], u["colB"]) for u in us)) if us else 0
        P.update(observed_A=obs, rate=(obs / n if n else None),
                 null_mean=obs if n else None, p=None,
                 verdict="DEGENERATE",
                 note=("no colour variation to shuffle toward extra matches "
                       f"({deg}); A is fixed by the inventories and N1 has max = min"))
        if us:
            P["matching_units"] = [
                dict(gA=u["gA"], gB=u["gB"], posA=u["posA"], posB=u["posB"],
                     value=u["value"], colour=colour_pretty(u["colA"]))
                for u in us if colour_match(u["colA"], u["colB"])
            ]
        print(f"{key} n={n} A={obs} DEGENERATE ({deg})", flush=True)
        json.dump(out, open(os.path.join(AN, "k050_checkpoint.json"), "w"), indent=1, default=list)
    else:
        t1 = time.time()
        M = match_matrix(us)
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
        pw, pmed, kpl = plant_power(us, F_PLANT, NPOW, RP, rng["power"])
        curve = {}
        for f in F_CURVE:
            if time.time() - t0 > WALL * 0.8:
                curve[str(f)] = "cut_by_wall"
                continue
            curve[str(f)] = plant_power(us, f, NCURVE, RP, rng["power"])[0]
        print(f"{key} n={n} fpr_perm={fpr_perm:.4f} fpr_shift={fpr_shift} "
              f"power={pw:.3f} ({time.time() - t1:.1f}s)", flush=True)

        obs = int(np.trace(M))
        p = pval(obs, bank)
        blocks, uniq = n2_blocks(us)
        if blocks is None:
            n2 = dict(applicable=False, n_keys=len(uniq),
                      note="units share a single (clusterA, clusterB) key; N2 identical to N1")
        else:
            bank_n2 = null_bank(M, R, rng["n2_sens"], blocks=blocks)
            n2 = dict(applicable=True, n_keys=len(uniq),
                      key_sizes=[len(b) for b in blocks],
                      null_mean=float(bank_n2.mean()), p=pval(obs, bank_n2),
                      note="descriptive, not a verdict")

        P.update(
            observed_A=obs, rate=obs / n if n else None,
            null_mean=float(bank.mean()), null_sd=float(bank.std()),
            null_q95=float(np.quantile(bank, 0.95)), null_max=int(bank.max()),
            null_min=int(bank.min()), p=p,
            calibration=dict(fpr_perm=fpr_perm, n=NCAL, shift_offsets=len(shifts),
                             min_offset=lo, fpr_shift=fpr_shift,
                             shift_p_min=(min(sp) if sp else None)),
            power=dict(f=F_PLANT, k_planted=kpl, power=pw, median_p=pmed,
                       n=NPOW, curve=curve, curve_n=NCURVE),
            N2_within_group=n2,
        )
        copy_ok = P["positive_control_copy_all"]["passed"]
        if (not copy_ok) or fpr_perm > FPR_GATE or (fpr_shift is not None and fpr_shift > FPR_GATE):
            v = "TOOL EXCLUDED"
        elif p < ALPHA:
            v = "SUPPORTED"
        elif pw < POWER_BAR:
            v = "NOT TESTABLE"
        else:
            v = "NOT SUPPORTED"
        P["verdict"] = v

        sens = {}
        Mby = match_matrix(us, True)
        ob = int(np.trace(Mby))
        sens["BY_eq_YB"] = dict(A=ob, p=pval(ob, null_bank(Mby, R, rng["n2_sens"])))
        unz = [u for u in us if u["value"] != 0]
        if unz and len(unz) != n:
            Mz = match_matrix(unz)
            oz = int(np.trace(Mz))
            sens["nonzero_value_units"] = dict(
                n=len(unz), A=oz, p=pval(oz, null_bank(Mz, R, rng["n2_sens"])))
        elif unz:
            sens["nonzero_value_units"] = dict(
                n=len(unz), A=obs, p=p, note="identical to primary (no zero-value units)")
        else:
            sens["nonzero_value_units"] = dict(n=0, A=0, p=None, note="no nonzero-value units")
        P["sensitivities"] = sens
        P["matching_units"] = [
            dict(gA=u["gA"], gB=u["gB"], posA=u["posA"], posB=u["posB"],
                 value=u["value"], colour=colour_pretty(u["colA"]))
            for u in us if colour_match(u["colA"], u["colB"])
        ]
        P["match_colour_counts"] = dict(Counter(
            colour_pretty(u["colA"]) for u in us if colour_match(u["colA"], u["colB"])
        ).most_common())
        print(f"{key} A={obs}/{n} null_mean={bank.mean():.2f} p={p:.5f} -> {v} "
              f"({time.time() - t1:.1f}s)", flush=True)
        json.dump(out, open(os.path.join(AN, "k050_checkpoint.json"), "w"), indent=1, default=list)

    out["sec"] = round(time.time() - t0, 1)
    fn = "k050_smoke.json" if smoke else "k050_results.json"
    json.dump(out, open(os.path.join(AN, fn), "w"), indent=1, default=list)
    print("wrote", fn, out["sec"], "s")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "fixture":
        ok, fx = run_fixture()
        print(json.dumps(fx, indent=1))
        sys.exit(0 if ok else 1)
    elif mode == "values":
        values_only()
    elif mode == "run":
        main(smoke="--smoke" in sys.argv)
    else:
        sys.exit(__doc__)
