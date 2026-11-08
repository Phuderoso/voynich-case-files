#!/usr/bin/env python3
"""K043 - literature / Khipu Field Guide audit of K042's 10 leftover singleton-total pendants.

Not a statistical test. Two modes:
  targets : read analysis/k042_results.json, verify the locked 10-pendant catalogue,
            write analysis/k043_targets.json (URLs to look up).
  merge   : read analysis/k043_records.json (hand-recorded after the web reads),
            apply the pre-registered labels/validation and write analysis/k043_results.json.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04.
"""
import json, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.join(HERE, "..", "analysis")
EXPECTED_OKR = {"KH0082", "KH0113", "KH0235", "KH0246", "KH0323", "KH0424", "KH0460", "KH0482", "KH0583"}
LABELS = {"already_counted", "mentioned_other_sum", "not_mentioned", "source_missing", "method_excluded"}
CONTROL = {"okr": "KH0359", "inv": "UR119"}
KFG = "https://www.khipufieldguide.com/catalog/{}.html"


def load_catalogue():
    d = json.load(open(os.path.join(AN, "k042_results.json")))
    cat = d["observed"]["catalogue_Gs"]
    if len(cat) != 10:
        sys.exit(f"EXCLUDED: catalogue_Gs has {len(cat)} entries, expected 10")
    okrs = {c["okr"] for c in cat}
    if okrs != EXPECTED_OKR:
        sys.exit(f"EXCLUDED: okr ids differ: {sorted(okrs ^ EXPECTED_OKR)}")
    if not all(c["singleton_total"] for c in cat):
        sys.exit("EXCLUDED: a catalogue entry is not singleton_total")
    keep = ("okr", "inv", "cord_ordinal", "cord_id", "value", "side", "group_len", "group_start", "group_end")
    return [{k: c[k] for k in keep} for c in cat]


def targets():
    cat = load_catalogue()
    out = {"cycle": "K043", "control": dict(CONTROL, url=KFG.format(CONTROL["okr"])),
           "pendants": [dict(c, url=KFG.format(c["okr"])) for c in cat],
           "khipus": sorted(EXPECTED_OKR)}
    json.dump(out, open(os.path.join(AN, "k043_targets.json"), "w"), indent=1)
    print(f"targets written: {len(cat)} pendants on {len(EXPECTED_OKR)} khipus + control {CONTROL['okr']}")


def merge():
    cat = load_catalogue()
    rec = json.load(open(os.path.join(AN, "k043_records.json")))
    ctl = rec["control"]
    control_pass = bool(ctl["retrieved"] and ctl["mentions_sums"])
    pend = rec["pendants"]
    if len(pend) != 10:
        sys.exit("records: need 10 pendant entries")
    keyset = {(c["okr"], c["cord_ordinal"]) for c in cat}
    out = []
    for p in pend:
        if (p["okr"], p["cord_ordinal"]) not in keyset:
            sys.exit(f"records: unknown pendant {p['okr']} {p['cord_ordinal']}")
        lab = p["label"] if control_pass else "method_excluded"
        if lab not in LABELS:
            sys.exit(f"bad label {lab}")
        if lab == "method_excluded" and control_pass:
            sys.exit("method_excluded used while control passed")
        out.append(dict(p, label=lab))
    counts = {l: sum(1 for p in out if p["label"] == l) for l in sorted(LABELS)}
    res = {"cycle": "K043", "control": dict(ctl, passed=control_pass),
           "pendants": out, "counts": counts,
           "khipu_page_mentions_any_sum": rec.get("khipu_page_mentions_any_sum", {}),
           "notes": rec.get("notes", "")}
    json.dump(res, open(os.path.join(AN, "k043_results.json"), "w"), indent=1, ensure_ascii=False)
    print("control passed:", control_pass); print("counts:", counts)


if __name__ == "__main__":
    {"targets": targets, "merge": merge}[sys.argv[1] if len(sys.argv) > 1 else "targets"]()
