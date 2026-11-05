# C028 — The Binomial Bones, second dig (F-LEN step 2: C027 repaired)

*Expedition 28. Family F-LEN (word-length morphology), repair of C027, which was NOT TESTABLE.*

Status: PRE-REGISTERED before any run (this file is committed before the tool is executed).

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

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
