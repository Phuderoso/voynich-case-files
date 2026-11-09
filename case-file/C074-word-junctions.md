# C074 — Word junctions: does the end of a word predict the start of the next? (NEW FAMILY F-JUNC)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Status: PRE-REGISTERED (pushed before running)

## Why
C072 and C073 ran into a junction effect: a *sh*-initial word follows a `y`-final word about half as often as it follows other words. This new family measures the whole junction table. How much does the last glyph unit of a word tell you about the first glyph unit of the next one, beyond what the page's vocabulary alone gives? And does the Timm–Schinner generator, which has its own `canFollow` junction rules, land in the same place? Junction dependence between words was noted in earlier Voynich literature. This is our own calibrated measurement of it, not a claim of novelty.

## Statistic
- **Lines and pairs:** paragraph lines with ≥ 5 clean words (C070 parser). Only **interior** words are used (positions 2..n−1), because line-first and line-final words have known position effects (C032, C033, C070). Pairs are adjacent interior words.
- **Classes:** the final unit of word *i* goes into one of the 8 commonest finals or "other". The initial unit of word *i+1* goes into one of the 10 commonest initials or "other". Classes are fixed per dataset from its own counts.
- **MI:** plug-in mutual information (bits) of the final × initial table.
- **Null:** interior words shuffled among interior slots of the same page, which keeps page vocabulary and line lengths. R = 200.
- **Effect size:** X = MI − mean null MI; ratio = MI / mean null MI.

## Tests
- {Currier A, Currier B} × {IT2a, ZL3b} = 4 tests, one-sided rank p, Holm α 0.05.
- **Gates (20 repetitions each):** FPR ≤ 2/20 on page-shuffled text. Power ≥ 16/20 with a planted junction rule: with q = 0.05, a pair's second word is swapped for a same-page interior word whose initial class is target(final class), using a fixed random map.
- **Verdict per language:** DETECTED, PARTIAL, NOT DETECTED, NOT TESTABLE.

## Generator (descriptive, pre-registered criterion)
- 20 default runs (seeds 10901–10920, 1,500 lines, pseudo-pages of 29 lines).
- The manuscript's Currier B ratio is called **ABOVE**, **INSIDE** or **BELOW** the run range, in both transcriptions; otherwise SPLIT.

## Disclosure
Before this push I ran one smoke test on IT2a Currier B (seed 1, R 20) to time the code: MI 0.229 bits against a null of 0.006. It is not part of the decision. I expect the tests to pass easily. The informative part is the size compared with the generator.

Seed 7474. Tool: `tools/c074_junction.py`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
