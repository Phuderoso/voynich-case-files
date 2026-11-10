# C103 — Can the copying machine learn the rhythm? (F-RHYTHM step 2)

> *Caderno de campo.* Last night the manuscript's words were heard keeping step with their neighbours, and the default
> copying machine did not. Tonight we turn every dial on that machine that our C083 map allows, and we also cover one
> footprint we left behind: the short second word of the line.

**Status:** PRE-REGISTERED 2026-11-10 (~04:31 PT), before the registered run. Results will be appended below without
editing this registration.

**Disclosure.** A smoke run of the tool (`smoke` mode, 2 cells × 1 seed, R = 50, 2 gate replicates) printed H2 point
estimates for the manuscript before this registration (D ≈ +0.06…+0.08 with words 1–2 dropped). The decision rules
below are copied from C102 and C083 and were not changed after the smoke run; the registered run uses fresh seeds.
The audit line in the smoke run read "not exact" only because it used R = 50 instead of 2,000.

## Questions
- **H1 (main).** Does any configuration in the fixed C083 65-cell Timm–Schinner grid reproduce the manuscript's
  Currier-B adjacent interior word-length persistence D (C102: +0.076 IT2a, +0.084 ZL3b) while keeping the C004/C005
  surface statistics?
- **H2 (position control).** Does the persistence survive when word 2 (shorter on average: 4.55 vs ~4.8 units in IT2a B)
  is dropped as well?

## Data
ZL IVTFF 3b and Takahashi IT2a as in `data/MANIFEST.md` (same files as C102). C070 parser verbatim. Generator: Timm–Schinner
`text-generator.jar` (MIT; hash in MANIFEST), driven by `tools/c004_generator_sweep.py`.

## H1 — fixed generator grid
- Statistic D exactly as C102 (`tools/c102_word_length_rhythm.py`, imported).
- Grid = C083 grid unchanged: sourceChooser {page, random} × combine_split {30, 0} × add_remove {20, 60} × word-final
  substitutions {true, false} × canFollow {curveline, none} × initial line {default, f103r.1}, plus the C005 selected
  configuration (65 cells). 2,500 lines per run; lines ≥ 5 words.
- Training: every cell on seeds 11651–11655 (R = 200). Feasible = C083 surface rule (5-run mean of mwl, TTR, h2, R within
  ±15 % of the C005 reference, all runs usable).
- Selection: feasible cell with the **highest** mean training D = the generator's best shot.
- Grid multiplicity (Kryptos I-107): the report quotes the grid extremes (max over feasible cells of mean D and of single
  run D; also over all cells, descriptive), never a hand-picked cell.
- Confirmation: winner on 20 fresh seeds 11656–11675 (reference, R = 500), 10 held-out runs 11676–11685, 5 plant hosts
  11686–11690 (C102 POS plant at q = 0.10 on the host's own lines).
- Call per transcription: ABOVE if manuscript D > max(reference), INSIDE if within [min, max], BELOW if < min.
- **Decision:** both ABOVE → **ROBUST DEPARTURE (within this grid)**; both INSIDE and the reference runs still meet the
  surface rule → **REACHED**; both INSIDE but surface lost → REACHED ONLY WITH SURFACE LOSS; else NOT CALLED.
  No feasible cell → NOT TESTABLE.
- **Gates (fail → NOT TESTABLE):** G1 held-out runs outside [min, max] ≤ 2/10 (false-positive rate of the range rule);
  G2 plants ABOVE ≥ 4/5 (power); G3 reference usable ≥ 18/20.
- A ROBUST DEPARTURE says nothing about generator settings outside this grid.

## H2 — word 2 dropped
- Interior = positions 3..n−1, lines ≥ 6 words; within-line permutation null, R = 2,000, seed 11691; Holm over
  {A, B} × {IT2a, ZL3b}.
- Gates (seed 11692, 20 replicates each, RG = 300, q = 0.20 fixed from C102's design): FPR ≤ 2/20, NEG and POS power
  ≥ 16/20, broken-meter check (mean D NEG < 0 < mean D POS).
- Decision per language as C102: DETECTED-PERSISTENT / -ALTERNATING if both transcriptions reject at Holm 0.05 with the
  same sign; PARTIAL if one; NOT DETECTED if none; NOT TESTABLE if a gate fails.

## Audit of C102
Recompute C102 H1 (seed 11624, R = 2,000): the four D values must equal `analysis/C102_results.json` to 1e-12.

## Budget (Kryptos I-229: probe before registering)
Smoke probe: ~2 s per generator run with 8 workers; estimated registered run ≈ 4–5 min (325 training + 35 confirmation
runs, H2 gates ≈ 80 s). Hard cap `timeout 600`.

## Seeds
11651–11655 train · 11656–11675 reference · 11676–11685 held-out · 11686–11690 plants · 11691 H2 test · 11692 H2 gates.
Next free seed after this cycle: **11693**.

## Code
`tools/c103_rhythm_grid.py` (committed with this registration). Run:
`timeout 600 python tools/c103_rhythm_grid.py analysis/C103_results.json`

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

## Results (appended after the registered run, 2026-11-10 04:31:07–04:34:55 PT, 228 s; registration commit `188a819`)
Raw output: [`analysis/C103_results.json`](../analysis/C103_results.json), log [`analysis/C103_run_log.txt`](../analysis/C103_run_log.txt).

**Audit of C102: exact.** D recomputed to 1e-12: +0.054292 / +0.076389 (IT2a A/B), +0.067767 / +0.084362 (ZL3b A/B).

**H1 — training (65 cells × 5 seeds, all usable).** 12 cells feasible (surface within ±15 %).
Grid extremes: max mean D over feasible cells **+0.009**, max single-run D over feasible cells **+0.017**; over all 65
cells (surface not required, descriptive) max mean D +0.054, max single run +0.067. **No run in any cell reached the
manuscript's Currier-B D (+0.076 IT2a).**
Winner (highest feasible mean D) = cell 32: sourceChooser random, combine_split 30, add_remove 20, word-final
substitutions on, canFollow curveline, default initial line (mean D +0.009).

**H1 — confirmation (winner).** 20 reference runs: D from −0.006 to +0.033 (mean +0.010, sd 0.009); reference surface still
feasible. Gates: **G1 2/10** held-out outside the range (at the bar), **G2 5/5** plants ABOVE (plant D +0.073…+0.093),
**G3 20/20** usable — all pass.
Manuscript Currier B: IT2a +0.076, ZL3b +0.084, both **ABOVE** all 20 reference runs (about 7.7 and 8.6 reference sd above
the reference mean, descriptive).

**Verdict H1: ROBUST DEPARTURE (within this grid).** Inside the C083 grid, no setting that keeps the surface statistics
comes near the manuscript's word-length persistence. This applies only to this grid. Settings outside it were not tested.

**Descriptive lever (not registered).** The highest-D cells all have canFollow = none with combine_split 30 (cell 34:
mean +0.054, runs +0.041…+0.067). Those cells lose the surface (h2 ≈ 2.49–2.67 vs 2.25 reference, rigidity R ≈ 0.17–0.31 vs
0.49). So the copying machine *can* make lengths persist, but in this grid only by giving up other Voynich-like properties.
Even so, none of its runs reached +0.076.

**H2 — word 2 dropped too (R = 2,000, seed 11691, Holm over 4).** Gates pass in every subset (FPR 0–2/20, power 20/20 each
sign, broken meter OK).

| Subset | lines | pairs | D | z | Holm |
|---|---|---|---|---|---|
| IT2a A | 637 | 2,751 | **+0.061** | 4.2 | 0.002 |
| IT2a B | 2,013 | 11,879 | **+0.072** | 9.8 | 0.002 |
| ZL3b A | 663 | 3,128 | **+0.067** | 4.9 | 0.002 |
| ZL3b B | 1,988 | 11,945 | **+0.077** | 10.5 | 0.002 |

**Verdict H2: Currier A and B DETECTED-PERSISTENT** without word 2. The short second word does not carry C102's effect.
D barely moves (B: +0.076 → +0.072 IT2a, +0.084 → +0.077 ZL3b).

**Excluded / not testable.** Nothing was NOT TESTABLE. Excluded, within these limits: (i) "the word-2 dip makes the
rhythm", and (ii) "a surface-matched setting in the C083 grid reproduces it". Not excluded: other generator settings (for
example suggestions, same-position probability or line-length parameters), a verbose cipher, or a scribal or layout habit.

**Next (C104).** Options: (a) a wider random generator sweep (C004 S2-style, 120 configs) with the same winner/confirm
design; (b) a short/long runs test as a second metric; (c) whether the persistence holds *across* line breaks (last word
→ next line's word 2).

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
