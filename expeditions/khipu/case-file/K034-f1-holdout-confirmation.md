# K034 · Held-out confirmation of F1-only hits KH0322/UR086 and KH0420/UR182 (README line 1)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K034 confirmation statistic was computed.

## Why
K033's calibrated F1 BH scan (D5w on 378 multi-group khipus) named eleven discoveries. Two are new against
K003's unrestricted list: **KH0322/UR086** and **KH0420/UR182**. A BH ranking is a discovery tool, not a
confirmation. This cycle tests those two named khipus with a **secondary statistic that does not reuse the
corpus BH ranking of D5w min-p**.

## Named targets (fixed)
1. KH0322 / UR086
2. KH0420 / UR182

OKR `khipu.db` @ `4039ca5`, level-1 pendants, same group definition as K031–K033 (`CLUSTER_ID` runs).

## Primary statistic L (per khipu)
**Longest within-group exact-sum window.** L = max k ∈ {2,…,12} such that some pendant with value ≥ 10 equals
the sum of k consecutive neighbours that lie entirely inside the same group, with ≥ 2 nonzero summands. The
within-group adjacency mask is identical to D5w's `valid_masks` in `tools/k032_d5w_corpus_scan.py`. L is a
**scalar** (one length), not a multi-column min-p, and the decision does **not** consult any BH list.

Descriptive (not used for the decision): number of eligible groups (size ≥ 4) that contain ≥ 1 such hit;
leave-one-group-out L after zeroing the group that carries the observed max-k hit.

## Null
Within-khipu permutation of pendant values; group IDs fixed (structure-preserving, same family as K031–K033).
R = 20 000 for the confirmation p-values.

## p-value
For each named khipu,

    p = (1 + #{null draws with L ≥ L_obs}) / (1 + R).

## Decision rule (Bonferroni × 2)
α_i = 0.025 per named khipu.
- khipu **confirmed** iff p ≤ 0.025 and the FPR gate passes;
- khipu **not confirmed** iff p > 0.025 and its plant power ≥ 0.5;
- khipu **not testable** iff p > 0.025 and power < 0.5.

Overall (written before any run):
1. **CONFIRMED** if both named khipus are confirmed.
2. **PARTIAL** if exactly one is confirmed.
3. **NOT CONFIRMED** if neither is confirmed and both are testable.
4. **NOT TESTABLE** if neither is confirmed and at least one is not testable.
5. **EXCLUDED** if the FPR gate fails (do not claim confirmation).

## FPR gate (seed 3433)
Draw 200 random multi-group pop khipus **other than the two named** (seed 3433). For each, take one
within-khipu permutation as a null "observed" and compute its L p-value against R_fpr = 5 000 fresh
permutations of that same multiset. FPR = fraction with p ≤ 0.025.
**Pass** iff FPR ≤ 0.08 (one-sided binomial P(X ≥ x | n=200, 0.05) is reported; the hard gate is ≤ 0.08).

Also report, descriptively, the exchangeable tail rate on each named khipu's own 20 000 null L draws
(fraction with L ≥ the α=0.025 critical value) — expected ≈ 0.025 under the null.

## Power (seed 3432)
For each named khipu, N = 200 plants: permute, then plant **one** within-group exact sum of length **k = 6**
inside a group of size ≥ 8 (total pendant = sum of 6 consecutive neighbours with ≥ 2 nonzero; if no such
group exists, plant k = 5 in a group of size ≥ 7). Score each plant with R_pow = 5 000 nested permutations.
Power = fraction with p ≤ 0.025. Required ≥ 0.5 for a negative to be readable.

## Seeds
confirm KH0322 = 3430, confirm KH0420 = 3431, power = 3432, FPR = 3433
(all distinct from K031–K033).

## No claims
A confirmed L means "this khipu's longest within-group exact-sum window is longer than chance under
permutation", a property of the record. It is not a reading of the khipu. No decipherment is claimed.

## Results

Run 2026-11-05 ~11:51 PT (America/Vancouver), `timeout 560 python3 tools/k034_f1_holdout_confirmation.py ../khipu.db`
(20.9 s). Output: [`analysis/k034_results.json`](../analysis/k034_results.json).
Prereg + tool committed first as `cd00cbf`.

### 1. FPR gate — **pass**
200 random other multi-group pop khipus, one null "observed" each, R = 5 000: **5 / 200 = 0.025**
(≤ 0.08; binomial P(X ≥ 5 | n=200, 0.05) = 0.97). Structure tails on the named khipus' own nulls
sit near the nominal 0.025 (KH0322 0.031, KH0420 0.027).

### 2. Confirmation (R = 20 000; α = 0.025 each)

| Khipu | L_obs | null mean / p95 / p99 / max | p | Power (k=6 plants) | Verdict |
|---|---|---|---|---|---|
| KH0322 / UR086 | **8** | 1.96 / 5 / 6 / 8 | **0.00140** | 0.11 | **confirmed** |
| KH0420 / UR182 | **8** | 0.40 / 3 / 4 / 8 | **0.00020** | 1.00 | **confirmed** |

Descriptive: KH0322 has 2 hit groups of 18 eligible (max-k hit in group 2; LOO after zeroing it → L = 3).
KH0420 has 1 hit group of 4 eligible (max-k hit in group 6; LOO → L = 0). The signal in KH0420 is
carried by a single long window; in KH0322 a second, shorter hit remains after removing the longest.

Plant power for KH0322 is low (0.11) because a single k=6 plant in a 107-pendant / 23-group khipu rarely
pushes L past the α = 0.025 critical value (~6); that would matter for a *negative*, not for these
positives. KH0420's smaller frame recovers every plant.

### Reading
Both F1-only hits from K033 are **confirmed** under a statistic that never consults the BH ranking:
each khipu's longest within-group exact-sum window (L = 8) is rarer than chance under permutation
(Bonferroni × 2). The two new names on the calibrated F1 list are not BH artefacts.

**Decision: CONFIRMED (both named khipus; FPR gate passed).**

Next on line 1: silence still not testable (BH power 0.16–0.36 from K033); raise BH-level power
(stronger / multi-plant or stratified BH). The held-out confirmation fork for KH0322/KH0420 is closed.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
