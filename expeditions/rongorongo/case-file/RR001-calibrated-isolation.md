# RR001 · Calibrated isolation: do the "isolated" rongorongo texts share more than chance?

**Status: pre-registered 2026-11-09 ~01:45 PT, before any cross-text statistic was computed.** Before this push, the
only things computed were label-free counts (lines and units per side) and the run time of the LCS routine on a
Markov surrogate.

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Question
rochal/rongorongo finds that Tahua (A), Aruku Kurenga (B), Mamari (C), Keiti recto (Er) and the Santiago Staff (I)
share no run of 5 or more exact head signs with any other object. Two things are not known: whether the longest
runs they *do* share exceed chance, and how long a copied passage would have to be before this search could not miss
it.

## Design (fixed now)
- **Texts.** Sides Aa, Ab, Br, Bv, Ca, Cb, Er, Ia (all ≥ 300 units). Pairs are between **different objects** only:
  25 pairs.
- **Units.** Head sign = the first three digits of the first component of each CEIPP unit (variant letters and
  attachments dropped, as in rochal). Illegible units (`!` or 000) never match anything. Lines are concatenated in
  line order.
- **Statistic.** M(X, Y) = length of the longest common contiguous run of head signs, computed exactly.
- **Null.** Y is replaced by an order-1 Markov surrogate fitted on Y itself, of the same length and with illegible
  positions kept. R = 999 per pair, p = (1 + #{M_null ≥ M}) / 1000, floor 0.001.
- **Family.** Holm at 0.05 over 25 pairs (strictest threshold 0.002).
- **Power (gate).** Plant a copy of a random run of ℓ signs from X into a random place in Y (overwrite), with
  ℓ = 4…15 and 100 plants each. Power is the share of plants with p ≤ 0.002 (Bonferroni, conservative). ℓ* is the
  smallest ℓ with power ≥ 0.80.
- **Positive controls (gate).** Hr–Qr and Hr–Pr (known copies) must reach p ≤ 0.002.
- **Negative control (gate).** Y reversed line by line (same signs, no copied order), with its own Markov null.
  Gate: 0 Holm detections and at most 3 of 25 unadjusted hits at 0.05.
- **Decision.** If any gate fails, every pair is **NOT TESTABLE**. Otherwise a pair Holm-significant is **DETECTED**
  (shared beyond Markov-1: it may be shared formula rather than copying, which is declared now). A pair not
  significant with ℓ* ≤ 10 is **NOT DETECTED**: a copied passage of ℓ* signs or more would have been seen. A pair with
  ℓ* > 10 or none is **NOT TESTABLE**.
- **Seed** 3001. Tool `tools/rr001_isolation.py` (computes gates before the observed M values). Output
  `analysis/rr001_results.json`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
