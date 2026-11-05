# C033 — The Edge of the Map, fourth survey (F-LINE step 4: the generator's line starts across configurations)

*Expedition 33. Family F-LINE. Robustness check of C032 Look 2 before any outreach.*

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

Status: **pre-registered** in this commit, before any generation or run (seed 3333).

## Question
C032 found the manuscript's line-initial words start with `s`, `y` or `d` 2.25× as often as the within-line null
expects, while the Timm–Schinner generator's published sample does not (0.88×). Is that a property of the generator
method, or of that one sample?

## Texts (14, fixed now)
Generated with the authors' jar (`tsgen/text-generator.jar`, `tools/c004_generator_sweep.py::generate`):
- base configuration (`conf.properties`, as C004 S0), seeds 9001, 9002, 9003;
- C005's matched configuration (`analysis/C005_confirm.json` A.selected), seeds 9001–9003;
- the first 8 random configurations of the C004 sweep (`S2.*`, ok), seed 9001.
Lines with ≥ 3 words.

## Test (per text; as C032 Look 2)
Count of line-initial words whose first glyph unit is `s`, `y` or `d`; within-line shuffle null (1,000 draws);
one-sided p for enrichment; **α = 0.05 / 14 = 0.0036** (Bonferroni). Gates per text on whole-text-shuffled versions:
FPR ≤ 4/40, power ≥ 32/40 with 15 % of lines getting an `s`/`y`/`d` word moved to the start (500 null draws in gates).

## Decision rule
- **Gap holds across configurations** if no testable text is ENRICHED.
- **Gap does not hold** if at least one testable text is ENRICHED; I then report which configurations reproduce the
  manuscript's line starts.
- If more than half the texts are NOT TESTABLE: overall NOT TESTABLE.
- Ratios (observed/expected) are reported for all texts against the manuscript's 2.25 (descriptive).

## Results
*(pending)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
