# K027 · Is the KH0240/KH0496 pattern a shared small-number template? (README line 3)

## Why
K012 raised one lead: KH0240 (UR004, Leymebamba) and KH0496 (UR260, Incahuasi) share the run-collapsed pendant
pattern `P = 1, 2, 1, 2, 3, 1, 2, 1, 3`. The run lengths differ, so they don't record the same numbers. K013's
run-length-aware score didn't find the pair (p 0.18), and the literature check found no link between the two sites.
The explanation still to rule out is a **typological** one: many khipus may use a common counting layout over 1–3, so
this match would be one member of a family, not a link between two sites.

## Pre-registration (written before the analysis code was run)
Data: OKR `khipu.db` as in K012. Level-1 pendants in cord order, non-duplicate khipus with ≥ 10 nonzero pendants;
multi-number (R5) cords set to 0, values as K001. Each sequence is collapsed into runs (value, length). A *k-block* is
k consecutive collapsed values, all nonzero.
Null: K012's run-permutation (shuffle the order of runs within each khipu, then collapse again), 2 000 corpus replicates.

- **T1 · Does P recur?** Statistic N₁ = number of khipus *other than* KH0240 and KH0496 whose collapsed sequence
  contains P. One-sided upper p against the null.
- **T2 · Is there a family of small-number blocks?** Statistic N₂ = number of khipu pairs, excluding the lead pair,
  sharing at least one 9-block whose values are all in {1, 2, 3}. One-sided upper p against the null.
- **Decision:** Bonferroni ×2, α = 0.025 each.
  - The template explanation is **supported** if T1 or T2 is significant.
  - It is **not supported** if neither test is significant and the test has power ≥ 0.8 under its planted control.
  - Otherwise it is **not testable**.
- **Planted controls** (100 trials each):
  - T1: write P (with run length 1 per value) into 3 random other eligible khipus at a random position.
  - T2: write a random 9-block over {1, 2, 3} (no repeated neighbours) into 5 random pairs of khipus.
  - Power is the share of trials significant against the real null's 97.5th percentile.
- **Reading if not supported:** the lead stays unexplained by a template and stays only a lead (one hit in 93 528
  pairs, not confirmed by K013). That would not show a link between the sites.

## Results
(Written after the run, below this line.)

Run: `python3 tools/k027_small_number_template.py ../khipu.db` (34.5 s, R = 2 000, 100 planted trials each). Output:
`analysis/k027_results.json`, log `k027_run1.log`. 433 eligible khipus.

| Test | Observed | Null mean | p | Power | Verdict |
|---|---|---|---|---|---|
| T1 · P in other khipus | **0** | 0.001 | 1.0 | 1.00 | not significant |
| T2 · other pairs sharing a {1,2,3} 9-block | **0** | 0.001 | 1.0 | 1.00 | not significant |

**Verdict: the template explanation is not supported** (both tests have power 1.00). Only KH0240 and KH0496 contain P,
and no other pair of the 433 khipus shares any 9-block over 1–3. If a common small-number layout existed, it would
show up elsewhere, and it doesn't. The power is trivially high because chance almost never makes such blocks (the
97.5th percentile is 0), so a single recurrence would have counted.

### Post-hoc (disclosed, not pre-registered)
`tools/k027_posthoc_anypair.py` (31 s, seed 27028; `analysis/k027_posthoc_anypair.json`): the same null with the lead
pair *included*. In 0 of 2 000 null corpora did **any** pair share a 9-block over {1,2,3}, so p = 0.0005. That would
be striking, but it doesn't confirm the lead:
1. The block length (9) and alphabet (1–3) were taken from the lead itself, so this is a selected statistic.
2. The pre-registered K013 test that keeps run lengths gave p 0.18 for this pair.
3. The run-permutation null scatters any short-range order inside a khipu (e.g. alternating 1, 2). A null that keeps
   each khipu's value-to-value transitions (an order-1 Markov null on collapsed values) is needed before reading
   p = 0.0005 as evidence.

### Line 3 status
**Advanced:** the "shared template" explanation for KH0240/KH0496 is excluded. The pair stays an unexplained lead,
not a confirmed link. Next (K028): a pre-registered order-1 Markov null for the collapsed pattern, with the lead
pair named in advance.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
