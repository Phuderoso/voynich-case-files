# C076 — Expedição 76: os andares do parágrafo, com régua calibrada (F-PARA step 2)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Question:** C071 asked whether the **interior** words of a paragraph line (positions 3..n−2) know the line's floor (top, second, last vs middle lines), but its power gate failed by design: the plant used the commonest words, which carry the average glyph mix. C076 repeats the test with a **calibrated, direction-neutral plant**, and adds one sharper question: **H2 — does the top-line body still differ once every interior word containing a `p`/`f` gallows (`p f cph cfh`) is removed?** That separates "Tiltman lines are just p/f-rich" (Currier, Tiltman, Neal; Pelling, Cipher Mysteries 4 Nov 2026) from a broader top-line make-up.

## Pre-registration (pushed before running the C076 tool)
- **Data, paragraphs, interior words, classes, statistic, null:** exactly C071 (`data/IT2a-n.txt`, `data/ZL3b-n.txt`, sha256 in `data/MANIFEST.md`; paragraphs ≥ 4 fully usable lines: IT2a A 86 / B 237, ZL A 89 / B 206; JSD in bits between pooled C003 glyph-unit counts of class X and middle lines M; null = within-paragraph line-order permutation). Code reuses `tools/c071_paragraph_depth.py`.
- **Label-free inventory looked at before this push (no class split):** interior tokens IT2a A 1,797 / B 8,221, ZL A 1,960 / B 6,870; share of interior tokens containing a p/f unit 4.5–5.3%.
- **Plant (direction-neutral):** in each pseudo replicate a target unit U is drawn uniformly from the units whose pooled interior share in that subset lies in [2%, 10%] (H2: p/f units excluded). In class-X lines each interior word is replaced with probability q by a word drawn uniformly from the subset's interior tokens that contain U (H2: from tokens without p/f units). The plant therefore moves mass toward a random mid-frequency unit, not toward the direction C071 saw.
- **Calibration of q (design phase, no manuscript statistic computed):** IT2a only, X = T, Currier A and B, 10 pseudo replicates (lines pre-permuted within paragraph) per q ∈ {0.04, 0.06, 0.08, 0.12, 0.16, 0.24}, gate R = 200, seed 76761. q* = the smallest q with planted p ≤ 0.05 in ≥ 9/10 for **both** A and B; if none, q* = 0.24 and the power gate decides. q* is used for all 16 gates. The median planted JSD at q* is reported as the instrument's detectable effect size.
- **Tests (Holm over 16, α 0.05; R = 1,000; seed 7676):** H1 = {T, S, Lst} × {A, B} × {IT2a, ZL} (12, C071 repeated); H2 = T vs M on interior words without p/f units × {A, B} × {IT2a, ZL} (4).
- **Gates per test (20 pseudo replicates, fresh seeds from 7676):** FPR p ≤ 0.05 in ≤ 2/20; power at q* p ≤ 0.05 in ≥ 16/20. A failing test is NOT TESTABLE and leaves the Holm family.
- **Verdict per (hypothesis, class, language):** DIFFERENT (both transcriptions reject after Holm), PARTIAL (one), NOT DETECTED (none, gates pass), NOT TESTABLE.
- **Interpretation fixed in advance:** H1-T DIFFERENT with H2 DIFFERENT → the top-line body differs beyond p/f gallows; H1-T DIFFERENT with H2 NOT DETECTED → the top-line body effect is carried by p/f words (consistent with the known gallows story, not a new property). S NOT DETECTED is only a non-detection at the stated effect size, never an exclusion of all effects.
- **Descriptive (no p claims):** the five units with the largest share difference X − M; manuscript JSD vs the median planted JSD.
- **Not done here:** generator (no paragraphs), natural texts (no comparable paragraph markup).
- **Tool:** `tools/c076_paragraph_depth2.py`, `timeout 600`, 8 processes.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
