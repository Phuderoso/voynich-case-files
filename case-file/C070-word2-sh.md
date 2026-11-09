# C070 — Expedição 70: a segunda palavra (F-LINE step 5, test of an external claim)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Question:** on 2026-11-08 Nick Pelling reported [a "Word 2 sh-initial boost"](https://ciphermysteries.com/2026/11/08/the-mysterious-word-2-sh-initial-boost): in Quire 20 (Takahashi transcription) the second word of a line is sh-initial about twice as often as mid-line words (top lines 21.2% vs 9.9%; other lines 16.7% vs 6.8%; found with the help of an AI assistant). C070 asks: (1) does it replicate in Q20 with a calibrated within-line null, in two transcriptions; (2) does it hold outside Q20, in Currier A and in the rest of Currier B; (3) does the Timm–Schinner generator produce it? Our F-LINE family (C030–C033) studied line-edge glyphs but never word 2. This is a test of someone else's published observation; the manuscript numbers for this exact statistic have not been computed by us before.

## Pre-registration (pushed before running the C070 tool)
- **Data:** `data/IT2a-n.txt` (Takahashi IT 2a) and `data/ZL3b-n.txt` (ZL 3b), sha256 in `data/MANIFEST.md`. Paragraph loci (`P*`), lines without drawing breaks `<->`, every word `[a-z]+` after markup removal (C068 rules; dots and commas both separate words), **≥ 5 words**. Top line = the line opens a paragraph (`<%>`). Quire 20 = `$Q=T`; Currier language from `$L`. Line counts (counted before any statistic): IT2a 2,971 lines (Q20 1,029; A 796; B outside Q20 1,106; top lines 585); ZL 2,970 (1,005; 826; 1,100; 570). Our word splitting (commas as separators, damaged lines dropped) may differ from Pelling's, so his exact percentages are not expected.
- **Statistic:** D = share of sh-initial words (EVA word starts `sh`) at position 2 − share at positions 3..n−2 (word 1 and the last two words excluded, since Pelling reports those as special too).
- **Null:** within each line, the words at positions 2..n−2 are permuted (word 1 and the last two fixed); R = 4,000; one-sided p = (1 + #D* ≥ D)/(R + 1). This keeps each line's vocabulary and length.
- **Tests (Holm over 6, α 0.05):** {Q20, Currier A, Currier B outside Q20} × {IT2a, ZL}.
- **Gates (per test, 20 pseudo replicates of the subset's own lines with positions 2..n−2 shuffled, seed 7070 + offset):** FPR p ≤ 0.05 in ≤ 2/20; power: plant — in each line with probability 0.10, if word 2 is not sh-initial and an sh-initial word sits at 3..n−2, swap them — p ≤ 0.05 in ≥ 16/20. No design run. A failed gate makes that test NOT TESTABLE.
- **Verdict per subset:** REPLICATED (both transcriptions reject after Holm), PARTIAL (one), NOT DETECTED (none, gates pass), NOT TESTABLE.
- **Generator family (separate, α 0.05):** V = D on all Currier B lines (IT2a; ZL descriptive) vs 40 default Timm–Schinner runs (fresh seeds 10301–10345, first 40 valid, 1,500 lines, lines ≥ 5 words; the generator has no paragraphs); rank p = (1 + #gen D ≥ V)/41. Gates on 20 held-out runs (10401–10425): FPR ≤ 2/20, power (same plant) ≥ 16/20. Verdict ABOVE GENERATOR / NOT DETECTED / NOT TESTABLE.
- **Descriptive (no p claims):** sh-initial share by position (words 1–6, mid, last two) for top and other lines; D for other word-initial groups (`ch q o d y s k t p a l c`) in Currier B — is the boost specific to `sh`?
- **Tool:** `tools/c070_word2_sh.py`, `timeout 600`, 8 processes.

## Results (run 2026-11-08 19:02:26–19:02:43 PT, 16.7 s, seed 7070, 8 processes; `analysis/C070_results.json`, `analysis/C070_run_log.txt`; pre-registration commit bb6af74)
- **Gates (all pass):** FPR 0–1/20 for the six manuscript tests; power 16–20/20 (ZL Currier A at the minimum, 16/20). Generator family: FPR 2/20 (at the limit), power 20/20, 40 + 20 valid runs.

| Subset | Transcription | lines | sh share at word 2 | sh share at words 3..n−2 | D | p (R = 4,000, floor 0.00025) | Holm |
|---|---|---|---|---|---|---|---|
| Quire 20 | IT2a | 1,029 | 0.177 | 0.077 | +0.100 | 0.00025 | reject |
| Quire 20 | ZL | 1,005 | 0.169 | 0.075 | +0.094 | 0.00025 | reject |
| Currier A | IT2a | 796 | 0.156 | 0.104 | +0.051 | 0.00025 | reject |
| Currier A | ZL | 826 | 0.156 | 0.097 | +0.059 | 0.00025 | reject |
| Currier B outside Q20 | IT2a | 1,106 | 0.203 | 0.111 | +0.092 | 0.00025 | reject |
| Currier B outside Q20 | ZL | 1,100 | 0.193 | 0.111 | +0.082 | 0.00025 | reject |

- **Verdict: REPLICATED in all three subsets** (Q20, Currier A, Currier B outside Q20), in both transcriptions. Pelling's observation holds and is **not confined to Quire 20**; in Currier A it is about half as large (D ≈ +0.05 vs +0.08–0.10).
- **Match to Pelling's numbers (Q20, IT2a, descriptive):** top lines word 2 20.5% vs mid 9.9% (his 21.2% vs 9.9%); other lines 16.6% vs 6.7% (his 16.7% vs 6.8%). Small differences are expected from our word splitting and dropped damaged lines.
- **Generator: ABOVE GENERATOR.** Currier B D = +0.098 (IT2a; ZL +0.089) vs 40 default Timm–Schinner runs −0.015 to +0.020 (median +0.003); rank p = 1/41 = 0.024 (the floor), both transcriptions above every run. The default generator does not produce a word-2 sh boost. With its FPR at 2/20 (the limit), the clear separation (V about 5× the generator maximum) is what carries the verdict, not the p value.
- **Profile (descriptive, IT2a):** sh-initial is rare at word 1 (0.4–1.5% top lines, 4–8% other lines), peaks at word 2, is flat in the middle, and drops at the last two words — Pelling's shape, in every subset.
- **Other initials in Currier B (descriptive, post hoc, no p values):** D for `ch` +0.004 / +0.017, `a` +0.021 / +0.020, `q` −0.039 / −0.035, `o` −0.041 / −0.031, others within ±0.018 (IT2a / ZL). The word-2 excess is mostly `sh`; `q` and `o` words are rarer than usual at word 2.
- **Not tested here:** why. Word 1 is fixed by the null, so the effect is not caused by word 1's own glyphs being rare; whether it depends on word 1's form (e.g. its length or ending), on scribal hand, or on the Neal-key / gallows top-line structure is open.
- **Credit:** observation by Nick Pelling (Cipher Mysteries, 2026-11-08). C070 adds a calibrated null, a second transcription, the whole manuscript and the generator comparison.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
