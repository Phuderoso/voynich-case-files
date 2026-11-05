# K008 · Do K001 and K004 survive without multi-number cords?

## Pre-registration (written before any K008 code was run)
- **Question (README line 8).** K007 found that about one pendant in ten carries more than one number (an "R5"
  cord), and our cord value (the plain sum of knot values) blends them. Do the two main results so far, K001's
  adjacent sum cords and K004's pendant = sum of its own subsidiaries, still hold when those cords are masked?
- **Data.** OKR `khipu.db` @ `4039ca5` (sha256 `6079130…c4db`), duplicate-flagged records removed, as before.
- **R5 cord (same as K007).** At least two knot clusters with a single decimal place, and those places, read in
  `knot_cluster.ORDINAL` order, are not strictly decreasing.
- **Masking (structure-preserving).** An R5 cord keeps its position but is never a sum target and never part of a
  summand block (K001), and is never an eligible parent nor counted among a parent's subsidiaries; a parent with
  any R5 subsidiary is ineligible (K004). Nulls permute only non-R5 values among non-R5 positions. Statistics,
  window sizes and thresholds are otherwise exactly those of K001 and K004.
- **K001 test.** Same 457 eligible khipus. Khipus with no R5 cord keep their K001 p (identical data and
  statistic). Khipus with R5 cords: masked N1 null, K = 5000; calibration (one masked shuffle treated as real,
  K = 2000). BH-FDR q = 0.05 over all khipus with at least 10 nonzero unmasked pendants.
- **K004 test.** Corpus test under N_a, K = 10000, with and without KH0349 (UR113); KH0349 alone, K = 20000.
  Controls: 20 shuffled masked corpora (calibration, FPR at 0.05) and 20 shuffled masked corpora with 10 planted
  hits each (power at p ≤ 0.01).
- **Decision rules.** A K001 khipu **survives** if it is BH-significant after masking. K004's corpus result
  **survives** if masked p ≤ 0.01 (its original rule). The non-UR113 K004 signal stays "suggestive" unless masked
  p without KH0349 is ≤ 0.01. A khipu with fewer than 10 nonzero unmasked pendants is **not testable**, not lost.
- **Out of scope this cycle.** K002, K003, K005 and K006 are not rerun; line 8 stays open for them.

## Results
3 069 cords in the database are R5 cords (K007's count). Run time 149 s, one run, no crashes, no amendments.

**K001 (adjacent sums), masked.** 457 khipus as in K001; 215 contain R5 pendants; 24 drop below 10 nonzero unmasked
pendants and become **not testable**; 433 tested. Calibration on the 191 re-run khipus: FPR 0.010 at p ≤ 0.05.

| Khipu | R5 pendants | Hits K001 → masked | p K001 → masked | BH after masking |
|---|---|---|---|---|
| KH0359 UR119 | 5 | 9 → 8 | 0.0002 → 0.0002 | survives |
| KH0405 UR166 | 0 | 4 → 4 | 0.0002 (unchanged data) | survives |
| KH0491 UR255 | 12 | 10 → 4 | 0.0002 → 0.0026 | **lost** |
| KH0492 UR256 | 13 | 8 → 5 | 0.0002 → 0.0004 | survives |
| KH0503 UR267A | 14 | 16 → 10 | 0.0002 → 0.0002 | survives |
| KH0504 UR267B | 17 | 13 → 9 | 0.0002 → 0.0002 | survives |
| KH0506 UR269 | 21 | 17 → 15 | 0.0002 → 0.0002 | survives |
| KH0507 UR270 | 22 | 5 → 4 | 0.0008 → 0.0022 | **lost** |
| KH0513 UR274B | 1 | 3 → 3 | 0.0006 → 0.0004 | survives |
| KH0514 UR275 | 13 | 10 → 7 | 0.0002 → 0.0002 | survives |

**8 of K001's 10 survive; no new khipu becomes significant.** The two lost ones stay nominally low (p ≈ 0.002) but
miss the BH bar over 433 tests. Masking also removes summand windows, so this is **"no longer established"**, not
"excluded": part of their K001 signal ran through cords that carry two numbers.

**K004 (pendant = sum of own subsidiaries), masked.** 178 khipus, 1 144 eligible parents (was 197 and 1 315).
Calibration 0 of 20 shuffled corpora at p ≤ 0.05; planted power (10 hits) 0.85 at p ≤ 0.01.

| | Hits | Null mean | Null max | p | Rule |
|---|---|---|---|---|---|
| Corpus, masked | 24 (was 25) | 5.67 | 18 | 0.0001 (floor) | **survives** |
| Corpus without KH0349, masked | 11 (was 12) | 4.70 | 15 | **0.006** (was 0.019) | meets ≤ 0.01 |
| KH0349 UR113 alone, masked | 13 (unchanged) | | | 0.00005 (floor) | survives |

## Verdict
- K001's adjacent-sum result is **robust for 8 of 10 khipus**; KH0491 (UR255) and KH0507 (UR270) are downgraded to
  not established. K004's corpus result is **robust**: none of UR113's 13 hits used a multi-number cord.
- Outside UR113, the K004 signal crosses the pre-registered bar after masking (p = 0.006). I report it as
  **meeting the rule but not independently replicated**: it is a second analysis of the same 11 scattered hits, the
  improvement comes from a cleaner null (fewer noisy cords), and the original "without UR113" test was itself not
  pre-registered. Line 7's held-out replication stays the proper test.
- K002, K003, K005 and K006 not rerun yet; line 8 stays open for them.

Raw output: `analysis/k008_results.json`. Re-run: `python3 tools/k008_multinumber_sensitivity.py data/khipu.db`
(about 2.5 minutes, needs numpy).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
