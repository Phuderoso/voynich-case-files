# C023 — Same distance, same hand: repairing the broken rope of Expedição 22
### Expedição 23 · family F-COD (codicology), step 3

> **Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. **Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026. An AI did all of this work.

Status: **PRE-REGISTERED** (written before any similarity was computed for this look). Results will be appended below.

## Question
C022 Look D (conjugates vs pairs at the same bound distance) was not testable: its re-pairing null rarely landed in
the distance-matched set (power 0/40). Repaired question: **are conjugate leaves more alike than other leaf pairs of
the same quire that lie at exactly the same bound distance and share LFD hand, Currier language and illustration type?**
This removes any explanation by "how far apart the leaves are in the bound book".

## Design (`tools/c023_distance_null.py`, seed 23023; leaves, similarity, redraw and plant from C021 unchanged)
- Cells = (quire, bound distance |folio number difference|) holding an eligible conjugate pair and ≥ 1 other eligible
  pair. Structure check (no similarities): 24 cells, 24 conjugate pairs, 74 comparison pairs.
- S = mean similarity of the conjugates − mean similarity of the other pairs in the cells.
- Null (distance-preserving): in each cell, the conjugate label goes to a random eligible pair of that cell; 4000 draws; one-sided p.
- One look, α = 0.05 (no other look this cycle).
- Gates: FPR at α ≤ 0.075 on 40 destroyed corpora; power ≥ 0.8 on 40 planted corpora (20 % of one conjugate leaf's
  words from its partner). A failed gate means **not testable**.
- Decision: p ≤ α **detected**; p > α with gates passed **not detected** (a 20 %-shared effect excluded at equal distance).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
