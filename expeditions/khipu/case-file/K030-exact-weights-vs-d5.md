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

Run 2026-11-05 ~10:20 PT, `python3 tools/k030_exact_weights_vs_d5.py ../khipu.db` (30 s; no time cap was hit, so all
444 computable khipus were scored in both stages). Output is in [`analysis/k030_results.json`](../analysis/k030_results.json).
The same 13 khipus as in K029 were *not computed* (a value above 20 000).

**Stage 1, development (seed 3030, K = 300).**

| Candidate | FPR | Spec A | Spec B | Mean | Eligible (FPR ≤ 0.05) |
|---|---|---|---|---|---|
| D5 (baseline) | 0.047 | 0.67 | 0.52 | 0.60 | (baseline) |
| D7 (K029's W) | 0.054 | 0.48 | 0.52 | 0.50 | no |
| D8 (exact per-hit odds, summed) | 0.052 | 0.52 | 0.52 | 0.52 | no |
| D9 (exact per-hit odds, per-k min-p) | 0.050 | 0.64 | 0.45 | 0.54 | **yes, chosen** |

**Stage 2, evaluation (fresh seed 3031, K = 500, paired).**

| Detector | FPR | Spec A | Spec B | Mean |
|---|---|---|---|---|
| D5 | 0.038 | **0.68** | **0.55** | **0.61** |
| D9 | 0.034 | 0.60 | 0.47 | 0.54 |

Paired plant outcomes: 22 found only by D9, 79 found only by D5. Exact McNemar **p 1.0 × 10⁻⁸**, gain −0.076.

**Decision: not adopted. D5 stays the line-1 detector.** This is a clean negative. Exact per-hit odds are a worse
weighting than log10(v), and significantly so. K003's bar (A ≥ 0.80, B ≥ 0.60) is not met by either detector.

### Reading
- Exactness doesn't buy power here. K029's win over raw counting reflects counting being a poor score, not exact
  odds being a good one. Once the baseline is D5, the exact weights lose on both plant specs.
- A plausible mechanism, offered as a hunch and not tested: the planted sums are built from the khipu's own values,
  so they sit at ordinary sizes. Exact odds put the most weight on rare large-value coincidences, while log10(v) is
  smoother. The plant therefore resembles the "typical-size" case D5 handles well.
- **Line 1 status.** Re-weighting per hit is now explored in three forms (K002 log-weights, K029/K030 exact odds), and
  D5 remains best. The remaining gap is large khipus, where chance sums crowd the signal (K003: 0.56 on the largest
  third). A different lever is needed there, such as restricting to within-group windows, rather than new weights.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
