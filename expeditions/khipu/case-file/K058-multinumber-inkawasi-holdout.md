# K058 · Does the held-out Inkawasi "totals coloured apart" result (K023) survive the multi-number (R5) mask?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any masked K058 number. (The empty-mask fixture G0 was checked once beforehand: it reproduces K023's 49 sum cords, 15 khipus, A = 13.8621; no masked quantity was looked at.)

## Why this line
A scan of `tools/` for R5 handling shows the frozen results never re-run under the K008 mask are now only: K022 (sum vs summand colour; primary was a published post-hoc-prompted negative) and **K023**, its pre-registered held-out test, the only *supported* (barely) result among them. K023 was left "weakly supported, not established" (p 0.048; 0.062 without KH0502, the published twin of UR275). The cross-khipu tools K010–K020 already zero R5 cords in their own code (4 R5 references each). K058 closes the last unmasked supported result of line 6/8.

## Frozen target
K023: 15 held-out Incahuasi khipus (PROVENANCE = 'Incahuasi' minus the ten K001 BH-significant), 49 sum cords, A = 13.862 vs null 17.322 ± 2.086, one-sided p = 0.048 (apart). Same pinned data (OKR `4039ca5`, SHA-256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`). Same-data sensitivity, not independent replication.

## Mask (K008, as K053–K057)
R5 pendants (3 069) keep their position but are never a sum-cord target, never in a legal summand block, never an eligible null anchor, and never inside a null anchor's block. The masked block search takes the first *legal* block (smallest k in 2..12, right before left). Statistic A and the anchor-redraw null are K022/K023's, unchanged.

## Pre-registered decision rule
α = 0.05, one-sided, seed 5858, R = 20 000.
- **Gate FPR** (200 random anchor draws from the masked pools, seed 5859) ≤ 0.08, else EXCLUDED.
- **ROBUST** if p ≤ 0.05 under the mask. Flagged **fragile** if any of five extra null seeds (58601–58605) gives p > 0.05.
- **NOT ESTABLISHED under the mask** if p > 0.05 and power ≥ 0.5 (200 plants, each block cord recoloured away with prob 0.3, seed 5860).
- **NOT TESTABLE** if p > 0.05 and power < 0.5.
- Disclosed secondary, no decision weight: the same without KH0502 (K023's independence concern).
- Any difference of sum-cord counts is reported descriptively (raw 49 → masked n).

Tool: [`tools/k058_multinumber_inkawasi_holdout.py`](../tools/k058_multinumber_inkawasi_holdout.py). Compute: seconds.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
