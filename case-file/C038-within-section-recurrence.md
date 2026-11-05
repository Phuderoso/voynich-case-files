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


## Results (run after the pre-registration push, commit f014b51e; runtime 95 s)

**Gates failed on power.** FPR 2/40 (pass: ≤4), power **22/40** (need ≥36), natural texts 6/7 significant at α≈0.0167 (Dante p=0.029 missed). Per the pre-registration, **every H1 verdict is *not testable***. Numbers below are still reported for H2/H3 and for the next design step; they are not confirmatory claims.

**N = 6152** (limited by balneological B = 6152 tokens; H = 11,349; S = 11,214). Same first-N cut for whole ZL and the 7 natural controls. IT2a carries `$I` headers; its H/S/B streams are reported descriptively only.

| Stream | S (d=1–10) | L (d=50–500) | p_L | z | vs natural L | vs whole-ZL L | H1 |
|---|---:|---:|---:|---:|---|---|---|
| Whole ZL (folio order, N) | 0.636 | 0.054 | 0.001 | 5.8 | inside | — | (replication, not H1) |
| H herbal | 0.657 | 0.057 | 0.001 | 6.4 | inside | within 2 SE | **not testable (gates)** |
| S stars | 0.904 | 0.282 | 0.001 | 27.6 | inside | above whole | **not testable (gates)** |
| B balneo | 0.602 | 0.089 | 0.001 | 12.2 | inside | within 2 SE | **not testable (gates)** |
| Natural range (7 texts) | 0.043 … 2.261 | 0.016 … 0.442 | — | — | — | — | 6/7 positive |
| IT2a H / S / B (descriptive) | 0.716 / 0.872 / 0.621 | 0.075 / 0.275 / 0.089 | — | — | inside / inside / inside | — | not tested |

**H2 (descriptive).** At this N, every within-section L sits **inside** the natural range (0.016–0.442). Stars (S) carries the most long-range excess (L=0.282); herbal and balneo are much lower and sit within 2 combined jackknife SEs of whole-ZL L at the same N (whole L=0.054). Whole-ZL L at N=6152 is far below C037's whole-text L at N=16,000 (0.527): the first 6,152 folio-order tokens are mostly early herbal/T pages, so this replication is length-matched, not span-matched, to C037.

**H3 (descriptive).** Cross-section stream H[:2050]+S[:2050]+B[:2050] (+2 H filler tokens to reach N; seams at 2050 and 4100) has L=0.672 vs mean within-section L=0.143. **Disclose:** this inflation is largely a P0 artefact. Mixing the three vocabularies flattens the type-frequency distribution (cross P0=0.0040 vs H 0.0061 / S 0.0036 / B 0.0085) while raw P(same) stays comparable, so C(d)=P(same)/P0−1 rises. It is **not** evidence that cross-section joins create more recurrence than staying inside one section.

**Interpretation (no overclaim).** The power gate failed, so this cycle does **not** confirm within-section long-range recurrence. Descriptively, at N=6152 the within-section L values sit inside the natural range, and C037's above-natural whole-text L at N=16k is not reproduced by a length-matched whole-ZL slice that barely leaves the opening sections. Surviving raw p-values under the token-permutation null (all 0.001) show dependence above a pure shuffle, but without a passing power gate that is not a registered claim — and dependence is still not meaning. `$I` is an illustration tag, not a content claim; page order inside a section can still mix sub-topics; self-citation can produce the same pattern.

**Code and numbers.** `tools/c038_within_section_recurrence.py`, `analysis/C038_results.json`. Seed 3838.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
