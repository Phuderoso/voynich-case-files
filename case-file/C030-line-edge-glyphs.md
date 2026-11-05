# C030 — The Edge of the Map (F-LINE step 1: glyphs at line edges vs the rest of their line)

*Expedition 30. **New approach family F-LINE** (the line as a unit), required by the one-in-three rule.*

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

Status: **pre-registered** in this commit, before any run of the tool on real or planted data (only a data-loading
smoke test was run: line counts ZL 3955, generator 1189, IT2a 3967).

## Question
Currier (1976) and later readers reported that Voynich lines behave as units: some glyphs prefer the start or end of
a line. Is that true under a calibrated null that keeps each line's own words, and does the Timm–Schinner
self-citation generator (whose rigidity and edge coupling we studied in C003–C011) reproduce it? The generator text
we use was produced line by line, so it has real line breaks to test.

## Data
- `data/ZL3b-n.txt` (ZL 3b): paragraph loci only (locus type starting with `P`); `<->` read as a word space;
  `[a:b]` → `a`; a line is dropped if any word contains a character outside `a–z` (unreadable) or it has < 3 words.
- `data/IT2a-n.txt` (Takahashi IT2a), same rules: **replication look**.
- `data/corpora/ts_generated_text.txt` (Timm–Schinner generator, authors' sample, 1,200 lines), lines with ≥ 3 words.
- Glyph units: `units()` from C003 (`cth ckh cph cfh ch sh` as single units).

## Metric
- **D_end** = Jensen–Shannon divergence (bits) between the last glyph unit of line-final words and the last unit of all
  other words of the same lines.
- **D_start** = same with the first unit of line-initial words; **paragraph-first lines excluded** (the known
  gallows-at-paragraph-start effect is not the line effect asked about).
- **Null:** word order shuffled within each line (the edge word becomes a uniformly random word of its own line),
  1,000 draws; p = (1 + #null ≥ observed) / 1,001. Effect size z = (D − null mean) / null sd.

## Gates (per text and statistic; 40 replicates each, 200 null draws per replicate)
- **Calibration:** re-lineate the text (all words concatenated, recut with the original sequence of line lengths
  from a random offset, so line breaks fall at arbitrary word boundaries). FPR at α must be ≤ 4/40.
- **Power:** on the re-lineated text, in 15 % of lines move one word whose edge unit is the text's 3rd most common
  edge unit to the line end (or start). Power ≥ 32/40.
- A failed gate makes that statistic **NOT TESTABLE** for that text.

## Decision rule
α = 0.025 per statistic (Bonferroni over the 2 statistics) within each text. **DETECTED** if p < α and both gates
pass. Main texts: ZL 3b and the generator; IT2a is a replication of ZL 3b (same rule).
- If Voynich is DETECTED and the generator is NOT DETECTED with gates passing, I will write "the generator sample does
  not reproduce the line-edge effect" (for this configuration only).
- Not a claim about meaning or about why lines differ; descriptive tables (edge units most over- and
  under-represented, observed vs expected counts) are reported but not tested.

Seed 3030. Tool: `tools/c030_line_edge_glyphs.py`. Output: `analysis/C030_results.json`.

## Results
*(pending)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
