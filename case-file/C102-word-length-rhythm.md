# C102 — Do neighbouring words keep the same length? (NEW FAMILY F-RHYTHM, step 1)

> *Caderno de campo.* Eleven expeditions have walked the same corridor of Quire 20. Tonight the map is turned over:
> instead of what a word *contains*, we listen to how long it is, and whether its neighbour answers in kind.

**Status:** PRE-REGISTERED 2026-11-10 (~00:50 PT), before any manuscript number of this statistic was computed.
Results will be appended below this registration without editing it.

## Why this question
Natural languages tend to alternate short (function) and long (content) words, so adjacent word lengths are often
negatively correlated. A copy-and-modify process (Timm & Schinner) copies a nearby word and changes a glyph, which could
make adjacent lengths *persist*. No earlier cycle (C001–C101; see the coverage table) measured the serial correlation of
word lengths inside a line. This is a new approach family, **F-RHYTHM**.

## Data
- ZL IVTFF 3b (13/05/2025), sha256 `bf5b6d4a…beccafc`; Takahashi IT2a (02/02/2023 mod. 25/06/2025), sha256 `7f27a8b0…3f536fb5`
  (`data/MANIFEST.md`). No image claim is made in this cycle.
- Lines: C070 parser verbatim (paragraph loci, no `<->` drawing break, every word `[a-z]+`, ≥ 5 words). Currier
  language from the page header `$L`.
- Word length = EVA glyph units (C003 `units()`: `ch sh cth ckh cph cfh` count as one).

## Hypothesis, metric, null
- **H1.** Within paragraph lines, adjacent interior word lengths are correlated (either sign).
- **Metric.** Interior words only (positions 2..n−1; the first and last word are excluded because line edges are known to
  be special). r = pooled Pearson correlation of (len_i, len_{i+1}) over all adjacent interior pairs.
- **Null (structure-preserving).** Interior words permuted within each line (each line's multiset of lengths, and so all
  line-to-line length heterogeneity, is kept). D = r − mean(null). Two-sided p = (1 + #|r* − m| ≥ |r − m|)/(R + 1), R = 2,000.
- **Tests:** {Currier A, Currier B} × {IT2a, ZL3b}, Holm over 4.
- **Decision rule per language:** DETECTED-ALTERNATING (D < 0) or DETECTED-PERSISTENT (D > 0) if both transcriptions
  reject at Holm 0.05 with the same sign; PARTIAL if one; NOT DETECTED if neither (gates passing); NOT TESTABLE if a gate fails.

## Planted controls and false-positive gate
- Pseudo replicate = the subset's real lines with interior words shuffled (true null).
- Plants, each line with probability q: **NEG** = interior reordered long/short alternately; **POS** = interior sorted by length.
- **Design (seed 11621):** q = smallest of {0.02, 0.05, 0.10, 0.20} giving p ≤ 0.05 with the correct sign in ≥ 9/10 design
  replicates for both plants in all four subsets (RG = 300 null draws). No q passing → NOT TESTABLE.
- **Gates (seed 11622, 20 fresh replicates per subset):** FPR p ≤ 0.05 in ≤ 2/20; power NEG and POS (correct sign) ≥ 16/20
  each; broken-meter check (Kryptos I-224): mean D of NEG replicates < 0 < mean D of POS replicates.

## H2 — generator reference (pre-registered reading)
Default Timm–Schinner configuration (MIT, hash in MANIFEST), seeds 11630–11649, 1,500 lines, lines ≥ 5 words, same
statistic (null R = 500). Manuscript Currier-B D (each transcription) INSIDE the [min, max] of the 20 generator D →
"generator-compatible on this statistic"; OUTSIDE → "generator-excluded on this statistic". Two-sided rank p
= min(1, 2·(1 + min(#gen ≤ D, #gen ≥ D))/(n + 1)) is reported.

## Descriptive (no verdict)
- Natural-language panel (letters as units): Latin (Caesar, Descartes), Italian (Dante), Spanish (Cervantes), Finnish
  (Kalevala, Kivi), Hebrew (Genesis, WLC). Running text cut into pseudo-lines whose word counts are drawn from the IT2a
  Currier-B line-length distribution (seed 11623), first 2,000 lines, lines ≥ 5 words.
- Full-line r (edges included) for the manuscript (R = 500).

## Seeds
11621 design · 11622 gates · 11623 chunking · 11624 test (+100 full-line, +200 generator nulls) · 11630–11649 generator.
Next free seed after this cycle: **11650**.

## Audit of C101
Recompute C101 H1 full ratio and T3 (Q20 top lines, p/f, top-3 pages removed) for both transcriptions; they must equal
the published 1.3447115589691347 / 1.2921060792569352 (IT2a) and 1.3047246173592428 / 1.2569236135333102 (ZL3b).

## Code
`tools/c102_word_length_rhythm.py` (committed with this registration). Run:
`timeout 600 python tools/c102_word_length_rhythm.py analysis/C102_results.json`

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
