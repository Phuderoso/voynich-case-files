# K048 · Rare-label concordance on the three K019 pairs (README line 6)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results appended** (pre-registration written and pushed with the tool as `b26aba4` before any
pair-level dual-rare count was computed). K047's published physical-feature *equality* results —
including a descriptive remark that broken ends sat at the null floor — are treated below as a
disclosure, not as a reason to change the hypothesis or to flip the test to a deficit / two-sided
look (that would be HARKing).

## Why
K018/K019 confirmed an ordered, cord-level **value** correspondence for three pairs:
KH0097·KH0586 (Paris·Lima, Ascher vs Pereyra/HP), KH0192·KH0470 and KH0192·KH0469 (Berlin, Ascher vs
Urton). K046 tested colour on the same alignment (one pair supported, one supported but fragile, one
degenerate). K047 then tested physical-feature *equality* — same termination code, same majority
knot direction — and found the witness unreadable: ply and attachment are recorder-level constants
(census, all six pair-fields degenerate); termination and majority knot direction are too unbalanced
(almost all knotted `K`, almost all `Z`) for a 25 % copy plant of *all* units to beat Bonferroni
α = 0.00833. No primary pair-field was SUPPORTED.

K047 reserved this step: a pre-registered look at the **rare marks only**. Equality of a
near-constant field is mostly "both cords are knotted" or "both are Z", which the margins already
force. Shared-object / shared-condition would instead predict extra *alignments of the rare class*
— the few broken ends, or the few S-majority cords, sitting opposite each other. That is a
different statistic from K047's overall match count, and a 50 % sharing plant of A's rare marks
is better matched to it than copying 25 % of all units (which mostly recopies the majority class).

**Disclosure, not a verdict.** K047 noted descriptively that the broken ends sat at the null floor
of the equality test (the rare labels did not overlap, so observed equality sat at the minimum the
margins allow). That peek is why this cycle exists as a question, not why the test is one-sided the
other way. The scientifically motivated prediction for same-object / shared-condition is *excess*
dual-rare alignments. If the broken ends again sit at the floor, the honest verdict is NOT
SUPPORTED (if powered) or NOT TESTABLE (if power fails) — not a post-hoc deficit test.

A colour code-*association* test on the K046 cross-tabs is same-data and is **not** a primary of
this cycle; if mentioned at all it must stay labelled exploratory.

## Question
On the value correspondence K019 already confirmed:

- **H_T.** Is the number of usable units where **both** cords have `TERMINATION = B` (broken)
  larger than expected under a within-khipu shuffle of B's termination labels?
- **H_D.** Is the number of usable units where **both** cords have majority knot direction = `S`
  larger than expected under a within-khipu shuffle of B's majority-direction labels?

## Data
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`;
read-only URI; the tool stops if the hash differs). Not committed.

## Alignment (copied from K046/K019; selected on values, never on these features)
1. Values, `DUPLICATE_FLAG`, R5 zeroing, groups, leader groups and leader weights are K019's code,
   imported from `tools/k046_colour_agreement.py` so the traceback cannot drift. Feature extraction
   (termination trim; majority knot direction) is the same rule as
   `tools/k047_physical_agreement.py`.
2. **Consistency gate (values only):** matched groups and ΣV must equal K019's published 13/89,
   14/37, 15/36, and every traceback length must equal V, or the cycle is **excluded**.
3. **Analysis unit (primary):** one LCS-aligned non-leader cord pair, mirroring K019's V and K047.
   Leaders are not in the primary statistic; they enter one disclosed sensitivity only.

## Feature rules (fixed now)

### Field T — termination (rare label = `B`)
- Value = trimmed `cord.TERMINATION`, or `no_feature` if empty/NULL.
- A unit with `no_feature` on either side is **excluded** from count and denominator (reason counted).
- Rare = `B` (broken). Other codes (`K`, `U`, …) are non-rare. No recoding.

### Field D — majority knot direction (rare label = `S`)
- Among that cord's knots whose `DIRECTION` is `S` or `Z` (`U`, NULL and empty ignored), in stored
  `KNOT_ORDINAL` order: if none, `no_feature` (unit excluded). If `#S` > `#Z` → `S`; if `#Z` > `#S`
  → `Z`; if equal → `TIE`. Same rule as K047.
- Rare = `S`. `Z` and `TIE` are non-rare.

**Usable unit** = both sides have a defined feature (not empty/NULL/`no_feature`), same as K047.

## Statistic, null, p
- **A** = number of usable units where **both** sides carry the rare label (dual-rare count).
  This is **not** overall equality (K047 already ran that). `K`=`K` and `Z`=`Z` do not increment A.
- **Null N1 (primary):** permute side B's feature labels among that pair-field's n usable units,
  R = 10 000. Keeps both records' frequencies on the analysed units. Equivalent to
  Hypergeometric(N = n, K = n_rare_A, n = n_rare_B).
- p = (1 + #{null ≥ A}) / (R + 1), **one-sided excess**.
- **α = 0.05 / 6 = 0.008333** (Bonferroni over 3 pairs × 2 primary fields). A degenerate pair-field
  still spends its α slot (conservative).
- **N2 (descriptive only):** permute B only within each matched group pair.
- **Degeneracy:** if either side has 0 rare labels on the n units, **or** if either side is all-rare
  (n_rare = n), the pair-field is **DEGENERATE** (A is then fixed by the margins; N1 has max = min).
  Report n, n_rare_A, n_rare_B, A anyway.

## Seeds and budget
N1 **4848**, calibration **4849**, power **4850**, N2 **4851**, sensitivities **4852**.
In-tool wall 540 s; outer `timeout 600`. `--smoke` (small R) runs only after this push,
output `analysis/k048_smoke.json`, not used for decisions.

## Gates and controls (written before the run)
1. **Match-function fixture** (`tools/k048_rare_label_concordance.py fixture`, no data): `B`=`B`
   matches, `K`≠`B`, empty excluded not matched; `S`=`S` matches, `Z`≠`S`, `TIE`≠`S`; dual-rare
   count on a tiny hand example; hypergeometric edge (0 rares → A = 0). Majority extraction is
   re-checked against K047's cases. The tool **refuses to write results** if any case fails.
2. **Copy-all positive control:** set B's rare-status := A's rare-status on the real units
   (`B_rare[i] := A_rare[i]` for all i, so margins match exactly); then A must equal n_rare_A and
   p must be < α (null R = 2 000). If not recovered, that pair-field is **tool excluded**.
   If n_rare_A = 0, skip as DEGENERATE rather than tool-excluded.
3. **Calibration FPR (seed 4849):** 1 000 fake observations, each a fresh N1 permutation, scored
   against the stored N1 bank; FPR = share with p < α. Gate **≤ 0.08**.
4. **Structural FPR (shift control):** every cyclic offset k of B's labels along the unit order
   with min(k, n−k) ≥ ⌈0.1 n⌉, scored against the N1 bank. Gate **≤ 0.08**.
5. **Power (seed 4850):** 200 replicates. Base = a random N1 permutation of B. Then, among units
   where A is rare, overwrite B to rare on a random subset of size max(1, round(0.50 × n_rare_A))
   when n_rare_A ≥ 1 (a 50 % sharing plant of A's rare marks). p from a fresh N1 bank (R = 2 000).
   Bar **≥ 0.5**. Descriptive curve at share fractions 0.25, 0.50, 0.75, 1.00 (100 replicates each),
   labelled descriptive. Degenerate pair-fields skip FPR/power and take verdict DEGENERATE.

Why 50 % of A's rares (not K047's 25 % of all units): K047's plant mostly recopied the majority
class (`K` or `Z`) and could not move the needle. The question now is whether shared *rare* marks
would be visible; plant those marks. Copy-all is the f = 1 end of that idea implemented as an
exact rare-status copy (every A-rare unit is rare on B, and every A-non-rare unit is non-rare on B).

## Decision rules (per pair-field)
1. **Excluded (cycle)** if the hash differs, the fixture fails, or the K019 consistency gate fails.
2. **DEGENERATE** if either side has 0 rares or is all-rare on the n units.
3. **TOOL EXCLUDED** if the copy-all control fails, or calibration FPR > 0.08, or shift FPR > 0.08.
4. **NOT TESTABLE** if power at the 50 % rare-share plant < 0.5, or n < 10, or n_rare_A + n_rare_B < 2.
5. **SUPPORTED** if p < 0.008333 and rules 2–4 do not fire.
6. **NOT SUPPORTED** (a real negative at the stated power) if p ≥ 0.008333 and rules 2–4 do not fire.

## What this cannot decide (confounds named in advance)
- **Recorder coding of "broken vs unfinished vs knotted":** Ascher, Urton and Pereyra may use `B`,
  `U` and `K` differently. A negative may be a coding disagreement, not a different object; a
  positive may be a shared coding habit rather than a shared break.
- **Breakage can change** between two recordings of the same object (a cord can break after the
  first record, or a broken end can be repaired in the notes). Two copies can also share a rare
  S-knot habit without being the same object. A SUPPORTED result leans toward "same object" or
  "shared rare-mark habit"; it does not prove either. A NOT SUPPORTED result does not prove
  different objects.
- **KH0586 knot directions** were all `Z` at khipu level in K047's coverage, so H_D on Paris·Lima
  is expected DEGENERATE (n_rare_B = 0 for `S`).
- Same data: the pairs and alignment are K018/K019's; K048 is not a re-test of their values, of
  K046's colours, or of K047's overall equality statistic.
- **K047 already peeked** descriptively at broken-end coincidence (they sat at the equality-test
  null floor). That is not a verdict, and K048's statistic is different (dual-rare count, not
  overall matches). The hypothesis stays one-sided excess.
- No decipherment is claimed.

## Disclosed, not verdicts
- Units with leaders included; only units whose aligned value ≠ 0; N2 within-group p.

## Next (depends on the result)
- If any primary pair-field is SUPPORTED: that is a new, value-independent witness on the rare
  marks and should be stated with the recorder-coding caveat; a colour code-association test on
  the K046 cross-tabs would still be same-data and must stay exploratory.
- If NOT SUPPORTED with power: shared rare marks are not visible on that pair-field under OKR
  codes; recorder effects and genuine non-overlap remain the leading alternatives to state.
- If DEGENERATE / NOT TESTABLE / TOOL EXCLUDED: say why. The rare-label fork may then be closed
  as not readable rather than as a negative.

## Output
`analysis/k048_results.json` (`analysis/k048_checkpoint.json` while running), log `analysis/k048_run.log`.
Run from `expeditions/khipu/`: `timeout 600 python3 tools/k048_rare_label_concordance.py run`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04


---

## Results (2026-11-08, run ~06:52 PT, America/Vancouver)

Run after the prereg was published as `b26aba4` (connector `push_files`; `git push` had no
credentials; local clone aligned with `git reset --mixed origin/main`, same tree, never `--hard`).
Full run **4.2 s** wall (nothing was cut by the wall). Output
[`analysis/k048_results.json`](../analysis/k048_results.json), log
[`analysis/k048_run.log`](../analysis/k048_run.log). No `--smoke` decision numbers were used.

### Gates (cycle-level)
- DB hash matches; **fixture 27/27 passed** (16 dual-rare identity/mismatch cases, hand-example
  count, equality ≠ dual-rare, three hypergeometric-edge cases, six majority-extraction cases);
  **K019 consistency passed** (13/89, 14/37, 15/36).

### Primary pair-fields (α = 0.00833)

| Pair-field | n | n_rare_A / n_rare_B | A | Null mean ± sd · max | p | Power f=0.50 | Copy-all | Cal / shift FPR | **Verdict** |
|---|---|---|---|---|---|---|---|---|---|
| KH0097·KH0586 termination (H_T) | 87 | 4 / 1 | 1 | 0.0457 ± 0.209 · 1 | 0.0458 | 0.945 | recovered (A=4, p 0.00050) | 0 / 0 | **NOT SUPPORTED** |
| KH0097·KH0586 knot dir (H_D) | 82 | 18 / 0 | 0 | — | — | — | — | — | **DEGENERATE** (B all `Z`) |
| KH0192·KH0470 termination (H_T) | 37 | 1 / 3 | 0 | 0.0837 ± 0.277 · 1 | 1.000 | 0.00 | **failed** (A=1, p 0.0305) | 0 / 0 | **TOOL EXCLUDED** |
| KH0192·KH0470 knot dir (H_D) | 27 | 0 / 6 | 0 | — | — | — | — | — | **DEGENERATE** (A 25 `Z` + 2 `TIE`, no `S`) |
| KH0192·KH0469 termination (H_T) | 36 | 3 / 2 | 0 | 0.167 ± 0.386 · 2 | 1.000 | 0.06 | recovered (A=3, p 0.00050) | 0.005 / 0.034 | **NOT TESTABLE** |
| KH0192·KH0469 knot dir (H_D) | 21 | 0 / 2 | 0 | — | — | — | — | — | **DEGENERATE** (A all `Z`) |

Power curves (share fractions 0.25 / 0.50 / 0.75 / 1.00; descriptive) for the three non-degenerate
fields: Paris·Lima termination 0.04 / 0.98 / 1.00 / 1.00; KH0192·KH0470 termination 0 / 0 / 0 / 0;
KH0192·KH0469 termination 0 / 0.04 / 0.04 / 1.00.

Label counts on the usable units. Paris·Lima termination: A 83 `K` + 4 `B` (2 units excluded,
empty on A); B 85 `K` + 1 `B` + 1 `U`. KH0192·KH0470 termination: A 36 `K` + 1 `B`; B 34 `K` + 3
`B`. KH0192·KH0469 termination: A 33 `K` + 3 `B`; B 34 `K` + 2 `B`.

### Why the readable tests look like this
- **One powered negative.** Paris·Lima H_T has four broken ends on the Ascher side and one on the
  HP side. They coincide once (A = 1 vs hypergeometric expectation 4 × 1 / 87 = 0.0460; null mean
  0.0457, p 0.0458). That is larger than the floor (0) but nowhere near α = 0.00833: with n_rare_B
  = 1, A is 0 or 1, and P(A = 1) = 4/87 ≈ 0.046. The 50 % rare-share plant (k = 2 of A's 4 `B`s)
  is recovered at power 0.945, so this is a **real negative** at the stated power, not an
  underpowered silence. The single dual-rare unit is a zero-value cord (group pair 10, positions
  7 and 9).
- **Copy-all vs Bonferroni, KH0192·KH0470 termination.** After copying A's rare-status onto B the
  margins are 1 `B` + 36 non-`B`. Identity (A = n_rare_A = 1) under N1 occurs only when that single
  `B` stays put, with probability 1/37 ≈ 0.027; the observed copy-all p was 0.0305, above
  α = 0.00833, so the pre-registered gate fired. The plant curve is 0 at every share fraction
  including f = 1.00: with n_rare_A = 1, even forcing that one mark to be shared gives
  P(A ≥ 1) ≈ n_rare_B / n, which stays above Bonferroni α. This is the same mechanical limit K047
  documented on a 36+1 equality margin, not a sign that the match function is broken (copy-all A
  did equal n_rare_A). Had the copy-all gate not fired first, the pair-field would have been NOT
  TESTABLE on power 0.00.
- **KH0192·KH0469 termination is visible only at a full share.** Copy-all and both FPR gates pass,
  but the 50 % plant (k = 2 of A's 3 `B`s) has power 0.06. The descriptive curve reaches 1.00 only
  at f = 1.00. Observed A = 0 (the floor) against a null mean of 0.167, p = 1.000 — a description,
  not a verdict.
- **H_D is degenerate on all three pairs.** Paris·Lima: every usable HP direction is `Z` (n_rare_B
  = 0), as K047's coverage predicted. Both Berlin pairs: Ascher's KH0192 has no `S` majority on the
  aligned usable units (25 `Z` + 2 `TIE` against KH0470; 21 `Z` against KH0469).

### Disclosed, not verdicts
- **Leaders.** Paris·Lima termination with leaders: n 100, n_rare 4 / 1, A = 1, p 0.0386. Both
  Berlin termination tests stay at A = 0 (p 1.0) with leaders (n 51 each). Knot direction stays
  degenerate with leaders on Paris·Lima (B still all `Z`). With leaders, both Berlin knot-direction
  fields become non-degenerate because one Ascher leader is `S`: KH0192·KH0470 1 dual-rare vs
  expectation 0.220, p 0.224; KH0192·KH0469 1 vs 0.306, p 0.310.
- **Non-zero-value units.** Paris·Lima termination becomes degenerate (n 81; n_rare_B = 0): the
  single HP broken end, and therefore the single dual-rare unit, was the zero-value cord named
  above. Both Berlin termination tests are likewise degenerate on non-zero-value units (KH0192·KH0470:
  n_rare_A = 0; KH0192·KH0469: n_rare_B = 0). Knot direction stays degenerate (no `S` on at least
  one side).
- **N2 (within-group).** Paris·Lima termination p 0.146 (null mean 0.146); both Berlin termination
  tests p 1.0 (N2 null mean 0: the broken ends of A and B never fall in the same matched group).

### Reading
No primary pair-field is SUPPORTED. H_D cannot be read: one side has no `S`-majority cords on every
pair. H_T is a real negative on Paris·Lima (one broken-end coincidence, consistent with the
hypergeometric chance of 4/87, at power 0.945), tool-excluded on KH0192·KH0470 (a single Ascher
`B` cannot beat Bonferroni α even under copy-all), and not testable on KH0192·KH0469 (power 0.06
at the 50 % plant). The K047 descriptive peek that broken ends sat at the equality-test floor is
not recycled as a verdict here: Paris·Lima's dual-rare count is 1, not 0, and that 1 does not
survive α. This does **not** say the records are different objects, and it does not say they are
the same object. It says the rare-mark witness we named is either unreadable or, where readable,
does not show extra dual-rare alignments. No decipherment.

### Next (line 6)
The rare-label concordance fork is answered as far as these OKR fields allow on these three pairs
(not as a blanket negative — as one powered negative and five unreadable pair-fields). A colour
code-*association* test on the K046 cross-tabs remains same-data and must stay labelled
exploratory if run. Line 6's colour and physical-feature questions on the K019 pairs are now
mapped.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
