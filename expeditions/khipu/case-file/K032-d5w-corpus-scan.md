# K032 · Corpus-wide D5w scan with BH-FDR, and when to keep unrestricted D5 (README line 1)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Why
K031 adopted D5w (D5's score, but only windows that stay inside one `CLUSTER_ID` group) on the largest third of
multi-group khipus. Two things were left open: (1) D5w has never been run on the real corpus under a multiple-comparison
correction, and (2) its mid-third FPR was 0.063 on n = 126 (noise or a real calibration problem?). This cycle runs the
scan, checks calibration with null corpora that are three times larger, measures power **at the BH level** (not just at
p ≤ 0.05), and fixes a rule, stratum by stratum, for when D5w should replace unrestricted D5.

## Data and strata (fixed before running)
OKR `khipu.db` @ `4039ca5`, level-1 pendants, `DUPLICATE_FLAG` khipus dropped, ≥ 10 nonzero pendants (457 eligible,
as K031). Groups = runs of consecutive pendants sharing `CLUSTER_ID`. Population (pop) = khipus with ≥ 2 groups of size
≥ 4 (378); thirds by pendant count as K031 (small, mid, large); **S0** = eligible khipus outside pop (79).

## Detectors and p-values
D5 and D5w exactly as in K031 (`tools/k031_within_group_windows.py`, logic copied unchanged). Within-khipu permutation
null, shared draws for both detectors. **Adaptive two-stage Monte Carlo** (pre-registered): K₀ = 1 000 draws; if either
p ≤ 0.01, extend to 10 000 total and recompute both p from all draws (floor 1/10 001 < BH rank-1 cut 0.05/378).

## Families and BH (q = 0.05)
- **F1 (primary): D5w on pop (378).** The within-group question.
- F2: D5 on all 457 (comparable to K003's 20 hits).
- F3: D5w on all 457 (descriptive).
Hits are compared with K003's 20 D5 hits (new / lost).

## Calibration (seed 3231·10 + r, r = 0..2)
Three **null corpora**: every eligible khipu replaced by a permuted copy, then passed through the identical adaptive
pipeline and BH families.
- **FPR gate per stratum and detector** (pooled over the 3 corpora, n = 3 × stratum size): pass iff the exact one-sided
  binomial P(X ≥ x | n, 0.05) ≥ 0.05 (FPR not significantly above nominal). **Mid-stratum watch:** if D5w fails in mid,
  D5w hits in mid are reported as *calibration-suspect* and mid cannot prefer D5w.
- **BH gate per family:** at most 1 of the 3 null corpora may produce any BH discovery. If a family fails, its real hits
  are *excluded* (tool not calibrated at the BH level).

## Power (seed 3232)
For every eligible khipu: one plant each of A_within, B_within (K031 within-group plants), A and B (K003 unrestricted
plants, n ≥ 20), same adaptive pipeline. **BH-level power** = the plant's p inserted in place of that khipu's real p in
the real family, BH recomputed, counted if significant. Also p ≤ 0.05 recovery. Wall-clock cap: stop at 560 s total and
report how many khipus were reached.
- **Silence rule:** a stratum's lack of F1 hits is *readable* (a real negative for within-group adjacent sums at the
  planted strength) only if BH-level D5w power on pooled within-plants ≥ 0.5; else *not testable*.

## Rule: D5w vs unrestricted D5 (per stratum S0, small, mid, large)
For the within-group question, **prefer D5w in stratum s iff** (i) the D5w FPR gate passes in s, (ii) pooled
A_within + B_within recovery at p ≤ 0.05 beats D5 by ≥ 0.03, (iii) exact two-sided McNemar on the paired plant outcomes
p < 0.05. Else **keep D5**. Fewer than 30 within-plants in s → *not testable*. For the unrestricted question (sums that
may cross groups) D5 stays by construction; the D5−D5w cost on A/B plants is reported.

## Seeds
scan 3230, null corpora 32310–32312, power 3232 (all distinct from K031's 3130/3131).

## No claims
A BH hit means "more within-group adjacent sums than chance in this khipu", which is a property of the record, not a
reading. No decipherment is claimed.

## Results

Run 2026-11-05 ~10:59 PT (America/Vancouver), `timeout 600 python3 tools/k032_d5w_corpus_scan.py ../khipu.db`
(324 s; all 457 khipus reached in every stage, no wall cap hit). Output: [`analysis/k032_results.json`](../analysis/k032_results.json).
**Amendment (code only, no design change):** the first two launches crashed *after* the scan and null stages, in the
binomial-tail helper (integer overflow at n = 1 371). The helper was rewritten in log space (`lgamma`) and checked
against the exact sum on small n; everything is seeded, so the rerun reproduced the same scan (15 / 18 / 18 hits) and
null corpora. No number was looked at to choose anything.

Strata: S0 79, small 126, mid 126, large 126 (thirds at 32.7 and 82.3 pendants, as K031).

### 1. Calibration at α = 0.05 (3 null corpora, pooled) — **all gates pass**
| Stratum | n | D5 FPR | D5w FPR | D5w binomial P(≥x) |
|---|---|---|---|---|
| S0 | 237 | 0.017 | 0.013 | 1.00 |
| small | 378 | 0.042 | 0.029 | 0.98 |
| **mid** | 378 | 0.042 | **0.040** | 0.85 |
| large | 378 | 0.061 | 0.037 | 0.90 |
| pop | 1 134 | 0.049 | 0.035 | 0.99 |

**Mid-stratum watch resolved:** with three times the checks, D5w's mid FPR is 0.040, so K031's 0.063 (n = 126) was
sampling noise. (D5's large-third 0.061 is inside the gate, binomial p 0.19.)

### 2. Calibration at the BH level — **F1 fails its gate**
Null corpora with any BH discovery: **F1 (D5w on pop) 2 of 3** (gate allows ≤ 1) → **F1 excluded**; F2 (D5 on all)
1 of 3 → passes, but only just; F3 (D5w on all) 2 of 3.

So, by the pre-registered rule, **the 15 real F1 hits are not reported as discoveries.** For the record (not
discoveries): KH0322/UR086, KH0395/UR155, KH0420/UR182, KH0428/UR190, KH0478/UR242, KH0491/UR255, KH0492/UR256,
KH0502/UR266, KH0504/UR267B, KH0506/UR269, KH0507/UR270, KH0511/UR273B, KH0513/UR274B, KH0514/UR275, KH0137/UR1123
(12 large, 2 small, 1 mid; 5 not in K003's 20). F2 (D5, calibrated by the gate): 18 hits, **all 18 inside K003's 20**
(a replication of K003, not new).

**Post-hoc diagnosis (labelled; not pre-registered).** [`tools/k032_posthoc_null_hits.py`](../tools/k032_posthoc_null_hits.py)
rebuilt the null corpora (same seeds): each false discovery is a single permuted *mid* khipu (KH0584/HP053; KH0620/JC013)
sitting at the Monte Carlo floor p = 1/10 001. [`tools/k032_posthoc_tail_audit.py`](../tools/k032_posthoc_tail_audit.py)
then measured the floor rate on 3 780 permuted copies (63 pop khipus × 60, K = 1 000, seed 32329):

| p-value construction | D5 floor rate | D5w floor rate | nominal |
|---|---|---|---|
| K003/K031 `colrank_p` (asymmetric) | 18 / 3 780 = 0.0048 | 17 / 3 780 = 0.0045 | 0.0010 |
| pooled (observed ranked inside observed + nulls) | 0 / 3 780 | 1 / 3 780 | 0.0010 |

Cause: the observed copy's per-column p counts only null draws (it can be 0/K), while each null draw's own p counts
itself (≥ 1/K). An observed sequence that tops **any one** of the 11 columns lands on the floor, so the extreme tail is
inflated about 4–5×. At α = 0.05 this is invisible (gates above pass), which is why K003 and K031 calibrated; under BH
with m ≈ 400 it is exactly the tail that matters. **This affects every BH list built on D5 (K003's 20, F2 here) as
well as D5w.** The pooled construction is the exact exchangeable fix and it is what the next cycle must use.

### 3. Power (seed 3232, one plant of each kind per khipu)
| Stratum | within plants n | D5 p≤.05 | D5w p≤.05 | D5 BH | D5w BH | unrestricted A+B: D5 / D5w (p≤.05) |
|---|---|---|---|---|---|---|
| S0 | 105 | 0.552 | 0.619 | 0.171 | 0.219 | 0.638 / 0.309 |
| small | 242 | 0.661 | 0.822 | 0.244 | 0.413 | 0.685 / 0.466 |
| mid | 246 | 0.646 | 0.805 | 0.211 | 0.398 | 0.659 / 0.393 |
| large | 250 | 0.532 | 0.648 | 0.200 | 0.300 | 0.512 / 0.329 |

(BH columns: pop family for small/mid/large, all-457 family for S0.) **Silence is not readable in any stratum**
(BH-level D5w power 0.22–0.41 < 0.5) → a khipu without a BH hit is *not testable* for within-group adjacent sums at
the planted strength.

### 4. Rule: D5w vs unrestricted D5 (pre-registered, per stratum)
| Stratum | D5w FPR gate | gain (within plants) | D5w-only / D5-only | McNemar p | Prefer |
|---|---|---|---|---|---|
| S0 | ✓ | +0.067 | 7 / 0 | 0.016 | **D5w** |
| small | ✓ | +0.161 | 43 / 4 | 2.8 × 10⁻⁹ | **D5w** |
| mid | ✓ | +0.159 | 44 / 5 | 7.6 × 10⁻⁹ | **D5w** |
| large | ✓ | +0.116 | 36 / 7 | 9.0 × 10⁻⁶ | **D5w** |

**Rule outcome:** for the *within-group* question D5w is preferred in every stratum (it extends K031's large-third
adoption to the whole eligible corpus). **Keep unrestricted D5** whenever the question allows windows that cross a
group boundary (e.g. K025-type whole-group totals): D5w loses 0.18–0.33 of recovery on unrestricted plants. The rule is
by *question*, not by size.

### Reading
- Calibration at 0.05 is fine everywhere (mid watch closed), and D5w is the better within-group tool in all strata.
- The corpus scan itself is **excluded**: the BH gate caught a real defect, the asymmetric min-p tail (≈ 4.5× at the
  floor), shared by D5 and D5w. No discovery is claimed from F1, and K003's / F2's BH lists are now flagged
  *tail-calibration pending* (not withdrawn, not confirmed).
- Next (K033): re-run the scan with the pooled exchangeable min-p, re-check the BH gate with ≥ 5 null corpora, and
  re-derive K003's list under the fix.

**Decision: method rule adopted (D5w for within-group questions in all strata; D5 for unrestricted); corpus scan
excluded (BH-level calibration failed); silence not testable (power 0.22–0.41).**

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
