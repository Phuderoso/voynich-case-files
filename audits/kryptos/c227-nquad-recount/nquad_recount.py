#!/usr/bin/env python3
"""Independent NC vs n recount for cycle 227 nulls and Gate P plants. See RULE.md."""
from __future__ import annotations

import hashlib
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

WORK = Path("/workspace/k227-nquad-recount")
REPO = WORK / "kryptos-main"
DATA = REPO / "data/cycle227"
QG_PATH = WORK / "qg.bin"

CRIB = set(range(21, 34)) | set(range(63, 74))  # 0-indexed; 1-indexed 22-34 and 64-74
NLETTERS = 97
WINDOW_STARTS = range(94)


def qi(a, b, c, d):
    return ((a * 26 + b) * 676) + c * 26 + d


qg = np.fromfile(QG_PATH, dtype=np.float32)
assert qg.shape == (26 ** 4,)
assert abs(float(qg.min()) - (-8.469008)) < 1e-6


def score_pt(pt: str):
    if len(pt) != NLETTERS or any(ch not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ?" for ch in pt):
        raise ValueError(f"bad pt length/charset: {pt!r}")
    known = NLETTERS - pt.count("?")
    sc = []
    for i in WINDOW_STARTS:
        span = range(i, i + 4)
        if any(x in CRIB for x in span):
            continue
        quad = pt[i : i + 4]
        if "?" in quad:
            continue
        sc.append(float(qg[qi(*[ord(ch) - 65 for ch in quad])]))
    n = len(sc)
    nc = (sum(sc) / n) if n else None
    return known, n, nc


def passes(nc, n, known):
    return nc is not None and nc >= -6.0 and known >= 49 and n >= 10


BODY_NC = re.compile(r"\s+nqnc=-?\d+")
BODY_NCF = re.compile(r"\s+nc=-?[0-9.]+")
HIT_RE = re.compile(
    r"^(?P<kind>[BCP]) (?P<model>[GVQ]) perm=(?P<perm>\d+) dir=(?P<dir>\d+) ix=(?P<ix>\d+) "
    r"(?:lay=(?P<lay>\d+) |X=(?P<X>\d+) Y=(?P<Y>\d+) form=(?P<form>\d+) )"
    r"p=(?P<p>\d+) known=(?P<known_pub>\d+)"
    r"(?: nqnc=(?P<nqnc>-?\d+) nc=(?P<nc_pub>-?[0-9.]+))?"
    r" qg=(?P<qg_pub>-?[0-9.]+) pt=(?P<pt>[A-Z?]+)"
)
NULL_FN = re.compile(r"^null(\d+)_")


def hit_body(line: str) -> str:
    s = line.strip()
    if s[:2] in ("B ", "C ", "P "):
        s = s[2:]
    s = BODY_NC.sub("", s)
    s = BODY_NCF.sub("", s)
    return s


def parse_hit(line: str):
    m = HIT_RE.match(line.strip())
    if not m:
        raise ValueError(f"unparsed hit: {line[:240]!r}")
    return m.groupdict()


def iter_null_files():
    return sorted(p for p in (DATA / "R").glob("null*.txt") if p.name != "time.txt")


def collect_null_hits():
    seen = {}
    n_raw = defaultdict(int)  # kind -> count
    n_unparsed = 0
    for path in iter_null_files():
        m = NULL_FN.match(path.name)
        if not m:
            continue
        null_id = m.group(1)
        for lineno, line in enumerate(path.open(), 1):
            if line[:2] not in ("B ", "C ", "P "):
                continue
            n_raw[line[0]] += 1
            if line[0] == "P":
                continue  # duplicate of B/C; do not add
            try:
                rec = parse_hit(line)
            except ValueError:
                n_unparsed += 1
                print("UNPARSED", path.name, lineno, line[:200], file=sys.stderr)
                continue
            key = (path.name, hit_body(line))
            if key in seen:
                seen[key]["kinds"].add(line[0])
                continue
            known, n, nc = score_pt(rec["pt"])
            seen[key] = dict(
                null_id=null_id,
                file=path.name,
                lineno=lineno,
                kinds={line[0]},
                model=rec["model"],
                perm=int(rec["perm"]),
                dir=int(rec["dir"]),
                ix=int(rec["ix"]),
                lay=rec["lay"],
                X=rec["X"],
                Y=rec["Y"],
                form=rec["form"],
                p=int(rec["p"]),
                pt=rec["pt"],
                known=known,
                n=n,
                nc=nc,
                pass_=passes(nc, n, known),
            )
    return list(seen.values()), dict(n_raw), n_unparsed


def parse_gatep():
    rows = []
    path = DATA / "gateP227.tsv"
    for i, line in enumerate(path.open(), 1):
        line = line.rstrip("\n")
        if not line:
            continue
        # id model geo scope p  then key=value fields, plus true=
        # The pt field may be '-' or a 97-letter string.
        main, _, true = line.partition("\ttrue=")
        parts = main.split("\t")
        pid, model, geo, scope, p = parts[0], parts[1], parts[2], parts[3], parts[4]
        fields = {}
        pt = None
        for tok in parts[5:]:
            if tok.startswith("pt="):
                pt = tok[3:]
            elif "=" in tok:
                k, _, v = tok.partition("=")
                fields[k] = v
        rec = dict(
            id=int(pid),
            model=model,
            geo=geo,
            scope=int(scope),
            p=int(p),
            bad=fields.get("bad"),
            found=fields.get("found"),
            pt=pt,
            true=true or None,
        )
        if pt and pt != "-":
            known, n, nc = score_pt(pt)
            rec.update(known=known, n=n, nc=nc, pass10=passes(nc, n, known),
                       pass20=passes(nc, n, known) and n >= 20,
                       lost20=passes(nc, n, known) and n < 20)
        else:
            rec.update(known=None, n=None, nc=None, pass10=False, pass20=False, lost20=False)
        rows.append(rec)
    return rows


def q95(vals):
    return float(np.quantile(np.asarray(vals, dtype=float), 0.95, method="linear"))


def fit_invsqrt(ns, ys):
    # ys ≈ a + b / sqrt(n), least squares
    x = 1.0 / np.sqrt(np.asarray(ns, dtype=float))
    y = np.asarray(ys, dtype=float)
    A = np.column_stack([np.ones_like(x), x])
    coeff, residuals, rank, _ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coeff
    sse = float(((y - pred) ** 2).sum())
    sst = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - sse / sst if sst > 0 else float("nan")
    return float(coeff[0]), float(coeff[1]), r2


def monotone_nonincreasing(pairs):
    """pairs: (n, value) sorted by n. True if values are nonincreasing in n."""
    last = None
    for _, v in pairs:
        if last is not None and v > last + 1e-12:
            return False
        last = v
    return True


def fmt_nc(nc):
    return "NA" if nc is None else f"{nc:.4f}"


def run():
    hits, n_raw, n_unparsed = collect_null_hits()
    plants = parse_gatep()
    if n_unparsed:
        raise SystemExit(f"unparsed hits: {n_unparsed}")

    with_nc = [h for h in hits if h["n"] >= 1]
    k49 = [h for h in with_nc if h["known"] >= 49]

    # primary table: all unique null hits with n>=1
    by_n = defaultdict(list)
    for h in with_nc:
        by_n[h["n"]].append(h)

    # also known>=49
    by_n_k49 = defaultdict(list)
    for h in k49:
        by_n_k49[h["n"]].append(h)

    counts_path = WORK / "counts_by_n.tsv"
    with counts_path.open("w") as f:
        f.write(
            "n\tn_hits\tmax_NC\tq95_NC\tpass_hits"
            "\tn_hits_known49\tmax_NC_known49\tq95_NC_known49\tpass_hits_known49\n"
        )
        for n in range(1, 65):
            rows = by_n.get(n, [])
            rows49 = by_n_k49.get(n, [])
            ncs = [h["nc"] for h in rows]
            ncs49 = [h["nc"] for h in rows49]
            n_hits = len(rows)
            n_hits49 = len(rows49)
            mx = max(ncs) if ncs else None
            mx49 = max(ncs49) if ncs49 else None
            q = q95(ncs) if ncs else None
            q49 = q95(ncs49) if ncs49 else None
            pss = sum(1 for h in rows if h["pass_"])
            pss49 = sum(1 for h in rows49 if h["pass_"])
            f.write(
                f"{n}\t{n_hits}\t{fmt_nc(mx)}\t{fmt_nc(q)}\t{pss}"
                f"\t{n_hits49}\t{fmt_nc(mx49)}\t{fmt_nc(q49)}\t{pss49}\n"
            )

    plants_path = WORK / "plants_floor20.tsv"
    with plants_path.open("w") as f:
        f.write(
            "id\tmodel\tgeo\tscope\tp\tknown\tn\tNC\tpass_n10\tpass_n20\tlost_if_floor20\tpt\n"
        )
        for r in plants:
            if r["n"] is None:
                f.write(
                    f"{r['id']}\t{r['model']}\t{r['geo']}\t{r['scope']}\t{r['p']}\t"
                    f"NA\tNA\tNA\t0\t0\t0\t{r['pt']}\n"
                )
            else:
                f.write(
                    f"{r['id']}\t{r['model']}\t{r['geo']}\t{r['scope']}\t{r['p']}\t"
                    f"{r['known']}\t{r['n']}\t{r['nc']:.4f}\t"
                    f"{int(r['pass10'])}\t{int(r['pass20'])}\t{int(r['lost20'])}\t{r['pt']}\n"
                )

    # overall
    def stats(hs, label):
        ncs = [h["nc"] for h in hs]
        pas = [h for h in hs if h["pass_"]]
        mx = max(ncs) if ncs else None
        mx_h = max(hs, key=lambda h: h["nc"]) if hs else None
        return dict(label=label, n=len(hs), max=mx, q95=q95(ncs) if ncs else None,
                    npass=len(pas), max_h=mx_h, passes=pas)

    all_s = stats(with_nc, "all n>=1")
    k49_s = stats(k49, "known>=49 n>=1")
    cand_s = stats([h for h in k49 if h["n"] >= 10], "known>=49 n>=10")

    # unique-on-(null, perm, model, p, pt)
    collapsed = {}
    for h in with_nc:
        k = (h["null_id"], h["perm"], h["model"], h["p"], h["pt"])
        if k not in collapsed or h["nc"] > collapsed[k]["nc"]:
            collapsed[k] = h
    col = list(collapsed.values())
    col_s = stats(col, "collapsed (null,perm,model,p,pt) n>=1")
    col_pass = [h for h in col if h["pass_"]]

    # monotone / fit on known>=49 q95, n with >=5 hits
    pairs_max = [(n, max(h["nc"] for h in by_n_k49[n])) for n in range(1, 65) if by_n_k49.get(n)]
    pairs_q95 = [(n, q95([h["nc"] for h in by_n_k49[n]])) for n in range(1, 65) if by_n_k49.get(n)]
    fit_n, fit_y = zip(*[(n, v) for n, v in pairs_q95 if len(by_n_k49[n]) >= 5]) if any(
        len(by_n_k49[n]) >= 5 for n in by_n_k49
    ) else ([], [])
    if fit_n:
        a, b, r2 = fit_invsqrt(fit_n, fit_y)
    else:
        a = b = r2 = float("nan")

    # violations of monotone nonincreasing for max and q95 (known>=49)
    def violations(pairs):
        out = []
        last_n, last_v = None, None
        for n, v in pairs:
            if last_v is not None and v > last_v + 1e-12:
                out.append((last_n, last_v, n, v))
            last_n, last_v = n, v
        return out

    viol_max = violations(pairs_max)
    viol_q95 = violations(pairs_q95)

    # plants summary
    vq = [r for r in plants if r["n"] is not None]
    lost = [r for r in vq if r["lost20"]]
    kept20 = [r for r in vq if r["pass20"]]
    fail10 = [r for r in vq if not r["pass10"]]

    lines = []
    def L(s=""):
        lines.append(s)

    L(f"unique null hits (B/C, P excluded as dups): {len(hits)}")
    L(f"raw line counts before unique: B={n_raw.get('B',0)} C={n_raw.get('C',0)} P={n_raw.get('P',0)} (P not added)")
    L(f"unparsed: {n_unparsed}")
    L(f"with n>=1 (NC defined): {len(with_nc)}; with known>=49 and n>=1: {len(k49)}; "
      f"with known>=49 and n>=10: {cand_s['n']}")
    L(f"PRIMARY (unique hits, n>=1): max NC {fmt_nc(all_s['max'])}  q95 {fmt_nc(all_s['q95'])}  "
      f"passes {all_s['npass']}")
    L(f"known>=49 n>=1: max NC {fmt_nc(k49_s['max'])}  q95 {fmt_nc(k49_s['q95'])}  passes {k49_s['npass']}")
    L(f"known>=49 n>=10 (house-bar eligible): max NC {fmt_nc(cand_s['max'])}  q95 {fmt_nc(cand_s['q95'])}  "
      f"passes {cand_s['npass']}")
    if cand_s["max_h"]:
        h = cand_s["max_h"]
        L(f"  eligible max is also overall known>=49 max: null {h['null_id']} model={h['model']} "
          f"p={h['p']} perm={h['perm']} dir={h['dir']} ix={h['ix']} "
          f"n={h['n']} known={h['known']} NC={h['nc']:.4f} file={h['file']} lineno={h['lineno']} pass={int(h['pass_'])}")
    L(f"all passes (unique hits): {all_s['npass']}")
    for h in all_s["passes"]:
        L(f"  PASS null {h['null_id']} model={h['model']} p={h['p']} perm={h['perm']} "
          f"dir={h['dir']} ix={h['ix']} lay={h['lay']} X={h['X']} Y={h['Y']} form={h['form']} "
          f"n={h['n']} known={h['known']} NC={h['nc']:.4f} file={h['file']} lineno={h['lineno']}")
    L(f"collapsed on (null,perm,model,p,pt): {col_s['n']} rows, max {fmt_nc(col_s['max'])}, "
      f"q95 {fmt_nc(col_s['q95'])}, passes {len(col_pass)}")
    L(f"monotone nonincreasing max_NC(n) over known>=49 n with hits: "
      f"{monotone_nonincreasing(pairs_max)}  violations={len(viol_max)}")
    for v in viol_max[:8]:
        L(f"  max rise: n={v[0]} {v[1]:.4f} -> n={v[2]} {v[3]:.4f}")
    L(f"monotone nonincreasing q95(n) over known>=49 n with hits: "
      f"{monotone_nonincreasing(pairs_q95)}  violations={len(viol_q95)}")
    for v in viol_q95[:8]:
        L(f"  q95 rise: n={v[0]} {v[1]:.4f} -> n={v[2]} {v[3]:.4f}")
    L(f"least-squares q95(n) ≈ a + b/sqrt(n)  (n with >=5 known>=49 hits, N={len(fit_n)}): "
      f"a={a:.4f} b={b:.4f} R^2={r2:.3f}")
    L("Gate P plants: 20 rows, 4 G unscorable (no pt), 16 V/Q scored from pt=")
    L(f"  pass at n>=10: {sum(r['pass10'] for r in vq)}/16")
    L(f"  pass at n>=20: {sum(r['pass20'] for r in vq)}/16")
    L(f"  lost if floor 20 (passed n>=10 but n<20): {len(lost)}")
    for r in vq:
        flag = "LOST" if r["lost20"] else ("KEEP" if r["pass20"] else "FAIL_BAR")
        L(f"  plant {r['id']:2d} {r['model']} p={r['p']} known={r['known']} n={r['n']:2d} "
          f"NC={r['nc']:.4f} {flag}")
    text = "\n".join(lines) + "\n"
    (WORK / "summary_nquad.txt").write_text(text)
    print(text, end="")


if __name__ == "__main__":
    run()
