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

Run 2026-11-05 ~11:45 PT (America/Vancouver), `timeout 600 python3 tools/k033_pooled_minp_rescan.py ../khipu.db`
(312.2 s; all 457 khipus reached in every stage, no wall cap hit). Output:
[`analysis/k033_results.json`](../analysis/k033_results.json). Prereg + tool committed first as `64bfcf83`.

Strata: S0 79, small 126, mid 126, large 126 (thirds at 32.7 and 82.3 pendants, as K031/K032).

### 1. Calibration at α = 0.05 (5 null corpora, pooled) — **all gates pass**
| Stratum | n | D5 FPR | D5w FPR | D5w binomial P(≥x) |
|---|---|---|---|---|
| S0 | 395 | 0.028 | 0.025 | 1.00 |
| small | 630 | 0.035 | 0.037 | 0.96 |
| mid | 630 | 0.049 | 0.052 | 0.42 |
| large | 630 | 0.059 | 0.041 | 0.87 |
| pop | 1 890 | 0.048 | 0.043 | 0.92 |

(All binom_p_above ≥ 0.05; D5 large 0.059 is inside the gate, binomial p 0.18.)

### 2. Calibration at the BH level — **all three families pass**
Null corpora with any BH discovery: **F1 0 of 5, F2 0 of 5, F3 0 of 5** (gate allows ≤ 1).
**The asymmetric defect is fixed.** Under the pooled construction the BH tool is calibrated.

### 3. Real scan (pooled; discoveries now reportable)
- **F1 (D5w on pop, primary): 11 hits** — KH0322/UR086, KH0395/UR155, KH0420/UR182, KH0428/UR190,
  KH0491/UR255, KH0492/UR256, KH0504/UR267B, KH0506/UR269, KH0507/UR270, KH0513/UR274B, KH0514/UR275
  (9 large, 2 small, 0 mid, 0 S0). Two are new vs K003: KH0322/UR086, KH0420/UR182.
- **F2 (D5 on all): 15 hits**, all inside K003's 20 (no F2-only discoveries).
- F3 (D5w on all): 13 (descriptive).
- Descriptive asym BH on the same draws: F1 13, F2 20 (reproduces K003's count), confirming the old
  construction still inflates the list when left unfixed.

### 4. K003 re-derivation under the exchangeable fix
| Status | Khipus |
|---|---|
| **Retained** (F2 ∩ K003) | 15: KH0027/AS026A, KH0168/UR1152, KH0218/AS200, KH0359/UR119, KH0385/UR145, KH0405/UR166, KH0424/UR186, KH0428/UR190, KH0491/UR255, KH0492/UR256, KH0503/UR267A, KH0504/UR267B, KH0506/UR269, KH0507/UR270, KH0514/UR275 |
| **Lost under pooled** (in K003, not in F2) | 5: KH0143/AS128, KH0395/UR155, KH0447/UR209, KH0478/UR242, KH0513/UR274B |

The five lost are exactly the ones whose asymmetric p sat near a Monte Carlo floor while the pooled p rose
(e.g. KH0447 and KH0478: asym ≈ 0.001 → pooled ≈ 0.011). They remain in the historical K003 record but are
**withdrawn from the calibrated list**. Note KH0395/UR155 and KH0513/UR274B are lost from F2 (unrestricted D5)
but retained as F1 hits under D5w (within-group).

### 5. Power and silence
| Stratum | within n | D5w p≤.05 | D5w BH | readable? |
|---|---|---|---|---|
| S0 | 105 | 0.55 | 0.16 | no |
| small | 242 | 0.86 | 0.36 | no |
| mid | 246 | 0.77 | 0.32 | no |
| large | 250 | 0.64 | 0.26 | no |

**Silence is not readable in any stratum** (BH-level D5w power 0.16–0.36 < 0.5).

### 6. Rule D5w vs D5 (secondary, same criteria as K032, this cycle's plants)
| Stratum | FPR gate | gain | D5w-only / D5-only | McNemar p | Prefer |
|---|---|---|---|---|---|
| S0 | ✓ | +0.029 | 6 / 3 | 0.51 | **D5** (gain < 0.03) |
| small | ✓ | +0.190 | 48 / 2 | 2.3 × 10⁻¹² | **D5w** |
| mid | ✓ | +0.179 | 50 / 6 | 1.0 × 10⁻⁹ | **D5w** |
| large | ✓ | +0.136 | 43 / 9 | 2.0 × 10⁻⁶ | **D5w** |

Under pooled p and seed 3332, S0 no longer meets the ≥ 0.03 gain bar (K032 had +0.067 under seed 3232).
**Updated rule:** D5w for within-group questions in small/mid/large; **D5 in S0** (and whenever windows may
cross groups). The question-based half of K032's rule is unchanged.

### Reading
- The pooled exchangeable min-p **calibrates the BH scan** (0 of 5 null corpora with a false discovery).
- F1 yields 11 within-group discoveries; F2 re-derives a tighter K003 list of 15 (5 withdrawn as floor artefacts).
- Silence still not testable at the planted strength.
- Next levers on line 1: raise BH-level power (stronger plants or stratified BH), or a held-out confirmation of
  the two F1-only hits (KH0322, KH0420).

**Decision: scan adopted (BH gate passed); K003 list re-derived (15 retained, 5 withdrawn); F1 = 11 discoveries;
silence not testable; rule refined (D5w in small/mid/large, D5 in S0 / unrestricted).**

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

