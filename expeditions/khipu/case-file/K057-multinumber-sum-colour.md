# K057 · Do the frozen K021 sum-cord colour results survive the multi-number (R5) mask?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before the full K057 run.

## Why this line
The README's open lines are mostly paused: line 1's power fork and optional R5 steps are done
(K054, K055); line 2 was closed in the literature (K043) and its remaining unmasked sum counts
were audited in K056 (PARTIAL: K040's pooled G no longer established; the singleton-total form
survives); line 3's lead waits for new OKR data (rechecked 2026-11-08 ~13:36 PT: OKR still
`4039ca5`, 2026-08-04, nothing newer); line 4 waits on the filing connector; line 7 needs khipus
outside the OKR. Line 8's stated job is "rerun with the multi-number pendants masked, and report
whether any result changes". After K053–K056 the remaining unmasked sum-adjacent result named
in the README is **K021's sum-cord colour test** (a colour test on K001 sum cords, not a sum
count). K056's journal pointed at the same crate.

K021 asked whether colour marks which cords are sums, on the ten K001 BH-significant khipus
(primary) and on every khipu with a sum cord (secondary). **H2 (shared colour) was supported**
in both populations (primary T2 = 416 vs 229.5, p < 10⁻⁴, FPR 0.01, power 0.98; secondary
T2 = 782 vs 612.5, p < 10⁻⁴). **H1 (colour boundary) was a powered negative** (p 0.19, power
1.00) and is not retested, matching K056's rule of leaving published negatives alone. The
shared-colour finding is already described as a Khipu Field Guide field mark; K057 only asks
whether that calibrated count depends on multi-number cords. Same-data caveat: a reanalysis of
the same pinned corpus, not an independent replication.

## Frozen targets (published value → tested under the mask)
| Target | Source | Published | α (kept) |
|---|---|---|---|
| T1 primary H2 | K021 primary (10 K001 BH-significant khipus) | T2 = 416 vs 229.5, p = 5.0×10⁻⁵ (R 20 000) | 0.025 |
| T2 secondary H2 | K021 secondary (245 khipus with a sum cord) | T2 = 782 vs 612.5, p = 5.0×10⁻⁵ | 0.025 |

K021 H1 (boundary) is not retested. The disclosed post-hoc within-group null from K021 is not
re-run as a decision test (it can weaken but not upgrade, and was never pre-registered).

Data: OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`);
level-1 pendants; `DUPLICATE_FLAG` khipus dropped. Primary population frozen as the ten K001
BH-significant khipus (KH0359, KH0405, KH0491, KH0492, KH0503, KH0504, KH0506, KH0507, KH0513,
KH0514), kept even if a khipu loses every legal sum cord. Secondary population: every khipu
with at least one *masked* sum cord (K021's construction, applied after the mask).

## Statistic (frozen, K021)
- **Sum cords** are the K001 hits: a level-1 pendant with value ≥ 10 that equals the sum of
  the next or previous k = 2..12 pendants, with at least 2 of them nonzero.
- **Eligible cords** are level-1 pendants with value ≥ 10 and a known colour (and, under the
  mask, non-R5, because an R5 cord cannot be a target).
- **Cord colour** is `FULL_COLOR` of the `ascher_cord_color` row with the smallest `RANGE_BEG`
  (ties: smallest `color_id`). Cords with no colour row are excluded.
- **T2** = number of same-colour pairs among the sum cords, summed over khipus. A khipu with
  fewer than two sum cords contributes 0.

## R5 cord and mask (K007/K008, exactly as K053–K056)
- **R5 cord:** ≥ 2 knot clusters with a single decimal place, and those places, read in
  `knot_cluster.ORDINAL` order, are not strictly decreasing (3 069 cords).
- **Mask:** an R5 pendant keeps its position but is never a sum-cord target and never inside
  a matching summand window. A K001 window (pendant i, side, k) is legal iff i is non-R5 and
  no pendant of that window is R5. The masked sum-cord set is the frozen K001 detector
  restricted to legal windows.
- **Null:** colour sequence untouched. In each replicate, the same number of (masked) sum
  cords is drawn uniformly without replacement from that khipu's eligible cords. R = 20 000.
  p = (1 + #null ≥ obs) / (1 + R). A khipu with m = 0 contributes 0 to observed and null.

## Gates
- **G0 fixture (stop on failure):** hash matches; 3 069 R5; 53 750 colour cords; with an
  **empty mask** the code reproduces K021's observed counts: primary n = 10 / 95 / 1 005,
  T1 = 35, T2 = 416; secondary n = 245 / 724 / 10 414, T1 = 290, T2 = 782. (T1 is a fixture
  check only.)
- **G1 FPR:** 200 masked redraws of the sum-cord labels among eligible cords, scored against
  the stored masked null; FPR at α = 0.025 must be ≤ 0.05 (K021's bar) for each target.
- **G2 power:** 200 masked redraws, each with K021's H2 plant (every drawn "sum cord" is
  swapped, with probability 0.5, for a remaining eligible cord of that draw's most common
  colour). Power at α = 0.025; bar ≥ 0.5.

## Decision rule (per target; written before the run)
- **survives** iff masked p ≤ 0.025 and the FPR gate passes;
- **no longer established** (not excluded) iff masked p > 0.025 and power ≥ 0.5;
- **not testable** iff masked p > 0.025 and power < 0.5, or the wall cuts calibration;
- **excluded** iff the FPR gate fails.

Overall: both survive → **ROBUST**; one survives → **PARTIAL** (name which and why); neither
survives and both are powered → **NONE ESTABLISHED**; otherwise per target. Descriptive (not
a test): how many published colour-eligible sum cords in the primary ten are removed because
the target itself is R5, or because every matching window holds an R5 cord.

## Seeds, wall
Primary null 5757, FPR 5758, power 5759; secondary null 5760, FPR 5761, power 5762.
WALL 540 s in the tool; outer `timeout 600`. Tool:
[`tools/k057_multinumber_sum_colour.py`](../tools/k057_multinumber_sum_colour.py)
(SHA-256 `9721a051db3dd3f453dbf389f33baf69fa70cc3be3d732d60129b4cc6e41bd44`).
Output `analysis/k057_results.json`, log `analysis/k057_run.log`.

A `--g0-only` fixture check (empty mask, no null, no masked p-value) was run before this
file was committed, solely to confirm the code reproduces K021's published counts. It
printed those already-published numbers and no masked statistic. Nothing in the design
above was changed after that check. The tool committed with this pre-registration is the
byte-identical file that was G0-checked (hash above).

## No claims
No decipherment is claimed. Shared sum-cord colour on several Inkawasi khipus is already a
Khipu Field Guide field mark. K057 only asks whether K021's calibrated shared-colour counts
depend on multi-number cords.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
