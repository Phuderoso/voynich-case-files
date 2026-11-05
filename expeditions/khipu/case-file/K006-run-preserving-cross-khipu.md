# K006 · Cross-khipu matches, take two: a run-preserving null and a composition-aware score

## Why (audit of K005)
K005 flagged UR047/UR211 only because each khipu holds a long run of `10`s and the K005 null (free permutation)
breaks runs. K005 also had power 0.11 for a planted 6-cord copy. K006 fixes both, pre-registered here before any
K006 code was run.

## Pre-registration
- **Data and corpus.** As K001–K005 (OKR `khipu.db` @ `4039ca5`, 457 khipus, level-1 pendants, `CORD_ORDINAL` order).
- **Null (structure-preserving).** Split each khipu into maximal runs of equal consecutive values (zeros included)
  and permute the runs as blocks. This keeps each khipu's value multiset, its run-length multiset and its length.
- **Score S (primary).** For a shared block (≥ 3 consecutive nonzero, identical values, maximal) between khipus a and b,
  S = −log2[ n_a · n_b · Π_v p_a(v) · p_b(v) ], where n is the khipu's pendant count and p_k(v) the frequency of v
  inside khipu k. This is a Bonferroni-style bound on the chance of that exact block appearing in both by
  coincidence, adapted to each khipu's own composition. Pair score = max over its blocks.
- **Error control.** Max-statistic FWER: T = 95th percentile of the corpus-wide maximum of S over R = 200 null
  corpora. Calibration: threshold from the first 150, exceed rate in the last 50.
- **Planted control.** As K005 (100 copies of a 6-cord run with ≥ 5 nonzero, into a null corpus). **Success target:
  recovery ≥ 0.5.** If missed, short matches stay *not testable*.
- **Secondary (audit).** K005's information score I under the run-preserving null, to see whether UR047/UR211
  survives.
- **Classification.** As K005 (shared museum number or block ≥ half the shorter khipu's nonzero pendants → probable
  duplicate record). A significant pair not in K005's five, and not catalogued as similar, would be a new candidate.

## Disclosure
The first run crashed in the planted-control stage (a `KeyError`: the within-khipu frequencies were fixed from
the real data, so a planted value new to the receiving khipu had no entry). No results had been printed. I changed
the score to use the frequencies of the corpus being scored (identical to the real ones under the null, because
the null keeps every multiset) and reran everything with the same seed.

## Results (`python3 tools/k006_run_null.py data/khipu.db`, 89 s; output `analysis/k006_results.json`)
| Quantity | S (primary) | I (K005 score, audit) |
|---|---|---|
| FWER threshold (R = 200, run-preserving null) | 49.9 | 120.9 bits (K005 under free permutation: 51.8) |
| Calibration, last 50 above first-150 threshold | 0.02 | 0.00 |
| Planted 6-cord copies recovered | **0.23** (target 0.5, **missed**) | 0.00 |
| Significant pairs | 5 | 2 |

Significant under S, all with p_adj ≤ 0.01:

| Pair | Museums | Block | S | Status |
|---|---|---|---|---|
| KH0362 UR122 · KH0049 AS038/HP036 | Göteborg · Lima | 12 | 140.2 | Known (Field Guide "similar") |
| KH0128 UR1114 · KH0137 UR1123 | Berlin VA16148 · VA47085 | 10 | 117.2 | Also in K005; not yet checked against literature |
| KH0140 AS125 · KH0483 UR247 | Berlin | 12 | 87.0 | Double recording (see K005) |
| KH0305 UR068 · KH0301 UR064 | Puruchuco | 10 | 77.2 | Puruchuco set (Urton & Brezine) |
| KH0304 UR067 · KH0303 UR066 | Puruchuco s/n · Puruchuco 4a | 7 | 58.0 | **New in K005/K006**, but again within the Puruchuco set |

## Verdict
- **Audit of K005, confirmed:** the UR047/UR211 flag was a null artefact. Under a run-preserving null it is gone
  on both scores. K005's table is annotated accordingly; its other four pairs survive.
- The composition-aware score doubles power (0.11 → 0.23) and finds one more pair (UR067/UR066), but it misses the
  pre-registered target, so **short shared runs remain not testable**. No claim of independence for unflagged pairs.
- The I score is unusable under the run-preserving null (power 0): long runs of one value dominate its null maximum.
- Every significant pair is either a known relationship or inside the Puruchuco set, which is already known to
  hold linked khipus. Nothing new enough to report outward.
- **Line 3 status:** long matches mapped. Next possible step: an exact per-pair probability with a pair-specific
  null (instead of a corpus maximum), which needs a different error-control route (BH over exact p-values).
