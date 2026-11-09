# PE008 · How are grain (capacity) totals built? Partial-total conventions vs upper capacity factors

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration** (this file and `tools/pe008_grain_totals.py` are published before any convention match,
gate or null number on these tablets is computed). Open line 9 of the expedition README.

## Why this line
PE006 showed (out of sample, gates passing) that capacity (grain, CAP) single-total tablets balance less often than the
rest (7/32 vs 18/32). Its post hoc found that 20 of the 25 grain mismatches have **total < sum of the obverse**, and
that dropping the sub-unit signs fixes none. A smaller total is what a scribe would write if the total covered only
part of the list (a prefix, a contiguous sub-group, the lines of one kind), **or** what our arithmetic would produce if
the upper capacity factors (N14 = 6 N01, N45 = 10 N14, N34 = 3 N45, N48 = 10 N34) were wrong for these tablets.
PE008 fixes the convention family and its rival **before** looking, and tests both.

## Disclosure: what has already been looked at
- **PE006 post hoc** inspected exactly the primary targets (the 25 fresh grain mismatches) for the **direction** of the
  mismatch (20/25 total < sum) and for sub-unit dropping (0/25). The convention family below was chosen *after* that
  look; this is hypothesis generation from those tablets, so the primary set is **not** pristine.
- **PE001** inspected the direction on its 38 intact tablets (16/19 non-balancing with total < sum), which overlap the
  PE005 set; **PE005 post hoc** checked sub-unit dropping on its 15 grain mismatches (≤ 3/15).
- **No prefix, contiguous-run, line-kind or upper-factor match has been computed on any tablet** before this file.
- Label-free inventory computed before this file (`analysis/pe008_inventory.json`): set sizes, entries per tablet,
  eligibility counts per convention; no match, no total value inspected.
- Because neither set is untouched by post hoc, the **replication set** below is the best confirmatory subset
  available: it was never inspected for these conventions nor (in PE006) for direction. Any convention that passes
  only on the primary set is reported as a **LEAD**, not SUPPORTED. If replication is not testable, **this cycle is
  exploratory** for that convention.

## Data
Pinned CDLI dump `d66b12b` (`pe.atf` sha256 `5c4860ab…159a6`); tablet sets and labels exactly as published:
- **P (primary)**: PE006 fresh set, CAP and not balancing: **25 tablets** (entries per tablet 2–13; 20 with ≥ 3 entries;
  17 with both sub-unit and non-sub-unit lines).
- **R (replication)**: PE004/PE005 intact calibration set, CAP and not balancing: **15 tablets** (12 with ≥ 3 entries;
  only 6 with mixed line kinds, so K3/K4 replication is expected NOT TESTABLE by the size gate).
- Descriptive comparison: non-CAP mismatches (fresh 14, PE005 6), same statistics, no decision weight.
Entries are taken in ATF line order (the editor's reading order of the obverse). A tablet's admitted systems are those
of S/D/B/C in which every entry and the total are valid (as for the balance label).

## Convention family (fixed now)
A tablet **matches** a convention if it holds in **any** admitted system.
| Id | Convention | Eligible | Null |
|---|---|---|---|
| K1 PREFIX | total = sum of the first k entries, 2 ≤ k ≤ n−1 | n ≥ 3 | line-order shuffle |
| K2 RUN | total = sum of a contiguous run, length 2 … n−1 | n ≥ 3 | line-order shuffle |
| K3 NONSUB | total = sum of the entries **without** sub-unit signs ("non-grain lines") | 1 ≤ #such ≤ n−1 | total permutation |
| K4 SUBONLY | total = sum of the entries **with** sub-unit signs | same | total permutation |
| K5 UPPER (rival) | total = sum of **all** entries under a C table with **one** upper factor changed: N14:N01 ∈ {5, 10}, N45:N14 ∈ {5, 6}, N34:N45 ∈ {2, 6}, N48:N34 ∈ {6} (7 variants) | C admitted | total permutation |

**Statistic**: number of eligible targets that match. **Nulls** (structure-preserving): K1/K2 — entries permuted within
each tablet (values, multiset and totals kept; only order destroyed), so a pass means *order* matters, not just "some
subset sums to the total"; K3–K5 are order-invariant, so totals are permuted among the targets of the set (entries
and the set's totals kept; the tablet-to-total link destroyed). R = 1 999, seed 801, p = (1 + #null ≥ obs)/(1 + R).
For K1/K2 the total-permutation p is also reported (descriptive).

## Gates (per set × convention; computed after this file is published, before the real test)
- **FPR**: 100 destroyed-signal datasets (K1/K2: one line-order shuffle; K3–K5: one total permutation), each tested
  with R = 299; rate of p ≤ 0.05 must be **≤ 0.06**. Seed 802.
- **Power** (planted convention): 100 datasets in which each eligible target independently (prob **0.5**) gets its
  total replaced by the canonical notation of that convention's own sum (K1 random k, K2 random run, K3/K4 the line-kind
  sum, K5 the full sum under a random variant) in a random admitted system; tested with R = 299; rate of
  **p ≤ 0.01** (the Holm worst case 0.05/5) must be **≥ 0.80**. Seed 803. Plant prob 0.8 reported (descriptive).
- **Size**: ≥ 8 eligible targets.

## Decision rule
- Primary: set P, **Holm over K1–K5** at 0.05. Replication: set R, unadjusted 0.05, only as confirmation of
  conventions that pass on P.
- **NOT TESTABLE** — a P gate fails. **NOT DETECTED** — P gates pass, Holm p > 0.05. **EXCLUDED** — NOT DETECTED and the
  one-sided 95 % Clopper–Pearson upper bound of matched/eligible is < 0.25 (the convention explains at most a quarter
  of grain mismatches). **SUPPORTED** — P passes, R gates pass and R p ≤ 0.05. **LEAD** — P passes, R not testable.
  **NOT CONFIRMED** — P passes, R gates pass, R p > 0.05.
- Descriptive: overlap on P between tablets explained by any partial-total convention (K1–K4) and by the upper-factor
  rival (K5); how many mismatches stay unexplained.

## Audit of PE007
Re-run `pe007_noncap.py test` from the published tool in a scratch copy with the published gates and compare every
field (run time excluded); independently re-compute set B's entry precision from a direct PE004 leave-one-out
(published 0.60).

## Honest limits
ATF line order is the editor's reading order; multi-column obverses could scramble true order, diluting K1/K2 (bias
toward NOT DETECTED). Proper sub-sums at one unit grain are frequent among short lists of repeated `1(N01)`, which is
why the nulls keep each tablet's own values. Partial-total matches are arithmetic, not readings: no decipherment is
claimed.

Tool: [`tools/pe008_grain_totals.py`](../tools/pe008_grain_totals.py) (`inventory`, `gates`, `test`, `audit`).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (computed after the pre-registration was published as `f68f50c`)

Order of events (America/Vancouver, 2026-11-08): pre-registration on `main` (`f68f50c`) at ~20:22; gates 20:22–20:25
(179 s); PE007 audit in parallel (44 s); the real test at 20:28 (9.5 s); post hoc right after (1.5 s). Outputs:
`analysis/pe008_gates.json`, `analysis/pe008_results.json`, `analysis/pe008_pe007_audit.json`,
`analysis/pe008_posthoc.json`, run log `analysis/pe008_run.log` (gates, test, audit, post hoc).

**Gates.**

| Set × convention | eligible | FPR (≤ 0.06) | power, plant 0.5, p ≤ 0.01 (≥ 0.80) | plant 0.8 (descr.) | testable |
|---|---|---|---|---|---|
| P K1 PREFIX | 20 | 0.01 | 1.00 | 1.00 | ✓ |
| P K2 RUN | 20 | 0.00 | **0.74** | 1.00 | ✗ (power) |
| P K3 NONSUB | 17 | 0.00 | 1.00 | 1.00 | ✓ |
| P K4 SUBONLY | 17 | 0.01 | 1.00 | 1.00 | ✓ |
| P K5 UPPER | 25 | 0.00 | 1.00 | 1.00 | ✓ |
| R K1 / K2 | 12 | 0.03 / 0.00 | 0.75 / 0.26 | 1.00 / 0.72 | ✗ (power) |
| R K3 / K4 | 6 | 0.00 / 0.00 | 0.84 / 0.84 | 1.00 | ✗ (size < 8, as expected) |
| R K5 | 15 | 0.00 | 1.00 | 1.00 | ✓ |

**Primary set P (25 fresh grain mismatches), Holm over 5.**

| Convention | matched / eligible | null mean (max) | p | Holm p | CP95 upper | Verdict |
|---|---|---|---|---|---|---|
| K1 PREFIX | 1 / 20 | 0.30 (2) | 0.293 | 1.00 | 0.216 | **EXCLUDED** |
| K2 RUN | 1 / 20 | 0.67 (2) | 0.586 | 1.00 | 0.216 | **NOT TESTABLE** (power 0.74) |
| K3 NONSUB | 0 / 17 | 0.00 (0) | 1.000 | 1.00 | 0.162 | **EXCLUDED** |
| K4 SUBONLY | 1 / 17 | 0.10 (2) | 0.096 | 0.48 | 0.250 | **NOT DETECTED** (bound 0.2501, just above 0.25) |
| K5 UPPER (rival) | 0 / 25 | 0.08 (2) | 1.000 | 1.00 | 0.113 | **EXCLUDED** |

Replication set R (15 PE005 grain mismatches; descriptive since nothing passed on P): K1 1/12 (p 0.63), K2 3/12
(p 0.44; total-permutation p 0.024, descriptive), K3 0/6, K4 0/6, K5 0/15. K1/K2 total-permutation p on P (descriptive):
0.079 / 0.52. Overlap on P: one tablet (P009219) matches any partial-total convention, none the upper-factor rival;
**24 of 25 grain mismatches stay unexplained.**

**Verdict.** No convention is SUPPORTED. Prefix totals, the "non-grain lines" total and the upper-factor rival are
**EXCLUDED** (each explains at most 11–22 % of the fresh grain mismatches, 95 % bound); sub-unit-line totals NOT
DETECTED; contiguous runs NOT TESTABLE (power 0.74). Because PE006's post hoc had looked at these tablets, this cycle
was partly exploratory; a negative is not weakened by that look.

## Post-hoc diagnostics (after test; no decision weight; `tools/pe008_posthoc.py`)
- **Q1 omit-one** (total = sum minus exactly one line): P 1/25 (P009219), R 1/15 (P368541).
- **Q2 any proper subset**: P 3/25 vs total-permutation mean 1.48 (rate ≥ obs 0.15); R 4/15 vs 2.12 (0.058). Arbitrary
  subsets explain little more than chance.
- **Q3 size**: in system C the fresh grain totals are a median **0.24** of the obverse sum (range 0.004–1.75; 5 above 1).
  Most reverse numbers are far too small to be any partial sum of these lines: the reverse "total" on grain tablets
  is mostly **not a sum of the obverse at all** (a different quantity, another system, or a summary of something else).
  This reframes line 9 toward ratio accounts (open line 4) and system disambiguation (line 3).

## PE007 audit
`pe007_noncap.py test` re-run in a scratch copy with the published gates: **identical** to `analysis/pe007_results.json`
in every field except run time. Independent re-check: set B entry precision recomputed by a direct PE004 leave-one-out
= **28 / 47 = 0.596** (published 0.60) ✓ (`analysis/pe008_pe007_audit.json`).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
