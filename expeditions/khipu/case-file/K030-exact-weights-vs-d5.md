# K030 · Exact per-hit odds against D5, on the same plants (README line 1)

## Why
K029 showed that exact window probabilities make a better score than K001's raw count, but its comparison was with
the wrong baseline: D5 (K003) is the best line-1 detector so far (stage 2: FPR 0.046, spec A 0.66, spec B 0.59). This
cycle runs the head-to-head K029 called for, with the same plants and the same null draws for every candidate.

## Candidates (fixed before running)
Matching rule as K001–K003: a pendant v ≥ 10 that equals the sum of the k = 2..12 pendants to its left or right, with
≥ 2 nonzero summands. The null is a within-khipu permutation. Min-p is calibrated against its own null as in K003.
- **D5** (K003, baseline): for each k, the sum of log10(v) over matching pendants; min-p over the 11 per-k scores.
- **D7** (K029's W): Σ_k (matches at k) × (−log p_k), with p_k the exact per-window chance probability.
- **D8** (new, exact per-hit odds): each match of value x at window k is weighted by −log q_k(x). Here
  q_k(x) = N_k(x; multiset without one x, ≥ 2 nonzero) / C(n−1, k) is the exact chance that *that value* equals a
  random k-subset of the other cords. The score is the sum over all matches.
- **D9** (new): the per-k version of D8, with min-p over the 11 per-k scores.

The q and p tables are recomputed for each tested sequence: for the real khipu, for each permuted copy, and for each
planted copy. Permutation keeps the multiset, so one table serves all of a sequence's null draws. Khipus whose largest
value exceeds 20 000 are *not computed* (13 in K029).

## Pre-registration
- **Stage 1, development (seed 3030, K = 300).** For each eligible khipu: calibration (a permuted copy treated as
  real), plant spec A (two cords equal the sum of the next 3) and plant spec B (two cords, k uniform in 2..10, either
  side), using K003's plant code unchanged. **Selection:** among D7, D8 and D9 with FPR ≤ 0.05, take the highest mean
  of spec A and spec B recovery at p ≤ 0.05. Ties go to the earlier candidate.
- **Stage 2, evaluation (fresh seed 3031, K = 500).** The chosen candidate and D5 are scored on the same draws.
  **Adopt** the chosen candidate as the line-1 detector if (a) its FPR is ≤ 0.05, (b) its mean A/B recovery beats D5's
  by ≥ 0.03, and (c) an exact two-sided McNemar test on the paired plant outcomes (A and B pooled) gives p < 0.05.
  Otherwise D5 stays, and the result is reported as a negative.
- K003's success bar (A ≥ 0.80, B ≥ 0.60) is reported for the winner too. Silence stays *not testable* unless it is met.

- **Compute checkpoint.** Each stage stops after 270 s, and the number of khipus reached is reported. Stage 2 is
  paired, so a partial stage still compares like with like.

## Results
(Written after the run, below this line.)
