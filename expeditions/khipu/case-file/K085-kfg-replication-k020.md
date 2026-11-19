# K085 · KFG re-audit of K020: does the two-stage scan still confirm KH0502·KH0514? (line 9, step 15)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K085 statistic is computed on KFG data.

## Why
K020 (OKR) ran the K018 → K019 pipeline over the whole corpus with groups of ≥ 3 cords. It passed (calibrated 2/20,
all three positive controls found in both stages) and confirmed **KH0502·KH0514** (UR266·UR275, Inkawasi) in both
stages (W 123.4, V 13 over 12 matched groups, p₂ < 10⁻⁴) — a blind rediscovery of Urton & Chu's "Matches UR 275".
The Urton & Chu close match **KH0491·KH0503** passed stage 1 only (p₂ 0.36). This is the next verdict-reaching row of
the coverage table owed under line 9 (named as next in K084's journal).

## Data (KFG store of K068, `/workspace/kfg/kfg_20261111.db`)
- Pendants: KFG cords named `p<n>`, in pendant order, KFG `value` (blank = 0); R5 multi-number pendants masked to 0
  by the K073 port of K007's rule (as K020 masked R5 on OKR).
- Groups: each Excel `CordGroups` sheet (K071 parser). A khipu enters only if its groups partition p1..pn exactly
  (G1). This replaces OKR's `CLUSTER_ID` runs.
- Eligibility, leaders, weights: K020 verbatim (≥ 10 non-zero pendants; leader = first value of each group of ≥ 3
  cords, zeros dropped; weight −log₂ of the leader's corpus frequency, recomputed on KFG).

## Gates
- **G0:** OKR and KFG store sha256 as in K073; every KFG xlsx matches the store hash.
- **G1:** CordGroups partition rate ≥ 0.95 (as K071).
- **A0 (already run, OKR only, no KFG statistic):** the K020 loader rebuilt inside this tool must reproduce K020's
  2 763 leaders (606 distinct) and the five published stage-1 W scores to 10⁻⁶. **Passed** before this commit
  (`analysis/k085_a0.json`: 2 763 / 606; all five W identical).

## Pipeline and decision rule (K020 verbatim)
- Stage 1: 100 leader-shuffle null corpora → T_W = 95th percentile of the null maximum; calibrated iff ≤ 3 of 20
  held-out corpora have any pair above T_W; power from 50 planted ordered copies of 10 leaders (descriptive).
- Stage 2 for each stage-1 discovery: leader-aligned groups, LCS of non-leader cords, random-partner-group null
  R = 10 000, Bonferroni α = 0.01 / K (K = number of stage-1 discoveries).
- **Pipeline OK** iff stage 1 is calibrated and all three positive controls (KH0097·KH0586, KH0192·KH0470,
  KH0192·KH0469) pass both stages. If not, every verdict below is **NOT TESTABLE**.
- **KH0502·KH0514:** REPLICATED if confirmed in both stages; CHANGED (correction) if present and eligible but not
  confirmed in both; NOT TESTABLE if absent / ineligible / G1-failed in KFG.
- **KH0491·KH0503:** REPLICATED if stage 1 only; CHANGED otherwise (either direction), reported.
- New pairs confirmed in both stages are listed as **candidates** (KFG data), with museum numbers, and checked for
  being the same object recorded twice; no claim of novelty without a literature check.
- Seed **6464** (single generator for nulls, held-out, plants, stage 2); next free **6465**. Wall clock 600 s.

Tool: `tools/k085_kfg_k020_two_stage.py`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
