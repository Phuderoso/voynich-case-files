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

## Results (run 2026-11-08 ~23:47 PT, 41 s, seed 7676, 8 processes; `analysis/C076_results.json`, `analysis/C076_run_log.txt`; pre-registration commit 604df62)
- **Design phase:** no q in the grid reached 9/10 in Currier A (best 6/10 at 0.24); Currier B reached 9/10 at 0.16 and 10/10 at 0.24. By the pre-registered rule **q\* = 0.24**. Median planted JSD at q\* (design, IT2a T): A 0.013, B 0.0096.
- **Gates at q\* (FPR / power out of 20):** Currier B passes everywhere except **ZL B T (FPR 3/20)**. Currier A fails power for T in both transcriptions (15/20, 13/20) and for IT2a S (13/20) and IT2a H2 (14/20); IT2a A Lst fails FPR (4/20). Ten tests entered Holm.

| Verdict | Currier A | Currier B |
|---|---|---|
| H1 top line T | NOT TESTABLE (power 15, 13) | **NOT TESTABLE** (ZL FPR 3/20; IT2a rejects after Holm) |
| H1 second line S | NOT TESTABLE (IT2a power 13) | **NOT DETECTED** (JSD 0.0012 / 0.0012, p 0.89 / 0.94; planted median 0.010) |
| H1 last line Lst | NOT TESTABLE (IT2a FPR 4) | **PARTIAL** (IT2a JSD 0.0038, p 0.004, rejects; ZL 0.0037, p 0.018, not after Holm) |
| H2 top line without p/f words | NOT TESTABLE (IT2a power 14; ZL rejects) | **DIFFERENT** (JSD 0.0051 / 0.0059, p 0.001 / 0.001, both reject after Holm) |

- **Manuscript JSD vs instrument (descriptive):** top-line body JSD in B is 0.021 in both transcriptions, about twice the median planted effect (0.009–0.012); in A 0.039–0.043 (planted 0.012–0.016). With p/f words removed, B keeps 0.005–0.006, below the median planted effect but rejected in both transcriptions.
- **What the B top-line body has, without p/f words (descriptive):** fewer `e` (−1.5 to −1.8 points of unit share), more `t` (+1.2 to +1.3), `r` (+1.2 to +1.3), `o` (+1.1). In A (not testable) more `sh` (+3.6 to +4.4) and fewer `k`, `a`.
- **Reading under the pre-registered interpretation:** the full top-line test (H1-T) is NOT TESTABLE in both languages, so the fixed rule "H1-T and H2 both DIFFERENT" cannot be applied. What stands: **in Currier B the body of the top line differs from middle lines even after every p/f-gallows word is removed**, and the second line does not differ at the instrument's detectable size. The last line in B shows a weak, one-transcription difference (fewer `d`).
- **Caveats:** (1) the H2 excess includes `t`, another gallows, so "beyond p/f" is not "beyond gallows"; Neal's and Pelling's observations also involve t-words. (2) Top-line interior words are longer (C071), and length alone could shift unit shares; a length-matched test is needed before reading this as a separate property. (3) The ZL B T FPR failure (3/20 at gate R = 200) is within what a correct test produces by chance (expected 1, P(≥3) ≈ 0.08), but the pre-registered rule is applied as written. (4) Currier A needs a stronger plant or more paragraphs; q 0.24 was not enough.
- **Audit of C071:** all twelve C071 descriptive JSD values are reproduced to the third decimal (same data, same statistic), and C071's NOT TESTABLE verdicts stand. C071's descriptive "second line indistinguishable" is now a gated NOT DETECTED in Currier B.
- **Next (F-PARA step 3, optional):** length-matched H2 (compare top-line and middle-line words of equal unit length), and removal of all gallows words (p f t k) as H3.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
