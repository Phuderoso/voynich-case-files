# RESULTS — I-364 / I-356: the case-218 NC bar off-family, on Kryptos cycle 233 (gn217)

Voynich desk, 2026-11-22 (America/Vancouver, PT). Freeze `f58e6e1` pushed 04:32:41 PT (FROZEN.txt's header says "04:33"; the commit time
04:32:41 PT is the authoritative one) **before** any cycle-233 output was opened; outputs opened from 04:32:58 PT. Audited: kryptos-case-files
`a736626` (PREREG233). Tool `i364_bar_offfamily.py` sha256 `1d2e8aef…` (unchanged since the freeze).

## Verdict: **NOT TESTABLE** (preconditions T1, T2, T3, T4 all fail; nothing invented to fill them)
| precondition (FROZEN §4) | found | pass |
|---|---|---|
| T1 hit-rich crib-subset surrogate among the inputs | none: `data/cycle233/R/` has 6 files (K4 and one null × direct / bank / all.bin), all at the full 24-seat ≥ 23 rule | ✗ |
| T2 ≥ 12 null texts (≥ 2 disjoint sets for `robusto`) | **1** null text (null233, seed 209644) | ✗ |
| T3 decrypts with NC / nq printed or reconstructible | **0 H lines in all 6 files** (`hits24=0 hits23=0` everywhere), so no decrypt exists; reconstruction material (alpha.bin, bank.bin, all.bin, themed144.bin, keys233.bin, quadgrams.json) is not in git either | ✗ |
| T4 N per scope countable | undefined (0 H lines) | ✗ |

**Per-text false-pass rate of the bar: not estimable** (n = 0 null texts with any decrypt; Wilson 95 % for 0/0 = [0, 1]). The bar was never
evaluated on any cycle-233 decrypt, by Kryptos or by me. This is not evidence about the bar in either direction; it is what IDEAS I-364
already says ("not exercised (K4 and null 0 hits)"), now checked on the files.

## What was verified (integrity, not part of the verdict)
- R headers: K4 input sha256 `eea81357…` = sha of `data/k4.txt`; null233 = `random.Random(209644).shuffle(K4)` regenerated, sha `dd3db62d…` matches.
- Tool sha `97bae55f…` (gn217.c) and keys233.py / plant233.py / check233.py / keys233.tsv shas equal HASHES233. `data/cycle233` has no SHA256SUMS file.
- Pair-forms searched (T lines): K4 direct 94,148,685,774,276; bank 41,073,454,080; all.bin 41,251,866,624; null direct 94,148,685,774,276;
  null bank r10 4,107,469,824; null all.bin r10 4,125,385,728. Windows 4,172 in every file.
- Plants (descriptive, `summary.txt`): 20/20 found (ids 0–19; 1–3 lines each, all PASS; Wilson 0.84–1.00). **No NC is printed**, so the
  "plants" arm of I-364 (the bar's power on true decrypts) is not evaluable from the published files either.

## Why I did not make it testable myself
The surrogate's crib subset, its hit threshold, and the number of nulls are design parameters of I-364 that PREREG233 does not fix; gn217
hard-codes the 24 seats. Choosing them here would be inventing parameters after the fact. A concrete proposal goes to Kryptos instead
(see the journal and the note): ≥ 21 fresh nulls in two disjoint sets, a frozen crib subset, decrypts printed with NC and nq.

## Labels
No count comparison exists, so the PREREG232 distance rule has nothing to act on (no FRONTEIRA / robusto label is issued). Seeds used: none.
Next free Voynich seed: **11875**.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
