# C039 — Measuring the Gaps with a Ruler (F-SEG step 4: ZL commas on the Beinecke scans)

*Expedition 39. Family F-SEG step 4. First cycle that measures the vellum images, not a transcription.*

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

Status: pre-registered in this commit before any test run (seed 3939); results added after.

## Question
C035 found ZL's commas (uncertain spaces) behave as half-boundaries on a glyph-context score. C036 found Takahashi
writes a space at 65% of them. Both are transcriptions. On the **images**, is the ink gap at a ZL comma as wide as
at a certain space, as narrow as a within-word join, or in between? Does gap width at a comma track the C035 Harris
score and Takahashi's space/no-space choice?

## Data and method (numpy + PIL, `tools/c039_comma_gap_widths.py`)
- Pages fixed in advance (text-only or star pages with many commas): **f58r** (`115_f58r.jpg`), **f58v**
  (`116_f58v.jpg`), **f111r** (`195_f111r.jpg`), **f113v** (`200_f113v.jpg`) from `/workspace/voynich/scans/`
  (Beinecke JPGs, ~2,600–3,000 × 3,700 px). Text boxes (x0, x1, y0, y1) were set from thumbnails and are in the tool.
- Ink mask: pixel darker than its 25-px Gaussian background by > 30 grey levels.
- Lines: profile peaks (min spacing 45 px) in a 320-px seed strip at the left of the text box, traced rightward in
  150-px strips (nearest peak within 22 px). The core band is −14..+10 px around the trace. The line runs from the
  first sustained ink to the first blank run ≥ 60 px.
- Traces are matched to ZL lines (all lines of the folio, in order) by a monotone DP on run count and length.
  A matched ZL paragraph line is used only if it is a C036-parsable line and passes a gate that is symmetric in
  commas: detected blank runs ≥ 10 px within [spaces − 1, spaces + commas + 1], and length within 25% of the
  glyph-weight prediction.
- Glyph weights (fixed): ch/sh 1.6, 3-char units 2.0, gallows 1.4, i 0.5, e 0.8, others 1.0.
- Anchors: ZL **certain spaces** are matched to blank runs by a monotone DP (score = run width − 0.1·|offset|).
  Every boundary (space, comma, within-word join) gets an expected x by interpolation in weight space between the
  nearest anchors. A space being measured has its own anchor removed (leave-one-out), so spaces are not wide by
  construction. Commas are never anchors.
- **Width** = full length of the longest blank band-run touching expected x ± 0.6 glyph width, capped at 60 px.

## Tests (α = 0.05/2 = 0.025 for A and B)
- **A**: mean width at commas minus mean width at within-word joins. Null: 2,000 relabellings of commas within
  commas ∪ joins, keeping each line's comma count. One-sided.
- **B**: mean width at spaces minus mean width at commas. Same stratified null within spaces ∪ commas. One-sided.
- Sanity (reported, not a gate): spaces vs joins.

## Gates (40 replicates, 200-draw nulls; label-level planted controls on the measured widths, as in C036)
- FPR A: fake commas drawn from joins. FPR B: fake commas drawn from spaces.
- Power A and B: fake commas, half from spaces and half from joins (a planted "half" gap), per-line counts kept.
- Required: FPR ≤ 4/40 and power ≥ 32/40, else **NOT TESTABLE**.

## Decision rule
- A and B: **HALF** (commas sit at intermediate gaps on the vellum).
- Only A: SPACE-LIKE. Only B: NON-GAP-LIKE. Neither: UNRESOLVED.
- **Look 2** (secondary, each α = 0.025, reported whether gates pass or not): Spearman ρ between comma width and the
  C035 Harris score (k = 2, whole ZL stream), one-sided > 0. Also the AUC of comma width for commas IT2a spaces vs
  commas it does not, on identical-glyph loci, one-sided > 0.5. Nulls: 2,000 permutations.

## Disclosure before running
While building the tool I ran a prototype on f58r once, using plain proportional alignment with no anchors. Spaces
did not separate from joins (mean blank run 10.5 vs 10.9 px; commas 11.7 px, n = 14). So I rejected that method and
added the anchor step. I also ran a geometry-only dry run with no widths or tests: traces/ZL lines/DP matches were
f58r 44/41/27, f58v 42/39/24, f111r 54/54/34, f113v 49/49/26. Nothing else was looked at.

## Limits
Four pages only. Alignment comes from line geometry and glyph weights, not glyph recognition, so misplaced expected
positions add noise to every class equally. The gates measure whether that noise still leaves the test able to see a
planted half-gap. Width is a horizontal blank run in a fixed band. It ignores slant and tails that cross gaps.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

## Run 1 (as pre-registered, commit 3f4d93b4): NOT TESTABLE
The line gate accepted only **9 lines** (f58r 2, f58v 0, f111r 3, f113v 4 of 111 DP matches). That gave 67 spaces,
16 commas and 296 joins. Gates: FPR A 0/40, FPR B 0/40, **power A 18/40, power B 6/40**, so the gates **failed** and
the verdict is **NOT TESTABLE**. Descriptive only: mean width spaces 19.4 px, commas 13.7, joins 6.7. The sanity
check (spaces vs joins, +12.7 px, p 0.002) shows the anchor alignment sees real gaps. Look 2 (n = 16): Harris ρ −0.10
(p 0.63), IT2a AUC 0.48 (p 0.56). `analysis/C039_results_run1.json`.

## Amendment 1 (pushed before run 2)
Cause: the run-count clause. Blank runs ≥ 10 px include within-word joins (8% of joins are ≥ 15 px), so the detected
count overshoots spaces + commas + 1 on most lines. **Change: drop the run-count clause and keep the length clause**
(within 25%). A geometry-only count gives 97 accepted lines (26/20/32/19). Nothing else changes: method, tests, α,
gates and decision rule are the same. Run 1 is kept as is (env `C039_RUN_GATE=1` reproduces it). The amendment was
made after seeing run 1, and I say so here. Its risk is that more lines are misassigned, which adds noise to every
class equally. The FPR and power gates still decide whether the run is testable.
