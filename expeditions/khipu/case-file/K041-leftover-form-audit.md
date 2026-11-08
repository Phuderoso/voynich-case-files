# K041 · Form-audit of the K040 leftover 23 whole-group-sum hits (README line 2)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registration** (written and to be pushed before any K041 form statistic is computed).

## Why
K040 supported a leftover excess of whole-group totals after holding out KH0359/UR119 and KH0405/UR166: G = 23 against a null mean of 14.1067 (p = 0.0162), calibrated (FPR 0.05) and powered at leftover size (m = 9 power 0.74). The individual BH scan found no additional khipu (H2 not supported; 4-plant power 0.94), so the leftover is diffuse: many khipus contribute a single hit. That classifies the *count*, not the *shape*. UR119 itself is a repeated record layout — four totals in a row, each adding the six-cord group that follows. K041 asks whether the leftover 23 hits share a layout (side, group length, singleton-total) more than chance hits would, or whether they are a mixed bag.

This is still the same OKR extract and the same hit definition as K025/K040. It is **not an independent replication** of the leftover count. It is a pre-registered form audit of the already-published 23.

## Data (fixed; identical to K040)
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`,
verified before the run; the tool stops if the hash differs). Level-1 pendants, `DUPLICATE_FLAG` dropped.
Groups = runs of consecutive pendants sharing `CLUSTER_ID`. Eligible and holdout filters copied from K040:
at least 4 groups, at least one candidate adjacent pair, at least one pendant with value ≥ 10; discovery
pair KH0359 and KH0405 held out of every test. Eligible must be 369 and holdout 367. Observed holdout G
(distinct pendants that are whole-group sums) must equal K040/K025's published leftover of 23, or the
cycle is excluded (implementation drift).

## Hit and form (fixed in advance)
A **whole-group sum** is the K025/K040 definition: a pendant with value ≥ 10 that equals the sum of
**all** pendants of the group immediately to its right or immediately to its left, where that group
has ≥ 2 cords, at least 2 of them nonzero, and the pendant is not itself in that group.

A **matching pair** is one such (pendant, neighbouring group). G counts distinct pendants; a pendant
that matches both sides contributes two matching pairs (disclosed as `n_both`) and two form records.
Form tests use the list of matching pairs.

For each matching pair `(i, s, e)` from K040's `prep` (`i` = pendant index, `[s, e)` = group):
- **side** = `L` if `i < s` (total immediately before the group; UR119's "total in front"), else `R`
  (total immediately after the group).
- **group_len** = `e - s` (raw, not binned).
- **singleton_total** = the total pendant's own `CLUSTER_ID` run has length 1 (a lone total sitting
  next to a multi-cord group).

A **layout key** is the pair `(side, group_len)`. Singleton-total is tested separately (H2), so it is
not folded into the key.

## Statistics (computed on the concatenated holdout matching pairs)
Let `n` be the number of matching pairs (may exceed 23 if any pendant matches both sides).
- **H1 (primary, one-sided):** layout concentration. `π` = (maximum count of any single layout key) / `n`
  (`π` = 0 if `n` = 0). Higher `π` means more of the leftover shares one (side, group_len) shape.
- **H2 (secondary, one-sided):** singleton-total share. `q` = (count of matching pairs with
  `singleton_total`) / `n` (`q` = 0 if `n` = 0). UR119's totals sit as their own cluster beside the
  summed group; a high `q` means the leftover shares that part of the form even if group lengths vary.
- **H3 (secondary, two-sided):** side balance. `r` = (count of `L` pairs) / `n` (`r` = 0.5 if `n` = 0,
  so an empty catalogue is not treated as extreme). Two-sided against the permutation null of `r`.

## Null
Within-khipu permutation of pendant values (K001's N1; group sizes and positions stay put), independently
across holdout khipus, R = 10 000, seed 4141. Each replicate yields a catalogue of chance matching pairs
and the triple `(π, q, r)`. One-sided p = `(1 + #{null ≥ obs}) / (1 + R)`. Two-sided p for H3 =
`min(1, 2 * min(p_upper, p_lower))`, where `p_upper = (1 + #{null r ≥ obs r}) / (1 + R)` and
`p_lower` is the symmetric lower tail. Bonferroni α = 0.05 / 3 ≈ 0.01667 for all three decisions.

The layout of every *candidate* pair is fixed by cluster structure; only which candidates become hits
depends on values. Comparing observed forms to the forms of permutation-null hits therefore folds in
the fact that short groups match by chance more easily than long ones. Using the *share* `π` (not the
raw modal count) avoids crediting the leftover with concentration just because it has 23 hits against
a null mean of about 14.

## Controls
- **Calibration (seed 4142, N = 200):** one shuffled copy of every holdout khipu, scored against the
  stored null bank of `(π, q, r)`. Per-test FPR = share of those copies with p ≤ α_Bonferroni.
  Gate passes at ≤ 0.08 (same bar as K034/K037/K040).
- **Power (seed 4143, N = 200, m = 9):** start from a fresh within-khipu permutation of the whole
  holdout (so no residual real structure), then plant 9 disjoint whole-group sums of a pre-registered
  form (K025/K040 plant: an adjacent eligible group is given a total ≥ 10 on a neighbouring pendant).
  Residual chance hits are left in place, matching the real leftover (about 9 extras on top of about
  14 chance hits). A replicate is a hit if that hypothesis's p ≤ α_Bonferroni against the stored null
  bank. Replicates that cannot place 9 disjoint plants of the required form are redrawn (cap 5 × N);
  the rate is used only if at least 30 replicates succeed.
  - H1 plant: 9 pairs sharing one layout key — the `(side, group_len)` with the most disjoint
    plantable pairs in the holdout (structure-only; disclosed). This asks whether 9 extra copies of
    one layout would have been readable, not whether we can plant UR119's exact six-cord form.
  - H2 plant: 9 pairs with `singleton_total`.
  - H3 plant: 9 pairs with side `L` (UR119's "total in front").
- **Descriptive catalogue (not a test):** every observed matching pair with OKR id, investigator
  number, cord ordinal, value, side, group_len, singleton_total. Also `n_pairs`, `n_both`, and
  whether the two hits on KH0424/UR186 (K040's closest name, G = 2, reported descriptively there)
  share a layout key.

## Seeds and wall
Nulls seed **4141**, calibration **4142**, power **4143** (distinct from K031–K040: 3130–4042).
WALL = 520 s inside the tool; outer `timeout 560`. `--smoke` keeps the full eligible set but uses
R = 200, N = 10 (syntax check; output `analysis/k041_smoke.json`, not used for decisions).
Checkpoint every 20 khipus to `analysis/k041_checkpoint.json`. Code: `tools/k041_leftover_form_audit.py`.

## Decision rules (written before the run)
1. **Excluded** if the database hash differs, `analysis/k025_results.json` cannot be read, the
   discovery pair is missing, the eligible count is not 369 or the holdout count is not 367, or the
   observed holdout G (distinct pendants) is not 23.
2. **Hi excluded** if that test's calibration FPR > 0.08.
3. **Hi not testable** if that test's m = 9 plant power is below 0.5 (n ≥ 30 required), or if
   calibration or power is cut by the wall before finishing.
4. **Hi supported** if p_i ≤ 0.05/3 and rules 2–3 do not fire.
5. **Hi not supported** if p_i > 0.05/3 and the m = 9 plant power is ≥ 0.5.
6. **Reading.** If at least one of H1–H3 is supported, the leftover shares that shape (concentration,
   singleton-totals, and/or a side bias). If all three are not supported, the leftover is a **mixed
   bag**: a calibrated count excess whose hits do not repeat one layout, do not prefer singleton
   totals, and do not prefer one side, beyond what chance hits already do. Mixed outcomes are
   reported as such (e.g. singleton-totals yes, concentration no).
7. Negatives published. No decipherment is claimed. A supported H1 means "the leftover matching pairs
   concentrate on one (side, group_len) more than permutation-null hits", never "this is another
   UR119" and never "independently replicated". The catalogue is descriptive and is not used to
   promote a fourth test.

## Output
`analysis/k041_results.json`: design, consistency with K040/K025, observed catalogue and
`(π, q, r)`, null summaries, calibration, power, verdicts, secs. Log: `analysis/k041_run.log`.

## No claims
No decipherment is claimed. K041 only classifies the shape of the leftover 23 already counted by
K040. UR119's own repeated six-cord layout remains the one already described by K025 and counted
by the Khipu Field Guide.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
