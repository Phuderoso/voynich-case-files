# C069 — Expedição 69: o copista que não olha para cima (F-VERT step 2, confirmatory)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Question:** C068 found no vertical alignment excess in the manuscript at the planted 2% size (Dc Δ ZL +0.0100, IT2a +0.0096, NOT DETECTED after Holm). Post hoc, the manuscript sat below 19 of 20 default Timm–Schinner generator runs (`sourceChooser=page`, `same_position_probability=28`) and above 15 of 20 runs with `same_position_probability=0`. **This hypothesis was suggested by C068 data**; the manuscript numbers are already seen. Only the generator seeds below are fresh. C069 asks, with a rule written first: is the manuscript's Dc **below the default generator** (H1) and **above the no-position generator** (H2)?

**Change from C068 (disclosed, decided before running):** C068's generator texts had 1,200 lines (about 1,160 pairs) against the manuscript's ~2,600 lower lines, so the generator spread included extra sampling noise. C069 size-matches: **2,784 lines per run** (96 pages of 29 lines, 2,688 pairs). This makes the comparison fair and is expected to narrow the generator ranges. The only design run used generator seed 1 for timing (1.4 s per run, no Dc value printed).

## Pre-registration (pushed before running the C069 tool)
- **Manuscript statistic V:** Dc Δ exactly as in C068 (`tools/c068_vertical_alignment.py`, same data files `data/ZL3b-n.txt`, `data/IT2a-n.txt`, sha256 in `data/MANIFEST.md`, seed 6868). Recomputing must reproduce +0.0100 / +0.0096.
- **Generator Dc:** same C068 functions (`block_text`, `table`, K = 5 other-page uppers, interior words, ≥ 3 units, edit distance ≤ 1, |centre diff| ≤ 3 chars); one page group (generator has no Currier language/section); rng seed 68680 + generator seed.
- **References (fresh seeds, first 100 valid runs of each range):** default 9401–9520; spp0 (`same_position_probability=0`) 9601–9720.
- **H1 (below default):** p1 = (1 + #{default ref ≤ V}) / 101. **H2 (above spp0):** p2 = (1 + #{spp0 ref ≥ V}) / 101. Floor 1/101 ≈ 0.0099, so Holm's first threshold 0.0125 is reachable.
- **Gates (held-out fresh seeds as pseudo-manuscripts, first 20 valid of each):** default 9801–9830, spp0 9901–9930. H1 FPR: held-out default runs with p1 ≤ 0.05 in **≤ 2/20**; H1 power: held-out spp0 runs with p1 ≤ 0.05 in **≥ 16/20**. H2 FPR: held-out spp0 with p2 ≤ 0.05 ≤ 2/20; H2 power: held-out default with p2 ≤ 0.05 ≥ 16/20. A gate also fails if fewer valid runs than required are produced.
- **Multiple comparisons:** Holm over the gated tests among 4 (H1, H2 × ZL, IT2a), α = 0.05.
- **Decision (each of H1, H2):** **SUPPORTED** if both transcriptions reject; **PARTIAL** if one; **NOT DETECTED** if none with gates passed; **NOT TESTABLE** if a gate fails. If H1 and H2 are both SUPPORTED: **BETWEEN-SETTINGS** (the manuscript's vertical copying is weaker than the generator default and stronger than none). This would be a statement about one generator parameter, not about how the manuscript was written.
- **Descriptive (no p claims):** dose curve — `same_position_probability` ∈ {7, 14, 21}, first 10 valid runs of seeds 10001–10015, 10101–10115, 10201–10215; median Dc per value with 0 and 28 from the references; the value where the median curve crosses V by linear interpolation.
- **Tool:** `tools/c069_vert_dose.py`, `timeout 600`, 8 processes.
- **Backlog, not run here:** two-lines-up and same-index variants of the C068 statistic; F-CROSS step 3 (A→B reuse inside herbal).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
