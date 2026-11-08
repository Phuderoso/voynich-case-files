# K049 · Cross-khipu colour agreement on the five K010 value-block pairs (README lines 3 and 6)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registered** (this file and `tools/k049_block_colour_agreement.py` are pushed before any
pair-level colour agreement number is computed; only value-side consistency counts, listed below,
were checked first).

## Why
K005–K010 mapped long identical value runs between different khipus. K010, with a steadier
threshold, confirmed **five** `significant_S` pairs — the five K006/K009 survivors — all selected
on **values only**. Those pairs are a different correspondence family from the K018/K019
group-leader alignments. K046 already tested colour on the three K019 pairs (one supported, one
supported but fragile, one degenerate). K047 and K048 then mapped physical-feature equality and
rare-label concordance on that same trio. Line 6's colour and physical-feature questions on the
K019 pairs are now mapped.

A colour-code *association* test on the K046 cross-tabs would be same-data and must stay
exploratory; it is **not** this cycle. This cycle instead asks the colour-agreement question on
the other confirmed cross-khipu value correspondences: the five K010 value-block pairs, which
were never selected on colour. Colour is therefore a fresh, value-independent look at those
blocks.

**Named pairs** (from `analysis/k010_results.json` `significant_S`; the K005 artefact
KH0277·KH0449 / UR047·UR211 is **not** included):

1. KH0362·KH0049 (UR122 · AS038/HP036), block_len 12,
   block `[1856, 2578, 89, 974, 1146, 1095, 849, 790, 6485, 875, 1348, 754]`
2. KH0128·KH0137 (UR1114 · UR1123, Berlin), block_len 10,
   block `[40, 9, 57, 30, 56, 80, 21, 8, 22, 12]`
3. KH0140·KH0483 (AS125 · UR247) — the unflagged double recording (museum numbers VA42670 vs
   VA 42610), block_len 12,
   block `[1517, 2373, 6291, 3495, 4213, 6323, 4122, 2220, 4377, 1292, 1162, 2393]`
4. KH0304·KH0303 (UR067 · UR066, Puruchuco), block_len 7,
   block `[22, 3, 9, 2, 156, 13, 12]`
5. KH0305·KH0301 (UR068 · UR064, Puruchuco), block_len 8 after R5 masking (K005 had 10),
   block `[8, 1, 3, 1, 57, 5, 6, 2]`

The K019 trio is **not** added (already tested in K046). The unconfirmed KH0240·KH0496 lead is
**not** added. The K020 pair KH0502·KH0514 uses a different alignment family (weighted leaders,
then within-group LCS) and is left for a later cycle.

## Question
On the five value-block correspondences that K010 confirmed, do the cords that share the published
identical value block also carry the **same colour code** more often than a within-khipu shuffle
of B's colours?

## Data
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`;
read-only URI; the tool stops if the hash differs). Not committed.

## Alignment (values only, selected on values, never on colour)
1. Rebuild each khipu's pendant sequence with the same rule as K009/K010
   (`tools/k010_steadier_threshold.py`): level-1 pendant values in stored `CORD_ORDINAL` order;
   R5 multi-number cords (K007 definition, same code as K010) zeroed in place, not dropped.
   Khipus with `DUPLICATE_FLAG = 1` are omitted from the sequence table, as in K010.
2. For each named pair, locate the published K010 `block` as a contiguous subsequence on each
   side. Deterministic tie-break: first (leftmost) occurrence on A, then on B.
3. **Consistency gate (values only):** reconstructed `block` and `block_len` must equal the
   published K010 arrays and lengths above, or that pair (or the whole cycle, if the sequence
   builder itself is wrong) is **excluded** as implementation drift. Start indices are recorded.
   No colour may be read before this file and the tool are pushed.
4. **Analysis unit:** one aligned position in that value block (n = `block_len`), then drop units
   with `no_colour` on either side from count and denominator, with reasons counted.

Checked before this push, values only (no colour was read). The published block was recovered
exactly once on each side of every pair:

| Pair | start A / B | reconstructed `block_len` | CLUSTER_ID groups (A / B) |
|---|---|---|---|
| KH0362 · KH0049 | 46 / 82 | 12 | 2 / 2 |
| KH0128 · KH0137 | 39 / 40 | 10 | 1 / 1 |
| KH0140 · KH0483 | 0 / 0 | 12 | 3 / 3 |
| KH0304 · KH0303 | 20 / 20 | 7 | 1 / 2 |
| KH0305 · KH0301 | 41 / 40 | 8 | 2 / 1 |

All five reconstructed arrays equal the published K010 blocks. The sequence builder is therefore
not excluded for drift.

## Colour field and match rule (copied from K046/K045; imported, so they cannot drift)
- Cord colour = K045/K021 field: the `ascher_cord_color` row with the smallest `RANGE_BEG` (ties:
  smallest `color_id`); colour tuple = (non-empty `COLOR_CD_1..5` in stored order, non-empty
  `OPERATOR_1..5` in stored order). A cord with no row, an empty `FULL_COLOR`, or no component is
  `no_colour`; a unit with `no_colour` on either side is **excluded from count and denominator**
  (counts reported by reason).
- **Primary match:** identical operator sequence (`-` is not `:`), identical ordered component
  sequence (Ascher order; no re-sort), `PK` ("unknown Urton color") on either side **never**
  matches, `BY` ≠ `YB` (Ascher Table 5 / OKR: ISCC 79 vs 76).
- **Sensitivity only:** `BY` ≡ `YB` (KFG's cleaning recode). Disclosed, not a verdict.
- The tool imports `colour_match` and the 14-case fixture from
  `tools/k046_colour_agreement.py` so the match function cannot drift from K046.

## Statistic, null, p
- **A** = number of coloured units whose colours match under the primary rule (denominator n
  fixed after `no_colour` exclusions).
- **Null N1 (primary):** permute side B's colour tuples among that pair's n coloured units,
  R = 10 000. This keeps both records' colour frequencies on the analysed units, keeps n fixed,
  and never uses the other khipu's colours.
- p = (1 + #{null ≥ A}) / (R + 1), one-sided (more agreement than frequency-matching chance).
- **α = 0.05 / 5 = 0.01** (Bonferroni over the five named pairs; one primary statistic).
- **N2 (descriptive, not a verdict):** partition the n coloured units by the pair of
  `CLUSTER_ID`s `(clusterA, clusterB)`. If every coloured unit shares one such key (the block is
  a single group on both sides, or the remaining units collapse to one key after `no_colour`
  drops), N2 is **not applicable** (it would be identical to N1). If two or more keys are
  present, permute B's colours only within each key. This asks whether agreement goes beyond
  group-level colour blocks. Reported, not decided on.

## Seeds and budget
N1 **4949**, calibration **4950**, power **4951**, N2 and sensitivities **4952**, copy-all
**4953**. In-tool wall 540 s (the power curve is skipped if 80 % of the wall is used); outer
`timeout 600`. `--smoke` (R = 200, small N) runs only after this push, output
`analysis/k049_smoke.json`, not used for decisions.

## Gates and controls (written before the run)
1. **Match-function fixture** (K046's 14 cases, imported; no data): identical
   plain/barber-pole/mottled/three-part sequences match; `PK` never matches (also inside a
   mottle); `-` ≠ `:`; component order matters; `BY` ≠ `YB` primary and `BY` ≡ `YB` only under
   the sensitivity flag; `no_colour` never matches. The tool **refuses to write results** if any
   case fails.
2. **Copy-all positive control (real structure):** set every B colour := A colour on the real
   units; A must equal the number of units without `PK` on side A and p must be < α (null
   R = 2 000, seed 4953). If not recovered, that pair is **tool excluded**. A degenerate pair
   (rule below) is labelled DEGENERATE rather than tool-excluded, even if copy-all is skipped.
3. **Calibration FPR (seed 4950):** 1 000 fake observations, each a fresh N1 permutation, scored
   against the stored N1 bank; FPR = share with p < α. Gate **≤ 0.08** (expedition bar,
   K034/K040–K042 / K046).
4. **Structural FPR (shift control, no seed):** every cyclic offset k of B's colours along the
   unit order with min(k, n−k) ≥ ⌈0.1 n⌉, scored against the N1 bank. This breaks the
   correspondence but keeps runs and colour blocks. Gate **≤ 0.08** (K046's numeric gate; zero
   false discoveries preferred). If either FPR gate fails, the pair is **tool excluded** and its
   real-data p is not interpreted.
5. **Power (seed 4951):** 200 replicates; base = a random N1 permutation of B's colours (no
   residual real signal); then on a random **25 %** of units (k = round(0.25 n)) set B's colour
   := A's colour; p from a fresh N1 bank of the planted data (R = 2 000). Power = share with
   p < α. Bar **≥ 0.5**. Descriptive curve at f = 0.10, 0.15, 0.25, 0.40 (100 replicates each).
6. **Data hash gate:** the tool stops if `khipu.db` is not SHA-256
   `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`.

## Decision rules (per pair)
1. **Excluded (cycle)** if the hash differs, the fixture fails, or the sequence builder fails the
   consistency gate on any named pair (implementation drift).
2. **DEGENERATE** if there is no colour variation that a shuffle of B could turn into extra
   matches: n = 0 after `no_colour` drops; or the two sides share no colour tuple that matches
   under the primary rule (null identically 0); or side A is monochromatic among the n units; or
   side B is monochromatic among the n units. In each of those cases A is fixed by the colour
   inventories (N1 has max = min). Report n, A, colour counts and the reason. FPR and power are
   skipped (as in K047/K048). Copy-all is still run as a tool check when n ≥ 1, but a degenerate
   pair is not tool-excluded for a copy-all failure caused by a monochromatic inventory.
3. **TOOL EXCLUDED** if the pair is not degenerate and (the copy-all control fails, or
   calibration FPR > 0.08, or shift FPR > 0.08).
4. **SUPPORTED** if p < 0.01 and rules 2–3 do not fire.
5. **NOT TESTABLE** if power at f = 0.25 < 0.5 and p ≥ 0.01 (not a negative).
6. **NOT SUPPORTED** (a real negative at the stated power) if p ≥ 0.01, power ≥ 0.5, and rules
   2–3 do not fire.

Every pair is published, including negatives and not-testable outcomes. No HARKing.

Sensitivities (disclosed, **not** verdicts): `BY` ≡ `YB`; only units whose aligned value ≠ 0
(the published blocks contain no zeros, so this should match the primary set unless a later
edit intervenes); N2 within-group null when applicable.

## Integrity notes
- The pairs and the blocks are K010's; K049 is not a re-test of their values.
- The K019 trio, the KH0240·KH0496 lead, and KH0502·KH0514 are out of scope.
- First colour row only (multi-range cords reduced to their first range, as K021/K045/K046).

## What this cannot decide (confounds named in advance)
- **Recorder effects:** Ascher, Urton and Pereyra may have judged the same fibre differently
  (lighting, chart, fading, code choice). K045 found no independent Urton or Pereyra colour
  dictionary; their records are in Ascher codes in OKR. K046 showed that recorder coding (for
  example `YB` ↔ `AB`) can make equality unreadable across recorders. A negative may be recorder
  disagreement, not a different object; a positive on a cross-recorder pair should be read with
  that confound named. A census of recorder and provenance per side is disclosed, not a verdict.
- **KH0140·KH0483** is already explained from values as a likely double recording (museum
  numbers VA42670 vs VA 42610). Colour agreement on that pair would be additional same-object
  evidence, not a new pair and not a decipherment. Colour alone does not prove same-object
  status.
- A **SUPPORTED** pair means colour-code agreement beyond frequency chance **on the published
  value block**. It does **not** by itself prove "same physical object recorded twice" (a
  faithful copy would also agree).
- A **NOT SUPPORTED** pair does **not** prove different objects.
- No decipherment is claimed.

## Next (depends on the result)
- If any pair is SUPPORTED: state it with the recorder-coding caveat. For KH0140·KH0483, a
  grounded colour addition may be folded into the pending OKR duplicates note as an observation,
  not as a new claim that the cycle did not support.
- If NOT SUPPORTED with power: colour-agreement is not visible on that block under OKR codes;
  recorder effects remain the leading explanation to state, not to test here.
- If DEGENERATE / NOT TESTABLE / TOOL EXCLUDED: say why.
- A later cycle may take the K020 pair KH0502·KH0514 (different alignment family) on the same
  colour-agreement design. The unconfirmed KH0240·KH0496 lead stays a lead.

## Output
`analysis/k049_results.json` (`analysis/k049_checkpoint.json` while running), log
`analysis/k049_run.log`.
Run from `expeditions/khipu/`: `timeout 600 python3 tools/k049_block_colour_agreement.py run`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
