# PE012 · Header structure: does the header sign predict the number system and the size of the entries?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration** (this file, `tools/pe012_header.py`, `tools/pe012_recount.py`, the label-free
`analysis/pe012_inventory.json` and the rehearsal on destroyed/planted data `analysis/pe012_rehearsal*.json` are
published before any observed header–label association is computed). Open line 5 of the expedition README, never
tested. The expedition resumes after the Rongorongo camp paused (RR014, `2b3bb56`; see `../TRIAGE.md`).

## Why this line
Most proto-Elamite account tablets open with a **header** line: one or a few signs, no numeral, then the list of
entries. CDLI's editors mark it in the ATF with a `# header` comment. If the header names the kind of account (grain,
animals, workers…), the header sign should carry information about **which number system** the entries use and
**how large** they are. Born et al. (CAWL 2023) use the first sign of the tablet as a classifier feature (FIRST_SIGN);
nobody has, to our knowledge, put the header–system link through a calibrated permutation test with planted power.

## Data (re-pinned this cycle)
`cdliatf_unblocked.atf` and `cdli_cat.csv` **downloaded again** from cdli-gh/data at `d66b12b` (Git LFS media URLs) on
2026-11-09 12:08 PT: sha256 `2896ec253767fa07fcaa5424af6fc25d6a047dc30b99c95f99d57ce75384d836` and
`2e3232f75325b61c4d1e788d4d8c074c6230a947aed422110f9f35a6e353d09c`, **identical to the PE001 pins**; `pe.atf` rebuilt by
`pe001_totals.py fetch`: 1 729 catalogue ids, 1 585 texts, sha256 `5c4860ab…159a6`, identical to the manifest.

## Definitions (fixed before looking)
- **Header**: obverse line `1.` immediately followed by the editors' `# header` comment, with no numeral. Header
  **key** = its first token, damage marks removed, a complex grapheme `|A+B|` reduced to `A`, the variant suffix `~x`
  removed (M157~a → M157). Non-sign tokens (`x`, `...`) → no key.
- **Entries**: obverse numeral slots after the header line, numeral part intact (no `[ ] # ? ...`, no `n(...)`), every
  sign in Englund's S/D/B/C tables (as PE001–PE011). Other breaks on the tablet are allowed (the header is what we need).
- **SYSTEM label (H1)**: with the bundling readings of Born et al. (as in PE011): C if ≥ 1 entry is valid only in C and
  none only in an integer system; I the reverse; MIX if both; no label if every entry is ambiguous.
- **SIZE label (H2)**: order of the largest unit sign over the entries: 0 = only C fractions (N39B N24 N30C N30D N39C),
  1 = N01, 2 = N14, 3 = anything higher (N34 N45 N48 N23 N51 N54).
- **Sets**: header keys that occur on ≥ 3 tablets of the labelled set.

## Label-free inventory (`analysis/pe012_inventory.json`; computed before this file)
623 tablets carry an editorial header key; 549 also have ≥ 1 intact entry (excluded: 962 no key, 74 no intact entry).
- **H1**: 234 tablets, 15 keys (M157 129, M327 26, M136 17, M305 15, M387 9, then 3–5 each); labels C 160, I 60, MIX 14.
- **H2**: 493 tablets, 25 keys (M157 244, M327 67, M136 25, M305 24, …); SIZE 0: 36, 1: 218, 2: 189, 3: 50.
The independent recount (`tools/pe012_recount.py --counts-only`, own parser and literal tables, imports nothing)
reproduces every one of these counts.

## Tests (fixed now)
| Id | Statistic | Null strata (header keys permuted within) |
|---|---|---|
| **H1 SYSTEM** | G = 2 Σ O ln(O/E), header key × {C, I, MIX} | number of entries (1 / 2–3 / 4–7 / ≥ 8) |
| **H2 SIZE** | between-key sum of squares Σ n_h (mean_h − mean)² of the size order | number of entries × SYSTEM label (C/I/MIX/none): size information **beyond** the system |

R = **9 999**, seed **1201**; p = (1 + #null ≥ obs)/(1 + R); attainable floor 1e-4. Holm over the 2 tests at α = 0.05
(Holm levels 0.025 / 0.05 are > 2 × 1e-4, so R is not the binding limit).
Seeds follow the PE convention (PE0NN → NN01…): 1201 null, 1202 FPR, 1203 power, 1204 power curve, 1205 audit, 1299
registered shuffle. (The planning note suggested 12120; the PE convention wins, nothing used 1201–1299 before.)

## Gates (re-run identically in `test`; a failed gate = NOT TESTABLE)
- **FPR**: 40 destroyed datasets (keys permuted within strata), R 299: rate p ≤ 0.05 must be ≤ 0.10.
- **Power**: 100 datasets — destroy first (so no real header–label link survives), then each key gets one target label
  drawn from the set's labels and each tablet (prob **0.5**) takes its key's target; R 299; rate p ≤ 0.025 (Holm level)
  must be ≥ 0.80.
- **Size**: ≥ 30 tablets in ≥ 3 keys.

## Rehearsal before this push (destroyed and planted data only; disclosed)
- **v1, plant 0.3** (`analysis/pe012_rehearsal_v1_plant03.json`): FPR 0.075 / 0.05 ✓, **power 0.61 (H1) / 0.76 (H2) ✗**.
  With plant 0.3 both tests would have been NOT TESTABLE, dead on arrival.
- **Change made, and why**: the plant was raised to **0.5** (half the tablets follow a header rule). This does not touch
  any observed number; it narrows the claim. A NOT DETECTED verdict will rule out only a *strong* header dependency of this
  kind, not a moderate one. Power curve (40 datasets each): H1 0.05 / 0.125 / 0.575 / 0.90 and H2 0.025 / 0.375 / 0.80 /
  1.00 at plant 0.1 / 0.2 / 0.3 / 0.5.
- **v2, plant 0.5** (`analysis/pe012_rehearsal.json`): FPR 0.075 / 0.05 ✓, **power 0.88 / 1.00 ✓**, size ✓. Timing
  (borrowing Kryptos's I-169 habit): H1 gates 2.9 s, H2 5.3 s, whole rehearsal 20 s.
- **Smoke run on registered shuffle 1299** (pipeline exercised end to end on a destroyed copy): H1 G 23.98 (null mean
  29.23, p 0.787), H2 SSB 21.07 (null mean 15.10, p 0.078). Not observed values.

## Decision rule
NOT TESTABLE if any gate fails; **SUPPORTED** if Holm p ≤ 0.05; **NOT DETECTED** (powered for plant 0.5) otherwise.
No EXCLUDED verdict is available for these statistics (no natural rate bound).

## Disclosure: what has been looked at
- PE011's label-free inventory printed the header (FIRST_SIGN) prediction mix of its 46-tablet set (6 predictions, all C)
  and its descriptive H2 (2 doubly-labelled tablets, 0 agree). Nothing else about header × system was ever computed.
- This cycle computed, before the push: the inventory above (marginals only), the rehearsal on destroyed/planted data,
  and the smoke run on shuffle 1299. No cross-table of header × label on the real pairing was formed.

## After the decision (descriptive, no weight)
Header key × label tables; the recount script's G and SSB must equal the tool's.

## PE011 audit (this cycle)
PE011's decision test (H1 OBJECT, 12/17 agree, p 0.148 with R 1 999, seed 1101) re-drawn with a **new seed 1205 and
R 9 999**: n and agree must be identical and p must stay > 0.05.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
