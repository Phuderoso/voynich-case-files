# PE001 · Do proto-Elamite reverse totals balance the obverse entries, under the published factor tables?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed with the tool before any H1/H2 number was computed. Looked at beforehand
(disclosed): sign inventory and candidate counts only (strict 38 tablets, lenient 65), and the timing of one shuffled
evaluation. No observed balance count, no p-value, no factor comparison.

## Data
CDLI bulk dump [cdli-gh/data](https://github.com/cdli-gh/data) at commit `d66b12b` (dump of Aug 2022), files
`cdliatf_unblocked.atf` and `cdli_cat.csv` (SHA-256 in [data/MANIFEST.md](../data/MANIFEST.md)). Proto-Elamite
texts = catalogue `period` contains "Proto-Elamite" (1 729 ids), of which 1 585 have ATF. The extract is rebuilt by
`tools/pe001_totals.py fetch`; nothing from CDLI is redistributed here.

## Why this line
Proto-Elamite accounts list entries on the obverse and very often a total on the reverse (Englund 2004; Dahl et al.,
CDLJ 2005:3). A total either equals the sum or it does not: plain arithmetic. Checking this across the whole corpus
does two things at once: it tests the published factor tables (wrong values make true totals fail), and it yields a
list of intact tablets whose arithmetic does not close, which is useful for collation.

## Number values (frozen before running)
From Englund 2004, Fig. 5.4, and the CDLJ 2005:3 factor diagram:
- S (sexagesimal): N01 1, N14 10, N34 60, N45 600, N48 3 600
- D (decimal): N01 1, N14 10, N23 100, N51 1 000, N54 10 000
- B (bisexagesimal): N01 1, N14 10, N34 60, N51 120, N54 1 200
- C (capacity): N48 ←10– N34 ←3– N45 ←10– N14 ←6– N01 ←5– N39B ←2– N24 ←3– N30C ←2– N30D ←2– N39C
- Framed/derived variants (`@b`, `@c`, `@g`: B#, C#) take the base values; `N1` = `N01`. Numerals inside complex
  graphemes `|...|` are not counts. Any other numeral sign (N08A, N02, N39A, N46, …) makes the tablet not testable.

## Candidates (rule fixed in the tool)
≥ 2 obverse lines with numerals; **exactly one** reverse line with numerals (the total); no `[ ]`/`...` on obverse or
reverse lines; no `$` line saying broken/missing/effaced/illegible/traces/lost on obverse or reverse.
**Strict** (primary): no `#` or `?` in any numeral part. **Lenient**: `#` allowed, `?` not.
A tablet **balances** if, for at least one system whose table covers every sign used, Σ obverse = reverse total exactly.

## Hypotheses and decision rule (α = 0.05 overall, Bonferroni → 0.025 each, one-sided)
- **H1** (strict set): the number of balancing tablets M exceeds a permutation null in which reverse totals are
  shuffled among candidate tablets (R = 9 999, seed 101). SUPPORTED if p ≤ 0.025; NOT DETECTED otherwise.
  Secondary, no decision weight: the same on the lenient set.
- **H2** (lenient set, tablets using any capacity sign below N01): each of the five sub-N01 ratios is varied alone over
  a pre-declared grid (N01:N39B ∈ {4,5,6,10}; N39B:N24 ∈ {2,3,4}; N24:N30C ∈ {2,3,4,5}; N30C:N30D ∈ {2,3,4};
  N30D:N39C ∈ {2,3}), others at Englund's values. Train = even P-numbers, test = odd P-numbers. Per ratio, on
  the **test** half: CONFIRMED if Englund's value balances strictly more tablets (in system C) than every
  alternative; NOT TESTABLE if tied with the best alternative; CONTRADICTED if an alternative balances more. Train
  argmax and the best joint chains over all 288 combinations are reported, descriptive only.

## Gates (must pass, or H1/H2 are NOT TESTABLE)
- **P0** valuation: replace every strict tablet's total by the greedy notation of its own entry sum; all must balance.
- **FPR**: 200 destroyed-signal datasets (totals shuffled once, seed 102), full test with R = 499; rate of p ≤ 0.025
  must be ≤ 0.05.
- **Power**: 200 datasets with totals shuffled and correct totals planted in 10 % of tablets (seed 103), R = 499;
  detection at p ≤ 0.025 must be ≥ 0.8.
- Disclosed check, no gate: adding one unit of the smallest sign to each balancing total must break the balance.

## Outputs
`analysis/pe001_results.json` (includes the list of balancing tablets and the list of intact strict tablets that
do not balance, with total − sum per system), `analysis/pe001_run.log`.

Tool: [`tools/pe001_totals.py`](../tools/pe001_totals.py). Compute: well under a minute expected.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (computed after the pre-registration commit `d3807ea`)

Tool run once as written (112 s; seeds 101 H1, 102 FPR, 103 power). Outputs: `analysis/pe001_results.json`,
`analysis/pe001_run.log`.

**Descriptive.** 1 585 texts, 11 413 obverse/reverse lines. Numeral tokens: N01 5 988, N14 2 063, N39B 1 301, N30C 674,
N24 593, N34 271, N30D 244, N45 209, N23 89, N08A 73 (unmapped), N51 48, N39C 46, others < 25. Candidates: strict 38,
lenient 65. Rejections (strict): no reverse numeral line 597, < 2 obverse numeral lines 465, damage 274, more than one
reverse numeral line 209, unmapped sign 2.

**Gates.** P0 valuation 38/38 (passes). FPR 0.005 (≤ 0.05, passes). **Power 0.61 (< 0.8, FAILS).** Disclosed check:
adding one smallest unit to each of the 19 balancing totals broke all 19.

**Verdict by the rule: H1 and H2 are NOT TESTABLE** (power gate failed). With 38 tablets, planting correct totals in
10 % (3 tablets) is too few to be caught reliably against a null whose maximum reaches 6.

Numbers below carry **no decision weight** (the gate failed) and are reported so nobody has to re-run to see them:

| | n | Balanced | Null mean | Null max (9 999 shuffles) | p |
|---|---|---|---|---|---|
| H1 strict | 38 | 19 | 0.90 | 6 | 0.0001 (floor) |
| H1 lenient (secondary) | 65 | 30 | 1.06 | — | 0.0001 (floor) |

The 19 balancing strict tablets: 9 close only in system C (Englund's capacity values), 1 only in D, 1 in S or B, 8 in
notations that read the same in S/D/B (4 of them also in C). The observed count is far outside the null, but the gate
was set before the run and it failed; the honest reading is "not testable at the pre-registered power", not "supported".

**H2** (sub-N01 capacity ratios; 16 train / 12 test tablets using sub-N01 capacity signs): only 5 train and 2 test
tablets balance in C at all. N01:N39B = 5 gives 2 test balances against 0 for 4, 6 and 10 (train: all four values tie at
5); the other four ratios tie on both halves (their signs don't separate any balancing tablet). Over all 288 joint
chains the maximum is 7 balancing tablets, reached by Englund's chain and by many others. With two test tablets this is
anecdote, not evidence, and the gate failed anyway.

**Intact strict tablets that do not balance** (19, listed with total − sum per system in the JSON): in 16 of 19 the reverse
total is *smaller* than the obverse sum in every system that covers the signs. The likely cause is structural, not
scribal: obverse lines that carry numerals but are not summed (header quantities, subscripts, notations in a second
system). This is why line 1 (multi-system reverses) and a "which obverse lines enter the total" rule come first. No
tablet is put forward for collation from this run.

## What PE001 settles
- The pipeline (fetch, hashes, parser, factor tables, total-shuffle null) works and is calibrated (FPR 0.005).
- The primary test was under-powered at the pre-registered plant size: **NOT TESTABLE**, published as such.
- Next step (PE002, to pre-register): a power curve (plant fraction 10–50 %) set *before* the test, and a larger
  candidate pool from multi-line reverses (line 1) and from obverse lines filtered by system.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
