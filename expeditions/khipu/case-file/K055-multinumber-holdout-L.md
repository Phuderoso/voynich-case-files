# K055 · Do the four frozen held-out L confirmations survive the multi-number (R5) mask?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K055 confirmation p-value, FPR or power number was computed.

## Why
K054 R5-masked the frozen K036 F1 / D5w scan: 13 of 14 names survive. KH0511/UR273B dropped as an
R5-score-invariant BH-boundary case (statistic unchanged at 3.20; p 0.00160 → 0.00210). K054 explicitly
said: "K037 had already noted that this name rests on a single 3-cord window (LOO → 0); that holdout is a
different test and was not rerun."

The four F1-only names already carry a held-out confirmation under the unmasked longest within-group
exact-sum window L (K034 for KH0322 and KH0420; K037 for KH0502 and KH0511). This cycle asks whether
those **frozen confirmation tests** themselves survive the same K008 multi-number mask. It is a
**sensitivity rerun of frozen confirmation tests**, not a redesign and not a new discovery scan. No new
name is added or dropped. The decision does not consult any BH list or D5w ranking.

Same-data caveat: a reanalysis of the same pinned corpus, not an independent replication.

## Named targets (frozen; do not add or drop)
1. KH0322 / UR086 — K034, L = 8, p = 0.0014 (K054: 0 R5 pendants; D5w scan survives)
2. KH0420 / UR182 — K034, L = 8, p = 0.00020 (K054: 3 R5; D5w statistic unchanged at 2.07; scan survives)
3. KH0502 / UR266 — K037, L = 3, p = 0.01465 (K054: 10 R5; D5w 6.81 → 3.56; scan survives; lost under masked D2 in K053). Close to α = 0.025, so the mask may matter.
4. KH0511 / UR273B — K037, L = 3, p = 0.00195 (K054: 3 R5; D5w unchanged; dropped from the BH list). The scientifically sharp case.

OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`),
level-1 pendants, same group definition as K031–K037 (`CLUSTER_ID` runs), duplicate-flagged khipus excluded
and khipus with < 10 nonzero pendants dropped, exactly as in K034/K037.

## Primary statistic L (per khipu; frozen)
**Longest within-group exact-sum window.** L = max k ∈ {2,…,12} such that some pendant with value ≥ 10
equals the sum of k consecutive neighbours that lie entirely inside the same group, with ≥ 2 nonzero
summands. The within-group adjacency mask is identical to D5w's `valid_masks` (K034/K037). L is a
**scalar**, and the decision does **not** consult any BH list or D5w ranking.

## R5 cord and mask (K007/K008, as K054)
- **R5 cord:** at least two knot clusters with a single decimal place, and those places, read in
  `knot_cluster.ORDINAL` order, are not strictly decreasing.
- **Mask (structure-preserving):** an R5 pendant keeps its position but is never a sum target and never
  part of a summand block. The null permutes only non-R5 values among non-R5 positions; group ids stay put.

With an empty mask the masked detector must reproduce unmasked L (G0).

## Null and p-value
Masked within-khipu permutation (N1 above). R = 20 000 for the confirmation p-values.

    p = (1 + #{null draws with L ≥ L_obs}) / (1 + R).

## Decision rule (original confirmation α; not a new four-way discovery)
Keep the original confirmation α_i = 0.025 (the threshold under which each name was confirmed).
**Do not** switch to Bonferroni × 4: this is a sensitivity of frozen tests, not a new four-way discovery.
Changing α would mix a multiple-comparison redesign into a sensitivity rerun.

Per name (frozen K034/K037 rule):
- **survives / still confirmed** iff masked p ≤ 0.025 and the FPR gate passes
- **no longer established** (not excluded) iff masked p > 0.025 and plant power ≥ 0.5
- **not testable** iff masked p > 0.025 and power < 0.5, OR the khipu cannot place a masked L
  (e.g. too few unmasked pendants) — said explicitly; not called a loss

A name that cannot be scored under the mask is not testable, not lost.

Overall (written before any run):
1. All four survive → the holdout confirmations are **robust** to the mask
2. A proper subset survive → **PARTIAL** (name who drops and why)
3. None survive and all are testable → none remain established under the mask
4. FPR gate fails → **EXCLUDED** (no confirmation claimed)
5. None survive and at least one is not testable → report each name individually; do not claim the set
   is established or that all are lost

## Gates
### G0 fixture (stop on failure)
DB hash matches the manifest; 3 069 R5 cords; four named targets load; with an empty mask the masked
code reproduces each name's published unmasked L (KH0322 L = 8, KH0420 L = 8, KH0502 L = 3,
KH0511 L = 3); R5-free named khipus (KH0322 has 0 R5) reproduce L under the real mask too.

### G1 FPR (seed 5555)
200 random multi-group pop khipus (≥ 2 groups of size ≥ 4) other than the four named. For each, one
masked-within-khipu permutation is a null "observed"; its L p-value vs R_fpr = 5 000 fresh masked
permutations. FPR = fraction with p ≤ 0.025. **Pass** iff FPR ≤ 0.08 (same gate as K034/K037).
Report binomial P(X ≥ x | n = 200, 0.05).

### G2 power (seed 5554)
Per named khipu, N = 200 plants: masked-permute, then plant one within-group exact sum of length
k = 6 inside a group of size ≥ 8, restricted so target and summands are all non-R5 (a block the masked
detector can see). Fallback k = 5 in a group of size ≥ 7 if needed, still all non-R5. Each plant scored
with R_pow = 5 000 nested masked permutations. Power = fraction with p ≤ 0.025. Required ≥ 0.5 for a
negative to be readable. If a named khipu cannot place the plant, report and skip that name for G2
(do not silently lower the bar).

## Descriptive (not for the decision)
R5 pendant counts; unmasked L vs masked L; leave-one-group-out L after zeroing the group(s) that carry
the observed max-k hit (as K037 reported).

## Seeds
- 5550 KH0322 confirm
- 5551 KH0420 confirm
- 5552 KH0502 confirm
- 5553 KH0511 confirm
- 5554 power
- 5555 FPR

Distinct from K034 (3430–3433), K037 (3730–3733), K053 (5353–5355) and K054 (5454–5455).

## Tool
[`tools/k055_multinumber_holdout_L.py`](../tools/k055_multinumber_holdout_L.py), adapting K037's L
confirmation and K054's R5 definition + structure-preserving mask. `--smoke` runs the G0 fixture and a
synthetic toy (no real-data p-value). Output: `analysis/k055_results.json`.

## No claims
A surviving masked L means "this khipu's longest within-group exact-sum window, ignoring multi-number
cords, is still longer than chance under a masked permutation" — a property of the record. It is not a
reading of the khipu. No decipherment is claimed. A drop is a same-data sensitivity result, not an
exclusion of the original unmasked confirmation.

## G0 fixture (run before this commit; no p-value)
`--smoke` run 2026-11-08 ~12:10 PT (America/Vancouver), 0.4 s, from `expeditions/khipu/`:
`python3 tools/k055_multinumber_holdout_L.py khipu.db --smoke`. **G0 pass.** No confirmation
p-value, FPR or power number was computed.

- sha256 matches the manifest (`607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`)
- 3 069 R5 cords (the K007/K008/K054 count)
- four named targets load: KH0322/UR086 (107 pendants, 23 groups, 18 of size ≥ 4, **0 R5**);
  KH0420/UR182 (30 pendants, 7 groups, 4 of size ≥ 4, **3 R5**); KH0502/UR266 (132 pendants,
  36 groups, 22 of size ≥ 4, **10 R5**); KH0511/UR273B (114 pendants, 32 groups, 13 of size ≥ 4,
  **3 R5**). R5 counts match K054. Frames match K034/K037.
- empty-mask L reproduces each name's published unmasked L: KH0322 **8**, KH0420 **8**,
  KH0502 **3**, KH0511 **3**
- the one R5-free named khipu (KH0322) reproduces L = 8 under the real mask
- all four can place a masked L and can host a non-R5 k = 6 (or fallback k = 5) plant
  (structural check only)
- synthetic toy: a planted k = 6 within-group window is seen (L = 6); the same window vanishes
  (L = 0) when an R5 cord is placed in the block


## Results
*(section reserved; no confirmation, FPR or power number is written until after this pre-registration is committed)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
