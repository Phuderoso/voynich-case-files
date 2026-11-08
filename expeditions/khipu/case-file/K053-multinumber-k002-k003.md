# K053 · Do K002's D2 and K003's D5 corpus detections survive without multi-number cords?

## Pre-registration (written and committed before any gate or corpus number was computed)
- **Question (README line 8, last item).** K008 reran K001 and K004 with K007's multi-number ("R5") cords masked;
  K009 reran K005/K006. The two detector-design cycles are left. Do the published K002 corpus detections
  (frozen **D2**, 16 BH names) and K003 corpus detections (frozen **D5**, 20 BH names) survive the same mask?
  This is a **sensitivity rerun of frozen detectors**, not a redesign: Stage 1/2 selection is not rerun, and
  line 1 (D5w / the K036 F1 list) is not reopened.
- **Data.** OKR `khipu.db` @ `4039ca5` (sha256 `6079130…c4db`); level-1 pendants in `CORD_ORDINAL` order;
  duplicate-flagged records removed; cord value = sum of knot values. Universe = K002/K003's 457 khipus. A khipu is
  **testable** if it keeps ≥ 10 nonzero *unmasked* pendants, otherwise **not testable** (not lost).
- **R5 cord (K007/K008).** At least two knot clusters with a single decimal place, and those places, read in
  `knot_cluster.ORDINAL` order, are not strictly decreasing.
- **Mask (K008, structure-preserving).** An R5 pendant keeps its position but is never a sum target and never part
  of a summand block. Null N1 permutes only non-R5 values among non-R5 positions. D2 (log10-weighted adjacent sums,
  k ≤ 6) and D5 (min-p over W_2..W_12, calibrated against its own null) are otherwise exactly as frozen.
- **Corpus procedure (as K002/K003).** K = 1000 for every testable khipu; p ≤ 0.01 → fresh K = 20000 whose p
  replaces the first; p = (1 + #null ≥ obs)/(1 + K); BH-FDR q = 0.05 over all testable khipus. Seeds: **5354**
  (masked D2), **5355** (masked D5). Khipus with no R5 pendant are recomputed with the new seed (fresh null).
- **Gates (seed 5353; one shared K = 1000 null per khipu for both detectors).**
  - **G0 fixture (stop on failure):** DB hash; 3 069 R5 cords; universe = K002's 457 ids; with an empty mask the
    masked code reproduces K002's D2 statistic for all 457 and K003's per-k scores; with the real mask, R5-free
    khipus reproduce K002's D2 statistic.
  - **G1 calibration FPR:** one masked shuffle per testable khipu treated as real; rate of p ≤ 0.05. Gate ≤ 0.05
    per detector (the original rule). If G1 fails, that detector's survival and new-candidate questions are
    **not testable**. Also reported: BH flags on the calibration p's.
  - **G2 planted recovery, spec A:** on a masked shuffle of each testable khipu with ≥ 20 pendants, two targets set to
    the sum of the next 3 pendants, target and summands all non-R5 and contiguous (K002's fill rules for empty or
    small blocks). Power = rate of p ≤ 0.05. Gate ≥ 0.50 per detector (the original spec-A power was 0.63 for D2
    and 0.66 for D5; the old 0.80 bar is not used). Failing G2 does not block reporting; it marks the detector
    **underpowered**.
- **Decision rules.** A K002 name **survives** if BH-significant under masked D2; a K003 name survives if
  BH-significant under masked D5. A name that drops is **no longer established** (not excluded). A BH name not in
  the original list is a **new candidate**, reported, not claimed. The fate of K001's 10 (KH0359, KH0405, KH0491,
  KH0492, KH0503, KH0504, KH0506, KH0507, KH0513, KH0514) is reported under both detectors.
- **Same-data caveat.** A reanalysis of the same pinned corpus, not an independent replication.
- **Tool.** [`tools/k053_multinumber_k002_k003.py`](../tools/k053_multinumber_k002_k003.py) (`fixture` mode was run
  before this commit: G0 passes, 433 of 457 testable, 24 not testable, 215 khipus carry R5 pendants; no p-value).
  Output: `analysis/k053_results.json` (checkpoint `analysis/k053_checkpoint.json`).

## Results
_(to be added after the run)_
