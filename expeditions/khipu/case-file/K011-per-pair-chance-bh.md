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

## Amendments
- One code bug before the first real run: my splice of K009's loader dropped the `collections` import and
  kept K009's old seed line. The script crashed at line 10 before reading any data; fixed and run once. No
  result was seen before the fix.

## Results (`python3 tools/k011_per_pair_bh.py data/khipu.db`, 32 s, one run)
N = 433 khipus, m = 93 528 pairs, 7 573 pairs with a shared block of at least 3.

| Check | Rule | Result | Verdict |
|---|---|---|---|
| (a) Null corpora with any BH discovery | ≤ 6 of 40 | **40 of 40** (mean 68.4 discoveries, range 37 to 137) | **fails** |
| (b) Share of all null pairs with p < 0.01 | ≤ 0.02 | 0.011 | passes |
| Planted 6-cord copies found by BH | ≥ 0.5 | 0.63 (median p 2·10⁻⁶) | not interpretable |

**The approximation is excluded as a tool for this corpus.** Under the run-preserving null, where every khipu
keeps its own runs and values but any link between khipus is destroyed, BH still "discovers" about 68 pairs per
corpus. The real data gives 72, which is inside the null range (11 of 40 null corpora gave 72 or more). So the
real list is not evidence of anything, and the planted power of 0.63 means nothing, because a detector that flags
dozens of pairs in pure noise will flag plants too.

Why it fails, from the null discoveries' shape and the real list (descriptive, not pre-registered): most flagged
blocks are runs of one small value (`2, 2, 2, 2, 2`, `5, 5, 5, 5, 5, 5`) or near-runs (`2, 1, 2, 2, 2`). The formula
assumes each position is independent, so it prices a run of six 2s as q⁶. But a khipu that has runs makes long
equal blocks far more likely than that. The run-preserving null keeps the runs, which is exactly why it exposes
the problem. The five K010 pairs do head the real list (the top three at p 10⁻²⁵ to 10⁻¹⁴), which agrees with
K010 but adds nothing.

## Verdict
- **Excluded (as a tool):** the independent-positions longest-match probability with BH over pairs. It is
  miscalibrated under a structure-preserving null (40 of 40 corpora give false discoveries).
- **Not testable (still):** short cross-khipu matches. K010's family-wise result stands unchanged.
- **Next for line 3:** a chance probability that respects runs. Two concrete options for a future cycle, each to be
  pre-registered: (1) compare run-collapsed sequences (each run becomes one symbol with its length), so a run of
  2s counts once; or (2) a per-pair empirical p from the run-preserving null for the few hundred pairs with the
  longest blocks, then BH over those, with the selection step built into the null.

Raw output: `analysis/k011_results.json` (summary, discoveries per null corpus, top 10 real rows; the full list and planted p-values regenerate from the tool with its fixed seed in 32 s).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
