# C019 — Mending the crate: the one-to-one reader, re-gated
### Expedição 19 · family F-LLM, step 0b (repair of C018)

> **Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. **Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026. An AI did all of this work.

Status: **PRE-REGISTERED** (committed before the counted run; results appended below).

## Question
C018's one-to-one reader (INJ: one Latin letter per glyph, exact words of the Caesar lexicon) failed its gate 5/10, partly
because two "Latin" positives were German and French front matter and partly because greedy search stalled. With both
defects repaired, does INJ separate enciphered Latin from meaningless text, and if so, does any Voynich passage
(ZL 3b, one page each) read as Latin above the bar of meaningless controls?

## Repairs (fixed in `tools/c019_inj_regate.py` before the design step)
1. **Latin-only filter for positives**: a 100-word Descartes passage (`pg23306`) is banked only if all its letters are
   in the lexicon alphabet and ≥ 35 % of its tokens are Caesar-lexicon words under the *true* text. The filter reads
   only the plaintext, never a reader output.
2. **Stronger search**: simulated annealing, 16 restarts × 20 000 proposals, temperature 2.0 → 0.05 linear, best state kept.
Everything else as C018: CMR = share of 100 tokens decoded into a lexicon word (length ≥ 2); classes P1 (mono-sub
Descartes), N1 Timm–Schinner generator, N2 random EVA with Voynich glyph and length distributions, N3 glyph-shuffled
Voynich, V Voynich; 10 items each, shuffled blind order, salted answer hashes in `analysis/C019_blind_bank.json`.

## Design step (power first, seed 19519, already run and published with this file: `analysis/C019_design.json`, `analysis/C019_design_log.txt`)
Gate 10/10: P1 0.48–0.67, every P1 item reached its true-key score (no stalls); negatives max 0.32 (N1 0.21–0.32,
N2 0.12–0.16, N3 0.09–0.19). One passage was rejected by the filter. **Disclosed:** the design step also scored 10
Voynich passages (0.14–0.30, none above 0.32). These are other passages than the counted ones, which come from a new seed.

## Decision rule (counted run, seed 19019, one run)
1. **Gate**: ≥ 9/10 P1 items above the maximum of all 30 negatives. Otherwise INJ is *not discriminating* and V is *not testable*.
2. **Voynich**: count V items above the negative maximum. ≥ 3/10 (binomial p ≈ 0.004 under exchangeability, chance 1/31 each) = **Latin-like signal under INJ**, which would go to the §4 protocol and image checks before any claim; 0–2 = **no reading above the bar**.
3. One reader, one look: α = 0.05, no further correction.

## Limits stated in advance
"No reading above the bar" excludes only **Latin under a one-to-one key on EVA glyph units**, with passages at least as
lexicon-rich as the positives (≥ 35 % coverage, after the filter). It says nothing about verbose ciphers (one letter →
several glyphs), nomenclators, other languages, abbreviation, or a different glyph segmentation. Caesar's vocabulary is
military; a herbal Latin would have lower coverage and less power. The positives are 100-word passages from one author.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
