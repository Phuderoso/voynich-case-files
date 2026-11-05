# C006 — Expedição 6: Footprints Across the Line. Do line-bound word pairs and word-edge coupling separate the copying machine from the verbose cipher?

**Status:** pre-registered 2026-11-04 23:30 PT, before any run. Results appended below.
**Approach family:** line-level co-occurrence and word-boundary coupling with within-text permutation nulls, applied to
the candidate processes matched in C005. New to the coverage table (C001–C005 used vocabulary-vs-labels and
within-word position). Metric ideas follow Zhang & Sheng (arXiv 2610.34499, same-line word pairs) and the
word-edge coupling literature (Rozanova & Temerev, arXiv 2608.17096; OSF bc5zr); **implementations are mine**, not
their code, so numbers are not directly comparable with theirs.

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Question
C005 showed that glyph-position rigidity cannot separate a self-citation generator from a verbose cipher with
positional symbols: both reach the manuscript's value. Do two line-level statistics do better?

## Texts (each measured on 20 samples of consecutive lines totalling ≥ 6,000 words, random start, seed 66)
- **V**: Voynich, ZL 3b, commas split (C003 tokenisation; one transcription line = one line).
- **G\***: C005's matched generator configuration (seeds 6001–6010, concatenated in seed order).
- **G0**: generator default configuration (seeds 1–10).
- **VF-LA / VF-IT**: C005's VC-F verbose cipher (final-only symbols) of Caesar / Dante, C005 code tables (seed 5005);
  lines = the Gutenberg text lines.
- **LA / IT**: plain Caesar / Dante (natural-language reference).

## Metrics
- **M1 line-pair excess** P: the number of distinct unordered word-type pairs (both words of ≥ 2 glyph units, the two
  words different) that co-occur within **≥ 2 different lines**, divided by the mean of the same count over 50
  permutations that shuffle words across all lines of the sample while keeping each line's length. P = 1: no
  line-bound pairing; P > 1: pairs recur together on lines more than chance.
- **M2 word-edge coupling** C: mutual information (bits) between the last glyph unit of a word and the first glyph unit
  of the next word in the same line, minus its mean over 50 permutations that shuffle word order **within each line**.
  C = 0: no coupling beyond what the line's word inventory implies.
- Report the mean and 99 % interval (0.5–99.5 percentiles) over the 20 samples.

## Controls (must pass before any verdict)
- **False-positive calibration:** for V and LA, 40 replicates where the sample is first permuted by the M1 (or M2) null
  itself; the metric must call it "above null" (z > 2.58 against its own 50 permutations) in ≤ 5 % of replicates.
- **Planted M1:** V with lines shuffled across (null text), then the word pair `xa xb` (two invented words) planted into
  60 random lines: P must exceed the unplanted null text's 99 % upper bound.
- **Planted M2:** V with word order shuffled within lines, then in 30 % of adjacent pairs where the left word ends in
  `y`, the right word's first glyph is replaced by `q` (an initial-only glyph): C must exceed the unplanted shuffled
  text's 99 % upper bound.

## Decision rules (2 metrics × 4 candidates G\*, G0, VF-LA, VF-IT = 8 looks; 99 % intervals are the correction)
- A candidate is **consistent with V on a metric** if its 99 % interval overlaps V's; otherwise "differs" (direction
  stated).
- **Separation:** the two metrics "separate copying from verbose cipher" if G\* and at least one VF text get different
  consistency calls on at least one metric.
- LA and IT are descriptive references, not looks.
- If a control fails, no verdict on the affected metric ("not testable this cycle").

## Budget
≤ ~8 min; per-text results cached in `analysis/C006_results.json` (resumable).

---

## Results (run 2026-11-04, ~2 min 44 s; `tools/c006_line_pairs_edges.py`, output `analysis/C006_results.json`)

Mean and 99 % interval over 20 samples of ≥ 6,000 words.

| Text | M1 line-pair excess P | M2 word-edge coupling C (bits) |
|---|---|---|
| V (Voynich, ZL 3b) | 1.031 [0.911, 1.134] | **0.204 [0.145, 0.281]** |
| G\* (matched generator) | 1.277 [1.018, 1.575] | 0.001 [−0.002, 0.004] |
| G0 (default generator) | 1.006 [0.951, 1.047] | 0.012 [0.005, 0.018] |
| VF-LA (verbose cipher, Caesar) | 1.291 [1.248, 1.342] | 0.008 [0.005, 0.012] |
| VF-IT (verbose cipher, Dante) | 1.150 [1.110, 1.189] | 0.027 [0.019, 0.038] |
| LA (Caesar, reference) | 1.287 [1.238, 1.333] | 0.038 [0.030, 0.045] |
| IT (Dante, reference) | 1.189 [1.142, 1.276] | 0.148 [0.129, 0.172] |

### Controls
- **False positives:** M1 0/40 (V) and 0/40 (LA); M2 1/40 (V, 2.5 %) and 0/40 (LA). Both within the ≤ 5 % rule.
- **Planted M1: FAILED.** Planting `xa xb` in 60 lines did not move P (0.992 [0.928, 1.045] vs. unplanted
  1.000 [0.935, 1.052]). The reason is a design flaw I should have caught: P counts *distinct* recurring pairs, so one
  planted pair adds one to a count of hundreds. M1 cannot detect a single strong pair; it only detects many weak ones.
  → **M1 is "not testable this cycle"**; its looks below are void. (The descriptive numbers are kept: V sits near 1
  while both natural texts sit near 1.2–1.3, which agrees in direction with Zhang & Sheng's "half the strength of the
  weakest language", but this cycle does not establish it.)
- **Planted M2: passed.** Rewriting 30 % of `-y` + next word into `q-` lifted C from −0.000 [−0.007, 0.006] to
  0.072 [0.053, 0.101].

### Looks (M2 only; 4 looks)
| Candidate | M2 call |
|---|---|
| G\* | differs (lower) |
| G0 | differs (lower) |
| VF-LA | differs (lower) |
| VF-IT | differs (lower) |

**Separation rule:** not met. On M2 the generator and both verbose ciphers get the *same* call: all fall far below
the manuscript. M2 does not separate copying from verbose cipher; it rejects both **as configured here**.

### Post-hoc robustness (declared after the main run; not looks) — `tools/c006_robustness.py`
| Variant | C (bits) |
|---|---|
| commas kept inside words | 0.168 [0.116, 0.243] |
| Currier A only | 0.139 [0.130, 0.151] |
| Currier B only | 0.249 [0.214, 0.286] |

Coupling survives the comma convention and both dialects, so it is not an artefact of splitting uncertain spaces.
The largest contributions (descriptive): `-y` → `q-` (3,488 pairs, 1.8× independence), `-r` → `a-` (3.0×),
`-s` → `a-` (4.8×), `-o` → `l-` (4.1×), `-n` → `o-`/`ch-`. Some of these (`-r a-`, `-o l-`) look like spaces that may
not be word breaks at all (compare Rozanova & Temerev); that reading is a hypothesis, not tested here.

## What this means
- **Established (replication):** Voynich words are strongly coupled across the space within a line
  (C ≈ 0.2 bits, above even Dante's 0.15 and five times Caesar's). This is a known result (Currier 1976; Smith & Ponzi
  2019; Rozanova & Temerev 2026; OSF bc5zr replication, 2026-11-01); my independent reimplementation agrees.
- **New here:** the generator configuration that C005 matched to the manuscript on rigidity, word length, vocabulary and
  h2 produces **no** edge coupling (0.001 bits), and neither does the default generator or the final-symbol verbose
  cipher. Matching four statistics did not buy the fifth.
- **Not excluded:** a copying process or a verbose cipher *with an added cross-word rule* (e.g. a scribe adjusting the
  next word's opening to the last word's ending). Both families remain open; these specific configurations are excluded
  on M2.
- **Not testable:** line-bound word pairs (M1), because the planted control failed.

## Next
Fix M1 (count pair-line co-occurrences weighted by recurrence, or test planted pairs at the level of total excess, and
re-plant), and ask whether the Timm–Schinner generator can be given a cross-word rule that reproduces C without losing
the C005 match.

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
