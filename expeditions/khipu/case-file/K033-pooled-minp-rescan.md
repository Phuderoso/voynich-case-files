# K033 · Pooled exchangeable min-p rescan: BH-FDR recalibration and K003 list re-derivation (README line 1)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Why
K032's corpus scan was **excluded** because its BH gate failed (false discoveries in 2 of 3 null corpora). A labelled
post-hoc audit pointed at the asymmetric `colrank_p` used by K003/K031/K032: the observed copy can land on the Monte
Carlo floor ~4.5× too often. Ranking the observed sequence **inside** the pool of (observed + null draws) restores
exchangeability (floor rate ≈ 1/(K+1) on 3 780 null copies). This cycle re-runs the scan under that pooled construction,
with a stricter BH gate (≥ 5 null corpora), and re-derives K003's 20-khipu BH list under the fix. No design change to
the D5/D5w scores themselves.

## Data and strata (fixed before running; identical to K032)
OKR `khipu.db` @ `4039ca5`, level-1 pendants, `DUPLICATE_FLAG` khipus dropped, ≥ 10 nonzero pendants (457 eligible).
Groups = runs of consecutive pendants sharing `CLUSTER_ID`. Population (pop) = khipus with ≥ 2 groups of size ≥ 4
(378); thirds by pendant count as K031/K032 (small, mid, large); **S0** = eligible outside pop (79).

## Detectors
D5 and D5w exactly as in K031/K032 (`tools/k032_d5w_corpus_scan.py` scoring, copied unchanged). Within-khipu
permutation null, shared draws for both detectors. Adaptive two-stage Monte Carlo: K₀ = 1 000; if either pooled p ≤
0.01, extend to 10 000 total and recompute both p from all draws.

## Primary change: pooled exchangeable min-p
Let No be the observed 1×C score row and Nn the K×C null-score matrix. Form A = [No; Nn]. Drop dead columns
(A.max(0) == 0). Let pa_i = min_j colrank_p(A, A)_{i,j}. The pooled p is

    p_pooled = (# of i with pa_i ≤ pa_0) / (K + 1).

This is the exact exchangeable construction from the K032 post-hoc. **All decisions use p_pooled.** For the real scan
only, the old asymmetric min-p is also recorded (descriptive; not used for BH, gates, rule, or silence).

## Families and BH (q = 0.05)
- **F1 (primary): D5w on pop (378).**
- F2: D5 on all 457 (K003-comparable).
- F3: D5w on all 457 (descriptive).

## Calibration (seed 3331·10 + r, r = 0..4) — **R = 5 null corpora**
Five null corpora: every eligible khipu replaced by a permuted copy, identical adaptive pipeline and BH families.
- **FPR gate** per stratum and detector (pooled over the 5 corpora): pass iff exact one-sided binomial
  P(X ≥ x | n, 0.05) ≥ 0.05.
- **BH gate per family:** at most **1 of the 5** null corpora may produce any BH discovery. If a family fails, its
  real hits are *excluded*. (Stricter rate than K032's ≤ 1 of 3.)

## Power (seed 3332)
Same plants as K032 (A_within, B_within, A, B). BH-level power by inserting the plant's pooled p into the real family.
Wall-clock cap: stop at 560 s total and report how many khipus were reached.
- **Silence rule:** a stratum's lack of F1 hits is *readable* only if BH-level D5w power on pooled within-plants ≥ 0.5;
  else *not testable*.

## Rule: D5w vs D5 (secondary; same criteria as K032)
Prefer D5w in stratum s for the within-group question iff (i) D5w FPR gate passes in s, (ii) within-plant gain at
p ≤ 0.05 ≥ 0.03, (iii) McNemar p < 0.05. Else keep D5. Reported to confirm K032's rule under the new p-values; not the
primary question.

## K003 re-derivation (pre-registered)
F2 hits under pooled p are compared with K003's 20 BH hits. Report: overlap, F2-only, K003-lost. A K003 hit that is
not in F2 under pooled is *not confirmed under the exchangeable fix*; one that is, is *retained*. This is a
re-derivation of the list, not a new discovery claim beyond what the BH gate allows.

## Seeds
scan 3330, null corpora 33310–33314, power 3332 (all distinct from K031's 3130/3131 and K032's 3230/3231/3232).

## Decision rules (written before any run)
1. If F1's BH gate fails → F1 **excluded** (scan still not calibrated); do not claim F1 discoveries.
2. If F1's BH gate passes → report F1 hits as BH discoveries at q = 0.05; compare with K003.
3. F2: same gate; if it passes, the F2 ∩ K003 overlap is the **re-derived K003 list** under the fix; F2-only hits are
   new candidates; K003-lost are withdrawn from the calibrated list (they remain in the historical K003 record).
4. Silence: as above.
5. Rule (D5w vs D5): secondary confirmation of K032.

## No claims
A BH hit means "more adjacent sums than chance in this khipu under the stated detector", a property of the record, not
a reading. No decipherment is claimed.

## Results
*(filled after the run)*

