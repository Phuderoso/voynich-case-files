# K039 · Fixed-K = 10 000 pooled-pop BH-level F1 power at m ∈ {4, 6} (README line 1)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registered** (this file and `tools/k039_fixedk_pooled_power.py` are pushed before any K039 power statistic is computed).

## Why
K036–K038 put line 1's silence map on one design (fixed K = 10 000; D5w; pooled exchangeable min-p; BH q = 0.05):
m*_small = 4, m*_mid = 4, m*_large = 6. A silent pop khipu is a readable negative only against an excess of
4 (small, mid) or 6 (large) planted within-group exact-sum windows, never at K033 strength (m = 2).

K038 proposed one remaining power check: a **pooled-pop** BH-level number at m = 4, so the expedition can
either adopt a single corpus-level readable-negative statement or refuse one because a pooled average would
conceal an unreadable third (large's published power at m = 4 is 0.416, below the bar). K039 runs that
check, and the matching check at m = 6 (where large first becomes readable), on the same inherited K036
p-map. **No new statistic. Published stratum m* are not revised.**

## Data and strata (fixed; identical to K031–K038)
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`,
verified before the run), level-1 pendants, `DUPLICATE_FLAG` dropped, ≥ 10 nonzero pendants (457). Groups =
runs of consecutive pendants sharing `CLUSTER_ID`. pop = ≥ 2 groups of size ≥ 4 (378); thirds by pendant
count on pop (small / mid / large, 126 each); S0 = 79. The tool recomputes strata and **stops (excluded)**
unless n_eligible, n_pop, thirds and every khipu's stratum match K036's published rows.

## Detector, plants and p (unchanged)
Copied from `tools/k038_fixedk_smallmid_power.py` without change: D5w scoring (`scores_w`, `valid_masks`),
`plant_within_m` (K035; A_within / B_within with probability ½), pooled exchangeable min-p (K033),
BH q = 0.05, fixed **K = 10 000** draws per plant, CHUNK = 1 000. Code:
`tools/k039_fixedk_pooled_power.py`.

## Inherited, not recomputed: K036's real F1 p-map and calibration
Same reasons as K038:
1. K036 already adopted the fixed-K F1 reference list (14 names) and published its calibration: gates 0/5
   (BH F1 discoveries per null corpus 0/0/0/0/0); D5w FPR small 0.0238, mid 0.046, large 0.0349,
   pop 0.0349, S0 0.0329; all `gate_pass` true; `gate_F1` true. Same K, same detector, same data, same strata.
2. Re-scanning with a new seed would jitter the adopted list and spend compute the power curve needs.
3. BH-level power = the plant's pooled p inserted in place of that khipu's real p in the **already
   published** F1 family (`bh_insert` on K036's `real_F1` p-map, pop = 378).

The tool loads `analysis/k036_results.json`, builds `real_F1 = {khipu_id: p_D5w}` over pop, and copies the
K036 FPR / BH numbers into the output as `inherited_calibration` (cited, not recomputed). If the file is
missing or `decision.gate_F1` is not true, it stops and reports — no p-value is invented.

## Scope of new compute
Power only, **all 378 pop khipus**, **m ∈ {4, 6}**. No real scan, no null corpora, no m = 2, 3, 5 or 8,
no S0. Two passes, so a wall cap prefers a complete primary:
1. **Primary:** every pop khipu at m = 4, strata interleaved (small₁, mid₁, large₁, …).
2. **Secondary:** every pop khipu at m = 6, same interleave.

Per-stratum rates at each m are recorded as **descriptive** seed-sensitivity against K036 (large m = 4 / 6)
and K038 (small / mid m = 4 only). They do not rewrite published m*.

## Seed and wall
Power seed **3939** only (distinct from K031–K038: 3130–3832). WALL = 520 s inside the tool; outer
`timeout 560`. `--smoke` keeps the full-data strata but plants only every 11th pop khipu (syntax check;
output `analysis/k039_smoke.json`, not used for decisions). Checkpoint every 20 khipus to
`analysis/k039_checkpoint.json`.

## Decision rules (written before the run)
1. **Excluded** if K036 `gate_F1` is not true, the p-map cannot be loaded, or data/strata do not match K036.
2. For each m ∈ {4, 6}, compute pooled-pop BH-level F1 power (`bh_F1` rate over every completed plant at
   that m) and the three stratum rates.
3. **meets_bar(m)** = pooled n ≥ 30 and pooled `bh_F1` ≥ 0.5.
4. **all_strata_readable(m)** = every stratum in {small, mid, large} with n ≥ 30 has `bh_F1` ≥ 0.5.
   (A stratum with n < 30 is ignored for this clause, not treated as readable.)
5. **adopt_corpus_statement(m)** = meets_bar(m) AND all_strata_readable(m). A pooled average that meets
   the bar only by mixing readable small/mid khipus with an unreadable large third is **not adopted**:
   that would conceal the unreadability K036 already measured.
6. **corpus_m\*** = smallest m ∈ {4, 6} with adopt_corpus_statement(m). Verdict:
   - if set: "corpus-level silence readable against ≥ {corpus_m*} planted within-group sums (every
     stratum also meets the bar at this m)";
   - else: "no corpus-level readable-negative statement at m in {4, 6}; keep stratum-specific thresholds
     (K038: small 4, mid 4; K036: large 6)".
7. Published m* (K038 small 4 / mid 4, K036 large 6) are **not revised**, even if a descriptive
   per-stratum rate here crosses or misses 0.5 (different seed; n may also differ when a plant cannot
   place m windows). Negatives published. If wall-capped, publish partial (`power_capped`,
   `power_khipus_reached` per pass); rules 3–4 still require n ≥ 30.
8. No new discoveries claimed. No holdout invented.

## Output
`analysis/k039_results.json`: design, `consistency_with_K036`, `inherited_calibration`, power by stratum
and pooled for each m (n, p05, bh_F1), `meets_bar`, `all_strata_readable`, `adopt_corpus_statement`,
`corpus_m_star`, verdict, descriptive `vs_published`, `power_rows`, secs. Log: `analysis/k039_run.log`.

## No claims
A readable negative means "no excess as large as m* planted within-group exact sums", never "no
arithmetic". A corpus-level statement, if adopted, is the conservative number at which *every* pop
stratum is readable, not a licence to read silence in large at m = 4. No decipherment is claimed.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
