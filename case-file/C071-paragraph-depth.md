# C071 — Expedição 71: os andares do parágrafo (NEW FAMILY F-PARA, the paragraph as a unit)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Question:** does the glyph make-up of a line's **interior** words depend on the line's floor in its paragraph — top line, second line, last line — compared with the paragraph's middle lines? Top lines are known to carry gallows-rich first words (Currier; Pelling's "Tiltman lines"), but that is a line-edge fact. C071 removes every word our earlier families found special (word 1, word 2 — C070's sh boost — and the last two) and asks whether the **body** of the line still knows which floor it is on.

**Why a new family:** rows 1–70 study the line from left to right (F-LINE), neighbouring lines (F-VERT, F-NEIGH), pages, leaves and sections (F-COD, F-CROSS), but no cycle uses the line's depth within its paragraph. The rule "at least one new family every three cycles" required it now (last new family C068). Planned C071 word-2 robustness moves to C072.

## Pre-registration (pushed before running the C071 tool)
- **Data:** `data/IT2a-n.txt`, `data/ZL3b-n.txt` (sha256 in `data/MANIFEST.md`). Paragraph = consecutive `P*` lines of one page from a line opening with `<%>` to the next line containing `<$>`; kept only if **≥ 4 lines** and **every** line is usable (no `<->`, all words `[a-z]+` after C068 markup rules). Counts before any statistic: IT2a 326 paragraphs (A 86, B 237; 2,184 lines), ZL 299 (A 89, B 206; 1,946 lines).
- **Interior words:** positions 3..n−2. Glyph units: C003 units (`ch sh cth ckh cph cfh` one unit).
- **Classes:** T = line 1, S = line 2, M = lines 3..last−1, Lst = last line.
- **Statistic:** Jensen–Shannon divergence (bits) between pooled unit counts of class X and class M, X ∈ {T, S, Lst}.
- **Null:** within every paragraph the line order is permuted (so each paragraph's vocabulary, its number of lines and every line's content are kept; only which line holds which floor changes); R = 1,000; p = (1 + #JSD* ≥ JSD)/(R + 1).
- **Tests (Holm over 12, α 0.05):** {T, S, Lst} × {Currier A, Currier B} × {IT2a, ZL}.
- **Gates (per test; 20 pseudo replicates with lines pre-permuted within paragraphs; gate permutations R = 200; seed 7171 + offsets):** FPR p ≤ 0.05 in ≤ 2/20; power — in class-X lines each interior word replaced with probability 0.08 by a word drawn uniformly from the subset's 20 commonest interior words — p ≤ 0.05 in ≥ 16/20. No design run; Currier A (86–89 paragraphs) may fail power, which would make it NOT TESTABLE.
- **Verdict per (X, language):** DIFFERENT (both transcriptions reject after Holm), PARTIAL (one), NOT DETECTED (none, gates pass), NOT TESTABLE.
- **Descriptive (no p claims):** the five units with the largest share difference X − M; mean interior-word length by class.
- **Not done here:** generator (it has no paragraphs) and natural texts (no comparable paragraph markup) — a later step can wrap known texts with real paragraph breaks.
- **Tool:** `tools/c071_paragraph_depth.py`, `timeout 600`, 8 processes.

## Results (run 2026-11-08 19:49:02–19:49:18 PT, 15.8 s, seed 7171, 8 processes; `analysis/C071_results.json`, `analysis/C071_run_log.txt`; pre-registration commit a6babe8)
- **Gates: FPR passes everywhere (1–2/20), power FAILS everywhere (0–4/20).** All 12 tests are **NOT TESTABLE** under the pre-registered rule. No Holm step was run.
- **Why the power gate failed (design error, disclosed):** the plant replaced interior words with the subset's 20 **commonest** words. Common words carry roughly the average glyph mix, so planting them barely moves a class's unit distribution — and partly moves it *toward* the middle lines. The plant was too weak by construction; this says the gate was badly chosen, not that the instrument is blind. A one-gate-job check after the run (IT2a B, replicate 0, no manuscript number involved) confirmed planted p values of 0.08–0.53.
- **Manuscript numbers (descriptive only, no verdict):**

| Class vs middle lines | IT2a A | ZL A | IT2a B | ZL B |
|---|---|---|---|---|
| Top line (T) | JSD 0.043, p 0.001 | 0.039, p 0.001 | 0.021, p 0.001 | 0.021, p 0.001 |
| Second line (S) | 0.004, p 0.98 | 0.003, p 1.00 | 0.001, p 0.89 | 0.001, p 0.95 |
| Last line (Lst) | 0.009, p 0.28 | 0.011, p 0.036 | 0.004, p 0.005 | 0.004, p 0.020 |

  (p from the within-paragraph permutation null, R = 1,000, floor 0.001; not gated, so not evidence.)
- **What the numbers suggest (to be tested in step 2):** the body of a **top line** still differs after removing words 1, 2 and the last two — more `p` (+2.7 to +3.7 points of unit share) and, in Currier A, more `sh` and fewer `k`; in B fewer `e`, `k`, `i`, `n`; and interior words are longer (B 4.94–4.98 vs 4.57–4.65 units). The **second line is indistinguishable** from the middle lines (p ≥ 0.89) — the top-line effect ends after one line. The **last line** may differ weakly in Currier B (fewer `d`).
- **Not excluded, not established:** any floor effect. The top-line `p` excess is consistent with the long-known gallows-rich top lines extending beyond the first word, which a step 2 must test with a gate that can see it.
- **Step 2 plan:** plant = move a fixed share of glyph-unit mass (e.g. replace interior words by words drawn from a skewed pool such as `p`/`f`-containing words, or shift a unit's share by a set amount), calibrated on a disclosed design seed with no manuscript number; same tests, fresh seed.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
