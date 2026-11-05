# K031 · Within-group D5 windows on large khipus (README line 1)

## Why
K030 closed the re-weighting lever: exact per-hit odds lose to D5 head-to-head. The remaining gap on line 1 is
**large khipus**, where chance adjacent sums crowd the signal (K003: recovery ~0.56 on the largest third). Cord
groups (consecutive level-1 cords that share `CLUSTER_ID`, as in K001) are a natural place to look: K001 found no
BH-significant sum cords *across* group boundaries, and K025 showed that some cross-group arithmetic is a different
habit (whole-group totals). This cycle asks whether restricting D5's matches to windows that lie entirely inside one
group recovers planted within-group sums better than unrestricted D5, especially on large multi-group khipus.

## Candidates (fixed before running)
Matching rule as K001–K003: a pendant v ≥ 10 that equals the sum of the k = 2..12 pendants immediately to its left or
right, with ≥ 2 nonzero summands. D5 score = min-p over the 11 per-k log10(v)-weighted hit scores, under a
within-khipu permutation null (same construction as K003).
- **D5** (baseline): unrestricted adjacent windows.
- **D5w** (new): identical scoring, but a hit is **invalid** if any cord of the window (or the anchor) has a different
  `CLUSTER_ID` than the anchor. Only within-group windows count.

**Null for both:** within-khipu permutation of pendant values. The same draws are shared. Groups stay fixed in their
ordinal positions; values move (structure-preserving for chance sums across the whole khipu).

All eligible khipus are kept (no value-cap skip): D5w needs no DP tables.

## Plants (shared)
- **Spec A_within:** two within-group planted sum cords at k = 3. The chosen group must have ≥ k + 2 cords; anchor and
  window lie entirely inside that group.
- **Spec B_within:** two within-group plants; for each plant, k is uniform in 2..min(10, group_len − 1), group length
  ≥ k + 2, either side.
- **Spec A / Spec B:** unrestricted K003 plants, reported for comparability (descriptive when a within-group plant
  cannot be placed).

## Pre-registration
- **Stage 1, development (seed 3130, K = 300, checkpoint 270 s).** For each eligible khipu: calibration (a permuted
  copy treated as real), A_within, B_within, and unrestricted A/B when placeable. Report FPR and recovery for D5 and
  D5w. **No selection** between them beyond reporting — both go to evaluation.
- **Stage 2, evaluation (fresh seed 3131, K = 500, checkpoint 270 s, paired same draws).** Primary decision is on the
  **largest third of khipus by pendant count** among those with ≥ 2 groups of size ≥ 4 (the intended population).
  Whole-corpus and size-stratified descriptives are also reported. Mark a stratum *not testable* if the power bar
  below is unmet.
- **Adopt D5w as the line-1 detector iff**, on that large stratum in eval: (a) FPR ≤ 0.05, (b) mean(A_within,
  B_within) recovery beats D5 by ≥ 0.03, (c) exact two-sided McNemar on the paired plant outcomes (A_within and
  B_within pooled) gives p < 0.05. Else D5 stays, and the result is published as a negative.
- K003's absolute bar (A ≥ 0.80, B ≥ 0.60 on the corresponding plants) is reported too; silence stays *not testable*
  unless it is met on the primary stratum.

## Results

Run 2026-11-05 ~10:35 PT (America/Vancouver), `python3 tools/k031_within_group_windows.py ../khipu.db` (84 s; both stages
finished all 457 eligible khipus, no time cap). Output is in [`analysis/k031_results.json`](../analysis/k031_results.json).
No value-cap skip (all eligible kept). Population: 378 khipus with ≥ 2 groups of size ≥ 4; size thirds at 32.7 and 82.3
pendants; largest third **n = 126** (83–1650 pendants).

**Stage 1, development (seed 3130, K = 300).** Whole corpus (descriptive; no selection).

| Detector | FPR | A_within | B_within | Mean within | A (unrest.) | B (unrest.) |
|---|---|---|---|---|---|---|
| D5 | 0.055 | 0.629 | 0.600 | 0.615 | 0.668 | 0.580 |
| D5w | 0.042 | 0.785 | 0.753 | 0.769 | 0.477 | 0.291 |

D5w recovers within-group plants far better and, as expected, loses on unrestricted plants (many of which sit across
groups). FPR for D5w is inside the bar.

**Stage 2, evaluation (fresh seed 3131, K = 500, paired).** Primary stratum = largest third of the population.

| Detector | FPR (large) | A_within | B_within | Mean within |
|---|---|---|---|---|
| D5 | 0.048 | 0.532 | 0.468 | 0.500 |
| D5w | **0.048** | **0.686** | **0.571** | **0.628** |

Paired plant outcomes (A_within + B_within on the large stratum, n = 124 + 126): **40** found only by D5w, **8** found
only by D5. Exact McNemar **p = 3.3 × 10⁻⁶**. Mean gain **+0.128**.

Adoption rule: (a) FPR ≤ 0.05 ✓, (b) gain ≥ 0.03 ✓, (c) McNemar p < 0.05 ✓.

**Decision: D5w adopted as the line-1 detector for within-group sum recovery on large multi-group khipus.**
K003's absolute bar (A ≥ 0.80, B ≥ 0.60) is **not** met on the large stratum (0.686 / 0.571), so silence on that
stratum stays *not testable* at the old absolute power target; D5w is still the better tool there.

### Descriptives (eval; not the decision)
| Stratum | n | D5w FPR | D5w A_within | D5w B_within | D5 A_within | D5 B_within |
|---|---|---|---|---|---|---|
| small third | 126 | 0.056 | 0.836 | 0.817 | 0.681 | 0.643 |
| mid third | 126 | 0.063 | 0.800 | 0.675 | 0.617 | 0.516 |
| large third (primary) | 126 | 0.048 | 0.686 | 0.571 | 0.532 | 0.468 |
| whole population | 378 | 0.056 | 0.772 | 0.688 | 0.608 | 0.542 |
| whole eligible | 457 | 0.055 | 0.763 | 0.679 | 0.620 | 0.536 |

Mid-third D5w FPR (0.063) sits slightly above 0.05; the primary large stratum is calibrated. Unrestricted A/B recovery
for D5w on the large stratum is 0.421 / 0.278 (below D5's 0.524 / 0.484): D5w is specialised to within-group structure.

### Reading
- Restricting to within-group windows removes chance sums that cross `CLUSTER_ID` boundaries. On large khipus those
  false matches were drowning the planted within-group signal; D5w lifts recovery by about 13 percentage points there.
- The gain is largest where it was needed (large third). On small khipus both detectors are already strong; D5w is
  stronger still, but that was not the decision stratum.
- **Line 1 status.** D5w replaces D5 as the preferred detector when the scientific question is within-group adjacent
  sums on multi-group khipus. D5 remains the right tool for unrestricted adjacent sums. Next levers: a corpus-wide
  D5w scan with BH-FDR (held-out calibration, given the mid-stratum FPR), and/or a combined rule that uses D5w inside
  groups and D5 only where a window is free to cross.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

