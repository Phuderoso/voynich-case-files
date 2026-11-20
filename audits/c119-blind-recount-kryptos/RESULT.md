# RESULT.md — Independent blind recount of Voynich C119

Recount by Kryptos · Pesquisadora, 2026-11-20, America/Vancouver (PT, UTC-7).
Source: https://github.com/Phuderoso/voynich-case-files at `40b032197b13a7db964c39007b6ecc516873b5f8` (requested `40b0321`), cloned read-only to `/workspace/c119-blind-recount/repo`. Nothing was committed or pushed.

**Independence.** The procedure was reimplemented from the case-file prose (sections 1–10 and the run amendments; Results, lines 323–382, were not read). The official runner `tools/c119_hmm_line_stream.py` and the C119 precheck tools were **not** opened or imported. Shared loaders (C003, C047, C049, C051, C108, C115) and the C111/C117 EM *update* were retyped from those earlier tools. Code: `/workspace/c119-blind-recount/recount.py`.

**Seeds (as declared, no new seed).** 11802 main run; 11804 bootstrap (B = 10,000). Frozen calib values R1 = 10, CONV_TOL1 = 5.0 nats, RB = 5, CONV_TOLB = 0.001 nats were taken from case-file amendment R11; seed 11803 was not re-run. Seed 11805 was not needed (CAE-DV mean-rank CI did not contain a gate edge). 11809 was not used.

**Blinding.** See `LEAKS.md`. The git checkout printed the commit subject, which already contained the published C119 numbers, and the case-file header states the verdict. I did not open `C119_results.json`, logs, gate files, or the Results section. Section 6 control numbers (CAE-DV W1 only) were used solely to resolve two under-specified instrument choices (symbol-ID order; which EM parameters are frozen); after those fixes the W1 precheck table in 6.1 is recovered to the printed precision. I did not tune anything to the leaked manuscript figures. Agreement with them, where it occurs, is reported after the run.

**Fitter self-check (CAE-DV W1, seeds 11801 / [11801, 3] / [11801, 5], closed precheck).** best ℓ = −79,623.32605161758 (declared −79,623.3260516); A = [[0.425336, 0.574664], [0.005301, 0.994699]] (declared 0.4253, 0.5747, 0.0053, 0.9947); π = [0.991582, 0.008418] (declared 0.9916, 0.0084); 0/10 restarts hit the 500 cap; A1 = 0. Observed and N-LINE reps 1–3: S = 7.27976469e-5, 3.04132652e-5, 2.42159114e-5, 1.19492543e-4; fitted observed ℓ = −79,622.673202; B_11, B_22 as in the 6.1 table (1 and 0.012695; 0.990581 and 0; 1 and 0.003407; 1 and 0.017634).

**A0 / inputs.** `data/ZL3b-n.txt` sha256 `bf5b6d4ac1e3a51b…09beccafc`. W1 text sha `29df436a…5a2a2eeb`, 10,008 words, 1,040 lines, 32,824 glyphs, 8,968 boundaries, 1,021 movable lines, movable-middle share 0.789568 (78.96%). W2: 10,007 words, 1,056 lines, first source-line index 1,040, 0 lines textually equal to a W1 line. CAE-V 10,005 / 1,022; HEB-ABJ 10,016 / 758. ZL3b A/B1/B2 = 10,005 / 10,007 / 10,004 tokens. Caesar and Genesis corpora were copied from `/workspace/voynich/backup/corpora/` after matching `data/MANIFEST.md` sha prefixes (`84ac8411…cb2f659c`, `0526e5c9…68d86449`).

---

## Gates (controls only)

All of G1, P-NOISE and G-POW **pass**. No 11805 extension (not borderline).

| gate | result | detail |
|---|---|---|
| **G1** (CAE-DV W1+W2) | **PASS** | Both windows 79/79 nulls converged, obs converged, effective N = 79, G-CANFAIL yes. W1 rank **0.860759** p = 0.15; W2 rank **0.810127** p = 0.20. Mean rank **0.835443**. Bootstrap 95% CI of the mean rank (seed 11804, `[11804, 0]`): **[0.778481, 0.892405]**. Neither window has p ≤ 0.05/3. |
| **P-NOISE** | **PASS** | W1: SD(S)_starts = 0, SD(S)_null = 1.899e-5 (ratio infinite, condition holds). W2: SD(S)_starts = 8.90e-16, SD(S)_null = 2.623e-6. |
| **G-POW** (aligned plant, q = 0.10, `[11802, 0]`) | **PASS** | 100 movable lines planted. Observed S = **2.47331943e-4**, null mean 1.7083e-5, **z = 10.697**, **p = 0.0125** (floor 1/80), rank = 1.00, effective N = 79, P-NOISE ok, G-CANFAIL yes (printed, not required). |

Secondary (non-blocking):

- **CAE-V:** S = 2.61871619e-4, rank **0.9870** (77 converged nulls; two jobs, reps 9 and 49, fail the start-level KKT flag). Counting all 79 already-computed S values: rank **0.987342**, p = 0.025, z = 3.516. The row is above its null. Rank CI under the strict 77: see `work/summary.json`.
- **HEB-ABJ:** S = 1.35322297e-4, rank = 1.00, p = 0.0125, z ~ 6.16e11 on 79/79 nulls. The null is degenerate (near-zero null SD relative to the observed S). Recorded as a finding about the null, as the case file provided for.

---

## Primary strata (Holm m = 3, α = 0.05)

Two readings are given. **Strict** uses only jobs whose S_converged flag is true (≥ 3 of 5 starts meet KKT < 1e-8 or Δℓ, and lie within CONV_TOLB of the best). **All-79** also counts the four primary jobs (ZL_A nulls 10, 12, 46; ZL_B1 null 56) whose five starts already agreed on S to 1e-15 but fewer than three starts satisfied the KKT flag (see AMBIGUITIES 27). Observed S is identical in both readings. The Holm decision is the same in both: B1 and B2 pass, A does not. Under all-79, p_cons = p_lib for every primary stratum.

| stratum | observed S | B_11, B_22 | strict p (rank) | strict z, null mean, N_eff | all-79 p (rank) | all-79 z, null mean | step-1 basin |
|---|---|---|---|---|---|---|---|
| **ZL_A** | **1.94295866e-4** | 0.007083, 0.994153 | 0.7922 (0.2105), N=76 | z = −0.802, mean 2.930e-4 | **0.7875** (0.2152) | z = −0.815, mean 2.938e-4 | **sticky**, 7/10 same label, **6/10** within 5 nats of the best ℓ |
| **ZL_B1** | **2.20840119e-2** | 0.434998, 0.328531 | 0.012658 (1.00), N=78 | z = 39.334, mean 2.257e-3 | **0.0125** (1.00) | z = **39.509**, mean **2.260e-3** | **alternating**, **3/10** same label, **3/10** within 5 nats |
| **ZL_B2** | **2.49230280e-4** | 0.988176, 0 (exact) | **0.0125** (1.00), N=79 | z = **8.462**, mean **1.00785e-5** | same | same | **mixed** under the 0.5-cut (A_00 = 0.49796 after alignment), 4/10 mixed + 3/10 sticky + 3/10 alternating; **7/10** within 5 nats (4 mixed, 3 sticky) |

A1 on every observed job is 0 or 2.9e-11 nats (tolerance 1e-6).

**Holm (strict, p_lib):** B2 p = 0.0125 ≤ 0.05/3, pass; B1 p = 0.012658 ≤ 0.05/2, pass; A p = 0.792, fail. p_cons for B1 is (1+0+1)/80 = 0.025, which still meets 0.05/2, so B1 is **not** convergence-sensitive. Under all-79, B1 p = p_cons = 0.0125.

**Verdict (both readings):** **BOUNDARY STATE IN WORD ORDER in ZL_B1 + ZL_B2**, not in ZL_A. This is not a decipherment and does not identify a language.

### Step-1 basins (definition in AMBIGUITIES 19)

States of each restart are aligned to the best restart's emission rows, then flipped so π_0 ≥ π_1. *sticky*: both A_ii ≥ 0.5; *alternating*: both off-diagonals ≥ 0.5; *mixed*: otherwise.

- **A** best A (unflipped as stored) ≈ [[0.9828, 0.0172], [0.1226, 0.8774]], sticky. Six of ten restarts are within 5 nats of the best and all six are sticky; the other three restarts are an alternating basin, more than 5 nats worse.
- **B1** best A ≈ [[0.1875, 0.8125], [0.9836, 0.0164]], alternating. Exactly three of ten restarts land in that basin, and those three are the ones within 5 nats of the best (restarts 5, 8, 9). The other seven are sticky (3) or mixed (4) and are not within 5 nats.
- **B2** best A ≈ [[0.49796, 0.50204], [0.00060, 0.99940]], **mixed** only because A_00 sits just below 0.5. It is a knife-edge: one state is essentially absorbing, the other is a fair coin. A coarser "has an absorbing state" reading would call it sticky. Seven of ten restarts are within 5 nats of the best (four mixed, three sticky).

---

## What this does and does not say

- Gates 1, P-NOISE and 3 pass, so the instrument can see state-aligned word order when it is planted (G-POW z = 10.7 at the p floor). Passing G-POW says nothing about whether the manuscript uses that order.
- In Currier B1 and B2 the manuscript's word order inside lines gives a higher S than N-LINE shuffles of the same lines; in Currier A it does not (A's observed S is slightly *below* its null mean).
- Both B passes sit at or next to the p floor 1/80. B2 is exactly at the floor with all 79 nulls; B1 is at the floor once its one KKT-flagged null (rep 56, S = 2.526e-3, well below observed) is counted.
- S depends on the step-1 basin: B1's passing value is two orders of magnitude larger than B2's, and B1 is the only primary stratum whose winning restart is alternating.
- CAE-V (voweled Latin) is also above its null (rank 0.987). HEB-ABJ's null is degenerate. Neither is in the Holm family.
- This is not a decipherment.

---

## Files

| path | role |
|---|---|
| `/workspace/c119-blind-recount/recount.py` | Independent implementation |
| `/workspace/c119-blind-recount/FROZEN.txt` | Files opened before any recount computation |
| `/workspace/c119-blind-recount/LEAKS.md` | Unblinding declaration |
| `/workspace/c119-blind-recount/AMBIGUITIES.md` | Under-specified points and choices |
| `/workspace/c119-blind-recount/RESULT.md` | This file |
| `/workspace/c119-blind-recount/work/checkpoint.jsonl` | 640 B-jobs (final, with tight gtol + Newton polish) |
| `/workspace/c119-blind-recount/work/summary.json` | Gates, Holm, bootstrap (strict flags) |
| `/workspace/c119-blind-recount/work/step1_*.json` | Frozen step-1 fits |
| `/workspace/c119-blind-recount/work/precheck.json` | W1 section-6 self-check |
| `/workspace/c119-blind-recount/work/checkpoint_default_gtol.jsonl` | Earlier B-jobs, scipy default gtol (S already agreed; flags weaker) |
| `/workspace/c119-blind-recount/work/checkpoint_tight_gtol.jsonl` | Tight gtol, no Newton polish |

SHA256 of the main work products is in `SHA256SUMS`.
