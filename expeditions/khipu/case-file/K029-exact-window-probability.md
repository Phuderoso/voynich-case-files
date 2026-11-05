# K029 · Exact chance probability of a sum window, and a detector weighted by it (README line 1)

## Why
Line 1 asks for a sharper sum-cord detector. K002/K003's best was D5 (min-p over per-k scores), and the gap is power on
short sums. K001 counts a cord as a hit when it equals the sum of the k = 2..12 pendants next to it, but a match over
k = 12 big values and a match over k = 2 small ones are not equally surprising. Under K001's null (values permuted
within the khipu), the chance that one fixed window matches can be computed **exactly** by counting subsets, with no
simulation.

## Exact formula (fixed before any code was run)
For a khipu with pendant values y₁…yₙ and window size k, the probability that a fixed cord position equals the sum of
a fixed set of k other positions is

p_k = (1/n) · Σ_{j : y_j ≥ 10} [ N_k(y_j; multiset without j) − E_k(j) ] / C(n−1, k)

- N_k(x; M) is the number of k-subsets of M summing to x. It is computed by dynamic programming over (count, sum), with
  one item deleted exactly by the inverse recursion g[c][s] = f[c][s] − g[c−1][s−y].
- E_k(j) removes the subsets with only one nonzero value: (# other cords equal to y_j) × C(# zeros, k−1). This
  matches K001's "at least 2 nonzero" rule.
- Khipus whose largest value exceeds 20 000 are skipped for cost and reported as *not computed*.

## Pre-registration
- **Audit (exactness check).** For 20 random eligible khipus, the exact expected number of matching windows
  Σ_k 2(n−k)·p_k must agree with a 2 000-permutation Monte Carlo mean of the same count within 3 standard errors in
  ≥ 19 of 20. Otherwise the formula is wrong and the cycle stops as *not testable*.
- **Detector W.** W = Σ over matching (cord, side, k) of −log p_k. S is K001's hit count. Null: 1 000 within-khipu
  permutations, shared by W and S.
- **Calibration.** One permuted copy of each khipu is treated as observed. W is acceptable if its false-positive rate at
  α = 0.05 is ≤ 0.06.
- **Power.** On each khipu with ≥ 20 pendants, K001's planted control (two sum cords over the next 3, on a permuted
  copy) is scored by both W and S at α = 0.05.
- **Decision.** W is **adopted** as the line-1 detector if it passes calibration and its power beats S by
  ≥ 0.05 with an exact McNemar p < 0.05 on the paired planted results. Otherwise it is **not adopted** (reported
  either way). Real-data BH discoveries under W are reported as secondary, against K001's ten.

**Pre-run unit test (synthetic data only, no khipu data read):** on three random 25-value sequences, the exact expected
match count agreed with 20 000-permutation means within 1.2 standard errors (1.848 vs 1.843, 1.427 vs 1.416, 1.604 vs 1.608).

## Results
(Written after the run, below this line.)
