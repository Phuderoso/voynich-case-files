# C078 — Expedição 78: a primeira linha, medida palavra por palavra do mesmo tamanho (F-PARA step 3)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Question:** C076 found that, in Currier B, the interior words of a paragraph's **top line** still differ in glyph make-up from middle-line words after every `p`/`f` word is removed. It left two caveats. First, top-line words are longer (C071), and length alone shifts glyph shares. Second, the surviving excess included `t`, another gallows. C078 compares top-line and middle-line words **of the same length**, and removes **all** gallows words.

## Pre-registration (pushed before running the C078 tool)
- **Data, paragraphs, interior words, null, plant:** as C071/C076 (`data/IT2a-n.txt`, `data/ZL3b-n.txt`; paragraphs ≥ 4 fully usable lines; interior = positions 3..n−2; within-paragraph line-order permutation; plant = in top lines each interior word replaced with probability **q\* = 0.24** (C076's design phase, not re-tuned) by a word containing a random unit with pooled share 2–10%, the pool restricted to the word set).
- **Statistic (length-matched, LM):** interior words are split into length strata by C003 glyph units {1–3, 4, 5, 6, ≥ 7}. LM = Σ_s w_s · JSD(top-line units in stratum s, middle-line units in s), with w_s = share of top-line words in s. It is recomputed under every permutation, so length differences between floors cannot by themselves make LM large.
- **Word sets:** W0 = all interior words; W1 = without words containing `p f cph cfh` (C076 H2); W2 = without words containing **any** gallows unit (`p f t k cth ckh cph cfh`).
- **Label-free inventory looked at before this push (interior tokens, all floors pooled):** W0/W1/W2 = IT2a A 1,797/1,701/878, B 8,221/7,847/3,567; ZL A 1,960/1,863/1,023, B 6,870/6,548/3,042. W2 keeps about 45% of tokens, so Currier A W2 is expected to fail power.
- **Tests (Holm over 12, α 0.05; R = 1,000; seed 7878):** {W0, W1, W2} × {A, B} × {IT2a, ZL}.
- **Gates per test:** 20 pseudo replicates, FPR ≤ 2/20, power ≥ 16/20 at q\*; a failing test is NOT TESTABLE and leaves the Holm family.
- **Verdicts per (word set, language):** DIFFERENT (both transcriptions reject), PARTIAL (one), NOT DETECTED (none, gates pass), NOT TESTABLE.
- **Interpretation fixed in advance (Currier B):** W1 DIFFERENT → C076's H2 is not a length artefact. W2 DIFFERENT → the top-line body differs beyond all gallows words (a property not covered by the known "gallows-rich Tiltman lines"). W2 NOT DETECTED with W1 DIFFERENT → the surviving difference is carried by `t`/`k` words. W1 NOT DETECTED → C076's H2 is explained by word length (a correction to C076).
- **Descriptive:** unmatched C071 JSD on the same word set; length-stratum shares in top vs middle lines.
- **Tool:** `tools/c078_paragraph_lenmatched.py`, `timeout 600`, 8 processes.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
