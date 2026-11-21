# COMPARISON (written after freezing; her files opened 2026-11-21 14:37 MST, after `FROZEN.txt` and `SHA256SUMS`)

Opened only after the freeze: `data/cycle231/R/*`, `SHA256SUMS_R.txt` (check), `an231.log`, `pool231.log`, `journal/2026-11-21-cycle231.md`, `case-file/217-…md` at `36b2871`. `postcompare.py` / `postcompare.out` do the mechanical part.

## Survivor lines: exact agreement
- **48 of 48** null survivor files (20 bank, 20 all.bin, 8 direct; seeds 209588–209607) are identical to mine (sets of `S` lines and `T` lines). `SHA256SUMS_R.txt` verifies **49/49**. My `bsk230` source `580159e6…`, binary `52c8d591…` (built with `gcc -O3 -march=native -fopenmp`); `bank.bin` `004ffc24…e862`, `all.bin`, `alpha.bin`, `themed144.bin`, `k4.txt` and `nulls231.txt` all equal `HASHES231.txt`. My regenerated nulls are byte-identical to her `nulls231.txt`.
- My independent re-derivation of the 24 shifts, width and pop: 0 mismatches on K4 and on all 96 null / replica files (48 + 48) except **one** line (fresh null 6, all.bin, row 26206, form 1): tool prints `w=26` but the circular arc is 19 (width > 13 is outside the tool's exact range, I-346; the line is a D ≤ 6 line, outside W ≤ 10).
- **Plants (gate P):** her 20 plants (`plants231.tsv`, hash `11f93579…`; I could not regenerate them because `plant230.py` needs an unpublished `k123_eng.txt`): my own `bsk230` runs give the same survivor counts per plant as her `an231.log` (1122, 3, 2, 2, 642, 1, 81, 10, 25, 3, 8, 4, 22, 8, 4, 4, 24, 2, 12, 4) and **recover 20/20** (Wilson 0.839–1.000), strict and loose; I rebuilt every plant's true key from ct and it satisfies its stated type and size.

## Counts (her claims vs my recount)
| claim | mine | |
|---|---|---|
| W ≤ 9 fresh nulls with a line: direct 0/8, bank 1/20, all.bin 2/20 | 0/8, 1/20, 2/20 | agree |
| bank W ≤ 9 null-equivalent 2.0 cells (1 cluster) | raw lines 2.0, house cells 1.0, I-291R clusters 1.0 | agree ("cells" there = raw lines) |
| pooled with the 10 old nulls: 10.7 cells, 3/30 texts | bank W ≤ 9 raw 10.67, house cells 5.33, I-291R 2.00; 3/30 | agree (10.7 = raw lines, 2.0 = clusters) |
| per-null raw / clusters, all six scope × W columns (`an231.log`) | raw lists identical in all 6; her clusters = my I-291R reconstruction in **6 of 6** | agree; my house rule differs only in bank W ≤ 10 (26 vs 21) |
| K4 raw (clusters): direct 3 (2) / 47 (22), bank 0 / 44 (8), all 6 (2) / 48 (20) | same raw; house cells 1 / 19, 0 / 15, 2 / 20 | agree (K4 files unchanged from c230) |
| W ≤ 10 NO-SIGNAL in all three scopes | rank rule: NO-SIGNAL in all three, on fresh nulls and on my replica | agree on the rank rule; see distance column (FRONTEIRA) |
| W ≤ 9 INSUFFICIENT-DISCRIMINATION | same on fresh; on my replica direct and bank also INSUFFICIENT; all.bin W ≤ 9 replica has 3/20 hits (NO-SIGNAL) | agree on her data; all.bin flips at the m_f = 3 threshold on mine |
| pooled direct 4.4 (2.2), 16.7 (7.5); bank W10 52 (24); all 6.0 (3.3), 44 (29.3) | identical | agree |

## What differs or needs a caveat (not disagreement with her numbers)
1. **Precedence of the rank rule.** Read literally, rule 2 tests K4 > max first. Direct W ≤ 9 has K4 per-slice 0.6 > null max 0, so the literal order would say EXCESS (the label printed under "literal-order" in `summary231.txt`); she (and my primary precedence) test m_f < 3 first, so INSUFFICIENT. Worth writing into PREREG232.
2. **Replica.** With 20 new nulls of my own (seeds 31231000+i), the W ≤ 10 verdict is the same (NO-SIGNAL), but the null band is wide and heavy-tailed: direct W ≤ 10 replica null-equivalent is 46 raw / 24 clusters (fresh: 10 / 4.4), and bank W ≤ 10 replica 66 raw / 33 clusters (fresh 44 / 21). At W ≤ 9 the replica direct nulls fire in 2/8 (fresh 0/8), all.bin in 3/20 (fresh 2/20). So the m_f < 3 threshold is not stable across replicas.
3. **The 28 vs 2.0 for bank W ≤ 9 is stable:** replica bank W ≤ 9 is also 1/20 texts, 2.0 raw / 1.0 cell / 1.0 cluster.

## Distance to the bar (rule frozen before opening outputs; descriptive relabelling only)
Hit rate of nulls with Wilson 95% vs K4's slice-occupancy rate (RULE.md). Counts are the I-291R clusters' rank labels; raw and house cells give the same labels. See `res/summary231.txt` for every number.
| scope, W | rank label (fresh / replica) | Wilson side, distance (fresh / replica) | count distance, I-291R (fresh / replica) | label (frozen rule: Wilson primary) |
|---|---|---|---|---|
| direct ≤ 9 | INSUFFICIENT / INSUFFICIENT | inside 1.62× / inside 2.80× | ∞ (null max 0) / 5.0× | INSUFFICIENT-DISCRIMINATION-FRONTEIRA |
| direct ≤ 10 | NO-SIGNAL / NO-SIGNAL | above 1.15× / above 1.02× | 1.14× / 4.55× | NO-SIGNAL-FRONTEIRA |
| bank ≤ 9 | INSUFFICIENT / INSUFFICIENT | "below" 0.36× / 0.36× (floor artefact: K4 has 0 hits, but the floor 0.5/20 = 0.025 exceeds the null lower bound 0.009, so K4 is effectively on the bar) | ∞ / ∞ | INSUFFICIENT-DISCRIMINATION-FRONTEIRA |
| bank ≤ 10 | NO-SIGNAL / NO-SIGNAL | inside 1.01× / above 1.04× | 7.5× / 15× | NO-SIGNAL-FRONTEIRA |
| all ≤ 9 | INSUFFICIENT / NO-SIGNAL | inside 3.01× / inside 1.91× | 10× / 20× | INSUFFICIENT-DISCRIMINATION-FRONTEIRA (labels differ across replicas) |
| all ≤ 10 | NO-SIGNAL / NO-SIGNAL | above 1.13× / above 1.09× | 4.0× / 4.0× | NO-SIGNAL-FRONTEIRA |
No cell reaches 'robusto' under the frozen rule (Wilson distance ≥ 2× with the same side and the same label on the replica): all six are **FRONTEIRA**, so no causal reading. Caveat: the secondary count distance would call bank ≤ 10 (7.5× / 15×) and all ≤ 10 (4× / 4×) 'robusto' NO-SIGNAL, and direct ≤ 10 not (1.14×); the two distance readings disagree because the null hit rate at W ≤ 10 is high (65–80%) while K4 occupies nearly all slices. I report both and keep the frozen one as the label. The K4 hit rate in the W ≤ 10 scopes sits at or just above the upper Wilson bound of the null hit rate (K4 occupies 17–20 of 20 residue slices at W ≤ 10; null texts hit 65–80%), i.e. K4 is not distinguishable from the null there but also not clearly inside; the count-based rank rule (her primary) says inside. Retroactively relabelling case 216: bank W ≤ 9 EXACT-EXCL on the fresh data has a null per-text hit rate of 5% (1/20, Wilson 0.9–23.6%) against K4's 0: the zero is not distinguishable from the null (distance < 1×), so FRONTEIRA / 'not discriminating at this null count', consistent with her own retraction of "discriminating".
