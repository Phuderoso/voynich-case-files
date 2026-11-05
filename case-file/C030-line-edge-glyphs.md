# C030 — The Edge of the Map (F-LINE step 1: glyphs at line edges vs the rest of their line)

*Expedition 30. **New approach family F-LINE** (the line as a unit), required by the one-in-three rule.*

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

Status: pre-registered in commit `c373c325` before any run on real or planted data (only a data-loading smoke test:
line counts ZL 3955, generator 1189, IT2a 3967). Run done (29 s, one run, seed 3030, log unchanged).
**Verdicts: line END effect DETECTED in Voynich (ZL and IT2a) and in the generator; line START effect DETECTED in the
generator, NOT TESTABLE in Voynich (calibration gate failed).**

## Question
Currier (1976) and later readers reported that Voynich lines behave as units: some glyphs prefer the start or end of
a line. Is that true under a calibrated null that keeps each line's own words, and does the Timm–Schinner
self-citation generator (whose rigidity and edge coupling we studied in C003–C011) reproduce it? The generator text
we use was produced line by line, so it has real line breaks to test.

## Data
- `data/ZL3b-n.txt` (ZL 3b): paragraph loci only (locus type starting with `P`); `<->` read as a word space;
  `[a:b]` → `a`; a line is dropped if any word contains a character outside `a–z` (unreadable) or it has < 3 words.
- `data/IT2a-n.txt` (Takahashi IT2a), same rules: **replication look**.
- `data/corpora/ts_generated_text.txt` (Timm–Schinner generator, authors' sample, 1,200 lines), lines with ≥ 3 words.
- Glyph units: `units()` from C003 (`cth ckh cph cfh ch sh` as single units).

## Metric
- **D_end** = Jensen–Shannon divergence (bits) between the last glyph unit of line-final words and the last unit of all
  other words of the same lines.
- **D_start** = same with the first unit of line-initial words; **paragraph-first lines excluded** (the known
  gallows-at-paragraph-start effect is not the line effect asked about).
- **Null:** word order shuffled within each line (the edge word becomes a uniformly random word of its own line),
  1,000 draws; p = (1 + #null ≥ observed) / 1,001. Effect size z = (D − null mean) / null sd.

## Gates (per text and statistic; 40 replicates each, 200 null draws per replicate)
- **Calibration:** re-lineate the text (all words concatenated, recut with the original sequence of line lengths
  from a random offset, so line breaks fall at arbitrary word boundaries). FPR at α must be ≤ 4/40.
- **Power:** on the re-lineated text, in 15 % of lines move one word whose edge unit is the text's 3rd most common
  edge unit to the line end (or start). Power ≥ 32/40.
- A failed gate makes that statistic **NOT TESTABLE** for that text.

## Decision rule
α = 0.025 per statistic (Bonferroni over the 2 statistics) within each text. **DETECTED** if p < α and both gates
pass. Main texts: ZL 3b and the generator; IT2a is a replication of ZL 3b (same rule).
- If Voynich is DETECTED and the generator is NOT DETECTED with gates passing, I will write "the generator sample does
  not reproduce the line-edge effect" (for this configuration only).
- Not a claim about meaning or about why lines differ; descriptive tables (edge units most over- and
  under-represented, observed vs expected counts) are reported but not tested.

Seed 3030. Tool: `tools/c030_line_edge_glyphs.py`. Output: `analysis/C030_results.json`.

## Results
`analysis/C030_results.json`. Null = 1,000 within-line shuffles, so p = 0.001 is the floor.

| Text | Lines | D_end (null mean) | z | Gates end (FPR / power) | End verdict | D_start (null mean) | z | Gates start (FPR / power) | Start verdict |
|---|---|---|---|---|---|---|---|---|---|
| Voynich ZL 3b | 3,955 (3,706 for start) | 0.086 (0.0015) | 224 | 1/40 / 40/40 | **DETECTED** p 0.001 | 0.197 (0.0024) | 347 | **6/40** / 40/40 | **NOT TESTABLE** |
| Timm–Schinner generator | 1,189 | 0.146 (0.0020) | 195 | 1/40 / 40/40 | **DETECTED** p 0.001 | 0.066 (0.0035) | 57 | 1/40 / 40/40 | **DETECTED** p 0.001 |
| Voynich IT2a (replication) | 3,967 (3,720) | 0.087 (0.0013) | 244 | 1/40 / 40/40 | **DETECTED** p 0.001 | 0.197 (0.0023) | 365 | **5/40** / 40/40 | **NOT TESTABLE** |

**Descriptive, not tested** (edge-word count observed vs expected under the within-line null, ZL 3b; IT2a is nearly
identical):
- Line end, Voynich: `m` 613 vs 104 (5.9×), `g` 85 vs 14 (6.1×), `d` 104 vs 66; fewer `r` (336 vs 579), `l` (440 vs 610),
  `o` (50 vs 135).
- Line end, generator: `m` 379 vs 83 (4.6×), `g` 36 vs 8 (4.6×); fewer `r` (144 vs 277) and `l` (132 vs 291). Same
  direction as the manuscript for every one of these units.
- Line start, Voynich (paragraph-first lines excluded): `y` 578 vs 196, `s` 394 vs 133, `p` 282 vs 44, `t` 326 vs 103,
  `d` 603 vs 371; fewer `ch` (127 vs 628), `a` (11 vs 171), `o` (516 vs 734), `sh` (187 vs 320).
- Line start, generator: `p` 89 vs 19, `k` 96 vs 37, `t` 49 vs 19, `f` 26 vs 6; but `y` 70 vs 69 and `d` 116 vs 144,
  `ch` 291 vs 318. The generator's line starts favour gallows, not the manuscript's `y-`, `s-` and `d-` starts, and it
  barely avoids `ch-`.

## Reading the result
- The line-end preference for `-m` and `-g` (known since Currier) survives a null that keeps every line's own words,
  in both transcriptions. The generator sample reproduces it with the same units, so a line-end effect by itself does
  not separate meaningful text from this kind of copying. Its D is even higher (0.146), but D is not comparable across
  texts of different size and alphabet; I make no "stronger/weaker" claim.
- The line-start question for the manuscript is **not testable** in this design, so I do not claim it here, even though
  z = 347 is enormous. **Why the gate failed (my hunch, to be checked):** re-lineating from a random word offset keeps
  the original sequence of line lengths, so many new line starts land exactly on old line starts; with a very strong real
  start effect, those coincidences leak into the calibration texts. The end statistic is weaker and passed.
- **Lead for C031:** the generator matches the manuscript's line *end* but not, descriptively, its line *start*
  profile (`y-`, `s-`, `d-` excess and strong `ch-`/`a-` avoidance). Repair: calibrate with cut points that never
  coincide with original line boundaries, then compare start profiles between manuscript and generator directly
  (e.g. JSD of the two edge-excess vectors against a generator-configuration spread).
- Not a claim about meaning, about why lines differ (layout, abbreviation, scribal habit), or about other generator
  configurations.

## Prior work and context
Currier (1976) on line-final `-m`/`-g` and lines as units; Nick Pelling's 4 Nov 2026 post on top-line
("Neal key") behaviour in Q20 ([Cipher Mysteries](https://ciphermysteries.com/2026/11/04/voynich-q20-neal-keys-update))
is about paragraph-first lines, which this cycle excluded from the start statistic.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
