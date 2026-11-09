# PE010 · Is the grain reverse a per-line amount? One entry, the largest entry, or the mean entry, on a fresh crate

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration** (this file and `tools/pe010_per_line.py` are published before any match, gate or null
number on these tablets is computed). Open line 9 of the expedition README (PE010 plan in `c8cce53`).

## Why this line
PE008 and PE009 left one shape standing: on grain (CAP) tablets that do not balance, the reverse number is itself grain
(capacity sub-unit signs on 34/40) and much smaller than the obverse sum (median ratio 0.24 on PE006's set, 0.088 on
PE005's). PE009 disclosed an impression it did **not** compute: ratios ≈ 1/n for lists of 7–13 entries. If the reverse
is a **per-line amount** — the mean entry (sum / n), one of the entries, or the largest entry — it would sit exactly
there. PE010 tests that on tablets never used by PE004–PE009.

## Disclosure: what has been looked at
- PE009's A (15) and B (25) are **exposed** (their ratios were printed); they are used here **only descriptively**.
- The fresh crate below excludes every tablet of the PE004/PE005 intact set and of the PE006 fresh set.
- **Multi-line reverses** (set D2) were used by PE002/PE003 for *sums of ≥ 2 entries*; PE002 also reported, pooled over
  all systems, that 78–183 reverse lines equal a single obverse entry (lists continuing onto the reverse). So
  "reverse = one entry" on D2 is **exposed and confounded** and is descriptive only here. "Last reverse line = largest
  entry" and "= mean entry" were never computed on D2 (the largest-entry case is a subset of PE002's pooled count, so it
  is disclosed as *adjacent* to an exposed number).
- Computed before this file (label-free, `analysis/pe010_inventory.json`): set sizes, entries per tablet, eligibility
  (entries/shape only), strata sizes. No total was compared with any entry.

## Data and sets
Pinned CDLI dump `d66b12b` (`pe.atf` sha256 `5c4860ab…159a6`). *Readable* numeral slot = intact, or damaged but
completely read by the editor (PE006 rule). CAP = a capacity sub-unit sign in any readable slot (PE005 definition).
- **D1 (single-total, fresh)**: exactly one reverse numeral slot, readable in C; ≥ 2 obverse slots and ≥ 2 readable C
  entries; damaged-unread entries and broken/primed surfaces **allowed** (the entry list may be partial, so only
  "equals one entry" is testable there). **60 tablets**, 0 complete.
- **D2 (multi-line reverse, fresh for per-line readings)**: ≥ 2 reverse numeral slots, no broken $-line, no primed
  line, every obverse slot readable in C; the candidate is the **last** reverse numeral slot, readable in C. **17 tablets**.
- Why not "grain mismatches": balance cannot be decided on partial lists (D1), and multi-line reverses have no single
  total (D2). The hypotheses are per-line readings, so a balancing tablet simply cannot match; membership uses shape
  and readability only.

## Tests (fixed now; Holm over 3 at 0.05)
| Id | Set | The reverse number equals… | Eligible (inventory) |
|---|---|---|---|
| T1 ENTRY | D1 | the value in C of one of the readable entries | 60 |
| T2 MAX | D2 | the largest entry | 17 |
| T3 MEAN | D2 | the mean entry within one N39C (\|n·total − sum\| < n; exact means included) | 17 |

Exact MEAN (n·total = sum) is eligible on only **7** D2 tablets (< 8): **descriptive only, declared now**. MAX and MEAN
on D1 are not testable (0 complete D1 tablets), declared now.

**Statistic**: matched eligible tablets. **Null (structure-preserving)**: totals permuted **within magnitude strata**
(quartiles of the tablet's largest entry, ties never split; 2 strata for sets < 40 tablets — D1 strata 15/15/18/12,
D2 12/5), so a total only moves to tablets of similar scale. R = 1 999, seed 1001; p = (1 + #null ≥ obs)/(1 + R).

## Gates (per test, after this file is published, before the test)
- **FPR**: 100 stratified-permuted datasets, R = 299; rate of p ≤ 0.05 must be **≤ 0.06** (seed 1002).
- **Power**: 100 planted datasets, each eligible tablet (prob **0.5**) gets total := canonical C notation of its own
  hypothesised quantity (T1 a random entry, T2 the max, T3 floor(sum/n)); R = 299; rate of **p ≤ 0.0167** (0.05/3)
  must be **≥ 0.80** (seed 1003). Plant 0.8 descriptive.
- **Size**: ≥ 8 eligible.

## Decision rule
**NOT TESTABLE** — a gate fails. **NOT DETECTED** — gates pass, Holm p > 0.05. **EXCLUDED** — NOT DETECTED and one-sided
95 % Clopper–Pearson upper bound of matched/eligible < 0.25. **SUPPORTED** — gates pass, Holm p ≤ 0.05.
Descriptive after the test (no decision weight): T1 shifted control (total ± one unit of its smallest sign); ENTRY on
D2 (exposed); exact MEAN on D2; ENTRY / MAX / MEAN on PE009's exposed A and B with the same null.

## Audit of PE009
Re-run `pe009_other_quantity.py test` in a scratch copy with the published gates and compare every field except time;
independently re-count A H4 (count of lines, published 0/15) and the A H1 hit P008825 (ratio 1/30) with literal C and
S tables and plain integer sums.

## Honest limits
- Within-tablet repetition (rations often repeat one amount) is not reproduced by any cross-tablet null; the strata
  only control scale. A T1 hit must also beat the shifted control descriptively before anyone reads it as a convention.
- D2's "last reverse line" may be a continuation of the list rather than a total; D2 is small (17).
- Per-line readings are hypotheses about bookkeeping, not readings of signs; no decipherment is claimed.

Tool: [`tools/pe010_per_line.py`](../tools/pe010_per_line.py) (`inventory`, `gates`, `test`, `audit`).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
