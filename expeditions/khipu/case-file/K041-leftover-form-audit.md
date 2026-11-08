# K041 · Form-audit of the K040 leftover 23 whole-group-sum hits (README line 2)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results appended** (pre-registration written and pushed first as `b4dad9e`, before any K041 form statistic was computed).

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


## Results

Run 2026-11-08 03:19 PT (America/Vancouver), after prereg `b4dad9e`. Compute **13.9 s**
(all 367 holdout khipus reached; nulls, calibration and power all finished; `capped` false;
wall 520 s not hit). Smoke (`--smoke`, R = 200, N = 10) ran first in 0.7 s, no crash, not
used for decisions. Output: [`analysis/k041_results.json`](../analysis/k041_results.json),
log [`analysis/k041_run.log`](../analysis/k041_run.log).

### 1. Consistency (rule 1)
Database SHA-256 matches `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`.
K025 secondary n = 369; eligible 369; holdout 367; discovery pair KH0359 and KH0405 both
present; observed holdout G = 23 distinct pendants; matching pairs n = 23; pendants matching
both sides n_both = 0. Rule 1 (excluded) does not apply.

### 2. H1 — layout concentration (primary)
R = 10 000, seed 4141. Bonferroni α = 0.05/3 ≈ 0.01667. Statistic `π` = modal share of any
single `(side, group_len)` key among the 23 matching pairs.

| Quantity | Value |
|---|---|
| Modal key (count) | **(L, 4)** with 4 pairs; **(L, 2)** also has 4 |
| π_obs | **0.1739** (4/23) |
| Null mean (sd) | 0.2705 (0.0782) |
| p (one-sided, greater concentration) | **0.9308** |
| Calibration FPR (N = 200, seed 4142) | 0.01 |
| Power at m = 9 (N = 200, seed 4143) | **0.16** (plant key (L, 3); capacity 466) |

- meets_fpr: yes (0.01 ≤ 0.08)
- meets_power: no (0.16 < 0.5, n = 200)
- **Verdict: not testable** (rule 3).

Observed `π` sits *below* the null mean: the leftover catalogue is at least as mixed as
chance hits of typical size (~14), and the one-sided test for extra concentration is far
from the bar (p = 0.9308). Nine extra copies of the most common plantable layout were not
enough to push `π` over the Bonferroni bar at least half the time, because a smaller null
catalogue inflates the modal share (null mean 0.2705 vs observed 0.1739 at n = 23). No
concentration claim is made either way.

### 3. H2 — singleton-total share (secondary)
| Quantity | Value |
|---|---|
| Singleton-total pairs | **10 / 23** |
| q_obs | **0.4348** |
| Null mean (sd) | 0.1248 (0.0919) |
| p (one-sided) | **0.00330** |
| Calibration FPR | 0.005 |
| Power at m = 9 | **0.975** (capacity 899) |

- meets_fpr: yes (0.005 ≤ 0.08)
- meets_power: yes (0.975 ≥ 0.5, n = 200)
- meets_alpha: yes (0.00330 ≤ 0.01667)
- **Verdict: supported** (rules 2–4).

The leftover matching pairs are singleton-totals — a lone total sitting next to the
multi-cord group it sums, the layout UR119 uses for its four totals — more often than
permutation-null hits are. Chance hits have that form about one time in eight; the leftover
has it about two times in five.

### 4. H3 — side balance (secondary)
| Quantity | Value |
|---|---|
| Left / right | **16 / 7** |
| r_obs (share L) | **0.6957** |
| Null mean (sd) | 0.5006 (0.1349) |
| p (two-sided) | **0.1490** |
| Calibration FPR | 0.025 |
| Power at m = 9 | **0.045** (capacity 2 557) |

- meets_fpr: yes (0.025 ≤ 0.08)
- meets_power: no (0.045 < 0.5, n = 200)
- **Verdict: not testable** (rule 3).

Sixteen of the 23 totals sit in front of the group they sum (UR119's side), but that split
does not meet the two-sided bar, and nine extra left-sided plants on top of the residual
chance hits are not enough to make a side bias readable. No side claim is made.

### 5. Catalogue (descriptive, not a test)
Twelve layout keys appear. Besides the two four-pair keys, (R, 6) appears three times
(including both hits on KH0424/UR186, which share that key and are both singleton-totals:
ordinals 24 and 58, values 75 and 596). No pendant matched both sides.

| Khipu | Investigator | Cord ordinal | Value | Side | Group length | Singleton-total |
|---|---|---|---|---|---|---|
| KH0080 | AS067/MA029 | 116 | 98 | R | 4 | no |
| KH0082 | AS069 | 286 | 18 | L | 7 | yes |
| KH0090 | AS077 | 16 | 10 | L | 4 | no |
| KH0101 | UR1088 | 54 | 14 | L | 4 | no |
| KH0113 | UR1100 | 1 | 259 | L | 6 | yes |
| KH0191 | AS174 | 7 | 16 | L | 2 | no |
| KH0225 | AS207A | 177 | 10 | L | 5 | no |
| KH0235 | AS215 | 12 | 14 | L | 4 | yes |
| KH0246 | UR010 | 91 | 112 | L | 7 | yes |
| KH0267 | UR034 | 25 | 15 | L | 2 | no |
| KH0269 | UR037 | 6 | 14 | L | 9 | no |
| KH0322 | UR086 | 62 | 15 | L | 4 | no |
| KH0323 | UR087 | 7 | 15 | R | 6 | yes |
| KH0406 | UR167 | 4 | 11 | L | 15 | no |
| KH0424 | UR186 | 24 | 75 | R | 6 | yes |
| KH0424 | UR186 | 58 | 596 | R | 6 | yes |
| KH0446 | UR208 | 132 | 80 | R | 5 | no |
| KH0460 | UR222 | 1 | 17 | L | 6 | yes |
| KH0482 | UR246 | 25 | 288 | R | 8 | yes |
| KH0489 | UR253 | 55 | 21 | L | 2 | no |
| KH0509 | UR272 | 163 | 10 | L | 5 | no |
| KH0583 | HP052 | 7 | 40 | L | 2 | yes |
| KH0617 | JC010 | 101 | 30 | R | 11 | no |

### 6. Reading
- **H2 supported:** the leftover shares the singleton-total part of UR119's form.
- H1 and H3 are not testable at leftover-excess size (m = 9) under the pre-registered
  shares, so this cycle does not decide whether one `(side, group_len)` repeats or whether
  totals prefer one side.
- Same-data caveat stands (the 23 were already counted by K040). No new named khipu, and
  no decipherment. The Field Guide already counts UR119's own totals; K041 only classifies
  the leftover's shape.

### Next
Proposed for K042: a pre-registered holdout test of whether the leftover *count* excess
lives in the singleton-total pairs (G restricted to singleton-totals, versus the same
within-khipu permutation), now that H2 has named that form — or line 8 (still low priority).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
