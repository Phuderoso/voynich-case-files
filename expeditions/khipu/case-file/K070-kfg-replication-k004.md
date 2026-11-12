# K070 · KFG re-audit, step 2: do pendants still record their own subsidiaries' sum (K004) on Khipu Field Guide data?

*Caderno de campo, 12 Nov 2026, ~01:55 PT.* Second stop on the KFG re-audit trail (README line 9). K004 found, on the
historical OKR, that pendants equal the sum of their own subsidiaries more often than chance, concentrated in KH0349
(UR113, Göteborg). Its non-UR113 signal (p 0.019, later 0.006 under the K008 mask, same data) was left owing a
**held-out replication** (line 7). The KFG has 84 khipus that are not in the OKR, so that replication is now possible.

## Pre-registration (written and committed before any K070 count on real data)
- **Data.** KFG store `/workspace/kfg/kfg_20261111.db` (K068 loader; 695 khipus, KFG Excel release recorded in K068),
  G0: every per-khipu Excel file's sha256 must match the store. OKR `data/khipu.db` only for the A0 audit and for the
  held-out split. Value = KFG `Value` column (integer; blank → 0).
- **Hierarchy from KFG cord names.** Level-1 pendant: `^p(\d+)$`. Direct level-2 subsidiary: `^p(\d+)s(\d+)$`, parent
  `p\1` of the same khipu. Deeper levels and `p#m#` cords are not used (same as K004, which used levels 1–2 only).
- **Definitions verbatim from K004.** Eligible parent: level-1 pendant with value ≥ 10 and ≥ 2 direct subsidiaries.
  Hit: parent value = sum of its direct subsidiaries, with ≥ 2 of them nonzero. N_a: permute subsidiary values among
  all level-2 cords of the khipu. N_b: permute parent values among the khipu's eligible parents.
- **T1 corpus test** (all KFG khipus with ≥ 1 eligible parent): total hits vs the sum of within-khipu nulls, K = 10000,
  N_a primary, N_b secondary.
- **T2 per khipu** (≥ 3 eligible parents): N_a K = 2000, fresh K = 20000 when p ≤ 0.01; N_b K = 2000; BH q = 0.05.
  Calibration (one shuffle treated as real; FPR at 0.05 must be ≤ 0.05) and planted control (two eligible parents set
  to their subsidiaries' sum in a shuffled copy) exactly as K004.
- **T3 without KH0349** (post hoc in K004, pre-registered here): T1 under N_a with KH0349 removed, K = 10000.
- **T4 held-out replication of the non-UR113 signal** (line 7): T1 under N_a restricted to KFG khipus whose name is
  **not** an OKR `OKR_NUM` (84 khipus; KH0349 is not among them), K = 10000. **Power for T4:** 200 replicates of a
  shuffled held-out corpus with m planted hits, m = round(e × n_eligible_heldout), e = the OKR non-UR113 excess rate
  (12 − 5.97) / (1315 − 82) from K004's sensitivity run; each replicate tested with K = 1000; power = share with p ≤ 0.05.
- **Gates.** G0 hash mismatches = 0. G2 per-khipu calibration FPR ≤ 0.05. A0: the published K004 script, re-run on the
  OKR, must reproduce 25 hits / null mean 7.14 (otherwise the comparison is void and reported as such).
- **Decision rules.** R1 corpus: T1 N_a p ≤ 0.01 → corpus signal REPLICATED, else NOT REPLICATED. R2 UR113: KH0349
  BH-significant in T2 → REPLICATED; p ≤ 0.05 but not BH → WEAKENED; else NOT REPLICATED. Headline: both replicated →
  **REPLICATED**; one → **CHANGED**; neither → **NOT REPLICATED**. Per-khipu silence is a real negative only where planted
  recovery ≥ 0.8. R3 (T4): if power < 0.5 → **NOT TESTABLE (data-limited)**; else p ≤ 0.01 → **established on held-out
  data**, p ≤ 0.05 → **suggestive**, else **not replicated** (powered negative). T3 is descriptive (same-data).
- **Descriptive.** Overlap of the T2 BH set with K069's 15 KFG adjacent-sum names (K004 found 0 overlap with K003).
- **Seed** 6418 (next free 6419). Tool before run: `tools/k070_kfg_k004_replication.py`. No smoke run on real data
  beyond a parse count of cords (number of eligible parents is printed only in the registered run).

## Results
Registered run 12 Nov 2026, 01:52:03–01:53:04 PT (61 s; prereg commit `1577d09` made at 01:52, just before; the "~01:55" in the
header was my estimate when writing). Log `analysis/k070_results.json`. No smoke on real counts.

**Gates.** G0: 0 hash mismatches. G2: per-khipu calibration FPR **0.025** (≤ 0.05, pass). **A0:** the untouched K004 tool, re-run on
the OKR, reproduced its published corpus numbers exactly (197 khipus, 1315 eligible parents, 25 hits, null mean 7.1412, p 0.0001).

| Test | Khipus | Eligible parents | Hits | Null mean (max) | p |
|---|---|---|---|---|---|
| T1 corpus, N_a | 238 | 1503 | **29** | 8.45 (22) | **0.0001** (floor) |
| T1 corpus, N_b | 238 | 1503 | **29** | 10.14 (23) | **0.0001** (floor) |
| T3 without KH0349, N_a | 237 | 1421 | 16 | 7.39 (20) | **0.0035** |
| T4 held-out (KFG-only), N_a | 34 | 187 | 2 | 1.52 (8) | 0.45 |

**T2 per khipu** (118 khipus with ≥ 3 eligible parents): planted recovery **0.97** (0.95–1.00 in every size band), so silence is a real
negative. Two khipus pass BH:
- **KH0349 (UR113, Göteborg): 13 of 82 eligible pendants**, p 0.00005 (N_a floor), N_b 0.0005, exactly as on the OKR.
- **KH0276 (UR046, Museo Larco ML600134): 2 of 9**, p 0.00065 (N_b 0.013). This is a **data change**, not a method change: on the OKR
  it had 4 eligible parents and 0 hits (p 1.0). The KFG changelog (3 Dec 2025) says the OKR had no information on its subsidiaries
  ("just that they exist") nor on cords p12 onwards, and that these were added from museum images. The two hits are 378 = 278 + 100
  and 340 = 36 + 289 + 15. Two hits on image-reconstructed cords are a **lead**, not an established habit.

**Decisions (as registered).** R1 corpus: p 0.0001 ≤ 0.01 → **REPLICATED**. R2 UR113: BH-significant → **REPLICATED**.
**Headline: K004 REPLICATED on KFG.** R3 (held-out replication of the non-UR113 signal): planted power **0.075** at the expected one
excess hit (rate 0.0049 × 187 parents), far below 0.5 → **NOT TESTABLE (data-limited)**. The 84 KFG-only khipus are too few (only
34 have an eligible parent) to replicate a signal that weak. Line 7's held-out replication therefore stays owed and needs new khipus,
not new statistics. T3 (same data as the OKR, plus KFG corrections) sits at p 0.0035, now meeting the 0.01 rule, but it is a re-analysis
and not counted as replication. Overlap of the T2 BH set with K069's 15 adjacent-sum names: **0**, again (K004 found 0 with K003).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
