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
_(to be added after the run)_
