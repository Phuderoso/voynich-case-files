# K087 · KFG re-audit of K047: cross-khipu physical-feature agreement on the three K019 pairs (README line 9)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results appended** (pre-registration, tool and shuffled-feature smoke pushed as `3920169` before the real run).

## Why
Step 2 of the data-source migration: every published khipu result is re-run on the Khipu Field Guide (KFG,
Khosla, Medrano, Thompson and the KFG team) one at a time. K047 (OKR) asked whether cords that K019 aligned by value
across the three pairs KH0097·KH0586, KH0192·KH0470 and KH0192·KH0469 also agree in **termination** and **majority
knot direction**. Its headline: **no primary pair-field readable** (2 degenerate, 3 not testable at the 25 % plant
rate, 1 tool-excluded). K076 already rebuilt the same alignment on KFG (13/89, 14/37, 15/36: identical to K019).

## Question
On the KFG, with the same alignment, does any of the six pair-fields become readable (SUPPORTED or NOT SUPPORTED),
or does K047's "not readable" headline hold?

## Disclosed before writing this (whole-khipu frequencies on KFG level-1 pendants; never the alignment, never a cross-tab)
| Khipu | n | termination | knot-direction majority (S knots expanded by count) |
|---|---|---|---|
| KH0097 | 319 | K 245, B 52, ? 15, U 7 | S 139, Z 72, TIE 46, none 62 |
| KH0586 | 189 | K 168, B 18, U 3 | Z 162, none 27 |
| KH0192 | 224 | K 213, B 7, U 4 | Z 179, TIE 4, S 2, none 39 |
| KH0470 | 126 | K 120, B 6 | Z 52, S 30, TIE 8, none 36 |
| KH0469 | 125 | K 103, B 22 | Z 38, S 37, TIE 1, none 49 |
Twist is S on every pendant of KH0586/KH0192/KH0470/KH0469; attachment is a single code on each of those four, so
both stay census-only as in K047.

## Design (K047 frozen; only the data layer is ported)
- **Data.** KFG db `kfg_20261111.db` (SHA-256 `582e548d…742994d`) and its Excel files (CordGroups), hash-checked;
  OKR `khipu.db` @ `4039ca5` for F0. Tool `tools/k087_kfg_physical_agreement.py`.
- **Alignment.** K076's KFG data layer copied verbatim (pendants `^p\d+$`, R5 multi-number mask, CordGroups, leader
  weights over KFG eligible khipus, weighted leader LCS, within-group LCS). Gate: groups/V must be logged; any pair
  not eligible → NOT TESTABLE (data).
- **Physical port (the only new code).** termination, twist, attachment from the KFG `cord` columns; empty, `?`,
  `None`, `nan` → missing (excluded, as empty was in K047); `U` stays a label (as in K047). Length = float of
  `length`. Knot directions from the KFG cluster string, stored order: a direction string longer than one letter
  gives one letter per knot; otherwise S-type clusters (`S`, `SP`) give *n* knots and every other cluster type gives
  one knot; a trailing `[...]` annotation is ignored. Majority and ordered tuple then use K047's functions unchanged
  (only S/Z usable; ties → `TIE`). Fixture of 7 strings must pass.
- **Statistic, nulls, gates, verdict.** K047's `evaluate_categorical` unchanged: A = aligned units with equal labels;
  N1 = permutation of side B among units, R 10 000; α = 0.05/6 (Bonferroni, 3 pairs × 2 fields); degenerate if either
  side has < 2 distinct labels; n < 10 → NOT TESTABLE; gates: copy-all positive control (A = n and p < α), FPR of
  random permutations ≤ 0.08 (1 000) and of circular shifts ≥ 10 % ≤ 0.08; power at 25 % planted copies ≥ 0.5
  (200 reps × 2 000) else NOT TESTABLE; SUPPORTED iff p < α. N2 within-group, knot tuple, with-leaders, non-zero
  units and length Spearman are disclosed, never verdicts.
- **F0.** The K047 engine on OKR must reproduce K047's published (n, A) for all six pair-fields exactly, else EXCLUDED.
- **Seeds.** null 6468, calibration 6469, power 6470, N2 6471, sensitivities 6472; next free **6473**.

## Decision rule (OKR vs KFG, per pair-field)
- both unreadable (NOT TESTABLE / DEGENERATE / TOOL EXCLUDED) → **REPLICATED (not readable on either)**;
- same readable verdict → REPLICATED; OKR unreadable, KFG readable → **CHANGED (now readable: verdict)**.
- Headline: K047's "no primary pair-field readable" is REPLICATED iff no KFG pair-field is SUPPORTED or NOT
  SUPPORTED; otherwise CHANGED. A SUPPORTED pair-field would be a physical witness on the KFG only, labelled as such,
  and would need a held-out confirmation before any claim. No decipherment either way.

## Results (run 19 Nov 2026 ~18:10 PT, 9.0 s; `analysis/k087_results.json`)
Gates: G0 hashes pass; K047 fixture pass; KFG knot fixture 7/7; **F0 6/6** (OKR (n, A) = K047's exactly);
alignment on KFG 13/89, 14/37, 15/36 (identical to K019/K076).

| Pair · field | n | A | null mean | p | copy-all | FPR perm / shift | power (25 %) | KFG verdict | K047 (OKR) | OKR vs KFG |
|---|---|---|---|---|---|---|---|---|---|---|
| KH0097·KH0586 termination | 89 | 83 | 81.2 | 0.0686 | pass | 0.001 / 0.000 | 0.42 | NOT TESTABLE | NOT TESTABLE (n 87, p 0.047, power 0.36) | **Replicated (not readable)** |
| KH0097·KH0586 knot direction | 82 | 55 | — | — | — | — | — | DEGENERATE (B all Z) | DEGENERATE | **Replicated (not readable)** |
| KH0192·KH0470 termination | 37 | 33 | 33.2 | 1.0 | **fail** | 0 / 0 | 0.00 | TOOL EXCLUDED | TOOL EXCLUDED | **Replicated (not readable)** |
| KH0192·KH0470 knot direction | 27 | 19 | 19.5 | 1.0 | pass | 0 / 0 | 0.08 | NOT TESTABLE | NOT TESTABLE | **Replicated (not readable)** |
| KH0192·KH0469 termination | 36 | 31 | 31.3 | 1.0 | pass | 0.005 / 0.034 | 0.04 | NOT TESTABLE | NOT TESTABLE | **Replicated (not readable)** |
| KH0192·KH0469 knot direction | 21 | 17 | — | — | — | — | — | DEGENERATE (A all Z) | DEGENERATE | **Replicated (not readable)** |

Labels on the aligned units: KH0097·KH0586 termination A {K 83, B 4, U 2} / B {K 87, B 1, U 1}; KH0192·KH0470
A {K 36, B 1} / B {K 34, B 3}; KH0192·KH0469 A {K 33, B 3} / B {K 34, B 2}. The only data change: the two KH0097
cords whose termination was empty in the OKR are coded on the KFG, so n rises 87 → 89 with A unchanged (83);
the null mean rises and p moves 0.047 → 0.069 (never below α = 0.0083 on either), power 0.36 → 0.42.

Disclosed, not verdicts: ordered knot tuples A 21 / 11 / 12 (p 10⁻⁴ each; labels SUPPORTED / TOOL EXCLUDED /
NOT TESTABLE) and length Spearman ρ 0.206 / 0.242 / −0.078 (p 0.026 / 0.072 / 0.675) — the same values K047
printed. K047's caveat stands unchanged: KH0586 (and KH0192) record nearly every knot as `Z`, so a tuple match
is mostly "equal knot counts on cords already paired by equal value", a leak of the alignment, not a physical witness.

**Headline: REPLICATED.** K047's "no primary pair-field readable" holds on the KFG, 6/6. The KFG's curation did not
change a single label on the aligned cords; it filled two empty ends. Physical-feature *equality* on these fields,
for these three pairs, stays unreadable: termination is ~93 % `K` on both sides and knot chirality is a recorder
constant on two of the five records. Nothing is said about same-object vs copy. No decipherment.

### Next (line 9)
K048 (rare-label concordance: do the few `B` ends land on each other?) on KFG is the natural sequel; the counts above
already show its ceiling (at most 4 / 1 / 3 `B` units on the KH0097 / KH0470 / KH0469 sides of the aligned pairs).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
