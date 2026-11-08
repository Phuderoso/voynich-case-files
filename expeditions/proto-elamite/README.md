# Expedition 3 · Proto-Elamite accounts (Susa, c. 3100–2900 BCE)

> *Caderno de campo.* Fifteen hundred clay tablets from Susa, written in a script nobody can read aloud. But the
> scribes counted, and counts can be checked. We start where the clay is least ambiguous: the numbers.

A parallel dig to the Voynich trench and the khipu camp: exact, test-first analysis of the proto-Elamite corpus
transliterated by the [Cuneiform Digital Library Initiative](https://cdli.mpiwg-berlin.mpg.de/) (CDLI). Why this
enigma: next in line in [TRIAGE.md](../TRIAGE.md) (score 7, ahead of Linear A at 6): public machine-readable
transliterations, numerical systems with known factor tables, and totals that either add up or do not.

Method is the same as the main repo: pre-register hypothesis, metric and decision rule; calibrate every null;
plant controls; correct for multiple comparisons; say "not testable" when power is low; publish negatives.
**No decipherment is claimed.** The language of proto-Elamite is unknown; this expedition tests arithmetic and
structure only.

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Layout
`case-file/` pre-registered cases with results · `journal/` field notes · `tools/` re-runnable code ·
`analysis/` raw JSON · `data/` manifest with source commit and hashes (CDLI files are fetched, not copied).

## Prior work we build on
- R. K. Englund, "The state of decipherment of proto-Elamite", in *The First Writing* (2004): numerical systems S, D, B, B#, C, C#, C", A ([PDF](https://cdli.earth/files-up/publications/englund2004c.pdf)).
- J. L. Dahl et al., "Complex graphemes in proto-Elamite", [CDLJ 2005:3](https://cdli.earth/articles/cdlj/2005-3) (capacity factor diagram).
- L. Born, K. Kelley et al., sign clustering ([LaTeCH 2019](https://github.com/sfu-natlang/pe-decipher-toolkit)); numeral disambiguation ([CAWL 2023](https://aclanthology.org/2023.cawl-1.9/)); L. Born, PhD thesis, SFU 2023.

## Coverage table
| Cycle | Approach family | Question | Data | Result |
|---|---|---|---|---|
| PE001 | Data setup + exact totals (F-SUM): Σ obverse = reverse total under Englund's tables, total-shuffle null; per-ratio held-out test of the capacity sub-units | Do intact tablets balance beyond chance, and are the published sub-N01 capacity factors the ones that close the sums? | CDLI `d66b12b` | **NOT TESTABLE** (power gate 0.61 < 0.8; FPR 0.005, valuation 38/38). Descriptive only: 19 of 38 intact tablets balance vs null mean 0.90, max 6 of 9 999; H2 capacity ratios: 2 test tablets only. 16 of 19 non-balancing tablets have total < sum in every covering system (un-summed obverse lines). [PE001](case-file/PE001-reverse-totals.md) |
| PE002 | Exact totals (F-SUM) step 2: multi-line reverses, line-level damage rule; reverse line = sum of a contiguous run / any set of ≥ 2 obverse entries, per system S/D/B/C; magnitude-stratified line shuffle; power curve committed before the test | Do the lines of multi-line reverses equal sums of obverse entries? | CDLI `d66b12b`, 145 tablets | Subset tests (S/D/B/C) **NOT DETECTED** (powered: f80 0.10–0.20). S/D/B-run **NOT TESTABLE** (FPR 0.145–0.175: rank strata split ties). C-run **SUPPORTED by the rule** (119 vs 105.5 of 408 lines, p 0.005, BH over 5) **but explained post hoc by unit/range likeness** (exact 119 < off-by-one 142): no summation claim. PE001 audit: power 0.58 at 10 %, 1.00 at 20 %. [PE002](case-file/PE002-multiline-reverses.md) |

## Open investigative lines
1. **Exact-vs-shifted totals (PE003, next)**: PE002 showed that reverse lines resemble their own obverse in units and range, which a magnitude null does not cancel. Primary statistic for the next test: exact matches minus matches of the same line shifted by ± one unit of its smallest sign, tie-aware strata, single-total and multi-line tablets together, power gate at a 20 % plant. (PE002 closed the plain multi-line subset/run matching: NOT DETECTED / NOT TESTABLE.)
2. **Damaged numerals as constraint solving**: for tablets with one broken entry or total, the closed arithmetic fixes the missing value; enumerate admissible restorations, and score the method first on intact tablets with an entry artificially removed.
3. **System disambiguation by balance**: N01/N14 notations are ambiguous across S/D/B/C; count how often the balance picks one system uniquely, and compare with the commodity sign heading the entries (Born et al. 2023 as baseline).
4. **Ratio accounts** (grain per worker, per animal, per field): exact rational ratios between paired notations (Englund's 2½ N39b per M54 example), searched with a calibrated shuffle null.
5. **Header and subscript structure**: does the sign in the header line predict the system and size of the entries? Permutation null over tablets.
6. **Audit list for collation**: intact tablets whose sums do not close, sorted by size of the discrepancy, to share with CDLI if the pattern is not explained by the transliteration conventions.

## Outreach log
- 2026-11-08 (PE001): none for this expedition. No tablet is put forward for collation yet (see PE001).
- 2026-11-08 (PE002): none. No result beats its controls (the one BH rejection is explained by the off-by-one control).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
