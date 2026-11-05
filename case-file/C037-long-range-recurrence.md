# C037 — Expedição 37: o eco das palavras distantes (long-range word recurrence)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** F-MI (new family: long-range dependence between words). The last three cycles were F-SEG, so this cycle opens a new family, as the one-in-three rule requires.

## Question
Does the same Voynich word type come back at distances of 50–500 tokens more often than chance, as words do in natural texts that have topics? And does the Timm–Schinner self-citation generator reproduce the Voynich profile of short-range and long-range recurrence?

## Pre-registration (written and pushed before any run)
- **Data:**
  - Voynich: ZL 3b (`data/ZL3b-n.txt`) and Takahashi IT2a (`data/IT2a-n.txt`), with the paragraph words from `c030.ivtff_paragraphs`, in folio order.
  - Generator: two texts from the jar (`c004.generate`, seed 3701, 2,400 lines), one with the base config and one with the C005 matched config.
  - Natural texts: the same 7 as C034 (Caesar, Descartes, Dante, Machiavelli, Cervantes, Genesis, Exodus).
  - Every text is cut to its **first N = 16,000 tokens**. Exodus is the shortest at 16,726 tokens.
- **Metric:**
  - Recurrence at distance d: C(d) = P(w_i = w_{i+d}) / P0 − 1, where P0 = Σ n_w(n_w−1) / (N(N−1)) is the exact chance level under a random order of the same tokens.
  - S is the mean of C(d) for d = 1–10 (short range).
  - L is the mean of C(d) for d = 50–500 (long range).
- **H1 (tested on 4 texts):** each of ZL, IT2a, Generator_base and Generator_C005matched has L above its null.
  - Null: 1,000 random permutations of the same tokens, which keep the word frequencies.
  - One-sided p-value; Bonferroni α = 0.05/4 = 0.0125.
  - Verdict: LONG-RANGE RECURRENCE or NO DETECTED LONG-RANGE RECURRENCE.
- **H2 (descriptive, no p-values):**
  - S and L of each tested text are placed inside, above or below the range of the 7 natural texts.
  - Each generator "matches" ZL on S or L if the difference is within 2 combined jackknife SEs (10 contiguous chunks; seams at the joins are disclosed).
- **Gates (all must pass, or every H1 verdict becomes *not testable*):**
  - False-positive rate: 40 fully permuted copies of ZL, each tested with 200 permutations; at most 4/40 may come out significant.
  - Power: 40 planted copies, each a permuted ZL in which, in every 500-token block, 2% of tokens are replaced by one block-specific word (a planted "topic"); at least 36/40 must be detected.
  - The natural texts' p-values are reported as a sanity check, and are not a gate.
- **Caveats fixed in advance:**
  - Long-range recurrence in the manuscript can come from section topics (herbal vs. balneological pages) without any language behind it. H1 can show *dependence*, not *meaning*.
  - The manuscript order is the current binding, which may be wrong (Layfield & Fagin Davis 2026). Mis-binding would mostly weaken long-range recurrence.
- **Code:** `tools/c037_long_range_recurrence.py`, seed 3737, run with `timeout 600`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
