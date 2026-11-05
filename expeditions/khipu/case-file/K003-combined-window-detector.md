# K003 · Combining short and long sum windows, and a size-matched look at the UR excess

## Pre-registration (written before any K003 code was run)
- **Why.** K002's frozen detector D2 (log10-weighted adjacent sums, k ≤ 6) reached 0.63 planted recovery on short
  sums but no gain on long ones (0.36 on plants with k from 2 to 10). K002's README line 1 asks for a detector
  that keeps both without paying for the extra windows with false positives. Line 5 asks whether the UR-series
  excess survives once khipu size is held fixed.
- **Data, cord value, relation, null.** As in K002 (OKR `khipu.db`, sha256 `6079130…c4db`; 457 khipus; R1 adjacent
  sums with v ≥ 10, at least two nonzero summands; N1 within-khipu permutation of pendant values).
- **Candidates.** For each k, let W_k = sum of log10(v) over pendants that equal a k-block sum (left or right).
  D2 = log-weighted hits for any k ≤ 6 (K002 baseline). D4 = min-p over two scores, short (k 2..6) and long
  (k 7..12). D5 = min-p over the 11 per-k scores W_2..W_12. Min-p is calibrated against its own null: each null
  draw's per-score p is its rank among the null draws, and the final p is the share of null draws whose min-p is
  at most the observed one, p = (1 + #) / (1 + K).
- **Stage 1, development (seed 4004, K = 300).** Calibration FPR (shuffled copy treated as real) and recovery at
  p ≤ 0.05 for plant spec A (two cords = sum of the next 3) and spec B (two cords, k uniform in 2..10, either side).
  **Selection rule:** among candidates with FPR ≤ 0.05, highest mean of spec-A and spec-B recovery; ties go to the
  earlier candidate in the order D2, D4, D5. (The criterion changed from K002, which used spec A only and so
  favoured short windows; this is declared here, before running.)
- **Stage 2, evaluation (fresh seed 5005, K = 500).** **Success:** FPR ≤ 0.05, spec-A recovery ≥ 0.80 and spec-B
  recovery ≥ 0.60. Also reported: recovery by khipu size (thirds of pendant count).
- **Stage 3, corpus (seed 6006).** Frozen detector; K = 1000, then a fresh K = 20000 for khipus with p ≤ 0.01;
  BH-FDR q = 0.05 over all 457. Silence may be called "no detectable sum structure at this power" only if stage 2
  succeeds; otherwise it stays *not testable*.
- **Line 5, size-matched UR test.** On the stage-3 BH flags: statistic = number of UR-series khipus among the
  flagged; null = permute the UR label within quintiles of pendant count (100 000 permutations, seed 7007);
  one-sided p. **Rule:** p ≤ 0.05 means the UR excess is not explained by size alone; otherwise the K002 excess is
  attributed to size (not *excluded* as a convention, just not supported).

## Deviation, stated openly
The first development run had a bug in the min-p code: a candidate's p was set to 1 whenever its *first* score was
zero, even if another score hit. That crippled D4 and D5 (recovery about 0.2). I fixed the one line and reran
**stage 1 only**, with the same seed and the same rule; stage 2 and 3 had not been run. The buggy output is kept
as `analysis/k003_dev_buggy.json`.

## Results
**Stage 1, development (seed 4004, K = 300, after the fix).**

| Candidate | FPR at p ≤ 0.05 | Spec A | Spec B | Mean |
|---|---|---|---|---|
| D2 (K002) | 0.031 | 0.60 | 0.39 | 0.50 |
| D4 (min-p, short/long) | 0.026 | 0.55 | 0.56 | 0.56 |
| D5 (min-p, per k) | 0.039 | 0.66 | 0.56 | **0.61** |

By the rule, **D5** was frozen.

**Stage 2, evaluation (fresh seed 5005, K = 500).**

| Detector | FPR | Spec A | Spec B | Spec A by size (small / mid / large) | Spec B by size |
|---|---|---|---|---|---|
| D2 | 0.037 | 0.57 | 0.41 | 0.63 / 0.55 / 0.53 | 0.44 / 0.41 / 0.38 |
| D5 | 0.046 | 0.66 | 0.59 | 0.73 / 0.71 / 0.56 | 0.61 / 0.64 / 0.51 |

Size thirds: up to 37, 38 to 86, and more than 86 pendants (khipus with at least 20 pendants).

**The success criterion failed again**, though narrowly on spec B (0.59 against 0.60) and clearly on spec A
(0.66 against 0.80). D5 is the best detector so far on long sums (+18 points over D2), with a false-positive
rate close to the 0.05 limit. Silence in unflagged khipus stays *not testable*.

**Audit of K002.** K002 explained the UR excess by assuming "power grows with size". The plant data contradict
that: recovery is **lowest** on the largest khipus, because long khipus contain more chance sums. K002's
mechanism was wrong; the size question itself still needed a test, which follows.

**Stage 3, corpus (seed 6006; 26 khipus re-run at K = 20000).** **20 of 457 pass BH-FDR q = 0.05.** 14 of K002's 16
are kept; KH0068 (UR1057) and KH0502 (UR266, p = 0.0073) drop below the line. Six are new: KH0143 (AS128),
KH0218 (AS200), KH0395 (UR155), KH0424 (UR186), KH0428 (UR190), KH0478 (UR242). **All 10 of K001's detections are
flagged by all three detectors**, the most robust set so far.

**Line 5, size-matched UR test (pre-registered).** 17 of the 20 flagged khipus are UR-series (304 UR in the
corpus). Permuting the UR label within pendant-count quintiles gives **p = 0.175**: the UR excess is **not
supported** once size is held fixed. Flagged khipus sit mostly in the two largest quintiles (14 of 20), and those
quintiles are mostly UR (143 of 185). This doesn't *exclude* a UR convention; it says the corpus can't tell it
apart from "bigger khipus carry more detectable sums".

| Pendant-count quintile | Khipus | UR | Flagged | Flagged UR |
|---|---|---|---|---|
| ≤ 22 | 90 | 46 | 0 | 0 |
| 23–34 | 91 | 57 | 3 | 3 |
| 35–62 | 91 | 58 | 3 | 1 |
| 63–108 | 91 | 64 | 6 | 6 |
| > 108 | 94 | 79 | 8 | 7 |

Raw output: `analysis/k003_dev.json`, `analysis/k003_eval.json`, `analysis/k003_corpus.json`.
Re-run: `python3 tools/k003_combined_window.py data/khipu.db dev`, then `eval D5`, then `corpus D5` (about 2 minutes).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
