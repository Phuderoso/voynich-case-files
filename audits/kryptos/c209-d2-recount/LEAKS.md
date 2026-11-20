# LEAKS — what I saw before freezing (04:44:52 PT)

Disclosed in full. The counter recomputes every hit line from the raw col21 output and was compared on 169 texts × 6 numbers. The leaked items cover only the K4 row and aggregates, so they could not steer the per-text agreement, but they were seen.

1. **The brief / Kryptos's message:** K4 D2 99, null median 114, p 0.63, raw rank p 0.041, and "width-10 families with reorderable columns give 1,800 of 1,928 cells".
2. **`counts223.tsv`** header + K4 row (`head -3` while checking the input format): K4 p20 R 3 / D2 2 / D3 2, p21 1,928 / 99 / 99.
3. **`results_K4.txt`** header (`head -12`, looking for the results-file format): the same K4 R / D2 / D3 line.
4. **`IDEAS.md`** (a grep for I-318 / I-320 / I-322 that was too broad): her summary line shows 6/168 nulls ≥ K4 on R, 105/168 on D2, CP95 0.013–0.076, "all p 21 cells are model B with one two-member dissenting class", the best decrypt −6.48, and "nine COL / σ⁻¹" families.
5. **Tools opened:** `PREREG223.md` (the intended source), `run223.sh`, `col21.c` (hit-line format and transposition), `tools/cycle220/col1e4.c` (for the case 206 side check). In `analyze223.py` I saw only the lines matching `results_` / `def` / `argv` (function names and argument order), not the counting logic. `mult223.py` was not opened.
6. **Published case 205 / 206 data** (summary219.json counts and hit-line heads; cycle 220 results files) were read. They are the gate references, not case 209 results.

**After freezing:** her `analyze223.py` was run (it printed gates, labels and the K4 decrypt list), and case file 209 lines 25–64 were read for the comparison.
