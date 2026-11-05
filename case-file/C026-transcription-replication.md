# C026 — Expedição 26: Does the bifolium trail survive a second map?

**Status:** pre-registered before any run (this file is committed with the tool before results exist).
**Family:** F-TRX (transcription reliability), step 3: an audit of earlier positive findings.

## Question
C021 (Look B) and C023 found that the two leaves of a bifolium share more vocabulary than other leaf pairs of the
same quire, even with hand, language, illustration and bound distance held fixed. Both used only the ZL 3b
transcription. C025 then showed that labels, rings and rays are where transcribers disagree most. A finding that
depends on one transcriber's readings, or on the least reliable text, should not be trusted. C026 reruns both tests,
unchanged, on different text.

## Data
- `data/IT2a-n.txt` (Takahashi IT2a, IVTFF, with its own page headers for quire, bifolio, hand, language, illustration).
- `data/ZL3b-n.txt` restricted to paragraph loci (locus type P) only.
- Words, vocabulary rule (≥ 5 tokens), leaves (≥ 20 words), similarity, nulls, redraw and plant are reused unchanged
  from `tools/c021_bifolium_vocab.py` and `tools/c023_distance_null.py`.

## Looks (α = 0.05 / 3 = 0.0167 each, one-sided)
1. **IT_C023:** the C023 distance-preserving test on IT2a.
2. **ZLpara_C023:** the C023 test on ZL 3b paragraphs only.
3. **IT_C021B:** the C021 Look B test (hand × language × illustration strata, random re-pairing null) on IT2a.

## Gates (per look, as in C021/C023)
- Calibration: 40 destroyed corpora (leaf words redrawn from the hand × language × illustration pool); FPR at α ≤ 0.075.
- Power: 40 planted corpora (20 % of one conjugate leaf's words taken from its partner); detection ≥ 0.8.

## Decision rule
- REPLICATED: gates pass and p ≤ 0.0167.
- NOT REPLICATED: gates pass and p > 0.0167. That would weaken C021/C023 and be published as a correction.
- NOT TESTABLE: a gate fails.
- The bifolium finding is called **robust to transcription** only if all three looks replicate. Effect sizes are
  reported next to the ZL originals (C021 B: +0.037; C023: +0.070) but are not part of the decision.

## Caveats named in advance
- IT2a and ZL 3b are not independent: both read the same scans, and the bifolium finding concerns shared vocabulary,
  which shared misreadings could in principle create. Replication here rules out one transcriber's idiosyncrasies,
  not a reading convention common to both.
- The tests are about the sheet as the working unit. Nothing here bears on reading order or meaning.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
