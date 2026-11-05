# C029 — The Binomial Bones, third dig (F-LEN step 3: goodness of fit with a refitting bootstrap)

*Expedition 29. Family F-LEN (word-length morphology). Follows C027 and C028, both NOT TESTABLE as comparisons.*

Status: PRE-REGISTERED before any run (this file is committed before the tool is executed).

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

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
