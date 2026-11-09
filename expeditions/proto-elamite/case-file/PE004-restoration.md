# PE004 · Can the grand-total rule restore a damaged numeral, and how often is the answer unique?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration** (this file and `tools/pe004_restore.py`), committed and published before any
calibration number (recovery, precision, baseline, null) was computed.
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
