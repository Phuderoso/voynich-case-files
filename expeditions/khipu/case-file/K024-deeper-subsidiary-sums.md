# K024 · Deeper levels: does a subsidiary record the sum of its own subsidiaries? (open line 7)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K024 statistic was computed.

## Why
K004 found that level-1 pendants often equal the sum of their level-2 subsidiaries (corpus-wide, strongest in UR113).
Line 7 asks whether the same rule continues one or more levels down. These are **different cords** from K004's, so
this is a fresh question, not a re-use of K004's hits.

## Definitions (K004's rules, moved down a level)
- **Eligible parent:** a cord at level L ≥ 2 with value ≥ 10 and at least 2 children at level L + 1
  (children = cords whose `PENDANT_FROM` is the parent). Value = sum of `knot_value_type` over the cord's knots.
- **Hit:** the parent's value equals the sum of its children's values, with at least 2 children nonzero.
- Duplicates (`DUPLICATE_FLAG = 1`) excluded.

## Null and tests
- **Null N_a (primary):** within each khipu, permute child values among all cords at **the same level** as the
  children (pooled over the khipu's levels ≥ 3, each level permuted separately). Keeps parent values, tree shape and
  each level's value distribution. 10 000 replicates.
- **Primary test:** corpus total H against the summed null, one-sided p = (1 + #null ≥ obs) / (1 + K).
  **Secondary:** the same test without KH0349 (UR113), reported with Bonferroni ×2 (α = 0.005 each for "evidence").

## Decision rule
p ≤ 0.01 (primary) counts as **evidence** that deeper subsidiaries record sums. Otherwise **not supported** if
planted power ≥ 0.5, **not testable** if below.

## Controls
- **Calibration:** 200 corpora where every khipu's child values are shuffled once and treated as observed;
  false-positive rate at 0.01 must be ≤ 0.03.
- **Power:** 200 shuffled corpora with **3 eligible parents** (chosen at random corpus-wide) set to the sum of their
  children (two children forced nonzero if needed), the smallest planted signal I'd want to see.

Compute: seconds.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (computed after the pre-registration commit `99e115c4`)

Tool: `tools/k024_deeper_subsidiary_sums.py` (9.9 s). Output: `analysis/k024_results.json`.

Deeper levels are sparse: **109 eligible parents** in 41 khipus (98 at level 2 with level-3 children, 11 at level 3).

| Test | Hits | Null mean | Null max (of 10 000) | p |
|---|---|---|---|---|
| **Primary** (all) | 2 | 0.89 | 5 | 0.22 |
| Without KH0349 (UR113) | 2 | 0.88 | 5 | 0.22 |

The calibration passes (0 of 200 false positives at 0.01), but **power with 3 planted parents is 0.22**, under the 0.5
bar. **Verdict: not testable** by the pre-registered rule. The two hits are in KH0183 (UR1166) and KH0536 (HP004),
one each. UR113 has no eligible deeper parents.

### Power curve (disclosed add-on, not pre-registered; it does not change the verdict)
Tool: `tools/k024_power_curve.py`. Output: `analysis/k024_power_curve.json`. With 100 control corpora each, power is
0.23 for 3 planted parents, **0.87 for 5** and 1.00 for 8. Since the data show about one hit above chance, a habit that
would put the sum on **5 or more of the 109 deeper parents (about 5 %)** would very likely have been seen, and it
wasn't. A rarer habit can't be ruled out.

### Line 7 status
The deeper-levels question is answered as far as the OKR allows: no detectable sum habit below level 1, and anything
under about 5 % is not testable. What's left on line 7 is the held-out replication of K004's non-UR113 signal, which
needs khipus that weren't in K004 (none in the OKR today).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
