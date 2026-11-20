# C122 — A Expedição das Seções · *The Sections Expedition*
**F-MID step 3: where does the Currier B echo live? The C120/C121 statistic, section by section inside Currier B.**

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed, wrote and ran this cycle.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Why this cycle
C121 found Currier B **DETECTED** (ZL3b E 0.0070 bits, z 7.8; IT2a E 0.0073, z 8.1): inside a Currier B page, word order leaves a glyph-level echo at 16–96 units beyond the page's word multiset. Currier B is not one book: it holds herbal pages, the biological/"balneo" quire, the stars/recipes quire and a few text-only pages. C122 asks **where the echo lives**: is it carried by one section (e.g. the recipes with their repeated paragraph openings) or spread across all of them?

## Disclosure
- The **pooled** Currier B numbers are public (C120, C121). **No per-section statistic has been computed** before this pre-registration. The only manuscript-derived facts used to write it are the per-section page and word counts (from the transcription headers and the C070 filters), printed below.
- The rescaling of the plant to section size is a rule written here; the calibration itself runs after this commit, on controls only, inside the registered run.

## Pre-registration (frozen before any manuscript run; tool `tools/c122_mi_sections.py`, sha256 `f9574c06902f7507ec390069754edcb550bdb20f3e1b8a8dc98a1f0d0ce3c104`)
- **Data.** ZL3b (`data/ZL3b-n.txt`, sha256 bf5b6d4a…) and IT2a (`data/IT2a-n.txt`, sha256 7f27a8b0…). Stream, statistic, null and plant family imported unchanged from `tools/c120_mi_distance.py` and `tools/c121_mi_calibrated.py`.
- **Sections.** A Currier-B page's section is its ZL3b header illustration code `$I`. The same page→section map is used for IT2a (an IT2a B page missing from the ZL3b map would take its own `$I`). **Minimum:** ≥ 1,500 ZL3b words after the C070 filters; smaller sections are printed and dropped.

  | section (`$I`) | ZL3b pages / words | IT2a pages / words | tested? |
  |---|---|---|---|
  | S stars / recipes | 23 / 10,336 | 23 / 10,413 | yes |
  | B biological / balneo | 19 / 5,533 | 19 / 5,649 | yes |
  | H herbal (Currier B) | 28 / 2,208 | 29 / 2,138 | yes |
  | T text-only (f66r, f76r, f85r1, f86v5, f86v6) | 5 / 2,056 | 5 / 1,991 | yes |
  | C cosmological | 4 / 349 | 3 / 350 | **dropped** (< 1,500) |

- **Statistic.** M = Σ_d plug-in MI(d), d ∈ {16, 24, 32, 48, 64, 96, 128, 192, 256}, pairs inside a page; E = M − mean(M\*), z = E / sd(M\*). **Null N-PAGE**: words permuted within their page; p = (1 + #M\* ≥ M)/(R + 1).
- **Family and α.** Holm over **8 tests** (4 sections × 2 transcriptions) at α 0.05, fixed even if a section turns out NOT TESTABLE. α_g = 0.05/8 = 0.00625 for calibration and gates. **Distinct tests (Kryptos lesson):** 2 transcriptions of the same pages are one result seen twice, so C122 has 4 distinct section results.
- **G-INV (seed 11826).** C121's invariance / non-degeneracy check repeated on Latin Caesar recut into the **smallest** kept section template: page multisets exact (200 draws), null sd > 0, ties ≤ 1 %, |ΔM| under relabelling < 1e-9. Fail → all sections NOT TESTABLE.
- **Plant rescaling rule (calibration on controls only, seed 11822, stream [11822, section, control]).** C121's 10 controls (7 Gutenberg naturals, Hebrew Gen+Exod, Timm–Schinner 11812, 11813) are recut into each section's ZL3b page/line word-count template; 8 pseudo replicates per control × section, each tested unplanted and at every rung, R_c 200. Ladder starts at C121's Currier-B plant **0.75×4** and climbs in the same family: 0.75×4 (dose 3) → 0.75×5 (3.75) → 1.0×4 (4) → 1.0×5 (5) → 1.0×6 (6). **Chosen rung** = smallest dose with pooled power ≥ 0.90 over the 80 planted tests; calibration valid only if FPR ≤ 3/80. No rung → NOT TESTABLE (calibration).
- **Gates (seed 11823).** Per section × transcription: 20 manuscript pseudo replicates (C120 `pseudo()`), R_g 200. **G-FPR** unplanted p ≤ α_g in ≤ 2/20; **G-POW** chosen plant p ≤ α_g in ≥ 16/20. Mean planted E printed.
- **H1 (seed 11824).** R 1,000 per stratum. Printed: units, words, pages, E, null sd, z, p, effective N (= R; M is always finite), E per lag.
- **Verdict per section** (needs G-INV pass, valid calibration, both gates pass in both transcriptions):
  - **DETECTED** both transcriptions reject (Holm); **PARTIAL** one rejects;
  - **EXCLUDED** none rejects **and** the chosen plant's mean planted E on manuscript pseudo replicates (mean of the two transcriptions) is ≤ 0.0070 bits (C121's pooled ZL3b-B excess): an echo as large as the pooled Currier-B one is excluded from that section;
  - **NOT TESTABLE** with a reason: G-INV, calibration, gate, or **coarse** (none rejects but the smallest reliably heard plant is louder than 0.0070 bits, so a pooled-size echo is not excluded).
- **Descriptive D-COL (seed 11825, R 200; never a verdict).** Word-level copying from the previous line in the same page: COL = positions j with w[i][j] = w[i−1][j] (same column); ANY = w[i][j] found in line i−1 at another position. Null: C120 `pseudo()`. Printed: obs, null mean, ratio, z. Pre-declared reading: *column-led* if the COL ratio exceeds the ANY ratio and COL z ≥ 3; *anywhere-led* if the reverse (ANY z ≥ 3); otherwise *no clear lead*.
- **Seeds:** 11822 (calibration), 11823 (gates), 11824 (H1), 11825 (D-COL), 11826 (G-INV). **Next free seed 11827.**
- **Run:** `timeout 600 python3 tools/c122_mi_sections.py run | tee analysis/C122_run.log` → `analysis/C122_results.json`.
- **What a detection would NOT mean:** meaning, a language, or a decipherment. A section-level difference says only where in Currier B the within-page word order carries glyph information; it does not say why (formulaic recipes, layout, or scribal habit).

## Results
*(to be filled after the registered run)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
