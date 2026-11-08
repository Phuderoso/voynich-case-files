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
One run, 2026-11-08 ~10:39–10:40 PT (America/Vancouver), 55.9 s, no crash, no amendment to the prereg.
Output: [`analysis/k053_results.json`](../analysis/k053_results.json), log [`analysis/k053_run.log`](../analysis/k053_run.log).

**G0 fixture: pass.** sha256 matches; 3 069 R5 cords (K007/K008 count); universe = K002's 457 ids; empty mask
reproduces K002's D2 statistic 457/457 and K003's per-k scores 457/457; with the real mask the 242 R5-free khipus
reproduce K002's D2 statistic 242/242. 215 khipus carry R5 pendants; **433 testable, 24 not testable** (the same
24 as K008).

**Gates (seed 5353, K = 1000): both detectors pass.**

| | G1 FPR at p ≤ 0.05 (n = 433) | BH flags on calibration | G2 spec-A power at p ≤ 0.05 (n = 374) |
|---|---|---|---|
| masked D2 | **0.028** (≤ 0.05 ✓) | 0 | **0.60** (≥ 0.50 ✓; original 0.63) |
| masked D5 | **0.042** (≤ 0.05 ✓) | 0 | **0.66** (≥ 0.50 ✓; original 0.66) |

Two khipus with ≥ 20 pendants (KH0415, KH0431) have no contiguous non-R5 4-window and were skipped for the plant.

**Corpus (BH q = 0.05 over 433).** Masked D2 (seed 5354): 19 khipus at stage-1 p ≤ 0.01, **14 BH** (bar at rank 14
= 0.00162). Masked D5 (seed 5355): 29 at p ≤ 0.01, **19 BH** (bar at rank 19 = 0.00219). **No new candidate** under
either detector: every masked BH name was already on the original list.

| Khipu | R5 pendants | D2 stat orig → masked | D2 p orig → masked | D2 fate | D5 p orig → masked | D5 fate |
|---|---|---|---|---|---|---|
| KH0027 AS026A | 0 | 3.74 → 3.74 | 0.00085 → 0.0011 | survives | 0.00005 → 0.00085 | survives |
| KH0068 UR1057 | 0 | 3.62 → 3.62 | 0.0011 → 0.0010 | survives | (not in K003 list) | |
| KH0143 AS128 | 0 | 6.20 → 6.20 | (not in K002 list) | | 0.00005 → 0.00055 | survives |
| KH0168 UR1152 | 0 | 6.93 → 6.93 | 0.0016 → 0.0019 | **no longer established** ¹ | 0.0012 → 0.0013 | survives |
| KH0218 AS200 | 0 | 0 → 0 | (not in K002 list) | | 0.00005 → 0.00005 | survives |
| KH0359 UR119 | 5 | 19.6 → 17.7 | 0.00005 → 0.00005 | survives | 0.00005 → 0.00005 | survives |
| KH0385 UR145 | 0 | 5.37 → 5.37 | 0.0012 → 0.0011 | survives | 0.00005 → 0.00005 | survives |
| KH0395 UR155 | 0 | 5.56 → 5.56 | (not in K002 list) | | 0.0014 → 0.0012 | survives |
| KH0405 UR166 | 0 | 9.74 → 9.74 | 0.00005 → 0.00005 | survives | 0.00005 → 0.00005 | survives |
| KH0424 UR186 | 7 | 5.76 → 5.76 | (not in K002 list) | | 0.0015 → 0.00005 | survives |
| KH0428 UR190 | 2 | 26.0 → 26.0 | (not in K002 list) | | 0.00005 → 0.00005 | survives |
| KH0447 UR209 | 3 | 5.70 → 5.70 | 0.00005 → 0.00015 | survives | 0.00005 → 0.00055 | survives |
| KH0478 UR242 | 0 | 4.73 → 4.73 | (not in K002 list) | | 0.00005 → 0.00005 | survives |
| KH0491 UR255 | 12 | 20.3 → 8.57 | 0.00005 → 0.00075 | survives | 0.00005 → 0.0025 | **no longer established** |
| KH0492 UR256 | 13 | 20.9 → 13.4 | 0.00005 → 0.00005 | survives | 0.00005 → 0.00005 | survives |
| KH0502 UR266 | 10 | 6.81 → 3.56 | 0.00025 → 0.0051 | **no longer established** | (not in K003 list) | |
| KH0503 UR267A | 14 | 33.4 → 21.8 | 0.00005 → 0.00005 | survives | 0.00005 → 0.00005 | survives |
| KH0504 UR267B | 17 | 34.0 → 23.5 | 0.00005 → 0.00005 | survives | 0.00005 → 0.00005 | survives |
| KH0506 UR269 | 21 | 54.6 → 48.4 | 0.00005 → 0.00005 | survives | 0.00005 → 0.00005 | survives |
| KH0507 UR270 | 22 | 11.3 → 9.20 | 0.00030 → 0.00080 | survives | 0.00025 → 0.00080 | survives |
| KH0513 UR274B | 1 | 9.30 → 9.30 | 0.00010 → 0.00015 | survives | 0.0013 → 0.0014 | survives |
| KH0514 UR275 | 13 | 33.2 → 23.1 | 0.00005 → 0.00005 | survives | 0.00005 → 0.00005 | survives |

¹ KH0168 has **no R5 pendant**: its data and D2 statistic are unchanged. Its p moved 0.0016 → 0.0019 by fresh
Monte-Carlo draws (K = 20000) and now sits just above the BH bar (0.00162 at rank 14, 0.00173 at rank 15). By the
pre-registered rule it is "no longer established" under masked D2, but the cause is a BH-boundary case, not
multi-number cords, and it stays BH-significant under masked D5. I report it as is and don't change the rule
after the fact.

**K002 (D2, 16 names): 14 survive, 2 no longer established (KH0502 UR266 — a real masking effect, statistic
halved by 10 R5 pendants; KH0168 UR1152 — boundary case, see ¹), 0 not testable.**
**K003 (D5, 20 names): 19 survive, 1 no longer established (KH0491 UR255, 12 R5 pendants, statistic 20.3 → 8.6),
0 not testable.** No new BH candidate under either detector.

**K001's 10.** Under masked D2 all 10 survive; under masked D5, 9 of 10 survive (KH0491 drops). Compare K008 (K001's
own detector, masked): KH0491 and KH0507 lost there. So KH0507 holds under the log-weighted detectors, and KH0491 is
the one name that is weakened under two of three masked detectors (K001, D5) and survives one (D2, p 0.00075).

## Verdict
- Gates pass for both detectors (FPR 0.028 / 0.042; spec-A power 0.60 / 0.66, close to the unmasked originals).
- **The K002 and K003 corpus detections are robust to the multi-number mask**: 14/16 and 19/20 survive, nothing
  becomes not testable, and no new candidate appears. The losses are KH0502 UR266 (D2), KH0491 UR255 (D5) and the
  boundary case KH0168 UR1152 (D2, R5-free).
- Same-data sensitivity, not an independent replication; no new structure is claimed.
- Line 8 can close: K001, K002, K003, K004, K005 and K006 have all been rerun with R5 cords masked. Not covered: the
  later adopted K036 F1 / D5w list (line 1) has not itself been R5-masked; that's a possible later step, not this cycle.
