# K026 · Where do the inconsistent E and L knots come from? (README line 4)

## Why
K007 found that `E` (figure-eight) and `L` (long) knots in `khipu.db` break the decimal reading rules a little more
often than the 1% bar: 89 `E` knots not valued 1 (R1) and 490 `L` knots whose value isn't their turn count in 2–9
(R2). Before writing a data-quality note to the Open Khipu Repository (OKR), two questions need exact answers:
**are these errors clustered in particular khipus or recording series** (a transcription batch) or spread evenly,
and **which field looks wrong** in each case (the knot type, the value, or the turn count)?

## Pre-registration (written before the analysis code was run)
Data: OKR `khipu.db` as in K001–K025, non-duplicate khipus. Audited knots are those K007 audited: all `E` knots, and
`L` knots with `NUM_TURNS` recorded. A **violation** is a K007 R1 or R2 violation.

**H1 (concentration).** Violations are concentrated by khipu beyond chance.
- Statistic: the G statistic (likelihood ratio) of violations per khipu against the expected count, which is the
  khipu's share of audited knots computed separately for `E` and `L`.
- Null: permute violation labels among audited knots, within knot type, across the corpus. 10 000 replicates.
- Second test with the same statistic and null, grouped by recording series (the letter prefix of
  `INVESTIGATOR_NUM`, e.g. UR, AS, JC).
- Decision: Bonferroni ×2, α = 0.025 each. Supported if p < 0.025.
- Power: plant 50 extra violations (relabel valid knots) into 3 random khipus on null-labelled data; 100 trials.
  Below 0.8 power, a non-significant result is *not testable*, not a negative.

**H2 (which field is wrong).** Exact classification, no test. Each violation goes into exactly one category:
- `E` knots:
  - **E-type**: value 10^k with k ≥ 1 and the knot's cluster is not the last cluster on its cord (the position
    agrees with the value, so the type code is the suspect).
  - **E-value**: value 10^k with k ≥ 1 in the last (units) cluster (the position agrees with `E`, so the value is the
    suspect).
  - **E-zero**: value 0 or empty.
  - **E-other**: anything else.
- `L` knots:
  - **L-shift**: turns in 2–9 and value = turns × 10^k with k ≥ 1.
  - **L-off1**: turns in 2–9 and |value − turns| = 1.
  - **L-zero**: turns in 2–9 and value 0 or empty.
  - **L-other**: turns in 2–9, anything else.
  - **L-turn1**: turns = 1 (the turn count says `E`).
  - **L-turn0**: turns = 0.
  - **L-turn10+**: turns ≥ 10.
- Decision: a category with ≥ 20 knots is reported as **noteworthy for an OKR note**, with example knot ids.
  Smaller categories are listed but not raised.

## Results
(Written after the run, below this line.)
