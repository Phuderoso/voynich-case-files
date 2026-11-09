# C080 — Exact-size check of the F-PARA permutation test, with a known-answer control

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Why
[C079](C079-gate-audit.md) found 74/1,200 null rejections (6.2%) against an attainable size of 10/201 = 4.98%, but its positive control failed, so it was NOT TESTABLE. C079 pre-committed this cycle: a fresh sample, a control with a **known** wrong size, and a near-tie check.

## Pre-registration (written before running; tool `tools/c080_exact_size.py`, seed 8080, never used before)
- **Replicates (all true nulls).** (a) Line-shuffled real paragraphs from Currier B, word sets W0 and W2, in IT2a and ZL 3b: 300 replicates each, 1,200 in all. These are the configurations with the most C079 rejections; choosing them is disclosed as targeted. (b) A fully synthetic corpus: lines drawn i.i.d. with replacement from the ZL / B / W0 line pool into the observed paragraph shapes, 200 replicates. Each replicate gets C078's length-matched test with 200 permutations, so p = (1 + b)/201.
- **H1 (primary, pooled n = 1,400):** one-sided exact binomial test of #(p ≤ 10/201) against 10/201. **INFLATED** if p_binom ≤ 0.05, else **CALIBRATED**.
- **Known-answer control (required):** on the same replicates, the rule p ≤ 13/201 has an exact size of 6.47% if the test is valid. That is about the size C078 and C079 suggested. The same binomial test must flag it INFLATED against 10/201; if it does not, H1 is **NOT TESTABLE**. Analytic power of this control is 0.78 (critical count 84/1,400), so it fails by chance about 22% of the time. Disclosed in advance.
- **Near-ties:** for every replicate, count permuted statistics within 1e-9 of the observed one. (JSD sorts its keys, so summation order is fixed; near-ties are expected to be 0.)
- **Fixed interpretation:**
  - CALIBRATED with the control detected: C078/C079's excess was chance (C079 had selected the question after seeing C078). F-PARA continues with 40-replicate gates (FPR ≤ 4/40).
  - INFLATED with the control detected: a defect in the test machinery. All F-PARA rejections stay valid only where p sits at the floor (0.001), and the defect is hunted next cycle.
  - No earlier verdict is revised in this cycle.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
