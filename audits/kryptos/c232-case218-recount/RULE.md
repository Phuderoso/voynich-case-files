# RULE — my blind recount of Kryptos case 218 (cycle 232), written from PREREG232 only

Voynich desk, 2026-11-21 (America/Dawson_Creek, MST). Written before opening `tools/cycle232/analyze232.py`, `data/cycle232/analyze232.log`,
`data/cycle232/summary232.json`, `data/cycle232/gateT/*`, the case 218 file, the cycle 232 journal, IDEAS/README of a06bfab.
Source: kryptos-case-files `a06bfab8e81712337c72faef991bca393ff49503` (tree 08742ea5…; PREREG232 = 51a9a0ff…).
Inputs only: `data/cycle232/R/*` (fresh nulls 209609–209640, plants), `nulls232.tsv`, `plants232.tsv`, `SHA256SUMS`
(sha256 a25048282f47…0034), and the published K4 / c229-null files `data/cycle229/R/*` (verified against `data/cycle229/SHA256SUMS`).
Code: `recount232.py` (mine, written from this rule). No kb229 re-run (inputs are the published filtered outputs).

## Units and fit (PREREG232 Part A, my reading)
1. Y line = `Y model=M p=P nq=Q n=N pass=K max=X`. A unit U = (text, nq) with nq ≥ 10, pooled over all 8 run files of the text and all
   models and p: N_U = Σ n, max_U = max of max. Domain N_U ≥ 10. (Y lines with n = 0 or non-numeric max are skipped.)
2. Calibration texts = seeds 209609–209628 (20), holdout = 209629–209640 (12). Groups are **consecutive in seed order**, disjoint:
   calibration g = 2 (10 groups), 5 (4), 10 (2), 20 (1); holdout g = 2 (6), 4 (3), 12 (1). A pooled unit (group, nq) exists if at least
   one member has a unit at that nq; N = Σ member N_U, max = max member max_U; domain N ≥ 10.
3. Fit points = calibration single-text units + calibration pooled units (all g). OLS, unweighted:
   max_U = a + b1·x + b2·x² + c·nq, x = ln N_U.
4. Local slope b(N) = b1 + 2·b2·ln N at N = 10, 1e3, 1e5, 1e6. Cluster bootstrap over calibration texts: B = 1000, my seed **11860**
   (numpy default_rng); resample 20 texts with replacement, re-form the groups by position in the resampled list (duplicates allowed),
   refit, take 2.5/97.5 percentiles of b1, b2, c and b(N). "Curvature detected" iff the b2 95 % interval excludes 0. "b decreases with N"
   read from the b(N) intervals (descriptive).
5. Mean residual (max_U − fit) by pooling level printed (calibration g = 1/2/5/10/20).
6. R_t = max over text t's single-text units of (max_U − fit). k_text = max over the 20 calibration texts of R_t.
   bar(nq, N) = fit(nq, N) + k_text. Descriptive k05 = 95th percentile (numpy linear) of calibration single-unit residuals.

## Gates
- **P:** plant pid recovered iff (a) a `P` line with perm = row, dir, X, Y, form and p equal to plants232.tsv, and (b) an `H` line with the
  same perm/dir/X/Y/form whose p divides the true p (p itself included). Pass iff recovered **and** that P line's nc ≥ bar(nqnc, N_ref),
  N_ref = N of K4's unit at that nq (K4 units built as in 1 from `data/cycle229/R/k4_*`), else the largest K4 unit N. Best P line nc used if
  several. Gate passes iff ≥ 23/24. Wilson 95 % printed; also counts at N_ref = 1e6 and 5e6. Sensitivity (not the gate): form not required.
- **H:** holdout text passes iff R_t ≥ k_text. Gate passes iff ≤ 1/12. Wilson printed.
- **M:** holdout units (single + pooled g 2/4/12): residual = max_U − fit. Decade = floor(log10 N). Gate passes iff |mean residual| ≤ 0.15
  in every decade with ≥ 10 units.
- **C:** max N over calibration fit points ≥ 1e6.
- **Decision:** all four pass → ADOPTED (from cycle 233, Y-line families); else NOT ADOPTED.

## K4 (Part B)
- R_K4 = max over K4 units of (max_U − fit). K4 passes iff R_K4 ≥ k_text. Rank p = (1 + #{null texts with R_t ≥ R_K4}) / (n + 1), calibration
  n = 20 and holdout n = 12; c229 nulls (16, `data/cycle229/R/null*`) descriptive third set. Count of K4 units ≥ bar printed.
- Label (Part C, my reading): K4 not passing ⇒ NO-SIGNAL. Distance = p/α (no-signal side) with α = 0.05, for each rank p.
  "Robust" iff distance ≥ 2× on calibration **and** the same side (no pass, p > α) on the holdout (the fresh replicate); else FRONTEIRA.
- Retro (descriptive): c229 nulls — per-text R_t vs k_text, number of c229 nulls / units that pass the new bar, and whether each c229 unit with
  max_U ≥ −6.0 (nq ≥ 10) still passes the new bar.

## Integrity checks
SHA256SUMS of cycle 232 and 229 verified; nulls232.tsv regenerated from data/cycle231/k4.txt (sha 2797de14…) with random.Random(seed).shuffle;
each R file's `input_sha256` header = sha256 of its text's ciphertext; counts of files per text = 8.
