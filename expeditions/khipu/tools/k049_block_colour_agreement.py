#!/usr/bin/env python3
"""K049 - cross-khipu colour agreement on the five K010 value-block pairs (README lines 3 and 6).
Pre-registered in case-file/K049-block-colour-agreement.md (prereg pushed before any pair-colour number).

Units: aligned positions of each published K010 significant_S value block, both sides coloured.
Statistic A = number of units whose colours match (primary rule, imported from K046).
Null N1: permute side B's colour tuples among the pair's units (within-khipu; keeps both sides'
colour frequencies on the analysed units; never uses the other khipu's colours).

Usage (from expeditions/khipu/):
  python3 tools/k049_block_colour_agreement.py fixture   # match-function fixture only (no data)
  python3 tools/k049_block_colour_agreement.py values    # consistency gate only (no colour)
  python3 tools/k049_block_colour_agreement.py run [--smoke]  # full run -> analysis/k049_results.json
Seeds: N1 4949, calibration 4950, power 4951, N2/sensitivities 4952, copy-all 4953.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04.
"""
import hashlib, importlib.util, json, math, os, sqlite3, sys, time
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.join(HERE, "..", "analysis")
DB_CANDIDATES = [os.path.join(HERE, "..", "khipu.db"), os.path.join(HERE, "..", "data", "khipu.db")]
SHA = "607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db"
ALPHA = 0.05 / 5            # Bonferroni x5 over the named pairs
FPR_GATE = 0.08             # expedition bar (K034/K037/K040-K042 / K046)
POWER_BAR = 0.5
F_PLANT = 0.25
F_CURVE = (0.10, 0.15, 0.25, 0.40)
SEEDS = dict(null=4949, calib=4950, power=4951, n2_sens=4952, copyall=4953)
WALL = 540.0

# Published K010 significant_S pairs (values only; KH0277·KH0449 artefact excluded)
PAIRS = (
    dict(key="KH0362/KH0049", a="KH0362", b="KH0049",
         a_inv="UR122", b_inv="AS038/HP036",
         block_len=12,
         block=[1856, 2578, 89, 974, 1146, 1095, 849, 790, 6485, 875, 1348, 754]),
    dict(key="KH0128/KH0137", a="KH0128", b="KH0137",
         a_inv="UR1114", b_inv="UR1123",
         block_len=10,
         block=[40, 9, 57, 30, 56, 80, 21, 8, 22, 12]),
    dict(key="KH0140/KH0483", a="KH0140", b="KH0483",
         a_inv="AS125", b_inv="UR247",
         block_len=12,
         block=[1517, 2373, 6291, 3495, 4213, 6323, 4122, 2220, 4377, 1292, 1162, 2393]),
    dict(key="KH0304/KH0303", a="KH0304", b="KH0303",
         a_inv="UR067", b_inv="UR066",
         block_len=7,
         block=[22, 3, 9, 2, 156, 13, 12]),
    dict(key="KH0305/KH0301", a="KH0305", b="KH0301",
         a_inv="UR068", b_inv="UR064",
         block_len=8,
         block=[8, 1, 3, 1, 57, 5, 6, 2]),
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


def run_fixture():
    """Reuse K046's 14 cases exactly so the match function cannot drift."""
    return K046.run_fixture()


# ------------------------------------------------------------------ K010 sequences (values; no colour)
def build_sequences(c):
    dups = {r[0] for r in c.execute("select KHIPU_ID from khipu_main where DUPLICATE_FLAG=1")}
    meta = {}
    for r in c.execute(
        "select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM, MUSEUM_NAME, MUSEUM_NUM, "
        "PROVENANCE, REGION, orig_inv_num from khipu_main"
    ):
        meta[r[0]] = dict(
            okr=r[1] or "", inv=r[2] or "", museum=(r[3] or "").strip().strip('"'),
            mnum=(r[4] or "").strip(), provenance=r[5] or "", region=r[6] or "",
            orig_inv=r[7] or "",
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

    seq = defaultdict(list)
    for khid, cid, cl, cord_ord in c.execute(
        "select KHIPU_ID, CORD_ID, CLUSTER_ID, CORD_ORDINAL from cord "
        "where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"
    ):
        if khid in dups:
            continue
        v = 0 if cid in R5 else val.get(cid, 0)
        seq[khid].append(dict(cid=cid, value=int(v), cluster=cl, ordinal=cord_ord))
    byokr = {meta[k]["okr"]: k for k in seq}
    return dict(seq=seq, meta=meta, byokr=byokr, n_R5=len(R5), n_dups=len(dups))


def find_block(values, block):
    L = len(block)
    return [i for i in range(len(values) - L + 1) if values[i:i + L] == block]


def locate_side(S, okr, block, block_len):
    if okr not in S["byokr"]:
        return dict(ok=False, okr=okr, reason=f"OKR {okr} not in sequences")
    khid = S["byokr"][okr]
    items = S["seq"][khid]
    vals = [it["value"] for it in items]
    hits = find_block(vals, block)
    if not hits:
        return dict(ok=False, okr=okr, khid=khid, reason="block not found",
                    n_pendants=len(items), meta=S["meta"][khid])
    i = hits[0]  # leftmost (pre-registered tie-break)
    rec = items[i:i + block_len]
    rec_block = [x["value"] for x in rec]
    clusters = [x["cluster"] for x in rec]
    ok = rec_block == block and len(rec_block) == block_len
    return dict(
        ok=ok, okr=okr, khid=khid, start=i, n_hits=len(hits), hits=hits,
        block=rec_block, block_len=len(rec_block),
        clusters=clusters, n_clusters=len(set(clusters)),
        n_pendants=len(items), items=rec, meta=S["meta"][khid],
        reason=None if ok else "reconstructed block != published K010 array",
    )


def public_side(side):
    """Drop cord items (ids) from a values-only report."""
    skip = {"items"}
    return {k: v for k, v in side.items() if k not in skip}


def consistency_report(S):
    out, all_ok = {}, True
    for spec in PAIRS:
        A = locate_side(S, spec["a"], spec["block"], spec["block_len"])
        B = locate_side(S, spec["b"], spec["block"], spec["block_len"])
        ok = bool(A["ok"] and B["ok"])
        all_ok &= ok
        out[spec["key"]] = dict(
            ok=ok, a=public_side(A), b=public_side(B),
            published_block=spec["block"], published_block_len=spec["block_len"],
        )
    return all_ok, out


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


def build_units(A, B):
    units = []
    for ia, (ua, ub) in enumerate(zip(A["items"], B["items"])):
        units.append(dict(
            pos=ia, value=ua["value"],
            cidA=ua["cid"], cidB=ub["cid"],
            clusterA=ua["cluster"], clusterB=ub["cluster"],
            startA=A["start"] + ia, startB=B["start"] + ia,
        ))
    return units


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
    S = build_sequences(c)
    cons_ok, cons = consistency_report(S)
    out = dict(cycle="K049", db=f"OKR khipu.db @ 4039ca5 sha256 {h}",
               fixture_passed=ok, consistency_ok=cons_ok, n_R5=S["n_R5"],
               pairs=cons)
    print(json.dumps(out, indent=1, default=list))
    sys.exit(0 if cons_ok else 1)


def main(smoke=False):
    t0 = time.time()
    ok, fx = run_fixture()
    if not ok:
        print(json.dumps(fx, indent=1))
        sys.exit("REFUSED: match-function fixture failed; no results written")
    c, h = open_db()
    S = build_sequences(c)
    print(f"loaded sequences {time.time() - t0:.1f}s R5={S['n_R5']}", flush=True)

    # --- consistency gate (values only) before any colour is touched
    built = {}
    cons = {}
    for spec in PAIRS:
        A = locate_side(S, spec["a"], spec["block"], spec["block_len"])
        B = locate_side(S, spec["b"], spec["block"], spec["block_len"])
        cons[spec["key"]] = dict(ok=bool(A["ok"] and B["ok"]),
                                 a=public_side(A), b=public_side(B))
        if not (A["ok"] and B["ok"]):
            sys.exit(f"EXCLUDED: K010 drift on {spec['key']}: A={public_side(A)} B={public_side(B)}")
        built[spec["key"]] = (spec, A, B, build_units(A, B))
    print("K010 consistency ok", {k: (v[1]["start"], v[2]["start"], v[1]["block_len"])
                                  for k, v in built.items()}, flush=True)

    # Colour is read only after every named pair has passed the values gate
    colour = load_colour(c)

    R = 200 if smoke else 10000
    NCAL = 50 if smoke else 1000
    NPOW = 10 if smoke else 200
    RP = 200 if smoke else 2000
    NCURVE = 10 if smoke else 100
    rng = {k: np.random.default_rng(v) for k, v in SEEDS.items()}
    out = dict(
        cycle="K049", db=f"OKR khipu.db @ 4039ca5 sha256 {h}", smoke=smoke,
        alpha=ALPHA, fpr_gate=FPR_GATE, power_bar=POWER_BAR, f_plant=F_PLANT,
        seeds=SEEDS, R=R, n_calibration=NCAL, n_power=NPOW, R_power=RP,
        fixture_passed=ok, fixture=fx, consistency_ok=True, consistency=cons,
        n_R5=S["n_R5"], pairs={},
    )

    for key, (spec, A, B, units) in built.items():
        P = out["pairs"].setdefault(key, {})
        P["a"] = public_side(A)
        P["b"] = public_side(B)
        P["published_block"] = spec["block"]
        P["published_block_len"] = spec["block_len"]
        P["census"] = dict(a=dict(A["meta"]), b=dict(B["meta"]))
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
            print(f"{key} n={n} A={obs} DEGENERATE ({deg})", flush=True)
            json.dump(out, open(os.path.join(AN, "k049_checkpoint.json"), "w"), indent=1, default=list)
            continue

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
                      note="block is a single (clusterA, clusterB) key; N2 identical to N1")
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
                n=len(unz), A=obs, p=p, note="identical to primary (published block has no zeros)")
        P["sensitivities"] = sens
        P["matching_units"] = [
            dict(pos=u["pos"], value=u["value"],
                 startA=u["startA"], startB=u["startB"],
                 colour=colour_pretty(u["colA"]))
            for u in us if colour_match(u["colA"], u["colB"])
        ]
        print(f"{key} A={obs}/{n} null_mean={bank.mean():.2f} p={p:.5f} -> {v} "
              f"({time.time() - t1:.1f}s)", flush=True)
        json.dump(out, open(os.path.join(AN, "k049_checkpoint.json"), "w"), indent=1, default=list)

    out["sec"] = round(time.time() - t0, 1)
    fn = "k049_smoke.json" if smoke else "k049_results.json"
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
