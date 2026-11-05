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
