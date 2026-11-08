#!/usr/bin/env python3
"""K044 - literature / schema audit of four KFG-T / OKR-U leftover sum-top cords.

Not a statistical test. Modes:
  targets : read analysis/k043_results.json, verify the locked four-pendant catalogue,
            write analysis/k044_targets.json (URLs to look up).
  schema  : read-only query of khipu.db for ATTACHMENT_TYPE vocabulary and the four rows;
            write analysis/k044_schema.json. Run only after the prereg commit.
  merge   : read analysis/k044_records.json (hand-recorded after the web reads),
            apply the pre-registered labels/validation and write analysis/k044_results.json.
Pimpolha Voynich, do Phuderoso - AI born 2026-11-04.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AN = os.path.join(HERE, "..", "analysis")
DB = os.path.join(HERE, "..", "khipu.db")

# Locked to K043's published T-attachment leftover pendants.
EXPECTED = (
    ("KH0323", 7, 15),
    ("KH0424", 24, 75),
    ("KH0424", 58, 596),
    ("KH0482", 25, 288),
)
LABELS = {
    "changelog_corrected",
    "changelog_notes_mismatch",
    "no_changelog_mention",
    "source_missing",
}
SCHEMA_SECONDARY = {"okr_has_T", "okr_never_T"}


def load_four():
    d = json.load(open(os.path.join(AN, "k043_results.json")))
    pend = d["pendants"]
    if len(pend) != 10:
        sys.exit(f"EXCLUDED: k043 pendants has {len(pend)} entries, expected 10")
    marked_t = [p for p in pend if p.get("kfg_attachment") == "T"]
    got = [(p["okr"], p["cord_ordinal"], p["value"]) for p in marked_t]
    if got != list(EXPECTED):
        sys.exit(f"EXCLUDED: T-attachment catalogue differs: {got}")
    keep = ("okr", "inv", "cord_ordinal", "value", "kfg_cord", "kfg_attachment")
    return [{k: p[k] for k in keep} for p in marked_t]


def targets():
    four = load_four()
    out = {
        "cycle": "K044",
        "pendants": four,
        "branches": {
            "A_kfg_paths": [
                "https://www.khipufieldguide.com/",
                "https://www.khipufieldguide.com/changelog",
                "https://www.khipufieldguide.com/changelog.html",
                "https://www.khipufieldguide.com/news",
                "https://www.khipufieldguide.com/news.html",
                "https://www.khipufieldguide.com/updates",
                "https://www.khipufieldguide.com/updates.html",
                "https://www.khipufieldguide.com/about",
                "https://www.khipufieldguide.com/about.html",
                "https://www.khipufieldguide.com/notebook/",
            ],
            "B_okr": "https://github.com/khipulab/open-khipu-repository",
            "D_kfg_xlsx": [
                f"https://www.khipufieldguide.com/databook/excel_khipus/{p['okr']}.xlsx"
                for p in four
            ],
        },
    }
    path = os.path.join(AN, "k044_targets.json")
    json.dump(out, open(path, "w"), indent=1)
    print(f"targets written: {len(four)} pendants -> {path}")


def schema():
    import sqlite3
    four = load_four()
    db = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    # Prefer a cord-level table that has ATTACHMENT_TYPE.
    cord_table = None
    for t in tables:
        cols = [r[1] for r in db.execute(f"PRAGMA table_info({t})")]
        if "ATTACHMENT_TYPE" in cols and "CORD_ORDINAL" in cols:
            cord_table = t
            cord_cols = cols
            break
    if cord_table is None:
        sys.exit(f"EXCLUDED: no table with ATTACHMENT_TYPE and CORD_ORDINAL in {tables}")
    vocab = [
        {"attachment_type": r[0], "n": r[1]}
        for r in db.execute(
            f"SELECT ATTACHMENT_TYPE, COUNT(*) FROM {cord_table} GROUP BY ATTACHMENT_TYPE ORDER BY COUNT(*) DESC"
        )
    ]
    has_t = any((v["attachment_type"] == "T") and v["n"] > 0 for v in vocab)
    rows = []
    for p in four:
        q = db.execute(
            f"SELECT * FROM {cord_table} c JOIN khipu k ON k.KHIPU_ID = c.KHIPU_ID "
            f"WHERE k.KHIPU_ID = ? AND c.CORD_ORDINAL = ?",
            (p["okr"], p["cord_ordinal"]),
        ).fetchall()
        if not q:
            # Some dumps use an investigator code or a numeric id; try JOIN via PRIMARY_ID / KHIPU
            q = db.execute(
                f"SELECT * FROM {cord_table} WHERE CORD_ORDINAL = ? AND KHIPU_ID IN "
                f"(SELECT KHIPU_ID FROM khipu WHERE KHIPU_ID = ? OR INVESTIGATOR_NUM LIKE ?)",
                (p["cord_ordinal"], p["okr"], p["okr"] + "%"),
            ).fetchall()
        if len(q) != 1:
            sys.exit(f"EXCLUDED: {p['okr']} ordinal {p['cord_ordinal']} matched {len(q)} cord rows")
        rec = dict(q[0])
        # Keep a stable subset plus attachment.
        keep_keys = [
            k for k in (
                "KHIPU_ID", "CORD_ID", "CORD_ORDINAL", "ATTACHMENT_TYPE",
                "CORD_LEVEL", "CLUSTER_ID", "CLUSTER_BEGINS_NEW_GROUP",
                "PENDANT_FROM", "TERMINAL", "KNOTTED",
            ) if k in rec
        ]
        slim = {k: rec[k] for k in keep_keys}
        # knot value if present
        try:
            kv = db.execute(
                "SELECT knot_value_type FROM knot WHERE CORD_ID = ?",
                (rec.get("CORD_ID"),),
            ).fetchone()
            slim["knot_value_type"] = None if kv is None else kv[0]
        except sqlite3.Error:
            slim["knot_value_type"] = None
        if slim.get("knot_value_type") != p["value"]:
            # Some schemas store the value on the cord table.
            if "knot_value_type" in rec:
                slim["knot_value_type"] = rec["knot_value_type"]
        rows.append({**p, "okr_row": slim})
    out = {
        "cycle": "K044",
        "cord_table": cord_table,
        "cord_columns": cord_cols,
        "attachment_vocab": vocab,
        "secondary": "okr_has_T" if has_t else "okr_never_T",
        "pendants": rows,
    }
    path = os.path.join(AN, "k044_schema.json")
    json.dump(out, open(path, "w"), indent=1, default=str)
    print("schema written:", path)
    print("vocab:", vocab)
    print("secondary:", out["secondary"])
    for r in rows:
        print(r["okr"], r["cord_ordinal"], "OKR", r["okr_row"].get("ATTACHMENT_TYPE"),
              "value", r["okr_row"].get("knot_value_type"))


def merge():
    four = load_four()
    rec = json.load(open(os.path.join(AN, "k044_records.json")))
    pend = rec["pendants"]
    if len(pend) != 4:
        sys.exit("records: need 4 pendant entries")
    keyset = {(c["okr"], c["cord_ordinal"], c["value"]) for c in four}
    out = []
    for p in pend:
        key = (p["okr"], p["cord_ordinal"], p["value"])
        if key not in keyset:
            sys.exit(f"records: unknown pendant {key}")
        lab = p["label"]
        if lab not in LABELS:
            sys.exit(f"bad label {lab}")
        out.append(dict(p))
    counts = {l: sum(1 for p in out if p["label"] == l) for l in sorted(LABELS)}
    secondary = rec.get("secondary")
    if secondary not in SCHEMA_SECONDARY:
        sys.exit(f"bad secondary {secondary}")
    res = {
        "cycle": "K044",
        "changelog_sources": rec.get("changelog_sources", []),
        "okr_docs": rec.get("okr_docs", []),
        "pendants": out,
        "counts": counts,
        "secondary": secondary,
        "note_action": rec.get("note_action", ""),
        "notes": rec.get("notes", ""),
    }
    path = os.path.join(AN, "k044_results.json")
    json.dump(res, open(path, "w"), indent=1, ensure_ascii=False)
    print("counts:", counts)
    print("secondary:", secondary)
    print("note_action:", res["note_action"])


if __name__ == "__main__":
    modes = {"targets": targets, "schema": schema, "merge": merge}
    if len(sys.argv) != 2 or sys.argv[1] not in modes:
        sys.exit("usage: k044_tu_attachment_audit.py [targets|schema|merge]")
    modes[sys.argv[1]]()
