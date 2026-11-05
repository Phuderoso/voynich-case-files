# C041 — Expedição 41: a entropia do próximo glifo (conditional glyph entropy h2)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** F-ENT (new family: glyph-level entropy). C038–C040 were all continuations (F-MI, F-SEG, F-SEG), so this cycle opens a new family, as the one-in-three rule requires. It is the first item under "Not yet covered" in the README.

## Question
Given one glyph, how predictable is the next one? We measure this with h2 = H(X_{i+1} | X_i). Is the Voynich h2 below the range of 7 natural-language texts, at the same sample length? Where does the Timm–Schinner self-citation generator sit?

Lindemann & Bowern (arXiv 2010.14697) and Rozanova & Temerev (arXiv 2608.17096, h2 ≈ 2.7 for Voynich vs ≈ 3.5 for Latin) report a low Voynich h2. We don't just repeat their number. This cycle adds our own controls: matched N, a within-word shuffle null, planted gates, a block bootstrap and an alphabet-normalised second look.

## Pre-registration (written and pushed before any Voynich number is computed)
- **Data:**
  - **Voynich:** ZL 3b (`data/ZL3b-n.txt`) and Takahashi IT2a (`data/IT2a-n.txt`). We use the paragraph words from `c030.ivtff_paragraphs`, in folio order. Commas are read as word spaces, and lines with unreadable words are dropped.
  - **Generator:**
    - `Generator_base` is the published base sample `data/corpora/ts_generated_text.txt`.
    - `Generator_C005matched` is the jar run with the C005 matched config: 2,400 lines, seed 4141. If the jar is unavailable, it is skipped and that is disclosed.
  - **Natural texts:** the same 7 as C034 and C037: Caesar, Descartes (Latin); Dante, Machiavelli (Italian); Cervantes (Spanish); Genesis, Exodus (Hebrew). They use the `c003.gutenberg` and `c003.hebrew` parsers: lower case, diacritics stripped, a–z only. Hebrew keeps its final letter forms as separate letters.
- **Primary tokenization (only one):**
  - Voynich and generator words are cut into **EVA glyph units** with `c003.units`, so `cth ckh cph cfh ch sh` each count as one glyph and every other EVA letter is one glyph.
  - Natural texts are cut into letters.
  - **One space token `_` follows every word**, so the stream is `w1 _ w2 _ …`.
  - Every text is cut to its **first N = 50,000 symbols**, spaces included. The short texts are checked and disclosed in the results.
- **Metrics (log2, bits):**
  - h1 = H(X).
  - h2 = H(X_i, X_{i+1}) − H(X_i), from plug-in bigram counts over the N−1 adjacent pairs.
  - |A| = number of distinct symbols in the sample, including the space.
  - h2_norm = h2 / log2|A|.
  - The plug-in bias at |A| ≤ ~40 and N = 50k is about 0.01–0.02 bits, the same for every text, and is not corrected.
- **Within-text null (reported for every text; not the decision):**
  - Shuffle the glyphs **inside each word**, keeping word lengths, spaces and each word's glyph multiset. We use 200 shuffles.
  - One-sided p-value: is the observed h2 lower than the null?
- **Robustness:**
  - Block bootstrap: 20 contiguous blocks, 200 resamples of the blocks' bigram counts, 95% interval for h2 and for h2_norm.
- **A text is called "robustly low" when** its h2 point estimate **and** its bootstrap 97.5% upper bound are both below the **minimum of the 7 natural texts' h2** at the same N. The same rule applies to h2_norm.
- **H1 (primary):**
  - **UNUSUALLY LOW** if ZL 3b is robustly low on h2 **and** IT2a replicates.
  - **INSIDE NATURAL** if both are inside the natural range.
  - **SPLIT (not replicated)** if ZL and IT2a disagree.
  - The generators are classified the same way but **do not decide H1**. They tell us whether a meaningless self-citation process also reaches the Voynich value.
- **H2 (secondary):** the same rule on h2_norm, which controls for alphabet size. There are two looks, each a range rule; the notional α is 0.025 each. The rule is not a p-value, so the split is recorded rather than applied.
- **Gates (40 replicates each, on Latin Caesar, run before the Voynich texts):** each replicate takes a random 50,000-symbol window of the full Caesar stream.
  - **FPR:** the window with its glyphs shuffled within words is called "robustly low" in ≤ 4/40 replicates.
  - **Power:** a Voynich-like low-h2 plant is called "robustly low" in ≥ 32/40 replicates.
    - Each replicate draws a random successor map f, with one preferred follower per symbol.
    - Inside each word, each glyph after the first is replaced with probability **p = 0.6** by f(previous, already rewritten glyph).
    - The space is never planted.
  - The same gates are run for h2_norm.
  - If a gate fails, that look is **NOT TESTABLE** and only descriptive numbers are published.
- **Calibration disclosure:**
  - p = 0.6 was chosen on Caesar **before this pre-registration**, after p = 0.5 doubling and copy plants proved too weak (≈ 3.03 bits vs a natural minimum ≈ 3.04).
  - During that check the 7 natural h2 values were seen (≈ 3.04–3.44 bits).
  - **No Voynich or generator number was computed before this push.**
  - The plant's target (≈ 2.75 bits) is near the published Voynich figure, which is literature, not our measurement.
- **Descriptive only (no decision):**
  - Raw EVA characters instead of units.
  - Units with no space token.
  - Natural texts with no space token.
  - Vowelless Caesar and Dante.
  - The natural leave-one-out check: is any natural text "robustly low" against the other six?
- **Caveats fixed in advance:**
  - A low h2 means strong glyph ordering *inside the writing system*: `qo-`, `-dy`, `ch-e-` sequences. It does not say whether the text has meaning.
  - Verbose ciphers, abbreviations, syllabaries and generated gibberish can all lower h2.
  - The tokenization choice (units vs raw EVA) changes |A| and h2, which is why h2_norm and a raw-EVA descriptive are reported.
- **Code:** `tools/c041_conditional_entropy.py`, seed 4141, run with `timeout 600`. Output: `analysis/C041_results.json`.

**Status:** pre-registered; no run yet.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
