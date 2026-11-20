# C119 power preview: decision rule, frozen BEFORE the preview is run (2026-11-19 PT)

The preview has 20 N-LINE nulls per planted text, so the smallest attainable p is 1/21 = 0.048 > 0.05/3. "Reaches p ≤ 0.05/3" is therefore impossible
in the preview, and the operative criterion is **"top of the null"**: planted S above all 20 null S (percentile rank = 1.0).
Percentile rank = (#{null S < planted S} + 0.5·#ties) / 20; p = (1 + #{null S ≥ planted S}) / 21.

1. **KEEP hash plant** if hash q = 0.10 is at the top of its null (rank 1.0).
2. **REPLACE with the state-aligned plant** if hash q = 0.10 is not at the top AND hash q = 0.5 has rank in [0.25, 0.75] (middle of the null).
3. **In-between** (hash q = 0.10 not at the top, hash q = 0.5 outside [0.25, 0.75]): run the aligned preview at q = 0.10.
   - If aligned q = 0.10 is at the top, and hash q = 0.10 is not → REPLACE (the instrument sees state-based order, and the hash plant at 0.10 would make G-POW fail
     for a reason unrelated to the question).
   - Otherwise → KEEP the hash plant, but do NOT commit; report to Kryptos that G-POW is expected to fail (no plant is visible at q = 0.10).
4. Under 2 or 3-REPLACE the aligned preview is run, and under 1 it is run anyway as descriptive information, if cheap. **Nothing is committed** unless rule 1 holds.

— Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026
