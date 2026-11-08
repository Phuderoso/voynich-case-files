# K047 · Cross-khipu physical-feature agreement on the three K019 pairs (README line 6)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: preregistered** (this file and `tools/k047_physical_agreement.py` are written and will be
pushed before any pair-feature agreement number is computed). A whole-khipu coverage look at OKR
physical fields on these five khipus — frequencies only, never the K019 alignment and never a
cross-tab — is disclosed below and was used to choose which fields are primary vs census-only.

## Why
K018/K019 confirmed an ordered, cord-level **value** correspondence for three pairs:
KH0097·KH0586 (Paris·Lima, Ascher vs Pereyra/HP), KH0192·KH0470 and KH0192·KH0469 (Berlin, Ascher vs
Urton). K046 tested whether the same alignment also carries matching colour codes: one pair
supported, one supported but fragile, one degenerate (no shared code). Colour across recorders is
mostly a recorder-translation problem, and colour equality cannot tell "same object recorded twice"
from "faithful copy".

K046's Next named this step: a pre-registered **physical-feature** agreement test on the same
alignment, using fields K046 never looked at. Physical features that a recorder actually observed
cord by cord (not batch-filled) are a fresh, value-independent and colour-independent witness.
Condition features such as how a cord ends (knotted vs broken) would be expected to agree if two
records describe the same object, and not systematically if they describe two objects.

## Whole-khipu coverage (disclosed; not on the alignment)
On all level-1 pendants of the five khipus, before any alignment was built:

| Field | KH0097 (AS) | KH0586 (HP) | KH0192 (AS) | KH0470 (UR) | KH0469 (UR) |
|---|---|---|---|---|---|
| `TWIST` (ply) | S 298, U 19, Z 1, empty 1 | S 189 | S 224 | S 126 | S 125 |
| `ATTACHMENT_TYPE` | R 58, V 241, U 20 | R 189 | U 224 | R 126 | V 125 |
| `FIBER` | all empty | CN 189 | all empty | CN 126 | CN 125 |
| `TERMINATION` | K 245, B 52, empty 22 | K 170, B 16, U 3 | K 213, B 7, U 4 | K 120, B 6 | K 103, B 22 |
| knot `DIRECTION` majority (usable S/Z) | S 129, Z 128, mixed 105 | Z 162 (all Z) | Z 183, S 2, mixed 8 | Z 79, S 11, mixed 38 | Z 61, S 15, mixed 28 |
| `THICKNESS` | varies | all 0 | all 0 | varies | varies |
| `TWIST_ANGLE` | all 0 | empty | all 0 | all 0 | all 0 |
| `CORD_LENGTH` | varies | varies | varies | varies | varies |

So ply is monochromatic S (or nearly) on every side; attachment is a recorder-level constant on
KH0586 (all R), KH0192 (all U), KH0470 (all R) and KH0469 (all V); fiber and thickness are missing
or zeroed on the Ascher side of every pair. Those fields cannot produce a non-degenerate within-khipu
shuffle (if one side is constant on the analysed units, permuting it leaves the match count fixed).
They are therefore **census-only**. Termination varies on both sides of every pair; knot-direction
majority varies on both sides of the two Berlin pairs (Paris·Lima's HP side is all Z, so that
pair-field is expected to be degenerate). Those two are the **primary tests**. Length varies on all
five and is tested as a disclosed rank correlation (different metric; not a verdict).

## Question
On the value correspondence K019 already confirmed, do aligned cords carry the **same termination
code** / **same majority knot direction** more often than a within-khipu shuffle that keeps each
record's feature frequencies?

## Data
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`;
read-only URI; the tool stops if the hash differs). Not committed.

## Alignment (copied from K046/K019; selected on values, never on these features)
1. Values, `DUPLICATE_FLAG`, R5 zeroing, groups, leader groups and leader weights are K019's code,
   imported from `tools/k046_colour_agreement.py` so the traceback cannot drift.
2. **Consistency gate (values only):** matched groups and ΣV must equal K019's published 13/89,
   14/37, 15/36, and every traceback length must equal V, or the cycle is **excluded**.
3. **Analysis unit (primary):** one LCS-aligned non-leader cord pair, mirroring K019's V. Leaders
   are not in the primary statistic; they enter one disclosed sensitivity only.

## Feature rules (fixed now)

### Primary field T — termination
- Value = trimmed `cord.TERMINATION`, or `no_feature` if empty/NULL.
- A unit with `no_feature` on either side is **excluded** from count and denominator (reason counted).
- **Match:** identical code (`K`=`K`, `B`=`B`, `U`=`U`; `K`≠`B`, `K`≠`U`, `B`≠`U`). No recoding.

### Primary field D — majority knot direction
- Among that cord's knots whose `DIRECTION` is `S` or `Z` (`U`, NULL and empty ignored), in stored
  `KNOT_ORDINAL` order: if none, `no_feature` (unit excluded). If `#S` > `#Z` → `S`; if `#Z` > `#S`
  → `Z`; if equal → `TIE`.
- **Match:** identical label (`S`=`S`, `Z`=`Z`, `TIE`=`TIE`; `S`≠`Z`).

### Census-only (no p interpreted as agreement)
- **Ply** `cord.TWIST` (trimmed; empty excluded): report n, distinct values on each side, raw match
  count. Expected degenerate (one or both sides monochromatic S).
- **Attachment** `cord.ATTACHMENT_TYPE` (trimmed; empty excluded): same report. Expected degenerate
  (KH0586 all R, KH0192 all U, KH0470 all R, KH0469 all V at khipu level).

### Disclosed, not verdicts
- Knot-direction as the **ordered tuple** of usable `S`/`Z` directions (length-sensitive).
- Units with leaders included; only units whose aligned value ≠ 0; N2 within-group null.
- **Length Spearman:** on units where both `CORD_LENGTH` are non-NULL; ρ = Spearman rank correlation
  of the two length vectors; null = permute B's lengths. One-sided (larger ρ). Degenerate if either
  side has zero length variance or n < 5.

## Statistic, null, p (categorical primary fields)
- **A** = number of usable units whose features match (denominator n fixed).
- **Null N1 (primary):** permute side B's feature labels among that pair-field's n units, R = 10 000.
  Keeps both records' frequencies on the analysed units.
- p = (1 + #{null ≥ A}) / (R + 1), one-sided.
- **α = 0.05 / 6 = 0.008333** (Bonferroni over 3 pairs × 2 primary fields). Census-only fields do
  not spend α. A degenerate primary pair-field still spends its α slot (conservative).
- **N2 (descriptive):** permute B only within each matched group pair.
- **Degeneracy gate:** if either side has fewer than 2 distinct values on the n units (equivalently,
  if the N1 distribution of A has max = min), the pair-field is **DEGENERATE**. This gate uses only
  per-side distinct counts, not a reading of A against chance. A is still reported (when one side is
  constant, A is a function of the other side's margin).

## Seeds and budget
N1 **4747**, calibration **4748**, power **4749**, N2 **4750**, sensitivities **4751**.
In-tool wall 540 s; outer `timeout 600`. `--smoke` (R = 200, small N) runs only after this push,
output `analysis/k047_smoke.json`, not used for decisions.

## Gates and controls (written before the run)
1. **Match-function fixture** (`tools/k047_physical_agreement.py fixture`, no data): termination
   identities and mismatches; empty never matches; knot-majority S/Z/TIE and empty; ply and
   attachment identities. The tool **refuses to write results** if any case fails.
2. **Copy-all positive control:** set every B feature := A feature on the real units; A must equal n
   and p must be < α (null R = 2 000). If not recovered, that pair-field is **tool excluded**.
3. **Calibration FPR (seed 4748):** 1 000 fake observations, each a fresh N1 permutation, scored
   against the stored N1 bank; FPR = share with p < α. Gate **≤ 0.08**.
4. **Structural FPR (shift control, no seed):** every cyclic offset k of B's features along the unit
   order with min(k, n−k) ≥ ⌈0.1 n⌉, scored against the N1 bank. Gate **≤ 0.08**.
5. **Power (seed 4749):** 200 replicates; base = a random N1 permutation of B; then on a random
   **25 %** of units set B's feature := A's feature; p from a fresh N1 bank (R = 2 000). Bar **≥ 0.5**.
   Descriptive curve at f = 0.10, 0.15, 0.25, 0.40 (100 replicates each).
   Degenerate pair-fields skip FPR/power (there is nothing to calibrate) and take verdict DEGENERATE.

## Decision rules (per pair-field)
1. **Excluded (cycle)** if the hash differs, the fixture fails, or the K019 consistency gate fails.
2. **DEGENERATE** if either side has fewer than 2 distinct values on the n units.
3. **TOOL EXCLUDED** if the copy-all control fails, or calibration FPR > 0.08, or shift FPR > 0.08.
4. **NOT TESTABLE** if power at f = 0.25 < 0.5, or n < 10.
5. **SUPPORTED** if p < 0.008333 and rules 2–4 do not fire.
6. **NOT SUPPORTED** (a real negative at the stated power) if p ≥ 0.008333 and rules 2–4 do not fire.

## What this cannot decide (confounds named in advance)
- **Recorder effects:** Ascher, Urton and Pereyra may code ply, attachment, knot chirality and
  "broken vs unfinished" differently, or fill a field with a single default for a whole khipu
  (the coverage table already shows this for attachment and for KH0586's knot directions). A
  negative may be recorder disagreement, not a different object; a positive on a batch-filled
  field would be meaningless, which is why those fields are census-only.
- **Condition vs design:** termination (especially `B` broken) can change between two recordings of
  the same object, and two copies can share a knotted-end habit without being the same object.
  A SUPPORTED termination result leans toward "same object" or "shared condition-coding habit"; it
  does not prove either. A NOT SUPPORTED result does not prove different objects.
- Knot-direction majority collapses mixed-chirality cords to one label; the ordered-tuple
  sensitivity is stricter and can fail because aligned cords (same value) still decompose into a
  different number of knot clusters.
- Length Spearman is invariant to a recorder's scale or offset but not to strongly non-monotone
  measurement differences; it is disclosed, not a verdict.
- Same data: the pairs and alignment are K018/K019's; K047 is not a re-test of their values or of
  K046's colours.
- No decipherment is claimed.

## Next (depends on the result)
- If any primary pair-field is SUPPORTED: fold a caveated sentence into the pending OKR note, and
  say whether termination (a condition feature) or knot direction (a design feature) carried it.
- If NOT SUPPORTED with power: that physical-feature equality fork is closed for that pair-field
  under OKR codes; recorder effects remain the leading alternative to state.
- If DEGENERATE / NOT TESTABLE / TOOL EXCLUDED: say why. A colour code-*association* test on the
  K046 cross-tabs would still be post hoc and must stay labelled exploratory.

## Output
`analysis/k047_results.json` (`analysis/k047_checkpoint.json` while running), log `analysis/k047_run.log`.
Run from `expeditions/khipu/`: `timeout 600 python3 tools/k047_physical_agreement.py run`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
