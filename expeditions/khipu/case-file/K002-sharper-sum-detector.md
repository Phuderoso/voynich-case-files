# K002 · A sharper sum-cord detector, tuned blind and evaluated on fresh plants

## Pre-registration (written before any K002 code was run)
- **Why.** K001's detector caught only 38% of planted sum cords, so silence in 447 khipus was *not testable*.
  K002 tries to build a detector with at least **80%** planted recovery at a calibrated false-positive rate,
  without tuning it on the real corpus.
- **Data, cord value, inclusion.** Same as K001 (OKR `khipu.db`, sha256 `6079130…c4db`, level-1 pendants in
  `CORD_ORDINAL` order, duplicates removed, at least 10 nonzero pendants: 457 khipus).
- **Relations.** R1 = a pendant with value v ≥ 10 equals the sum of the next k or previous k pendants
  (k = 2..12, at least two of them nonzero), as in K001. R2 = a pendant with v ≥ 10 equals the total of a whole
  cord group that does not contain it (group with at least two nonzero pendants).
- **Candidate statistics.** D0 = K001 count of R1 pendants. D1 = sum of log10(v) over R1 pendants (big exact
  matches count more, because they are rarer by chance). D2 = D1 with k limited to 2..6. D3 = D1 plus R2 pendants
  (each pendant counted once).
- **Null.** N1, within-khipu permutation of pendant values. p = (1 + #null ≥ obs) / (1 + K).
- **Stage 1, development (seed 1001, K = 300).** For each candidate: calibration FPR (a shuffled copy treated as
  real) and planted recovery at p ≤ 0.05 under plant spec A (K001's spec: two cords set to the sum of the next 3).
  **Selection rule:** among candidates with FPR ≤ 0.05, take the highest spec-A recovery; ties go to the
  lower-numbered candidate. The choice is then frozen.
- **Stage 2, evaluation (seed 2002, K = 500, fresh shuffles and plants).** Report FPR, spec-A recovery and spec-B
  recovery (two sum cords, k drawn uniformly from 2..10, left or right at random), for the frozen detector and D0.
  **Success:** FPR ≤ 0.05 and spec-A recovery ≥ 0.80. Spec B is reported as a harder, untuned check.
- **Stage 3, corpus (seed 3003).** Frozen detector on all 457 khipus. Two-stage Monte Carlo: K = 1000 for every
  khipu; khipus with p ≤ 0.01 get a fresh K = 20000 run whose p replaces the first. (This is conservative: for
  t < 0.01, P(final p ≤ t) ≤ P(second-run p ≤ t) = t.) BH-FDR q = 0.05 across all 457.
  **Interpretation rule:** if stage 2 fails, corpus results are reported but silence stays *not testable*; if it
  succeeds, khipus that are not significant can be called *no detectable sum structure at this power* (still not
  "absent").
- **Audit of K001.** Report how many of K001's 10 detections the new detector also flags.

## Results
**Stage 1, development (seed 1001, K = 300).** All four candidates are calibrated.

| Candidate | Calibration FPR at p ≤ 0.05 | Spec-A recovery |
|---|---|---|
| D0 (K001 count) | 0.018 | 0.38 |
| D1 (log-weighted) | 0.037 | 0.52 |
| D2 (log-weighted, k ≤ 6) | 0.037 | **0.62** |
| D3 (D1 + whole-group totals) | 0.037 | 0.42 |

By the selection rule, **D2** was frozen. Adding whole-group totals (D3) *lowered* power: group totals mostly add
chance matches.

**Stage 2, evaluation (fresh seed 2002, K = 500).**

| Detector | FPR at p ≤ 0.05 | Spec-A recovery (sum of next 3) | Spec-B recovery (k from 2 to 10) |
|---|---|---|---|
| D0 | 0.018 | 0.37 | 0.37 |
| D2 | 0.026 | **0.63** | 0.36 |

**The success criterion failed.** Recovery rose from 37% to 63% on the K001 plant, short of the 80% target, and
on the harder, untuned plant D2 is no better than D0, because limiting k to 6 throws away the long sums that D0
still catches. So the gain is partly specific to short sums. By the pre-registered rule, silence in khipus that
are not significant remains *not testable*.

**Stage 3, corpus (seed 3003; K = 1000, then a fresh K = 20000 for 18 khipus with p ≤ 0.01).**
**16 of 457 khipus pass BH-FDR q = 0.05.** All 10 of K001's detections are kept; 6 are new:

| OKR | Investigator no. | Pendants | D2 | p |
|---|---|---|---|---|
| KH0447 | UR209 | 71 | 5.70 | 0.00005 |
| KH0502 | UR266 | 132 | 6.81 | 0.00025 |
| KH0027 | AS026A | 54 | 3.74 | 0.00085 |
| KH0068 | UR1057 | 557 | 3.62 | 0.00115 |
| KH0385 | UR145 | 32 | 5.37 | 0.00125 |
| KH0168 | UR1152 | 80 | 6.93 | 0.00160 |

The 0.00005 floor (1/20001) is reached by 9 khipus: KH0359, KH0405, KH0447, KH0491, KH0492, KH0503, KH0504,
KH0506, KH0514.

**Exploratory, not pre-registered (line 5, "why all UR?").** 15 of 303 UR-series khipus are significant against 1
of 154 others (one-sided hypergeometric p = 0.012). The first non-UR detection (AS026A) breaks K001's
"all UR". But UR khipus are larger (median 59 pendants against 33), and power grows with size, so this is
**confounded by size** and is not evidence of a regional or recorder convention until a size-matched test is run.

## Reading
- A real improvement (+26 points of recovery on the reference plant, same calibration) that found 6 more khipus,
  but **not** the detector K002 promised. Honest status: line 1 *advanced, not closed*.
- The weakness is now located: weighting helps, the k-window trades short-sum power against long-sum power.
  The next detector should combine windows without paying the multiple-window penalty (e.g. a max over
  per-k calibrated scores), and power should be reported by khipu size.

Raw output: `analysis/k002_dev.json`, `analysis/k002_eval.json`, `analysis/k002_corpus.json`.
Re-run: `python3 tools/k002_sharper_detector.py data/khipu.db dev`, then `eval D2`, then `corpus D2`
(about 1 minute in total).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
