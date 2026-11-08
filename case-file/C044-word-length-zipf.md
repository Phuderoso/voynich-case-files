# C044 — Expedição 44: a régua do comprimento das palavras (word-length dispersion and Zipf slope)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** F-ZIPF step 1 — **new approach family** (C041–C043 were F-ENT; the one-in-three rule requires a new family now). Listed in README "Not yet covered" as "Zipf and word-length profiles".

## Question
Is the spread of Voynich word lengths unusually narrow compared with natural-language texts at matched length (a long-standing observation, e.g. Stolfi's binomial-like word-length distribution and Reddy & Knight 2011), and is the Zipf rank-frequency slope inside or outside the natural range? Where do the Timm–Schinner generator samples sit?

## Pre-registration (written and pushed before any Voynich or generator number is computed)
- **Data (reuse C041–C043 exactly):** ZL 3b (`data/ZL3b-n.txt`) and Takahashi IT2a (`data/IT2a-n.txt`) paragraph words via `c030.ivtff_paragraphs` (commas as word spaces, folio order); 7 natural texts (Caesar, Descartes, Dante, Machiavelli, Cervantes, Genesis, Exodus; `c003.gutenberg` / `c003.hebrew`); generators `Generator_base` (published sample, 10,810 tokens, shorter than N, disclosed) and `Generator_C005matched` (jar, 2,400 lines, seed 4444; skipped and disclosed if unavailable).
- **Length:** first **N = 15,000 word tokens** of each text (Exodus has 16,726, so all natural texts reach N).
- **Tokenization:** Voynich and generators in **EVA glyph units** (`c003.units`: `cth ckh cph cfh ch sh` one unit); natural texts in letters. Descriptive secondary: Voynich in raw EVA characters (no verdict).
- **Metrics:** word-length coefficient of variation **CV = sd/mean** (H1); **Zipf slope** = least-squares slope of log10 frequency on log10 rank over ranks 1–500 (H2). Also reported: mean, sd, skew, length histogram, types.
- **Uncertainty:** token-block bootstrap, 20 contiguous blocks, 200 resamples, 95% percentile CI.
- **Calls:** H1 *low* if CV < natural minimum **and** CI upper < natural minimum (one-sided, direction fixed by the literature). H2 *outside* if the whole CI lies below the natural minimum or above the natural maximum (two-sided).
- **Gates (seed 4444, run and printed before any Voynich number):**
  - FPR: for each natural text, 6 random N-token windows called against the range of the **other six** (leave-one-out) → 42 trials; pass if ≤ 4/42 for each hypothesis.
  - Power H1: 40 Dante windows, letters re-cut into words whose lengths are drawn from a normal with the same mean and **half** the sd; must be called low vs the all-seven minimum in ≥ 32/40.
  - Power H2: 40 Dante windows with each token replaced, with probability 0.5, by a uniformly random type from the window (flatter Zipf); must be called outside in ≥ 32/40.
  - A failed gate makes that hypothesis **NOT TESTABLE** (no verdict).
- **Decision rule:** UNUSUALLY LOW (H1) / OUTSIDE NATURAL (H2) only if both ZL and IT2a are called; INSIDE NATURAL if neither is called and both point estimates are inside the range; SPLIT if they disagree; otherwise NOT CALLED. Generators are descriptive and do not decide H1/H2.
- **Multiple comparisons:** two hypotheses, each requiring replication in two transcriptions; no other looks are confirmatory.
- **Caveat fixed in advance:** EVA units vs letters are not the same kind of unit; a CV is scale-free but still depends on how a script cuts glyphs. A low CV would describe the writing system, not meaning.
- **Tool:** `tools/c044_word_length_zipf.py` → `analysis/C044_results.json`. Run: `timeout 600 python3 tools/c044_word_length_zipf.py`.

## Results
*(to be filled after the run)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
