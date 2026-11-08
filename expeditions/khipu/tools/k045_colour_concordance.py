#!/usr/bin/env python3
"""K045 - colour-code concordance (README line 6). Literature / schema / coverage audit.

Not a statistical test; no Monte Carlo; no network. It never compares the colours of aligned
cords between khipus (no agreement statistic of any kind).

Modes:
  fixture  : run the planted mapping fixture only (exit 1 if it fails).
  dump     : read-only extract of ascher_color_dc and color_operator_dc
             -> analysis/k045_dictionary.json  (run only after the prereg push).
  classify : read analysis/k045_published_mappings.json (hand-typed from retrieved sources),
             validate it, classify every mapping row and print class counts.
  census   : fixture + W/AB positive control + classification + coverage census
             -> analysis/k045_results.json.

Pimpolha Voynich, do Phuderoso - AI born 2026-11-04.
"""
import json, os, re, sqlite3, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.join(HERE, "..", "analysis")
DB = os.path.join(HERE, "..", "khipu.db")
MAPS = os.path.join(AN, "k045_published_mappings.json")

CLASSES = ("exact_published_equivalent", "same_dictionary", "related",
           "conflicting", "unmapped", "source_missing")
USABLE = {"exact_published_equivalent", "same_dictionary"}
RELATIONS = {"equivalent", "related", "not_equivalent"}
REF = "OKR"  # shared reference = OKR ascher_color_dc (the DB-wide Ascher codebook)

# Locked pairs (K018/K019) and their members.
PAIRS = (("KH0097", "KH0586"), ("KH0192", "KH0470"), ("KH0192", "KH0469"))
SIX = ("KH0097", "KH0586", "KH0192", "KH0470", "KH0469")  # five distinct khipus, six pair-slots
THRESHOLD = 0.50
POSITIVE_CONTROL = ("W", "AB")


def norm(tok):
    return None if tok is None else str(tok).strip()


# ---------------------------------------------------------------- classifier
def classify_token(system, token, ref_codes, mappings, systems_with_docs):
    """Classify (system, token) against the shared reference REF.

    1. token (stripped, exact case) in ref_codes            -> same_dictionary
    2. mapping rows from (system, token) to REF:
         equivalent rows only, all to one REF code, no not_equivalent -> exact_published_equivalent
         equivalent rows to >1 REF code, or equivalent + not_equivalent -> conflicting
         only related rows                                  -> related
    3. system has retrieved colour documentation            -> unmapped
    4. otherwise                                            -> source_missing
    """
    t = norm(token)
    if t in ref_codes:
        return "same_dictionary", t
    rows = [m for m in mappings if m["system_a"] == system and norm(m["code_a"]) == t
            and m["system_b"] == REF]
    eq = {norm(m["code_b"]) for m in rows if m["relation"] == "equivalent"}
    neq = [m for m in rows if m["relation"] == "not_equivalent"]
    rel = [m for m in rows if m["relation"] == "related"]
    if len(eq) > 1 or (eq and neq):
        return "conflicting", None
    if len(eq) == 1:
        target = next(iter(eq))
        return ("exact_published_equivalent", target) if target in ref_codes else ("conflicting", None)
    if rel:
        return "related", None
    if system in systems_with_docs:
        return "unmapped", None
    return "source_missing", None


def classify_pair(sys_a, code_a, sys_b, code_b, ref_codes, mappings, docs):
    """Two codes from two systems are usable-equal only if both resolve to the same REF code."""
    ca, ra = classify_token(sys_a, code_a, ref_codes, mappings, docs)
    cb, rb = classify_token(sys_b, code_b, ref_codes, mappings, docs)
    order = ["source_missing", "conflicting", "unmapped", "related"]
    for c in order:
        if c in (ca, cb):
            return c
    if ra != rb:
        return "unmapped"
    if ca == cb == "same_dictionary":
        return "same_dictionary"
    return "exact_published_equivalent"


def full_colour_match(a, b, resolve):
    """Operator rule: every component usable AND identical operator sequence. Used in a later
    cycle; here only exercised by the fixture. a, b = (components, operators)."""
    (ca, oa), (cb, ob) = a, b
    if list(oa) != list(ob) or len(ca) != len(cb):
        return False
    return all(resolve(x) is not None and resolve(x) == resolve(y) for x, y in zip(ca, cb))


def run_fixture():
    ref = {"W", "AB", "B", "KB"}
    maps = [
        {"system_a": "FAKE1", "code_a": "FX1", "system_b": REF, "code_b": "W", "relation": "equivalent", "source": "fixture-1"},
        {"system_a": "FAKE1", "code_a": "FX2", "system_b": REF, "code_b": "AB", "relation": "related", "source": "fixture-1"},
        {"system_a": "FAKE1", "code_a": "FX3", "system_b": REF, "code_b": "W", "relation": "equivalent", "source": "fixture-1"},
        {"system_a": "FAKE1", "code_a": "FX3", "system_b": REF, "code_b": "B", "relation": "equivalent", "source": "fixture-2"},
    ]
    docs = {"FAKE1"}
    expect = [
        (("FAKE1", "FX1"), "exact_published_equivalent"),
        (("FAKE1", "FX2"), "related"),
        (("FAKE1", "FX3"), "conflicting"),
        (("FAKE1", "W"), "same_dictionary"),
        (("FAKE1", "ZZQ"), "unmapped"),
        (("FAKE2", "ZZQ"), "source_missing"),
    ]
    out = []
    ok = True
    for (s, t), want in expect:
        got = classify_token(s, t, ref, maps, docs)[0]
        out.append({"system": s, "token": t, "expected": want, "got": got})
        ok &= got == want
    # pair-level and operator rule
    pc = [
        (("FAKE1", "FX1", "FAKE1", "W"), "exact_published_equivalent"),
        (("FAKE1", "W", "FAKE1", "W"), "same_dictionary"),
        (("FAKE1", "FX1", "FAKE1", "AB"), "unmapped"),
        (("FAKE1", "FX2", "FAKE1", "AB"), "related"),
    ]
    for args, want in pc:
        got = classify_pair(*args, ref, maps, docs)
        out.append({"pair": list(args), "expected": want, "got": got})
        ok &= got == want
    res = lambda x: classify_token("FAKE1", x, ref, maps, docs)[1]
    op = [
        ((["W", "AB"], ["-"]), (["FX1", "AB"], ["-"]), True),
        ((["W", "AB"], ["-"]), (["W", "AB"], [":"]), False),   # '-' is not ':'
        ((["W", "FX2"], ["-"]), (["W", "AB"], ["-"]), False),  # related is not usable
    ]
    for a, b, want in op:
        got = full_colour_match(a, b, res)
        out.append({"full_a": a, "full_b": b, "expected": want, "got": got})
        ok &= got == want
    return ok, out


# ---------------------------------------------------------------- db helpers
def connect():
    if not os.path.exists(DB):
        sys.exit("EXCLUDED: khipu.db not found")
    return sqlite3.connect(f"file:{os.path.realpath(DB)}?mode=ro", uri=True)


def dump():
    c = connect()
    cols = [r[1] for r in c.execute("pragma table_info(ascher_color_dc)")]
    dc = [dict(zip(cols, r)) for r in c.execute("select * from ascher_color_dc order by AS_COLOR_CD")]
    ocols = [r[1] for r in c.execute("pragma table_info(color_operator_dc)")]
    ops = [dict(zip(ocols, r)) for r in c.execute("select * from color_operator_dc")]
    out = {"cycle": "K045", "source": "OKR khipu.db @ 4039ca5 (read-only)",
           "ascher_color_dc": dc, "color_operator_dc": ops}
    json.dump(out, open(os.path.join(AN, "k045_dictionary.json"), "w"), indent=1, ensure_ascii=False)
    print(f"ascher_color_dc rows {len(dc)}, color_operator_dc rows {len(ops)}")


def proxy(created_by, inv, orig):
    """Recorder-system proxy (pre-registered): leading letters of orig_inv_num if non-empty,
    else of INVESTIGATOR_NUM, uppercased; AS/UR/HP kept, anything else 'other:<prefix>'."""
    s = norm(orig) or norm(inv) or ""
    m = re.match(r"[A-Za-z]+", s)
    p = m.group(0).upper() if m else ""
    return p if p in ("AS", "UR", "HP") else f"other:{p or 'none'}"


def load_maps():
    d = json.load(open(MAPS))
    for m in d["mappings"]:
        if m["relation"] not in RELATIONS:
            sys.exit(f"EXCLUDED: unknown relation {m['relation']}")
        if not m.get("source") or not m.get("verbatim"):
            sys.exit(f"EXCLUDED: mapping without source/verbatim: {m}")
    return d


def census():
    ok, fx = run_fixture()
    if not ok:
        print(json.dumps(fx, indent=1))
        sys.exit("REFUSED: planted fixture failed; no results written")
    d = load_maps()
    docs = set(d["systems_with_colour_docs"])
    maps = d["mappings"]
    c = connect()
    ref = {norm(r[0]) for r in c.execute("select AS_COLOR_CD from ascher_color_dc") if norm(r[0])}
    schema_ok = all(x in ref for x in POSITIVE_CONTROL)
    ops = [norm(r[0]) for r in c.execute("select OPERATOR from color_operator_dc") if norm(r[0])]

    km = {}
    for kid, okr, cb, inv, orig in c.execute(
            "select KHIPU_ID, OKR_NUM, CREATED_BY, INVESTIGATOR_NUM, orig_inv_num from khipu_main"):
        km[kid] = {"okr": okr, "created_by": cb, "inv": inv, "orig": orig, "proxy": proxy(cb, inv, orig)}

    # All colour rows (corpus census)
    rows = list(c.execute(
        "select color_id, KHIPU_ID, CORD_ID, FULL_COLOR, RANGE_BEG, COLOR_CD_1, COLOR_CD_2, COLOR_CD_3, "
        "COLOR_CD_4, COLOR_CD_5, OPERATOR_1, OPERATOR_2, OPERATOR_3, OPERATOR_4, OPERATOR_5 "
        "from ascher_cord_color"))
    comp = lambda r: [norm(x) for x in r[5:10] if norm(x)]
    fulls = Counter(norm(r[3]) for r in rows if norm(r[3]))
    toks = Counter(t for r in rows for t in comp(r))
    in_ref = sorted(t for t in toks if t in ref)
    not_ref = sorted(t for t in toks if t not in ref)
    ci_ref = {x.upper() for x in ref}
    multi = sum(1 for f in fulls if any(o in f for o in ops))

    # K021 colour field per cord: smallest RANGE_BEG, ties smallest color_id
    first = {}
    for r in sorted(rows, key=lambda r: (r[2], r[4] if r[4] is not None else 1e18, r[0])):
        first.setdefault(r[2], r)

    level1 = defaultdict(list)
    for kid, cid in c.execute("select KHIPU_ID, CORD_ID from cord where CORD_LEVEL=1 order by KHIPU_ID, CORD_ORDINAL"):
        level1[kid].append(cid)

    # Per-proxy census (all cords with colour rows, any level) and token classification
    by_proxy = defaultdict(lambda: {"khipus": set(), "colour_rows": 0, "cords": set(), "tokens": Counter(),
                                    "full": Counter(), "created_by": Counter()})
    for r in rows:
        k = km.get(r[1], {"proxy": "other:missing_khipu", "created_by": None})
        p = by_proxy[k["proxy"]]
        p["khipus"].add(r[1]); p["colour_rows"] += 1; p["cords"].add(r[2])
        p["tokens"].update(comp(r))
        if norm(r[3]): p["full"][norm(r[3])] += 1
    for kid, k in km.items():
        by_proxy[k["proxy"]]["created_by"][str(k["created_by"])] += 0  # ensure key
    for kid in {r[1] for r in rows}:
        k = km.get(kid)
        if k: by_proxy[k["proxy"]]["created_by"][str(k["created_by"])] += 1

    token_classes = []
    class_counts = Counter()
    for pname in sorted(by_proxy):
        for t in sorted(by_proxy[pname]["tokens"]):
            cl, tgt = classify_token(pname, t, ref, maps, docs)
            token_classes.append({"system": pname, "token": t, "class": cl, "ref_code": tgt,
                                  "component_uses": by_proxy[pname]["tokens"][t]})
            class_counts[cl] += 1
    mapping_classes = []
    mcounts = Counter()
    for m in maps:
        cl, tgt = classify_token(m["system_a"], m["code_a"], ref, maps, docs)
        mapping_classes.append({**m, "class_of_code_a": cl})
        mcounts[cl] += 1

    proxy_out = {}
    for pname, p in sorted(by_proxy.items()):
        proxy_out[pname] = {"khipus_with_colour": len(p["khipus"]), "colour_rows": p["colour_rows"],
                            "cords_with_colour": len(p["cords"]), "distinct_tokens": len(p["tokens"]),
                            "distinct_full_color": len(p["full"]),
                            "tokens_not_in_ascher_color_dc": sorted(t for t in p["tokens"] if t not in ref),
                            "created_by_khipus": dict(p["created_by"])}

    okr2kid = {v["okr"]: k for k, v in km.items()}
    six = {}
    for okr in SIX:
        kid = okr2kid[okr]
        sysname = km[kid]["proxy"]
        cords = level1[kid]
        coloured = [first[cid] for cid in cords if cid in first]
        fullset = Counter(norm(r[3]) for r in coloured)
        tokset = Counter(t for r in coloured for t in comp(r))
        usable = 0
        for r in coloured:
            cs = comp(r)
            if cs and all(classify_token(sysname, t, ref, maps, docs)[0] in USABLE for t in cs):
                usable += 1
        six[okr] = {"khipu_id": kid, "investigator_num": km[kid]["inv"], "orig_inv_num": km[kid]["orig"],
                    "created_by": km[kid]["created_by"], "system_proxy": sysname,
                    "level1_pendants": len(cords), "coloured_level1": len(coloured),
                    "no_colour_level1": len(cords) - len(coloured),
                    "distinct_full_color": len(fullset), "full_color_counts": dict(sorted(fullset.items())),
                    "distinct_tokens": len(tokset), "token_counts": dict(sorted(tokset.items())),
                    "token_classes": {t: classify_token(sysname, t, ref, maps, docs)[0] for t in sorted(tokset)},
                    "fully_usable_coloured": usable,
                    "fully_usable_fraction": (usable / len(coloured)) if coloured else None}
    pairs = []
    for a, b in PAIRS:
        fa, fb = six[a]["fully_usable_fraction"], six[b]["fully_usable_fraction"]
        both = six[a]["coloured_level1"] > 0 and six[b]["coloured_level1"] > 0
        gate = both and fa >= THRESHOLD and fb >= THRESHOLD
        pairs.append({"pair": [a, b], "systems": [six[a]["system_proxy"], six[b]["system_proxy"]],
                      "fraction_a": fa, "fraction_b": fb, "threshold": THRESHOLD,
                      "shared_reference": "OKR ascher_color_dc",
                      "gate": "co_mappable" if gate else "not_co_mappable"})

    out = {
        "cycle": "K045", "db": "OKR khipu.db @ 4039ca5 (read-only)",
        "fixture_passed": ok, "fixture": fx,
        "positive_control": {"codes": list(POSITIVE_CONTROL), "present": [x in ref for x in POSITIVE_CONTROL],
                             "label": "schema_ok" if schema_ok else "schema_unexpected"},
        "corpus": {"colour_rows": len(rows), "distinct_full_color": len(fulls),
                   "distinct_component_tokens": len(toks), "tokens_in_ascher_color_dc": len(in_ref),
                   "tokens_not_in_ascher_color_dc": not_ref,
                   "tokens_not_in_dc_but_case_insensitive_match": sorted(t for t in not_ref if t.upper() in ci_ref),
                   "ascher_color_dc_codes": len(ref), "dictionary_codes_never_used": sorted(ref - set(toks)),
                   "multi_component_full_color": multi, "operators": ops},
        "by_proxy": proxy_out,
        "token_classification": token_classes, "token_class_counts": {k: class_counts.get(k, 0) for k in CLASSES},
        "mapping_rows": mapping_classes, "mapping_row_class_counts": {k: mcounts.get(k, 0) for k in CLASSES},
        "systems_with_colour_docs": sorted(docs), "sources": d.get("sources", []),
        "six_khipus": six, "pairs": pairs,
        "note": "Vocabulary coverage only. No aligned-cord colour agreement computed.",
    }
    if not schema_ok:
        out["warning"] = "schema_unexpected: coverage numbers not trusted"
    json.dump(out, open(os.path.join(AN, "k045_results.json"), "w"), indent=1, ensure_ascii=False, default=list)
    print(json.dumps({k: out[k] for k in ("fixture_passed", "positive_control", "corpus", "token_class_counts",
                                           "mapping_row_class_counts", "pairs")}, indent=1, default=list))


def classify():
    d = load_maps()
    c = connect()
    ref = {norm(r[0]) for r in c.execute("select AS_COLOR_CD from ascher_color_dc") if norm(r[0])}
    cnt = Counter(classify_token(m["system_a"], m["code_a"], ref, d["mappings"], set(d["systems_with_colour_docs"]))[0]
                  for m in d["mappings"])
    print(dict(cnt))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "fixture":
        ok, fx = run_fixture(); print(json.dumps(fx, indent=1)); sys.exit(0 if ok else 1)
    elif mode == "dump": dump()
    elif mode == "classify": classify()
    elif mode == "census": census()
    else: sys.exit(__doc__)
