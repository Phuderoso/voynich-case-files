# K049 · Cross-khipu colour agreement on the five K010 value-block pairs (README lines 3 and 6)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results appended** (pre-registration written and pushed with the tool as `a1d1fcf` before any
pair-colour agreement number was computed; only value-side consistency counts, listed below, were
checked first).

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


---

## Results (2026-11-08, run ~07:40 PT, America/Vancouver)

Run after the prereg was published as `a1d1fcf` (connector `push_files`; `git push` had no
credentials; local clone aligned with `git pull --ff-only`). A one-line census-dict crash
(duplicate `okr` keyword when folding provenance metadata) was fixed after that commit and before
the run; it did not change the pre-registered statistic, null, gates or seeds. Smoke (`--smoke`,
R = 200) ran first at 07:40 PT, 0.5 s, no crash; not used for decisions and not committed. Full run
**1.0 s** wall (nothing was cut by the wall; the power curve finished). Output
[`analysis/k049_results.json`](../analysis/k049_results.json), log
[`analysis/k049_run.log`](../analysis/k049_run.log).

### Gates (cycle-level)
- DB hash matches; **fixture 14/14 passed**; **K010 consistency passed** (starts 46/82, 39/40,
  0/0, 20/20, 41/40; every reconstructed block equals the published array).
- **Excluded units: 0** in all five pairs (every aligned cord has a usable first colour row;
  n = 12, 10, 12, 7, 8).

### Primary statistic (N1, R = 10 000, seed 4949; α = 0.01)

| Pair | Systems | n | A (matches / n) | Null mean ± sd · q95 · max | p | Power f=0.25 | Copy-all | Cal / shift FPR | **Verdict** |
|---|---|---|---|---|---|---|---|---|---|
| KH0362 · KH0049 | UR · AS/HP | 12 | 6 / 12 | 5.50 ± 0.50 · 6 · 6 | 0.5002 | 0.00 | **failed** (A=12, p 0.0780) | 0 / 0 | **TOOL EXCLUDED** |
| KH0128 · KH0137 | UR · UR | 10 | 0 / 10 | — | — | — | skipped (p 1.00; all-same after copy) | — | **DEGENERATE** (no shared matching colour: `HB` vs `EB`) |
| KH0140 · KH0483 | AS · UR | 12 | 12 / 12 | — | — | — | skipped (p 1.00; A fixed at n) | — | **DEGENERATE** (A monochromatic: both sides all `W`) |
| KH0304 · KH0303 | UR · UR | 7 | 3 / 7 | 0.85 ± 0.77 · 2 · 3 | 0.0173 | 0.065 | recovered (A=7, p 0.00100) | 0 / 0 | **NOT TESTABLE** |
| KH0305 · KH0301 | UR · UR | 8 | 4 / 8 | 1.00 ± 0.89 · 3 · 4 | 0.00470 | 0.040 | recovered (A=8, p 0.00050) | 0.004 / **0.143** | **TOOL EXCLUDED** |

Power curves (f = 0.10 / 0.15 / 0.25 / 0.40; descriptive) for the three non-degenerate pairs:
KH0362·KH0049 all 0.00; KH0304·KH0303 0.01 / 0.01 / 0.06 / 0.19; KH0305·KH0301 0.00 / 0.01 / 0.01 / 0.10.

### Why the tests look like this
- **KH0362·KH0049 — tool excluded by copy-all, near-chance agreement.** Urton's KH0362 is almost
  monochromatic on the block (11 plain `AB`, 1 plain `MB`); Ascher's/Pereyra's KH0049 is 6 `AB`,
  4 mottled `W:KB` and 2 plain `W`. The six matches are the six `AB`=`AB` landings. Because A has
  a single non-`AB` cord, N1 can only produce A = 5 or A = 6 (null mean 5.50, max 6), and the
  observed 6 is the upper point of that two-value distribution (p = 0.500). After copy-all, B
  becomes 11 `AB` + 1 `MB` as well, so identity (A = 12) occurs only when that single `MB` stays
  put: p ≈ 1/12. The observed copy-all p was 0.0780, above α = 0.01, so the pre-registered gate
  fired — the same mechanical 1/n limit K047 and K048 documented on narrow margins. The 25 %
  plant (k = 3) and the whole descriptive curve stay at power 0.00: Bonferroni α = 0.01 sits
  below what this inventory can reach. Cross-recorder (UR vs AS/HP) and cross-museum (Göteborg
  vs Lima).
- **KH0128·KH0137 — degenerate, no shared code.** The Berlin pair is monochromatic on each side,
  but not with the same code: all 10 of KH0128 are plain `HB`, all 10 of KH0137 are plain `EB`.
  Equality cannot score (A is identically 0). Both records are filed as Urton (originally Ascher
  AS114 and AS123); this is not the cross-recorder `YB`↔`AB` pattern K046 saw, but two uniform
  and different codes on a shared value run. Copy-all p = 1.00, as expected when B is overwritten
  with a single colour.
- **KH0140·KH0483 — degenerate, complete but untestable agreement.** The unflagged double
  recording is uniformly plain `W` on all 12 cords of both the Ascher record (VA42670) and the
  Urton record (VA 42610). A = 12/12, and A is fixed at 12 under every shuffle of B, so N1 has
  max = min. This is additional same-object-*consistent* colour information, **not** a statistical
  confirmation beyond the colour frequencies, and not a new pair. Colour alone does not prove
  same-object status; the value evidence already explained this pair.
- **KH0304·KH0303 — not testable.** Both Urton, Huaquerones/Puruchuco. A = 3/7 against null mean
  0.85 (q95 = 2, max = 3), p = 0.0173, which does not beat α = 0.01. The three matches are plain
  `W` (values 22 and 156) and plain `AB` (value 13); 3 is also the inventory maximum
  (min(2,2) `W` + min(2,1) `AB`). Copy-all and both FPR gates pass, but power at f = 0.25
  (k = 2) is only 0.065, and the descriptive curve reaches just 0.19 at f = 0.40. A silence — or
  a near-threshold excess — on n = 7 cannot be read at this Bonferroni bar.
- **KH0305·KH0301 — tool excluded by the shift control.** Both Urton, Puruchuco. A = 4/8 against
  null mean 1.00 (q95 = 3, max = 4), p = 0.00470, which would have beaten α = 0.01 if the gates
  had passed. The four matches are `W`, `AB`, `GG` and `W` (values 8, 1, 3, 57); 4 is again the
  inventory maximum. Copy-all recovered (A = 8, p 0.00050) and calibration FPR was 0.004, but
  one of the seven eligible cyclic offsets of B's colours is at least as extreme as the real
  alignment (shift FPR = 1/7 ≈ 0.143 > 0.08; shift p min = 0.00470). The real-data p is therefore
  **not interpreted**. Power at f = 0.25 is 0.040 (curve 0.00 / 0.01 / 0.01 / 0.10), so even
  without the shift gate a 25 % plant would not have been readable.

### Disclosed, not verdicts
- **Recorder / provenance census.** KH0362 (UR122, Nazca, Göteborg 1938.45.0228) · KH0049
  (AS038/HP036, Costa Sur, MNAAHP 3550). KH0128 (UR1114 / orig. AS114, between Ica and Pisco,
  Berlin VA16148) · KH0137 (UR1123 / orig. AS123, Ica, Berlin VA47085). KH0140 (AS125,
  Pachacamac, Berlin VA42670) · KH0483 (UR247, Pachacamac, Berlin VA 42610). KH0304 (UR067,
  Huaquerones / Puruchuco, s/n) · KH0303 (UR066, Huaquerones / Puruchuco, Puruchuco Museum 4a).
  KH0305 (UR068, Puruchuco Museum 2) · KH0301 (UR064, Huaquerones / Puruchuco Museum #3).
- **BY ≡ YB.** No pair uses `BY` or `YB` on the analysed units; the sensitivity is identical to
  the primary (KH0362·KH0049 6/12, p 0.502; KH0304·KH0303 3/7, p 0.0182; KH0305·KH0301 4/8,
  p 0.00570 — the last p is not interpreted, same reason as the primary).
- **Non-zero-value units.** Identical to the primary on every pair (the published blocks contain
  no zeros).
- **N2 (within `(clusterA, clusterB)` key).** Applicable on the three non-degenerate pairs:
  KH0362·KH0049 two keys (8+4), null mean 5.25, p 0.246; KH0304·KH0303 two keys (4+3), null mean
  0.92, p 0.0431; KH0305·KH0301 two keys (4+4), null mean 1.00, p 0.0117 (descriptive; that pair
  is tool-excluded). Not applicable on the two degenerate pairs (each side of KH0128·KH0137 is a
  single cluster; KH0140·KH0483 was not scored under N1).

### Reading
No primary pair is SUPPORTED. Colour on these five value-block correspondences is largely
unreadable at the pre-registered bar: the blocks are short (n = 7–12), several inventories are
monochromatic or nearly so, and Bonferroni α = 0.01 sits at or below the 1/n mechanical floor of
a copy-all or a 25 % plant. Where a number can be written, KH0362·KH0049 agrees at chance
(6/12 vs 5.50) and is tool-excluded by copy-all; KH0128·KH0137 shares no colour code (`HB` vs
`EB`); KH0140·KH0483 is uniformly `W` on both records, consistent with the already-explained
double recording but degenerate under the shuffle; KH0304·KH0303 hits its inventory maximum
(3/7 vs 0.85, p 0.0173) without beating α or the power bar; KH0305·KH0301 would have beaten α
(4/8 vs 1.00, p 0.00470) but failed the shift-control gate, so that p is not a verdict. This
does **not** overturn K010's value correspondences, does not prove same-object or two-copy
status, and does not read a khipu. No decipherment.

### Next (lines 3 and 6)
Colour agreement on the five K010 `significant_S` value blocks is now mapped (not as a blanket
negative — as two degeneracies, one not-testable pair and two tool exclusions). A later cycle
may take the K020 pair KH0502·KH0514 (different alignment family) on the same colour-agreement
design. The unconfirmed KH0240·KH0496 lead stays a lead. A colour code-*association* test on
the K046 cross-tabs remains same-data and must stay labelled exploratory if run.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
