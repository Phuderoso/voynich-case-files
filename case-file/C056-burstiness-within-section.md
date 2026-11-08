# C056 — Expedição 56: o bando sobrevive dentro de cada seção? (F-BURST step 2)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Why:** [C055](C055-burstiness.md) found that the manuscript's mid-frequency words clump (D 0.29–0.34), inside the natural range and below the default generator, but its halves cross sections (herbal, astro, balneo, pharma, stars), and section changes alone can make words clump. Its gates also passed exactly at the bars.

## Pre-registration (pushed before any C056 number)
- **Statistic:** as C055 (115-token chunks, eligible types 15–150 per 15,000-token half, B = mean log var/mean).
- **New null:** tokens shuffled only *inside blocks*, where a block is a contiguous run of the same IVTFF `$I` section in reading order (ZL half 1: 15 blocks, the longest 9,843 tokens of herbal; half 2: 10 blocks, the longest 6,541 of stars; IT2a similar). The block lengths were read before pre-registration (design input; no statistic was computed on them). **D_blk = B − mean(B under block shuffle)**, 200 shuffles, p by rank. D under a global shuffle (50) is recorded for comparison.
- **Controls get the same blocks:** each control half is cut with the block lengths of the matching ZL half (one-half texts use ZL half 1), so their long-range drift is removed in the same way. Controls: as C055 (9 natural, 3 devowelled, one half for texts under 30k tokens); generator default settings, seeds 551–557 (texts under 30,000 tokens dropped; ≥ 6 halves needed).
- **Gates (stronger than C055):** 40 replicates under the block null. FPR — shuffled natural halves, p < 0.05 at most 4/40. Power — C055's planted clumping, p < 0.05 at least 28/40. Failing → all NOT TESTABLE.
- **H1:** EXCESS if all four Voynich halves have block-null p < 0.0125; NO EXCESS if none; SPLIT otherwise.
- **H2 / H3:** D_blk of the four Voynich halves against the natural / generator D_blk ranges: ABOVE, BELOW, INSIDE, STRADDLE.
- **Reading rules fixed in advance:** EXCESS means clumping remains inside sections, so section changes alone do not explain it (it still does not mean topic or meaning: page-level layout, scribe changes and copying remain candidates). NO EXCESS means C055's clumping is accounted for by section structure.
- **Tool:** `tools/c056_burstiness_within_section.py` → `analysis/C056_results.json`; `timeout 600`; seed 5656.

## Results
(pending)

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
