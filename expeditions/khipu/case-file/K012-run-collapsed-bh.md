# K012 · Run-collapsed sequences: a per-pair chance probability that respects runs

## Pre-registration (written 2026-11-05 05:04 PT, before any K012 code was run)
- **Question (README line 3).** K011's per-pair probability failed calibration because runs of one value (2, 2, 2,
  …) look like rare coincidences to a formula that assumes independent positions. If each run is collapsed to a
  single symbol, does the same per-pair probability with BH become calibrated, and can it then test short matches?
- **Data.** Exactly K009–K011: OKR `khipu.db` @ `4039ca5`, duplicate-flagged khipus removed, multi-number (R5)
  pendants masked to 0, khipus with at least 10 non-zero pendants (N = 433, m = 93 528 pairs).
- **Collapsing.** Each khipu's pendant-value sequence becomes its sequence of runs; each run becomes one symbol, its
  value (run length is dropped). Zero runs stay as symbols and break blocks.
- **Statistic.** The longest aligned block of equal non-zero collapsed symbols per pair, from shared 3-symbol seeds
  (pairs without one get p = 1). Then K011's formula on the collapsed sequences: q = Σ_v p_A(v)·p_B(v) over non-zero
  v (shares among collapsed symbols), λ = (1 − q)·q^L·(n_A − L + 1)(n_B − L + 1), p = 1 − exp(−λ).
- **Correction.** BH at FDR 0.05 over all m pairs.
- **Null.** K011's run-preserving permutation on the uncollapsed sequence, then collapsing (runs of equal value that
  end up adjacent merge, exactly as they would in real data). 40 corpora, seed 20121105.
- **Calibration rule (unchanged from K011).** Acceptable only if (a) at most 6 of 40 null corpora give any BH
  discovery and (b) the pooled share of all null pairs with p < 0.01 is at most 0.02. Failing either: excluded as a
  tool, and the real list is not reported as evidence.
- **Power.** 200 planted 6-cord copies (planted in the uncollapsed null sequence, as K010/K011, then collapsed);
  recovered if the planted pair is a BH discovery. Short matches are **testable** only if calibrated and power ≥ 0.5.
- **Reading the real data.** If calibrated, report every BH discovery; the five K010 pairs are known, and anything
  else is a lead to inspect by hand. Descriptive extra (not part of the decision): how many discovered blocks also
  agree on run lengths.
- **Budget.** One run, `timeout 600`. Any amendment is disclosed below.
