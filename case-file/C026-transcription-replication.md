# C026 — Expedição 26: Does the bifolium trail survive a second map?

**Status:** pre-registered before any run (commit `d4274284`, with the tool); results appended below.
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

## Results (run after the pre-registration; `analysis/C026_results.json`, `analysis/C026_run_log.txt`, 11 s)

| Look | Text | Leaves | Units tested | Effect | ZL original | p | FPR at α | Power | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| IT_C023 | Takahashi IT2a | 102 | 24 cells, 24 conjugates | +0.068 | +0.070 (C023) | 0.00025 | 0/40 | 40/40 | **REPLICATED** |
| ZLpara_C023 | ZL 3b, paragraphs only | 99 | 24 cells, 24 conjugates | +0.070 | +0.070 (C023) | 0.00025 | 0/40 | 40/40 | **REPLICATED** |
| IT_C021B | Takahashi IT2a | 102 | 44 eligible conjugate pairs | +0.038 | +0.037 (C021 B) | 0.0082 | 0/40 | 40/40 | **REPLICATED** |

All three looks pass both gates and replicate at α = 0.0167, so by the pre-registered rule the bifolium finding is
**robust to transcription**: it does not depend on ZL's particular readings, and it is not carried by labels, rings
or rays. Effect sizes are almost identical to the originals.

**Limit (as pre-registered).** IT2a and ZL 3b read the same scans, so a reading convention shared by both could still
in principle create shared vocabulary between conjugate leaves. This audit excludes one transcriber's idiosyncrasies,
not common conventions. Nothing here concerns reading order or meaning.

## Post-hoc sensitivity: words split by drawings (not pre-registered; disclosed as such)
While checking news I found VCAT's ERRATA E-002 ([noah-chelednik/voynich-data](https://github.com/noah-chelednik/voynich-data/blob/main/ERRATA.md)):
deleting IVTFF markup with no separator fuses the words on either side of `<->` (text interrupted by a drawing).
**Our loader in `tools/c021_bifolium_vocab.py` has the same defect**, so C021, C022, C023 and C026 all read fused
words at drawing breaks (627 `<->` in ZL 3b, 662 in IT2a). `tools/c026_posthoc_drawing_breaks.py` reads `<->` as a word
space and reruns the looks with the same seed and gates (`analysis/C026_posthoc_drawing_breaks.json`, 15 s):

| Look | Effect, original loader | Effect, `<->` as space | p | FPR | Power | Verdict |
|---|---|---|---|---|---|---|
| ZL C023 (the C023 result itself) | +0.070 | +0.063 | 0.00025 | 0/40 | 40/40 | still detected |
| IT_C023 | +0.068 | +0.061 | 0.00025 | 0/40 | 39/40 | replicated |
| ZLpara_C023 | +0.070 | +0.064 | 0.00025 | 0/40 | 40/40 | replicated |
| IT_C021B | +0.038 | +0.036 | 0.0055 | 0/40 | 40/40 | replicated |

The defect shrinks the effects by about a tenth and changes no verdict. **Correction for C021–C023:** their effect
sizes were measured with fused words at drawing breaks; the corrected values for C023 are in the first row above.
Future cycles use `<->` as a word space.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
