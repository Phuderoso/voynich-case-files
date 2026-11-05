# K013 · Run-length-aware symbols: getting power back without losing calibration

## Pre-registration (written 2026-11-05 05:16 PT, before any K013 code was run)
- **Question (README line 3).** K012's run-collapsed test is calibrated (0 of 40 null corpora with a false
  discovery) but finds only 25% of planted 6-cord copies, because it throws run lengths away. If each run becomes
  the symbol (value, run length), so a block has to agree on both, does power reach 0.5 while staying calibrated?
- **Data.** Exactly K009–K012: OKR `khipu.db` @ `4039ca5`, duplicate-flagged khipus removed, multi-number (R5)
  pendants masked to 0, khipus with at least 10 non-zero pendants (N = 433, m = 93 528 pairs).
- **Symbols.** Each khipu's pendant-value sequence becomes its sequence of runs, and each run becomes one symbol
  (value, length). Zero-value runs stay as symbols and break blocks.
- **Statistic.** As in K012, but on these symbols: the longest aligned block of equal non-zero symbols per pair, from
  shared 3-symbol seeds (pairs without one get p = 1). Then q = Σ_s p_A(s)·p_B(s) over non-zero symbols s (shares
  among each khipu's symbols), λ = (1 − q)·q^L·(n_A − L + 1)(n_B − L + 1), p = 1 − exp(−λ).
- **Correction.** BH at FDR 0.05 over all m pairs.
- **Null.** The run-preserving permutation (it keeps every run and its length), then re-collapsing, so equal runs
  that end up next to each other merge, as they would in real data. 40 corpora, seed 20131105.
- **Calibration rule (unchanged from K011/K012).** Acceptable only if (a) at most 6 of 40 null corpora give any BH
  discovery and (b) the pooled share of all null pairs with p < 0.01 is at most 0.02. Failing either: excluded as a
  tool.
- **Power.** 200 planted 6-cord copies (planted in the uncollapsed null sequence, as K010–K012, then collapsed);
  recovered if the planted pair is a BH discovery. Short matches are **testable** only if calibrated and power ≥ 0.5.
- **Reading.** If calibrated, report every BH discovery against K010–K012. The K012 lead KH0240/KH0496 has
  different run lengths, so this test is not expected to find it, and not finding it does not refute it.
- **Budget.** One run, `timeout 600`. Any amendment is disclosed below.
