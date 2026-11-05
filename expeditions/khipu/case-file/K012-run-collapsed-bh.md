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

## Amendments
None. One run.

## Results (`python3 tools/k012_run_collapsed_bh.py data/khipu.db`, 15 s)
N = 433 khipus, m = 93 528 pairs, 5 323 pairs with a shared collapsed block of at least 3.

| Check | Rule | Result | Verdict |
|---|---|---|---|
| (a) Null corpora with any BH discovery | ≤ 6 of 40 | **0 of 40** | passes |
| (b) Share of all null pairs with p < 0.01 | ≤ 0.02 | 0.0007 | passes |
| Planted 6-cord copies found by BH | ≥ 0.5 | **0.25** (median p 1.5·10⁻⁴) | target missed |

**Calibrated, but not powerful enough.** Collapsing runs fixes K011's problem completely (false discoveries per
null corpus went from 68 to 0), which confirms that runs were the cause. But it is conservative, and it throws away
run lengths, so a planted 6-cord copy is found only a quarter of the time. Short matches stay **not testable**.

### Real BH discoveries (6)
| Pair | Collapsed block | p | Run lengths agree? | Reading |
|---|---|---|---|---|
| KH0362 UR122 · KH0049 AS038/HP036 | 12 | 4.3·10⁻²⁴ | yes | known (K005–K010) |
| KH0128 UR1114 · KH0137 UR1123 | 10 | 1.3·10⁻¹⁷ | yes | known |
| KH0140 AS125 · KH0483 UR247 | 12 | 2.9·10⁻¹⁴ | yes | known double recording |
| KH0240 UR004 · KH0496 UR260 | 9 | 1.3·10⁻⁸ | **no** | **new lead**, see below |
| KH0304 UR067 · KH0303 UR066 | 7 | 2.6·10⁻⁷ | yes | known Puruchuco pair |
| KH0284 UR053B · KH0285 UR053C | 6 | 3.1·10⁻⁶ | no | same object number (Banco Central ATE 3517): parts of one khipu, expected |

The fifth K010 pair (Puruchuco UR068/UR064) is not found here, which fits the lower power.

**The lead, inspected by hand.** KH0240 (Leymebamba, Centro Mallqui) and KH0496 (Incahuasi) share the collapsed
pattern `1, 2, 1, 2, 3, 1, 2, 1, 3`. Their run lengths differ (`4,1,1,1,1,1,1,1,1` vs `1,1,3,1,1,2,1,1,1`), so the
two khipus do not record the same numbers. What they share is the order in which small values change. All values
are 1 to 3, the alphabet where chance agreement is easiest, although the calibrated null accounts for each khipu's
own value shares. It is a **lead only**: one hit among 93 528 pairs. It is not checked against the literature, and
it is not a claim of a link between the two sites.

## Verdict
- **Advanced:** a calibrated per-pair test for cross-khipu blocks now exists (run-collapsed, BH). It confirms the
  four strongest known pairs, finds the expected UR053B/UR053C parts, and raises one new lead (KH0240/KH0496).
- **Not testable (still):** short copies (power 0.25 < 0.5). Silence on other pairs is not evidence of independence.
- **Audit of K011:** K011's diagnosis (runs break the independence formula) is confirmed by this cycle.
- **Next for line 3:** get power back without losing calibration. Score each collapsed block together with its
  run-length agreement, using a null that keeps run lengths. Or use option (2) from K011: empirical per-pair p-values
  for the top blocks.

Raw output: `analysis/k012_results.json` (summary, discoveries per null corpus, planted p-values, all six real rows
with run lengths).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
