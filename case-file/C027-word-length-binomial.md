# C027 — Expedição 27: The Binomial Bones

**Status:** pre-registered before any run (commit `7f3c1347`, with the tool); results appended below. **Verdict: NOT TESTABLE** (both gates failed; design defects found).
**Family:** **new family F-LEN (word-length morphology).** C024–C026 were all F-TRX, so this cycle opens a new family.

## Question
Jorge Stolfi observed that the lengths of distinct Voynich words follow a binomial distribution unusually closely,
with sharp cut-offs, unlike natural languages. This is often repeated but, to my knowledge (not verified exhaustively),
rarely tested against several natural-language controls with a calibrated test and planted controls. C027 asks:
**is the word-type length distribution of the Voynich text closer to its best-fitting binomial than that of each
natural-language control?**

## Data
- Voynich: `data/ZL3b-n.txt` (ZL 3b), all loci, read with `tools/c003_position_rigidity.py` (`voynich()`), with `<->`
  read as a word space (C026 correction). Length in glyph units (`cth ckh cph cfh ch sh` count as one, as in C003).
- Controls (`data/corpora/`, hashes in `data/MANIFEST.md`): Latin Caesar and Descartes, Italian Dante and Machiavelli,
  Spanish Cervantes, Hebrew Genesis and Exodus (consonantal), letters as units.
- Comparison look: the Timm–Schinner generator sample (`ts_generated_text.txt`), glyph units. It has fewer tokens than
  the window, so its windows wrap around (disclosed in advance).

## Metric
For a window of 10,000 consecutive tokens (random start, wrapping at the end), take the set of distinct words and
their lengths L. Fit L − 1 ~ Binomial(N, p) with p = mean(L − 1)/N for each N in 1–25 and keep the N with the smallest
total-variation distance (TV) between the empirical and binomial distributions. TV is the metric: smaller = more
binomial. 200 windows per corpus (seed 27027).

## Test and decision rule
- For each control c: p_c = (1 + #{b : TV_Voynich[b] ≥ TV_c[b]}) / (1 + 200), draws paired by index. One-sided.
- Holm correction over the 8 comparisons (7 natural languages + generator), family α = 0.05.
- **H1 CONFIRMED** if the gates pass and the Voynich text is closer than **every one** of the 7 natural-language
  controls after Holm. **NOT CONFIRMED** if the gates pass and any natural control is not beaten. **NOT TESTABLE** if a
  gate fails. The generator comparison is reported separately and does not enter H1.

## Gates (on the hardest step of Holm, α/8 = 0.00625; checked against Caesar)
- **Calibration (false positives):** 40 twins = the Voynich token stream with every word type given a random length
  drawn from Caesar's type lengths. A twin is not more binomial than Caesar, so "twin closer than Caesar" at p < 0.05
  must occur in ≤ 7.5 % of twins.
- **Power:** 40 twins whose type lengths are drawn half from Caesar's best binomial and half from Caesar's own
  lengths (a planted, partial binomial). Detection at α/8 must be ≥ 0.8.

## Caveats named in advance
- Glyph units are a choice: EVA splits some glyphs into several letters, and the "right" segmentation is unknown.
  A result holds for this unit system only.
- A binomial-like length distribution would say something about how words are built (for example, from slots of
  optional parts), not what they mean. It would be a structural fact, not a reading.

## Results (run after the pre-registration; `analysis/C027_results.json`, `analysis/C027_run_log.txt`, 15 s)

### Gates: both failed, so H1 is NOT TESTABLE
| Gate | Required | Observed |
|---|---|---|
| Calibration: twins "closer than Caesar" at p < 0.05 | ≤ 7.5 % | **42.5 %** |
| Power at α/8 = 0.00625 | ≥ 0.8 | **0.00** |

### Why (design defects, found after the run and published here)
1. **The power gate could not pass.** Twins used 100 window draws, so the smallest possible p was 1/101 = 0.0099,
   above the 0.00625 the gate required. With 200 draws the main comparisons also sit at the p-value floor
   (1/201; Holm × 8 = 0.0398 for every control), so the floor, not the data, set them.
2. **The calibration twin was not a fair null.** Twin type lengths were drawn independently from Caesar's whole
   vocabulary. A real 10,000-token window of Caesar has its own, topic-shaped vocabulary and fits a binomial worse
   than the whole book does (window mean TV 0.075 against 0.063 for all Caesar types). So the twins looked "more
   binomial" than Caesar's windows for a reason that has nothing to do with binomiality. TV also depends on how many
   types a window holds, which differs between corpora.

### Descriptive numbers (not a verdict, because the gates failed)
TV to the best binomial, mean over 200 windows of 10,000 tokens [2.5–97.5 % of windows], and on all types:

| Corpus | Tokens | Types | TV, windows | TV, all types (best N) |
|---|---|---|---|---|
| **Voynich ZL 3b** (glyph units) | 38,834 | 8,104 | **0.024** [0.015–0.038] | 0.023 (N 10) |
| Spanish, Cervantes | 383,633 | 22,470 | 0.046 [0.035–0.057] | 0.023 (N 22) |
| Generator, Timm–Schinner | 10,832 | 2,228 | 0.050 [0.047–0.056] | 0.050 (N 8) |
| Italian, Dante | 102,005 | 12,669 | 0.057 [0.039–0.075] | 0.042 (N 19) |
| Latin, Caesar | 20,547 | 5,687 | 0.075 [0.069–0.080] | 0.063 (N 25) |
| Italian, Machiavelli | 29,883 | 4,795 | 0.078 [0.070–0.087] | 0.060 (N 25) |
| Hebrew, Genesis | 20,629 | 5,007 | 0.079 [0.073–0.086] | 0.078 (N 6) |
| Hebrew, Exodus | 16,726 | 4,170 | 0.079 [0.070–0.087] | 0.077 (N 6) |
| Latin, Descartes | 20,834 | 4,825 | 0.094 [0.068–0.119] | 0.088 (N 25) |

In 10,000-token windows the Voynich text has the lowest TV of all nine corpora, as Stolfi's observation leads one
to expect. But the whole-vocabulary column already shows the trap: Cervantes, with 22,470 types, reaches the same
TV (0.023) as the Voynich text. Sample size and window composition move TV as much as language does. Until a fair
null is in place, **no claim** that the Voynich text is "more binomial" than natural language is made here.

### Prior work found after the run (news check)
The exact Binomial(9, ½) + 1 fit was already tested and rejected by goodness-of-fit tests in 2003
([voynich.net archive](http://www.voynich.net/Arch/2003/11/msg00138.html)). Stolfi later reported binomial-like lengths in
East Asian monosyllabic languages ([chinese-redux](https://www.voynich.nu/hist/stolfi/chinese-redux.html)). C027 asks a
different, comparative question ("closer than each control"), but its control set has no such language, which limits
any future positive result.

### Repair for C028 (proposal, to be pre-registered there)
- Compare at an **equal number of types** (for example 1,500 distinct words drawn per window) so sample size cannot
  move TV.
- **Calibration by self-comparison:** each control against independent windows of itself must give "closer" at
  p < α in about α of cases.
- **Power by planting into the control's own stream:** give a fraction of a control's word types binomial lengths
  and require detection.
- 2,000 draws per comparison so the p-value floor (1/2,001) sits well under the strictest Holm step.
