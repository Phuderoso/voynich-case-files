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

## Results (one run, 9.4 s, log in the expedition's run notes; `analysis/k013_results.json`)
**Amendment, disclosed:** the tool is K012's with a single change, the symbol encoding (value·1000 + run length
for non-zero runs, 0 for zero runs; an assert checks that no run reaches 1000). No other run was made.

| Check | Rule | Result | Verdict |
|---|---|---|---|
| Null corpora with any BH discovery | ≤ 6 of 40 | **0 of 40** | pass |
| Pooled share of null pairs with p < 0.01 | ≤ 0.02 | **0.0006** | pass |
| Planted 6-cord copies recovered | ≥ 0.5 for "testable" | **0.32** (64/200) | short matches **not testable** |

So the test is **calibrated** (conservative, like K012), and power rose from 0.25 to 0.32, but not to 0.5.

**Real discoveries (6, BH 0.05), every block also agrees on run length by construction:**

| Pair | Block (symbols) | p | Status |
|---|---|---|---|
| KH0362 UR122 · KH0049 AS038/HP036 | 12 | 4.3e-24 | known (K006–K012) |
| KH0128 UR1114 · KH0137 UR1123 | 10 | 5.6e-19 | known |
| KH0140 AS125 · KH0483 UR247 | 12 | 2.9e-14 | known (OKR data-quality question) |
| KH0304 UR067 · KH0303 UR066 | 7 | 2.6e-07 | known (Puruchuco) |
| KH0305 UR068 · KH0301 UR064 | 8 | 7.5e-07 | known (Puruchuco); **recovered**, K012 had missed it |
| KH0616 JC009 · KH0620 JC013 | 6 | 2.7e-06 | **new lead** (Incahuasi PAI-007-2016 / PAI-008-2016), values 10, 1, 2, 10, 30, 28 |

- All five cross-khipu pairs from K010 are back, now under a calibrated null, which K010–K011 could not claim.
- K012's KH0284/KH0285 (same Banco Central object) is not found here, and neither is the K012 lead KH0240/KH0496,
  as expected because their run lengths differ. That does **not** refute it; it stays a lead.
- **New lead, not a finding:** two Incahuasi khipus from the same project share a 6-run block. Incahuasi khipus are
  discussed in the literature for repeated values across khipus; I have **not yet** checked this exact pair
  against it. Next: literature check, then a sharper power study at lengths 6–10.

**Verdict:** the run-length-aware per-pair test is a **calibrated tool**. It confirms 5 known cross-khipu matches and
adds one lead. Short (≈6-cord) matches remain **not testable** (power 0.32 < 0.5).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
