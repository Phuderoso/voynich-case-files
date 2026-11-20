# RESULT — independent D2 / D3 recount of Kryptos case 209 (cycle 223)

Voynich desk, 2026-11-20 (America/Vancouver). Repo: Phuderoso/kryptos-case-files @ `b304de5` (PREREG223 `193b4fe`, case 209 `b304de5`), fresh clone.

## 1. Inputs regenerated, hashes verified
- `tools/cycle223/run223.sh` re-run in a fresh work dir (gcc 14.2, 8 cores, ≈ 7.5 min wall; the box was shared with other jobs): 189 job dirs (K4 + 168 nulls + 20 plants), every `.raw` ends with its `C` line.
- `texts.tsv` regenerated = committed `data/cycle223/texts.tsv` byte for byte.
- `analyze223.py` (her tool, run **after** my counts were frozen) regenerated the 169 `results_*.txt` + `summary223.json`: **170 / 170 match `SHA256SUMS_all_results.txt`**, and `summary223.json` is byte-identical to the committed one. **No mismatch.** (qg.bin taken from the support backup, sha256 `4a02ba4e…` as declared in PREREG223.) `counts223.tsv` is not written by `analyze223.py`, so it was compared row by row (below), not by hash.

## 2. D2 — my own counter, frozen before comparison
`recount209.py` reads the raw col21 hit lines, **recomputes j[0..23] from π / read / direction, the key values and the excess ≤ 1 test for every line** (all lines re-verified, 0 failures), then counts per PREREG223: R, D2 = distinct (alphabet, form, model, p, j[0..23]), D3map = distinct crib maps, D3read (see 4). Ranks by the PREREG223 rule, M = 168. Frozen at 04:44:52 PT (`FROZEN.txt`).

| statistic | K4 | null median | null 95th* | null max | nulls ≥ K4 | p_up |
|---|---|---|---|---|---|---|
| p 21 R | 1,928 | 911 | 1,710 | 2,849 | 6 | **0.0414** |
| p 21 D2 | **99** | **114** | 235 | 375 | 105 | **0.6272** |
| p 20 R | 3 | 14 | 102 | 286 | 138 (≤: 36, p_low 0.219) | 0.8225 |
| p 20 D2 | 2 | 4 | 13 | 31 | 135 | 0.8047 |

**Agreement: full.** Her stated K4 99 vs null median 114, p 0.63, raw rank p 0.041 are reproduced, and **all 169 texts × 6 numbers (p20/p21 × R/D2/D3) equal `counts223.tsv`: 0 divergences.** Label `STRUCTURAL MULTIPLICITY` follows from the pre-registered rule. *Only difference: the descriptive 95th percentile (mine 1,710 / 102, hers 1,709 / 101) — percentile convention, no decision depends on it.

## 3. Gate-T-style check at p 17–19 (for I-322)
col21 re-run with periods 17,18,19 on K4 + 168 nulls (w 9 + 10, all orders). K4 and the 8 cycle-219 nulls reproduce `data/cycle219/summary219.json` one-error counts exactly (K4 p17 0, p18 2, p19 14).

## 4. The unit question (I-322): D2 vs a coarser D3
Two coarser candidates were tested:
- **D3map** (PREREG223's D3, distinct crib maps: alphabet, form, model, residue + key value of each seat).
- **D3read** (the desk's "width × crib family": column orders whose crib-derived key gives the same 97-letter partial reading, '?' where undetermined, are one).

| | p 17 | p 18 | p 19 | p 20 | p 21 |
|---|---|---|---|---|---|
| K4 R / D2 / D3map / D3read | 0/0/0/0 | 2/1/1/2 | 14/7/7/14 | 3/2/2/3 | 1,928/99/99/1,928 |
| null median R / D2 | 0 / 0 | 1 / 1 | 3 / 1 | 14 / 4 | 911 / 114 |
| null max R / D2 | 26 / 13 | 30 / 13 | 432 / 65 | 286 / 31 | 2,849 / 375 |
| p_up R | 1.00 | 0.40 | 0.24 | 0.82 | 0.041 |
| p_up D2 (= D3map) | 1.00 | 0.54 | 0.14 | 0.80 | 0.63 |
| nulls with ≥ 1 cell | 45/168 | 91/168 | 101/168 | — | 168/168 |

- **D3map = D2** in 168 / 169 texts at every period (one null differs at p 18). Crib maps add nothing: rank p at p 21 is the same 0.6272.
- **D3read collapses nothing**: it equals R in every text at p 17, 18, 20, and in all but 6 (p 21) and 10 (p 19) texts. Reordering the free columns (the 6! = 720 families) leaves the crib seats in place but moves the non-crib letters, so every order gives a different reading. p 21: K4 1,928, null median 911, p_up 0.0414 (same as R).
- **Saturation is not removed by any collapse.** A text has 0 cells under R if and only if it has 0 under D2 / D3, so the share of nulls with ≥ 1 cell (27 % at p 17, 54 % at p 18, 60 % at p 19 for w 9–10) is identical under every unit; the exclusion question ("K4 has 0, do the nulls?") cannot be rescued by collapsing. What D2 does is compress the tails (p 19 null max 432 → 65, 95th 72 → 10), which matters for excess claims.
- Case 206 side check (published cycle 220 w 11 hit lines, `c206_d2.py`): K4 0 cells; the nulls go R → D2 as 69 → 45 (209249), 24 → 24, 15 → 11, 12 → 6, 4 → 4, 2 → 2, 2 → 1, 1 → 1. The w 11 "saturated" nulls are mostly distinct crib tests, not duplicates; the desk's "~8 families" in 209249 (386e342) were near-duplicate families, not identical placements.

**Recommendation (numbers-based): keep D2 as the collapsed unit.** D3map is numerically identical to D2 (168 / 169 texts, all periods) but needs residue / key bookkeeping; D3read is no coarser than R. For I-322 the answer is no: no collapse changes the zero / non-zero pattern that limits the exclusions at p 17–19; report it as a null-occupancy rate (nulls with ≥ 1 cell) next to the D2 rank, and use D2 for excess claims.

Not a decipherment; no K4 cell at p 17–21 is claimed as a candidate here.
