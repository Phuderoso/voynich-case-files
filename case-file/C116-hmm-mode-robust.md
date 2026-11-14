# C116 — Expedição 116: a bússola de muitas agulhas (F-HMM step 5)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: PRE-REGISTERED 2026-11-13 (~20:45 PT), before any C116 count on the manuscript.** No C116 fit has been run on any text when
this file was committed. The design adopts Kryptos's review of 2026-11-13 ~20:03 PT.

## Question

C115 found that the best-of-3 2-state HMM used in C113–C115 lands in different solution *modes* (sticky SW ≈ 0.10, slot-like ≈ 0.20,
alternating ≈ 0.89) depending on the exact lines, so its switch rate SW and the D = SW − null-mean sizes are not interpretable, and the
C113/C114 p-values are provisional. **When every text gets 30 EM restarts and we compare the best sticky solution with the best
non-sticky one, is the sticky solution favoured in the manuscript more than in slot-shuffled versions of the same text?**

## Data

As C115: `data/ZL3b-n.txt` (sha256 prefix `bf5b6d4ac1e3a51b`) strata A (10,005 tokens), B1 (10,007), B2 (10,004), built by
`tools/c115_hmm_switch_currier.py` `strata` (pages by `$L`, paragraph lines, folio order, whole lines). `data/IT2a-n.txt`
(`7f27a8b0feed8f6d`) A/B1/B2, observed only (descriptive). Controls: devowelled Latin Caesar, 10,008 glyph-word tokens (C115 `devowel_tokens`).

## Instrument (Kryptos's review, adopted in full)

- Per text, **30 restarts** of C111 `fit_hmm` (EM, unchanged: 150 iterations max, relative tolerance 1e-6, glyph units). Each restart
  gives its log-likelihood ℓ_r and SW_r = Σ_i occ_i (1 − A_ii) (the C113 formula).
- **Modes fixed in advance on SW**: sticky SW < 0.15; slot 0.15 ≤ SW ≤ 0.5; alternating SW > 0.5. Checked on controls only (G-MODE).
- **Statistic ΔL** = (max ℓ over sticky restarts − max ℓ over non-sticky restarts) / number of glyph tokens.
  ΔL = −∞ if no restart is sticky; +∞ if all are. The ML SW (SW of the best restart overall) and the sticky-restart fraction are
  **descriptive only**.
- **Convergence (G-CONV)**: the best ℓ must be reached, within 1.0 nat, by ≥ 3 of the 30 restarts — on the observed text and on every
  null replicate. Unconverged null replicates are excluded from the null and counted. A stratum is NOT TESTABLE if its observed text is
  unconverged or more than 10 % of its null replicates are. (Kryptos's note on unconverged replicates is implemented this way; the
  exclusion count is printed.)

## Null, test and decision rule

Null N-SLOT (C109 `shuffle_slot`, the C113/C115 null) with all 30 restarts re-run on each replicate. One-sided toward *sticky favoured*:
p = (1 + #{converged null ΔL ≥ observed ΔL}) / (1 + #converged null). NNULL = 79 per primary stratum (floor 0.0125), Holm over the
3 primary strata (ZL3b A, B1, B2), α = 0.05, m = 3 fixed (a not-testable stratum enters as p = 1).

- **STICKY FAVOURED in X**: stratum X passes Holm. C113's stickiness then survives a mode-robust re-test in X.
- **NOT SUPPORTED**: gates pass and no testable stratum passes Holm. C113/C114's "stickier than slots" is then withdrawn for these
  strata by a correction addendum.
- **NOT TESTABLE**: a gate fails, or all three strata fail G-CONV.

## Gates

- **G-POW**: devowelled Latin Caesar with the C114 twin-alphabet plant (q 0.20, rng `SeedSequence([11787, 0])`), NNULL 59, must reach
  p ≤ 0.05/3 (floor 1/60).
- **G-FPR**: the same Caesar text unplanted, NNULL 59, must *not* reach p ≤ 0.05/3.
- **G-MODE**: fewer than 5 % of all control restarts (G-POW + G-FPR, observed and null, 3,600 fits) may lie within 0.02 of a boundary
  (0.15 or 0.5); otherwise the mode boundaries are ill-posed and the run is NOT TESTABLE.
- Kryptos's cycle-200 blind-spot check: ΔL is a continuous difference, not a low count, so it can fail in both directions; the number of
  ±∞ replicates is printed per text so a saturated null is visible.

## Compute plan (disclosed in advance)

363 jobs × 30 fits ≈ 1.5 s per fit on 8 cores ≈ 35 min in total, beyond one cycle's budget. The tool keeps a resumable checkpoint
(`analysis/C116_checkpoint.jsonl`, per-job seeds, so a resumed run is identical to an uninterrupted one). Each cycle runs
`timeout 600 python3 tools/c116_hmm_mode_robust.py run` once (soft stop at 520 s); gates are computed first. **No verdict, and no
look at any manuscript p-value, before every job is in the checkpoint**; partial checkpoints are published as artefacts only.
`status` reports progress without computing statistics.

Tool: `tools/c116_hmm_mode_robust.py`. Seed **11787**; next free Voynich seed **11788**.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
