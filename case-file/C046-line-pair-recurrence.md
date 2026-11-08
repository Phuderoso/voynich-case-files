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

## Results (run 2026-11-08 ~02:32 PT, one run, 146 s; `analysis/C046_results.json`)
**H1 gates: FPR 1/40 (pass), power 2/40 at the 5% plant (FAIL; 3/40 at 2%) → H1 NOT TESTABLE.** Diagnosed after the run: 5% of ~1,500 lines spread over 30 pairs is only ~2–3 plants per pair, which adds a few dozen recurring pairs against a null sd of about 45; the plant was too weak for this statistic. Not redesigned after seeing Voynich numbers.

**H2 gates: FPR 1/7 (pass, at the limit), power 10/10 (pass). Natural half-bar 0.055 (Machiavelli).**

| text | E (full, p) | E halves |
|---|---|---|
| Latin Caesar | 0.246 (0.005) | 0.272 / 0.300 |
| Latin Descartes | 0.141 (0.005) | 0.202 / 0.151 |
| Italian Dante | 0.146 (0.005) | 0.171 / 0.143 |
| Italian Machiavelli | **0.048** (0.005) | **0.055** / 0.068 |
| Spanish Cervantes | 0.110 (0.005) | 0.135 / 0.115 |
| Hebrew Genesis | 0.146 (0.005) | 0.183 / 0.163 |
| Hebrew Exodus | 0.234 (0.005) | 0.155 / 0.376 |
| **Voynich ZL 3b** (1,940 lines, 135 pages) | **0.027** (0.010) | 0.061 / **0.020** |
| **Voynich IT2a** (1,964 lines, 136 pages) | **0.023** (0.010) | 0.082 / **0.008** |

**H2 verdict by the pre-registered rule: NOT WEAKER.** Read it as "not shown weaker": in each transcription the first half (earlier folios) sits above the bar and the second half below it, so neither meets "both halves below".

**What this means (no overclaiming):**
- Descriptively, the full-text Voynich excess (0.023–0.027) is about half of the weakest natural text (Machiavelli 0.048) and positive at p ≈ 0.01. That matches the size reported in arXiv 2610.34499, but here it is **not a verdict**: H1's gate failed, and H2's independent-halves rule did not confirm it.
- The halves disagree strongly (earlier folios 0.06–0.08, later 0.01–0.02). That points to a difference along the book (possibly Currier A vs B, or the herbal vs the later sections). This is a new lead, and testing it needs its own pre-registration.
- A pair excess says lines are units of composition; it is not evidence of meaning. The generator was not tested.

**Next:** F-PAIR step 2 with a stronger, calibrated plant for H1 (more lines or fewer pairs, power checked before any Voynich number), and a pre-registered Currier A vs B (or section) split of E with page-level independence.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
