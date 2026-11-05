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

---

## Results (computed after the pre-registration commit `85389cf3`)

Tool: `tools/k025_whole_group_sums.py` (5.6 s). Output: `analysis/k025_results.json`.

### Primary (Bonferroni ×2, α = 0.025)
| Khipu | Pendants / groups | G (obs) | Null mean | p | FPR | Power (1 planted) | Verdict |
|---|---|---|---|---|---|---|---|
| KH0359 (UR119, Göteborg) | 173 / 49 | **4** | 0.015 | < 1e-4 | 0.02 | 1.00 | **supported** |
| KH0405 (UR166) | 30 / 12 | **4** | 0.003 | < 1e-4 | 0.00 | 1.00 | **supported** |

### Secondary (reported)
Across 369 khipus with ≥ 4 groups: G = 31 against 14.1 expected (p = 0.0002); BH-significant only KH0359 and KH0405;
calibration 0 BH false discoveries (FPR at 0.05: 0.014).

### Post-hoc (disclosed, not pre-registered)
Tool: `tools/k025_posthoc.py`. Output: `analysis/k025_posthoc.json`.
- **The sums themselves.** In UR119, four totals in a row (cords 52, 59, 66, 73) each add up the six-cord group that
  follows: 416, 390, 406, 481. Each of those groups opens with 19 and has a large fourth cord (212–226), so it is one
  repeated record layout with a total in front. In UR166, the totals are 658 (the group before it), 612 (after),
  805 (before) and 17 (after).
- **Selection.** These two khipus were chosen because K001 flagged them, so the corpus total is partly selected.
  Without them: G = 23 against 14.1, p = 0.018, a smaller excess spread over many khipus, none BH-significant.

### Literature and audit
Ascher-style pendant sums in UR119 are already counted by the
[Khipu Field Guide](https://www.khipufieldguide.com/catalog/KH0359.html) (65 "Ascher sums"), so this isn't a new
discovery. What K025 adds is a calibrated test that pins down the **form** of the sums: a total placed next to a whole
group. **Audit of K001:** K001's generic window detector only reached nominal p under its group-order null for these
khipus; a statistic aimed at the actual structure gives p < 1e-4 with full power. K001's "none across group
boundaries" reflected its tool's low power, not an absence of group-level sums.

### Line 2 status
**Closed, answered:** the cross-group sums in KH0359 and KH0405 are whole-group totals.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
