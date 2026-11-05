# K035 · BH-level power by planted-sum count m, and size-stratified BH (README line 1)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Why
K033 calibrated the corpus scan (pooled exchangeable min-p, BH gate 0/5) but left **silence not testable**: BH-level
D5w power on within-group plants was 0.16–0.36 (< 0.5) in every stratum. K034 closed the confirmation fork. Line 1's
next step is to raise BH-level power, or find out at what effect size silence becomes readable.

Design-stage note (stated before running, from K033's *published* power rows, not new data): of K033's within-plants,
only 12–17 % reached p ≤ 0.0005 and 25–35 % p ≤ 0.0016 (≈ the BH cut for one extra hit in F1 with 11 real hits).
The BH cut, not Monte Carlo resolution (floor 1/10 001), is the bottleneck. K033's within plants each contain
**m = 2** exact-sum windows (`for _ in range(2)` in `plant_within`). Two levers follow, and this cycle tests both,
with one primary:

- **Primary — power curve by m.** Plant m ∈ {1, 2, 3, 4} independent within-group exact-sum windows per permuted copy
  and measure BH-level power in the unchanged F1 family. This does not make the tool stronger; it finds the
  **minimum detectable effect**: the smallest m at which a silent khipu becomes a readable negative.
- **Secondary — size-stratified BH.** BH at q = 0.05 separately inside small / mid / large (and S0), instead of one BH
  over pop. Under independence, separate-class BH keeps the overall FDR ≤ q; we still gate it empirically.

## Data and strata (fixed; identical to K031–K034)
OKR `khipu.db` @ `4039ca5` (SHA-256 `60791303…`), level-1 pendants, `DUPLICATE_FLAG` dropped, ≥ 10 nonzero pendants
(457). Groups = runs of consecutive pendants sharing `CLUSTER_ID`. pop = ≥ 2 groups of size ≥ 4 (378); thirds by
pendant count (small / mid / large, 126 each); S0 = 79.

## Detector and p (unchanged from K033)
D5w scoring, within-khipu permutation null, pooled exchangeable min-p, adaptive Monte Carlo (K₀ 1 000 → 10 000 if
p ≤ 0.01). Code copied verbatim from `tools/k033_pooled_minp_rescan.py`; tool `tools/k035_bh_power_multiplant.py`.

## Families (q = 0.05)
- **F1 (primary):** D5w BH over pop (378), as K033.
- **F1-strat (secondary):** D5w BH within each of small, mid, large (126 each); S0 BH reported descriptively.

## Plants (seed 3532)
For each eligible khipu and each m ∈ {1,2,3,4}: a fresh within-khipu permutation, then m within-group exact-sum
windows inserted with K033's `_fill`; each window's spec is A_within (k = 3, right) or B_within (k 2–10, either side)
with probability ½ (K033's pooled "within" mixed the two equally). Plants may overlap, as in K033. BH-level power =
the plant's pooled p inserted in place of that khipu's real p in the real family (F1 or its stratum), as K033.

## Calibration (seeds 35310–35314)
Five structure-preserving null corpora (each khipu replaced by a within-khipu permutation, groups kept).
- FPR gate (α 0.05) per stratum and pop: exact one-sided binomial P(X ≥ x | n, 0.05) ≥ 0.05.
- BH gate per family (F1, strat_small, strat_mid, strat_large, strat_S0, F1-strat union): at most 1 of 5 null corpora
  with any discovery.

## Real scan (seed 3530)
Re-run of K033's real scan with a fresh Monte Carlo seed, needed as the background family for insertion; F1 hits
are reported (reproducibility check vs K033's 11), not a new discovery claim.

## Decision rules (written before any run)
1. **Excluded** if F1's BH gate fails or any pop-stratum FPR gate fails.
2. For s ∈ {small, mid, large}: m*_s = smallest m with BH-level F1 power ≥ 0.5 (n ≥ 30 plants).
   - If some m*_s ≤ 2 → **power raised: silence testable at K033 strength** in that stratum.
   - Else if some m*_s ∈ {3, 4} → **silence testable only against stronger effects**: a silent khipu in s is a
     readable negative against "≥ m*_s planted within-group sums", not against K033's m = 2.
   - Else → **not improved**.
3. **Stratified BH adopted** for line 1 iff all three stratum BH gates pass, its m = 2 power is not lower than F1's
   by > 0.03 in any stratum, and is higher by ≥ 0.05 in at least one. m*_s under stratified BH is reported too; if
   adopted, the silence reading uses the stratified m*.
4. Wall clock: stop power at 560 s and report how many khipus were reached; publish partial.
5. Negatives published.

## Seeds
scan 3530, nulls 35310–35314, power 3532 (distinct from K031–K034: 3130–3433).

## No claims
A BH hit means "more within-group adjacent exact sums than chance in this khipu under D5w"; a readable negative means
"no excess as large as m* planted sums", never "no arithmetic". No decipherment is claimed.

## Results

Run 2026-11-05 ~12:04–12:10 PT (America/Vancouver), `timeout 600 python3 tools/k035_bh_power_multiplant.py khipu.db`
(**346.6 s**, exit 0; all 457 khipus reached in every stage, no wall cap). Output:
[`analysis/k035_results.json`](../analysis/k035_results.json). Prereg + tool committed first as `2dc09aa`.

### 1. Calibration — all gates pass
| Stratum | n (5 corpora) | D5w FPR | binomial P(≥x) |
|---|---|---|---|
| S0 | 395 | 0.030 | 0.98 |
| small | 630 | 0.038 | 0.93 |
| mid | 630 | 0.030 | 0.99 |
| large | 630 | 0.054 | 0.35 |
| pop | 1 890 | 0.041 | 0.97 |

BH discoveries per null corpus: **F1 0/0/0/0/0; strat_small, strat_mid, strat_large, strat_S0 and the stratified
union all 0 of 5.** Both partitions are calibrated at the BH level.

### 2. Primary — BH-level F1 power by planted-sum count m
| Stratum | m = 1 | m = 2 | m = 3 | m = 4 | m* (≥ 0.5) |
|---|---|---|---|---|---|
| small (n ≈ 116–120) | 0.10 | 0.28 | 0.49 | **0.59** | **4** |
| mid (n ≈ 121–123) | 0.04 | 0.19 | **0.50** | 0.49 | **3** (fragile) |
| large (n ≈ 124–125) | 0.06 | 0.18 | 0.30 | 0.38 | none |
| pop | 0.07 | 0.22 | 0.43 | 0.48 | — |
| S0 (stratum BH, descriptive) | 0.04 | 0.12 | 0.16 | 0.38 | — |

Per-plant p ≤ 0.05 (not BH) at m = 2: small 0.76, mid 0.66, large 0.52. m = 2 reproduces K033's BH-level range
(0.18–0.28 vs 0.26–0.36; K033 also counted pure A/B specs, so not identical).

Mid's m* = 3 rests on 0.504 (61/121; binomial SE ≈ 0.045), and m = 4 gives 0.488: the curve is flat at the bar
between m = 3 and 4. By the pre-registered rule mid is **readable at m* = 3**, but the margin is within Monte
Carlo noise, so we call it **fragile**.

### 3. Secondary — stratified BH
At m = 2, stratified minus F1 power: small **−0.21**, mid **−0.17**, large **+0.08**. Stratified BH helps the
large stratum (where 10 of 11 real F1 hits sit, so the BH cut is loose) and hurts small/mid (few or no real hits,
so the cut is near q/126). No stratum reaches 0.5 under stratified BH at any m ≤ 4 (large best: 0.46 at m = 4).
**Not adopted** (rule 3 fails: drops > 0.03 in two strata).
Descriptive only: stratified BH on the real scan names 12 large-stratum khipus, including two not in any F1 list,
KH0502/UR266 (p 0.0021) and KH0511/UR273B (p 0.0019); S0 BH names KH0038/UR1033D, KH0198/AS181/UR236,
KH0503/UR267A. **Not discoveries** under the adopted tool (F1).

### 4. Real scan with a fresh seed (reproducibility, not a new claim)
F1 = **11** again; 9 shared with K033. Swapped at the BH boundary: **KH0420/UR182 out** (p 0.0005 → 0.0019) and
**KH0478/UR242 in** (0.011 → 0.0011). KH0478's change comes from the adaptive Monte Carlo cut: in K033 its stage-1
p landed just above 0.01 (no escalation, p stays at K = 1 000); here it fell below and was escalated to K = 10 000.
KH0420 remains **confirmed** by K034's held-out test, which does not use the BH ranking. Lesson: F1 membership near
the BH cut is seed-sensitive at K₀ = 1 000 and should be reported with MC uncertainty or a fixed larger K.

### Reading
- **Verdict: silence testable only against stronger effects (m* > 2).** At K033's strength (2 planted sums)
  silence is still unreadable in every stratum. A silent **small** khipu is a readable negative against **≥ 4**
  within-group exact sums; a silent **mid** khipu against **≥ 3** (fragile); **large** stays not testable at m ≤ 4.
- Real-data consequence: the mid stratum, which has **0** F1 discoveries, shows no within-group exact-sum excess
  as strong as ~3 planted windows (fragile). The large stratum's non-hits cannot be read.
- Stratified BH is calibrated but trades small/mid power for large power; not adopted.
- Pre-registered decision: **gate passed; m*: small 4, mid 3 (fragile), large none; stratified BH not adopted.**

### Next (line 1)
K036: remove the adaptive-cut seed sensitivity by giving every F1 khipu a fixed K = 10 000 (or K₀ 2 000 with
escalation at p ≤ 0.02), then re-run the m-curve on large only with m ∈ {4, 6, 8} to locate large's m*.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
