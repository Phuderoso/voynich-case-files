# C046 — Expedição 46: os pares que voltam à mesma linha (same-line word-pair recurrence)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** F-PAIR, a power-first redesign of the same-line word-pair question (README backlog: "C006/C007 metrics lack power; needs a power-first design"). Prompted by the October 2026 preprint [arXiv 2610.34499](https://arxiv.org/abs/2610.34499), which reports that in 28 texts in 16 languages the same word pairs keep sharing a line, and that the manuscript shows this "at half the strength of the weakest". This is an independent check with our own data and code, not a reuse of theirs.

## Question
H1: in Voynich paragraph text, do the same two words share a line more often than a within-page shuffle predicts? H2: is that excess weaker than in every one of our 7 natural texts?

## Pre-registration (pushed before any Voynich number; a 0.2 s timing smoke test on Caesar only was run first, disclosed)
- **Data:** ZL 3b and IT2a paragraph lines (same filters as `c030.ivtff_paragraphs`: P loci, commas as spaces, lines < 3 words or with unreadable words dropped), grouped by **folio page**. Natural: the 7 texts of C041–C045 (Gutenberg typeset lines; Hebrew verses), lines < 3 words dropped, pages = consecutive blocks of **30 lines**. Each text capped at whole lines up to **15,000 tokens**.
- **Statistic:** for every line, the set of unordered pairs of *different* words on it. **Rec** = number of distinct pairs that occur on ≥ 2 lines. Null: shuffle all word tokens **within each page** (keeps page vocabulary and line lengths), B = 200. **Excess E = Rec / mean(null) − 1**; one-sided p = (1 + #null ≥ obs)/(B + 1).
- **H1 call:** PRESENT if E > 0 and p < 0.05 in both ZL and IT2a; ABSENT if neither; else SPLIT.
- **H1 gates (seed 4646, before any Voynich number):** FPR — 40 natural texts (cycling the 7) pre-shuffled within pages, tested with B = 100; pass ≤ 4/40 at p < 0.05. Power — 40 shuffled Dante texts with a plant: on 5% of lines two random words are overwritten by one of 30 fixed pairs of mid-frequency words (5–50 occurrences); pass ≥ 32/40. The 2% plant is reported as a sensitivity number, not a gate.
- **H2 (independent material, the C045 lesson):** each text split by pages into two disjoint halves; E computed on each half (B = 100). Natural bar = minimum over the 14 natural half-values. **WEAKER** if both halves of ZL **and** both halves of IT2a lie below the bar; NOT WEAKER if neither transcription does; else SPLIT.
- **H2 gates:** FPR (leave-one-out) — a natural text is falsely called weaker if both its halves fall below the minimum of the other six texts' halves; pass ≤ 1/7. Power — 10 Dante texts where 75% of lines are re-shuffled within pages (removes about three quarters of the line structure); pass ≥ 8/10 called weaker.
- **Multiple comparisons:** two hypotheses, each needing both transcriptions.
- **Caveats fixed in advance:** natural "pages" are artificial 30-line blocks and typeset lines are not scribal lines; line length differs between texts (the shuffle ratio absorbs part of this, not all). A pair excess says lines are units of composition; it does not show meaning, and the generator could produce it too (not tested this cycle).
- **Tool:** `tools/c046_line_pair_recurrence.py` → `analysis/C046_results.json`. Run `timeout 600 python3 tools/c046_line_pair_recurrence.py`.

## Results
*(to be filled after the run)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
