# PE003 · Do reverse lines hit exact sums of their own obverse more often than the same line moved by one unit?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registered** (this file and `tools/pe003_contrast.py` are committed before any observed PE003 statistic).
Looked at beforehand (disclosed): the structural inventory below (`analysis/pe003_inventory.json`: tablets, lines,
lines on single-total tablets per test) and the timing of two planted replicates. No observed exact or shifted count,
no p-value. Known from earlier cycles: PE001 (19 of 38 intact single-total tablets balance, descriptive) and PE002
(exact 119 < off-by-one 142 on C-run; post-hoc), which is why this design exists.

## Why this line
PE002's one BH rejection (C-run) was explained post hoc: a reverse line resembles its own obverse in units and range,
and a magnitude-stratified shuffle does not remove that likeness. The cure is a statistic that cancels it by
construction: compare each line's **exact** value with the **same line moved by ± one unit** of its smallest sign.
Unit/range likeness raises both; only arithmetic raises the exact one.

## Data
Pinned CDLI dump `d66b12b`, parser and value tables of PE001 (`tools/pe001_totals.py`; Englund 2004 Fig. 5.4;
CDLJ 2005:3 capacity chain). PE002's line-level damage rule (only intact numeral lines, `strict_bad` false; `n(...)` and
unmapped signs dropped). **Pooled**: every tablet with ≥ 2 intact obverse numeral lines and ≥ 1 intact reverse numeral
line, single-total and multi-line alike: **253 tablets** (108 with exactly one reverse numeral line).

## Metrics — 8 tests: system X ∈ {S, D, B, C} × reach ∈ {full, subset}
For a reverse line with exact value v (integer, X's smallest unit) on tablet t:
- **unit u(v)** = value of the smallest sign in the greedy canonical notation of v in X (a function of v alone, so it
  travels with the value under permutation and planting).
- **reach(t)**: *full* = {sum of all obverse entries}, only for tablets whose obverse is whole (no damaged numeral line,
  no broken-surface `$`-line) and whose entries are all valid in X; *subset* = sums of any ≥ 2 entries valid in X,
  tablets with ≤ 12 such entries (as PE002).
- **E** = [v ∈ reach], **O** = ([v − u ∈ reach] + [v + u ∈ reach]) / 2.
- **Primary statistic: K = Σ (E − O)** over the test's lines = exact matches minus mean shifted matches.

| Test | S-full | D-full | B-full | C-full | S-subset | D-subset | B-subset | C-subset |
|---|---|---|---|---|---|---|---|---|
| lines / tablets | 40 / 29 | 35 / 25 | 36 / 26 | 76 / 56 | 242 / 132 | 225 / 127 | 235 / 128 | 367 / 210 |
| lines on single-total tablets | 22 | 19 | 20 | 43 | 51 | 49 | 49 | 95 |

The *run* reach of PE002 is dropped (it is nested in *subset* where both apply, and its FPR failure is not repeated).

## Null
Line values permuted among the test's positions **within tie-aware magnitude classes** (5 classes by cumulative count;
equal values never split — PE002 D2 fix). Each value carries its own u. p = (1 + #{null K ≥ observed K}) / (1 + R),
one-sided.

## Gates — stage 1, computed and committed before stage 2 (`analysis/pe003_curve.json`)
500 replicates per condition, R = 999, seed 303·100 + test index. Each replicate first destroys the line–tablet link
(permutation within tie-aware classes), then plants:
- **FPR** (no plant): rate p ≤ 0.05 must be ≤ 0.08 and rate p ≤ 0.00625 (= 0.05/8) must be ≤ 0.02.
- **Specificity against unit likeness** (*near plant*, f = 0.20): a fraction 0.20 of positions get their own tablet's
  admissible sum (full: total; subset: random ≥ 2-entry set) **moved by ± its unit** — values that look like the tablet
  but are not sums. Rate p ≤ 0.05 must be ≤ 0.08. This is the PE002 confound, planted on purpose.
- **Power** (*exact plant*, f = 0.20, the 20 % rate asked for): rate p ≤ 0.00625 must be ≥ 0.8. The curve at f ∈
  {0.10, 0.20, 0.30} and f80 are published whatever happens.
- Tests with < 20 lines: EXCLUDED (none by the inventory).

## Decision rule — stage 2 (`analysis/pe003_results.json`)
Observed K, R = 9 999, seed 302. Benjamini–Hochberg at q = 0.05 over the tests that passed all three gates.
**SUPPORTED** if BH-rejected; **NOT DETECTED** if gates passed and not rejected; **NOT TESTABLE** if a gate failed.
Descriptive only (no decision weight): exact and shifted counts split by single-total vs multi-line tablets; tablet ids
with exact matches.

A SUPPORTED test would mean: reverse lines equal sums of their own obverse entries more often than one-unit
neighbours do, beyond a shuffle that keeps magnitudes. It would **not** by itself fix which entries are summed.

## Audit of PE002 (`analysis/pe003_pe002_audit.json`)
Re-run PE002 stage 2 (seed 202) from the committed tool in a scratch copy and compare every matched count, p and
verdict with the published `analysis/pe002_results.json`.

Tool: [`tools/pe003_contrast.py`](../tools/pe003_contrast.py) (`inventory`, `curve`, `test`, `audit`).
Expected compute: well under a minute per stage on 8 cores.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
