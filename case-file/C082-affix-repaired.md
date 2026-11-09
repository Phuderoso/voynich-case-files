# C082 — Are the manuscript's word ends looser than the generator's? (F-AFFIX step 2, confirmatory)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed, ran and wrote up this cycle.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Why
C081 measured K, the share of a word's last-symbol uncertainty explained by its first symbol at fixed length, beyond chance. The manuscript came out at K ≈ 0.103 (IT2a) and 0.107 (ZL 3b), below all 10 Timm–Schinner generator runs (0.124–0.200). Formally nothing was called, because C081's bootstrap CI was biased upward: resampling with replacement inflates plug-in mutual information while E_null was held fixed. C081 pre-committed this cycle: repair the CI, then test "below the generator" on 20 **new** seeds. This is a hypothesis suggested by C081's data. It is tested here on fresh generator runs only; the manuscript texts are of course the same.

## Pre-registration (written and committed before the full run; tool `tools/c082_affix_repaired.py`, seed 8282)
- **Texts and statistic:** exactly C081: same 9 natural texts, ZL 3b (`data/ZL3b-n.txt`, "Version 3b of 13/05/2025", md5 1b9c653b…) and IT2a (`data/IT2a-n.txt`, "Version 2a of 02/02/2023 modified 25/06/2025", md5 0e7b3a6a…), C003 glyph units, first 15,000 tokens, tokens of ≥ 3 symbols, strata {3, 4, 5, 6, ≥ 7}, K = [I(first; last | stratum) − E_null] / H(last | stratum), E_null = mean over 50 within-stratum shuffles. The mutual-information routine is vectorised; it reproduces C081's Caesar value to 1e-15.
- **Repaired CI:** half-sample subsampling **without replacement**. Each of B = 400 draws takes 10 of the 20 contiguous blocks, and **E_null is recomputed inside every draw** (20 shuffles). For m = n/2 the spread of d = K_half − K_full estimates the sampling spread of K_full (finite-population factor 1/m − 1/n = 1/n). The 95% CI is the basic interval [K − q97.5(d), K − q2.5(d)].
- **Generator:** default Timm–Schinner runs, 2,500 lines each, on fresh seeds:
  - **reference** 11211–11230 (20 runs; at least 18 must be usable);
  - **held-out negatives** 11231–11240 (10 unmodified runs, each with a CI);
  - **plant hosts** 11241–11245 (5 runs with the endings of 25% of tokens shuffled within strata, so expected K ≈ 0.56 × the host's K).
- **Rule per text:**
  - **BELOW GENERATOR** iff K < min(reference) **and** CI upper < min(reference). The first condition alone has rank p = 1/21 = 0.048 under exchangeability with the generator.
  - **ABOVE GENERATOR** is the mirror rule.
  - **INSIDE GENERATOR RANGE** if min ≤ K ≤ max.
  - Otherwise **NOT CALLED**.
- **H1 (single confirmatory test):** both transcriptions are called BELOW GENERATOR. This is an intersection–union test at α = 0.05, so no further correction is needed. If both are INSIDE, H1 is rejected. Any other combination is NOT CALLED.
- **Gates (any failure makes H1 NOT TESTABLE):**
  - **G1, CI repaired:** every CI row contains its own point K. Centring, |median d| ≤ ¼ half-width, is reported descriptively only. Disclosure: the one smoke test, on Caesar only, gave median d = −0.0047, a residual small-sample bias. The basic interval moves the CI upward, which is conservative for a BELOW call. I removed a centring gate after seeing that smoke test and before committing.
  - **G2, false positives:** at most 2 of the 10 held-out runs may be called BELOW or ABOVE. Expected about 0.95 by chance.
  - **G3, power (planted known answer):** at least 4 of the 5 plants must be called BELOW GENERATOR.
- **H2 (secondary, range rule, no p-value):** C081's natural rule with the repaired CI. The leave-one-out gate allows at most 1 of the 9 texts called OUTSIDE, and decoupled Caesar must be called OUTSIDE NATURAL. Otherwise H2 is NOT TESTABLE.
- **Fixed interpretation:** "BELOW GENERATOR" means that default self-citation ties word beginnings to endings more tightly than the manuscript does. That is a quantitative misfit of the generator's *default settings*, not a refutation of self-citation in general. It says nothing about meaning. "INSIDE" means this feature cannot separate them.
- **Next seeds after this cycle:** 11246+.

## Results
*(to be filled after the run)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
