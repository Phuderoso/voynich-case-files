# PE002 · Do the lines of multi-line reverses equal sums of obverse entries, one number system at a time?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **results below** (verdict: C-run SUPPORTED by the rule but explained by a post-hoc off-by-one control; subsets NOT DETECTED; S/D/B-run NOT TESTABLE). Pre-registration was committed with the tool before any observed match count. Looked at beforehand
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

---

## Results (computed after the pre-registration commit `012c5f9`)

Order of events (America/Vancouver): pre-registration committed locally 15:56 (`150af9b`, published as `012c5f9`);
stage 1 ran 15:56–15:58 (88.8 s) and was committed locally before stage 2 was run (published afterwards as `7a92ee3`); stage 2 took 0.8 s.
Outputs: `analysis/pe002_curve.json`, `analysis/pe002_results.json`, `analysis/pe002_pe001_audit.json`,
`analysis/pe002_posthoc.json`, run logs `analysis/pe002_curve_run.log`, `analysis/pe002_run.log`.

**Stage 1 — gates** (200 replicates per point, p ≤ 0.00625 for power):

| Test | lines / tablets | FPR p≤.05 / p≤.00625 | power f=.10 | power f=.25 | f80 | Gate |
|---|---|---|---|---|---|---|
| S-subset | 191 / 81 | 0.020 / 0.000 | 0.57 | 1.00 | 0.15 | pass |
| D-subset | 176 / 78 | 0.020 / 0.000 | 0.42 | 1.00 | 0.20 | pass |
| B-subset | 186 / 79 | 0.025 / 0.005 | 0.47 | 0.995 | 0.15 | pass |
| C-subset | 272 / 115 | 0.025 / 0.000 | 0.91 | 1.00 | 0.10 | pass |
| S-run | 316 / 101 | **0.170** / 0.040 | 0.90 | 1.00 | 0.10 | **FPR fails** |
| D-run | 302 / 99 | **0.175** / 0.055 | 0.775 | 1.00 | 0.15 | **FPR fails** |
| B-run | 311 / 100 | **0.145** / 0.030 | 0.84 | 1.00 | 0.10 | **FPR fails** |
| C-run | 408 / 140 | 0.025 / 0.000 | 0.995 | 1.00 | 0.10 | pass |

**Stage 2 — observed** (R = 9 999 magnitude-stratified shuffles, seed 202; BH q = 0.05 over the 5 testable tests):

| Test | matched lines | null mean (max) | p | unstratified p (secondary) | Verdict |
|---|---|---|---|---|---|
| C-run | 119 / 408 | 105.5 (124) | **0.0050** | 0.0004 | **SUPPORTED** (BH rank 1, threshold 0.010) |
| D-subset | 57 / 176 | 50.3 (62) | 0.0209 | 0.064 | NOT DETECTED (BH threshold 0.020) |
| S-subset | 61 / 191 | 57.3 (70) | 0.171 | 0.0048 | NOT DETECTED |
| B-subset | 61 / 186 | 57.7 (69) | 0.188 | 0.010 | NOT DETECTED |
| C-subset | 66 / 272 | 62.6 (78) | 0.242 | 0.0053 | NOT DETECTED |
| S-, D-, B-run | 101, 99, 102 | 93.8, 96.2, 93.9 | 0.062, 0.300, 0.041 | — | NOT TESTABLE (FPR gate) |

Descriptive: full-sum equalities are rare (5–6 lines per system); 78–183 reverse lines per system equal a single
obverse entry (repeated values, e.g. lists continuing onto the reverse).

**By the rule: C-run SUPPORTED, the four subset tests NOT DETECTED, S/D/B-run NOT TESTABLE.**

## Post-hoc diagnostics (after stage 2, no decision weight; `tools/pe002_posthoc.py`, seeds 205/206)
- **D1, off-by-one control — the C-run excess is not arithmetic.** If reverse lines were sums, the exact value
  should be reachable more often than the same line moved by ± one unit of its own smallest sign. It is the other way:
  C-run exact 119 vs off-by-one mean 142 (contrast −23; null contrast −15.2; p_contrast 0.91). Same in every test
  (contrast −6 to −27.5, all p_contrast ≥ 0.22). The quintile-stratified null leaves room for a finer likeness — a
  reverse line written in the same units and range as its own obverse — and that likeness alone produces the C-run
  excess. **So the SUPPORTED verdict is a statement about the statistic, not evidence that the reverse lines are totals
  of contiguous obverse runs.** It is not carried forward as a finding.
- **D2, why S/D/B-run failed FPR.** The pre-registered rank strata split equal values across a stratum boundary by
  line position, which breaks exchangeability. FPR at p ≤ 0.05 on 200 destroyed-signal replicates: rank strata 0.155–0.21;
  tie-aware strata (equal values share a stratum) 0.035–0.045; no strata 0.02–0.035. C-run 0.045 / 0.04 / 0.06. The gate did its job.
- **PE001 audit.** PE001's own H1 design re-simulated (seed 204): power 0.58 at f = 0.10 (published 0.61, within
  Monte-Carlo error), **1.00 at f = 0.20** and above. PE001 missed its gate only because of the 10 % plant size; its
  verdict (NOT TESTABLE) stands as written.

## What PE002 settles
- Exact sums of obverse entries do not show up on multi-line reverses at a detectable rate in any system (subset tests
  powered at f80 0.10–0.20, NOT DETECTED), under the line-level damage rule on 145 tablets.
- The one BH-rejected test is explained by unit/range likeness (D1); no summation claim.
- Method debt for PE003: tie-aware strata; an exact-vs-shifted contrast as the *primary* statistic (it cancels unit
  likeness by construction); one pre-registered test on PE001-style single totals with a 20 % plant gate.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
