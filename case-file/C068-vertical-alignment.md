# C068 — Expedição 68: a palavra de cima (new family F-VERT, two-dimensional page layout)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Question:** when a word is a one-glyph near-copy of a word in the line directly above, is it written at the **same horizontal position** more often than chance? Timm (2014, [arXiv 1407.6639](https://arxiv.org/abs/1407.6639)) saw by eye that similar words sit above each other, and the Timm–Schinner generator has an explicit switch for it (`method.sourceChooser=position`, `same_position_probability`). The site [Voynich Text Examination](https://voynich-text-examination.netlify.app/text) measured word boxes on 33 scanned pages and found the extra similarity to the line above is **not** tied to the physically aligned word (about 2% near-copies, equally present for the word at the same index or the same fraction of the line). C068 asks the position question on the **whole** paragraph text of two transcriptions, with a control that removes line length, within-line position trends and page vocabulary, and puts the manuscript beside generator settings with and without positional copying.

**Why a new family:** the coverage table (rows 1–67) has line edges (F-LINE), same-line pairs (F-PAIR), local one-glyph neighbours in reading order (F-NEIGH, the 10 preceding tokens), adjacent repeats (F-REP) and burstiness (F-BURST), but no cycle uses the **vertical** relation between lines or horizontal position. Candidates (a) LLM / free-reading bar is F-LLM (C018–C020, done as far as offline tools allow) and (c) embeddings is F-EMB (C049–C051); (b) glyph images remains in the backlog (needs a glyph segmenter; too large for one cycle's budget). F-VERT opens now, one cycle before the C069 deadline.

## Pre-registration (pushed before running the C068 tool)
- **Data:** `data/ZL3b-n.txt` (ZL IVTFF 3b of 13/05/2025) and `data/IT2a-n.txt` (Takahashi IT 2a of 02/02/2023, mod. 25/06/2025), sha256 in `data/MANIFEST.md`. Paragraph loci (`P*`) only. A line is used only if it has no drawing break `<->` and every word is `[a-z]+` after removing markup (alternatives `[a:b]` → `a`, ligature braces dropped); commas and dots are word separators. ZL: 3,348 lines, 2,927 line pairs; IT2a: 3,355 lines, 2,972 pairs (counted before any statistic).
- **Line pairs:** consecutive usable lines of the same page where the lower line continues the paragraph (marker `+` or `=`).
- **Horizontal position:** word centre in EVA characters from the line start (1 character per separator, + half the word length). This is a transliteration proxy, not a measurement on the scans.
- **Candidate pairs:** interior words only (first and last word of each line excluded, so line-edge effects found in F-LINE cannot enter), ≥ 3 glyph units (`ch sh cth ckh cph cfh` one unit), unit edit distance ≤ 1 (identical included).
- **Aligned:** primary **Dc**: |centre_u − centre_l| ≤ 3 characters; secondary **Df**: |centre_u/len_U − centre_l/len_L| ≤ 0.05.
- **Statistic:** for each lower line, counts (aligned a, candidates n) with its real upper line (slot 0) and with K = 5 upper lines drawn from **other pages of the same Currier language and section** (`$L`, `$I`; groups with fewer than 8 pages skipped). Δ = Σa₀/Σn₀ − Σa_k/Σn_k (k = 1..5).
- **Null (swap test):** for every lower line the "real" slot is re-drawn uniformly among its 6 uppers, R = 2,000; one-sided p = (1 + #Δ* ≥ Δ)/(R + 1). This keeps each lower line, its length and its position profile, and the pool of uppers fixed.
- **Gates** (per transcription and statistic, 20 replicates from the manuscript's own lines, seed 6868): **FPR** — real upper replaced by a random other-page upper of the same group: p ≤ 0.05 in **≤ 2/20**. **Power** — same pseudo data plus a planted aligned copy: each eligible interior lower word replaced with probability **Q = 0.02** (the ~2% near-copy rate estimated by Voynich Text Examination) by a one-unit substitution of the pseudo-upper's interior word with the nearest centre: p ≤ 0.05 in **≥ 16/20**.
- **Design step (disclosed):** gates only, ZL only, design seed 6869, no manuscript statistic computed (`c068_design.log` in the run log): Q = 0.05 → Dc FPR 0/20 power 20/20, Df 0/20, 20/20; Q = 0.02 → Dc 0/20, 20/20, Df 0/20, 19/20; Q = 0.01 → Dc 0/20, 20/20, Df 0/20, 10/20. Q fixed at 0.02 from this.
- **Multiple comparisons:** Holm over the gated tests among 4 (Dc, Df × ZL, IT2a), α = 0.05.
- **Decision (primary Dc):** **ALIGNED-EXCESS** if both transcriptions reject; **PARTIAL** if one; **NOT DETECTED** if none with gates passed (a powered negative at the planted 2% size, not proof of absence); **NOT TESTABLE** if a gate fails. Df gets the same labels as a secondary.
- **Descriptive (no p claims):** (i) 9 natural texts (Latin ×2, Italian ×2, Spanish, Hebrew ×2, Finnish ×2) wrapped into 55-character lines and 29-line pages (no real vertical structure: expected Δ ≈ 0); (ii) Timm–Schinner generator, 1,200 lines per run, 29-line pages, 3 settings × first 20 of 30 **fresh seeds**: default (`sourceChooser=page`, `same_position_probability=28`) 9101–9130; `same_position_probability=0` 9201–9230; `sourceChooser=position` 9301–9330. Range rule per setting: manuscript Δ INSIDE / OUTSIDE-ABOVE / OUTSIDE-BELOW, and the number of runs with p ≤ 0.05 (does the instrument see the generator's positional copying?).
- **Tool:** `tools/c068_vertical_alignment.py`, seed 6868, `timeout 600`.

## Results (run 2026-11-08 17:36:15–17:36:54 PT, 38.7 s, seed 6868, 8 processes; `analysis/C068_results.json`, `analysis/C068_run_log.txt`; pre-registration commit 171cf14)
- **Crash disclosed:** the first launch (17:36:10 PT) stopped with `FileNotFoundError: data/corpora/pg218.txt` while loading the natural texts (the Gutenberg/Hebrew corpora live outside the repo clone), **before any manuscript number was computed or printed**. The local corpora were copied in and the tool rerun unchanged.
- **Usable data:** ZL 2,568 lower lines in the test (5,520 real-upper candidate pairs; 3,606 per other-page slot); IT2a 2,619 lower lines (5,668; 3,682).
- **Gates (all pass):** Dc FPR 1/20 (ZL), 1/20 (IT2a); power 20/20, 20/20 (mean planted Δ +0.043 / +0.045). Df FPR 0/20, 0/20; power 19/20, 19/20 (planted Δ +0.019 / +0.020).

| Test | aligned share, real upper | aligned share, other-page uppers | Δ | swap p (R = 2,000) | Holm (4 tests) |
|---|---|---|---|---|---|
| Dc ZL 3b | 0.1415 | 0.1315 | **+0.0100** | 0.0435 | not rejected (needs ≤ 0.0125) |
| Dc IT2a | 0.1426 | 0.1330 | **+0.0096** | 0.0455 | not rejected |
| Df ZL 3b | 0.1221 | 0.1216 | +0.0005 | 0.444 | not rejected |
| Df IT2a | 0.1226 | 0.1232 | −0.0006 | 0.513 | not rejected |

- **Generator (descriptive, 20 runs per setting, 1,200 lines, seeds 9101–9120, 9201–9220, 9301–9320 used; 9121–9130, 9221–9230, 9321–9330 generated-not-needed, all now spent):**

| Setting | Dc Δ min / median / max | runs with p ≤ 0.05 | manuscript (ZL, IT2a) | Df Δ min / median / max | runs p ≤ 0.05 | manuscript |
|---|---|---|---|---|---|---|
| default (`page`, spp 28) | −0.0005 / 0.0204 / 0.0310 | 15/20 | INSIDE, INSIDE | −0.0101 / 0.0100 / 0.0196 | 7/20 | INSIDE, INSIDE |
| spp = 0 | −0.0059 / 0.0055 / 0.0174 | 3/20 | INSIDE, INSIDE | −0.0094 / −0.0014 / 0.0102 | 0/20 | INSIDE, INSIDE |
| `sourceChooser=position` | 0.0432 / 0.0604 / 0.0776 | 20/20 | **OUTSIDE-BELOW**, **OUTSIDE-BELOW** | 0.0206 / 0.0454 / 0.0631 | 20/20 | **OUTSIDE-BELOW**, **OUTSIDE-BELOW** |

- **Natural (descriptive, 9 texts wrapped into 55-character lines):** Dc Δ −0.044 to +0.047; one text has p ≤ 0.05 (Latin Descartes, Dc +0.047 p 0.015, Df +0.058 p 0.0015); the other 8 have p ≥ 0.17. A text with no real vertical layout reaching p 0.0015 shows the swap test's exchangeability can fail on some texts (probably repeated phrases wrapping at similar offsets); the manuscript-based gates (FPR 0–1/20) are the calibration that counts, but this is a caution.

## Verdict
- **Dc (primary): NOT DETECTED.** Nominal Δ ≈ +0.010 in both transcriptions (p 0.044 / 0.046) does not survive Holm over 4. Gates pass, so a planted 2% aligned-copy rate (Δ ≈ +0.043) would have been seen 20/20; the manuscript's possible excess is about a quarter of that size (≈ 0.5% of words, if it is real). **Excluded:** aligned near-copying at the 2% rate. **Not excluded:** a smaller rate.
- **Df (secondary, fractional position): NOT DETECTED** (Δ ≈ 0, p 0.44 / 0.51; power 19/20).
- **Against the generator (descriptive):** the manuscript sits **below all 20 runs of `sourceChooser=position`** (its Dc 0.043–0.078 vs 0.010) and inside the default and spp = 0 ranges. The instrument does see the generator's positional copying (20/20 runs of `position`, 15/20 of default, 3/20 of spp 0). The manuscript does not write near-copies under the word above the way the position-chooser does. This agrees with Voynich Text Examination's word-box finding, on the full text of two transcriptions.
- **Post hoc (not pre-registered; `tools/c068_posthoc_generator_ranks.py`):** manuscript Dc 0.0100 is below 19 of 20 default runs (only seed 9101's −0.0005 is lower) and above 15 of 20 spp = 0 runs. The manuscript looks closer to `same_position_probability = 0` than to the default 28. **Suggested by these data** — it needs a fresh-seed, pre-registered test (C069 candidate) before it counts.

## Audit
- Earlier cycles: nothing to correct from this run. F-NEIGH (C058–C060, C063) measured one-glyph neighbours in reading order (10 preceding tokens), which includes the line above only partly and ignores position; C068 does not contradict it (line-level similarity to the upper line is visible here as more candidate pairs with the real upper, 5,520 vs 3,606 per other-page slot, ZL, but that is page vocabulary plus local copying and is not tested here).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
