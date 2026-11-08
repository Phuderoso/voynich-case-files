# K054 · Do K036's F1 / D5w reference-list detections survive without multi-number cords?

## Pre-registration (written and committed before any gate or corpus number was computed)
- **Question (README line 1, the optional step named after K053 closed line 8).** K053 reran the frozen K002 (D2)
  and K003 (D5) corpus scans with K007's multi-number ("R5") cords masked. The later adopted line-1 reference list
  is K036's fixed-K = 10 000 F1 scan (D5w, pooled exchangeable min-p, BH q = 0.05 over pop = 378, 14 names). Do
  those 14 names survive the same K008 mask? Does any new BH name appear? This is a **sensitivity rerun of a
  frozen detector**, not a redesign: D5w, the pooled min-p, the fixed K = 10 000 budget and the F1 family are not
  reopened, and no new holdout is invented.
- **Data.** OKR `khipu.db` @ `4039ca5` (sha256 `6079130…c4db`); level-1 pendants in `CORD_ORDINAL` order;
  duplicate-flagged records removed; cord value = sum of knot values; groups = runs of consecutive pendants
  sharing `CLUSTER_ID` (as K031–K036). Eligible = ≥ 10 nonzero pendants (457). F1 universe = pop = ≥ 2 groups of
  size ≥ 4 (378), identical to K036. A pop khipu is **testable** if it keeps ≥ 10 nonzero *unmasked* pendants,
  otherwise **not testable** (not lost). BH is over the testable subset of that same F1 family (not over S0, and
  not over a redesigned universe).
- **R5 cord (K007/K008).** At least two knot clusters with a single decimal place, and those places, read in
  `knot_cluster.ORDINAL` order, are not strictly decreasing.
- **Mask (K008, structure-preserving).** An R5 pendant keeps its position but is never a sum target and never part
  of a summand block. Null N1 permutes only non-R5 values among non-R5 positions; group ids stay put (the same
  layout K036 kept). D5w (per-k log10-weighted within-group exact-sum hits, k = 2..12) and the pooled
  exchangeable min-p (K033/K036: stack observed + K null score-rows, live columns only,
  p = (# rows whose min-p ≤ observed min-p) / (K+1)) are otherwise exactly as frozen, at **fixed K = 10 000** (no
  adaptive cut).
- **Corpus procedure (as K036 F1, with the mask).** Fixed K = 10 000 for every testable khipu; BH-FDR q = 0.05
  over all testable khipus. Seed: **5455**. Khipus with no R5 pendant are recomputed with the new seed (fresh
  null).
- **Gates (seed 5454; K = 10 000, the frozen detector's own budget).**
  - **G0 fixture (stop on failure):** DB hash; 3 069 R5 cords; eligible = 457 and pop = K036's 378 ids; published
    K036 F1 list loads as the 14 reference names; with an empty mask the masked code reproduces K036's unmasked
    D5w scores for every eligible khipu; with the real mask, R5-free eligible khipus reproduce those scores.
  - **G1 calibration FPR:** one masked shuffle per testable khipu treated as real; rate of p ≤ 0.05. Gate ≤ 0.05
    (K053 G1 and K036's α = 0.05 FPR; a single-corpus rate cap, not a looser binomial). If G1 fails, the survival
    and new-candidate questions are **not testable**. Also reported: BH flags on the calibration p's.
  - **G2 planted recovery at corpus_m\* = 6 (K039; K036 large m\* = 6):** on a masked shuffle of each testable
    khipu, six within-group exact-sum windows are inserted with K036's `plant_within_m` fill rules (A_within /
    B_within with probability ½), restricted so target and summands are all non-R5 and contiguous inside one
    group (a block the masked detector can see). Khipus that cannot place all six are skipped (reported). Power =
    rate of p ≤ 0.05 (K053 G2 metric). Gate ≥ 0.50, evaluated only if n_planted ≥ 30 (K036's n ≥ 30 rule). The
    unmasked K036 large p ≤ 0.05 rate at m = 6 was 0.9516 and K039's corpus BH-level power was 0.7056; 0.50 is
    the adopted bar, not a lowered one. Failing G2 does not block reporting; it marks the detector
    **underpowered**.
- **Decision rules.** A K036 F1 name **survives** if BH-significant under masked D5w. A name that drops is **no
  longer established** (not excluded). A BH name not in the original 14 is a **new candidate**, reported, not
  claimed.
- **Seeds.** 5454 (gates), 5455 (corpus). 5456 is unused (one frozen detector, two phases). Distinct from K053
  (5353–5355) and from K036 (3630–3632).
- **Same-data caveat.** A reanalysis of the same pinned corpus, not an independent replication.
- **Tool.** [`tools/k054_multinumber_k036_f1.py`](../tools/k054_multinumber_k036_f1.py) (`fixture` mode was run
  before this commit: G0 passes, 365 of 378 pop testable, 13 not testable, 186 pop khipus carry R5 pendants;
  empty-mask D5w scores reproduce 457/457 and R5-free scores reproduce 242/242; no p-value).
  Output: `analysis/k054_results.json` (checkpoint `analysis/k054_checkpoint.json`, left untracked).

## Results
One run, 2026-11-08 ~11:24–11:26 PT (America/Vancouver), 99.1 s, no crash, no amendment to the prereg.
Output: [`analysis/k054_results.json`](../analysis/k054_results.json), log [`analysis/k054_run.log`](../analysis/k054_run.log).

**G0 fixture: pass.** sha256 matches; 3 069 R5 cords (K007/K008 count); eligible = 457 and pop = K036's 378 ids;
published F1 list loads as the 14 reference names; empty mask reproduces K036's unmasked D5w scores 457/457; with
the real mask the 242 R5-free eligible khipus reproduce those scores 242/242. 186 of 378 pop khipus carry R5
pendants; **365 testable, 13 not testable** (none of the 14): KH0001, KH0032, KH0089, KH0190, KH0227, KH0281,
KH0410, KH0522, KH0551, KH0564, KH0572, KH0585, KH0619.

**Gates (seed 5454, K = 10 000): pass.**

| | G1 FPR at p ≤ 0.05 (n = 365) | BH flags on calibration | G2 m = 6 power at p ≤ 0.05 (n = 346) |
|---|---|---|---|
| masked D5w / F1 | **0.0493** (18/365, ≤ 0.05 ✓) | 0 | **0.954** (330/346, ≥ 0.50 ✓; unmasked K036 large was 0.9516) |

Nineteen testable khipus could not place six non-R5 within-group windows and were skipped for the plant
(KH0050, KH0052, KH0071, KH0090, KH0129, KH0160, KH0186, KH0194, KH0195, KH0219, KH0221, KH0243, KH0405,
KH0411, KH0431, KH0443, KH0485, KH0491, KH0510). G2 remains evaluable (346 ≥ 30).

**Corpus (BH q = 0.05 over 365).** Masked F1 (seed 5455, fixed K = 10 000): **13 BH** (bar at rank 13 = 0.00178).
**No new candidate**: every masked BH name was already on the original 14.

| Khipu | R5 pendants | D5w stat orig → masked | p orig → masked | Fate |
|---|---|---|---|---|
| KH0322 UR086 | 0 | 4.68 → 4.68 | 0.00070 → 0.00060 | survives |
| KH0395 UR155 | 0 | 8.16 → 8.16 | 0.00110 → 0.00060 | survives |
| KH0420 UR182 | 3 | 2.07 → 2.07 | 0.00140 → 0.00090 | survives |
| KH0428 UR190 | 2 | 32.71 → 32.71 | 0.00100 → 0.00110 | survives |
| KH0478 UR242 | 0 | 12.66 → 12.66 | 0.00110 → 0.00110 | survives |
| KH0491 UR255 | 12 | 20.33 → 8.57 | 0.00010 → 0.00020 | survives |
| KH0492 UR256 | 13 | 23.63 → 16.15 | 0.00070 → 0.00100 | survives |
| KH0502 UR266 | 10 | 6.81 → 3.56 | 0.00090 → 0.00070 | survives |
| KH0504 UR267B | 17 | 34.01 → 23.53 | 0.00040 → 0.00050 | survives |
| KH0506 UR269 | 21 | 47.82 → 41.64 | 0.00040 → 0.00040 | survives |
| KH0507 UR270 | 22 | 11.32 → 9.20 | 0.00060 → 0.00060 | survives |
| KH0511 UR273B | 3 | 3.20 → 3.20 | 0.00160 → 0.00210 | **no longer established** ¹ |
| KH0513 UR274B | 1 | 6.26 → 6.26 | 0.00020 → 0.00050 | survives |
| KH0514 UR275 | 13 | 33.24 → 23.15 | 0.00030 → 0.00040 | survives |

¹ KH0511's D5w statistic is **unchanged** (3.20 → 3.20): its three R5 pendants are not part of the within-group
hits the detector sees. Fresh Monte-Carlo draws (fixed K = 10 000) moved p from 0.00160 (cnt 16) to 0.00210
(cnt 21), just above the BH bar (0.00178 at rank 13; even the rank-14 bar would be 0.00192). By the
pre-registered rule it is "no longer established", but the cause is a BH-boundary case, not a masking cut of the
signal. K037 had already noted that this name rests on a single 3-cord window (LOO → 0); that holdout is a
different test and was not rerun. I report the drop as the rule says and don't change the rule after the fact.

**K036 F1 (14 names): 13 survive, 1 no longer established (KH0511 UR273B — boundary case, see ¹), 0 not
testable.** No new BH candidate.

The two names K053 lost under other detectors both **survive** here, even though the mask cuts their scores the
same way: KH0502 UR266 (stat 6.81 → 3.56; lost under masked D2) and KH0491 UR255 (stat 20.33 → 8.57; lost under
masked D5). Under within-group D5w the remaining signal still clears the BH bar. Several other Inkawasi records
also drop in score but stay significant (KH0492, KH0504, KH0506, KH0507, KH0514). Names whose score is unchanged
are either R5-free (KH0322, KH0395, KH0478) or carry R5 pendants that are not in the D5w hits (KH0420, KH0428,
KH0511, KH0513).

## Verdict
- Gates pass (FPR 0.0493; m = 6 planted recovery 0.954, matching the unmasked K036 large p ≤ 0.05 rate).
- **The K036 F1 / D5w reference list is robust to the multi-number mask**: 13 of 14 survive, nothing on the list
  becomes not testable, and no new candidate appears. The one loss (KH0511 UR273B) is a BH-boundary Monte-Carlo
  move with an unchanged statistic, not a masking cut.
- Same-data sensitivity, not an independent replication; no new structure is claimed.
- The optional line-1 step named after K053 is done. Line 1's power fork stays closed (K039); this cycle does
  not reopen it.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
