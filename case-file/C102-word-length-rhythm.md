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

## Results (appended after the registered run, 2026-11-10 00:36:04–00:41:53 PT, 349 s; registration commit `e20077e`)
Raw output: [`analysis/C102_results.json`](../analysis/C102_results.json), log [`analysis/C102_run_log.txt`](../analysis/C102_run_log.txt).

**Sizes.** Interior adjacent pairs: IT2a A 3,706 (796 lines), IT2a B 14,136 (2,135), ZL3b A 4,117 (826), ZL3b B 14,167 (2,105).

**Design and gates.** The design rule picked **q = 0.20** (q 0.02, 0.05 and 0.10 each failed in at least one Currier-A
subset, e.g. q 0.10 NEG 8/10). Gates at q 0.20, seed 11622, all pass:

| Subset | FPR | NEG power | POS power | mean D NEG / POS |
|---|---|---|---|---|
| IT2a A | 1/20 | 20/20 | 20/20 | −0.089 / +0.107 |
| IT2a B | 0/20 | 20/20 | 20/20 | −0.102 / +0.127 |
| ZL3b A | 1/20 | 20/20 | 20/20 | −0.091 / +0.109 |
| ZL3b B | 2/20 | 20/20 | 20/20 | −0.105 / +0.129 |

Broken-meter check passes: the plants move D in opposite directions in every subset.

**H1 (R = 2,000, seed 11624, Holm over 4).**

| Subset | r | null mean | D | z | p | Holm |
|---|---|---|---|---|---|---|
| IT2a A | 0.124 | 0.070 | **+0.054** | 4.3 | 0.0005 (floor) | 0.002 |
| IT2a B | 0.149 | 0.073 | **+0.076** | 11.1 | 0.0005 (floor) | 0.002 |
| ZL3b A | 0.150 | 0.083 | **+0.068** | 5.4 | 0.0005 (floor) | 0.002 |
| ZL3b B | 0.157 | 0.072 | **+0.084** | 12.3 | 0.0005 (floor) | 0.002 |

**Verdict H1: Currier A DETECTED-PERSISTENT; Currier B DETECTED-PERSISTENT.** Inside a line, a word tends to be about as
long as its neighbour, more than the line's own length mix predicts. The effect is small in correlation units (about
+0.05 to +0.08) but far outside the null. Full lines (edges kept, R = 500): D +0.048 / +0.081 (IT2a A/B), +0.061 / +0.087 (ZL3b A/B).

**H2 (generator reference, 20 default Timm–Schinner runs, seeds 11630–11649).** Generator D ranges from −0.019 to
+0.010 (mean −0.005). Manuscript Currier B D = +0.076 (IT2a) and +0.084 (ZL3b) lie **above all 20 runs**, so the reading is
**generator-excluded on this statistic, default configuration only.** The rank p is 0.095 for both, which is the floor
with 20 runs, so this reading rests on the registered range rule and not on a small p. Parameter settings other than the
default were not tested.

**Descriptive natural-language panel (letters; D, z).** Latin Caesar +0.018 (2.5), Latin Descartes −0.019 (−2.4),
Italian Dante −0.099 (−12.6), Spanish Cervantes −0.170 (−22.1), Finnish Kalevala +0.022 (3.1), Finnish Kivi −0.029 (−3.7),
Hebrew Genesis −0.027 (−3.7). Most of these texts *alternate*. The two that persist do it at a quarter of the manuscript's
strength. The panel is descriptive: its pseudo-lines are cut from running text, so they carry no real line structure.

**Post hoc (not registered, descriptive only; `tools/c102_posthoc.py`, seed 11650, R = 200).**
- (a) Identical adjacent words are rare (53–151 per subset). Dropping them leaves D unchanged (+0.054 / +0.078 / +0.071 /
  +0.087), so the persistence is **not** carried by reduplication (C052's R0).
- (b) Mean interior word length by position is flat from word 3 on (B ≈ 4.7–4.8 units), with a dip at word 2 (4.55 in
  IT2a B). A drift along the line would also make adjacent lengths persist. The flat profile argues against that, but the
  word-2 dip is not controlled here.

**What is excluded / not testable.** No subset was NOT TESTABLE. Nothing is *excluded* about meaning. The result is a
structural property, and it is open to more than one account: a copy-and-modify process with settings other than the
default, a verbose cipher whose units come in runs of similar length, or a scribal or layout habit.

**Audit of C101.** H1 full ratio and T3 recomputed exactly: IT2a 1.3447115589691347 / 1.2921060792569352 (dropped f104r,
f105r, f106v); ZL3b 1.3047246173592428 / 1.2569236135333102 (dropped f104r, f106r, f114r). **Exact, no correction needed.**

**Next (C103, F-RHYTHM step 2).**
1. A position-stratified null: shuffle only among words at the same distance from the line start, or drop word 2 as well.
2. The C083 65-cell generator grid on D, to see whether any setting reaches +0.08.
3. Optionally a length-class (short/long) runs test as a second metric.

Seeds from 11651 (11650 used post hoc).

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
