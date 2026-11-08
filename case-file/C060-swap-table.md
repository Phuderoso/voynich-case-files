# C060 — Expedição 60: quais glifos trocam de lugar? (F-NEIGH step 3)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Why:** [C058](C058-edit-neighbours.md) found an excess of nearby words one glyph apart, at the generator's level; [C059](C059-neighbour-edit-position.md) found the change sits in about the same word positions as in the Timm–Schinner generator (PARTIAL), but the generator range is wide. A sharper question: **which** glyph units are swapped? The generator applies its own substitution rules; a scribe or a morphology would swap others. If the manuscript's swap table looks like a draw from the generator, the self-citation account survives a more specific test; if not, the generator gets the right amount and place of change from the wrong glyphs.

## Pre-registration (pushed before any C060 number)
- **Labels:** for every focal token (≥ 3 units) with its nearest one-glyph neighbour among the 10 preceding tokens (C058 definition; EVA units from `tools/c003_position_rigidity.units`), the change is labelled: substitution → unordered unit pair {u, v}; insertion/deletion → ('+', unit), first mismatching position.
- **Excess table:** clip(observed − mean null, 0) per label, normalised; null = C058's 100 shuffles inside 115-token chunks.
- **Distance:** Jensen–Shannon divergence (bits) over the union of labels.
- **H1:** VG = JSD between each Voynich half (ZL 3b and IT2a, halves 1–2: 4) and each generator half (default settings, seeds 551–557, halves of 15,000 tokens; texts under 30,000 tokens dropped; ≥ 6 halves needed). GG = JSD between generator halves from **different** seeds (the generator's own spread). **GENERATOR-LIKE** if median VG ≤ the 95th percentile of GG; **DIFFERENT** if median VG > max GG; **INTERMEDIATE** otherwise.
- **Gate (label recovery):** 20 natural halves (C058 rotation) with copy-with-mutation planted at Q = 0.03 using one fixed swap between the text's two most frequent letters; recovered if that pair has the largest excess share and share > 0.3; bar ≥ 16/20. Failing → NOT TESTABLE.
- **Descriptive (no verdict):** VV distances (ZL half 1 vs 2, IT2a half 1 vs 2, ZL vs IT2a on the same half) as a transcription/section reference; top 8 labels for Voynich and generator.
- **Reading rules fixed in advance:** GENERATOR-LIKE means the generator reproduces which glyphs change, not only how often and where — another statistic it matches. DIFFERENT means the generator gets amount and place of change from different glyph swaps, a concrete defect worth reporting to its authors with the table. Neither implies meaning. Note that VG mixes manuscript-vs-generator difference with sampling noise of both; GG carries the generator's noise twice too, so the comparison is fair in noise but not a formal test.
- **Tool:** `tools/c060_swap_table.py` → `analysis/C060_results.json`; seed 6060; `timeout 600`.

## Results
*(to be filled after the run)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
