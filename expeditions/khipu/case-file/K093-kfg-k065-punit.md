# K093 · KFG re-audit of K065: do the cross-site leads survive the periodicity-preserving null on Khipu Field Guide data? (README line 9)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registration**, committed with the tool before any KFG reference null, FPR, power or observed W was computed.

## Why this one
Line 9 re-audits published K0xx headlines on KFG data, one at a time. The OKR-vs-KFG table has K010 (K073) and the K064/K065
lead L3 (corrected by K073 under the K010 engine), but **not K065's own headline**: **L1 KH0143·KH0591** (Nazca khipu in Berlin ·
Dallas fragment) **CONFIRMED** under the P-unit null, single-step p_adj 0.0060 against the maximum over all 89 489 cross-provenance
pairs (Holm over L1–L3, α 0.025; G1 FPR 0/40, G2 power 0.81). L2 KH0156·KH0432 (p 0.033) and L3 KH0377·KH0590 (p 0.201) were
NOT CONFIRMED; the diagnostic KH0309·KH0293 was not significant (p 0.121). K093 re-runs that confirmation on KFG data.
Preferred over the README's other candidates ((a) H1 power curve, (b) K020 family with 1 000 nulls, (c) K091 mutual pairs)
because data-source migration of headlines comes first, and this is the last line-3 confirmation without a KFG row.

## Disclosed before this commit
- **K073 already published part of the KFG picture for L3:** on KFG, KH0590 p11 is 24 (OKR 25, KFG change 17 Jan 2026 "from Quave
  original data"), so KH0377·KH0590 share an exact 8-value run and passed K010's family-wise bar (S 65.86, p 0.001). Under the
  P-unit null and the Hamming-1 W, nobody has computed it. I expect L3's W to rise; whether it beats the KFG family maximum is open.
- **A0 already run** (mode `a0`, OKR only, published data): `tools/k065_periodic_unit_confirm.py` run **verbatim** with its own
  seeds at registered size (output to `/tmp`) reproduces **every** field of `analysis/k065_results.json` except run time
  (differing fields: none; reference crit 29.117799105892537; L1/L2/L3 W 29.704 / 28.179 / 25.465, p_adj 0.00599 / 0.0330 / 0.2008;
  G1 0, G2 0.81). Written to [`analysis/k093_a0.json`](../analysis/k093_a0.json) (sha256 `98d0b8c4…`), 66.5 s.
- **Structure seen in the smoke** (mode `smoke`: KFG values shuffled within each khipu, R 20 / FPR 4 / plants 4; plumbing only,
  output deleted): KFG N **496** eligible, F_x **118 849** cross-provenance pairs, 2 588 R5 pendants masked, all three leads and the
  diagnostic pair are in F_x (both members eligible, different or unknown provenance). S0 20/20, G0 20/20. No real W was computed.
- **Known source differences (named in advance):** KFG sequences are `p<n>` pendants only (OKR level-1 cords may include top
  cords; same choice as K071–K073); KFG has no duplicate flag (OKR dropped flagged duplicates; the KFG merged KH0483 into KH0140);
  provenance strings are the KFG's (quotes stripped). The family F_x and the rarity weights are therefore rebuilt on KFG.

## Design (K065 verbatim except data source and seeds)
- **Tool** [`tools/k093_kfg_k065_punit.py`](../tools/k093_kfg_k065_punit.py), SHA-256
  `bd531d33a97194f998316dabf9b1694b916b91316ed23d73bb2ec31e8db1a9b4`; kernel [`tools/k065_wham1.c`](../tools/k065_wham1.c) verbatim
  (SHA-256 `286ff1d3…7e985`). Engine blocks (runs, collapse, full-corpus weights −ln((n_v+1)/(N_T+V+1)), Hamming-1 W, `units`,
  `punit`, S0 and G0 fixtures, `pu_top` with top-40 per null, `plant_one`, Holm, step-down) copied text-for-text from K065.
- **Data:** KFG store `kfg_20261111.db` (SHA-256 `582e548d…742994d`); `p<n>` pendants in pendant order, value = KFG `value`,
  R5 pendants masked to 0 (K072/K073 KFG port); eligible ≥ 10 non-zero pendants; F_x = all pairs not sharing a known provenance.
- **Null P-unit** (K065): periodic stretches (period 2/3, ≥ 2 periods) move as units; units permuted uniformly, then collapsed.
- **Confirmation rule (K065):** p_adj = (1 + #{null F_x max W ≥ W_obs}) / (1 + R), R = 1 000 P-unit nulls, seed **6493**;
  **Holm over L1–L3 at α 0.025** (m fixed at 3). **Diagnostic D** KH0309·KH0293 (outside Holm; prediction: not significant).
  **Secondary:** step-down max-W list under P-unit, up to 15 steps.

## Gates (all must pass before the observed W is read; the tool enforces the order)
- **A0** K065 rebuilt verbatim on OKR (done, passed; the `full` mode refuses to run if `k093_a0.json` says otherwise).
- **G-DATA** KFG store hash; OKR hash.
- **S0** unit fixture (seed 6408, K065's), 20/20. **G0** W fixture (seed 6404, K065's), 20/20.
- **G1** FPR: 40 P-unit KFG nulls (seed **6494**), share whose own max reaches p_adj ≤ 0.025 must be ≤ 0.10, else EXCLUDED.
- **G2** power: 100 plants (seed **6495**; K065/K064 design: 8 distinct non-zero cords, one interior cord ±1..3, planted into a
  P-unit KFG null corpus), recovered iff p_adj ≤ 0.025; **power ≥ 0.80**, else NOT TESTABLE (no observed W read).

## Decision rule (per lead, mapped to the OKR verdict)
- **L1** (OKR CONFIRMED): confirmed on KFG → **REPLICATED**; gates pass and not confirmed → **CHANGED (correction)**, addendum
  appended to K065; G2 fails → **NOT TESTABLE**; S0/G0/A0/G1 fail → **EXCLUDED**.
- **L2, L3** (OKR NOT CONFIRMED): not confirmed on KFG → **REPLICATED (not confirmed)**; confirmed → **CHANGED (now confirmed)**,
  an addition from KFG data, recorded with the cord(s) that differ between sources (descriptive diff, post hoc).
- **D:** significant on KFG → published as a weakening of K064's periodicity explanation.
- A confirmed lead is a **lead for the archives**, never a reading.

Seeds 6493 (reference), 6494 (FPR), 6495 (plants); fixtures reuse K065's 6408/6404 (data-independent). **Next free 6496.**
Compute: about 2 minutes, `timeout 600`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
