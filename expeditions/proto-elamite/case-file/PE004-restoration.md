# PE004 · Can the grand-total rule restore a damaged numeral, and how often is the answer unique?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **results below** (verdict: entry and total targets both **NOT VALIDATED**, gate G2 precision fails; no
restoration list is published). Pre-registration (this file and `tools/pe004_restore.py`) was published as `5301a04`
before any calibration number (recovery, precision, baseline, null) was computed.
Looked at beforehand (disclosed): the structural inventory (`analysis/pe004_inventory.json`: tablet and slot counts
only), the solver check G0 on **synthetic** tablets (2 000 tablets, 11 994 slots, 0 missed, seed 401; no corpus data),
and the run time of the null on unshuffled-shape data (no count read). Known from earlier cycles: PE001 (19 of 38
intact single-total tablets balance, descriptive), PE003 (single totals equal the sum of the whole obverse, C-full
15 vs 0.5 shifted, p ≤ 0.0001: the known grand-total convention of Damerow & Englund 1989 and Englund 2004).

## Why this line
PE003 validated the instrument: on single-total tablets the reverse total is the sum of the whole obverse. A closed
sum is a constraint: if exactly one term is missing, arithmetic fixes it **given the numerical system**. Two things
can go wrong and must be measured before any restoration is proposed: (1) the tablet may not balance (PE001: about
half do not), and (2) the system may be ambiguous (N01/N14/N34 are shared by S, B and C with different values), so
the same arithmetic gives different notations. So the method is scored first where the answer is known.

## Data
Pinned CDLI dump `d66b12b`, value tables of PE001 (Englund 2004 Fig. 5.4; CDLJ 2005:3 capacity chain; S, D, B, C).
Parser of PE001 plus line labels; **damage is judged on the numeral part** of each line (after the last comma):
`[`, `]`, `...`, `#`, `?`. Tablets with a broken/missing `$`-line on obverse or reverse, or with a primed line number
(lost beginning), are excluded throughout.
- **Calibration set** (intact): no damaged numeral part on obverse/reverse, ≥ 2 obverse numeral lines, exactly one
  reverse numeral line, all notations mapped: **45 tablets → 266 entry tasks + 45 total tasks** (each obverse entry
  hidden in turn; the total hidden).
- **Application set** (damaged): exactly one damaged numeral slot (one obverse entry *or* the total), everything
  else intact and mapped, same shape: **51 tablets** (33 entry slots, 18 total slots; 41 with visible signs in the
  damaged slot; 6 with a complete editorial restoration in brackets).

## Rule (fixed; no parameter is tuned)
For a missing slot and each system X in which every intact notation (and every visible sign of the slot) is valid:
entry slot v = total − Σ other entries (admissible iff v > 0); total slot v = Σ entries. Candidate = the greedy
canonical notation of v in X, kept only if it contains the slot's visible signs (lower bounds; signs marked `#`/`?`
count as read, bracketed material does not). **Candidate set** = distinct notations over admissible systems;
**unique** iff exactly one; the **uniqueness count** is its size. The rule predicts only when unique.

## Metrics (stage 1, calibration; per target T ∈ {entry, total})
- **Recovery rate** = unique-and-correct / tasks; **precision** = unique-and-correct / unique; coverage (truth among
  candidates), mean candidate count, no-candidate count (descriptive).
- **Frequency baseline** (always guesses): entry → the most frequent notation among the tablet's other entries (ties:
  frequency among the other calibration tablets' entries, then lexical); total → the most frequent total among the
  other calibration tablets.
- **Arithmetic-destroyed null**: totals permuted among the 45 calibration tablets (R = 9 999, seed 404); statistic =
  unique-and-correct count; p = (1 + #{null ≥ observed}) / (1 + R).

## Gates (all must pass for a target T to be VALIDATED)
- **G0 solver**: on synthetic balancing tablets every hidden slot's truth is among the candidates (0 misses).
- **G1 size**: ≥ 30 tasks.
- **G2 precision**: ≥ 10 unique outputs, precision ≥ 0.80 **and** exact one-sided 95 % Clopper–Pearson lower bound ≥ 0.60.
- **G3 beats the frequency baseline**: exact one-sided McNemar (rule unique-correct vs baseline correct), Holm over the
  two targets at α = 0.05.
- **G4 beats the null**: p ≤ 0.05.

## Stage 2 (only for VALIDATED targets)
Apply the rule to the damaged tablets of that target; publish every candidate set with its systems and uniqueness
count, the ATF numeral part and visible lower bounds, and (descriptive) whether a complete editorial restoration is
among the candidates. These are **computed suggestions for collation, not readings**: they assume the tablet balances
and that the lost slot held a numeral. A NOT VALIDATED target gets no restoration list.

## Audit of PE003
Re-run PE003 stage 2 (seed 302) and the post hoc (seed 305) from the published tools in a scratch copy and compare
every field of `analysis/pe003_results.json` and `analysis/pe003_posthoc.json` (run time excluded).

Tool: [`tools/pe004_restore.py`](../tools/pe004_restore.py) (`inventory`, `calibrate`, `apply`, `audit`). Expected
compute: about 75 s for the null, under a second for the rest.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (computed after the pre-registration was published as `5301a04`)

Order of events (America/Vancouver, 2026-11-08): pre-registration published to `main` (`5301a04`) at ~17:23; stage 1
(calibration) ran 17:23:48–17:25:28 (99.7 s); PE003 audit and post hoc right after. Outputs:
`analysis/pe004_calibration.json` (every task with its candidates and the baseline guess),
`analysis/pe004_calibration_run.log`, `analysis/pe004_pe003_audit.json`, `analysis/pe004_posthoc.json`,
`analysis/pe004_posthoc_run.log`.

**Stage 1 — calibration on 45 intact single-total tablets** (leave-one-out):

| Target | tasks | unique | unique & correct | recovery | precision (CP95 low) | no candidate | baseline correct | McNemar rule-only / base-only, p | null mean (max), p | Gates G0 G1 G2 G3 G4 | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| entry | 266 | 122 | 85 | 0.320 | **0.697** (0.621) | 96 | 102 (0.383) | 47 / 64, p 0.956 | 3.2 (30), 0.0001 | ✓ ✓ **✗** **✗** ✓ | **NOT VALIDATED** |
| total | 45 | 21 | 8 | 0.178 | **0.381** (0.206) | 1 | 0 (0.000) | 8 / 0, p 0.0039 (Holm ✓) | 0.29 (3), 0.0001 | ✓ ✓ **✗** ✓ ✓ | **NOT VALIDATED** |

G0: 2 000 synthetic tablets, 11 994 slots, 0 missed. The arithmetic beats the destroyed-arithmetic null by far in both
targets (p 0.0001), but it is not precise enough to put forward a reading: about 3 in 10 unique entry restorations and
6 in 10 unique total restorations would be wrong, and for entries the plain frequency guess (the tablet's commonest
entry) is right more often (102 vs 85). **By the rule, stage 2 is not run: no restoration list is published.**

## Post-hoc diagnostics (after the gates; no decision weight; `tools/pe004_posthoc.py`, deterministic)
- **P1, where the errors come from.** All 37 wrong unique entry outputs and all 13 wrong unique total outputs are on
  the **23 of 45 tablets that do not balance** in any system. On the 22 balancing tablets there are no unique-but-wrong
  outputs, and no truth is a non-canonical notation.
- **P2, the upper bound.** Restricted to balancing tablets: entry precision 85/85 = 1.00 (CP95 low 0.965), recovery
  0.71 (34 of 119 tasks ambiguous across systems); total precision 8/8 (CP95 low 0.69), recovery 0.36 (14 of 22
  ambiguous). The solver and the canonical notation are not the problem. The problem is that **a damaged tablet cannot
  be checked for balance** (the missing slot absorbs any difference) and only about half of intact single-total tablets
  balance (22/45 here, 19/38 in PE001).
- **P3, why the baseline is strong.** 62 % of entry tasks hide a notation that occurs again on the same tablet (lists of
  `1(N01)`, `2(N01)`…), so the frequency guess is a hard baseline for entries.

## PE003 audit
PE003 stage 2 (seed 302) and post hoc (seed 305) re-run from the published tools in a scratch copy: **identical** to
the committed `analysis/pe003_results.json` and `analysis/pe003_posthoc.json` in every field except run time
(`analysis/pe004_pe003_audit.json`).

## What PE004 settles
- Grand-total arithmetic restores a missing numeral **exactly whenever the tablet balances** (P2), but blind to balance
  it is right only 70 % (entries) and 38 % (totals) of the times it gives a unique answer. That is below the
  pre-registered 0.80 bar, so **no restorations are proposed**. A negative, published as such.
- The next lever is not a better solver but a **balance predictor**: something observable on a damaged tablet that
  tells balancing from non-balancing tablets (e.g. mixed systems or commodities among the entries; PE001 saw that most
  non-balancing tablets have total < sum). It must be scored on intact tablets first (open line 6, reframed).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
