# K094 · Rescue design for K093: the K065 cross-site leads on KFG, inside the pre-named Berlin–Dallas sub-family (README line 9)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registration**, committed with the tool and the A0 audit **before** the registered run. **No observed lead W on KFG
has been computed by anyone in this repository** (K093's gate stopped its tool before that step; this tool computes it only after
its own gates pass).

## Why this one — and the multiplicity disclosure
K093 (`992a5a7` / `8173d9c` / `05ab538`) re-ran K065's P-unit confirmation on KFG: A0 exact, S0/G0 20/20, N 496, F_x 118 849,
bar 28.854, G1 FPR 0.025 (pass), but **G2 power 0.73** (Wilson 0.636–0.807) **< 0.80**, so L1 KH0143·KH0591 (OKR CONFIRMED),
L2 KH0156·KH0432 and L3 KH0377·KH0590 were NOT TESTABLE and no W was read. K093's verdict pre-named **two** rescue designs, to be
registered before any lead W: (i) a smaller family named in advance (K060-style), *e.g. pairs with at least one Dallas (QU) or Berlin
(VA/AS) member*; (ii) a power curve over plant length (8/10/12), each lead read only at its length class.

**This is a second design on the same question, chosen after K093's gate failed. I disclose it as such:** K094 is the *rescue* named
in K093 before any KFG W, it uses **fresh seeds**, and it is the **last** design for these three leads under this engine: if its
G2 fails too, the leads stay NOT TESTABLE on KFG and line 9 moves on (no third family, no cell-shopping). Because no KFG W has been
seen, the choice of design cannot have been steered by the leads' scores; it was steered only by K093's published gate numbers and
K065's published OKR artefacts, listed here.

**Why (i) and not (ii)** (from published artefacts only, no KFG W):
- K093's plants are 8 distinct non-zero cords with one interior cord altered, i.e. **7 matched cords**. K065's published OKR leads
  match **K = 4** (L1), **6** (L2), **6** (L3) cords (`analysis/k065_results.json`). Under design (ii)'s rule — read a lead only if
  its matched length is ≥ the shortest plant length passing G2 — every lead is shorter than the shortest class (8), so (ii) would
  leave **all three NOT TESTABLE by construction**. It cannot rescue anything; it would only certify longer copies.
- K093's diagnosis: the null bar barely moved (28.85 vs OKR 29.12) while the plant distribution has a weak tail (20 % quantile
  27.79, just under the bar). The lever that moves a max-W bar is the **family size** (K060: a 23× smaller family doubled power).
  So (i) attacks the actual bottleneck.
- Within (i) I take **exactly the family K093 named** (Berlin or Dallas member), not a new one: choosing another sub-family now
  would be a new forking path. It contains all three leads (L1 Berlin·Dallas; L2 Berlin·Berlin, different provenances Nazca/Ica;
  L3 Miami·Dallas); the diagnostic KH0309·KH0293 (Puruchuco · "Museum für Völkerkunde s/n G", not a VA number) is **not** in it.

## Disclosed before this commit
- **Family size, metadata only** (smoke, values shuffled within khipu, plumbing): F_DB = **59 406** pairs (half of F_x 118 849);
  147 khipus with a Berlin VA number (126) or in the Dallas Museum of Art (21); all three leads in F_DB, diagnostic not. Smoke
  output (R 20 / 4 / 4, meaningless) deleted; no real gate value read.
- **A0 already run** (mode `a0`): this tool with family F_x and K093's seeds 6493–6495 reproduces **every** field of
  `analysis/k093_results.json` except `seconds`/`mode` (differing fields: none; crit 28.853973557786595, G1 0.025, G2 0.73).
  Written to [`analysis/k094_a0.json`](../analysis/k094_a0.json) (sha256 `1b92ed60…`), 60.4 s. A0 mode never computes an observed W.
- Everything K064, K065, K073 and K093 published (incl. K073's K010-engine KFG L3 score S 65.86, p 0.001).
- **Expectation, written now:** halving a max family lowers the bar only modestly; G2 may well fail again. That is an allowed outcome.

## Design (K093 verbatim except the family and seeds)
- **Tool** [`tools/k094_kfg_k065_rescue_family.py`](../tools/k094_kfg_k065_rescue_family.py), SHA-256
  `6001444739955c14174d8406fa9159fe136226a82946c3dcc4ed7c1046bdb64b`; produced from K093's tool (sha256 `bd531d33…`) by text edits only: family filter, seeds, output paths, A0 mode, input
  delta fields. Kernel `tools/k065_wham1.c` verbatim. Data: KFG `kfg_20261111.db` (`582e548d…`), `p<n>` pendants, R5 masked,
  eligible ≥ 10 non-zero; weights over the full KFG corpus (unchanged; not re-estimated on the sub-family).
- **Family F_DB** = pairs of K093's F_x (different or unknown provenance) with at least one member whose KFG `museum_number` starts
  with `VA` (Berlin, Ethnologisches Museum) **or** whose `museum_name` is `Dallas Museum of Art`. |F_DB| = 59 406.
- **Null P-unit** (K065 verbatim). **Rule:** p_adj = (1 + #{null F_DB max W ≥ W_obs}) / (1 + R), R = 1 000, seed **6496**;
  **Holm over L1–L3 at α 0.025** (m fixed at 3). Diagnostic D: not in F_DB → reported as not in family. Secondary: step-down max-W
  under P-unit over F_DB, up to 15 steps (descriptive).

## Gates (in order; the tool enforces them before any observed W)
- **A0** K065 rebuilt on OKR (`k093_a0.json`, passed) **and** K093 rebuilt by this tool on F_x (`k094_a0.json`, passed).
- **G-DATA** OKR and KFG hashes. **S0** unit fixture (seed 6408) 20/20. **G0** W fixture (seed 6404) 20/20.
- **G1 FPR:** 40 P-unit KFG nulls (seed **6497**), share whose own F_DB max reaches p_adj ≤ 0.025 must be **≤ 0.10**, else EXCLUDED.
- **G2 power:** **100** plants (seed **6498**; K093 plant design verbatim, plant pair drawn uniformly from F_DB), recovered iff
  p_adj ≤ 0.025; **power ≥ 0.80** (Wilson 95 % reported), else NOT TESTABLE and no observed W.

## Hypothesis and decision rule (per lead, mapped to the OKR verdict)
- **H1:** the lead's KFG W beats the F_DB family maximum of the P-unit null (Holm-adjusted). Scope: this is a confirmation
  **within F_DB**, a smaller family than K065's; a KFG REPLICATED here is weaker than K065's OKR CONFIRMED and is labelled so.
- **L1** (OKR CONFIRMED): confirmed in F_DB → **REPLICATED (F_DB scope)**; gates pass and not confirmed → **CHANGED (correction)**
  — not even the smaller family confirms it on KFG; addendum to K065. G2 fails → **NOT TESTABLE**; A0/S0/G0/G1 fail → **EXCLUDED**.
- **L2, L3** (OKR NOT CONFIRMED): not confirmed → **REPLICATED (not confirmed)**; confirmed → **CHANGED (now confirmed in F_DB)**,
  an addition from KFG data.
- **Input delta printed beside every verdict** (K087 lesson): KFG W, K and matched segments next to K065's OKR W, K, segments.
- A confirmed lead is a **lead for the archives**, never a reading.

Seeds 6496 (reference), 6497 (FPR), 6498 (plants); fixtures 6408/6404 reused (data-independent). **Next free 6499.**
Compute ≈ 1 minute under `timeout 600`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
