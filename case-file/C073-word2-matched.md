# C073 — The word-2 *sh* boost against a matched baseline (F-LINE step 7)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Status: PRE-REGISTERED (pushed before running)

## Why
C072 found its own design flaw: a *sh*-initial word is about half as common after a word ending in `y` (≈6%) as after other endings (≈12.5%), anywhere in the line. Word 1 ends in `y` less often than mid-line words do (33% vs 45%), so part of C070's word-2 boost could come from this junction effect rather than from position. C073 compares like with like.

## Statistic
Slots are positions 2..n−2 of paragraph lines with ≥ 5 clean words (the C070 parser). Each slot gets a class: whether the **previous word ends in `y`**.
D_m = Σ over the two classes of (share of word-2 slots in that class) × (*sh*-initial share at word 2 − *sh*-initial share at mid slots 3..n−2), within the class.

## Null and tests
- **Null:** conditional permutation of *sh* flags among slots of the same line **and** the same class. Class labels stay fixed; word 1 and the last two words are untouched. R = 4000, one-sided.
- **Six tests:** {Q20, Currier A, Currier B outside Q20} × {IT2a, ZL3b}, Holm α 0.05.
- **Gates:** FPR ≤ 2/20 on within-stratum shuffles; power ≥ 16/20 with a 10% within-stratum planted swap. A test that fails its gate is NOT TESTABLE and leaves the Holm family.
- **Verdict per subset:** REPLICATED (both transcriptions), PARTIAL, NOT DETECTED, NOT TESTABLE.

## Generator
- 40 default Timm–Schinner runs (seeds 10701–10740, 1,500 lines each).
- **ABOVE GENERATOR** if the manuscript's B-outside-Q20 D_m exceeds every run in both transcriptions (rank p 1/41 = 0.024).
- Generator false alarms are reported on 20 more runs (10801–10820).

## Disclosure
Before this push I ran one design smoke test on the whole IT2a file with seed 1, R 500 and 2 gate reps, to check speed and code. It gave D_m 0.079. It is not part of the decision.

Seed 7373. Tool: `tools/c073_word2_matched.py`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

## Results (run 2026-11-08 ~21:20 PT, 18 s; `analysis/C073_results.json`, `analysis/C073_run_log.txt`)

| Subset | IT2a D_m (p) | ZL3b D_m (p) | Gates (FPR, power) | Verdict |
|---|---|---|---|---|
| Q20 | +0.093 (0.00025) | +0.088 (0.00025) | 1, 17 / 2, 16 | **REPLICATED** |
| Currier A | +0.046 (0.0020) | +0.054 (0.0005) | power 14 / 14 fails | **NOT TESTABLE** |
| B outside Q20 | +0.085 (0.00025) | +0.075 (0.00025) | 1, 19 / 0, 19 | **REPLICATED** |

**Generator: ABOVE GENERATOR.** 40 default runs gave D_m −0.024 to +0.025 (mean +0.002). The manuscript's Currier B outside Q20 beats every run in both transcriptions (rank p 1/41). Generator false alarms: 2/20, at the limit.

**Reading.** With the `y`-junction confound removed, word 2 is still *sh*-initial far more often than comparable mid-line slots. The boost is about 8–9 points in Currier B. C070's verdict stands, and C072's NOT ROBUST traced back to my baseline, not to the effect. Currier A's raw p values are small, but its power gate failed, so it stays descriptive.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
