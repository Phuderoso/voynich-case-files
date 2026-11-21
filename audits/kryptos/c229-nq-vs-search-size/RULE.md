# RULE — case 215 / cycle 229: null maximum NC per quadgram-count bin, and does it track log(number of decipherments in the bin) more than nq?

Voynich desk, 2026-11-21 (America/Dawson_Creek, MST). Written and hashed **before** any maximum NC was tabulated or any model was fit,
and before opening `summary229.json`, `analyze229.log`, `plants229.tsv`, `tools/cycle229/*` code, or `gateT/`. Not fully blind: see LEAKS.md.

## Inputs (fixed)
- Fresh sparse clone of `Phuderoso/kryptos-case-files` @ `01e823035e4b581fafd599534b08fcac6c910084`, folder `/workspace/k229-nq-vs-search-size/kryptos-main`:
  `data/cycle229/R/`, `data/cycle229/{MANIFEST.txt, SHA256SUMS, nulls229.tsv, resume229.sh}`, `tools/cycle229/PREREG229.md` only.
  Every file of `R/` present is verified against `data/cycle229/SHA256SUMS` (the 6 listed files I did not check out are not used).
- **Y lines** of the 16 null texts (seeds 209559–209574; 8 files each: `direct_a`, `direct_b`, `bank_Q_r10`, `bank_V_a`, `bank_V_b`, `all_Q_r10`, `all_V_a`, `all_V_b`),
  format `Y model=M p=P nq=Q n=N pass=K max=X`: for each (model, p, nq), the number N of scored V / Q hits with known ≥ 49 and nq ≥ 1 (the decipherments), K of them with NC ≥ −6.0,
  and the max NC X (3 decimals; floor −8.469). NC, known, tie = '?' and the −6.0 bar are hers (PREREG227/229); I do not re-decrypt here (the Y lines carry no texts).
  K4 Y lines (`k4_*` files) are tabulated only as a reference column. Plants (`plant_*.txt`) are not used.

## Bins and pooled quantities (primary)
- **nq bin** = the printed nq (1..64). For each nq: **N_bin** = Σ n over all Y lines of the 16 nulls and all 8 file types and all (model, p);
  **max_bin** = max of the printed max; **pass_bin** = Σ pass; plus the number of Y cells (null, file, model, p) with pass > 0 and their identities.
  N_bin counts decipherments as printed: Q is the r10 subsample (every 10th row), V is full scale, `bank` and `all` overlap on most rows (not de-duplicated).
  Secondary strata (same bins, same fits): V only, Q only, `all.bin` scope only.

## Model set (declared before fitting; the response is y = max_bin; OLS, unweighted)
Fit set: bins with **N_bin ≥ 20** (primary). Sensitivities: N_bin ≥ 5, N_bin ≥ 100, N_bin ≥ 1000.
- **M0**: y = a
- **M1**: y = a + b·ln(N_bin)
- **M2**: y = a + c·nq
- **M3**: y = a + b·ln(N_bin) + c·nq
- **M4** (extreme-value form: the max of N draws of a mean of nq terms): y = a + b·sqrt(2·ln N_bin)/sqrt(nq)
- **M5**: y = a + b/sqrt(nq)
Report per model: k, RSS, R², adjusted R², AIC = m·ln(RSS/m) + 2k' and AICc (m bins, k' = k + 1 counting the variance), ΔAIC to the best, estimated coefficients and t-statistics.
Also corr(ln N_bin, nq) and the VIF of M3.

## Permutation / rank checks (10,000 permutations, `numpy.random.default_rng(20261121)`)
1. **Rank:** Spearman ρ(y, ln N_bin) and ρ(y, nq) (no ties handling beyond average ranks), with two-sided permutation p-values (shuffle y over bins), and the **partial** Spearman of y with ln N_bin given nq, and with nq given ln N_bin (rank-residual correlation, permutation p by the Freedman–Lane scheme below).
2. **Freedman–Lane partial tests** for M3: H0 b = 0 (reduced model M2, permute its residuals, refit M3, statistic = t of b), and H0 c = 0 (reduced model M1, same). Two-sided p = (1 + #{|t*| ≥ |t|}) / 10001.
3. **Model-difference check:** observed R²(M1) − R²(M2) against its distribution when y is shuffled over bins (two-sided).

## Pre-declared verdict
- **LOGN-DOMINATES:** AICc(M1) ≤ AICc(M2) − 2 and Freedman–Lane p(b | nq) < 0.05 and not (p(c | lnN) < 0.05).
- **NQ-DOMINATES:** AICc(M2) ≤ AICc(M1) − 2 and p(c | lnN) < 0.05 and not (p(b | nq) < 0.05).
- **BOTH:** both partial p < 0.05. **NEITHER / INCONCLUSIVE:** otherwise.
- Stated for the primary (N ≥ 20, pooled) fit; the strata and sensitivities are reported beside it and cannot change the label.

## Pass accounting
- Per nq: pass_bin; list of Y cells with pass > 0 (null, file, model, p, nq, pass count, max); number of distinct nulls with ≥ 1 pass; counts in nq 10 and 11.
  (The Y lines do not carry decrypt texts, so "distinct text" cannot be recovered here; the count is of nulls and of Y cells.)
- Expected-pass sanity: none fitted; no new bar is proposed here.

## Outputs
`counts_by_nq.tsv` (pooled, plus K4 reference and the V / Q / all strata), `fits.tsv`, `perm.txt`, `pass_cells.tsv`, `summary_nq_search.txt`, `nq_search.py`, then `FROZEN.txt`, `SHA256SUMS`.
The comparison with her published numbers is **not** part of the freeze.
