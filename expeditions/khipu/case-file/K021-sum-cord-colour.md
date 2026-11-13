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

---

## Results (computed after the pre-registration commit `a77b72a3`)

Tools: `tools/k021_sum_cord_colour.py` (7.6 s) and the disclosed post-hoc `tools/k021_posthoc_group_null.py`.
Output: `analysis/k021_results.json`, `analysis/k021_posthoc_group_null.json`.

**Controls pass.** False-positive rate at α = 0.025: H1 0.015, H2 0.010 (rule ≤ 0.05). Power: H1 1.00, H2 0.98.

| Population | Khipus | Sum cords | Eligible | T1 (boundary) obs / null | p₁ | T2 (shared colour) obs / null | p₂ |
|---|---|---|---|---|---|---|---|
| **Primary** (K001 BH-significant) | 10 | 95 | 1,005 | 35 / 31.4 | 0.19 | **416 / 229.5** | **< 1e-4** |
| Secondary (any sum cord) | 245 | 724 | 10,414 | 290 / 278.1 | 0.11 | 782 / 612.5 | < 1e-4 |

- **H1 (sum cords sit at colour boundaries): not supported.** Power is 1.00, so this is a real negative: sum cords
  are no more colour-isolated from their neighbours than other cords of value ≥ 10.
- **H2 (sum cords share a colour): supported**, in both populations. In 7 of the 10 primary khipus, all or nearly
  all sum cords have one colour (e.g. UR267A all 16 in one colour; UR269 16 of 17; UR256 8 of 8).

### Post-hoc check (disclosed, not pre-registered; it can weaken but not upgrade the verdict)
Sum cords cluster in particular cord groups, and groups are often one colour, so H2 could just be "sum cords are in
the same groups". A stricter null redraws sum cords **only within their own cord group**. Overall, H2 survives:
T2 = 416 against a null mean of 261.5 (p < 1e-4). The excess comes from three Inkawasi khipus: UR267A (p 0.0006),
UR269 (p < 1e-4) and UR275 (p 0.029). In the other seven, group membership already explains the shared colour.

### Literature check
This is **not a new discovery**. The [Khipu Field Guide](https://khipufieldguide.com/notebook/fieldmarks/colored_pendant_sum/index.html)
already lists a "Colored Pendant Sum" field mark for many Inkawasi khipus, including UR255, UR256, UR267A, UR267B,
UR269 and UR270. What K021 adds is a calibrated, pre-registered test: colour does mark sum cords beyond chance, and in
UR267A, UR269 and UR275 the effect goes beyond group membership. Colour *boundaries* do not mark them.

### Line 6 status
Advanced. Next: test whether the shared sum-cord colour is the same colour as the summed cords (colour-matched sums,
as the Field Guide's field mark implies) against the within-group null, and do the colour-code concordance before any
cross-khipu comparison of colour names.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

## Audit note (K057, 2026-11-08)
Under the K008 multi-number (R5) mask, H2 is **robust**: primary T2 = 225 vs 100.938, p 5.0×10⁻⁵
(FPR 0.025, power 0.985); secondary T2 = 513 vs 406.595, p 0.00070 (FPR 0.040, power 1.00). The mask
removes 26 of 95 primary sum cords (24 R5 targets, 2 R5-only windows). H1 was not retested. See
[K057](K057-multinumber-sum-colour.md).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04


> **Audit note (K074, 12 Nov 2026, KFG re-audit).** On Khipu Field Guide data the primary verdicts (ten BH khipus) and the corpus shared-colour verdict replicate; the **secondary boundary verdict does not**: over 289 KFG khipus, sum cords differ in colour from both neighbours more than chance (367 vs 335.3, p 0.0012). 'Not supported' above is true of the OKR only. See [K074](K074-kfg-sum-cord-colour.md).
