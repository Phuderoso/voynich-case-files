# PE002 · Do the lines of multi-line reverses equal sums of obverse entries, one number system at a time?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed with the tool before any observed match count. Looked at beforehand
(disclosed): structural inventory only — how many tablets survive each filter, entries per tablet, and the number of
testable reverse lines per system (table below), plus the timing of one planted replicate. No observed match count, no
p-value. PE001's descriptive result (19 of 38 single-total tablets balance) is known and is the reason for the gate
effect size (see Gates).

## Why this line
PE001 failed its power gate (0.61 < 0.8) with 38 single-total tablets. Its open line 1: 209 tablets carry more than
one reverse numeral line, plausibly totals split by number system or commodity. Under PE001's whole-tablet damage rule
only **8** of them would survive (inventory), so PE002 moves to a **line-level** rule and asks a per-line question.

## Data and units
Same pinned CDLI dump (`d66b12b`), same parser and value tables as PE001 (`tools/pe001_totals.py`, Englund 2004 Fig.
5.4; capacity chain of CDLJ 2005:3). Tablets with ≥ 2 reverse numeral lines (any state). Only lines whose numeral
part and text are intact (PE001 `strict_bad` false: no `[ ]`, `...`, `#`, `?`) are used; lines with `n(...)` or
unmapped signs are dropped. **Entries** = intact obverse numeral lines (≥ 2 needed); **candidate totals** = intact
reverse numeral lines (≥ 1 needed). 145 tablets qualify.

Per system X ∈ {S, D, B, C}: an entry or line is *valid in X* if all its signs are in X's table; its value is the
exact integer in X's smallest unit. A tablet enters test X if it has ≥ 2 entries valid in X.

## Metrics (per system X)
- **run**: a reverse line *matches* if its value equals the sum of a contiguous run of ≥ 2 obverse entries, all valid
  in X (an invalid entry breaks a run). Includes the full sum when all entries are valid.
- **subset**: matches if its value equals the sum of any ≥ 2 entries valid in X; only tablets with ≤ 12 valid entries
  (larger tablets reach nearly every value and carry no information).
- Statistic T = number of matching reverse lines. Single-entry equalities and full-sum equalities are reported,
  descriptive only.

| Test | S-subset | D-subset | B-subset | C-subset | S-run | D-run | B-run | C-run |
|---|---|---|---|---|---|---|---|---|
| reverse lines / tablets | 191 / 81 | 176 / 78 | 186 / 79 | 272 / 115 | 316 / 101 | 302 / 99 | 311 / 100 | 408 / 140 |

## Null (structure-preserving)
Reverse lines valid in X are permuted among the positions valid in X, **within magnitude strata** (quintiles of line
value, ties broken by order). Each tablet keeps its obverse, its number of reverse lines, and the size class of each
line; only the exact values move. This guards against "big tablets have big totals" being read as exact summation.
The unstratified null is reported as secondary, no decision weight.

## Gates — stage 1, run and saved before stage 2 (`analysis/pe002_curve.json`)
For every test, 200 replicates per plant fraction f ∈ {0, .05, .10, .15, .20, .25, .30, .40, .50}: shuffle all lines
once (destroy signal), then in a fraction f of positions put the exact sum of a random admissible run / subset (size
≥ 2) of that tablet's own entries; test with R = 999 stratified permutations.
- **FPR** (f = 0): rate of p ≤ 0.05 must be ≤ 0.08 and rate of p ≤ 0.00625 must be ≤ 0.02.
- **Power** at **f = 0.25** must be ≥ 0.8 at p ≤ 0.00625 (= 0.05/8). f = 0.25 is chosen below PE001's descriptive
  balance rate (19/38) on purpose, so the gate asks for less than what single-total tablets already showed.
- The full curve and f80 (smallest f with power ≥ 0.8) are published whatever happens.
- Tests with < 20 lines are EXCLUDED (none, by the inventory above).

## Decision rule — stage 2 (`analysis/pe002_results.json`)
Observed T per test, R = 9 999 stratified permutations (seed 202), one-sided p. Benjamini–Hochberg at q = 0.05 over
the tests that passed both gates. **SUPPORTED** if BH-rejected; **NOT DETECTED** if gates passed and not rejected;
**NOT TESTABLE** if a gate failed. Matching tablet ids are listed for later audit, no decision weight.

## Audit of PE001 (`analysis/pe002_pe001_audit.json`)
Power curve of PE001's own H1 design (38 strict tablets, total shuffle, R = 499, p ≤ 0.025, 200 replicates, f ∈
{.10, .20, .30, .40, .50}, seed 204), to show how far PE001 was from its gate and whether f = 0.10 reproduces ~0.61.

Seeds: curve 203·100 + test index (0–7), test 202, audit 204. Tool: [`tools/pe002_multiline.py`](../tools/pe002_multiline.py)
(`curve`, then `audit`, then `test`). Expected compute: ~3 min stage 1 on 8 cores, seconds for stage 2.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
