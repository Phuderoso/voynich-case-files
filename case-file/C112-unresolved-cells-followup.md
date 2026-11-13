# C112 — Expedição 112: back to the fourteen locked doors (the C110 unresolved cells, twenty seeds each)
*Do any of the 14 copying-generator settings that C110 could not call reach the manuscript's neighbour alternation beyond slots?*

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed, ran and wrote this case.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Pre-registration (written and committed before any registered statistic of this cycle was computed)

**Why.** [C110](C110-grid-slot-null.md) ran the 65 cells of C083's generator grid under C109's slot null: 0 REACHES, 51 BELOW,
**14 UNRESOLVED** (means 0.122–0.172 under the bar, but six halves scatter too much to call). C110 proposed one confirmatory
follow-up on those 14 cells only. **Kryptos** approved it (12 Nov 2026, ~18:00 PT) on two conditions, both built in here:
(1) fix the per-cell n from C110's pooled sd 0.029 and print the MDE (target ≈ 0.03); (2) a regime-stratified secondary, with the
flip fraction printed and a cell rated REACHES only if its 'vowel' ('E') regime also reaches.

**Cells.** C110's UNRESOLVED list, fixed: **1, 2, 7, 9, 10, 14, 16, 21, 25, 27, 31, 40, 48, 49** (C083 `grid()` indices).

**Statistic.** C109 E_slot exactly as in C110 (`tools/c110_grid_slot_null.py::run`, imported unchanged: 4,600 lines, first 30,000
EVA tokens as two 15,000-token halves, slot null N2 with Sukhotin re-fitted on every shuffle, NSH = 100).

**Unit and n.** The **seed** (mean of its two halves), **n = 20 seeds per cell**, generator seeds **11753–11772**. One change from
C110, made here before any data: the two halves of one run are consecutive pieces of one text, so the seed, not the half, is the
independent unit. **MDE** (computed by the tool from sd 0.029, a conservative stand-in for the seed-mean sd, n 20, one-sided
α/14 = 0.00357, t_crit 3.014): **0.020** at 50 % power and **0.025** at 80 % power, both under the agreed 0.03.

**Bar.** B = **0.1996** (C110, from the published C109 Voynich values: minimum minus 2 SE across four halves).

**Primary per-cell test.** One-sided one-sample t of the 20 seed means vs B in each direction; **Holm over the 14 cells** at
α = 0.05 per direction. Labels REACHES / BELOW / UNRESOLVED.

**Secondary (regime-stratified, Kryptos's condition 2).** A half is 'E' iff EVA `e` is in its fitted Sukhotin vowel class (as in all
four Voynich halves). For each cell with ≥ 6 E halves: one-sided t of its E halves vs B per direction, Holm over the testable cells.
**Final REACHES** = primary REACHES **and** E-regime REACHES; a pooled-only REACHES is reported as such and does not count.
Flip fraction (cells with both regimes) and the E share are printed.

**H1 (the 14 cells).** Every cell BELOW → **NOT REACHED** (with C110's 51 BELOW, the whole C083 grid is below the manuscript); any
feasible final REACHES → **REACHED**; final REACHES only in infeasible cells → **REACHED ONLY WITH SURFACE LOSS**; otherwise
**UNRESOLVED** (k of 14). Feasibility = C083's surface rule, recomputed as the mean over the 20 runs.

**Gates (either fails → H1 NOT TESTABLE).** **G-NEG:** the default generator on the same 20 seeds must test BELOW at α/14.
**G-SHIFT** (certifies the rule at the agreed effect with the scatter actually observed): each cell's 20 seed means, recentred to
mean B + 0.03, must test above B at α/14, and recentred to B − 0.03 must test below at α/14, in **≥ 13 of 14** cells each.

**Descriptive only.** Max cell mean, max single half, halves at or above the bar, pooled seed sd and the realized MDE.

**Reading rule.** NOT REACHED → "no copying setting in C083's grid makes neighbour alternation beyond slots at the manuscript's
level". REACHED → "a copying setting does it; C109's gap was a settings gap". Nothing about meaning or vowels either way, and the
grid is C083's, not all generators.

**Seeds.** Generator 11753–11772, null rng 11773 (derived per task as `[11773, cell + 1, seed]`; default generator cell −1),
11774 reserved for a side task (blind plants for Kryptos's case 193), next free **11775**.

**Code.** `tools/c112_unresolved_cells_followup.py`, committed with this pre-registration. **Disclosure:** a smoke run used cell 1
on unregistered seeds 1–4 (half values 0.076–0.183, plus the default generator on the same seeds); none of those numbers is used.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

## Results (registered run 00:31:49–00:35:25 PT, 13 Nov 2026, 216 s; prereg `93a1697`; log `analysis/C112_run.log`, numbers `analysis/C112_results.json`)

**Gates pass.** G-NEG: default generator, 20 seeds, mean 0.122, p_down 4e-8 (BELOW at α/14 = 0.00357). G-SHIFT: the ±0.03
recentred plants are called correctly in **14/14** cells in both directions. All 14 cells usable (20 seeds × 2 halves each).

| Cell | Mean (20 seeds) | sd (seed means) | Label | E-regime label (E halves of 40) | Feasible |
|---|---|---|---|---|---|
| 1 | 0.128 | 0.030 | BELOW | BELOW (32) | no |
| 2 | 0.148 | 0.017 | BELOW | BELOW (19) | no |
| 7 | 0.151 | 0.027 | BELOW | BELOW (32) | no |
| 9 | 0.126 | 0.042 | BELOW | BELOW (30) | no |
| 10 | 0.148 | 0.027 | BELOW | BELOW (37) | no |
| 14 | 0.149 | 0.036 | BELOW | BELOW (30) | no |
| 16 | 0.166 | 0.023 | BELOW | BELOW (39) | no |
| 21 | 0.153 | 0.036 | BELOW | BELOW (27) | no |
| 25 | 0.170 | 0.019 | BELOW | BELOW (40) | no |
| 27 | 0.107 | 0.044 | BELOW | BELOW (29) | no |
| 31 | 0.106 | 0.044 | BELOW | BELOW (32) | no |
| 40 | 0.150 | 0.016 | BELOW | BELOW (28) | no |
| 48 | 0.162 | 0.015 | BELOW | BELOW (18) | yes |
| 49 | 0.153 | 0.018 | BELOW | BELOW (27) | yes |

All p_down ≤ 6.4e-6 (largest, cell 21), every p_up = 1.0. **H1: NOT REACHED** — all 14 cells BELOW, in the pooled test and in the
'E' regime alone. With C110's 51 BELOW, **all 65 cells of C083's grid are credibly below the manuscript's E_slot bar**.

**Descriptive.** Highest cell mean 0.170 (cell 25), bar 0.1996, Voynich 0.208–0.225. Halves at or above the bar: **11 of 560**
(Voynich 4 of 4); highest single half 0.225 (cell 10). Regime flips in **13/14** cells; 75 % of halves land in the 'E' regime.
Pooled sd of the seed means **0.030** (the same as C110's per-half sd 0.029, so the two halves of a run are strongly correlated:
treating the seed as the unit was needed); realized MDE 0.020 / 0.026 (50 / 80 % power).

**Reading (registered rule).** No copying setting in C083's grid makes neighbour alternation beyond slots at the manuscript's
level. The gap C109 found between the manuscript and the default generator is not a default-settings artefact within that grid.
This says nothing about meaning or vowels, and it covers C083's 65 settings, not every possible generator.

**Caveats.** (1) C083's grid only. (2) A few single halves (11/560) reach the bar, so a generator text *can* show Voynich-level
E_slot by chance; what it does not do is show it reliably. (3) Cell 49 was 'N' in 5 of 6 C110 halves and is 'E' in 27 of 40 here:
the regime is bistable, as C110 said, and six halves were not enough to see the mixture.

**Audit note on C110.** C110's H1 UNRESOLVED is now settled by this follow-up: the 14 unresolved cells are BELOW.

**Next (proposed).** F-HMM step 2 (registered test of the 'sticky' HMM observation from C111 against a slot-keeping null), or the
independent replication of Nick Pelling's Word-2 sh-initial boost with the C107 stratified null. Seeds used 11753–11774; next free **11775**.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
