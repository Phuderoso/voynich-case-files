# PE006 · Do capacity (grain) tablets balance less often? A fresh-sample test of the PE005 lead

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration** (this file and `tools/pe006_cap.py` are committed before any balance label of the new
tablets, any gate, or any association is computed).
Looked at beforehand (disclosed): the **label-free** inventory `analysis/pe006_inventory.json` (size of the fresh set,
CAP prevalence, R/H classes, editions; no balance labels) and a by-eye check of ~17 damaged numeral lines to confirm
the parser reads `#`/`?` flags and `[ ]` restorations as intended.

## Why this line
PE005 found one lead, not a result: on the 43 intact single-total tablets, those with capacity sub-unit signs (CAP)
balance 4/19 vs 18/24 for the rest (two-sided p 0.00067), but its parity-split confirmation was underpowered (power
0.43) and the even half gave p 0.167. The open line (README line 7) is to **enlarge the labelled set honestly** and test
CAP alone. Instead of mixing new tablets with the 43 that generated the lead, PE006 tests CAP on a **disjoint, fresh
set** that was never labelled: a clean out-of-sample replication with one test and no split penalty.

## Data
Pinned CDLI dump `d66b12b` (`pe.atf` sha256 `5c4860ab…159a6`). **Fresh set** = tablets **not** in the PE004/PE005
calibration set that pass the same shape rules (no broken `$`-line on obverse/reverse, no primed line, ≥ 2 obverse
numeral slots, exactly 1 reverse numeral slot) and have **≥ 1 damaged numeral part** (`[ ]`, `#`, `?`) where **every**
damaged numeral part is **completely read** by the editor: after removing `[ ] # ?` there is no `...`, no `n(…)`, no
`x`, and every notation maps to S/D/B/C. Tablets with no common system would be excluded (there are none).
Label-free inventory: **n = 64** (88 single-total candidates dropped because a damaged numeral is not completely
read). Classes: **H = 55** (only `#`/`?` flags: damaged but read signs), **R = 9** (≥ 1 editor restoration in `[ ]`).
**CAP = 32/64** (29 in H, 3 in R). Editions: MDP 26 (22), MDP 06 (16), MDP 17 (9), MDP 31 (7), MDP 26S (4), others 6.
**Label**: balances = Σ entries = total in ≥ 1 admitted system (`pe001_totals.balances`, Englund's sub-units), as in
PE001–PE005. **CAP**: N39B, N24, N30C, N30D or N39C present (PE005 definition, unchanged).

## Hypothesis, metric and decision rule
- **H1 (primary, the only decision test)**: on the fresh set, CAP tablets balance **less** often than non-CAP tablets.
  Metric: **one-sided exact Fisher test** (direction fixed by PE005), **α = 0.05**. One primary test → no
  multiple-comparison correction needed; everything else below is descriptive and carries no decision weight.
- **Verdicts**: **NOT TESTABLE** if a gate fails · **SUPPORTED** if gates pass and p ≤ 0.05 · **NOT DETECTED** if gates
  pass and p > 0.05 (this excludes only effects as strong as the plant; it would also be reported as weakening the
  PE005 lead). **EXCLUDED** is reserved for a gated test showing the effect is absent with a bound; it is not claimed
  from a single non-rejection.

## Gates (computed after this file is published, before the real test)
- **FPR gate** (structure-preserving null: CAP permuted across the 64 tablets, prevalence and balance labels kept):
  R = 2 000, seed 601; rate of p ≤ 0.05 must be **≤ 0.06**.
- **Power gate**: a planted feature with CAP's prevalence (32/64), drawn without replacement with **weight 4** for
  non-balancing and 1 for balancing tablets (PE005's planted strength), R = 2 000, seed 602; rate of p ≤ 0.05 must be
  **≥ 0.80**. Weight 9 reported (descriptive).

## Descriptive (no decision weight)
- **S1 sensitivity, H only** (55 tablets, no editor restoration): an editor who restores a numeral from the total makes
  a tablet balance by construction; H tablets are free of that. **S1b**: R only (9).
- **Pooled** 43 + 64 = 107 tablets (contains the discovery data, so descriptive only).
- **Edition-stratified permutation** (CAP shuffled within primary publication, R = 20 000, seed 603): CAP is
  concentrated in MDP 26 (PE005 H3); this checks that the H1 association is not just an edition effect.

## Audit of PE005
Re-run `pe005_balance.py test` from the published tool in a scratch copy and compare every field of
`analysis/pe005_results.json` (run time excluded); re-check the CAP table 4/15/18/6, p 0.00067.

## Honest limits
The fresh tablets carry damaged (but read) numerals: misreadings of `#` signs add label noise that can only dilute a
real effect (bias toward NOT DETECTED). Balance is arithmetic under Englund's tables, not a statement about what the
scribes meant. No decipherment is claimed.

Tool: [`tools/pe006_cap.py`](../tools/pe006_cap.py) (`inventory`, `gates`, `test`, `audit`).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
