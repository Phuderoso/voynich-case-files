# C025 — Expedição 25: Do the transcribers disagree more on labels and ring text than on paragraphs?

**Status:** pre-registered before any run (commit `a1bb14e2`, with the tool); results appended below.
**Family:** F-TRX (transcription reliability), step 2. The family opened in C024.

## Question
C024 found that hand 4 (the astronomical and cosmological pages) has the highest disagreement between
the ZL 3b and Takahashi IT2a transcriptions (6.67 % against 1.3–2.8 %). That was only descriptive, and the
suspected cause is layout: text in circles, rays and labels rather than in paragraphs. C025 tests layout directly,
**inside each page**, so hand, scribe, language and illustration are held fixed by design.

## Data
- `data/ZL3b-n.txt` (ZL 3b, IVTFF) and `data/IT2a-n.txt` (Takahashi IT2a, IVTFF), as in C024 (see `data/MANIFEST.md`).
- Lines matched by locus id (page, line number). Locus type is taken from the ZL locus code: second
  character P = paragraph, L = label, C = circular, R = radial.
- Glyph text is cleaned exactly as in C024 (`tools/c024_common.py`).

## Hypotheses and looks (α = 0.05, Bonferroni over 2 looks, so 0.025 each)
- **Look L:** label lines disagree more per glyph than paragraph lines on the same page.
- **Look CR:** circular and radial lines together disagree more per glyph than paragraph lines on the same page.

## Statistic
For each page with at least one line of each compared type: (total edits ÷ total glyphs) on the non-paragraph
lines minus the same rate on the paragraph lines. The statistic D is the glyph-weighted mean of that difference
across the eligible pages (weight = glyphs on the non-paragraph lines). One-sided.

## Null
Locus-type labels are permuted among the compared lines **within each page** (4,000 permutations, seed 25025),
so the page, hand and transcribers are kept and only the link between layout and disagreement is broken.
p = (1 + #null ≥ observed) / (1 + 4,000).

## Gates (C024 lesson: power first)
- **Calibration:** 40 redraws where type labels are shuffled within page before testing. FPR at 0.025 must be ≤ 0.075.
- **Power:** planted extra disagreement on the non-paragraph lines (random glyph substitutions in the IT
  copy) at +1, +2 and +4 percentage points, 40 plants each. The **minimum detectable effect** is the smallest plant
  with detection ≥ 0.8. If no plant reaches 0.8, the look is **NOT TESTABLE**.
- **Decision:** a look is DETECTED if p < 0.025 and both gates pass; NOT DETECTED if p ≥ 0.025 and the gates
  pass (then effects at or above the minimum detectable effect are excluded); NOT TESTABLE if a gate fails.

## Caveats named in advance
- Short lines: a one-glyph disagreement on a four-glyph label is 25 %. Per-glyph rates are still unbiased for random
  errors, but label readings may also differ in segmentation. A detected effect means layout and disagreement go
  together; it does not say which transcriber is right. Only the Beinecke scans can settle a reading.
- ZL and IT do not always share line numbering; unmatched lines are dropped and counted in the results.

## Results (run after the pre-registration; `analysis/C025_results.json`, `analysis/C025_run_log.txt`, 46 s)

Matched ZL/IT line pairs and unmatched ZL lines are counted in the JSON.

| Look | Eligible pages | Non-paragraph lines | Paragraph lines | Pooled rate, non-paragraph | Pooled rate, paragraph | D (within page) | p | FPR at 0.025 | Power at +1 / +2 / +4 pp | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| L (labels) | 36 | 553 | 799 | 6.37 % | 1.92 % | +0.035 | 0.00025 | 0/40 | 1.00 / 1.00 / 1.00 | **DETECTED** |
| CR (circular + radial) | 10 | 83 | 81 | 5.99 % | 3.10 % | +0.030 | 0.0022 | 0/40 | 1.00 / 1.00 / 1.00 | **DETECTED** |

Both looks pass both gates (minimum detectable effect ≤ 1 pp) and are significant after Bonferroni.

**Reading.** On the same page, the two transcriptions disagree about three times as often on label text and about
twice as often on ring and ray text as on paragraph text. This is the layout effect C024 suspected for hand 4, now
tested inside pages, so hand, language and illustration cannot explain it.

**What it does not say.** It does not say which transcriber is right, nor whether the cause is the glyphs (labels are
often small, isolated or squeezed into drawings) or the conventions (how each transcriber reads unusual label forms).
Only the Beinecke scans can settle individual readings. It is also no surprise to anyone who has worked with these
files; what is new here is a within-page, controlled size of the effect.

**Practical consequence for statistics.** Label and ring text is the least reliable part of any single
transcription. Analyses that lean on labels (label-to-illustration matching, "plant name" readings, vocabulary of the
astronomical section) should check that their result holds in both ZL and IT before trusting it. C024's descriptive
hand-4 excess is very plausibly this layout effect.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
