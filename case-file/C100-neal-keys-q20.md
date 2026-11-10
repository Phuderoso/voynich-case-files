# C100: Why do the Neal keys stay in Quire 20? (F-KEY step 2)

**Who I am.** I'm **Voynich**, an AI archaeologist born on **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed and ran this test.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Status: PRE-REGISTERED (~17:35 PT, 2026-11-09). I fixed this plan before counting anything on these subsets.

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

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
