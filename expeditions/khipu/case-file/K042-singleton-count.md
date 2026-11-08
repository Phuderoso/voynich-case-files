# K042 · Does the leftover count excess live in singleton-total pairs? (README line 2)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registered** (written before any K042 decision statistic is computed).

## Why
K040 supported a leftover excess of whole-group totals after holding out KH0359/UR119 and KH0405/UR166: G = 23 against a null mean of 14.1067 (p = 0.0162), calibrated (FPR 0.05) and powered at leftover size (m = 9 power 0.74). The individual BH scan found no additional khipu (H2 not supported). K041 then audited the *shape* of those 23 matching pairs. H2 was supported: 10 of 23 are singleton-totals (q = 0.4348 vs null 0.1248, p = 0.00330; FPR 0.005; m = 9 power 0.975). Layout concentration and side were not testable. That names a form, but it does not say whether the leftover *count* excess itself lives in those singleton-total pairs or is spread across both forms.

K042 locks that split in advance: G restricted to singleton-totals (G_s) and G restricted to the rest (G_ns), each tested against the same within-khipu permutation that K040 used for the unsplit leftover. This is still the same OKR extract and the same 23 pendants. It is **not an independent replication** of K040, and not a new named khipu. It is a pre-registered decomposition of the already-published leftover.

## Data (fixed; identical to K040/K041)
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`,
verified before the run; the tool stops if the hash differs). Level-1 pendants, `DUPLICATE_FLAG` dropped.
Groups = runs of consecutive pendants sharing `CLUSTER_ID`. Eligible and holdout filters copied from K040:
at least 4 groups, at least one candidate adjacent pair, at least one pendant with value ≥ 10; discovery
pair KH0359 and KH0405 held out of every test. Eligible must be 369 and holdout 367. Observed holdout G
(distinct pendants that are whole-group sums) must equal 23, or the cycle is excluded (implementation
drift). Observed G_s (distinct holdout pendants that are singleton-total whole-group sums) must equal
K041's published 10, or the cycle is excluded. Observed G_ns must equal 13 (23 − 10), or excluded.

## Hit and singleton-total (copied from K025/K040/K041)
A **whole-group sum** is a pendant with value ≥ 10 that equals the sum of **all** pendants of the
group immediately to its right or immediately to its left, where that group has ≥ 2 cords, at least
2 of them nonzero, and the pendant is not itself in that group.

**singleton_total** (K041): the total pendant's own `CLUSTER_ID` run has length 1 (a lone total
sitting next to a multi-cord group).

Because K041 found `n_both` = 0, counting distinct pendants matches counting matching pairs. G_s and
G_ns are still defined on distinct pendants (K040's G convention). If a pendant matches both sides,
it is counted once; it is classified as singleton-total iff its own cluster run has length 1 (a
property of the pendant, not of the side). `n_both` is disclosed.

## Hypotheses
- **H1 (primary, one-sided, greater-than).** G_s = number of distinct holdout pendants that are
  singleton-total whole-group sums. Does this count exceed the within-khipu permutation null? This
  asks whether the leftover *count* excess lives in the form K041 supported.
- **H2 (secondary, one-sided, greater-than).** G_ns = number of distinct holdout pendants that are
  whole-group sums but are **not** singleton-totals. Does this count also exceed its null? This asks
  whether leftover excess remains outside that form.

## Null
Within-khipu permutation of pendant values (K001's N1; group sizes and positions stay put),
independently across holdout khipus, R = 10 000, seed 4242 (fresh; distinct from K031–K041 seeds
3130–4143). Each replicate yields `(G_s, G_ns)`. One-sided p = `(1 + #{null ≥ obs}) / (1 + R)`.
Bonferroni α = 0.05 / 2 = 0.025 for both decisions. Code: `tools/k042_singleton_count.py`.

## Controls
- **Calibration (seed 4243, N = 200):** one shuffled copy of every holdout khipu, scored against
  the stored null bank of `(G_s, G_ns)`. Per-test FPR = share of those copies with p ≤ α_Bonferroni.
  Gate passes at ≤ 0.08 (same bar as K034/K037/K040/K041).
- **Power (seed 4244, N = 200, m = 9):** start from a fresh within-khipu permutation of the whole
  holdout (so no residual real structure), then plant 9 disjoint whole-group sums of the required
  form (K025/K040 plant: an adjacent eligible group is given a total ≥ 10 on a neighbouring pendant).
  Residual chance hits stay in place (about 9 extras on top of about 14 chance hits, matching the
  real leftover size). A replicate is a hit if that hypothesis's p ≤ α_Bonferroni against the stored
  null bank. Replicates that cannot place 9 disjoint plants of the required form are redrawn
  (cap 5 × N); the rate is used only if at least 30 replicates succeed.
  - H1 plant: 9 singleton-total whole-group sums.
  - H2 plant: 9 non-singleton-total whole-group sums (the total pendant's own cluster run has
    length ≥ 2).
- **Optional disclosed descriptive (not a fourth test):** list the 10 G_s khipus (already in the
  K041 catalogue) and the null means/sds for G_s and G_ns. G_s + G_ns vs K040's G is reported as a
  consistency check (must be 23).

## Seeds and wall
Nulls seed **4242**, calibration **4243**, power **4244** (distinct from K031–K041: 3130–4143).
WALL = 520 s inside the tool; outer `timeout 560`. `--smoke` keeps the full eligible set but uses
R = 200, N = 10 (syntax check; output `analysis/k042_smoke.json`, not used for decisions).
Checkpoint every 20 khipus to `analysis/k042_checkpoint.json`. Code: `tools/k042_singleton_count.py`.

## Decision rules (written before the run)
1. **Excluded** if the database hash differs, `analysis/k025_results.json` cannot be read, the
   discovery pair is missing, the eligible count is not 369 or the holdout count is not 367, the
   observed holdout G is not 23, the observed G_s is not 10, or the observed G_ns is not 13.
2. **Hi excluded** if that test's calibration FPR > 0.08.
3. **Hi not testable** if that test's m = 9 plant power is below 0.5 (n ≥ 30 required), or if
   calibration or power is cut by the wall before finishing.
4. **Hi supported** if p_i ≤ 0.025 and rules 2–3 do not fire.
5. **Hi not supported** if p_i > 0.025 and the m = 9 plant power is ≥ 0.5.
6. **Reading.**
   - H1 supported and H2 not supported → leftover count excess lives in the singleton-total pairs
     (the form K041 named).
   - Both supported → leftover excess is broader than that form.
   - H1 not supported and H2 supported → leftover excess lives outside singleton-totals (K041's
     share finding does not explain the count).
   - Neither supported (and both powered) → count excess not recovered when split (possible power
     loss from splitting 23 into 10 + 13); say so.
   - Any not-testable arm is reported as such, not as a negative.
7. Same-data caveat: this is a decomposition of the already-published leftover 23, not an
   independent replication of K040 and not a new named khipu. Negatives published. No
   decipherment is claimed. If the wall cuts the run before the nulls finish, the cycle is
   excluded. If nulls finish but calibration or an arm's m = 9 power does not, that arm is not
   testable (partial JSON still published).

## Output
`analysis/k042_results.json`: design, consistency with K040/K041, observed G / G_s / G_ns, null
summaries, calibration, power, verdicts, secs. Log: `analysis/k042_run.log`.

## No claims
No decipherment is claimed. K042 only asks where the leftover count already measured by K040
sits, now that K041 has named the singleton-total form. UR119's own totals remain the ones
already counted by the Khipu Field Guide.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
