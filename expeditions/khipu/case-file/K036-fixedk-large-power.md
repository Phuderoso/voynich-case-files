# K036 · Fixed-K=10 000 F1 scan and large-only power curve m ∈ {4, 6, 8} (README line 1)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Why
K035 found that silence is readable against stronger effects only (m* small = 4, mid = 3 fragile, large none
at m ≤ 4), and that a fresh adaptive Monte Carlo seed swaps **KH0420 ↔ KH0478** at the F1 BH boundary
because the adaptive cut (K₀ = 1 000, escalate if p ≤ 0.01) changes which boundary names get K = 10 000.
K034 already confirmed KH0420 under a held-out L-window that ignores the BH ranking. Line 1's next step is
to remove that seed sensitivity and to push the large-stratum power curve past m = 4.

Two primaries, same cycle:

- **Primary A — Fixed-K F1 scan.** Re-run F1 (D5w, pooled exchangeable min-p, BH q = 0.05 over pop = 378)
  with a **fixed K = 10 000 draws for every khipu** (no adaptive cut / no K₀ stage). Compare F1 membership
  to K033 (seed-adaptive) and K035 (fresh adaptive). Hypothesis: fixed K removes the KH0420↔KH0478-type
  boundary swap; report overlap and any remaining swaps with MC uncertainty (p ± se, se from count/K).
- **Primary B — Large-only power curve.** BH-level F1 power for the **large stratum only**, planted
  within-group exact-sum count **m ∈ {4, 6, 8}** (same `plant_within_m` as K035). Find
  m*_large = smallest m with power ≥ 0.5 (n ≥ 30). If none → not testable even at m = 8.

## Data and strata (fixed; identical to K031–K035)
OKR `khipu.db` @ `4039ca5` (SHA-256 `60791303…`), level-1 pendants, `DUPLICATE_FLAG` dropped, ≥ 10 nonzero
pendants (457). Groups = runs of consecutive pendants sharing `CLUSTER_ID`. pop = ≥ 2 groups of size ≥ 4
(378); thirds by pendant count (small / mid / large, 126 each); S0 = 79.

## Detector and p
D5w scoring and pooled exchangeable min-p **unchanged** from K033/K035
(`tools/k033_pooled_minp_rescan.py`, `tools/k035_bh_power_multiplant.py`). Only the Monte Carlo schedule
changes: **fixed K = 10 000 for every khipu** on real, null, and power stages (no K₀ / no escalation).
Tool computes D5w only (F1 family); unrestricted D5 is out of scope this cycle. Code:
`tools/k036_fixedk_large_power.py`.

## Families (q = 0.05)
- **F1 (primary):** D5w BH over pop (378), as K033/K035.

## Plants (seed 3632; Primary B)
For each large-stratum khipu and each m ∈ {4, 6, 8}: a fresh within-khipu permutation, then m within-group
exact-sum windows inserted with K035's `plant_within_m` (A_within / B_within with probability ½). BH-level
power = the plant's pooled p inserted in place of that khipu's real p in the real F1 family.

## Calibration (seeds 36310–36314)
Five structure-preserving null corpora (each khipu replaced by a within-khipu permutation, groups kept),
scored under the **same fixed K = 10 000**.
- FPR gate (α 0.05) for pop and large: exact one-sided binomial P(X ≥ x | n, 0.05) ≥ 0.05.
- BH gate for F1: at most 1 of 5 null corpora with any discovery.

## Real scan (seed 3630)
Fixed-K F1 scan; membership compared to K033's and K035's published F1 lists. p reported with Monte Carlo
count and SE ≈ √(p(1−p)/K) (K = 10 000; pooled construction uses denominator K+1 for the observed rank,
so se uses that denominator).

## Decision rules (written before any run)
1. **Excluded** if F1's BH gate fails or the pop / large FPR gate fails under fixed K.
2. Fixed-K F1 list is the **new reference list for line 1** iff the gate passes; report vs K033/K035
   shared / swapped. Do **not** claim new discoveries unless a khipu appears that was in neither prior list
   **and** passes a pre-registered holdout (no holdout invented this cycle — just flag candidates).
3. For large: if m*_large ∈ {4, 6, 8} → silence readable against ≥ m* planted within-group sums in large;
   else **not improved / not testable** at these m.
4. Wall clock: stop at ~560 s if needed; publish partial.
5. Negatives published.

## Seeds
scan 3630, nulls 36310–36314 (base 3631), power 3632 (distinct from K031–K035: 3130–3532).

## No claims
A BH hit means "more within-group adjacent exact sums than chance in this khipu under D5w"; a readable
negative means "no excess as large as m* planted sums", never "no arithmetic". No decipherment is claimed.

## Results

*(placeholder — filled after the run; prereg committed first)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
