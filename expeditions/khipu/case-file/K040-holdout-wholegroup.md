# K040 · Held-out corpus-wide whole-group detector (README line 2 leftover)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results appended** (pre-registration written and pushed first as `6568b90`, before any K040 statistic was computed).

## Why
K025 closed line 2 for the two khipus that had prompted it: KH0359/UR119 and KH0405/UR166 each carry four whole-group totals (p < 10⁻⁴, power 1.00). A disclosed post-hoc, not pre-registered, then found that the rest of the corpus still had G = 23 against a null mean of 14.0958 (p = 0.0176), a smaller excess spread over many khipus, none of them BH-significant. Those two had been chosen because K001 flagged them, so the leftover number cannot be read as a confirmation.

K040 locks a decision rule on that leftover and adds what the post-hoc lacked: a holdout that drops the discovery pair from both the observed total and the null, a proper calibration of the corpus test, BH-level calibration of the per-khipu scan, and power at a leftover-sized plant. **This is not an independent replication.** It is the same OKR extract and the same G, now run under a rule written in advance, so the leftover can be called supported, not supported, not testable, or excluded instead of remaining a disclosed aside. No new statistic.

## Data (fixed; identical to K025)
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`,
verified before the run; the tool stops if the hash differs). Level-1 pendants, `DUPLICATE_FLAG` dropped.
Groups = runs of consecutive pendants sharing `CLUSTER_ID`. Eligible: at least 4 groups, at least one
candidate adjacent pair, and at least one pendant with value ≥ 10 (K025's secondary filter).

## Discovery set (held out of every test)
KH0359 (UR119) and KH0405 (UR166). They are excluded from the observed total, from every null, from
calibration, from plants, and from the BH scan. K025 published 369 eligible khipus, so the holdout
set must have 367. The tool also recomputes G on the holdout and **stops (excluded)** unless that
observed G equals K025's published leftover of 23 (same data, same definition: a wrong G would mean
the implementation drifted).

## Statistic, null and detector (copied from K025)
A **whole-group sum** is a pendant with value ≥ 10 that equals the sum of **all** pendants of the
group immediately to its right or immediately to its left, where that group has ≥ 2 cords, at least
2 of them nonzero, and the pendant is not itself in that group. G counts distinct pendants that
satisfy this (a pendant matching both sides counts once).

**Null:** permute pendant values within the khipu (K001's N1; group sizes and positions stay put),
independently across khipus, R = 10 000 (K025's secondary used 5 000). One-sided
p = (1 + #null ≥ obs) / (1 + R). Code: `tools/k040_holdout_wholegroup.py`.

## Hypotheses
- **H1 (primary).** Corpus-level G_holdout is larger than the sum of the within-khipu permutation
  nulls. This is the leftover excess, re-measured.
- **H2 (secondary).** The BH scan (q = 0.05) of per-khipu p-values on the holdout set finds at least
  one individually significant khipu. K025 reported none; this re-checks that under R = 10 000 and
  a BH false-discovery gate.

H1 and H2 are not Bonferroni-shared: H1 is the confirmatory question, H2 is secondary, as in K025.

## Controls
- **Calibration (seed 4041, N = 200):** one shuffled copy of every holdout khipu, scored against
  that khipu's stored nulls. Corpus FPR = share of those copies with p_corpus ≤ 0.05. BH-gate =
  share of copies in which BH calls at least one discovery. Gate passes at ≤ 0.08 (same bar as
  K034/K037's FPR gate).
- **H1 power (seed 4042, N = 200):** start from a fresh within-khipu permutation of the whole
  holdout (so no residual real structure), then plant one whole-group sum in each of m distinct
  plantable khipus (K025's plant: an adjacent eligible group is given a total ≥ 10 on a neighbouring
  pendant). Primary m = 9 (K025 leftover 23 − 14.1, rounded). Flanking m ∈ {5, 15} are descriptive.
  A replicate is a hit if the planted corpus total has p ≤ 0.05 against the stored null totals.
- **H2 power (same seed, N = 200):** among holdout khipus with at least 4 candidate pairs, pick one
  at random, permute it, and plant 4 disjoint whole-group sums (an UR119-strength concentrated
  extra). Other khipus are permuted without planting. A replicate is a hit if the planted khipu is
  BH-significant. Replicates that cannot place 4 disjoint plants are redrawn; the rate is used only
  if at least 30 replicates succeed. A disclosed add-on plants a single extra (m = 1) and records
  whether BH finds anyone, to show why a diffuse leftover would not appear in H2.

## Seeds and wall
Nulls seed **4040**, calibration **4041**, power **4042** (distinct from K031–K039: 3130–3939, and
from K025: 20261111). WALL = 520 s inside the tool; outer `timeout 560`. `--smoke` keeps the full
eligible set but uses R = 200, N = 10 (syntax check; output `analysis/k040_smoke.json`, not used
for decisions). Checkpoint every 20 khipus to `analysis/k040_checkpoint.json`.

## Decision rules (written before the run)
1. **Excluded** if the database hash differs, `analysis/k025_results.json` cannot be read, the
   discovery pair is missing, the eligible count is not 369 or the holdout count is not 367, or the
   observed holdout G is not 23.
2. **H1 excluded** if corpus FPR > 0.08.
3. **H1 not testable** if the m = 9 plant power is below 0.5 (n ≥ 30 required).
4. **H1 supported** if p_corpus ≤ 0.05 and rules 2–3 do not fire.
5. **H1 not supported** if p_corpus > 0.05 and the m = 9 plant power is ≥ 0.5.
6. **H2 excluded** if the BH-gate exceeds 0.08.
7. **H2 supported** if the holdout BH scan has at least one discovery and the gate passes; those
   names are reported.
8. **H2 not supported** if there are no BH discoveries and the 4-plant power is ≥ 0.5 (n ≥ 30):
   that is a readable negative against another UR119-strength khipu.
9. **H2 not testable** if there are no BH discoveries and the 4-plant power is below 0.5 or has
   n < 30.
10. Negatives published. If the wall cuts the run before the nulls finish, the cycle is excluded.
    If nulls finish but calibration or the m = 9 power does not, H1 is not testable (partial JSON
    still published). Same for H2 and the 4-plant power. No decipherment is claimed. A supported H1
    means "the leftover excess survives a calibrated, powered, pre-registered corpus test on the
    same data", never "independently replicated" and never "no other kind of arithmetic".

## Output
`analysis/k040_results.json`: design, consistency with K025, observed holdout G and p, per-khipu
rows (top and BH names), calibration, power at m ∈ {5, 9, 15}, H2 4-plant and 1-plant power,
verdicts, secs. Log: `analysis/k040_run.log`.

## No claims
No decipherment is claimed. Whole-group totals in UR119 are already counted by the Khipu Field
Guide; K025 pinned down their form. K040 only decides whether a smaller excess of the same form
remains in the rest of the basket.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04


## Results

Run 2026-11-08 03:07 PT (America/Vancouver), after prereg `6568b90`. Compute **28.7 s**
(all 367 holdout khipus reached; nulls, calibration and power all finished; `capped` false;
wall 520 s not hit). Smoke (`--smoke`, R = 200, N = 10) ran first in 1.4 s, no crash, not
used for decisions. Output: [`analysis/k040_results.json`](../analysis/k040_results.json),
log [`analysis/k040_run.log`](../analysis/k040_run.log).

### 1. Consistency (rule 1)
Database SHA-256 matches `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`.
K025 secondary n = 369; eligible 369; holdout 367; discovery pair KH0359 and KH0405 both
present; observed holdout G = 23. Rule 1 (excluded) does not apply.

### 2. H1 — corpus leftover (primary)
R = 10 000, seed 4040. Decision uses the pre-registered one-sided p against the summed
within-khipu permutation null.

| Quantity | Value |
|---|---|
| G_holdout | **23** |
| Null mean (sd) | 14.1067 (3.738) |
| p_corpus | **0.0162** |
| Calibration FPR (N = 200, seed 4041) | 0.05 |
| Power at m = 5 / 9 / 15 (N = 200, seed 4042) | 0.32 / **0.74** / 0.995 |

- meets_fpr: yes (0.05 ≤ 0.08)
- meets_power: yes (m = 9 rate 0.74 ≥ 0.5, n = 200)
- meets_alpha: yes (0.0162 ≤ 0.05)
- **Verdict: supported** (rules 2–4).

The leftover excess that K025 reported post-hoc (G = 23 vs 14.0958, p = 0.0176, R = 5 000)
survives the locked rule: same G, a slightly finer null (R = 10 000, seed 4040), a passing
calibration, and enough power to have seen an excess of leftover size. It is **not an
independent replication** — same extract, same definition, same 23 pendants.

Power at m = 5 is only 0.32, so a weaker leftover than the one in hand would not have been
readable. Power at m = 15 is 0.995.

### 3. H2 — individual BH scan (secondary)
BH q = 0.05 over 367 holdout khipus.

| Quantity | Value |
|---|---|
| BH discoveries | **0** |
| BH-gate (N = 200) | 0.005 |
| 4-plant power (UR119-strength) | **0.94** (n = 200; 117 redraws that could not place 4 disjoint plants) |
| 1-plant power (disclosed) | 0.125 (n = 200) |

- Gate passes (0.005 ≤ 0.08).
- **Verdict: not supported** (rules 6–8): no additional individually significant khipu, and
  that silence is readable against another UR119-strength (four planted whole-group sums)
  extra.

The closest name, reported only descriptively, is KH0424/UR186 (G = 2, p = 0.00030). The
BH threshold for a single discovery is 0.05/367 ≈ 0.000136, so it stays outside the scan.
A lone extra whole-group sum is not what H2 can see (1-plant power 0.125); that is H1's job.

### 4. Reading
- A smaller excess of whole-group totals remains after KH0359 and KH0405 are set aside.
  It is calibrated, powered at leftover size, and diffuse: many khipus contribute a single
  hit, none strongly enough to pass BH.
- There is no third UR119 in this extract, and that negative can be read.
- Same-data caveat stands. Independent replication would need khipus outside this OKR
  snapshot (data-limited).
- No decipherment. UR119's own totals remain the ones already counted by the Khipu Field
  Guide; K040 does not add a new named object.

### Next
Line 2's leftover is classified (H1 supported, H2 not supported). Proposed for K041: a
pre-registered form-audit of the leftover 23 hits (side, group length, whether any layout
repeats) against the within-khipu permutation, to see whether the diffuse excess shares a
shape or is a mixed bag — or line 8 (K002/K003 with multi-number cords masked; still low
priority).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

## Audit note (K056, 2026-11-08)
Under the K008 multi-number (R5) mask, H1 is **no longer established**: masked G = 18 vs 12.7355, p 0.0955
(FPR 0.035, m = 9 power 0.81). The mask removes 5 of the 23 hits, all non-singleton. K042's singleton-total excess
survives the same mask. See [K056](K056-multinumber-wholegroup.md).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
