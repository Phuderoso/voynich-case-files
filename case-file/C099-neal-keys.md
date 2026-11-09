# C099 — NEW FAMILY F-KEY, step 1: do p/f-words sit next to each other on paragraph top lines ("Neal keys")?

**Status:** PRE-REGISTERED 2026-11-09 ~16:52 PT (commit `e601bfb`), before any count on the real lines. **Result:** Q20 top lines REPLICATED (1.3×), top lines outside Q20 NOT DETECTED, non-top lines REPLICATED (sparse), and the position-preserving check HOLDS.

## Why this cycle, and a correction first
**Correction to the C098 pointer.** The README pointer I wrote in C098 proposed Pelling's *word-2 sh-initial boost* as a "new family" for C099. That claim was already tested here in **C070, C072 and C073** (REPLICATED, and ABOVE the generator after a matched baseline). The pointer was my error: I hadn't searched my own coverage table. The rule of one new family in three still applies, so C099 opens a genuinely new family on the other open external claim in the backlog, **Neal keys**.

**The claim (external).** P. Neal, as quantified by N. Pelling on Cipher Mysteries ([4 Nov 2026](https://ciphermysteries.com/2026/11/04/voynich-q20-neal-keys-update)): on the top (Tiltman) line of a paragraph, the non-initial words that contain a single-leg gallows (EVA `p` or `f`) are adjacent to each other **5.4% vs 2.7% expected**. Pelling reads the behaviour as tied to top lines ("modal"), and also as "largely true throughout".

**Family F-KEY** is new: it tests the **co-location of a word class inside a line** (do members of a class sit next to each other?). Earlier families tested a slot's content (F-LINE), a line's glyph mix (F-PARA), word junctions (F-JUNC) and repeats across text (F-BURST, F-REP).

## Design (fixed now)
- **Lines:** C070's parser, verbatim. That means paragraph loci, no `<->`, clean words, and at least 5 words per line. A top line is one that starts with `<%>`. Word 1 is excluded. A p/f-word is any word containing `p` or `f`.
- **Statistic:** A = the number of adjacent p/f–p/f pairs at positions 2..n, summed over lines. The ratio is A / E[A].
- **Null:** words 2..n are permuted within each line, R = 4,000. The p value is one-sided, (1 + #A* ≥ A)/(R + 1).
- **Tests (Holm over 6):** {S1 Quire 20 top lines, S2 top lines outside Q20, S3 non-top lines in all quires} × {IT2a, ZL 3b}.
- **Robustness R1 (its own Holm over 2):** all top lines with a **position-preserving** null, which permutes separately within the first and second half of positions 2..n. A shared liking for early slots then cannot manufacture adjacency.
- **Gates per test (seed 9999):**
  - The pseudo text is 20 replicates of the subset's own lines with words 2..n shuffled.
  - FPR: p ≤ 0.05 in at most 2 of 20.
  - Power: for each line with at least 2 p/f-words and no adjacent pair, with probability q = 0.80, swap one p/f-word into the slot next to another. It must reach p ≤ 0.05 in at least 16 of 20.
  - q was fixed by a rehearsal on **shuffled** IT2a top lines only (`analysis/C099_rehearsal_log.txt`). It plants a ratio of about 1.5, half the claimed excess.
  - A failed gate makes that test **NOT TESTABLE**.
- **Verdict per subset:**
  - **REPLICATED** if both transcriptions reject after Holm;
  - **PARTIAL** if only one does;
  - **NOT DETECTED** if neither does and the gates pass.
- **Registered reading:**
  - S1 and S2 REPLICATED, with S3 NOT DETECTED, means the clustering is a top-line feature, as Pelling claims.
  - S3 REPLICATED as well means the clustering is general.
- **Descriptive, no verdict:**
  - the same ratio for k-words and t-words on top lines;
  - in adjacent pairs, the share of left keys ending in `-dy` and of right keys starting `o-`/`qo-`, against all p/f-words (Pelling: 41% vs 32%, and 61% vs 52%).
- **Not addressed:** the Timm–Schinner generator, which has no paragraphs. A generator comparison needs a paragraph model first.
- **Compute:** about 1–2 minutes, run under `timeout 600`.

Run: `timeout 600 python tools/c099_neal_keys.py analysis/C099_results.json`

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

---
## Results
**Run 2026-11-09 ~16:53 PT, 38 s.** Prereg commit `e601bfb`. Files: `analysis/C099_results.json` and `analysis/C099_run_log.txt`. **All 8 gates passed** (FPR 0–2/20, power 20/20).

| Subset | IT2a: A vs E (ratio), Holm p | ZL 3b: A vs E (ratio), Holm p | Verdict |
|---|---|---|---|
| S1 Quire 20 top lines (283 / 276 lines) | 116 vs 86.3 (**1.34**), 0.0015 | 112 vs 85.9 (**1.30**), 0.0015 | **REPLICATED** |
| S2 top lines outside Q20 (302 / 294) | 137 vs 131.0 (1.05), 0.32 | 137 vs 129.5 (1.06), 0.32 | **NOT DETECTED** |
| S3 non-top lines, all quires (2,386 / 2,400) | 24 vs 13.2 (**1.82**), 0.0022 | 25 vs 14.0 (**1.78**), 0.0015 | **REPLICATED** (sparse: only ~240 p/f-words) |
| R1 all top lines, position-preserving null | 253 vs 228.9 (1.11), 0.0055 | 249 vs 228.2 (1.09), 0.0062 | **HOLDS** |

**Reading.** The registered branches did not foresee this pattern, so here it is in plain words.
- **Quire 20 top lines:** Neal-key clustering is real, both transcriptions agree, and it survives a null that keeps early/late slot preferences. The excess is about 1.3×, smaller than the 2× in Pelling's raw figure.
- **Top lines outside Q20:** no clustering. The gate could detect a planted 1.5×, so a strong effect of that size is unlikely there. A small one is **not excluded**.
- **Non-top lines:** the rare p/f-words also stick together, at about 1.8×, but on only about 25 pairs.
- **Overall:** the behaviour is neither "a top-line feature" in general nor clearly "general". It is strongest where p/f-words are rare (non-top lines) and in Q20, and it is absent on top lines elsewhere.

**Descriptive, no verdict.**
- On all top lines, **t-words cluster too** (ratio 1.22 / 1.20, p at the floor), and so do k-words (1.09). Pooled over S1+S2, p/f-words give (116+137)/(86.3+131.0) ≈ 1.16. So across all top lines p/f-words do **not** cluster more than t-words. Pelling's "more than k/t" comparison was on Q20 only.
- In adjacent p/f pairs, 34–36% of left keys end in `-dy`, against 28% of all p/f-words (Pelling: 41% vs 32%). Right keys start with `o-`/`qo-` in 57–58% of cases, against 49–50% (Pelling: 61% vs 52%). The direction matches Pelling and the size is a little smaller.

**Not addressed:** the generator, which has no paragraphs.

**Audit of C098 (this cycle).** All four TOST gate tables were recomputed from the 40 stored runs in `analysis/C098_results.json`, and they reproduce exactly: δ1 N3 3/40 and 20/20, N4 2/40 and 18/20; δ2 8/20 and 0/20. The verdict is unchanged.
