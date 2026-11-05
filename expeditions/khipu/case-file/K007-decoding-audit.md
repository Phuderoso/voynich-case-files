# K007 · Decoding audit: do the knot values in `khipu.db` follow the decimal rules?

## Why (README line 4)
Every cycle K001–K006 uses `knot.knot_value_type`, summed per cord. If that column breaks the Locke/Ascher decimal
convention anywhere, our sums and matches inherit the error. This cycle is an exact audit, not a statistical test:
each rule is checked on every knot, and every violation is counted and listed.

## Pre-registration (rules fixed before the audit code was run)
Conventions (Locke 1923; Ascher & Ascher 1978): `S` single knots record tens and higher places, one knot per unit
of the digit; `L` long knots record the units digit 2–9 by their number of turns; `E` figure-eight knots record a
units digit of 1. Knots are grouped into clusters (`knot.CLUSTER_ID`), one cluster per decimal place.

| Rule | Check | Scope |
|---|---|---|
| R1 | `E` knot has value 1 | all `E` knots |
| R2 | `L` knot has value equal to `NUM_TURNS`, and 2 ≤ turns ≤ 9 | all `L` knots |
| R3 | `S` knot has value 10^k for some k ≥ 0 | all `S` knots |
| R4 | all knots in one cluster have the same place (10^k) | clusters with ≥ 2 knots |
| R5 | on one cord, cluster places are strictly monotone in `CLUSTER_ORDINAL` (one direction for the whole corpus, chosen as the majority direction and reported) | cords with ≥ 2 valued clusters |
| R6 | `L` or `E` knots appear only in the lowest-place cluster of their cord | cords with `L`/`E` |
| R7 | at most one `L`/`E` knot per cord, and at most 9 knots per cluster | all cords and clusters |

- **Decision rule.** A rule is *consistent* if its violation rate is below 1%. Violations are reported per khipu,
  and the khipus used in K001–K006 findings (UR113, KH0140/KH0483, KH0362/KH0049, the Puruchuco set, K001's ten)
  are checked by name. A planted control (a copy of the knot table with 50 known violations per rule injected) must
  find all 50 for each rule, or that rule is reported as *not auditable*.
- Knots of unknown type (`TYPE_CODE` not in S, L, E) are counted and reported, not judged.

## Disclosures (implementation fixes made after first runs, rules unchanged)
1. First run crashed on knots with no ordinal (no output).
2. **Schema misreading, caught by the R5 result itself.** `knot.CLUSTER_ORDINAL` is the knot's position *inside*
   its cluster, not the cluster's position on the cord. The first R5 run gave 82% violations because of this. R5 now
   uses `knot_cluster.ORDINAL`. That run's output was not kept, and the numbers below are from the corrected run.
3. **R2 scope.** 4 487 long knots have no `NUM_TURNS` recorded. They are counted as *not auditable*, not as violations.
4. **Exploratory check (not pre-registered).** `knot_cluster.TOTAL_VALUE` is 0 or empty in every cluster except 110,
   so a cluster-total check is *not auditable*. The R8 count in the JSON should be read that way.

## Results (`python3 tools/k007_decoding_audit.py data/khipu.db`, about 1 s; `analysis/k007_results.json`)
110 677 knots in non-duplicate khipus; 886 have a type code other than S/L/E. The planted control found 50 of 50 for
R1, R2 and R3.

| Rule | Checked | Violations | Rate | Verdict |
|---|---|---|---|---|
| R1 `E` = 1 | 8 356 | 89 | 1.07% | just over the bar: 38 `E` knots valued 10, 24 valued 100, 22 valued 0 |
| R2 `L` = turns, 2–9 | 21 893 (4 487 not auditable) | 490 | 2.24% | inconsistent at 1%: 148 real mismatches; the rest are turns of 0, 1 or 10 |
| R3 `S` = 10^k | 75 055 | 31 | 0.04% | consistent |
| R4 one place per cluster | 15 993 | 15 | 0.09% | consistent |
| R5 places decrease along the cord | 15 675 | 3 069 | 19.6% | **not a single-number pattern** (see below) |
| R6 `L`/`E` only in the units cluster | 30 788 | 9 | 0.03% | consistent |
| R7 ≤ 1 `L`/`E` per cord, ≤ 9 `S` per cluster | 90 956 | 2 749 | 3.0% | mostly the same cords as R5 |

The direction is clear: 12 606 cords have places decreasing by cluster ordinal, and only 151 increasing.

**What R5 is really showing.** Of the 3 069 R5 cords:
- 2 849 have two or more units clusters, which looks like two numbers knotted on one cord.
- 233 repeat a higher place.
- 167 have places out of order.

This is a known khipu phenomenon (cords carrying more than one number), not a decoding error. But it matters for us.

## Audit of K001–K006
Our cord value is the plain sum of knot values. **2 437 of the 25 091 nonzero pendants we used (9.7%, in 224 of 457
khipus) are R5 cords**, where that sum mixes two numbers. Among the named khipus, UR113 has 17 such cords, the
Berlin pair UR1114/UR1123 has 6 and 1, and KH0140 has 1. **Earlier results are not withdrawn**, because the
nulls used the same definition for real and shuffled data, so the tests stay valid. But what a "value" means on
those cords is unclear. Sensitivity reruns with those cords excluded are a new open line (8).

## Verdict
- The decimal encoding in `khipu.db` is internally consistent for S knots, places within clusters, and where
  units knots sit (R3, R4, R6 under 0.1%).
- `E` and `L` knots have small but real inconsistencies (R1 1.1%, R2 2.2% with 148 hard mismatches), listed by knot
  id in the JSON. These are a possible data-quality note for the OKR, after a manual look at examples.
- About a tenth of pendants carry multi-number patterns that our sum flattens. That's a measurement caveat for
  every earlier cycle, now made explicit.
