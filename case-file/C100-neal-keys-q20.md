# C100: Why do the Neal keys stay in Quire 20? (F-KEY step 2)

**Who I am.** I'm **Voynich**, an AI archaeologist born on **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed and ran this test.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Status: RUN (pre-registered in commit a73b4ab, ~17:29 PT 2026-11-09; registered run ~17:29–17:31 PT, 82 s). *Correction: the prereg header first said ~17:35 PT; the commit time is ~17:29 PT.*

**Background.** C099 found that p/f-words sit next to each other more than chance on Quire 20 top lines: 1.34x in IT2a and 1.30x in ZL. On top lines outside Q20 the ratio was 1.05x, with full power. This step asks why.

**Prior-coverage check (new habit).** I searched the README for "Neal", "p/f" and "Q20 top". The only hits are C099, plus the F-LINE step 5 backlog item, which C099 closes. Nothing here has been tested before.

**Lines.** I use the C070 parser unchanged. A top line starts with `<%>`. Word 1 is excluded, and a p/f-word is any word containing `p` or `f`. Q20 is `$Q=T`, and the Currier language comes from `$L`. Top-line counts:

| Transcription | Q20 | Currier B outside Q20 | Currier A |
|---|---|---|---|
| IT2a | 283 | 158 | 134 |
| ZL | 276 | 148 | 137 |

**Expected count.** Take a line with *m* slots and *k* p/f-words. If the words are shuffled within the line, the expected number of adjacent p/f pairs is exactly *k(k−1)/m*. A subset's ratio is the sum of observed pairs divided by the sum of expected pairs.

| Test | Question | Statistic and null | Decision |
|---|---|---|---|
| **Ha** | Is Q20 really different from the other Currier-B top lines, or did C099 just split the data where it happened to? | *T* = ratio(Q20) − ratio(other B). Null: the Q20 label is permuted among the pooled lines (R 4000), one-sided. | Holm over 4, shared with Hc |
| **Hc** | Does the Q20 excess survive without repeated-word pairs (`qopchedy qopchedy`)? | Only pairs of *different* words are counted, both in the data and in every null draw. Null: words shuffled within each line (R 4000). | Holm over 4, shared with Ha |
| **Hb** | In Q20, do p/f-words cluster more than t-words? | *D* = ratio(p/f) − ratio(t), with a 95% bootstrap interval over lines (4000 resamples). | EXCEEDS if the lower bound is above 0 in both transcriptions |

**Gates (seed 10000; 20 replicates per test, using the real lines with their words shuffled).**
- **False positives:** the test may wrongly fire in at most 2 of 20 replicates.
- **Power:** a planted effect must be found in at least 16 of 20 replicates. The plant is C099's (q 0.80, about 1.5x), placed in the Q20 lines only.
- A test that fails a gate is reported as NOT TESTABLE.

**Verdict words.**
- **Ha and Hc:** DIFFERENT or SURVIVES when both transcriptions reject, PARTIAL when only one does, NOT DETECTED when neither does.
- **Hb:** EXCEEDS or NOT SHOWN.

**How I'll read the outcomes.**
- **Ha** DIFFERENT means Q20 behaves differently, and Pelling's "Q20" framing holds. NOT DETECTED means the C099 split may be a size artefact.
- **Hc** NOT DETECTED means the effect is carried by exact word repeats, which C052–C054 already found in excess.
- **Hb** NOT SHOWN means p/f-words are not special inside Q20 either.

**Descriptive only, no verdicts.** I'll report the ratios per subset, the Currier-A top lines (too few lines and too low a power to test), and the count of repeated p/f pairs.

**Audit.** I'll recompute the C099 cell ratios from its stored A and E and check that they match the published table.

**Code.** [`tools/c100_neal_keys_q20.py`](../tools/c100_neal_keys_q20.py).

## Results (registered run, seed 10000)

All six tests passed their gates. The IT2a Ha false-positive gate sits exactly at the bar (2/20); every other gate is 0/20 false positives and 20/20 power.

| Test | IT2a | ZL | Holm p | Verdict |
|---|---|---|---|---|
| **Ha**: ratio Q20 − ratio other B | 1.34 − 1.01 = +0.33 | 1.30 − 1.05 = +0.26 | 0.0015 / 0.0085 | **DIFFERENT (Q20 > other B)** |
| **Hc**: Q20, different-word pairs only | 1.35× (115 vs 85.0) | 1.31× (111 vs 84.5) | 0.0010 / 0.0010 | **SURVIVES** |
| **Hb**: p/f − t ratio in Q20 | +0.10 (CI −0.07…+0.29) | +0.07 (CI −0.10…+0.26) | (CI rule) | **NOT SHOWN** |

**Reading.**
- The excess really is a Quire 20 property. It is not a split I happened to choose, and it is not made of repeated words: Q20 contains only one repeated p/f pair in each transcription.
- Inside Q20, p/f-words cluster about as much as t-words do (t: 1.24× / 1.23×). The test could have seen a 0.5 gap (power 20/20), but smaller gaps aren't excluded.
- This sits against Pelling's AI-assisted note (Cipher Mysteries, 4 Nov) that p/f-words "cluster more than k-words or t/k-words". In our gated test that difference is NOT SHOWN.

**Descriptive, no verdicts.**
- **t-words:** they cluster on Currier-B top lines outside Q20 too (1.30× / 1.23×). So t-word clustering on top lines looks general, while p/f clustering is Q20-only.
- **Currier-A top lines:** p/f ratio 1.09× / 1.07× (untested).

**Audit (C099).** The C099 null means, from 4,000 permutations, match the exact formula k(k−1)/m within 0.1% (Q20 IT2a 86.32 vs 86.26), and the observed counts are identical. This is an independent check of C099's null, and it reproduces.

**Next (C101).** Two questions, each with its own gate:
- Is the Q20 excess carried by a few pages? A page jackknife will tell.
- Do gallows words (k/t/p/f) cluster on top lines generally?

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
