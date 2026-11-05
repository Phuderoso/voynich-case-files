# C038 — Expedição 38: o eco dentro de uma só ilustração (within-section long-range recurrence)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** F-MI step 2 (follows C037 step 1).

## Question
Does long-range recurrence L survive *inside* a single illustration section (so cross-section topic shifts cannot explain it), and how does within-section L compare to C037's whole-text L and to length-matched natural slices?

## Pre-registration (written and pushed before any run)
- **Data:**
  - ZL 3b (`data/ZL3b-n.txt`) paragraph/page words tagged by IVTFF page variable `$I`. Words are collected per page, then pages of one `$I` are concatenated in folio order.
  - Primary sections: the three largest with enough length for d ≤ 500 — **H** (herbal), **S** (stars / Recipes-stars), **B** (balneological). Expected lengths ~11k / ~11k / ~6k tokens.
  - Whole ZL in folio order is also reported at the same N (replication of C037 L at the section length).
  - **N** = min(8000, min length among H, S, B). If B is shorter than 8000, N = that shared minimum (≥ 5500 expected). Each section stream and the whole-ZL stream are cut to their first N tokens.
  - Natural controls: the same 7 as C037 (Caesar, Descartes, Dante, Machiavelli, Cervantes, Genesis, Exodus), each cut to first N.
  - Optional descriptive: IT2a pages with the same `$I` mapping if IT2a carries matching page headers; if IT2a lacks `$I`, skip IT2a sections and say so. **H1 is ZL-only** for H, S, B. Generators are out of scope this cycle (not in H1).
- **Metric:** Same as C037: C(d) = P(same) / P0 − 1; S = mean d = 1–10; L = mean d = 50–500.
- **H1 (tested):** For each of H, S, B: L above a within-section token-permutation null (1,000 permutations of that section's N tokens). One-sided p; Bonferroni α = 0.05/3 ≈ 0.0167. Verdict per section: WITHIN-SECTION LONG-RANGE RECURRENCE or NO DETECTED WITHIN-SECTION LONG-RANGE RECURRENCE.
- **H2 (descriptive):** Place each section's L vs (a) whole-ZL L at the same N, (b) the natural range at N. Also report whether each section L is within 2 jackknife SEs of whole-ZL L (10 contiguous chunks; seams disclosed).
- **H3 (descriptive contrast):** Build a *cross-section* stream by concatenating the three section prefixes of length ⌊N/3⌋ each (H then S then B; forces two cross-section joins). Report its L and compare to the mean of the three within-section Ls. No p-values beyond noting the design. Disclose the seams.
- **Gates (must pass or all H1 = not testable):**
  1. FPR: 40 fully permuted copies of the herbal (H) section tokens (length N), each tested with 200 permutations at α = 0.0167; ≤ 4/40 significant.
  2. Power: 40 planted topic copies of H (same plant as C037: in every 500-token block replace 2% with a block-specific word); ≥ 36/40 detected.
  - Natural texts' significance is sanity, not a gate.
- **Caveats fixed in advance:**
  - Surviving L inside one section is still *dependence*, not *meaning* (self-citation can do it).
  - Page order inside a section may still mix sub-topics.
  - `$I` labels are Zandbergen/IVTFF illustration categories, not a claim about content.
  - Mis-binding (Layfield & Fagin Davis 2026) can scramble folio order inside a section; that would mostly weaken within-section L.
- **Code:** `tools/c038_within_section_recurrence.py`, seed **3838**, run with `timeout 600`. Runtime budget ~8 min. Writes `analysis/C038_results.json`.

