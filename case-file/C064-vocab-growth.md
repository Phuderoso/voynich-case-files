# C064 — Expedição 64: crescimento do vocabulário e compressibilidade (F-ZIP, new family, step 1)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Why this family (and not F-SPACE):** word-boundary placement is largely covered already by F-SEG (C034–C040: Harris boundary score, comma half-spaces, Takahashi agreement) and by C006/C008 (word-edge coupling), so F-SPACE would repeat. F-ZIP is untouched: C044/C045 measured the Zipf slope and word-length spread, C037/C055 recurrence and clumping, but nobody here has measured how fast the vocabulary grows (Heaps' law), how many types are hapax, or how much the word *order* helps a dictionary compressor. F-ZIP also has the cleanest planted-control design of the three candidates (inflate / deflate / shuffle plants have an exact known effect on each statistic). F-CROSS stays in the backlog.

## Pre-registration (pushed before any C064 number)
- **Data:** `data/ZL3b-n.txt` (ZL IVTFF 3b of 13/05/2025) and `data/IT2a-n.txt` (Takahashi, IT 2a of 02/02/2023 mod. 25/06/2025), sha256 in `data/MANIFEST.md`. Paragraph text as C047; units as C003 (`ch`, `sh`… single units). Two disjoint windows per transcription: **first 15,000** and **last 15,000** tokens.
- **Statistics (N = 15,000 tokens):** **S1** Heaps exponent β = slope of log V(N) on log N at N = 1000, 2000, 4000, 8000, 15000; **S2** hapax share = types seen once / types; **S3** order gain G = 1 − xz(text) / mean xz(5 word-order shuffles) (Python `lzma`, preset 9, words joined by single spaces).
- **References:** (H1) 12 natural texts as C051/C058 (9 + 3 devowelled; only those with ≥ 15,000 tokens; first 15,000); (H2) the Timm–Schinner generator, default settings, 3,400 lines, **fresh seeds 6401–6460**, first 40 texts with ≥ 15,000 tokens.
- **Decision rule (fixed now):** per statistic and reference, classify each of the 4 Voynich windows as below / inside / above the reference range (min–max). **OUTSIDE** if all 4 are strictly beyond the range on the same side; **INSIDE** if all 4 are inside; otherwise **STRADDLE**. A 12-text range is not a p-value, so no p is claimed and no multiplicity correction applies; 6 verdicts (3 stats × 2 references). The generator two-sided rank p (around its median) is reported descriptively only.
- **Gates (a statistic is NOT TESTABLE unless it passes both):** (a) leave-one-out: each natural text vs the other 11 → outside-range count ≤ 3/12 per statistic (a 12-text range gives ≈ 2/12 by chance); (b) planted power, 20 plants each on natural texts: *inflation* (10% of tokens turned into fresh unique types) must lift S1 and S2 above the natural maximum in ≥ 16/20; *deflation* (types of rank > 100 merged into 50 pooled types) must push S2 below the natural minimum in ≥ 16/20; *order destruction* (global word shuffle) must push S3 below the natural minimum in ≥ 16/20.
- **Reading rules:** OUTSIDE-NATURAL says the transcribed word vocabulary grows / compresses unlike the 12 natural texts (a property of the writing system or the transcription, not evidence for or against meaning). INSIDE says nothing unusual. Generator OUTSIDE means a measured difference to report, not a verdict on the self-citation account. Natural texts are different authors, genres and sizes of source, so the natural range is wide by design; section/Currier mixing in the manuscript windows is a known confound, disclosed here.
- **Not testable ≠ excluded** will be kept apart in the write-up.
- **Tool:** `tools/c064_vocab_growth.py` → `analysis/C064_results.json`; seed 6464; `timeout 600`; 8 processes. Reuses C003/C047/C051/C055/C058 helpers.

*Results below are added after the run.*

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
