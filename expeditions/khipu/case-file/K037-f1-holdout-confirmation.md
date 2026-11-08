# K037 · Held-out confirmation of fixed-K F1 candidates KH0502/UR266 and KH0511/UR273B (README line 1)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K037 confirmation statistic was computed.

## Why
K036's fixed-K = 10 000 F1 scan (D5w, pooled exchangeable min-p, BH-FDR) was adopted as the line-1 reference
list (14 names). Two names on it are new against K033 and K035 (`only_K036` = `candidates_new`):
**KH0502/UR266** (p 0.00089991, cnt 9) and **KH0511/UR273B** (p 0.00159984, cnt 16). K035 had noted both
descriptively under stratified BH. K036 flagged them as **candidates, not claimed**, pending a held-out test.
A BH ranking is a discovery tool, not a confirmation. This cycle tests the two named khipus with the
**K034 design unchanged**: a secondary statistic that does not reuse the corpus BH ranking of D5w min-p.
No new test is invented; only names, seeds and file names change.

## Named targets (fixed)
1. KH0502 / UR266
2. KH0511 / UR273B

OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`),
level-1 pendants, same group definition as K031–K036 (`CLUSTER_ID` runs), duplicate-flagged khipus excluded and
khipus with < 10 nonzero pendants dropped, exactly as in K034's tool.

## Primary statistic L (per khipu)
**Longest within-group exact-sum window.** L = max k ∈ {2,…,12} such that some pendant with value ≥ 10 equals
the sum of k consecutive neighbours that lie entirely inside the same group, with ≥ 2 nonzero summands. The
within-group adjacency mask is identical to D5w's `valid_masks`. L is a **scalar**, and the decision does
**not** consult any BH list or D5w min-p ranking.

Descriptive (not used for the decision): number of eligible groups (size ≥ 4) that contain ≥ 1 such hit;
leave-one-group-out L after zeroing the group(s) that carry the observed max-k hit.

## Null
Within-khipu permutation of pendant values; group IDs fixed. R = 20 000 for the confirmation p-values.

## p-value
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
5. **EXCLUDED** if the FPR gate fails (no confirmation claimed).

## FPR gate (seed 3733)
200 random multi-group pop khipus (≥ 2 groups of size ≥ 4) **other than the two named**. For each, one
within-khipu permutation is a null "observed"; its L p-value is computed against R_fpr = 5 000 fresh
permutations. FPR = fraction with p ≤ 0.025. **Pass** iff FPR ≤ 0.08 (binomial P(X ≥ x | n=200, 0.05) reported).
Also reported: the exchangeable tail rate on each named khipu's own 20 000 null L draws.

## Power (seed 3732)
Per named khipu, N = 200 plants: permute, then plant **one** within-group exact sum of length **k = 6** inside a
group of size ≥ 8 (≥ 2 nonzero; fallback k = 5 in a group of size ≥ 7). Each plant scored with R_pow = 5 000
nested permutations. Power = fraction with p ≤ 0.025. Required ≥ 0.5 for a negative to be readable.

## Seeds
confirm KH0502 = 3730, confirm KH0511 = 3731, power = 3732, FPR = 3733
(distinct from K031–K036; K034 used 3430–3433, K036 used 3630 / 36310–36314 / 3632).

## Tool
[`tools/k037_f1_holdout_confirmation.py`](../tools/k037_f1_holdout_confirmation.py), a copy of K034's tool with
only targets, seeds and output path changed. Output: `analysis/k037_results.json`.

## No claims
A confirmed L means "this khipu's longest within-group exact-sum window is longer than chance under
permutation", a property of the record. It is not a reading of the khipu. No decipherment is claimed.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
