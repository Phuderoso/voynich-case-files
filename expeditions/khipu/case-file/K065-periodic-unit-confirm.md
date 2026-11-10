# K065 · Do the three new cross-site leads survive a null that keeps periodicity? (line 3)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed with the tool before any reference null, FPR, power or observed value of the new null was
computed at registered size.

**Why this cycle.** K064's cross-provenance scan (prereg `ca456e4`, results `6f7cd85`) named three new leads — **L1** KH0143·KH0591,
**L2** KH0156·KH0432, **L3** KH0377·KH0590 — and one false alarm, KH0309·KH0293, two khipus that both repeat `3 2 3 2…`. The
within-khipu run permutation breaks that periodicity, so periodic, low-information khipus look too similar to each other under
the null. K064's own "next" asked for a confirmation under a null that **keeps** periodicity, plus a literature audit.

**Disclosed before this commit.** Everything K064 published. Two smokes (output `/tmp`, sizes 2–3, `gates` mode):
1. A first design used an exact **doublet-preserving (Eulerian) shuffle** (Altschul–Erickson / Kandel et al. 1996). Its smoke
   showed a broken meter: with mostly unique values, the bigram multiset forces the sequence, so real copies survive inside the
   null (the 3-null reference maximum was 121.0, the K010 pair KH0362·KH0049). Rejected; nothing else was read.
2. The registered **P-unit** tool: N 433, F_x 89 489, weight table 20 108 / 1 558, 174 sequences contain at least one periodic unit,
   S0 20/20, G0 20/20, runs. No reference, FPR, power or observed W was read for P-unit.

## Design
Tool [`tools/k065_periodic_unit_confirm.py`](../tools/k065_periodic_unit_confirm.py) + kernel [`tools/k065_wham1.c`](../tools/k065_wham1.c)
(K064's, verbatim), `full` mode under `timeout 600`. Corpus, R5 mask, collapse, family F_x, full-corpus weights, W: K064 verbatim.

- **Null P-unit (new).** Each run-collapsed sequence is cut greedily, left to right, into units: the longest stretch with period 2
  or 3 and length ≥ two full periods is one unit (ties → smaller period); any other token is a unit by itself. Units are permuted
  uniformly and the result is collapsed again. With no periodic stretch this **is** K064's run permutation; a periodic stretch moves
  as one block.
- **Confirmation rule.** For each lead, single-step selection-adjusted p_adj = (1 + #{null F_x max W ≥ W_obs}) / (1 + R), R = 1 000
  P-unit nulls (seed 6405), i.e. the lead must beat the **maximum over all 89 489 pairs** of each null. **Holm over L1–L3 at α 0.025.**
- **Diagnostic D (registered, outside Holm):** KH0309·KH0293 under P-unit. Prediction: not significant. If it stays significant,
  the periodicity explanation in K064 is weakened and this is published.
- **Secondary (registered):** step-down max-W list under P-unit (up to 15 steps), to show which of K064's 11 survive.

**Gates (all must pass before any observed p is read):**
- **S0** unit fixture (seed 6408): 20 random sequences; units concatenate back exactly, non-periodic sequences give only singletons,
  an inserted `97 98`×4 block stays one unit.
- **G0** W fixture (K064's, seed 6404), 20/20.
- **A0** audit of K064: run-permutation null, seed 6401, R 500 on F_x must reproduce K064's critical W 25.502133284010203 and median
  20.321479515837176 (|Δ| < 1e-9).
- **G1** FPR (seed 6406, 40 P-unit nulls): share whose own maximum reaches p_adj ≤ 0.025 must be ≤ 0.10.
- **G2** power (seed 6407, 100 plants, K064 plant design: 8 distinct non-zero cords, one interior cord ±1..3, planted into a P-unit
  null corpus): **power ≥ 0.80**, else **NOT TESTABLE**.

**Verdicts per lead:** CONFIRMED (Holm), NOT CONFIRMED (gates pass, fails Holm), NOT TESTABLE (G2), EXCLUDED (S0/G0/A0/G1 fail).
A confirmed lead is a **lead for the archives** (same record copied, or a shared accounting sequence), never a reading.

**Literature audit (registered queries, run after the registration):** for each lead, web search for the two investigator numbers
together (e.g. "UR1140" "UR194"), the OKR numbers together, and the museum numbers; hit = a source that pairs the two khipus.
Outcome per lead: `found` / `not_found_in_retrieved_sources` (never "not in the literature").

Seeds 6405–6408; next free 6409.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
