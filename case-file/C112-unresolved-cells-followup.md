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
