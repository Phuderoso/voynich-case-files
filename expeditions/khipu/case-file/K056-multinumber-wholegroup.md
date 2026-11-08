# K056 · Do the frozen whole-group-sum results survive the multi-number (R5) mask?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before the full K056 run (see the smoke disclosure below).

## Why this line
The README's open lines are mostly paused: line 1's power fork is closed and its optional R5 steps are done
(K054, K055); line 3's lead waits for new OKR data (rechecked 2026-11-08 ~12:47 PT: OKR still `4039ca5`, so no
holdout); line 4 waits on the filing connector; line 7 needs khipus outside the OKR. Line 8's stated job is
"rerun with the multi-number pendants masked, and report whether any result changes". It was scoped to K001–K006,
and the later cross-khipu cycles (K017–K020) already zero R5 cords, but the **whole-group-sum results of line 2
were computed on plain sums with no R5 mask**: K025 (KH0359/UR119 and KH0405/UR166, G = 4 each, p < 10⁻⁴), K040 H1
(holdout corpus G = 23 vs 14.1, p = 0.0162) and K042 H1 (singleton-total count G_s = 10 vs 1.73, p ≈ 10⁻⁴). Those
are the only supported sum results in this expedition that never faced the K008 mask. K056 is that audit: a
**sensitivity rerun of frozen tests**, not a redesign. No target is added or dropped, and no α is changed.

Same-data caveat: a reanalysis of the same pinned corpus, not an independent replication.

## Frozen targets (published value → tested under the mask)
| Target | Source | Published | α (kept) |
|---|---|---|---|
| T1 KH0359 / UR119 | K025 primary | G = 4, p = 5.0×10⁻⁵ (R 20 000) | 0.025 |
| T2 KH0405 / UR166 | K025 primary | G = 4, p = 5.0×10⁻⁵ | 0.025 |
| T3 holdout corpus G (367 khipus, KH0359/KH0405 held out) | K040 H1 | G = 23 vs 14.1067, p = 0.0162 (R 10 000) | 0.05 |
| T4 holdout singleton-total count G_s | K042 H1 | G_s = 10 vs 1.7338, p = 9.999×10⁻⁵ | 0.025 |

The K040 H2 and K042 H2 results were negatives (not supported) and are not retested.

Data: OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`);
level-1 pendants; `DUPLICATE_FLAG` khipus dropped; groups = runs of equal `CLUSTER_ID`; eligibility frozen
from K025/K040 (≥ 4 groups, ≥ 1 candidate pair, ≥ 1 pendant ≥ 10; 369 eligible, 367 holdout).

## Statistic (frozen, K025/K040/K042)
A whole-group sum is a pendant with value ≥ 10 equal to the sum of **all** pendants of the group immediately to
its left or right (that group ≥ 2 cords, ≥ 2 nonzero; the pendant is not in it). G = number of distinct such
pendants; G_s = those whose own group has size 1 (K042 `singleton_total`).

## R5 cord and mask (K007/K008, exactly as K053–K055)
- **R5 cord:** ≥ 2 knot clusters with a single decimal place, and those places, read in `knot_cluster.ORDINAL`
  order, are not strictly decreasing (3 069 cords).
- **Mask:** an R5 pendant keeps its position but is never a target and never inside a summand group. A
  candidate pair (pendant i, group s:e) is legal iff i is non-R5 and no pendant of s:e is R5. The masked
  statistic is the frozen statistic restricted to legal pairs.
- **Null:** permute only non-R5 values among non-R5 positions, within khipu; group ids stay put.
  T1/T2 R = 20 000 (K025); T3/T4 R = 10 000 summed over the holdout khipus (K040/K042).
  p = (1 + #null ≥ obs) / (1 + R). A holdout khipu with no legal pair contributes 0 to observed and null.

## Gates
- **G0 fixture (stop on failure):** hash matches; 3 069 R5; 369 eligible / 367 holdout; with an **empty mask**
  the code reproduces KH0359 G = 4, KH0405 G = 4, holdout G = 23 and G_s = 10.
- **G1 FPR:** T1/T2: 200 masked within-khipu shuffles scored against the stored masked null, FPR at α = 0.025
  must be ≤ 0.05 (K025's bar). T3/T4: 200 masked corpus shuffles against the summed null, FPR at the target α
  must be ≤ 0.08 (K040/K042 gate).
- **G2 power:** T1/T2: 200 masked shuffles, each with **one** whole-group sum planted on a random legal pair
  (K025 plant; target and group all non-R5); power at 0.025. T3: m = 9 legal plants on disjoint spans across
  the holdout (K040 plant), power at 0.05. T4: m = 9 legal **singleton-total** plants (K042), power at 0.025.
  Bar ≥ 0.5 (n ≥ 30 for T3/T4).

## Decision rule (per target; written before the run)
- **survives** iff masked p ≤ α and the FPR gate passes;
- **no longer established** (not excluded) iff masked p > α and power ≥ 0.5;
- **not testable** iff masked p > α and power < 0.5, or no legal pair exists, or the wall cuts calibration;
- **excluded** iff the FPR gate fails.

Overall: all four survive → **ROBUST**; some survive → **PARTIAL** (name which and why); none survive and all are
powered → **NONE ESTABLISHED**; otherwise per target. Descriptive (not a test): which published hits touch an R5
cord (as target or inside the summed group).

## Seeds, wall
T1/T2 nulls 5650, FPR 5651, power 5652; corpus nulls 5653, FPR 5654, power G 5655, power G_s 5656. WALL 540 s in
the tool; outer `timeout 600`. Tool: [`tools/k056_multinumber_wholegroup.py`](../tools/k056_multinumber_wholegroup.py)
(SHA-256 `25fb1d29fe0a3b53ceb0c98ef928d271aecdbba9120f89026a0874ff4cfff30d`). Output `analysis/k056_results.json`,
log `analysis/k056_run.log`.

## Smoke disclosure
At ~12:48 PT (America/Vancouver) I ran `--smoke` (R 500 / 200, N = 10) as a syntax check **before** this file was
committed, and it printed provisional numbers. Nothing in the design above was changed after that: the tool committed
with this pre-registration is the byte-identical file that was smoke-run (hash above). Smoke numbers are not used for
any decision and are not published as results.

## No claims
No decipherment is claimed. Whole-group totals in UR119 are already counted by the Khipu Field Guide; K043 showed
the leftover singleton-totals are too. K056 only asks whether those calibrated counts depend on multi-number cords.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results

Run 2026-11-08 ~12:50 PT (America/Vancouver), after prereg commit `8687bab`. `timeout 600 python3
tools/k056_multinumber_wholegroup.py khipu.db`: **19.7 s** (tool wall 540 s not hit; nothing capped). Tool hash
at run time `25fb1d29…f30d` (identical to the committed file). Output
[`analysis/k056_results.json`](../analysis/k056_results.json), log [`analysis/k056_run.log`](../analysis/k056_run.log).

### G0 fixture — pass
Hash matches; 3 069 R5; 369 eligible / 367 holdout; empty mask reproduces KH0359 G = 4, KH0405 G = 4, holdout
G = 23, G_s = 10 (G_ns = 13).

### R5 load (descriptive)
KH0359/UR119 has 5 R5 pendants (legal pairs 47 → 39); KH0405/UR166 has none (10 → 10). The holdout has 1 328 R5
pendants in 177 of 367 khipus; 9 holdout khipus have no legal pair left (358 active). Of the 31 published hits
(8 primary + 23 holdout), **26 stay legal and 5 are removed by the mask**, all holdout and all *non-singleton*:

| Khipu | Total | Why removed |
|---|---|---|
| KH0225 | 10 | target is R5 |
| KH0090 | 10 | 1 R5 in the summed group |
| KH0080 | 98 | target is R5 |
| KH0489 | 21 | target is R5 |
| KH0509 | 10 | 2 R5 in the summed group |

All 8 primary hits and all 10 holdout singleton-totals are legal.

### Per target
| Target | Published | Masked obs | Masked null mean | Masked p | α | FPR (gate) | Power (bar 0.5) | Verdict |
|---|---|---|---|---|---|---|---|---|
| T1 KH0359 / UR119 | G 4, p 5.0×10⁻⁵ | 4 | 0.0134 (max 2) | 5.0×10⁻⁵ (floor) | 0.025 | 0.025 (≤ 0.05) | 1.00 (1 planted) | **survives** |
| T2 KH0405 / UR166 | G 4, p 5.0×10⁻⁵ | 4 | 0.00295 (max 1) | 5.0×10⁻⁵ (floor) | 0.025 | 0.010 (≤ 0.05) | 1.00 (1 planted) | **survives** |
| T3 holdout G (K040 H1) | 23 vs 14.1067, p 0.0162 | 18 | 12.7355 (sd 3.57) | **0.0955** | 0.05 | 0.035 (≤ 0.08) | 0.81 (m = 9, n 200) | **no longer established** |
| T4 holdout G_s (K042 H1) | 10 vs 1.7338, p 9.999×10⁻⁵ | 10 | 1.5118 (sd 1.22) | 0.00020 | 0.025 | 0.020 (≤ 0.08) | 1.00 (m = 9, n 200) | **survives** |

KH0405 has no R5 pendant, so its masked test equals the unmasked one up to Monte Carlo (it is a fixture-like check).

### Overall: **PARTIAL** (pre-registered rule 2)
Three of four frozen results survive: UR119's and UR166's four whole-group totals each, and K042's
singleton-total excess in the holdout. **K040's pooled leftover G is no longer established** under the mask
(18 vs 12.74, p 0.0955, with readable power 0.81 and FPR 0.035). It is not excluded: the gate passed, so this is a
powered sensitivity negative for the pooled count. The five hits the mask removes are all of the non-singleton
kind, the part K042 had already found to be at chance (G_ns 13 vs 12.33, p 0.46). So the mask doesn't create a
contradiction. It sharpens K042: the leftover whole-group signal that is robust to multi-number cords is the
singleton-total form (already counted by the Khipu Field Guide per K043). The pooled count's significance in K040
leaned partly on hits that sit on, or sum over, R5 pendants. Most of them are small totals of 10.

Same-data sensitivity on the pinned corpus; not an independent replication. No decipherment is claimed.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
