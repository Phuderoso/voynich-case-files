# C031 — The Edge of the Map, second survey (F-LINE step 2: line starts with a repaired calibration)

*Expedition 31. Family F-LINE. Repairs the calibration that made C030's manuscript line-start test NOT TESTABLE.*

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

Status: **pre-registered** in this commit, before any run of the repaired gates or of the statistics with seed 3131.

## Why a repair
C030's calibration re-lineated the text by recutting the word stream with the original line-length sequence from a
random offset. Many new line starts then fall on old line starts, so a strong real start effect leaks into texts that
should have none (FPR 6/40 on ZL 3b, 5/40 on IT2a). This was a hunch in C030; the repair below removes the possibility
by construction, so if the gate still fails, the hunch was wrong.

## Change (only this)
**Calibration and power texts:** every original line is cut at a uniformly random interior word (position 1..n−1); each
new line = tail of old line *i* + head of old line *i*+1 (kept if ≥ 3 words). No new line edge coincides with an old one.
Everything else is C030 unchanged and imported from `tools/c030_line_edge_glyphs.py`: data rules, glyph units, D_end and
D_start (paragraph-first lines excluded from D_start), within-line shuffle null (1,000 draws), FPR ≤ 4/40, planted moves
of the 3rd most common edge unit in 15 % of lines with power ≥ 32/40, α = 0.025 per statistic, texts ZL 3b, the
Timm–Schinner generator sample, and IT2a as replication.

## Decision rule
As C030: **DETECTED** if p < 0.025 and both gates pass; a failed gate is **NOT TESTABLE**. The C030 end verdicts are
re-checked under the new calibration; if any end gate now fails, that is reported as a C030 correction.

## Descriptive only (not tested)
Per glyph unit seen ≥ 20 expected times in both texts: log lift = log((observed edge count + 0.5) / expected under the
within-line null), manuscript ZL 3b vs generator, Spearman correlation, for starts and ends. No p-value is claimed:
units are not independent and there is no calibrated null for this comparison yet.

Seed 3131. Tool: `tools/c031_line_start_repaired.py`. Output: `analysis/C031_results.json`.

## Results
*(pending)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
