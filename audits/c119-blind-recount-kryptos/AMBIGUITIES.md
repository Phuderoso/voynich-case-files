# AMBIGUITIES — C119 blind recount

Points where the case-file *procedure* (sections 1–10 and the run amendments; Results not read) under-specified an implementation choice, and the choice I made. Times in America/Vancouver (PT, UTC-7).

## Resolved against the section 6 control (CAE-DV W1 only)

These two choices were not stated in the prose. I fixed them by requiring the independent fitter to reproduce the *pre-registered* W1 numbers in section 6 (control only, not manuscript Results). After the fixes, W1 observed and N-LINE reps 1–3 match the table in 6.1 to the printed precision, including best ℓ = −79,623.3260516, A and π to four decimals, fitted ℓ = −79,622.673202, S, and B_11 / B_22.

1. **Symbol-ID order.** The prose names the C111/C117 EM and C108 `encode`, but C108 `encode` assigns IDs in first-seen (insertion) order, while C118's invariance check uses *sorted* unique units so IDs are stable. Insertion order on W1 with seed `[11801, 3]` does **not** recover the frozen step-1 ℓ; sorted order recovers it exactly. **Choice: sorted unique units of the observed text, frozen for that text's shuffles and plants.**

2. **Which EM parameters are frozen.** C111's loop reports the E-step ℓ and then performs an M-step before the tolerance check, so the returned (A, π, emissions) are one M-step ahead of the reported ℓ. Section 6 identifies the zero point of S with that reported best ℓ, and A1 requires ℓ(B = reset to π) = the word-row ℓ at the frozen parameters (diff 0.0). **Choice: freeze the pre-M-step parameters that generated the reported loop ℓ.** Recomputed word-row ℓ then equals loop ℓ, and A1 is 0.

## Other choices (prose-supported, or a documented default)

3. **N-LINE.** Implemented as C118 `nline` / section 4: lines with L ≥ 5 have their middle L−2 words permuted by `Generator.permutation`; L ≤ 4 are copied unchanged; first and last words stay put. RNG is consumed only on movable lines, in line order.

4. **Step-1 seeds (main run).** R4: restart *i* of text *t* uses `SeedSequence([11802, hash_name(t), 1000, i])`, independent streams. (The precheck self-check used the closed sequential stream `[11801, 3]`, as declared.)

5. **B-job seeds.** R4: one generator `default_rng(SeedSequence([11802, hash_name(t), rep]))` draws the N-LINE shuffle if rep > 0, then the RB Dirichlet row starts.

6. **L-BFGS-B.** `scipy.optimize.minimize(..., method='L-BFGS-B', bounds=[(0,1),(0,1)], jac=exact)`. Default scipy stopping; if the two-criterion rule is not met, warm-restart from the end point with fresh L-BFGS memory, ℓ history kept, at most 20 times, as written. No extra `ftol`/`gtol` overrides (defaults kept, because they already recovered the section 6 S table).

7. **KKT projected gradient.** Section 6.1 prints a "max KKT projected gradient", so the threshold 1e-8 is applied to the **max-abs (L^∞)** component of the projected gradient of ℓ (maximization) on [0,1]²: a coordinate at 0 with dℓ/dx ≤ 0, or at 1 with dℓ/dx ≥ 0, is projected to 0. Coordinates within 1e-14 of 0 or 1 are treated as on-bound for the KKT test.

8. **Δℓ window.** "|Δℓ| < 1e-9 nats over the last 5 iterations" is taken as |ℓ_last − ℓ_{last-5}|, with the history spanning warm restarts. A start with fewer than 6 recorded ℓ values cannot meet this criterion and must meet KKT.

9. **Unconstrained gradient G_ij.** "G_ij = ∂ℓ/∂B_ij from the forward-backward pass" is implemented as the independent-entry derivative, finite at bounds: at each word boundary, G += outer(α_end, F_next β) / c_next. Constrained: ∂ℓ/∂B_12 = G_12 − G_11, ∂ℓ/∂B_21 = G_21 − G_22. (If G had been ξ_ij / B_ij this would be undefined at 0, contradicting "ℓ stays finite at an exact bound".)

10. **G-POW plant Bernoulli draws.** For each movable line in W1 order, one `rng.random() < 0.10` from `default_rng(SeedSequence([11802, 0]))`. Non-movable lines do not consume a draw. q = 0.10 as registered.

11. **G-POW chaining ties.** Remaining middle words are scanned in their *current remaining* list, which starts in original middle order; a stricter score replaces, so ties keep the earliest original word. `c(w)` ties use `np.argmax` (state 0 if the two normalised forwards are equal). `c` and `a` are functions of the word type (glyph sequence).

12. **hash_name.** C113 formula, values confirmed against R2.

13. **Text loading.** C115 `strata(..., with_lines=True)` and `devowel_lines` / `E.take` / `nat_texts` / `T.hebrew(..., merge_finals=False)` as named. Glyph = character on controls, `T.units` on the manuscript. Corpora `pg218.txt` and `Gen.xml` were copied from `/workspace/voynich/backup/corpora/` after matching `data/MANIFEST.md` sha prefixes.

14. **W1 text sha.** SHA-256 of `'\n'.join(' '.join(''.join(units) for word in line) for line in lines)` recovers `29df436a…2a2eeb`.

15. **Movable-token share.** Section 4's 78.96% on W1 is the share of *middle* tokens in lines with L ≥ 5 (0.789568…), not the C118 "including fixed ends" figure (~99.36%). 1,021 / 1,040 movable lines matches.

16. **Frozen calib (R11), not re-run.** R1 = 10, CONV_TOL1 = 5.0 nats, RB = 5, CONV_TOLB = 0.001 nats, no flag, taken from the case-file amendment written before any manuscript fit. Seed 11803 was not re-run. I did not open `analysis/C119_frozen.json`.

17. **Bootstrap (11804).** 10,000 resamples with replacement of converged null S; 95% interval = 2.5/97.5 percentiles. Rank CI: `SeedSequence([11804, hash_name(t), 1])`. Quantile q: `[11804, hash_name(t), 2, 100·q]`. CAE-DV mean-rank CI: `[11804, 0]`, resampling the two windows independently. `np.quantile` (linear, default) for null quantiles.

18. **Extension seed 11805.** Used only if a control's bootstrap interval contains a gate edge (R8). Not used otherwise.

19. **Step-1 basin label (ours; not defined in the procedure sections I read).** After aligning each restart's states to the best restart's emission rows, then flipping so π_0 ≥ π_1: *sticky* if both A_ii ≥ 0.5; *alternating* if both off-diagonals ≥ 0.5; *mixed* otherwise. Reported: the best restart's label, how many of the 10 restarts share that label, and how many lie within CONV_TOL1 of the best ℓ. A mixed W1 (one sticky state, one slightly switching) is expected under this rule; the case-file header's "alternating / sticky" wording may use a different cut.

20. **Descriptive items not run.** IT2a, T, tied T, the hash plant, the C117 twin plant, the B-EM cross-check, the entropy table, and the 41×41 grid check (except that A1 is asserted on every observed job). The task asked for observed S, null rank, step-1 basins, and gates G1 / P-NOISE / G-POW, which do not require those extras. G-CANFAIL for G-POW is printed but not required (R7).

21. **P-NOISE ratio.** Sample SD (ddof=1) of S over all RB starts of the observed text vs sample SD of converged null S. If SD_starts = 0, the ratio is reported as null (infinite) and the condition holds if SD_null > 0 (R6).

22. **Percentile rank and p.** As R6: ties |ΔS| ≤ 1e-9; p = (1 + #{converged null S ≥ obs − 1e-9}) / (1 + effective N); rank = (#{S < obs − 1e-9} + 0.5·ties) / effective N.

23. **Secondary-control rank interval.** The 95% bootstrap interval of the percentile rank; a failure of the [0.05, 0.95] rank window makes only that row NOT TESTABLE (section 9.4).

24. **Independence.** `recount.py` does not import `tools/c119_*.py`. Shared loaders and the C111/C117 EM *update* were retyped from the named earlier tools. The official C119 runner was not opened.

25. **L-BFGS-B `gtol`.** scipy 1.18's default `gtol` is 1e-5, coarser than the declared KKT threshold 1e-8. With the defaults, a "converged" L-BFGS-B call often stops with ||proj g|| still above 1e-8, and a warm restart then exits at once with the same point (nit = 0, "NORM OF PROJECTED GRADIENT <= PGTOL"). **Choice: `options=dict(ftol=1e-15, gtol=1e-12, maxiter=15000)`.** The two-criterion rule is unchanged. On a probe (ZL_B2 observed) this moved KKT from 3.85e-8 to 1.14e-13 with ℓ identical to all printed digits. The first, default-gtol checkpoint is kept as `work/checkpoint_default_gtol.jsonl`.

26. **Newton polish after failed starts.** Even with tight `gtol`, some starts sit at the same ℓ as the best (Δℓ = 0 to 1e-11, same S to 1e-15) while ||proj g|| is 1e-5–1e-3, because the maximum is extremely flat / ill-conditioned (x differs at 1e-9, gradient differs a lot). **Choice: if a start still meets neither criterion after L-BFGS + 20 warm restarts, take up to five Newton steps on (B_12, B_21) with a finite-difference Hessian of the exact gradient, rejecting any step that lowers ℓ by more than 1e-12.** Thresholds never change. This typically drives KKT below 1e-8 in one or two steps with unchanged ℓ. A tight-gtol-only checkpoint is kept as `work/checkpoint_tight_gtol.jsonl`.

27. **Four jobs still fail the start-level flag.** After (25)+(26), 636/640 jobs have S_converged. The four that do not (ZL_A nulls 10, 12, 46; ZL_B1 null 56; plus two CAE_V nulls 9, 49 outside the primary family) already have SD(S) across the five starts of 0 or ~1e-15: every start found the same S; fewer than three starts have KKT < 1e-8. They are reported under the strict flag and, separately, under an all-79 reading that uses those already-computed S values. The Holm decision is the same in both readings.
