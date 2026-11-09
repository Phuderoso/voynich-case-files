# PE014 · Ratio accounts: do paired notations stand in exact small ratios more often than chance?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **PRE-REGISTRATION** (this file, `tools/pe014_ratio.py`, the label-free `analysis/pe014_inventory.json` and the
rehearsal on destroyed/planted data `analysis/pe014_rehearsal.json` are pushed before any observed ratio is computed).
Open line **4** of the expedition README (ratio accounts; PE009 said they should be sought between paired notations, not
between the reverse and the obverse sum).

## Why this line
Two published ratio conventions motivate it: Born et al. (2023, §4.1.2 and App. A) — in a group of two-entry texts the
S-counted M056~f is always exactly **2.5 × N01S per N01C** of M288, and on P008212 M288 entries are exactly 4× / 2× the
adjacent M376 / M367~i entries; Englund (2004) — **2½ N39b per M54** rations. If ratio accounting is a general practice,
paired notations should land on exact small ratios more often than a structure-preserving shuffle allows.

## Data
Pinned CDLI files as PE012/PE013: `pe.atf` sha256 `5c4860ab…159a6` (re-checked on the box this cycle, identical to
`data/MANIFEST.md`), `cdli-gh/data` at `d66b12b`.

## Definitions (fixed before looking)
- **H1 IN-LINE** (literal line 4: two notations inside one entry): a line whose numeral tokens, after compound graphemes
  `|…|` are collapsed, form ≥ 2 runs separated by a readable sign or the comma; no damage mark, `n(…)` or `x` on the line;
  all signs known. Pair = first two runs.
- **H2 ADJACENT** (the corpus' own form, one notation per entry, Born's pairs sit in consecutive entries): consecutive
  intact obverse entries (PE012 `entry_ok`; a damaged numeral line breaks the chain), **both informative** (≥ 2 distinct
  numeral signs, so `2(N01)` vs `1(N01)` cannot carry the result). Born-named tablets (P008212, P008791, P008796–P008802,
  P008804, P008805, P008810) **excluded** — a known result is not new; Englund's M54 tablet is not identified in our
  sources and cannot be excluded (disclosed).
- **Value**: every reading the notation is valid in (PE011 `readings`, Englund S/D/B/C), converted exactly to N01 units
  (`fractions.Fraction`; C fractions per Englund's chain 5, 2, 3, 2, 2).
- **HIT**: some pair of readings gives a ratio in RSET = {p/q : 1 ≤ p, q ≤ 6, gcd 1, p ≠ q} (1 excluded: a repeated
  notation is not a ratio account; 5/2 is in the set). **T** = number of hit pairs.

## Label-free inventory (`analysis/pe014_inventory.json`; no ratio computed on observed data)
- **H1: dead on arrival.** 35 lines carry two numeral runs, 34 of them damaged (`[...]`, `#`, `n`, `x`); **1 intact pair**
  (P009531) against the size gate of 30 → **NOT TESTABLE, NOT RUN**. The corpus writes paired notations as separate entries.
- **H2**: 1 090 informative intact obverse entries (Born tablets dropped: 12 tablets, 1 pair), **272 adjacent informative
  pairs** on 559 tablets (98 tablets with ≥ 3 informative entries carry 215 of them), 50 null strata.
- **M009 → M157 lead (PE013, post hoc)**: a confirmatory check needs tablets that PE013 did not see. PE013 used every keyed
  subscript of the whole pinned corpus (91 tablets), so there is **no held-out data → NOT TESTABLE without new tablets**;
  not pre-registered here. It reopens only with newly published proto-Elamite tablets.

## Tests (fixed now)
- **H2** — T on the 272 pairs vs the **structure-preserving null**: notations permuted across all 1 090 slots within strata
  = (top sign, reading set, distinct signs capped at 3). Order of magnitude, system ambiguity, notation complexity and
  tablet structure are kept; only which digits stand next to which changes. One-sided, R 9 999, seed **1401**.
- **H2W** — within-tablet **confound control**: same T, notations permuted only among the informative entries of the same
  tablet (keeps each tablet's magnitudes and repertoire). Two-entry tablets cannot move T (RSET is closed under inversion),
  so power comes from the 98 tablets with ≥ 3 entries. One-sided, R 9 999, seed 1401 + 20000.
- **Holm** over the runnable tests (H2, H2W). **Interpretation rule**: "ratio accounts SUPPORTED" needs **both** H2 and H2W
  Holm p ≤ 0.05. H2 alone = exact ratios beyond the magnitude-matched null but not beyond tablet-level similarity (no
  ratio-account claim). H2W alone = ordering effect without a corpus-level excess.

## Gates (re-run identically in `test`; a failed gate = NOT TESTABLE, NOT RUN on observed data)
- Size: H1 ≥ 30 pairs; H2/H2W ≥ 60 pairs.
- FPR: 40 destroyed datasets (one null shuffle each), R 299, rate of p ≤ 0.05 must be ≤ 0.10 (seed 1402).
- Power, plant strength fixed by the effect of interest **before** gating: a ratio convention on 20 % of informative pairs
  (each pair with prob 0.2 gets its second notation replaced by the canonical notation of value(first)/r, r ∈ {2, 3, 5/2,
  3/2, 4, 1/2}, in a system the first reads in, kept only if representable with ≥ 2 distinct signs). R 299, rate p ≤ α/k
  (k = 2) must be ≥ 0.80 in **both** independent batches of 100 (seeds 1403, 1404 — the second-batch rule from C094 /
  Kryptos I-182).

## Rehearsal before this push (destroyed/planted data only; `analysis/pe014_rehearsal.json`, 124 s)
| Test | pairs | FPR | power batch 1403 | power batch 1404 | planted pairs (mean) | gate |
|---|---|---|---|---|---|---|
| H1 | 1 | — | — | — | — | **size fails → NOT TESTABLE** |
| H2 | 272 | 0.075 | 0.97 | 0.97 | 26.6 / 27.1 | pass |
| H2W | 272 | 0.05 | 0.88 | 0.89 | 27.8 / 27.6 | pass |

Only ~27 of the 54 drawn plants are representable, so the gate actually certifies a convention on ~10 % of pairs.
Power curve (40 datasets, α/k 0.025, f = 0.1 / 0.2 / 0.3 / 0.5): H2 0.55 / 1.00 / 1.00 / 1.00; H2W 0.425 / 0.95 / 1.00 / 1.00.
A weak convention (f 0.1, ~5 % of pairs) is not powered. Smoke on the registered shuffle 1499 (not the observed statistic):
H2 T 37, p 0.565 (null mean 37.45); H2W T 43, p 0.022 (null mean 34.27) — one draw from the null, in its 2 % tail.

## Disclosure: what has been looked at
The inventory counts above, the two published ratio conventions (Born, Englund) and, from earlier cycles, PE009's reverse
vs obverse ratios. The null means of the rehearsal are properties of the shuffled corpus (they are the same for observed
and shuffled data); no observed T has been computed. Tool written in this cycle, before the push.

## Decision rule
H1 NOT TESTABLE (not run). H2/H2W: Holm p ≤ 0.05 → SUPPORTED, else NOT DETECTED; a NOT DETECTED with the gates above
**EXCLUDES** a ratio convention on ~10 % of informative pairs (f 0.2), not a weaker one.

## After the decision (descriptive, no weight)
The full set with the Born tablets put back; the RSET ratios that hit most often.

## PE013 audit (this cycle)
PE013 H3 REPEAT re-drawn with seed **1405**, R 9 999; must give M 3 / n 81 and p > 0.05 (published 0.4305, exact 0.4349).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
