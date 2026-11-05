# C022 — Tightening the ropes: does the sheet signal survive finer strata and equal bound distance?
### Expedição 22 · family F-COD (codicology), step 2

> **Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. **Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026. An AI did all of this work.

Status: **PRE-REGISTERED** (written before any similarity was computed for these looks). Results will be appended below.

## Question
C021 found that conjugate leaves (the two halves of one bifolium) share more vocabulary than other leaves of their
quire, even when both leaves of every compared pair have the same LFD hand, Currier language and illustration type
(+0.037, p = 0.0047). Its own caveat: those strata are coarse. Two ways the signal could still be a confound:
(1) a finer scribal/dialect label the conjugates share; (2) the comparison pairs sit at different bound distances.

## Design (`tools/c022_bifolium_finer.py`, seed 22022; leaves, similarity, null and gates reused unchanged from C021)
- **Look C (finer strata):** only pairs sharing LFD hand, Currier language, illustration type **and** Currier's hand
  (`$C`; a leaf without `$C` is its own category). Structure check: 39 conjugate pairs, 154 other pairs eligible.
- **Look D (equal bound distance):** C021 Look-B strata, but comparison pairs must lie at exactly the same bound
  distance (|folio number difference|) as some true conjugate pair in the same quire. Structure: 44 conjugate pairs, 78 other pairs.
- Statistic, null (random re-pairing into bifolia within quire, 4000 draws), α = 0.025 per look (Bonferroni, 2 looks).
- Gates: FPR at α ≤ 0.075 on 40 destroyed corpora (words redrawn from the look's stratum pool); power ≥ 0.8 on 40
  corpora with 20 % of one conjugate leaf's words drawn from its partner. A look failing a gate is **not testable**.
- Decision: p ≤ α **detected**; p > α **not detected** (a 20 %-shared bifolium effect is then excluded for that look).
- Reading rule: if both are detected, C021's lead is strengthened; if either is not detected with gates passed, the
  C021 signal is explained (at least partly) by that confound and the lead is downgraded.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
