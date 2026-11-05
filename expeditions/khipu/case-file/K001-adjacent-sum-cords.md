# K001 · Adjacent sum cords against calibrated nulls

## Pre-registration (fixed in `tools/k001_sum_cords.py` before the first run)
- **Question.** Do pendant cords whose value equals the sum of the cords right next to them occur more often than
  chance, once the null is checked for calibration?
- **Data.** OKR `khipu.db` (see `data/MANIFEST.md`). Duplicate-flagged khipus removed. Only top-level pendants
  (`CORD_LEVEL = 1`), in `CORD_ORDINAL` order. Khipus with at least 10 nonzero pendants: **457**.
- **Cord value.** Sum of `knot_value_type` over the cord's knots. This is the database's own per-knot decimal
  decoding, so any recording or decoding error in the source passes through.
- **Statistic S.** Number of pendants with value at least 10 that equal the sum of the next k pendants to the right,
  or the previous k to the left, for some k from 2 to 12, with at least two of those k nonzero.
- **Nulls.** N1 permutes pendant values within the khipu (destroys all order). N2 permutes the order of whole cord
  groups but keeps the order inside each group (tests whether relations reach across group boundaries).
  p = (1 + number of null values at least S) / (1 + K).
- **Decision rule.** A khipu counts as showing sum structure if Benjamini–Hochberg FDR q ≤ 0.05 across all tested
  khipus. Valid only if the calibration control (a shuffled copy treated as real) gives a false-positive rate
  at or below 0.05 at p ≤ 0.05.
- **Planted control.** Shuffled copies with two planted sum cords (a cord set to the sum of the next three).

## Results
| Run | K | Calibration FPR at p ≤ 0.05 | Planted recovery at p ≤ 0.05 | Khipus p ≤ 0.05 (N1) | BH-significant (N1) | BH-significant (N2) |
|---|---|---|---|---|---|---|
| Pre-registered | 500 | 0.026 | 0.37 (388 khipus) | 27 | **0** | 0 |
| Amendment A1 | 5000 | 0.022 | 0.38 (388 khipus) | 26 | **10** | 0 of 367 |

**Amendment A1, stated openly.** At K = 500 the smallest possible p is 1/501 ≈ 0.002, which is above the BH
threshold for the top rank with 457 tests (0.05/457 ≈ 0.0001). The pre-registered run could not have found
anything under its own rule. I raised K to 5000 *after* seeing this, and changed nothing else: same statistic,
same seed, same rule. Treat A1 as a resolution fix that was decided after looking, not as a clean pre-registered
result.

Khipus significant under N1 at K = 5000 (S observed vs. null mean):

| OKR | Investigator no. | Pendants | Groups | S | Null mean | p (N2) |
|---|---|---|---|---|---|---|
| KH0359 | UR119 | 173 | 49 | 9 | 1.70 | 0.001 |
| KH0405 | UR166 | 30 | 12 | 4 | 0.12 | 0.002 |
| KH0491 | UR255 | 86 | 28 | 10 | 0.85 | 1.0 |
| KH0492 | UR256 | 118 | 24 | 8 | 0.57 | 1.0 |
| KH0503 | UR267A | 82 | 29 | 16 | 0.94 | 0.34 |
| KH0504 | UR267B | 103 | 26 | 13 | 0.55 | 1.0 |
| KH0506 | UR269 | 289 | 107 | 17 | 0.27 | 0.033 |
| KH0507 | UR270 | 162 | 25 | 5 | 0.77 | 1.0 |
| KH0513 | UR274B | 101 | 33 | 3 | 0.17 | 0.21 |
| KH0514 | UR275 | 112 | 26 | 10 | 0.18 | 1.0 |

## Reading
- The null is calibrated (it is conservative: 2.2% false positives against a 5% target), so the 10 detections are
  not an artefact of a leaky null, unlike Voynich C001.
- Adjacent sum relations are a known feature of accounting khipus (Ascher & Ascher; Urton); this is a replication
  with a calibrated null and a corpus-wide multiple-comparison correction, **not a new discovery**.
- Under N2 nothing survives BH. Most of these relations sit **inside** cord groups, not across group boundaries.
  KH0359 and KH0405 show nominal cross-group structure (p ≈ 0.001–0.002) worth a targeted look.
- **Weak detector.** Planted recovery is only 38%, so absence of significance in the other 447 khipus is
  *not testable* with this statistic, not *excluded*. A better detector is the first open line for K002.
- All 10 detections are UR-series records. That could be real (a regional or administrative genre) or a recording
  convention; it is not tested here.

Raw output: `analysis/k001_results_K5000.json`, `analysis/k001_results_K500.json`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
