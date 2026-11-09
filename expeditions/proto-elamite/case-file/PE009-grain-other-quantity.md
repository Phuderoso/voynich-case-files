# PE009 · Is the grain reverse a different quantity? Mixed-system readings and exact metrological ratios

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration** (this file and `tools/pe009_other_quantity.py` are published before any H1–H4 match,
gate or null number on these tablets is computed). Open lines 9 and 4 of the expedition README.

## Why this line
PE008 EXCLUDED partial sums and other upper capacity factors as the way grain (CAP) totals are built: 24 of 25 fresh
grain mismatches stay unexplained, and its post hoc found the reverse number is a median 0.24 of the obverse sum in C.
A number that small may not be a total at all. PE009 asks whether it is a **different quantity**: (a) a count written in
a discrete-count system (S/B/D: people, rations, lines) while the obverse is grain in C, or (b) the grain sum converted
by an **exact metrological ratio** (written one or more units up or down).

## Disclosure: what has already been looked at (and how the lists are guarded)
- **PE008 post hoc published the 25 total/sum ratios in C of the fresh set** (`analysis/pe008_posthoc.json`: median
  0.242, range 0.004–1.75, five above 1, one exactly 0.5). I have read that list. Therefore:
  - the fresh set is **not** the decision set; it is demoted to replication, and for the ratio hypothesis H1 its
    replication is labelled **exposed** in any verdict;
  - the **H1 ratio list is not chosen from data**: it is derived mechanically from Englund's C table (all value ratios
    v_a / v_b between two different C signs, 56 fractions: 1/2, 1/3, 1/5, 1/6, 1/10, 1/12, … and their inverses);
    1/4 is in it only because N30C = 4 N39C in the table. The generic small-fraction list (1/2 … 1/10) is
    **exploratory only**, run after the test, no decision weight;
  - the H3 ration list U is fixed from the table (single C signs below N01, plus N14 and N45) and from the one
    documented ration in Englund 2004 (2½ N39B = 60 N39C per head); nothing in it comes from these tablets.
- PE001 looked at the direction (total < sum) on intact tablets that overlap set A; PE008 computed partial sums,
  omit-one and subsets on A. **No ratio, cross-system reading, per-head division or line count has been computed on A.**
- Label-free inventory computed before this file (`analysis/pe009_inventory.json`): set sizes, entries per tablet and
  eligibility counts (eligibility depends on the entries only); no total inspected.

## Data and sets
Pinned CDLI dump `d66b12b` (`pe.atf` sha256 `5c4860ab…159a6`); labels exactly as published (PE005/PE006 balance).
- **A (primary, decision)**: PE004/PE005 intact set, CAP and not balancing: **15 tablets**.
- **B (replication, reserved before looking)**: PE006 fresh set, CAP and not balancing: **25 tablets** (exposed for H1 only).
C values in N39C units (N01 = 120). Eligible counts (inventory): A — H1 15, H2 **5**, H3 15, H4 15; B — 25, 8, 25, 25.
H2 on A is therefore expected **NOT TESTABLE** by the size gate (< 8); declared now.

## Hypothesis family (fixed now)
| Id | The reverse number is… | Match rule (exact, integers/rationals) | Eligible |
|---|---|---|---|
| H1 RATIO_METRO | the grain sum converted by a C unit ratio | value_C(total) / sum_C = v_a / v_b, a ≠ b C signs | entries valid in C |
| H2 MIX_EQ | the same grain quantity in N01, written in a count system | 120 · value_X(total) = sum_C, X ∈ {S, B, D} | sum_C a whole number of N01 |
| H3 PER_HEAD | a head count k (read in S) of exact standard rations | sum_C = k · u, k ≥ 1, u ∈ {1, 2, 4, 12, 24, 60, 720, 7200} | some u divides sum_C |
| H4 COUNT_LINES | the number of obverse entries (read in S) | value_S(total) = n | n ≥ 2 |

**Statistic**: number of eligible targets that match. **Null** (structure-preserving): totals permuted among the targets
of the set (each tablet keeps its entries; the set keeps its totals; only the link is destroyed). R = 1 999, seed 901,
p = (1 + #null ≥ obs)/(1 + R).

## Gates (per set × hypothesis; after this file is published, before the real test)
- **FPR**: 100 total-permuted datasets, R = 299 each; rate of p ≤ 0.05 must be **≤ 0.06**. Seed 902.
- **Power** (planted quantity): 100 datasets, each eligible target independently (prob **0.5**) gets its total replaced
  by the canonical notation of the hypothesis' own quantity (H1 random C sign ratio giving a whole positive value;
  H2 random X; H3 random dividing u; H4 n); R = 299; rate of **p ≤ 0.0125** (Holm worst case 0.05/4) must be
  **≥ 0.80**. Seed 903. Plant 0.8 descriptive.
- **Size**: ≥ 8 eligible targets.

## Decision rule
- Primary: set A, **Holm over H1–H4** at 0.05. Replication: set B, unadjusted 0.05, only for hypotheses passing on A.
- **NOT TESTABLE** — an A gate fails. **NOT DETECTED** — A gates pass, Holm p > 0.05. **EXCLUDED** — NOT DETECTED and
  one-sided 95 % Clopper–Pearson upper bound of matched/eligible on A < 0.25. **SUPPORTED** — A passes, B gates pass,
  B p ≤ 0.05 (H1: "replication exposed"). **LEAD** — A passes, B not testable. **NOT CONFIRMED** — A passes, B gates
  pass, B p > 0.05.
- Descriptive: B results for all hypotheses; tablets explained by any H; exploratory small fractions (after the test).

## Audit of PE008
Re-run `pe008_grain_totals.py test` in a scratch copy with the published gates and compare every field except time;
independently re-compute the PE008 post-hoc median total/sum ratio in C on the fresh set (published 0.242) with a
literal C table and plain integer sums (no PE001 value code).

## Honest limits
A has only 15 tablets: with exact matching the planted signal is strong, but a real convention affecting a minority of
tablets would be missed. The H1 list has 56 fractions, so chance matches are not rare; the permutation null keeps the
set's own totals and handles that. Readings of a total in S are hypotheses about the scribe's intent, not readings of the
signs: no decipherment is claimed.

Tool: [`tools/pe009_other_quantity.py`](../tools/pe009_other_quantity.py) (`inventory`, `gates`, `test`, `audit`).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
