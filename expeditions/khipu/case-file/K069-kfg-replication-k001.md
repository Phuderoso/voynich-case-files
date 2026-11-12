# K069 · KFG re-audit of K001 (adjacent sum cords)

First step of open line 9 (the *OKR vs KFG replication* table): re-run the first verdict-reaching result, K001, on the
curated Khipu Field Guide (KFG) data that K068 loaded, with nothing changed except the data source and the seed.

## Pre-registration (fixed in `tools/k069_kfg_k001_replication.py` before the registered run)
- **Question.** Do the 10 khipus that K001 (amendment A1, K = 5000) found BH-significant for adjacent sum cords on the
  historical OKR stay significant on KFG data?
- **Data.** KFG store `/workspace/kfg/kfg_20261111.db` built by K068 from the per-khipu Excel files (write date
  2026-09-08; per-file SHA-256 in `data/MANIFEST.md`). Pendants = cords named `p<n>` in sheet order; value = KFG
  `Value` column (blank = 0). Cord groups for N2 are read from each file's `CordGroups` sheet
  (`… group of n pendants (a-b)` and single-pendant rows `… 1 (a)`). KFG has no duplicate flag (duplicates are
  coalesced), so no khipu is excluded. Khipus with at least 10 nonzero pendants are tested.
- **Statistic, nulls, controls.** Verbatim from K001: S = pendants with value ≥ 10 equal to the sum of the next or
  previous k pendants (k 2–12, ≥ 2 nonzero); N1 within-khipu value permutation; N2 group-order permutation (≥ 4 groups);
  p = (1 + #null ≥ S)/(1 + K), **K = 5000**; calibration (one shuffled copy as observed) and planted control (two
  3-summand sums in shuffled copies with ≥ 20 pendants). BH-FDR q 0.05 across all tested khipus.
- **Seed.** 6417 (one stream; next free **6418**). K001 used 20261104; a different seed is part of the test.
- **Gates.** G0: every Excel file's SHA-256 equals the K068 store (0 mismatches). G1: `CordGroups` partitions the
  pendants exactly (1..n, contiguous) in ≥ 95 % of tested khipus. G2: calibration FPR at p ≤ 0.05 is ≤ 0.05.
  A0 (audit, not a gate): the unchanged K001 tool re-run on OKR (K = 5000, seed 20261104) reproduces the 10 names.
- **R1, per name (primary).** For each of K001's 10 names (KH0359, KH0405, KH0491, KH0492, KH0503, KH0504, KH0506,
  KH0507, KH0513, KH0514): **REPLICATED** if BH-significant under N1 on KFG; **WEAKENED** if p_N1 ≤ 0.05 but not
  BH-significant; **NOT REPLICATED** if p_N1 > 0.05; **NOT TESTABLE** if absent or under 10 nonzero pendants.
- **Headline rule (declared convention).** If all gates pass: ≥ 8 of 10 REPLICATED → *K001 replicated on KFG*;
  5–7 → *partly replicated*; ≤ 4 → *not replicated* (a correction to K001 would be published).
- **Secondary (descriptive, no claim).** New KFG-only BH names (with their OKR status); S1 = BH over the khipus whose
  KH id is shared with the OKR only (KFG's larger m makes BH stricter); N2 BH count (K001: 0 of 367); planted power
  (K001: 0.38); corpus totals S vs null mean.
- **Disclosures.** Smoke runs before registration were K = 20 (plumbing and gates only: 525 tested khipus, 471 shared,
  436 with ≥ 4 groups, G0 0, G1 1.00, G2 0.021, no unparseable values, KH0521 has non-sequential pendant names but its
  groups still cover 1..n) and K = 200 (timing only). No R1 classification or p-value was looked at.

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
