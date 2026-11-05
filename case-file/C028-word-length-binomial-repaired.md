# C028 — The Binomial Bones, second dig (F-LEN step 2: C027 repaired)

*Expedition 28. Family F-LEN (word-length morphology), repair of C027, which was NOT TESTABLE.*

Status: pre-registered in commit `1a388733` before the run; run done (71 s). **Verdict: NOT TESTABLE** (power gate 5/7, needed 6/7).

## Question
Stolfi observed that the lengths of distinct Voynich words look like a binomial distribution. Is a Voynich text sample
*more* binomial than equally sized samples of natural-language texts, once sample size and corpus heterogeneity are controlled?

## What C027 got wrong, and the repair
1. TV distance depends on how many types are measured. **Repair:** every sample is exactly K = 1,000 distinct word types,
   drawn without replacement from the types of a random contiguous window of 10,000 tokens.
2. C027's calibration twins drew lengths from a whole book. **Repair:** each control is calibrated against itself
   (first half vs second half of the same book).
3. C027 used 100 draws, so p could never reach α/8. **Repair:** D = 2,000 draws per corpus.
4. **Planted power:** in each control's own token stream, every word type gets a new length drawn from the binomial fitted to
   that control (type identity and token stream kept). The planted text must come out "more binomial" than the original.

## Data
- Voynich: `data/ZL3b-n.txt` (ZL 3b, IVTFF), `<->` read as a word space (C026 lesson), lengths in glyph units (`units()` of C003).
- Natural controls (7, same files as C027): Caesar, Descartes (Latin); Dante, Machiavelli (Italian); Cervantes (Spanish);
  Genesis, Exodus (Hebrew, consonantal). Generator: Timm–Schinner text (as C027, one extra look).
- Known gap: no East Asian monosyllabic control (Stolfi reported binomial-like lengths there); a positive result cannot
  speak against such languages.

## Metric
For one sample: TV = total-variation distance between the length histogram of the K types and the best binomial
(length − 1 ~ Bin(N, mean/N), N = 1..25, minimum TV).
For two corpora X, Y: p(X closer than Y) = (1 + #{i : TV_X,i ≥ TV_Y,i}) / (1 + D), draws paired by index (independent windows).
This is the probability that a random X sample is *not* closer than a random Y sample, so it is an effect-size threshold,
not a sample-size artefact.

## Hypotheses and decision rule
- **H1:** Voynich is closer to a binomial than every natural control. Seven p values, Holm at α = 0.05.
  CONFIRMED if all seven Holm-adjusted p < 0.05; NOT CONFIRMED otherwise (with the list of controls that tie or win).
- Generator look (reported separately, uncorrected, descriptive): p(Voynich closer than Timm–Schinner).

## Gates (must pass, otherwise NOT TESTABLE)
- **Calibration:** for each natural control, half A vs half B and B vs A (14 ordered pairs, D draws each, windows drawn
  inside the half). False-positive rate = share with p < 0.05/7. Gate: ≤ 1 of 14 (≈ 7 %).
- **Power:** for each natural control, planted vs original (7 tests). Gate: ≥ 6 of 7 with p < 0.05/7.

Seed 28028. Tool: `tools/c028_word_length_binomial_repaired.py`. Budget ≤ 8 minutes (`timeout 600`).

## Results (run of `1a388733`, seed 28028, 71 s; `analysis/C028_results.json`, `analysis/C028_run_log.txt`)

**Gates.** Calibration passed: 0 of 14 half-vs-half comparisons below α/7 = 0.0071 (all p between 0.20 and 0.80).
Power failed: planted binomial lengths were detected in 5 of 7 controls (Caesar 0.0045, Descartes 0.0070,
Machiavelli 0.0015, Genesis 0.0005, Exodus 0.0005) but not in Dante (0.016) or Cervantes (0.088). Gate needed 6 of 7.
**Verdict: NOT TESTABLE.** With K = 1,000 types, sampling noise alone keeps a perfectly binomial sample from being
reliably closer than the most binomial-looking controls, so the metric cannot separate "more binomial than Dante or
Cervantes" from chance.

**Descriptive (not a finding, gates failed).** Mean TV per 1,000-type sample:

| Corpus | TV mean [2.5–97.5 %] |
|---|---|
| Voynich ZL 3b | 0.034 [0.017–0.055] |
| Cervantes | 0.053 [0.032–0.076] |
| Timm–Schinner generator | 0.054 [0.035–0.075] |
| Dante | 0.065 [0.041–0.091] |
| Caesar | 0.081 |
| Genesis | 0.082 |
| Machiavelli | 0.084 |
| Descartes | 0.085 |
| Exodus | 0.087 |

Holm-adjusted p (Voynich closer): Genesis 0.0035, Exodus 0.0035, Machiavelli 0.0075, Descartes 0.0080, Caesar 0.010,
Dante 0.059, Cervantes 0.103. Generator look: 0.084. These would be 5 of 7 if the instrument were valid; it is not, for
the two controls that matter most.

**Post-hoc (disclosed, not pre-registered; `tools/c028_posthoc_noise_floor.py`, `analysis/C028_posthoc_noise_floor.json`).**
A truly binomial sample of 1,000 types (Bin(10, 0.469) + 1, fitted to the Voynich) has TV 0.028 [0.013–0.046] from
sampling noise alone. The Voynich's 0.034 is close to that floor, which is the descriptive core of Stolfi's
observation, and also shows why there is little room left to beat Cervantes.

## Audit of C027
C027's descriptive ordering (Voynich lowest) survives the repair; its Cervantes tie came from unequal type counts and
disappears at equal K (0.034 vs 0.053), but the gap is still not testable at this K.

## Next step (F-LEN step 3, proposal)
Larger K is impossible for 10,000-token windows of most controls. Options: (a) a goodness-of-fit question instead of a
comparison (is each corpus's own type-length distribution consistent with a binomial, using a parametric bootstrap
that refits N and p per replicate), which matches the 2003 test but with controls; (b) add an East Asian
monosyllabic control. Option (a) is preferred.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
