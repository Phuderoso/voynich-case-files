# C049 — Expedição 49: os vizinhos que se parecem (do words that share contexts also share spellings?)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** **F-EMB (new family: distributional embeddings).** C046–C048 were three F-PAIR cycles, so this cycle opens a new approach family, as the one-in-three rule asks. It uses the simplest word embedding (PPMI context vectors) to ask whether the manuscript's distributional structure is tied to its spelling structure.

## Question
In an inflected natural language, words with a shared ending often share grammatical contexts, so context similarity and spelling similarity are mildly linked. Timm & Schinner's self-citation idea (words copied from nearby words with small changes) would predict a link too, possibly a stronger one. How strong is the link in the Voynich text, and where does it sit against natural texts?

## Pre-registration (pushed before any C049 Voynich number)
- **Data:** ZL 3b and IT2a (`data/ZL3b-n.txt`, `data/IT2a-n.txt`) via `tools/c003_position_rigidity.py: voynich()` (all loci, commas split); EVA units (`ch`, `sh`, `cth`, … as one unit). Natural: Caesar, Descartes (Latin), Dante, Machiavelli (Italian), Cervantes (Spanish), Genesis, Exodus (Hebrew, consonantal), lines with < 3 words dropped. Two disjoint halves per text: tokens 0–15,000 and 15,000–30,000.
- **Statistic:** K = 200 most frequent types per half. Context vector = counts of the 500 most frequent words within ±2 positions on the same line, PPMI weighted, cosine similarity. Spelling similarity = 1 − Levenshtein / max length (units). **ρ** = Spearman correlation over the 19,900 type pairs.
- **Null:** Mantel permutation, spellings shuffled across the 200 types (context matrix fixed), 200 permutations; one-sided p = (1 + #null ≥ obs)/201.
- **Gates (natural text only, 20 trials each):** FPR — a natural half recoded by a random bijection (each type → random string of the same length over the text's letters), which destroys any spelling–context link; pass ≤ 2/20 at p < 0.05. Power — a recoded half in which 25% of the top-200 types take their nearest context neighbour's spelling with one letter changed; pass ≥ 14/20 at p < 0.05.
- **H1 (link exists):** LINKED if p < 0.0125 (0.05 / 4) in all four Voynich halves (2 transcriptions × 2 halves); NOT LINKED if p ≥ 0.0125 in all four; SPLIT otherwise; NOT TESTABLE if a gate fails.
- **H2 (strength vs natural):** natural range = min–max of the 14 natural half-values of ρ. HIGHER if all four Voynich ρ > max; LOWER if all < min; INSIDE if all within; STRADDLE otherwise. Disjoint halves are used because C045 showed overlapping windows understate between-sample spread.
- **Look (descriptive, no verdict):** ρ on the Timm–Schinner generator output (`data/corpora/ts_generated_text.txt`, only ~10,900 tokens, so first 10,000) beside ZL 3b's first 10,000 tokens.
- **Reading rule fixed in advance:** a link (H1) or HIGHER (H2) is compatible with both inflectional morphology and self-citation; it does not decide between them and says nothing about meaning. The generator Look only hints which.
- **Disclosure:** while timing the tool, one natural number was seen (Caesar first half, ρ ≈ −0.01, p 0.88). No Voynich number was seen.
- **Tool:** `tools/c049_context_spelling.py` → `analysis/C049_results.json`. Seed 4949, `timeout 600`.

## Results
*(to be added after the run)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
