# K021 · Do sum cords stand out by colour? (open line 6)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K021 statistic was computed.

## Why
Open line 6 asks whether cord colour marks which cords are sums. Only equality of colour codes *within one khipu* is
used, so the test does not depend on how different investigators named colours (the concordance problem noted in K019).

## Definitions (fixed in advance)
- **Sum cords** are the K001 hits: a level-1 pendant with value ≥ 10 that equals the sum of the next or previous
  k = 2..12 pendants, with at least 2 of them nonzero (multi-number cords included, as in K001).
- **Eligible cords** are level-1 pendants with value ≥ 10 and a known colour.
- **Cord colour** is `FULL_COLOR` of the `ascher_cord_color` row with the smallest `RANGE_BEG` (ties: smallest
  `color_id`). Cords with no colour row are excluded.
- **Primary population:** the 10 khipus that were BH-significant in K001 (K = 5000), where sum cords are real rather
  than chance. **Secondary population:** every khipu with at least one sum cord (reported, separately corrected).

## Hypotheses and statistics
- **H1 (boundary):** sum cords differ in colour from both neighbouring pendants more often than other eligible cords.
  T1 = number of sum cords whose colour differs from both the left and the right neighbour (neighbours of unknown
  colour count as "different"; the end cords use one neighbour).
- **H2 (shared colour):** sum cords in one khipu share a colour among themselves more than chance.
  T2 = number of same-colour pairs among the sum cords, summed over khipus.

## Null (keeps all colour structure)
The colour sequence of every khipu is left untouched. In each replicate, the same number of sum cords is drawn
uniformly without replacement from that khipu's eligible cords. 20 000 replicates. One-sided p = (1 + #null ≥ obs) / (1 + R).

## Decision rule
Two primary tests (H1, H2 on the primary population), Bonferroni α = 0.025 each. A hypothesis is **supported** if its
p ≤ 0.025 and the controls pass; **not supported** if p > 0.025 with power ≥ 0.5; **not testable** if power < 0.5.
The secondary population is reported with its own Bonferroni (α = 0.025), and cannot rescue a primary result.

## Controls
- **Calibration:** 200 times, replace the real sum cords with a random eligible draw and test it; the false-positive
  rate at α = 0.025 must be ≤ 0.05 for each hypothesis.
- **Power:** 200 planted sets in which each sum cord is swapped, with probability 0.5, for a random eligible cord that
  meets the hypothesis (a colour boundary for H1; the khipu's most common sum-cord colour for H2).

Compute: well under a minute.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
