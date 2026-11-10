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

---

## Results (registered run 21:54:29–21:55:15 PT, 45.3 s, prereg `ca456e4`)
Output [`analysis/k064_results.json`](../analysis/k064_results.json), log [`analysis/k064_run.log`](../analysis/k064_run.log). Tool and kernel unchanged after the pre-registration.

**Gates: all pass.** G0 fixture 20/20. A0 audit of K063 **reproduced exactly** (critical W 26.62082430464733, median 18.3558702091879).
Reference over F_x (R 500): critical W at α 0.025 = **25.50** (median family max 20.32). G1 FPR **0/40**. G2 power **0.97** (97/100,
Wilson 95 % 0.915–0.990), so silence would have been readable for 8-cord near-copies.

**H1: DETECTED** (registered verdict). Step-down max-W found **11** significant F_x pairs (stopped at step 12, KH0240·KH0496,
p 0.036). Under the registered label (known = K010's five long-match pairs) 3 are known and 8 are "new". Ordered by W:

| # | pair (inv.) | provenances | W | K | p single | p step-down | post-hoc label (from our own earlier cycles and OKR metadata, not part of the registered rule) |
|---|---|---|---|---|---|---|---|
| 1 | KH0362·KH0049 (UR122·AS038/HP036) | Nazca · Costa Sur | 121.0 | 14 | 0.002 | 0.002 | re-finding, K010 |
| 2 | KH0128·KH0137 (UR1114·UR1123) | between Ica and Pisco · Ica | 49.5 | 10 | 0.002 | 0.002 | re-finding, K010 |
| 3 | KH0192·KH0470 (UR1175·UR233) | Pachacamac · Huacho | 43.8 | 8 | 0.002 | 0.002 | re-finding, K019 (leader method) — now confirmed at cord level |
| 4 | KH0097·KH0586 (UR1084·HP055) | blank · unknown | 42.5 | 8 | 0.002 | 0.002 | re-finding, K018/K019 |
| 5 | KH0305·KH0301 (UR068·UR064) | blank · Huaquerones | 34.9 | 10 | 0.002 | 0.002 | re-finding, K010 |
| 6 | KH0284·KH0285 (UR053B·UR053C) | blank · blank | 33.0 | 6 | 0.004 | 0.002 | same object: both OKR museum number ATE 3517 |
| 7 | KH0192·KH0469 (UR1175·UR232) | Pachacamac · Huacho | 30.2 | 6 | 0.006 | 0.002 | re-finding, K019 |
| 8 | KH0143·KH0591 (AS128·QU03) | Nazca (Berlin VA63042(B)) · blank (Dallas B378) | 29.7 | 4 | 0.006 | 0.002 | **NEW lead** (`226 115 124 200|357 161`) |
| 9 | KH0156·KH0432 (UR1140·UR194) | Nazca (Berlin VA16636) · Ica (Berlin 47082) | 28.2 | 6 | 0.010 | 0.004 | **NEW lead** (`53 8 11 19|17 25 24 12`) |
| 10 | KH0309·KH0293 (UR072·UR057) | Huaquerones · Atarco | 26.4 | 9 | 0.014 | 0.006 | **null limitation**: two-value periodic `3 2 3 2…` in both; the run permutation breaks within-khipu periodicity, so this is not evidence of copying |
| 11 | KH0377·KH0590 (UR137·QU02) | Chancay (Lowe 57.172.002) · blank (Dallas B388) | 25.5 | 6 | 0.032 | 0.020 | **NEW lead** (`22 24|25 28 12 14 8 1`), weakest |

**Reading.** The scan is calibrated and powered, and it re-finds every cross-provenance correspondence our earlier, different
methods named (K010 long matches; K018/K019 leaders), which is a strong external check on the score. It adds **three new leads**
(rows 8, 9, 11) that no earlier cycle named. They are **leads for the archives**, not readings, and two caveats are on the record:
(i) row 10 shows the run-permutation null under-represents periodic, low-information sequences, so a confirmation of the new leads
must condition on information content (as K061 did) — none of the three is periodic (4–6 distinct matched values each), but the
check is owed; (ii) the "new" label is post hoc against our own logs; literature has not yet been searched.

**Next (K065).** Pre-registered literature audit of the three new leads (Khipu Field Guide pages, Urton/Ascher databooks, the
Dallas QU-series notes), then a held-out, information-conditioned confirmation (null that preserves within-khipu periodicity, e.g.
block-bootstrap of runs, with its own plants) for those not found in the literature.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
