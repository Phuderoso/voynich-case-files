# AMBIGUITIES — choices made where the PREREG223 prose is open

1. **D2 key includes p.** The prose lists (alphabet, form, model, p, j[0..23]); counts are per period, so p is constant inside a count anyway.
2. **D3map residues.** "Residue of each seat" read as (j or plaintext index) mod p per the model, i.e. the res[] that the excess test uses; p included. For model A the residues are the same in every cell, so D3map reduces to the key-value vector there.
3. **D3read (the desk's width × crib family; not in PREREG223).** The key of a residue class is its majority value; a one-against-one ambiguous class is left undetermined. Partial reading: Vigenère P = C − k, Beaufort P = k − C, in the cell's alphabet; '?' where the class is undetermined. Key = (w, alphabet, form, model, p, reading). Another reading of "same reading" (the crib seats only) is D3map, which is also reported.
4. **95th percentile** is descriptive; I used the sorted value at index round(0.95·(M−1)). Kryptos's convention gives 1 lower at p 20 / 21 R. No decision uses it.
5. **counts223.tsv** is not written by `analyze223.py`, so it was checked row by row against my counts, not by hash.
6. **qg.bin** is not in the repo. I took `/workspace/k4_support_backup/qg.bin` (sha256 4a02ba4e…, as declared in PREREG223). It is used only by her `analyze223.py` for the hash check, never by my counter.
7. **p 17–19 run** used `col21.c` unchanged with PLIST 17,18,19 and the same job split as `run223.sh` (plants skipped). It is not pre-registered by Kryptos; it is the I-322 test, gate-checked against summary219.
8. **Case 206 side check** recomputes only j (from π / read / direction) on the published cycle 220 hit lines (w 11, four alphabets). The D2 key uses her alphabet index 0–3, and excess is not re-verified there (the Quagmire alphabets were not re-implemented).
9. **Saturation** is read as "share of nulls with ≥ 1 cell" (an exclusion with K4 = 0 is discriminating only when most nulls are ≥ 1) together with the null tail size. Both are reported.
