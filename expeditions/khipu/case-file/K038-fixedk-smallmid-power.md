# K038 · Fixed-K = 10 000 BH-level F1 power for small and mid, m ∈ {2, 3, 4} (README line 1)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registration** (written and pushed before any K038 power statistic was computed).

## Why
K037 confirmed both K036 candidates (KH0502/UR266, KH0511/UR273B) on the K034 L-window holdout, so every
F1-only name now carries a held-out confirmation. The remaining line-1 gap is **silence in small and mid**:
their readable-negative thresholds (K035: m* small = 4, power 0.10 → 0.59 over m = 1…4; mid = 3 *fragile*,
0.04 → 0.50, then 0.49 at m = 4) come from K035's **adaptive-cut** Monte Carlo (K₀ = 1 000, escalate if
p ≤ 0.01), the same schedule that caused the KH0420 ↔ KH0478 boundary swap. K036 removed that schedule and
measured large only (m*_large = 6). K038 extends K036's power design to **small and mid** at **fixed
K = 10 000**, m ∈ {2, 3, 4}, to replace the fragile adaptive-cut m* values. **No new statistic.**

## Data and strata (fixed; identical to K031–K037)
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`,
verified before the run), level-1 pendants, `DUPLICATE_FLAG` dropped, ≥ 10 nonzero pendants (457). Groups =
runs of consecutive pendants sharing `CLUSTER_ID`. pop = ≥ 2 groups of size ≥ 4 (378); thirds by pendant
count on pop (small / mid / large, 126 each); S0 = 79. The tool recomputes strata and **stops (excluded)**
unless n_eligible, n_pop, thirds and every khipu's stratum match K036's published rows.

## Detector, plants and p (unchanged)
Copied from `tools/k036_fixedk_large_power.py` without change: D5w scoring (`scores_w`, `valid_masks`),
`plant_within_m` (K035; A_within / B_within with probability ½), pooled exchangeable min-p (K033),
BH q = 0.05, fixed **K = 10 000** draws per plant, CHUNK = 1 000. Code:
`tools/k038_fixedk_smallmid_power.py`.

## Inherited, not recomputed: K036's real F1 p-map and calibration
Reasons (written before the run):
1. K036 already adopted the fixed-K F1 reference list (14 names) and published its calibration: gates 0/5
   (BH F1 discoveries per null corpus 0/0/0/0/0); D5w FPR small 0.0238, mid 0.046, large 0.0349,
   pop 0.0349, S0 0.0329; all `gate_pass` true; `gate_F1` true. Same K, same detector, same data, same strata.
2. Re-scanning with a new seed would jitter the adopted list and spend ~6 minutes that the power curve needs.
3. BH-level power = the plant's pooled p inserted in place of that khipu's real p in the **already
   published** F1 family (`bh_insert` on K036's `real_F1` p-map, pop = 378).

The tool loads `analysis/k036_results.json`, builds `real_F1 = {khipu_id: p_D5w}` over pop, and copies the
K036 FPR / BH numbers into the output as `inherited_calibration` (cited, not recomputed). If the file is
missing or `decision.gate_F1` is not true, it stops and reports — no p-value is invented.

## Scope of new compute
Power only, strata **small** and **mid**, **m ∈ {2, 3, 4}**. No real scan, no null corpora, no m = 1 or
m = 5, no large (K036 already has m*_large = 6 at m ∈ {4, 6, 8}). Small and mid khipus are processed
**interleaved** (small₁, mid₁, small₂, mid₂, … in data order) so a wall cap leaves both partially covered.

## Seed and wall
Power seed **3832** only (distinct from K031–K037: 3130–3733; K036 used 3630 / 36310–36314 / 3632).
WALL = 520 s inside the tool; outer `timeout 560`. `--smoke` keeps the full-data strata but plants only
every 11th small/mid khipu (syntax check; output `analysis/k038_smoke.json`, not used for decisions).
Checkpoint every 20 khipus to `analysis/k038_checkpoint.json`.

## Decision rules (written before the run)
1. **Excluded** if K036 `gate_F1` is not true, the p-map cannot be loaded, or data/strata do not match K036.
2. For each of small and mid independently: **m*** = smallest m ∈ {2, 3, 4} with BH-level F1 power
   (`bh_F1` rate) ≥ 0.5 **and** n ≥ 30. If none → that stratum is **not testable** at these m.
3. Verdict template: "silence readable against ≥ {m*} within-group sums in {stratum}" or
   "not testable at m in {2,3,4} for {stratum}".
4. Descriptive comparison to K035 (adaptive cut): small m* = 4 (0.10 → 0.59), mid m* = 3 fragile
   (0.04 → 0.50). K035 is not changed; K038 says whether fixed K **confirms**, **shifts** or **unreads**
   those m*.
5. No new discoveries claimed. No holdout invented. Negatives published. If wall-capped, publish partial
   (`power_capped`, `power_khipus_reached` per stratum); rule 2's n ≥ 30 still applies.

## Output
`analysis/k038_results.json`: design, `consistency_with_K036`, `inherited_calibration`, power by stratum
and m (n, p05, bh_F1), `m_star_small`, `m_star_mid`, verdicts, `vs_k035`, `power_rows`, secs. Log:
`analysis/k038_run.log`.

## No claims
A readable negative means "no excess as large as m* planted within-group exact sums in that stratum",
never "no arithmetic". No decipherment is claimed.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
