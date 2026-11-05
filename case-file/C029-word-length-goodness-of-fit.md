# C029 — The Binomial Bones, third dig (F-LEN step 3: goodness of fit with a refitting bootstrap)

*Expedition 29. Family F-LEN (word-length morphology). Follows C027 and C028, both NOT TESTABLE as comparisons.*

Status: pre-registered in commit `3da20026` before the run; run done (59 s). **Verdicts: Voynich INCONCLUSIVE (R 0.11); distinctively binomial NOT SUPPORTED** (as pre-registered; see results).

## Question
C028 showed that "more binomial than Dante or Cervantes" cannot be resolved at 1,000 types. A different, answerable
question: at that sample size, is a sample of Voynich word types **consistent with** a binomial length distribution at
all (Stolfi's strong form), and are natural-language samples of the same size consistent with one too?
The exact Binomial(9, ½) + 1 fit on the whole lexicon was already rejected in 2003
([voynich.net archive](http://www.voynich.net/Arch/2003/11/msg00138.html)); here N and p are refitted, the sample size is
fixed, and the test is calibrated on controls.

## Data
Same as C028: `data/ZL3b-n.txt` (ZL 3b), `<->` read as a word space, Voynich lengths in glyph units (`units()` of C003);
7 natural controls (Caesar, Descartes, Dante, Machiavelli, Cervantes, Genesis, Exodus) and the Timm–Schinner generator.

## Metric
One sample = K = 1,000 distinct word types drawn without replacement from the types of a random 10,000-token window.
Statistic: TV distance between the sample's length histogram and the best binomial (length − 1 ~ Bin(N, mean/N), N = 1..25).
Parametric bootstrap, B = 200: draw 1,000 lengths from the fitted binomial, **refit N and p**, recompute TV.
p = (1 + #{bootstrap TV ≥ observed}) / (B + 1). A sample is "rejected" if p < 0.05.
Rejection rate R = share of S = 100 samples rejected, per corpus.

## Gates (must pass, otherwise NOT TESTABLE)
- **Calibration (size):** in each natural control's own token stream, give every word type a length drawn from the binomial
  fitted to that control. R must have mean ≤ 0.075 over the 7 planted controls and no single R > 0.15.
- **Power:** in each control's stream, give every type a length from 1 + negative binomial with the control's mean and
  variance 1.5 × (mean − 1) (overdispersed, so outside the binomial family). R ≥ 0.80 in at least 6 of 7.

## Decision rule
- Voynich: **consistent with binomial** if R_V ≤ 0.10; **rejected** if R_V ≥ 0.50; otherwise inconclusive.
- **Distinctively binomial** (Stolfi's strong form, with controls) only if Voynich is consistent AND at least 6 of 7
  natural controls are rejected (R ≥ 0.50). One look, no family-wise correction needed beyond this conjunction;
  the generator's R is reported descriptively.

Seed 29029. Tool: `tools/c029_word_length_gof.py`. Budget ≤ 8 minutes (`timeout 600`).

## Results (seed 29029, 59 s; `analysis/C029_results.json`, `analysis/C029_run_log.txt`)

**Gates passed.** Calibration (planted binomial lengths in each control's own stream): R = 0.03, 0.02, 0.05, 0.04, 0.04,
0.08, 0.01 (mean 0.039, max 0.08; gate mean ≤ 0.075, max ≤ 0.15). Power (planted overdispersed lengths): R = 1.00 in
7 of 7 (gate ≥ 0.80 in 6 of 7).

| Corpus | Rejection rate R (100 samples of 1,000 types) | Median p |
|---|---|---|
| Voynich_ZL3b | 0.11 | 0.323 |
| Latin_Caesar | 1.00 | 0.005 |
| Latin_Descartes | 0.98 | 0.005 |
| Italian_Dante | 0.93 | 0.005 |
| Italian_Machiavelli | 1.00 | 0.005 |
| Spanish_Cervantes | 0.55 | 0.045 |
| Hebrew_Genesis | 1.00 | 0.005 |
| Hebrew_Exodus | 1.00 | 0.005 |
| Generator_TimmSchinner | 0.87 | 0.010 |

**Voynich: inconclusive.** R_V = 0.11, one sample above the pre-registered "consistent" bound (≤ 0.10); the 95 % Wilson
interval for 11/100 is about 0.06–0.19, so the data cannot tell 0.11 from the nominal 0.05 or from 0.15.
**All 7 natural controls rejected** (R ≥ 0.50): Caesar, Machiavelli, Genesis, Exodus 1.00; Descartes 0.98; Dante 0.93;
Cervantes 0.55. The Timm–Schinner generator: 0.87.
**Distinctively binomial: NOT SUPPORTED**, because the Voynich condition failed by one sample. The bound is not moved
after the fact.

**What can be said plainly.** At 1,000 types, the binomial is rejected for 55–100 % of samples of every natural text and of
the generator, and for 11 % of Voynich samples (planted binomials: 1–8 %). The Voynich is far closer to a binomial than any
control by this measure, but the pre-registered claim is not met, so this is a description, not a finding.

**Process note (disclosed).** The first run crashed only when writing JSON (numpy types). The fix touched output
serialisation only; the rerun with the same seed printed identical numbers.

## Audit
Consistent with C028's descriptive ordering (Voynich lowest TV, Cervantes nearest control). It does not contradict the
2003 rejection of the exact Bin(9, ½) + 1 fit on the whole lexicon: here N and p are refitted and samples are smaller.

## Next step (proposal, F-LEN step 4)
A confirmatory replication with fresh samples on Takahashi IT2a and on Currier A and B separately, with S = 400 so the
interval around R is narrow, and the same pre-registered bounds. To be scheduled after a new-family cycle.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
