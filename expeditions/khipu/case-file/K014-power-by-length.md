# K014 · Where does short-match power begin? A power curve, and a combined detector

## Pre-registration (written 2026-11-05 05:28 PT, before any K014 code was run)
- **Question (README line 3).** K012 (run-collapsed values) and K013 (run-length-aware symbols) are both calibrated,
  but each finds only about 0.25–0.32 of planted 6-cord copies. At what copy length does each reach power 0.5,
  and does a combined detector (a pair counts if either test finds it, each run at FDR 0.025) do better while
  staying calibrated?
- **Data and tools.** Exactly K012/K013: OKR `khipu.db` @ `4039ca5`, duplicate-flagged khipus removed, R5 masked,
  N = 433, m = 93 528. Same block search, same Poisson longest-match p-value, same BH over all m pairs.
- **Combined detector.** BH at 0.025 on the K012 p-values, BH at 0.025 on the K013 p-values, take the union.
  (Under the union bound, FDR ≤ 0.05 if each holds; checked empirically below, not assumed.)
- **Calibration of the combined detector.** 40 run-preserving null corpora (seed 20141105), same rule as K011–K013:
  at most 6 of 40 with any discovery, and the share of null pairs with min(p12, p13) < 0.005 is at most 0.02.
  If it fails, the combined detector is excluded and only the single-test curves are reported.
- **Power curve.** Planted copy lengths L ∈ {6, 8, 10, 12, 16} raw cords, 100 plants each (at least L − 1 non-zero
  cords in the copied stretch), planted in a fresh run-preserving null corpus, then collapsed. A plant is
  recovered if its pair is a discovery. For each detector, the **detection floor** is the smallest L with power
  ≥ 0.5.
- **Reading.** Matches shorter than the floor are declared **not testable** with these tools; matches at or above it
  are testable, and the K012/K013 maps of real discoveries are then complete for that length range (up to the power
  shown).
- **Budget.** One run, `timeout 600`. Any amendment is disclosed below.
