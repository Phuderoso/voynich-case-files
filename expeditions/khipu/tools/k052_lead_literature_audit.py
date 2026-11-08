#!/usr/bin/env python3
"""K052 - pre-registered literature audit of the unconfirmed lead KH0240 (UR004) . KH0496 (UR260).

Not a statistical test. Three modes:
  targets : check the pinned OKR khipu.db ids and K051's values gate, lock the two subjects and the
            two controls, write analysis/k052_targets.json (URLs to look up).
  merge   : read analysis/k052_records.json (hand-recorded after the web reads), enforce the
            pre-registered labels and control gates, write analysis/k052_results.json.
  context : read-only khipu.db labels (site, museum, notes) of the two subjects -> k052_okr_context.json
            (descriptive, not a test).
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04.
"""
import hashlib, json, os, sqlite3, sys
HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.join(HERE, "..", "analysis")
DB = os.path.join(HERE, "..", "khipu.db")
SHA = "607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db"
SUBJECTS = {"KH0240": "UR004", "KH0496": "UR260"}
CONTROLS = {
    "C1": {"evidence_class": "E1_similar_field", "okr": "KH0616", "inv": "JC009", "partner_okr": "KH0620", "partner_inv": "JC013"},
    "C2": {"evidence_class": "E2_publication_match", "okr": "KH0502", "inv": "UR266", "partner_okr": "KH0514", "partner_inv": "UR275"},
}
CLASSES = {c["evidence_class"]: k for k, c in CONTROLS.items()}
LABELS = {"already_paired", "mentioned_other_match", "not_mentioned", "source_missing", "method_excluded"}
KFG = "https://www.khipufieldguide.com/catalog/{}.html"
XLSX = "https://www.khipufieldguide.com/databook/excel_khipus/{}.xlsx"
APPX = ("https://static.cambridge.org/content/id/urn:cambridge.org:id:article:S1045663500008786/"
        "resource/name/S1045663500008786sup001.pdf")
RUNLEN = {"KH0240": [4, 1, 1, 1, 1, 1, 1, 1, 1], "KH0496": [1, 1, 3, 1, 1, 2, 1, 1, 1]}


def open_db():
    h = hashlib.sha256(open(DB, "rb").read()).hexdigest()
    if h != SHA:
        sys.exit(f"EXCLUDED: khipu.db hash {h} != pinned {SHA}")
    return sqlite3.connect("file:" + DB + "?mode=ro", uri=True)


def check_ids():
    db = open_db()
    want = dict(SUBJECTS)
    for c in CONTROLS.values():
        want[c["okr"]] = c["inv"]; want[c["partner_okr"]] = c["partner_inv"]
    got = {o: i for o, i in db.execute(
        "select OKR_NUM, INVESTIGATOR_NUM from khipu_main where OKR_NUM in (%s)" % ",".join("?" * len(want)),
        tuple(want))}
    if got != want:
        sys.exit(f"EXCLUDED: id map differs: want {want} got {got}")
    k51 = json.load(open(os.path.join(AN, "k051_results.json")))["consistency"]
    pair = {k51["a"]["meta"]["okr"]: k51["a"]["runlen"], k51["b"]["meta"]["okr"]: k51["b"]["runlen"]}
    if not k51["ok"] or pair != RUNLEN or k51.get("other_P_holders"):
        sys.exit(f"EXCLUDED: K051 values gate does not name the locked pair: {pair}")
    return db


def targets():
    check_ids()
    out = {"cycle": "K052", "pattern_collapsed": [1, 2, 1, 2, 3, 1, 2, 1, 3], "runlen": RUNLEN,
           "subjects": [{"okr": o, "inv": i, "kfg": KFG.format(o), "kfg_alt": KFG.format(i), "xlsx": XLSX.format(o)}
                        for o, i in SUBJECTS.items()],
           "controls": {k: dict(c, kfg=KFG.format(c["okr"]), kfg_partner=KFG.format(c["partner_okr"]))
                        for k, c in CONTROLS.items()},
           "named_publication": {"ref": "Urton & Chu, Appendix I: Inventory of Inkawasi Khipus (supplement to "
                                        "'Accounting in the King's Storehouse', Latin American Antiquity)", "url": APPX},
           "labels": sorted(LABELS)}
    json.dump(out, open(os.path.join(AN, "k052_targets.json"), "w"), indent=1)
    print("targets written: subjects", list(SUBJECTS), "controls", {k: c["okr"] for k, c in CONTROLS.items()})


def agg(labels):
    if not labels:
        return "source_missing"
    for l in ("already_paired", "mentioned_other_match", "not_mentioned"):
        if l in labels:
            return l
    if all(l == "method_excluded" for l in labels):
        return "method_excluded"
    return "source_missing"


def merge():
    check_ids()
    rec = json.load(open(os.path.join(AN, "k052_records.json")))
    passed = {}
    for k, c in CONTROLS.items():
        r = rec["controls"][k]
        if r["okr"] != c["okr"]:
            sys.exit(f"records: control {k} okr {r['okr']} != {c['okr']}")
        passed[k] = bool(r["retrieved"] and r["names_partner"])
    out = []
    for s in rec["sources"]:
        cls = s["evidence_class"]
        if cls not in CLASSES:
            sys.exit(f"bad evidence class {cls}")
        ok = passed[CLASSES[cls]]
        lab = {}
        for o in s["subjects"]:
            if o not in SUBJECTS:
                sys.exit(f"unknown subject {o}")
            l = s["labels"][o]
            if l not in LABELS:
                sys.exit(f"bad label {l}")
            if l == "method_excluded" and ok:
                sys.exit("method_excluded used while control passed")
            if not s["retrieved"] and l != "source_missing":
                sys.exit(f"source not retrieved but labelled {l}: {s['url']}")
            if l == "already_paired" and (s.get("quote") in (None, "", "none")):
                sys.exit("already_paired needs a verbatim quote")
            lab[o] = l if (ok or l == "source_missing") else "method_excluded"
        out.append(dict(s, labels=lab, control_passed=ok))
    subj = {}
    for o in SUBJECTS:
        ls = [s["labels"][o] for s in out if o in s["labels"]]
        subj[o] = {"label": agg(ls), "by_class": {cls: agg([s["labels"][o] for s in out
                                                             if o in s["labels"] and s["evidence_class"] == cls])
                                                  for cls in CLASSES}}
    usable = {o: any(s["labels"].get(o) in ("already_paired", "mentioned_other_match", "not_mentioned")
                     for s in out) for o in SUBJECTS}
    if not any(passed.values()):
        pair = "method_excluded"
    elif any(s["labels"].get(o) == "already_paired" for s in out for o in SUBJECTS):
        pair = "already_paired"
    elif all(usable.values()):
        pair = "not_mentioned"
    else:
        pair = "source_missing"
    counts = {l: sum(1 for s in out for v in s["labels"].values() if v == l) for l in sorted(LABELS)}
    res = {"cycle": "K052", "controls": {k: dict(rec["controls"][k], passed=passed[k]) for k in CONTROLS},
           "sources": out, "subjects": subj, "pair_label": pair, "label_counts_source_x_subject": counts,
           "n_sources": len(out), "descriptive": rec.get("descriptive", {}), "failed_attempts": rec.get("failed_attempts", []),
           "notes": rec.get("notes", "")}
    json.dump(res, open(os.path.join(AN, "k052_results.json"), "w"), indent=1, ensure_ascii=False)
    print("controls passed:", passed); print("subjects:", {o: v["label"] for o, v in subj.items()})
    print("pair:", pair); print("counts:", counts)


def context():
    db = check_ids()
    cols = ["OKR_NUM", "INVESTIGATOR_NUM", "PROVENANCE", "REGION", "MUSEUM_NAME", "MUSEUM_NUM",
            "EARLIEST_AGE", "LATEST_AGE", "CREATED_BY", "CREATED_ON", "NOTES"]
    out = []
    for o in SUBJECTS:
        row = db.execute("select %s from khipu_main where OKR_NUM=?" % ",".join(cols), (o,)).fetchone()
        out.append(dict(zip(cols, row))); print(out[-1])
    json.dump(out, open(os.path.join(AN, "k052_okr_context.json"), "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    {"targets": targets, "merge": merge, "context": context}[sys.argv[1] if len(sys.argv) > 1 else "targets"]()
