# C063 — Expedição 63: réplica com sementes novas das observações pós-hoc de ch e q (F-NEIGH step 4)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Why:** [C060](C060-swap-table.md) saw, *by looking at the run* (post-hoc, uncorrected), that in the table of one-glyph changes between nearby words the Timm–Schinner generator spends 11–26% of the excess on inserting/deleting `ch`, the manuscript 1–5%; and the manuscript 4–16% on `q`, the generator 0–3%. **Caveat: these two hypotheses were suggested by C060's data, so the C060 numbers cannot count as evidence. Only a replication on data that did not decide them counts: fresh generator seeds and per-Currier-language manuscript subsets.**

## Pre-registration (pushed before any C063 number)
- **Statistic:** share of the C060 excess table (`tools/c060_swap_table.excess`: C058 neighbour definition, 100 shuffles inside 115-token chunks, clip(obs−null,0), normalised) carried by label `+|ch` and by `+|q`.
- **Manuscript subsets (4):** ZL 3b and IT2a (`data/ZL3b-n.txt`, `data/IT2a-n.txt`, as in `data/MANIFEST.md`) × Currier A pages / Currier B pages (`$L=` page tag). Paragraph text as in C047/C060. Token counts: ZL A 10,847; ZL B 22,559; IT A 10,592; IT B 22,515. B subsets capped at their first 15,000 tokens. Subsets under 5,000 tokens would be *not testable* (none are).
- **Generator:** default settings, 3,400 lines, **fresh seeds 6301–6360** (never used before; the first 40 texts long enough are kept). For each subset the generator's *first n_s tokens* give a size-matched share (so sampling noise matches).
- **H-ch (per subset):** manuscript `+|ch` share is below the minimum of the 40 generator shares. p = (1 + #gen ≤ V)/41. **H-q:** manuscript `+|q` share above the generator maximum; p = (1 + #gen ≥ V)/41. Minimum attainable p = 1/41 = 0.0244.
- **Multiplicity:** 8 tests (2 units × 4 subsets), Benjamini–Hochberg at 0.05. A test counts only if it is BH-rejected **and** satisfies the strict min/max rule.
- **Verdict per unit:** CONFIRMED if 4/4 subsets count; PARTIAL if 1–3; NOT CONFIRMED if 0; NOT TESTABLE if the gate fails or < 40 generator texts.
- **Calibration/gate:** (i) estimator gate — 20 natural texts at subset sizes with single-unit insertions planted (rank-3 letter, Q = 0.03): that unit's excess share must exceed 0.5 in ≥ 16/20; unplanted controls: that unit's share < 0.2 in ≥ 18/20 (a clean negative control: no phantom share). (ii) rank-test calibration: leave-one-out on the generator runs (each run treated as "manuscript" against the other 39) reports the empirical rate of p ≤ 0.05 per subset/unit (exchangeable, expected ≈ 0.025 or lower). Power for the manuscript side is limited by the 1/41 floor, stated above.
- **Reading rules fixed in advance:** CONFIRMED for ch means the generator's `ch` edits are an edit-profile difference from every manuscript subset (a defect to report to the generator's authors, with code). Not confirmed: the C060 observation was noise/section confounding. Neither says anything about meaning.
- **Tool:** `tools/c063_ch_q_replication.py` → `analysis/C063_results.json`; seed 6363; `timeout 600`; reuses `c060_swap_table.py`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
