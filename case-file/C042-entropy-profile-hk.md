# C042 — Expedição 42: o perfil de entropia condicional h_k (k = 1–4)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** F-ENT step 2 (continuation of C041). C041 opened the family with h2; this cycle asks whether the low next-glyph uncertainty persists at longer contexts and which predecessor glyphs carry the deficit.

## Question
Does the Voynich low next-glyph uncertainty persist at longer contexts (h3, h4), and does the gap vs natural language hold? Does the Timm–Schinner generator follow the same h_k profile? Separately (Look 3 / descriptive attribution): which predecessor glyphs carry most of the ~0.70-bit h2 deficit vs natural?

## Pre-registration (written and pushed before any Voynich or generator number is computed)
- **Data (reuse C041 exactly):**
  - **Voynich:** ZL 3b (`data/ZL3b-n.txt`) and Takahashi IT2a (`data/IT2a-n.txt`). Paragraph words from `c030.ivtff_paragraphs`, folio order. Commas as word spaces; lines with unreadable words dropped.
  - **Generator:**
    - `Generator_base` = published base sample `data/corpora/ts_generated_text.txt`.
    - `Generator_C005matched` = jar run with the C005 matched config (2,400 lines, seed 4242 for this cycle's generation call; if the jar is unavailable, skip and disclose).
  - **Natural texts:** the same 7 as C041: Caesar, Descartes (Latin); Dante, Machiavelli (Italian); Cervantes (Spanish); Genesis, Exodus (Hebrew). Parsers `c003.gutenberg` / `c003.hebrew`.
- **Primary tokenization (only one; identical to C041):**
  - Voynich and generator: **EVA glyph units** via `c003.units` (`cth ckh cph cfh ch sh` each one glyph).
  - Natural: letters.
  - **One space token `_` after every word.**
  - First **N = 50,000** symbols (spaces included). Short texts disclosed.
- **Metrics (log2, bits):**
  - h1 = H(X).
  - For k ≥ 2: h_k = H(k-gram) − H((k−1)-gram), plug-in counts on the N−(k−1) overlapping k-grams (same construction as C041 for k = 2).
  - Report the profile (h1, h2, h3, h4) and |A| for every text.
  - Optional secondary: h_k_norm = h_k / log2|A| for k = 2, 3, 4.
  - Plug-in bias at |A| ≤ ~40 and N = 50k is ~0.01–0.02 bits at k = 2 and grows with k; it is the same order for every text and is not corrected. At k = 4 sparse cells inflate bias; that is disclosed, not patched.
- **Robustness:**
  - Block bootstrap: 20 contiguous blocks, 200 resamples of the blocks' n-gram counts, 95% CI on each h_k.
  - Compute budget: if too slow, CI only on h2–h4 for Voynich + the natural min and max texts; disclose.
- **A text is "robustly low at k"** when its point h_k **and** its bootstrap 97.5% upper bound are both below the **minimum of the 7 natural texts' h_k** at the same N.
- **H1 PRIMARY (profile persistence):**
  - **UNUSUALLY LOW** if ZL is robustly low at k = 2 **and** at least one of k = 3 or k = 4, **and** IT2a replicates the same pattern (same ks).
  - **INSIDE NATURAL** if ZL is not robustly low at any of k = 2, 3, 4.
  - **PARTIAL** if only h2 stays low and h3/h4 enter the natural range (or only one of 3/4 is low, so the "at least one of 3/4" clause fails for the pair of looks, or the pattern of which ks are low is incomplete relative to the rule above — recorded precisely in results).
  - **SPLIT** if ZL and IT2a disagree on which ks are robustly low.
  - Generators are classified the same way but **do not decide H1**.
- **H2 SECONDARY (normalised):** the same rule on h_k_norm; recorded separately; notional α 0.025.
- **Look 3 DESCRIPTIVE (no verdict):** per-predecessor mutual information contribution I(prev=a; next) = H(next) − H(next | prev=a), weighted by P(a). List the top glyphs driving Voynich h2 below the natural median. Vowelless Caesar and Dante as descriptive controls (strip aeiou).
- **Gates (40 replicates on Latin Caesar windows of 50k, BEFORE any Voynich or generator number):**
  - **FPR:** within-word glyph shuffle called robustly low at k = 2 in ≤ 4/40 (and separately check k = 3 if cheap).
  - **Power:** successor-map plant p = 0.6 as in C041 called robustly low at k = 2 in ≥ 32/40.
  - Same gates recorded for the normalised look at k = 2.
  - If a gate fails for a look → **NOT TESTABLE** for that look.
- **Seed:** 4242 (new for C042).
- **Leave-one-out (descriptive):** is any natural text robustly low vs the other six at k = 2?
- **Caveats fixed in advance:**
  - Low h_k is about writing-system ordering, not meaning.
  - Sparse 4-grams at N = 50k make h4 noisier; the bootstrap CI is the guard.
  - Helpers imported from `tools/c041_conditional_entropy.py` and `c003` / `c030`.
- **Code:** `tools/c042_entropy_profile.py`, seed 4242, run with `timeout 600`. Output: `analysis/C042_results.json`.

**Status:** pre-registered before any Voynich or generator run. Results will be appended after the run.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
