# K050 · Cross-khipu colour agreement on the K020 pair KH0502·KH0514 (README lines 3 and 6)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results appended** (pre-registration written and pushed with the tool as `e7fec23` before any
pair-colour agreement number was computed; only value-side consistency counts, listed below, were
checked first).

## Why
K020's two-stage pipeline (information-weighted group-leader LCS with groups of ≥ 3
cords, then a within-group non-leader cord check) confirmed one pair that was not
already on the K018/K019 list: **KH0502 · KH0514** (UR266 · UR275, Inkawasi; museum
numbers 13829 / 13836-2014). K020 reported W = 123.4, 12 matched groups, V = 13
non-leader LCS cords, and a stage-2 p < 1e-4. The literature audit in K020's addendum
showed that Urton & Chu had already published the pair in their Inkawasi inventory as
"Matches UR 275" (and discussed them in Urton 2017 and Urton & Chu 2019). K020 was a
**blind rediscovery of a published match**, not a new correspondence. This cycle does
not reopen that claim.

K046 tested colour on the three K019 pairs, which use a different alignment family
(group-leader LCS with groups ≥ 5, then within-group LCS). K047 and K048 then mapped
physical-feature equality and rare-label concordance on that same trio. K049 tested
colour on the five K010 `significant_S` value-block pairs (contiguous published
blocks). Line 6's colour question on the K019 and K010 families is now mapped. K049's
"Next" named this step: the same colour-agreement design on the remaining confirmed
correspondence family — the K020 pair — which was never selected on colour.

**Named pair** (from `analysis/k020_results.json` stage 2; already published by Urton
& Chu):

1. KH0502 · KH0514 (UR266 · UR275, Inkawasi, Proyecto Incahuasi 13829 / 13836-2014),
   12 matched groups, V = 13, W = 123.4.

KH0491 · KH0503 (UR255 · UR267A) is **not** added: it passed K020's leader stage and
failed stage 2, so there is no confirmed cord-level alignment to colour. The K019
trio is **not** re-tested (already tested in K046). The five K010 value-block pairs
are **not** re-tested (already tested in K049). A colour-code *association* test on
the K046 cross-tabs would be same-data and must stay exploratory; it is **not** this
cycle.

## Question
On the value correspondence that K020 confirmed (groups ≥ 3, corpus-wide weighted
leader LCS, then within-group non-leader LCS), do the aligned non-leader cords carry
the **same colour code** more often than a within-khipu shuffle of B's colours?

## Data
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`;
read-only URI; the tool stops if the hash differs). Not committed.

## Alignment (values only; K020's family, not K046's and not K049's)
1. Rebuild level-1 pendant sequences with the same rule as K020
   (`tools/k020_two_stage.py`): R5 multi-number cords (K007 definition) zeroed in
   place, not dropped; khipus with `DUPLICATE_FLAG = 1` omitted, as in K020.
2. A **leader group** is a `CLUSTER_ID` run of level-1 pendants with **≥ 3 cords**
   and a positive first value (K020). This is the critical difference versus K046 /
   K019, which required ≥ 5 cords.
3. Information weights WL for the leader alignment are **corpus-wide**, exactly as
   in `tools/k020_two_stage.py` (`allW` / full-corpus leaders): every khipu with at
   least 10 positive pendants contributes its ≥ 3-cord positive leaders; WL[v] =
   −log2(frequency of v / total leaders). Pair-only weights are **not** used: they
   can change which groups match.
4. Leader alignment = K020's information-weighted LCS with the same −1 mismatch
   penalty and the same traceback as `k020_two_stage.py` / `k046_colour_agreement.py`
   `walign` (diagonal when the leaders are equal and the score equals the
   predecessor plus WL; else up if that cell is ≥ left, else left).
5. Units = aligned **non-leader** cords via K046's deterministic `lcs_traceback` on
   the non-leader value sequences of each matched group (same rule as K046
   `build_units`: from the end, take the diagonal when the values are equal and
   `D[i][j] = D[i−1][j−1] + 1`; else move up if `D[i−1][j] ≥ D[i][j−1]`; else
   left). Leaders are **not** in the primary count (they selected the pair).
6. **Consistency gate (values only):** reconstructed matched groups and ΣV must
   equal K020's published **12** and **V = 13**, or the cycle is **excluded** as
   implementation drift. Reconstructed W is recorded as a descriptive check
   (K020 published 123.4); it is **not** a hard gate. No colour may be read before
   this file and the tool are pushed.

Checked before this push, values only (no colour was read). The published alignment
was recovered, and the corpus-wide leader census matches K020 (2,763 leaders, 606
distinct values):

| Pair | matched groups | V (per-group) | reconstructed W | leader groups A / B | corpus leaders (n / distinct) | zero-value units |
|---|---|---|---|---|---|---|
| KH0502 · KH0514 | 12 | 13 (1, 2, 1, 2, 1, 1, 1, 0, 1, 1, 1, 1) | 123.429… (published 123.4) | 21 / 19 | 2 763 / 606 | 0 |

Matched leader values, in alignment order: 2089, 1842, 1876, 2229, 3320, 4273,
2633, 2950, 2275, 2106, 1737, 1505 (the first nine are the run K020 reported).
Matched group-index pairs (0-based, A · B): (3, 0), (4, 1), (5, 2), (7, 3),
(8, 4), (9, 5), (10, 6), (11, 7), (12, 8), (15, 11), (17, 13), (20, 17). One
matched group pair contributes V = 0 (leaders match; no non-leader LCS cords),
so the 13 units come from 11 of the 12 groups.

**Analysis unit (primary):** one LCS-aligned non-leader cord pair, mirroring
K020's V. Then drop units with `no_colour` on either side from count and
denominator, with reasons counted.

## Colour field and match rule (copied from K046/K045/K049; imported, so they cannot drift)
- Cord colour = K045/K021 field: the `ascher_cord_color` row with the smallest
  `RANGE_BEG` (ties: smallest `color_id`); colour tuple = (non-empty
  `COLOR_CD_1..5` in stored order, non-empty `OPERATOR_1..5` in stored order). A
  cord with no row, an empty `FULL_COLOR`, or no component is `no_colour`; a unit
  with `no_colour` on either side is **excluded from count and denominator**
  (counts reported by reason).
- **Primary match:** identical operator sequence (`-` is not `:`), identical
  ordered component sequence (Ascher order; no re-sort), `PK` ("unknown Urton
  color") on either side **never** matches, `BY` ≠ `YB` (Ascher Table 5 / OKR:
  ISCC 79 vs 76).
- **Sensitivity only:** `BY` ≡ `YB` (KFG's cleaning recode). Disclosed, not a
  verdict.
- The tool imports `colour_match` and the 14-case fixture from
  `tools/k046_colour_agreement.py` so the match function cannot drift from K046.

## Statistic, null, p
- **A** = number of coloured units whose colours match under the primary rule
  (denominator n fixed after `no_colour` exclusions).
- **Null N1 (primary):** permute side B's colour tuples among that pair's n
  coloured units, R = 10 000. This keeps both records' colour frequencies on the
  analysed units, keeps n fixed, and never uses the other khipu's colours.
- p = (1 + #{null ≥ A}) / (R + 1), one-sided (more agreement than
  frequency-matching chance).
- **α = 0.05** (one named pair; no Bonferroni). Decision thresholds use 0.05
  everywhere K049 used 0.01.
- **N2 (descriptive, not a verdict):** partition the n coloured units by the pair
  of `CLUSTER_ID`s `(clusterA, clusterB)`. If every coloured unit shares one such
  key, N2 is **not applicable** (it would be identical to N1). If two or more
  keys are present, permute B's colours only within each key. This asks whether
  agreement goes beyond group-level colour blocks. Reported, not decided on.

## Seeds and budget
N1 **5050**, calibration **5051**, power **5052**, N2 and sensitivities **5053**,
copy-all **5054**. In-tool wall 540 s (the power curve is skipped if 80 % of the
wall is used); outer `timeout 600`. `--smoke` (R = 200, small N) runs only after
this push, output `analysis/k050_smoke.json`, not used for decisions.

## Gates and controls (written before the run)
1. **Match-function fixture** (K046's 14 cases, imported; no data): identical
   plain/barber-pole/mottled/three-part sequences match; `PK` never matches
   (also inside a mottle); `-` ≠ `:`; component order matters; `BY` ≠ `YB`
   primary and `BY` ≡ `YB` only under the sensitivity flag; `no_colour` never
   matches. The tool **refuses to write results** if any case fails.
2. **Copy-all positive control (real structure):** set every B colour := A colour
   on the real units; A must equal the number of units without `PK` on side A
   and p must be < α (null R = 2 000, seed 5054). If not recovered, the pair is
   **tool excluded** unless it is degenerate (rule below).
3. **Calibration FPR (seed 5051):** 1 000 fake observations, each a fresh N1
   permutation, scored against the stored N1 bank; FPR = share with p < α. Gate
   **≤ 0.08** (expedition bar, K034/K040–K042 / K046 / K049).
4. **Structural FPR (shift control, no seed):** every cyclic offset k of B's
   colours along the unit order with min(k, n−k) ≥ ⌈0.1 n⌉, scored against the
   N1 bank. This breaks the correspondence but keeps runs and colour blocks.
   Gate **≤ 0.08**. If either FPR gate fails, the pair is **tool excluded** and
   its real-data p is not interpreted.
5. **Power (seed 5052):** 200 replicates; base = a random N1 permutation of B's
   colours (no residual real signal); then on a random **25 %** of units
   (k = round(0.25 n)) set B's colour := A's colour; p from a fresh N1 bank of
   the planted data (R = 2 000). Power = share with p < α. Bar **≥ 0.5**.
   Descriptive curve at f = 0.10, 0.15, 0.25, 0.40 (100 replicates each).
6. **Data hash gate:** the tool stops if `khipu.db` is not SHA-256
   `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`.

## Decision rules (this one pair)
1. **Excluded (cycle)** if the hash differs, the fixture fails, or the K020
   alignment-consistency gate fails (implementation drift).
2. **DEGENERATE** if there is no colour variation that a shuffle of B could turn
   into extra matches: n = 0 after `no_colour` drops; or the two sides share no
   colour tuple that matches under the primary rule (null identically 0); or
   side A is monochromatic among the n units; or side B is monochromatic among
   the n units. In each of those cases A is fixed by the colour inventories (N1
   has max = min). Report n, A, colour counts and the reason. FPR and power are
   skipped (as in K047–K049). Copy-all is still run as a tool check when n ≥ 1,
   but a degenerate pair is not tool-excluded for a copy-all failure caused by a
   monochromatic inventory.
3. **TOOL EXCLUDED** if the pair is not degenerate and (the copy-all control
   fails, or calibration FPR > 0.08, or shift FPR > 0.08).
4. **SUPPORTED** if p < 0.05 and rules 2–3 do not fire.
5. **NOT TESTABLE** if power at f = 0.25 < 0.5 and p ≥ 0.05 (not a negative).
6. **NOT SUPPORTED** (a real negative at the stated power) if p ≥ 0.05, power
   ≥ 0.5, and rules 2–3 do not fire.

The pair is published, including a negative or not-testable outcome. No HARKing.

Sensitivities (disclosed, **not** verdicts): `BY` ≡ `YB`; only units whose
aligned value ≠ 0; N2 within-group null when two or more `(clusterA, clusterB)`
keys exist.

## Integrity notes
- The pair and the alignment are K020's; K050 is not a re-test of their values.
- KH0491 · KH0503, the K019 trio and the five K010 value-block pairs are out of
  scope.
- First colour row only (multi-range cords reduced to their first range, as
  K021/K045/K046/K049).
- This is not a new pair. Urton & Chu already listed UR266 as matching UR 275.

## What this cannot decide (confounds named in advance)
- **Recorder effects:** Ascher, Urton and Pereyra may have judged the same fibre
  differently (lighting, chart, fading, code choice). Both sides of this pair
  are Urton / Inkawasi records (UR266 and UR275), so they are likely the same
  recorder — the cross-recorder coding problem that made KH0192·KH0469
  unreadable in K046 (`YB` ↔ `AB`) is less exposed here. The confound is still
  named: a shared recording habit can produce colour agreement without proving
  that the two records describe one physical object.
- A **SUPPORTED** pair means colour-code agreement beyond frequency chance **on
  an already-published value correspondence**. It does **not** by itself prove
  "same physical object recorded twice" (a faithful copy would also agree), and
  it is not a new discovery of the pair.
- A **NOT SUPPORTED** pair does **not** prove different objects.
- No decipherment is claimed.

## Next (depends on the result)
- If SUPPORTED: state it with the recorder-habit caveat, and say plainly that
  this is colour confirmation on a published Urton & Chu pair, not a new pair.
  Do not add KH0502·KH0514 to the pending OKR duplicates note: they are
  published corresponding Inkawasi records, not a double recording.
- If NOT SUPPORTED with power: colour-agreement is not visible on this
  alignment under OKR codes.
- If DEGENERATE / NOT TESTABLE / TOOL EXCLUDED: say why.
- A colour-code *association* test on the K046 cross-tabs remains same-data and
  must stay labelled exploratory if run. The unconfirmed KH0240·KH0496 lead
  stays a lead.

## Output
`analysis/k050_results.json` (`analysis/k050_checkpoint.json` while running), log
`analysis/k050_run.log`.
Run from `expeditions/khipu/`: `timeout 600 python3 tools/k050_k020_colour_agreement.py run`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04


---

## Results (2026-11-08, run ~08:26 PT, America/Vancouver)

Run after the prereg was published as `e7fec23` (connector `push_files`; `git push` had no
credentials; local clone aligned with `git reset --mixed origin/main` on an identical tree,
never `--hard`). Full run **0.8 s** wall (nothing was cut by the wall; the power curve
finished). Output [`analysis/k050_results.json`](../analysis/k050_results.json), log
[`analysis/k050_run.log`](../analysis/k050_run.log).

### Gates (cycle-level)
- DB hash matches; **fixture 14/14 passed**; **K020 consistency passed** (12 matched groups,
  V = 13; reconstructed W = 123.429… against the published 123.4; corpus-wide leaders
  2 763 / 606 distinct, matching K020; per-group V = 1, 2, 1, 2, 1, 1, 1, 0, 1, 1, 1, 1).
- **Excluded units: 0** (every aligned non-leader cord has a usable first colour row; n = 13).
- **Copy-all control recovered** (A = 13, p = 0.00050, R = 2 000 floor).

| Pair | n | Calibration FPR (1 000) | Shift FPR (offsets) | Power f = 0.25 (k planted) | Curve f = 0.10 / 0.15 / 0.25 / 0.40 |
|---|---|---|---|---|---|
| KH0502 · KH0514 | 13 | 0.000 | 0.000 (10; min p 1.000) | **0.44** (3) | 0.04 / 0.18 / 0.32 / 0.93 |

Calibration and shift FPR pass (both 0 ≤ 0.08). Power at the pre-registered 25 % plant
(k = 3 of 13) is **0.44**, below the readability bar of 0.5. The descriptive curve's own
f = 0.25 estimate (100 replicates) is 0.32; at f = 0.40 (k = 5) it reaches 0.93. A stronger
plant would have been readable; the pre-registered 25 % plant is not.

### Primary statistic (N1, R = 10 000, seed 5050; α = 0.05)

| Pair | Systems | n | A (matches / n) | Null mean ± sd · q95 · max | p | Power f=0.25 | Copy-all | Cal / shift FPR | **Verdict** |
|---|---|---|---|---|---|---|---|---|---|
| KH0502 · KH0514 | UR · UR (Inkawasi) | 13 | 1 / 13 | 0.073 ± 0.260 · 1 · 1 | 0.0733 | 0.44 | recovered (A=13, p 0.00050) | 0 / 0 | **NOT TESTABLE** |

### Why the test looks like this
KH0502 (UR266) and KH0514 (UR275) share almost no colour codes on the 13 aligned
non-leader cords. Side A is 8 plain `YB`, 3 plain `HB`, 1 plain `MB` and 1 barber-pole
`W-AB`. Side B is 11 plain `NB`, 1 plain `AB` and 1 barber-pole `W-AB`. The single match
is that `W-AB` (group indices 7 · 3, non-leader positions 3 · 2, value 386). Because the
inventories share only that one matching tuple, and each side has exactly one of it, N1
can only produce A = 0 or A = 1 (null mean 0.073, max 1), and the observed 1 is the
upper point of that two-value distribution. The Monte Carlo p is 0.0733, which does not
beat α = 0.05 (it sits near the exact 1/13 ≈ 0.0769 chance that B's single `W-AB` lands
on A's). Copy-all and both FPR gates pass, but power at f = 0.25 is 0.44, just under the
0.5 bar, so a silence — or this near-chance single coincidence — cannot be read as a
powered negative.

### Disclosed, not verdicts
- **Recorder / provenance census.** KH0502 (UR266, Incahuasi, Proyecto Incahuasi 13829) ·
  KH0514 (UR275, Incahuasi, Proyecto Incahuasi 13836-2014). Both records are filed as
  Urton at the same site, so they are likely the same recorder. The dominant codes still
  do not meet (`YB`/`HB` vs `NB`); that is a descriptive inventory fact, not a verdict,
  and it is not the cross-recorder `YB`↔`AB` translation K046 saw. The recorder-habit
  confound named in the prereg still applies: agreement, had it appeared, would not have
  proved one physical object.
- **BY ≡ YB.** No pair of aligned units is a `BY`/`YB` pair (A has plain `YB` but B does
  not); the sensitivity is essentially identical to the primary (1/13, p 0.0717).
- **Non-zero-value units.** Identical to the primary (the 13 aligned values include no
  zeros).
- **N2 (within `(clusterA, clusterB)` key).** Applicable: 11 keys (sizes 1, 2, 1, 2, then
  seven 1s — the two doubleton groups are the ones whose V was 2). Null mean 0.490,
  p 0.490 (descriptive). The one match sits inside a size-2 group, so a within-group
  shuffle keeps or loses it about half the time.

### Reading
KH0502 · KH0514 is **NOT TESTABLE**. Colour-code equality on K020's already-published
value alignment does not beat frequency-matching chance (1/13 vs 0.073, p 0.0733) and
does not meet the power bar (0.44 at a 25 % plant). This is **not** a negative, **not**
a confirmation, and **not** a new pair: Urton & Chu already listed UR266 as matching
UR 275. The result does not overturn K020's value correspondence, does not prove
same-object or two-copy status, and does not read a khipu. No decipherment.

### Next (lines 3 and 6)
Colour-code equality on every confirmed cross-khipu correspondence family this
expedition has — the K019 group-leader alignments (K046), the K010 value-block pairs
(K049), and the K020 pair (this cycle) — is now mapped. No further colour-equality test
on those same pairs is owed. A colour-code *association* test on the K046 cross-tabs
remains same-data and must stay labelled exploratory if run. The unconfirmed
KH0240·KH0496 lead (line 3) stays a lead. A physical-feature check on this K020
alignment would face the same n = 13 and the unreadability K047 already documented on
larger, unbalanced fields; it is not proposed here.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
