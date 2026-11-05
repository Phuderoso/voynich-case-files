# K010 · A steadier family-wise threshold for cross-khipu matches

## Pre-registration (written before any K010 code was run)
- **Question (README line 3).** K009's calibration came out at 0.14 (7 of 50 held-out null maxima above the
  threshold, target 0.05). Is the cross-khipu threshold miscalibrated, or was that the noise of only 200 null
  corpora? Do K009's five pairs hold with a precise threshold?
- **Data and statistic.** Exactly K009: OKR `khipu.db` @ `4039ca5`, duplicates removed, multi-number (R5) pendants
  masked to 0, composition-aware score S, run-preserving null, max over all pairs.
- **Changes.** R = 1 000 null corpora (was 200), new seed. **Calibration by 4-fold cross-validation:** for each fold
  of 250 null maxima, the threshold is the 95th percentile of the other 750; report the pooled exceedance rate over
  all 1 000. Planted 6-cord copies: 200 (was 100).
- **Decision rules.** Calibration is **acceptable** if the pooled exceedance falls inside the 95% binomial range
  for a true rate of 0.05 over 1 000 checks (0.037 to 0.064); above 0.064 means the null is miscalibrated and the
  pairs' verdicts get re-examined. A pair **survives** if its adjusted p = (1 + #null maxima ≥ score) / 1 001 is at
  most 0.05. Short matches are testable only if planted recovery reaches 0.5.

## Results (`python3 tools/k010_steadier_threshold.py data/khipu.db`, 196 s, one run, no amendments)
**Calibration is acceptable: 0.051** for score S (0.049 for the information score), inside the pre-registered range
of 0.037 to 0.064. K009's 0.14 was the noise of a 50-check estimate, not a broken null. Threshold T = 47.1
(K009: 46.1 from 200 corpora).

| Pair | Block | Score | Adjusted p (R = 1 000) | Verdict |
|---|---|---|---|---|
| KH0362 UR122 · KH0049 AS038/HP036 | 12 | 140.2 | 0.001 (floor) | survives |
| KH0128 UR1114 · KH0137 UR1123 | 10 | 117.2 | 0.001 (floor) | survives |
| KH0140 AS125 · KH0483 UR247 | 12 | 87.0 | 0.001 (floor) | survives |
| KH0304 UR067 · KH0303 UR066 | 7 | 58.0 | 0.007 | survives |
| KH0305 UR068 · KH0301 UR064 | 8 | 52.6 | 0.014 | survives |

Planted 6-cord copies: recovery 0.20 over 200 plants (K006 0.23, K009 0.22), so short matches stay **not testable**.
No new pair.

## Verdict
- The run-preserving null is calibrated, and all five pairs survive with a precise threshold. The three strongest
  sit at the p floor of 1 000 corpora. The two Puruchuco pairs are real but weaker (p = 0.007 and 0.014).
- **Audit of K009.** K009 said four pairs score "above every one of the 200 null maxima". That was true for those
  200, but with 1 000, UR067/UR066 (58.0) is matched by 6 of them. Its verdict doesn't change; the wording was too
  strong and is corrected here.
- Line 3's remaining gap is power for short matches (0.20). Building a more powerful detector is a design problem,
  not a rerun. Next: exact per-pair probabilities (an analytic chance probability for each shared block, given
  both khipus' value multisets) with BH over pairs, scored against the same planted copies.

Raw output: `analysis/k010_results.json` (includes all 1 000 null maxima).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
