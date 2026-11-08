# K051 · Colour agreement on the shared block of the unconfirmed lead KH0240 · KH0496 (README lines 3 and 6)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registration** (written and pushed with the tool before any colour of this pair was
read; only the values-only consistency check listed below was run first).

## Why
K012 raised one unconfirmed lead: **KH0240 (UR004, Leymebamba, Centro Mallqui CMA 847-LC1.476 TEQ)**
and **KH0496 (UR260, Incahuasi, Proyecto Incahuasi 9228-13B)** share the run-collapsed pendant
pattern `P = 1, 2, 1, 2, 3, 1, 2, 1, 3`, with different run lengths. K027 excluded a shared
small-number template (no other khipu or pair has such a block). K028 found the lead survives an exact
doublet-preserving null (p 0.027) but is **not confirmed**: the length 9 and the {1, 2, 3} alphabet
were selected from the lead itself, and K013's run-length-aware test gave p 0.18. K028's named
held-out test (the same search on khipus added to OKR later) is data-limited.

Every test so far used the **values** that selected the pair. Colour is a field the pair was **not
selected on**, so it is an independent witness. If the two blocks are related records (a copy, or one
account written twice), the runs might also share colour codes. The README's "no further
colour-equality test" applies to the already-mapped confirmed families (K019 / K010 / K020), not to
this unconfirmed lead, which has never had a colour test.

## Question
On the 9 aligned collapsed runs of `P`, do the two khipus carry the **same colour code** more often
than a within-khipu shuffle of KH0496's run colours?

## Data
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`;
read-only URI; the tool stops if the hash differs). Not committed. The pinned file has not changed
since K028, so K028's held-out search (fallback (a)) has no new khipus to use in this repository.

## Block (values only; K012/K027/K028 rule)
Level-1 pendants in `CORD_ORDINAL` order; khipus with `DUPLICATE_FLAG = 1` omitted; R5 multi-number
cords (K007 definition) zeroed in place; khipus with ≥ 10 nonzero pendants (N = 433). Runs of equal
values are collapsed. `P` must occur **exactly once** in each khipu, and the run lengths must equal
K012's published ones, or the cycle is **excluded** (drift).

Checked before this push, values only (no colour read):

| Khipu | collapsed runs / pendants | block starts at run / cord index (0-based) | run lengths |
|---|---|---|---|
| KH0240 (UR004) | 363 / 472 | 329 / 402 | 4, 1, 1, 1, 1, 1, 1, 1, 1 (published) |
| KH0496 (UR260) | 20 / 24 | 0 / 0 | 1, 1, 3, 1, 1, 2, 1, 1, 1 (published) |

`P` occurs once in each; no other eligible khipu contains `P` (K027 T1 re-derived: 0). Both blocks
span 12 cords, but the run lengths differ, so **no 1-1 cord alignment exists**.

## Unit and colour rule (pre-registered; no tuning)
- **Unit** = one collapsed run, n = 9 (run r of A against run r of B).
- **Cord colour** = K045/K046 field: the `ascher_cord_color` row with the smallest `RANGE_BEG` (ties:
  smallest `color_id`); tuple = (non-empty `COLOR_CD_1..5`, non-empty `OPERATOR_1..5`, stored order).
  No row / empty `FULL_COLOR` / no component = `no_colour`.
- **Run colour (primary)** = the **modal** exact tuple among the run's coloured cords; **tie** → the tied
  tuple carried by the **earliest** cord of the run. Runs of length 1 (15 of the 18 runs) are just the
  cord's colour. A run with no coloured cord is `no_colour`; a unit with `no_colour` on either side is
  dropped from count and denominator (reported).
- **Match** = K046 `colour_match`, imported (identical operator sequence, `-` ≠ `:`, identical ordered
  components, `PK` never matches, `BY` ≠ `YB`). K046's 14-case fixture must pass.

## Statistic, null, p
- **A** = number of the n units whose run colours match.
- **Null N1:** permute KH0496's n run colours among the n units (within-khipu, keeps both inventories).
  The distribution is computed **exactly** over all n! permutations (subset DP on the n × n match
  matrix; self-tested against brute force for n ≤ 6 and against the derangement count 133 496 for
  n = 9). **p = P_null(A ≥ A_obs)**, exact, one-sided. A Monte Carlo bank (R = 10 000, seed 5151) is a
  cross-check only.
- **α = 0.05**: one named pair, one primary hypothesis, no Bonferroni.

## Gates and controls
1. **Data hash** must match; **fixture** 14/14 and the exact-DP self-test must pass (else no results).
2. **Values consistency** (above) must pass (else excluded).
3. **Copy-all** (set B := A on the real units): A must equal the number of A runs without `PK`, and the
   exact p < α. Else **tool excluded** (unless degenerate).
4. **Calibration FPR** (seed 5152): 1 000 fresh N1 permutations scored with the exact p; share with
   p < α ≤ 0.08.
5. **Shift FPR**: every cyclic offset k = 1…8 of B's run colours (min(k, n−k) ≥ ⌈0.1 n⌉), scored with the
   exact p; share with p < α ≤ 0.08.
6. **Power** (seed 5153): 200 replicates; base = a random N1 permutation of B; then copy A's colour
   onto a random 25 % of units (k = round(0.25 n) = 2 for n = 9); exact p. Power = share p < α.
   Bar **≥ 0.5**. Descriptive curve f = 0.10, 0.15, 0.25, 0.40, 0.55 (100 replicates each).

## Decision rule
1. **Excluded (cycle)**: hash, fixture, DP self-test or values consistency fails.
2. **DEGENERATE**: n = 0, or no A tuple matches any B tuple, or A or B monochromatic on the n units
   (A fixed by the inventories). FPR / power skipped; reported with colour counts.
3. **TOOL EXCLUDED**: not degenerate and copy-all fails or either FPR > 0.08.
4. **SUPPORTED**: exact p < 0.05 and rules 2–3 do not fire (power is reported alongside).
5. **NOT TESTABLE**: p ≥ 0.05 and power < 0.5.
6. **NOT SUPPORTED**: p ≥ 0.05, power ≥ 0.5 (a real negative at that power).

Sensitivities (disclosed, **not** verdicts): `BY` ≡ `YB`; run colour = first cord of the run instead of
the modal tuple. Monte Carlo p as a cross-check.

## Seeds and budget
MC cross-check 5151, calibration 5152, power 5153, sensitivities 5154, copy-all MC 5155. In-tool wall
540 s; outer `timeout 600`. A `--smoke` run (output `analysis/k051_smoke.json`, not committed, not used
for decisions) may run only after this push.

## Confounds named in advance
- **Site and recorder:** Leymebamba (Chachapoyas, OKR region field) vs Incahuasi (Cañete valley; OKR region field empty). Both are UR records, but they
  may have been recorded at different times and with different colour judgement; K046 showed
  recorder translation (`YB` ↔ `AB`) can erase real agreement. A NOT SUPPORTED / DEGENERATE result can
  be recorder translation, not independence.
- **Regional dye palettes:** a SUPPORTED result could reflect common colour habits (e.g. many plain
  `W` or `AB` cords) rather than a link; the within-khipu null only controls each record's own
  frequencies on these 9 runs.
- **Run-level reduction:** the modal-per-run rule discards within-run colour changes on 3 runs
  (A run 1 of 4 cords; B runs of 3 and 2 cords).
- A SUPPORTED result would **not confirm the lead as a link between sites**; it would be a second,
  independent field agreeing on the block, to be stated with these caveats. No decipherment.

## Next (depends on the result)
- SUPPORTED: report as independent-field agreement on the lead; the lead stays unconfirmed until a
  held-out value test exists; check literature again.
- NOT SUPPORTED / NOT TESTABLE / DEGENERATE / TOOL EXCLUDED: say why; the lead stays a lead.
- Not added to the pending OKR note in any case (an unconfirmed lead is not a data-quality fact).

## Output
`analysis/k051_results.json`, log `analysis/k051_run.log`.
Run from `expeditions/khipu/`: `timeout 600 python3 tools/k051_lead_block_colour.py run`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
