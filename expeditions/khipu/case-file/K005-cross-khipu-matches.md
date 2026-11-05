# K005 · Do different khipus share long runs of identical values?

## Pre-registration (written before any K005 code was run)
- **Question (README line 3).** Do pairs of *different* khipus share contiguous runs of identical pendant values
  more than chance predicts, once value frequencies are accounted for? Matching khipus are known in the
  literature (e.g. UR267A and UR267B); the question is which pairs beat a calibrated null.
- **Data.** OKR `khipu.db` (sha256 `6079130…c4db`), duplicate-flagged records removed, level-1 pendants in
  `CORD_ORDINAL` order, cord value = sum of `knot_value_type`; khipus with at least 10 nonzero pendants (457).
- **Pair statistic.** A *shared block* is a run of at least 3 consecutive nonzero pendants whose values are
  identical, in order, in both khipus. Its information is the sum over its values of −log2 f(v), where f is the
  corpus frequency of that nonzero value (computed once, on the real data). The pair statistic I(a, b) is the
  largest information among the shared blocks of the pair, or 0. Blocks are found by indexing 3-grams of nonzero
  values; 3-grams that occur more than 300 times in the corpus are not used as seeds (such blocks are
  low-information anyway).
- **Null.** Each khipu's pendant values are permuted independently (keeps every khipu's value multiset and length).
- **Multiple comparisons.** Family-wise error control by the max statistic (Westfall–Young). Over R = 200 null
  corpora, take the maximum of I over all pairs; the threshold T is the 95th percentile. A pair is significant
  if I(a, b) > T. Adjusted p for each pair = (1 + #replicates with max ≥ I) / (1 + R).
- **Calibration check.** Threshold from the first 150 replicates; rate at which the last 50 exceed it (should be
  about 0.05).
- **Planted control.** 100 times: pick a null corpus, two random khipus, copy a run of 6 consecutive pendants
  (with at least 5 nonzero) from one into the other at a random place; report recovery (planted pair > T).
- **Classification of significant pairs (fixed now).** *Probable duplicate record* if the two records share a
  museum number, or the shared block covers at least half of the shorter khipu's nonzero pendants; otherwise
  *inter-khipu match*. Duplicates would be a data-quality note for the OKR, not an Inka finding.

## Results (run once, `python3 tools/k005_cross_khipu.py data/khipu.db`, 18 s; output `analysis/k005_results.json`)
| Quantity | Value |
|---|---|
| Khipus / pairs | 457 / 104 196 (9 245 pairs share at least one 3-value block) |
| Family-wise threshold T (95th pct of null max, R = 200) | 51.8 bits (null max median 37.7) |
| Calibration: last 50 replicates above T from first 150 | 0.02 (target 0.05; slightly conservative) |
| Planted 6-cord copies recovered | **0.11** (median planted information 28 bits, below T) |
| Significant pairs (FWER 0.05) | 5 (1 classified duplicate, 4 inter-khipu) |

| Pair (OKR / investigator) | Museums | Shared block | Bits | p_adj | Pre-registered class | Note after inspection |
|---|---|---|---|---|---|---|
| KH0140 AS125 · KH0483 UR247 | Berlin VA42670 · Berlin VA 42610 | 12 (14 of 15 pendants identical at offset 0) | 161.6 | 0.005 | probable duplicate | The [Khipu Field Guide](https://www.khipufieldguide.com/catalog/KH0140.html) says KH0483 is a later recording of KH0140 and gives museum number VA42610. In `khipu.db` neither record is duplicate-flagged, and KH0140 says VA42670. Only pendant 13 differs (3130 vs 31111). |
| KH0362 UR122 · KH0049 AS038/HP036 | Göteborg 1938.45.0228 · Lima MNAAHP3550 | 12 (28 identical values at best offset) | 157.4 | 0.005 | inter-khipu | The Field Guide already lists KH0362 as the khipu "similar" to KH0049. Not new. |
| KH0277 UR047 · KH0449 UR211 | Larco · Berlin | 21 values, all `10` | 90.7 | 0.005 | inter-khipu | **Null artefact.** Each khipu has a long run of 10s. Within-khipu permutation breaks runs, so two run-rich khipus look matched. This is not evidence of a link. |
| KH0128 UR1114 · KH0137 UR1123 | Berlin VA16148 · VA47085 (Ica / Ica–Pisco) | 10 | 70.8 | 0.010 | inter-khipu | Same museum and region. A plausible related-record pair; not checked against literature yet. |
| KH0305 UR068 · KH0301 UR064 | Puruchuco 2 · Puruchuco #3 | 10 (18 identical at offset 0) | 61.0 | 0.020 | inter-khipu | Puruchuco matching khipus are known from Urton & Brezine's work. Replication of known structure. |

## Verdict
- **Excluded:** nothing. **Not testable:** short shared blocks (power 0.11 for 6-cord copies), so silence for any
  other pair is *not* evidence of independence.
- Long shared blocks are found, and the clearest ones are already known (one unreconciled double recording, one
  catalogued similar pair, one Puruchuco pair). One flag is a null artefact (runs), which I disclose rather than drop.
- **Data-quality note for the OKR:** KH0140/KH0483 is a double recording of one object that is not flagged as a
  duplicate in `khipu.db`, with conflicting museum numbers. Any corpus statistic counts it twice (it did here).
- **Fixes for a K006 version:** a run-preserving null (permute runs of equal values as blocks), and a power-aware
  statistic for short blocks (exact chance probability given both khipus' value multisets).
