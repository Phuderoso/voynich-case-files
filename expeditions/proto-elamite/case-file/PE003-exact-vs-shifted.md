# PE003 · Do reverse lines hit exact sums of their own obverse more often than the same line moved by one unit?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **results below** (verdict: C-full and S/D/B/C-subset SUPPORTED; S/D/B-full NOT TESTABLE; post hoc the whole signal is the grand total on single-total tablets). Pre-registration (this file and `tools/pe003_contrast.py`) was published as `d26764e` before any observed PE003 statistic.
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

---

## Results (computed after the pre-registration was published as `d26764e`)

Order of events (America/Vancouver, 2026-11-08): pre-registration committed and published to `main` (`d26764e`) at
~16:31; stage 1 ran 16:32:19–16:32:57 (38.1 s) and was committed and published (`843c6b7`) **before** stage 2 was run;
stage 2 ran 16:33:19 (0.3 s); PE002 audit and post-hoc right after. Outputs: `analysis/pe003_curve.json`,
`analysis/pe003_results.json`, `analysis/pe003_pe002_audit.json`, `analysis/pe003_posthoc.json`, run logs
`analysis/pe003_curve_run.log`, `analysis/pe003_run.log`, `analysis/pe003_posthoc_run.log`.

**Stage 1 — gates** (500 replicates per condition; FPR and near plant at p ≤ 0.05, power at p ≤ 0.00625):

| Test | lines / tablets | FPR p≤.05 / p≤.00625 | near plant f=.20 | power f=.10 / **.20** / .30 | f80 | Gate |
|---|---|---|---|---|---|---|
| S-full | 40 / 29 | 0.060 / 0.006 | 0.000 | 0.114 / **0.614** / 0.98 | 0.30 | **power fails** |
| D-full | 35 / 25 | 0.030 / 0.006 | 0.002 | 0.192 / **0.560** / 0.884 | 0.30 | **power fails** |
| B-full | 36 / 26 | 0.020 / 0.002 | 0.004 | 0.148 / **0.448** / 0.928 | 0.30 | **power fails** |
| C-full | 76 / 56 | 0.042 / 0.002 | 0.000 | 0.876 / **1.00** / 1.00 | 0.10 | pass |
| S-subset | 242 / 132 | 0.028 / 0.004 | 0.000 | 0.358 / **0.950** / 1.00 | 0.20 | pass |
| D-subset | 225 / 127 | 0.044 / 0.008 | 0.000 | 0.130 / **0.848** / 1.00 | 0.20 | pass |
| B-subset | 235 / 128 | 0.038 / 0.004 | 0.000 | 0.104 / **0.872** / 1.00 | 0.20 | pass |
| C-subset | 367 / 210 | 0.046 / 0.000 | 0.000 | 0.904 / **1.00** / 1.00 | 0.10 | pass |

The near plant (sums moved by one unit — PE002's confound, planted on purpose) never fires (≤ 0.4 %): the contrast
does what it was built for.

**Stage 2 — observed** (R = 9 999, seed 302; BH q = 0.05 over the 5 testable tests):

| Test | exact | shifted (mean of ±1) | K = exact − shifted | null K mean (max) | p | Verdict |
|---|---|---|---|---|---|---|
| C-full | 15 / 76 | 0.5 | **14.5** | 1.5 (9.0) | **0.0001** | **SUPPORTED** |
| B-subset | 76 / 235 | 72.0 | 4.0 | −7.4 (7.5) | **0.0023** | **SUPPORTED** |
| D-subset | 72 / 225 | 68.5 | 3.5 | −7.6 (7.0) | **0.0024** | **SUPPORTED** |
| C-subset | 98 / 367 | 88.5 | 9.5 | −3.7 (16.5) | **0.0071** | **SUPPORTED** |
| S-subset | 76 / 242 | 72.5 | 3.5 | −5.6 (12.0) | **0.0239** | **SUPPORTED** (BH threshold 0.05) |
| S-, D-, B-full | 11, 11, 11 | 0, 0, 0 | 11, 11, 11 | 2.1, 3.2, 2.8 | 0.0001–0.0002 | NOT TESTABLE (power gate; reported, no weight) |

Descriptive split (no decision weight): C-full single-total lines 14 exact / 0.5 shifted of 43, multi-line 1 / 0 of 33;
subset tests single-total 15–32 exact vs 5.5–15 shifted, multi-line 57–66 exact vs 63–73.5 shifted (exact **below**
shifted, as in PE002).

**By the rule: C-full and all four subset tests SUPPORTED; S/D/B-full NOT TESTABLE.**

## Post-hoc diagnostics (after stage 2, no decision weight; `tools/pe003_posthoc.py`, seed 305, R = 9 999)
- **P1, split by tablet type.** Single-total tablets: K = 13.5 (C-full), 9.5–17 (subsets), p 0.0001–0.0018. Multi-line
  tablets: K = 1.0 (C-full, p 0.40) and −5.5 to −7.5 (subsets, p 0.14–0.74). **The whole signal sits on tablets with one
  reverse numeral line.**
- **P2, subset tests without the full sum.** Drop the 17–21 lines that equal their tablet's full sum: K = −7.5 to −10.5,
  p 0.64–0.76 in all four systems. **Nothing beyond the grand total survives**: no evidence of partial sums.
- **P3.** 81 distinct tablets carry at least one exact hit across the five testable tests (most subset hits are the
  coincidences the shifted term cancels).

## PE002 audit
PE002 stage 2 re-run from the published tool (seed 202) in a scratch copy: **identical** matched counts, p-values and
verdicts (`analysis/pe003_pe002_audit.json`).

## What PE003 settles
- With a statistic that cancels unit/range likeness (verified by the near plant), intact proto-Elamite **single-total
  reverses equal the sum of all obverse entries** far more often than their one-unit neighbours (C-full 15 vs 0.5,
  p ≤ 0.0001, BH). This is the **grand-total convention already described in the literature** (Damerow & Englund 1989, *The Proto-Elamite Texts from Tepe Yahya*; Englund 2004): PE003 confirms it
  on the CDLI transliterations with a calibrated, powered test. It is a **validation of the instrument**, not a new
  discovery about the script.
- **Multi-line reverses**: no excess of exact over shifted sums, full or partial (P1, P2). Their lines are not shown to
  be sums of obverse entries; PE002's NOT DETECTED stands, now without the unit-likeness confound.
- The closed-arithmetic instrument is now calibrated, which is what open line 2 (restoring damaged numerals) needs.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
