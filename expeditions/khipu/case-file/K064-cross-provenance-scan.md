# K064 · Cross-provenance scan with the rarity-weighted, one-cord-tolerant score (line 3)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed with the tool before any reference null, FPR, power or observed value on the new family was
computed at registered size.

**Why this cycle.** K063 showed that the rarity-weighted, one-mismatch score W lifts power from 0.01 to 0.955 inside the 4 039
same-provenance pairs (F_prov). Until now, short copies *across* provenances were never readable: K012/K059 found them NOT TESTABLE with
counts. The new score may make the much larger cross-provenance family readable. This is the question K063 leaves open: are there
copies between sites (or with unprovenanced khipus) that the archive has not paired?

**Disclosed before this commit.** Everything K061–K063 published, including K063's F_prov top-10 (a different family, not reused
here). One smoke (`K064_SMOKE=4,2,2`, `gates` mode, output `/tmp`, 2 s): I read only N = 433, F_prov 4 039, **F_x 89 489**, full weight
table 20 108 tokens / 1 558 distinct values, G0 20/20, and that the code runs (A0 on 2 corpora is not comparable to its target). No
reference, FPR, power or observed W over F_x was looked at.

## Design
Tool [`tools/k064_cross_provenance_scan.py`](../tools/k064_cross_provenance_scan.py) + kernel [`tools/k064_wham1.c`](../tools/k064_wham1.c)
(K063's kernel, verbatim), `full` mode under `timeout 600`. Corpus, R5 mask, run-collapse, null (within-khipu run permutation) and W: K063 verbatim.

- **Family F_x** = all 89 489 pairs of the 433 khipus **not** in F_prov (different provenances, or one of them blank/unknown). Named from metadata only.
- **Weights, fixed in advance:** w(v) = −ln[(n_v + 1)/(n_tot + V + 1)] over the run-collapsed non-zero level-1 values of **all** 433 khipus (no lead to exclude; one table for every null, plant and the observed corpus).
- **Discovery rule:** Westfall–Young **step-down max-W** over F_x, α = 0.025, R = 500 reference nulls (seed 6401, one `SeedSequence` child per replicate; each null keeps its 40 largest pair scores, exact for step-down while < 40 pairs removed). Up to 15 steps reported; stop at the first non-significant.
- **Hypothesis H1:** at least one F_x pair is significant. Each significant pair is labelled **known** (K010's five long-match pairs) or **new**.

**Gates (in order, all must pass before the observed scan):**
- **G0** brute-force fixture (seed 6404), 20/20.
- **A0** audit of K063: K063's own weights, seed 6301, R = 1 000 on F_prov must reproduce K063's published critical W 26.62082430464733 and median 18.3558702091879 (|Δ| < 1e-9).
- **G1** FPR (seed 6402, 40 fresh nulls): share whose own F_x maximum reaches p_adj ≤ 0.025 must be ≤ 0.10.
- **G2** power (seed 6403, 100 plants; K062/K063 plant design verbatim — 8 distinct non-zero cords, one interior cord altered by ±1..3 — planted in a random F_x pair): recovered iff that pair's single-step p_adj ≤ 0.025; **power ≥ 0.80** else **NOT TESTABLE**, and no observed W over F_x is computed.

**Verdicts:** EXCLUDED (G0/A0/G1 fail), NOT TESTABLE (G2 fail), DETECTED (≥ 1 new significant pair), ONLY KNOWN PAIRS, NOT DETECTED
(silence readable for 8-cord near-copies at the measured power). A new pair is a **lead for the archives**, never a reading.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
