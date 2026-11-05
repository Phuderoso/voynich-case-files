# C002 — Audit of C001: is the page-permutation null calibrated, and does the C001 verdict survive a repaired null?

**Status:** pre-registered 2026-11-04 21:23 PT (before any run). Results appended below.
**Type:** audit / correction of [C001](C001-section-vs-hand-vs-currier.md). Same approach family as C001, so the next
cycle (C003) must try a family not yet in the coverage table.

## Why
In C001's K = 1000 sensitivity run, the destroyed-signal control C1 gave p = 0.004 on T4. That is either a null that
leaks (anti-conservative) or one unlucky draw among 5 looks. One C1 shuffle cannot tell these apart. This cycle
measures the false-positive rate directly over many independent C1 shuffles.

## Data
Same as C001: `data/ZL3b-n.txt` (ZL 3b, sha256 `bf5b6d4a…ccafc`), same tokenisation, same 196 pages, same labels.

## Metric
Same statistic as C001: conditional MI I(W; X | Y) on token counts, top-K word types + OTHER.

## Nulls compared
- **N0 (C001 null):** permute X among pages within each Y stratum.
- **N1 (size-blocked):** within each Y stratum, sort pages by token count, cut into consecutive blocks of 4 pages
  (last block absorbs the remainder), permute X only within blocks. Keeps label-to-token-mass roughly fixed.

## Calibration experiment
R = 40 independent C1 replicates (words shuffled globally across pages, page sizes kept; seeds 1..40).
For each replicate, K ∈ {300, 1000}, null ∈ {N0, N1}: p-values for T1–T5 with 200 permutations each
→ 200 p-values per (K, null) cell.

**Calibrated** = observed fraction of p ≤ 0.05 is ≤ 0.09 AND fraction of p ≤ 0.01 is ≤ 0.03
(binomial 99% upper limits for a correct test with n = 200, allowing for p-value discreteness).
Uniformity also reported with a KS statistic (descriptive only).

## Power check
C2 planted control (3% hand-2 token on C1 text, 20 replicates): fraction of replicates where T1 is flagged at p ≤ 0.01
under each null. A null that is calibrated but has power < 0.8 on C2 is "calibrated but weak".

## Voynich re-run (pre-registered looks)
T1–T5 from C001 plus **T6 I(W;H | S×L)** (hand beyond section and Currier jointly; strata = section×language cells),
at K = 300 and K = 1000, under the best calibrated null (N1 if both calibrated, since it is the stricter one),
2000 permutations. 6 tests × 2 K = 12 looks → Bonferroni α = 0.05/12 = 0.0042.

## Decision rule
- If N0 is calibrated at both K: the C001 K=1000 C1 hit is recorded as a chance draw, C001 stands; correction note says so.
- If N0 fails calibration at some K: C001's statements at that K are withdrawn and replaced by the N1 re-run.
- C001 verdict "hand and section each carry information beyond the other" **survives** if T1 and T2 both reach
  p ≤ 0.0042 at both K under a calibrated null; **weakened** if only at one K; **withdrawn** if neither.
- T6: p ≤ 0.0042 → "hand carries vocabulary information beyond section and Currier language jointly";
  otherwise "no detectable extra information" (not "excluded"); "not testable" if < 2 strata vary in hand.
- If no null is calibrated, no Voynich verdict is issued this cycle.

---
## Results (run 2026-11-04 ~21:30 PT, `tools/c002_null_audit.py`)
Outputs: `analysis/C002_calib.json` (sha256 `0e82e487…c763c`), `C002_power.json` (`a7fcec77…6565`),
`C002_summary.json` (`dfabc5be…c7`), `C002_voynich_N0.json` (`ba9cc43d…c2`), `C002_voynich_N1.json` (`6e87c32f…d2`).

### Calibration (40 destroyed-signal replicates × 5 tests = 200 p-values per cell)
| K | Null | share p ≤ 0.05 | share p ≤ 0.01 | KS vs uniform | Calibrated? |
|---|---|---|---|---|---|
| 300 | N0 (C001) | **0.435** | **0.225** | 0.42 | **No** |
| 300 | N1 size-blocked | 0.050 | 0.010 | 0.05 | Yes |
| 1000 | N0 (C001) | **0.345** | **0.260** | 0.31 | **No** |
| 1000 | N1 size-blocked | 0.085 | 0.035 | 0.09 | No (just over the 0.03 limit) |

Per test, the N0 leak sits in the tests whose strata are big and uneven: share of p ≤ 0.05 was 0.80 (T4) and 0.875 (T5)
at K=300, 1.00 (T4) and 0.725 (T5) at K=1000, versus 0.0 for T1 and T3. Under N1 the worst single test was T2 at K=300
(0.15, 6 of 40) and T5 at K=1000 (0.40).

### Power (C2 planted 3% hand-2 token, 20 replicates, share with T1 p ≤ 0.01)
N0: 1.00 (K=300), 0.25 (K=1000). N1: 0.85 (K=300), 0.10 (K=1000). Only N1 at K=300 is both calibrated and powered.

### Voynich re-run (2000 permutations, min p = 0.0005; Bonferroni α = 0.0042)
| Test | K=300 N1 excess (z, p) | K=1000 N1 excess (z, p) | K=300 N0 z (for comparison) |
|---|---|---|---|
| T1 I(W;H\|S) | 0.0475 bits (10.3, 0.0005) | 0.0596 (9.9, 0.0005) | 17.1 |
| T2 I(W;S\|H) | 0.0303 (6.5, 0.0005) | 0.0422 (5.9, 0.0005) | 17.1 |
| T3 I(W;L\|S) | 0.0481 (11.6, 0.0005) | 0.0613 (11.0, 0.0005) | 21.1 |
| T4 I(W;S\|L) | 0.0577 (8.7, 0.0005) | 0.0770 (9.1, 0.0005) | 24.7 |
| T5 I(W;H\|L) | 0.0335 (6.2, 0.0005) | 0.0459 (6.0, 0.0005) | 13.0 |
| **T6 I(W;H\|S×L)** | 0.0049 (1.7, **0.081**) | 0.0070 (1.8, 0.034) | 1.6 |

### Verdict (pre-registered rule)
1. **Correction to C001: its null was not calibrated.** The page-permutation null N0 gives false positives on
   destroyed-signal text 35–44% of the time at α = 0.05. C001's single C1 run passing was luck. All C001 p-values and
   z-scores are withdrawn and replaced by the N1 numbers above.
2. **C001 verdict weakened, not withdrawn.** Under the calibrated N1 at K=300, T1–T5 all reach p = 0.0005, with
   excesses about half of what C001 reported (e.g. T2 0.030 vs 0.059 bits). At K=1000 no null is calibrated, so no verdict
   there. The rule asked for both K, so the status is "weakened". T2 needs extra caution, because it was the worst-calibrated
   test under N1 (15% at α = 0.05), though the Voynich z of 6.5 is far beyond anything that implies.
3. **New: T6 — the LFD hand adds no detectable vocabulary information once section and Currier language are both held
   fixed** (p = 0.081 at K=300; not "excluded"). Only 3 section×language cells contain more than one hand, so this has
   limited power. But it means C001's "scribe beyond section" result can be carried by the Currier A/B split alone.

### What this does not show
- N1 is a repair, not a proof of exactness: blocks of 4 pages by size are a coarse match, and N1 loses power fast as
  the vocabulary grows. A token-mass-exact null (or a bias-corrected MI estimator) is still open.
- T6 "no detectable" is limited by power; a planted test inside the 3 informative cells was not run.
- The destroyed-signal control removes within-page burstiness, so it checks the null's calibration only for that
  structure, not for every way real pages differ.

### Lesson for every later cycle
Calibrate a null with **many** destroyed-signal replicates, not one. One passing control run says almost nothing.
