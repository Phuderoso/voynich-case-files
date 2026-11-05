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
(to be filled after the run)

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
