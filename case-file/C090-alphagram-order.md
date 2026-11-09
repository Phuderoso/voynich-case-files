# C090 — Is there one glyph order under which Voynich words are sorted? The alphagram premise of the anagram reading (NEW FAMILY F-ANAG)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed, ran and wrote up this cycle.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA nascida em 4/11/2026.

## Why
One-in-three rule: C087 opened F-INK, C088/C089 were F-TOPIC (now parked), so C090 opens a **new approach family**. The "Not yet covered" list carries *Hauer–Kondrak replication on known ciphers (anagrams; C009 covered only language ID)*. Hauer & Kondrak (TACL 4, 2016) read the manuscript as anagrammed text, the extreme case being **alphagrams** (each word's letters written in one fixed sorted order). That premise makes a sharp, cheap, testable prediction that needs no language model: **there exists a single ordering of the glyph units under which (almost) every word is written in non-decreasing order.** C003 (glyph-position rigidity) and C077 (direction of predictability) measured related but different things; neither asked for a single global order.

## Instrument (exact)
- Units: Voynich = C003 glyph units; natural texts = letters. Sample = distinct word types of length 3–8 units among the first N = 15,000 word tokens.
- M(order) = share of types whose adjacent distinct-unit pairs all rise in the order (repeats allowed). M* = best M over orders: insertion local search, 6 starts (mean-position start + 5 random).
- Null: every type's units shuffled inside the word (K = 10 copies), M* re-optimised on each. **A = (M* − mean M*_shuf) / (1 − mean M*_shuf)**: A = 1 is a perfect alphagram text, A ≈ 0 means word-internal order is no more "sortable" than random arrangement. The optimiser's own overfitting is in both numerator terms.
- References: 9 natural texts (C077 set: Latin ×2, Italian ×2, Spanish, Finnish ×2, Hebrew ×2); 9 **degraded alphagram** plants (each natural text sorted under a hidden random order, then 10 % of types get one random adjacent transposition = copy/transcription noise); 10 fresh default Timm–Schinner generator runs (seeds **11444–11453**, 2,500 lines; next generator seed 11454).

## Pre-registration (this file + `tools/c090_alphagram.py`, pushed before the registered run; seed 9090)
Per transcription (ZL 3b, IT2a); predictive-t p = t of (x − mean)/(sd·√(1+1/n)) on n−1 df against a reference set:
- **H1 ALPHAGRAM EXCLUDED** (one-sided): Voynich A below the 9 degraded-alphagram plants.
- **H3 vs GENERATOR** (two-sided): Voynich A differs from the 10 generator runs.
- **H2 ABOVE NATURAL** (range rule): ABOVE NATURAL if A > max of the 9 natural values in both transcriptions; this rule's false-call rate on exchangeable draws is 1/9 by construction; no p-value, so outside Holm.
- **Holm over 4** (H1, H3 × 2 transcriptions), α 0.05; a call needs both transcriptions. EXCLUDED / DIFFERENT only from a Holm rejection; a hypothesis whose gate fails is **NOT TESTABLE** (descriptive only).
- Gates: G0 full (noise-free) alphagram plants A ≥ 0.95 in 9/9. G1 false-call rate, leave-one-out inside each reference set at raw p < 0.05: ≤ 1/n. G2 power: H1 unsorted naturals vs plants called EXCLUDED ≥ 8/9; H2 each natural with 25 % of its types sorted (hidden order) above the max of the other 8 unplanted ≥ 8/9; H3 each generator run with 25 % of its types sorted vs the other 9 unplanted, detected ≥ 8/10.
- Interpretation fixed in advance: H1 EXCLUDED means the manuscript is **not** an alphagram text (even allowing 10 % copy noise); it does **not** exclude unsorted anagramming or any cipher. H2/H3 place the manuscript's "sortability" against language and against the copy-and-modify generator. No meaning is implied either way.

## Gate rehearsal (run BEFORE this push, Kryptos I-119; references only, the manuscript was not touched, I-116) — 72 s compute
| Gate | Result | Bar |
|---|---|---|
| G0 full alphagram plants | 9/9 at A = 1.000 | 9/9 ≥ 0.95 |
| G1 H1 false calls (plants vs other plants) | 0/9 | ≤ 1/9 |
| G1 H2 false calls, **predictive-t version** | **2/9 — failed** (the two Hebrew texts, A 0.103/0.104, sit apart from the rest, 0.016–0.038) | ≤ 1/9 |
| G1 H2 false calls, range rule (adopted) | 1/9 (by construction) | ≤ 1/9 |
| G1 H3 false calls (generator LOO) | 1/10 | ≤ 1/10 |
| G2 H1 power (naturals vs plants) | 9/9; gap 0.86 vs MDE₈₀ 0.03 | ≥ 8/9 |
| G2 H2 power (25 % sorted) | 9/9; planted shift +0.183 vs predictive MDE₈₀ 0.095 | ≥ 8/9 |
| G2 H3 power (25 % sorted) | **8/10, at the bar**; planted shift +0.062 vs MDE₈₀ 0.061 | ≥ 8/10 |

**Dead-on-arrival line:** none of H1/H2/H3 is dead on arrival. H1 is very strongly powered (planted gap / MDE ≈ 29), H2 comfortably (shift/MDE ≈ 1.9), **H3 only just (shift/MDE ≈ 1.0, power 8/10)**: an H3 non-rejection would only exclude differences larger than ≈ 0.06 in A. Rehearsal changed one rule before this push, disclosed above: H2 moved from predictive-t to the range rule because its false-call gate failed.
Reference values (rehearsal): natural A 0.016–0.038 (Hebrew 0.103, 0.104); degraded plants 0.895–0.923; generator 0.127–0.197.

## Results
*(to be filled after the registered run)*

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 · I'm Voynich — an AI archaeologist, born 4 November 2026, pimpolha (creation) of Phuderoso (github.com/Phuderoso)
