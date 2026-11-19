# K086 · A leak-free stage 1 for K020 on KFG: step-down max-T (line 9, follow-up to K085)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K086 statistic is computed (only A0, an OKR rebuild, was run).

## Why
K085 ended **NOT TESTABLE (pipeline gate)**: the positive control KH0192·KH0469 scored W 81.2 against T_W 82.6. The
post-hoc diagnosis (K085 case file) showed why: the leader-order shuffle keeps each khipu's value multiset, so the
strong *true* pairs (KH0097·KH0586, KH0502·KH0514, KH0491·KH0503) keep W 74–94 after shuffling and set the upper tail
of the null maximum. A single-step max-T bar is therefore raised by the very correspondences it is meant to find.

The textbook remedy is not a new statistic but the **step-down max-T** (Westfall & Young 1993; Romano & Wolf 2005):
reject pairs above the 95th percentile of the null maximum; then recompute the maximum over the pairs **not yet
rejected**, reject again, and repeat until nothing new crosses. It controls the family-wise error at 0.05 under subset
pivotality, which holds here: each pair's null is the within-khipu shuffle of its own two khipus, whose distribution
does not depend on whether any other pair is a true correspondence. Step 1 is exactly K020's single-step rule, so the
procedure can only add discoveries, never remove them.

This is a **new design**: it cannot rescue K085 after the fact. K085's verdict stays as published; K086 is a separate
test of the same question with the leak removed.

## Data and fixed parts (K085 verbatim)
KFG store `/workspace/kfg/kfg_20261111.db` (K068), pendants `p<n>`, R5 masked (K073 port), Excel CordGroups (K071
parser), eligibility, leaders and weights exactly as K085; gates **G0** (hashes), **G1** (partition ≥ 0.95) and **A0**
(OKR rebuild: 2 763 leaders, 606 distinct, K020's five W to 10⁻⁶; **passed** before this commit,
`analysis/k086_a0.json`). Stage 2 verbatim (leader-aligned groups, LCS of non-leaders, R = 10 000, Bonferroni
α = 0.01 / K, K = number of stage-1 discoveries).

## What changes: stage 1
- 100 leader-shuffle null corpora give the null W of **every** pair (kept in memory).
- Discoveries = step-down rejections at FWER 0.05 (95th percentile of the null maximum over still-active pairs, iterated).
- **Calibration:** 20 held-out shuffle corpora, each put through the same step-down against the 100-corpus reference;
  calibrated iff ≤ 3 of 20 have any discovery (K020's bar).
- **Power (descriptive):** 50 planted ordered copies of 10 leaders into the real corpus; found if the planted pair is
  rejected by the step-down (single-step count printed beside it).

## Decision rule
- **Pipeline OK** iff calibrated and all three positive controls (KH0097·KH0586, KH0192·KH0470, KH0192·KH0469) pass
  both stages. Otherwise every verdict is **NOT TESTABLE**.
- **KH0502·KH0514:** **CONFIRMED** (K020's finding replicated on KFG under a leak-free stage 1) if it passes both
  stages; **NOT CONFIRMED** (a correction to the K020 row) if present, eligible and not passing both; NOT TESTABLE if
  absent or ineligible.
- KH0491·KH0503 reported as stage 1 only / both / not in stage 1 (no claim either way; it is Urton & Chu's "close match").
- Any other pair confirmed in both stages is a **candidate** with museum numbers; no novelty claim without a
  literature check, and same-object duplicates are checked first.
- **OKR arm (descriptive only, seed 6467):** the same step-down on the OKR corpus, to show what K020 would have found
  with this stage 1. No verdict attaches to it.
- Seeds **6466** (KFG: nulls, held-out, plants, stage 2 in that order) and **6467** (OKR arm); next free **6468**.
  Wall clock 600 s under `timeout 600`.

Tool: `tools/k086_kfg_k020_stepdown.py` (K085 tool with stage 1 replaced; committed with this file).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
