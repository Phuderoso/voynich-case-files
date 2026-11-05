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
