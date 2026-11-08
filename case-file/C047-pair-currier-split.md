# C047 — Expedição 47: a bifurcação no meio do livro (same-line pair excess, Currier A vs B)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** F-PAIR step 2. C046 found (descriptively) that the same-line pair excess E is much larger in the earlier folios (0.06–0.08) than the later ones (0.01–0.02). Earlier folios are mostly Currier A, later mostly Currier B.

## Question
Is E larger on Currier A pages than on Currier B pages, beyond what a random split of pages gives?

## Pre-registration (pushed before any Voynich number; a 0.16 s timing test on Dante only was run first, disclosed)
- **Data:** ZL 3b and IT2a paragraph lines (C046 filters), all of them (no token cap); page language from the IVTFF page header `$L` (A or B); pages without A/B dropped. Section `$I` is used for one descriptive look only.
- **Statistic:** E as in C046 (distinct different-word pairs sharing ≥ 2 lines, over the mean of NS = 5 within-page shuffles, minus 1), computed separately for A pages and B pages. **D = E_A − E_B.**
- **Test:** page-label permutation. Draw the same number of pages as A at random, recompute D, 200 times; one-sided p = (1 + #null ≥ obs)/201.
- **Verdict:** A > B if p < 0.05 in both ZL and IT2a; NO DIFFERENCE SHOWN if neither; SPLIT otherwise.
- **Gates (seed 4747, natural text only, before any Voynich number), 40 permutations per trial:**
  - FPR: 20 windows of 34,000 tokens (Dante and Cervantes alternating; 30-line pages); pseudo-"A" = a **contiguous** block of 40% of pages at a random start (wraps around). This is deliberately harsh: it catches ordinary drift along a book being mistaken for a language effect. Pass ≤ 2/20.
  - Power: 20 Dante windows, contiguous pseudo-A as above; on non-A pages 60% of lines have their words re-shuffled within the page (B weakened). Pass ≥ 16/20.
  - A failed gate → NOT TESTABLE.
- **Descriptive (no verdict):** herbal-only (`$I=H`) A vs B E, to hold the section roughly fixed.
- **Caveats fixed in advance:** Currier language is confounded with section, scribe (Fagin Davis hands) and position in the book. A positive result says "A pages behave differently", not why. Group sizes differ (permutation keeps page counts, not token counts).
- **Tool:** `tools/c047_pair_currier_split.py` (imports C046) → `analysis/C047_results.json`.

## Results
*(to be filled after the run)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
