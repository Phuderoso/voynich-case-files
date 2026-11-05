# C032 — The Edge of the Map, third survey (F-LINE step 3: two-part calibration and a targeted start test)

*Expedition 32. Family F-LINE. Follows C030 (line edges, start not testable) and C031 (repair failed by construction).*

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

Status: **pre-registered** in this commit, before any run of `tools/c032_line_edges_two_part.py` (seed 3232).

## Lesson carried in
C030 and C031 showed that re-cutting a text that has real line structure leaks some edge structure into the
calibration texts (a surplus with offset re-cutting, a deficit with interior re-cutting). So no re-cut text can be the
size check. The size check must use texts with no line structure at all, and the leak must be bounded separately.

## Look 1 — line edges, two-part calibration (ZL 3b, generator; IT2a replication)
Statistics, null, data rules and plant as C030 (imported): D_end, D_start (paragraph-first lines excluded), within-line
shuffle null with 1,000 draws, α = 0.025 per statistic.
- **(a) Size and power:** texts with every word shuffled across the whole text, recut with the original line lengths
  (no line structure by construction). FPR ≤ 4/40; power (15 % of lines get a move of the 3rd most common edge unit)
  ≥ 32/40. Otherwise **NOT TESTABLE**.
- **(b) Leakage bound:** L = the largest D among 40 offset re-cut texts (C030 method) and 40 interior re-cut texts (C031
  method).
- **DETECTED** only if (a) passes, p < 0.025, **and D > 3 × L**. If (a) passes but either condition fails: NOT DETECTED.

## Look 2 — do generator line starts carry the manuscript's start units?
C030/C031 (manuscript only) showed the manuscript's line starts are enriched in first units `s`, `y`, `d` (the
strongest non-gallows start lifts). Fixed now from manuscript data, before looking at this statistic in the generator:
- Statistic: number of line-initial words in the **generator** whose first unit is `s`, `y` or `d`.
- Null: within-line shuffle, 1,000 draws; one-sided p for enrichment; α = 0.05 (single test).
- Gates on generator shuffled texts (as Look 1a): FPR ≤ 4/40; power ≥ 32/40 with 15 % of lines getting an `s`/`y`/`d`
  word moved to the start.
- **ENRICHED** if p < 0.05 with gates passed; otherwise NOT ENRICHED (or NOT TESTABLE if a gate fails).
- The same count for the manuscript is reported **descriptively only**: the units were chosen from manuscript data, so
  testing it there would be circular.

Not a claim about meaning or the cause of line effects; one generator sample (authors' configuration) only.

## Results
*(pending)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
