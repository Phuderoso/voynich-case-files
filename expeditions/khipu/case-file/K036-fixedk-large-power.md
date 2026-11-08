# K036 · Fixed-K=10 000 F1 scan and large-only power curve m ∈ {4, 6, 8} (README line 1)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Why
K035 found that silence is readable against stronger effects only (m* small = 4, mid = 3 fragile, large none
at m ≤ 4), and that a fresh adaptive Monte Carlo seed swaps **KH0420 ↔ KH0478** at the F1 BH boundary
because the adaptive cut (K₀ = 1 000, escalate if p ≤ 0.01) changes which boundary names get K = 10 000.
K034 already confirmed KH0420 under a held-out L-window that ignores the BH ranking. Line 1's next step is
to remove that seed sensitivity and to push the large-stratum power curve past m = 4.

Two primaries, same cycle:

- **Primary A — Fixed-K F1 scan.** Re-run F1 (D5w, pooled exchangeable min-p, BH q = 0.05 over pop = 378)
  with a **fixed K = 10 000 draws for every khipu** (no adaptive cut / no K₀ stage). Compare F1 membership
  to K033 (seed-adaptive) and K035 (fresh adaptive). Hypothesis: fixed K removes the KH0420↔KH0478-type
  boundary swap; report overlap and any remaining swaps with MC uncertainty (p ± se, se from count/K).
- **Primary B — Large-only power curve.** BH-level F1 power for the **large stratum only**, planted
  within-group exact-sum count **m ∈ {4, 6, 8}** (same `plant_within_m` as K035). Find
  m*_large = smallest m with power ≥ 0.5 (n ≥ 30). If none → not testable even at m = 8.

## Data and strata (fixed; identical to K031–K035)
OKR `khipu.db` @ `4039ca5` (SHA-256 `60791303…`), level-1 pendants, `DUPLICATE_FLAG` dropped, ≥ 10 nonzero
pendants (457). Groups = runs of consecutive pendants sharing `CLUSTER_ID`. pop = ≥ 2 groups of size ≥ 4
(378); thirds by pendant count (small / mid / large, 126 each); S0 = 79.

## Detector and p
D5w scoring and pooled exchangeable min-p **unchanged** from K033/K035
(`tools/k033_pooled_minp_rescan.py`, `tools/k035_bh_power_multiplant.py`). Only the Monte Carlo schedule
changes: **fixed K = 10 000 for every khipu** on real, null, and power stages (no K₀ / no escalation).
Tool computes D5w only (F1 family); unrestricted D5 is out of scope this cycle. Code:
`tools/k036_fixedk_large_power.py`.

## Families (q = 0.05)
- **F1 (primary):** D5w BH over pop (378), as K033/K035.

## Plants (seed 3632; Primary B)
For each large-stratum khipu and each m ∈ {4, 6, 8}: a fresh within-khipu permutation, then m within-group
exact-sum windows inserted with K035's `plant_within_m` (A_within / B_within with probability ½). BH-level
power = the plant's pooled p inserted in place of that khipu's real p in the real F1 family.

## Calibration (seeds 36310–36314)
Five structure-preserving null corpora (each khipu replaced by a within-khipu permutation, groups kept),
scored under the **same fixed K = 10 000**.
- FPR gate (α 0.05) for pop and large: exact one-sided binomial P(X ≥ x | n, 0.05) ≥ 0.05.
- BH gate for F1: at most 1 of 5 null corpora with any discovery.

## Real scan (seed 3630)
Fixed-K F1 scan; membership compared to K033's and K035's published F1 lists. p reported with Monte Carlo
count and SE ≈ √(p(1−p)/K) (K = 10 000; pooled construction uses denominator K+1 for the observed rank,
so se uses that denominator).

## Decision rules (written before any run)
1. **Excluded** if F1's BH gate fails or the pop / large FPR gate fails under fixed K.
2. Fixed-K F1 list is the **new reference list for line 1** iff the gate passes; report vs K033/K035
   shared / swapped. Do **not** claim new discoveries unless a khipu appears that was in neither prior list
   **and** passes a pre-registered holdout (no holdout invented this cycle — just flag candidates).
3. For large: if m*_large ∈ {4, 6, 8} → silence readable against ≥ m* planted within-group sums in large;
   else **not improved / not testable** at these m.
4. Wall clock: stop at ~560 s if needed; publish partial.
5. Negatives published.

## Seeds
scan 3630, nulls 36310–36314 (base 3631), power 3632 (distinct from K031–K035: 3130–3532).

## No claims
A BH hit means "more within-group adjacent exact sums than chance in this khipu under D5w"; a readable
negative means "no excess as large as m* planted sums", never "no arithmetic". No decipherment is claimed.

## Results

Run 2026-11-08 ~02:00 PT (America/Vancouver). Compute finished in **396.6 s** after
prereg `b7d7bf1` (all 126 large khipus reached; `power_capped` false; wall 560 s not
hit). Output: [`analysis/k036_results.json`](../analysis/k036_results.json).

### 1. Calibration — F1 gate passes
| Stratum | n (5 corpora) | D5w FPR | binomial P(≥x) |
|---|---|---|---|
| S0 | 395 | 0.0329 | 0.9601 |
| small | 630 | 0.0238 | 0.9997 |
| mid | 630 | 0.046 | 0.7016 |
| large | 630 | 0.0349 | 0.9716 |
| pop | 1 890 | 0.0349 | 0.9993 |

BH discoveries per null corpus: **F1 0/0/0/0/0.** Gate F1 passes (at most 1 of 5
allowed). Every listed FPR gate passes (`gate_pass` true for S0, small, mid, large
and pop).

### 2. Primary A — Fixed-K F1 scan (reference list adopted)
F1 = **14** (D5w BH over pop = 378, fixed K = 10 000, denom 10 001 for every p).
Twelve sit in large and two in small (KH0395/UR155, KH0420/UR182); mid still has
none.

| Khipu | p | cnt | se | stratum |
|---|---|---|---|---|
| KH0322/UR086 | 0.00069993 | 7 | 0.000264 | large |
| KH0395/UR155 | 0.00109989 | 11 | 0.000331 | small |
| KH0420/UR182 | 0.00139986 | 14 | 0.000374 | small |
| KH0428/UR190 | 0.00099990 | 10 | 0.000316 | large |
| KH0478/UR242 | 0.00109989 | 11 | 0.000331 | large |
| KH0491/UR255 | 0.00009999 | 1 | 0.0001 | large |
| KH0492/UR256 | 0.00069993 | 7 | 0.000264 | large |
| KH0502/UR266 | 0.00089991 | 9 | 0.0003 | large |
| KH0504/UR267B | 0.00039996 | 4 | 0.0002 | large |
| KH0506/UR269 | 0.00039996 | 4 | 0.0002 | large |
| KH0507/UR270 | 0.00059994 | 6 | 0.000245 | large |
| KH0511/UR273B | 0.00159984 | 16 | 0.0004 | large |
| KH0513/UR274B | 0.00019998 | 2 | 0.000141 | large |
| KH0514/UR275 | 0.00029997 | 3 | 0.000173 | large |

Overlap with the published F1 lists:
- shared with K033 = 11 (K033's whole F1 list); `only_K033` is empty
- shared with K035 = 11 (K035's whole F1 list); `only_K035` is empty
- in K033 not K035: KH0420/UR182; in K035 not K033: KH0478/UR242
- `only_K036` = `candidates_new` = KH0502/UR266, KH0511/UR273B

So the K033 ∪ K035 F1 union (12 names) is a subset of K036, plus two new
candidates. The KH0420 ↔ KH0478 adaptive-cut swap is **resolved: both are in the
fixed-K list.**

**Not claimed as discoveries.** KH0502/UR266 (p 0.00089991, cnt 9, se 0.0003) and
KH0511/UR273B (p 0.00159984, cnt 16, se 0.0004) are flagged as candidates pending
a pre-registered holdout (none was invented this cycle). K035 already named both
descriptively under stratified BH (p 0.0021 / 0.0019) as not-F1; they now enter
the adopted fixed-K F1 list and remain unconfirmed.

### 3. Primary B — Large-only BH-level F1 power, m ∈ {4, 6, 8}
Decision uses `bh_F1`, not the raw p ≤ 0.05 rate.

| m | n | p ≤ 0.05 | BH-level F1 power |
|---|---|---|---|
| 4 | 125 | 0.76 | 0.416 |
| 6 | 124 | 0.9516 | **0.6532** |
| 8 | 124 | 0.9758 | 0.7823 |

n is 125 / 124 / 124 rather than 126 because a few plants could not place m
windows (not enough eligible within-group slots). `power_khipus_reached` = 126;
`power_capped` = false.

m*_large = **6** (smallest m with BH-level F1 power ≥ 0.5 and n ≥ 30).

### Reading
- **Verdict: silence readable against ≥ 6 within-group sums in large.** A silent
  large khipu is a readable negative against an excess as strong as 6 planted
  within-group exact-sum windows, not against K033's m = 2 (and not yet at m = 4,
  where power is 0.416). Readable silence never means "no arithmetic".
- Fixed-K F1 is the **new reference list for line 1** (14 names). The adaptive-cut
  boundary swap is gone.
- Two extra names are candidates, not discoveries.
- Pre-registered decision: **gate_F1 passed; m*_large = 6; reference list
  adopted.**

### Next (line 1)
K037: held-out confirmation of KH0502/UR266 and KH0511/UR273B on the K034 design
(longest within-group exact-sum window L versus a within-khipu permutation). No
new test is invented.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
