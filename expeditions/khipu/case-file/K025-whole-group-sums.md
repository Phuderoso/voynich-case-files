# K025 · Do totals add up whole neighbouring groups? (open line 2)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K025 statistic was computed.

## Why
Line 2 flagged KH0359 (UR119) and KH0405 (UR166): their K001 sums were nominal under the group-order null, which
hints that the sums depend on how groups sit next to each other. A sharp, checkable form of that idea is
the classic Ascher pattern: **a total that adds up one whole neighbouring cord group**.

## Definitions (fixed in advance)
- Pendant values and groups as in K001 (level-1 pendants, `CLUSTER_ID`, duplicates excluded).
- A **whole-group sum** is a pendant with value ≥ 10 that equals the sum of **all** pendants of the group
  immediately to its right or immediately to its left, where that group has ≥ 2 cords, at least 2 of them nonzero,
  and the pendant is not itself in that group.
- Statistic G = number of pendants that are whole-group sums.

## Null and tests
- **Null:** permute pendant values within the khipu (K001's N1; keeps group sizes and positions), 20 000 replicates.
  One-sided p = (1 + #null ≥ obs) / (1 + R).
- **Primary:** KH0359 and KH0405 separately, Bonferroni ×2 (α = 0.025 each).
- **Secondary (reported, BH q = 0.05):** every non-duplicate khipu with at least 4 groups, per khipu, plus a corpus
  total against the summed null.

## Decision rule
Per primary khipu: **supported** if p ≤ 0.025; otherwise **not supported** if planted power ≥ 0.5, **not testable** if
below.

## Controls
- **Calibration:** for each primary khipu, 200 shuffled copies tested as observed (FPR at 0.025 ≤ 0.05); corpus-wide,
  one shuffled copy per khipu, BH false discoveries reported.
- **Power:** for each primary khipu, 200 shuffled copies with **one** whole-group sum planted (a pendant adjacent to a
  random eligible group set to that group's sum).

Compute: under a minute.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
