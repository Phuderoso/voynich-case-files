# C010 — Expedição 10: The Shape of the Tail. Does any Voynich-like generator configuration also end its words like the manuscript?

**Status:** pre-registered 2026-11-05 01:30 PT, before any run. Results appended below.
**Approach family:** generator configuration screen (as C004/C005) with a new match statistic. Not a new family; C009
was the most recent new family.

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Question
C008 found (descriptively, one seed) that C005's matched configuration ends its words very differently from the
manuscript (ending entropy 1.79 vs 2.53 bits). **Among all generator configurations already found to be Voynich-like
on four statistics (C004 sweep + C005 search: mean word length, TTR, h2 and rigidity R each within ±15 % of the
whole-manuscript reference), does any also match the manuscript's word-final glyph distribution?**

## Metric
- E = distribution of the last glyph unit of each word (C003 tokenisation), on the first 6,000 words.
- D = Jensen–Shannon divergence (bits) between E of a text and E of the whole manuscript (ZL 3b, commas split).
- **Bar:** 99th percentile of D over 40 samples of 6,000 consecutive Voynich words (random starts, seed 10). A text
  "ends like the manuscript" if D ≤ bar.

## Controls
- **Planted negative:** the same 40 Voynich samples with half of the `-n` endings changed to `-m` (C008's most visible
  difference). At least 95 % must fail the bar, or the metric is too blunt ("not testable").
- **Known negative:** C005's selected configuration (seed 6001) is expected to fail. This is reported, not a gate.

## Screen and confirmation
- Rerun every unique Voynich-like configuration from `analysis/C004_sweep.jsonl` and `analysis/C005_search.jsonl`
  (366 configurations) once, with the first seed it was logged with, recomputing the four statistics plus D.
- **Confirmation:** the 3 passing configurations with the lowest D are run on held-out seeds 8001–8010. A configuration
  **matches** if its 10-seed means of mwl, TTR, h2 and R are within ±15 % **and** its 10-seed mean D ≤ bar.
- **Verdict:** "some configuration matches all five" if ≥ 1 confirms. "No screened configuration matches" if none pass
  the screen or none confirm. This covers only configurations already logged, not the whole generator space.
  3 confirmation looks.

## Budget
≤ ~8 min (366 runs at about 1 s each over 10 workers, plus 30 confirmation runs); output `analysis/C010_*.json`.

## Results (run 2026-11-05, about 2 min; `tools/c010_word_endings.py`, `analysis/C010_results.json`, cache `analysis/C010_screen.jsonl`)
Transcription: ZL 3b as in C003–C009 (commas split). Generator: the authors' Timm–Schinner jar (C004).

- **Bar:** 40 Voynich 6,000-word samples give D median 0.0059, maximum 0.0284; bar (99th percentile) = **0.0281**.
  The bar is wide because sections differ in their endings, which makes the test lenient to the generator.
- **Planted negative passed:** 97.5 % of the `-n`→`-m` samples fail the bar (median D 0.035). The metric is usable.
- **Screen:** all 366 Voynich-like configurations reran and still met the four statistics. **None passed D ≤ 0.0281.**
  Lowest D 0.038, median 0.083. Their ending entropy ranges 1.68–2.94 bits (manuscript 2.53), so entropy alone can
  match; the shape of the distribution does not.
- **Known negative:** C005's selected configuration (seed 6001): D = 0.286, ending entropy 1.76 bits.
- **Confirmation:** nothing to confirm (0 configurations passed the screen).
- The five closest configurations all use `use_word_final_substitutions=true`, four with the default seed line.

**Verdict: no screened configuration matches all five statistics.** Among the 366 generator settings already logged as
Voynich-like, none ends its words like the manuscript; the closest is about 1.4 times the bar. This is a statement about
logged configurations, not about the whole generator space or about a modified generator. It also explains part of C008:
the cross-word rule had the wrong word endings to work with.

Next: a search that optimises D directly under the four constraints (pre-registered, held-out seeds), before declaring
the generator unable to match.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
