# K046 · Cross-khipu colour agreement on the three K019 pairs (README line 6)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registration** (written and pushed with the tool before any pair-colour agreement
number was computed; only value-side consistency counts, listed below, were checked first).

## Why
K018/K019 confirmed, on **values only**, an ordered group-leader and cord-level correspondence for
three pairs: KH0097·KH0586 (Paris·Lima, Ascher vs Pereyra/HP), KH0192·KH0470 and KH0192·KH0469
(Berlin, Ascher vs Urton). K045 showed that all three recorders' colours sit in OKR's single Ascher
dictionary and gated all three pairs as **`co_mappable`**. K045's "Next" named this step: a
pre-registered cross-khipu colour-agreement test on those pairs only. Colour is a field the pairs
were **not** selected on, so it is a fresh, value-independent look at the correspondence.

## Question
On the value correspondence K019 already confirmed, do aligned cords carry the **same colour code**
more often than a within-khipu shuffle that keeps each record's colour frequencies?

## Data
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`;
read-only URI; the tool stops if the hash differs). Not committed.

## Alignment (copied from K018/K019; selected on values, never on colours)
1. Values, `DUPLICATE_FLAG`, R5 zeroing, groups (`CLUSTER_ID` runs of level-1 pendants), leader groups
   (≥ 5 cords, leader > 0) and the corpus-wide leader weights are K019's code, copied verbatim.
2. Groups are matched by K019's weighted leader LCS traceback (`walign`).
3. Inside each matched group pair, the **non-leader** cords are aligned by the exact value LCS (zeros
   included, as in K019's V). K019 only needed the length; K046 needs the alignment, so a
   deterministic traceback is fixed now: from the end, take the diagonal when the values are equal and
   `D[i][j] = D[i−1][j−1] + 1`; else move up if `D[i−1][j] ≥ D[i][j−1]`; else left.
4. **Consistency gate (values only):** matched groups and ΣV must equal K019's published 13/89,
   14/37, 15/36, and the traceback length must equal V in every group pair, or the cycle is
   **excluded** (implementation drift). Checked before this push, values only: 13/89, 14/37, 15/36;
   aligned non-leader units 89, 37, 36 (of which value 0: 7, 10, 15). No colour was read.

**Analysis unit (primary):** one LCS-aligned non-leader cord pair, mirroring K019's V.
Leaders are **not** in the primary statistic (they selected the pairs); they enter one disclosed
sensitivity only.

## Colour field and match rule (fixed now)
- Cord colour = K045/K021 field: the `ascher_cord_color` row with the smallest `RANGE_BEG` (ties:
  smallest `color_id`); colour tuple = (non-empty `COLOR_CD_1..5` in stored order, non-empty
  `OPERATOR_1..5` in stored order). A cord with no row, an empty `FULL_COLOR`, or no component is
  `no_colour`; a unit with `no_colour` on either side is **excluded from count and denominator**
  (counts reported by reason).
- **Primary match:** identical operator sequence (`-` is not `:`), identical ordered component
  sequence (Ascher order; no re-sort), `PK` ("unknown Urton color") on either side **never** matches,
  `BY` ≠ `YB` (Ascher Table 5 / OKR: ISCC 79 vs 76).
- **Sensitivity only:** `BY` ≡ `YB` (KFG's cleaning recode). Disclosed, not a verdict.

## Statistic, null, p
- **A** = number of coloured units whose colours match under the primary rule (denominator n fixed).
- **Null N1 (primary):** permute side B's colour tuples among that pair's n coloured units, R = 10 000.
  This keeps **both** records' colour frequencies on the analysed units, keeps n fixed, and never uses
  the other khipu's colours (permuting one side is equivalent in distribution to permuting both).
  Chosen over "all coloured level-1 pendants" so the frequencies are those of the cords actually compared.
- p = (1 + #{null ≥ A}) / (R + 1), one-sided (more agreement than frequency-matching chance).
- **α = 0.05 / 3 = 0.01667** (Bonferroni over the three named pairs; one primary statistic).
- **N2 (descriptive, not a verdict):** permute B's colours only within each matched group pair. It asks
  whether agreement goes beyond group-level colour blocks. Reported, not decided on.

## Seeds and budget
N1 **4646**, calibration **4647**, power **4648**, N2 **4649**, sensitivities **4650**; copy-all control
seed 4748. In-tool wall 540 s (the power curve is skipped if 80 % is used); outer `timeout 600`.
`--smoke` (R = 200, small N) runs only after this push, output `analysis/k046_smoke.json`, not used
for decisions.

## Gates and controls (written before the run)
1. **Match-function fixture** (`tools/k046_colour_agreement.py fixture`, 14 cases, no data): identical
   plain/barber-pole/mottled/three-part sequences match; `PK` never matches (also inside a mottle);
   `-` ≠ `:`; component order matters; `BY` ≠ `YB` primary and `BY` ≡ `YB` only under the sensitivity
   flag; `no_colour` never matches. The tool **refuses to write results** if any case fails.
2. **Copy-all positive control (real structure):** set every B colour := A colour on the real units;
   A must equal the number of units without `PK` on side A and p must be < α (null R = 2 000).
   If not recovered, that pair is **tool excluded**.
3. **Calibration FPR (seed 4647):** 1 000 fake observations, each a fresh N1 permutation, scored against
   the stored N1 bank; FPR = share with p < α. Gate **≤ 0.08** (expedition bar, K034/K040–K042).
4. **Structural FPR (shift control, no seed):** every cyclic offset k of B's colours along the unit order
   (group-pair order, then position) with min(k, n−k) ≥ ⌈0.1 n⌉, scored against the N1 bank. This
   breaks the correspondence but keeps runs and colour blocks, so it catches a null that is too
   generous when colours come in blocks. Gate **≤ 0.08**. If either FPR gate fails, the pair is
   **tool excluded** and its real-data p is not interpreted.
5. **Power (seed 4648):** 200 replicates; base = a random N1 permutation of B's colours (no residual
   real signal); then on a random **25 %** of units (k = round(0.25 n)) set B's colour := A's colour;
   p from a fresh N1 bank of the planted data (R = 2 000). Power = share with p < α. Bar **≥ 0.5**.
   Descriptive curve at f = 0.10, 0.15, 0.25, 0.40 (100 replicates each).

## Decision rules (per pair)
1. **Excluded (cycle)** if the hash differs, the fixture fails, or the K019 consistency gate fails.
2. **TOOL EXCLUDED** if the copy-all control fails, or calibration FPR > 0.08, or shift FPR > 0.08.
3. **NOT TESTABLE** if power at f = 0.25 < 0.5.
4. **SUPPORTED** if p < 0.01667 and rules 2–3 do not fire.
5. **NOT SUPPORTED** (a real negative at the stated power) if p ≥ 0.01667 and rules 2–3 do not fire.

Sensitivities (disclosed, **not** verdicts): BY ≡ YB; units with leaders included; only units whose
aligned value ≠ 0; N2 within-group null.

## Integrity notes
- K019 printed same-position (zip) colour counts as descriptive notes. They are **not** used as an
  expectation or to set any threshold here; K046 uses the LCS alignment, not zip positions, and every
  bar above is the expedition's standing bar.
- Same data: the pairs and alignment are K018/K019's; K046 is not a re-test of their values.

## What this cannot decide (confounds named in advance)
- **Recorder effects:** Ascher, Urton and Pereyra may have judged the same fibre differently (lighting,
  chart, fading, code choice). K045 found no independent Urton or Pereyra colour dictionary; their records
  are in Ascher codes in OKR. A negative may be recorder disagreement, not a different object.
- A **SUPPORTED** pair means colour-code agreement beyond frequency chance **on the value alignment**.
  It does **not** by itself prove "same physical object recorded twice" (a faithful copy would also agree).
- A **NOT SUPPORTED** pair does **not** prove different objects.
- First colour row only (multi-range cords reduced to their first range, as K021/K045).
- No decipherment is claimed.

## Next (depends on the result)
- If any pair is SUPPORTED: fold the pre-registered colour agreement into the pending OKR duplicates
  note (as an observation, with the confound), and consider a physical-feature check (ply, attachment,
  knot direction) on the same alignment.
- If NOT SUPPORTED with power: colour-agreement fork closed for that pair under OKR codes; recorder
  effects remain the leading explanation to state, not to test here.
- If NOT TESTABLE / TOOL EXCLUDED: say why, and propose a design that fixes the named gap.

## Output
`analysis/k046_results.json` (`analysis/k046_checkpoint.json` while running), log `analysis/k046_run.log`.
Run from `expeditions/khipu/`: `timeout 600 python3 tools/k046_colour_agreement.py run`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
