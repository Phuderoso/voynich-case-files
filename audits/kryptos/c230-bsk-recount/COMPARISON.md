# COMPARISON (written after freezing; her files opened 2026-11-21 ~09:08 MST)

Opened only after `FROZEN.txt` and `SHA256SUMS` existed: `data/cycle230/R/*` (survivor files), `analyze230.log`, `clus230.log`, `recount230.log` at `a96260d` (`R_run.log` is empty). Not opened: `plants230.tsv`, `decode230.*`, `winctl230.*`, `smoke*`, the cycle 230 journal.

## Survivor lines: exact agreement
`postcompare.py` / `postcompare.out`: my `bsk230` outputs (source sha `580159e6…`, binary `52c8d591…`) vs her `R/`: 33 files (K4 and 10 nulls × direct, bank, all.bin), **33 identical** sets of `S` lines and identical `T` lines. K4 `T` survivors: direct 47, bank 48, all.bin 48 (W ≤ 10 or D ≤ 6). Her extra files in `R/` (`recount_slice_X7623.txt`, `time.txt`) not used. My Python re-derivation of the 24 shifts, width and pop from (row, dir, X, Y, form) found **0 mismatches** over every K4 and null survivor line (her `recount230.log` differences all have width ≥ 14, outside the tool's exact range; none touches W ≤ 10 / D ≤ 6).

## The leaked cell counts are raw lines, not clusters
Her raw per-criterion lines: direct W ≤ 9 **3**, all.bin W ≤ 9 **6**, bank D ≤ 6 **4** (`analyze230.log`), equal to my raw lines. With a cluster rule they are fewer:

| scope / criterion | K4 raw | K4 mine (decrypt profile) | K4 hers (I-291) | null NE mine | null NE hers |
|---|---|---|---|---|---|
| direct W ≤ 9 | 3 | **1** (2 X,Y) | 2 | 4.0 | 4 |
| bank D ≤ 6 | 4 | **1** | 1 | 2.0 | 2 |
| all.bin W ≤ 9 | 6 | **2** | 2 | 6.0 | 6 |
| bank W ≤ 9 | 0 | 0 | 0 | 14.0 | 4 |
| direct D ≤ 6 / all.bin D ≤ 6 | 0 | 0 | 0 | 0 | 0 |

Where the rules differ (and why):
- **direct W ≤ 9, K4:** the three raw lines are (X 7623, Y 60128, forms 0 and 1) and (X 7623, Y 60126, form 2 Beaufort). They have the **identical** decrypt profile (97 of 97 candidate-letter sets), so my rule merges them (Beaufort on Y 60126 = Vigenère on 60128, a reversal twin). Her I-291 rule keeps them as 2 clusters (different Y, different form).
- **bank W ≤ 9, nulls 6 and 9:** raw 4 and 10 lines; mine 2 and 5 cells, hers 1 and 1. The cells are rows of one near-duplicate family (null 9: rows 41118, 61518, 61698, 71778, 81858, all X 118 / Y 36, all ≡ 18 mod 20; null 6: rows 20952 and 21012, ≡ 12 mod 20). Their decrypt profiles agree on 38–77 % of the 97 positions: **not the same decrypt**, so my rule counts them separately, her single-linkage ≥ 16/24 crib-map agreement merges them. This is the only scope where the null-equivalent differs by more than a factor of 2 (14 vs 4); it does not change the K4 side (0).
- **Agreement elsewhere:** the other K4 cells merge the same way in both rules: bank D ≤ 6 (rows 102675 / 102676, X 0, Y 39: dir-0/dir-1 inverse twins × forms 0 / 1 with negated key = 1 test) and all.bin W ≤ 9 (rows 102426 / 102427, X 126, Y 44, and rows 139826 / 139827, X 53, Y 101 = 2 tests).

## The ×20/10 null-equivalent
Her "sum × 20 / 10 per-null-equiv" is exact arithmetic on both raw lines and clusters: each null covers 1/20 of the scope, so a full-scope equivalent per null is 20 × its count, and over 10 nulls `sum × 20 / 10`. Recomputed from my own null runs: raw 8.0 / 28.0 / 4.0 / 12.0 (direct W9, bank W9, bank D6, all W9) = hers; cells 4.0 / 14.0 / 2.0 / 6.0 under my rule (hers 4 / 4 / 2 / 6 clusters). Caveats I would print beside it:
- It is an expectation scaling, not an observation: in direct W ≤ 9 only 2 of 10 nulls have any line (≈ 1 cell each), in bank W ≤ 9 2 of 10 (2 and 5 cells), bank D ≤ 6 1 of 10, all.bin W ≤ 9 3 of 10; the median null has 0.
- The slices are residue classes: direct uses X ≡ i (mod 20) for i = 0…9 (the first ten residues), and bank / all.bin use rows ≡ 2i (mod 20), i.e. **only even residues** (0, 2, …, 18). The near-duplicate families above have members ≡ the same residue mod 20, so a family sits wholly inside one slice: the ×20 scaling is unbiased for raw lines and for family counts, but with high variance (one null can hold a whole family: 5 cells in null 9).
- K4's counts are full-scope observed counts, so K4 vs null-equivalent compares an observation to a scaled expectation.

I assign no label here; the counts only.
