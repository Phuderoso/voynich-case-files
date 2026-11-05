# K016 · Gapped ordered matches: weighted LCS with a max-statistic null, checked against Urton & Chu's pairs

## Pre-registration (written 2026-11-05 06:02 PT, before any K016 code was run)
- **Question (README line 3, opened by K015).** K015's post-hoc look suggests that the published Inkawasi close
  matches (Urton & Chu 2015) are **gapped, ordered** shared values. Does a weighted longest common subsequence
  (LCS) score, calibrated by a corpus-level null, find both published pairs, and which other pairs pass?
- **Data.** As K009–K015: OKR `khipu.db` @ `4039ca5`, duplicate-flagged khipus removed, R5 masked to 0, khipus with
  at least 10 non-zero pendants (N = 433, m = 93 528). Each khipu becomes its sequence of **non-zero** pendant values,
  in cord order.
- **Weights.** w(v) = −log2(share of v among all non-zero pendants in the corpus), so a shared 1 counts little and
  a shared 1411 counts a lot.
- **Scores (two, pre-declared).** S1 is the maximum total weight of a common subsequence (weighted LCS). S2 is
  S1 / √(W_A·W_B), where W is the khipu's total weight. S1 favours long khipus and S2 favours short ones.
- **Null.** Run-preserving permutation of each raw sequence (runs kept as blocks), then zeros removed. **100
  corpora** (seed 20161105) set the thresholds: T_k is the 97.5th percentile of the null **maximum** of S_k over all
  m pairs (k = 1, 2; family-wise error 0.025 each, 0.05 together).
- **Decision.** A pair is a discovery if S1 > T1 or S2 > T2 (family-wise error ≤ 0.05).
- **Calibration check (held out).** 20 more null corpora: the share with any discovery must be ≤ 0.15 (at most 3 of
  20). Failing that, the tool is **excluded**.
- **Positive controls (published, not tuned on).** KH0503 UR267A · KH0491 UR255 and KH0504 UR267B · KH0492 UR256. The
  tool is **accepted** only if calibrated and at least one control is a discovery. If neither is found, it is "not
  shown to see the published kind of match".
- **Power (descriptive).** 50 gapped plants: 12 consecutive non-zero values of khipu A written in order onto every
  other non-zero position of a stretch of khipu B, in a fresh null corpus. Recovered if the planted pair passes.
- **Sanity.** The five known exact pairs (K010–K014) should also pass.
- **Budget.** One run, `timeout 600`, with weighted LCS in a small C routine. Any amendment is disclosed below.
