# K011 · Per-pair chance probabilities with BH for short cross-khipu matches

## Pre-registration (written 2026-11-05 04:47 PT, before any K011 code was run)
- **Question (README line 3).** K005–K010 judged every pair against the maximum over all ~100 000 pairs, which
  controls family-wise error but leaves 6-cord copies at power 0.20. Does a per-pair analytic chance probability,
  corrected with Benjamini–Hochberg (BH) over all pairs, make short matches testable while staying calibrated?
- **Data.** Exactly K009/K010: OKR `khipu.db` @ `4039ca5`, duplicate-flagged khipus removed, multi-number (R5)
  pendants masked to 0, khipus with at least 10 non-zero pendants. Blocks are runs of equal non-zero pendant values
  at aligned positions, found from shared 3-value seeds (so blocks shorter than 3 are never scored; those pairs get p = 1).
- **Statistic.** For each pair (A, B) with longest shared block length L: q = Σ_v p_A(v)·p_B(v) over non-zero values
  v, where p_X(v) is the share of X's pendants (zeros included) equal to v. Per-pair chance probability by the
  standard longest-match (Poisson, declumped) approximation: λ = (1 − q)·q^L·(n_A − L + 1)(n_B − L + 1),
  p = 1 − exp(−λ). This is an approximation to the exact probability and assumes independent positions, so it is
  only trusted if it passes the calibration check below.
- **Correction.** BH at FDR 0.05 over all m = N(N − 1)/2 pairs (pairs with no block count, with p = 1).
- **Calibration (run-preserving null, 40 corpora, seed 20111105).** Acceptable only if (a) at most 6 of 40 null
  corpora (0.15) give any BH discovery, and (b) the pooled share of all null pairs (p = 1 for pairs with no block) with p < 0.01 is at
  most 0.02 (twice nominal). Failing either: the approximation is **excluded as a tool** here (runs or other
  dependence break it), and no list of discoveries is reported as evidence.
- **Power.** 200 planted 6-cord copies into run-preserving null corpora (as K010); recovered if the planted pair
  is a BH discovery in its corpus. Short matches are **testable** only if calibration passes and power ≥ 0.5.
- **Reading the real data.** If calibrated: report every BH discovery. The five K010 pairs are known; any other
  discovery is a *lead*, checked by hand for runs or obvious artefacts before any claim. If power < 0.5, silence on
  other pairs is still not evidence of independence.
- **Budget.** One run, `timeout 600`. Any amendment is disclosed below.
