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
(Written after the run, below this line.)

