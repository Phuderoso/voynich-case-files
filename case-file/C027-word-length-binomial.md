# C027 — Expedição 27: The Binomial Bones

**Status:** pre-registered before any run (this file is committed with the tool before results exist).
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

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
