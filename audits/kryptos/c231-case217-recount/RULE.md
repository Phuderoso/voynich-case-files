# RULE — blind recount of Kryptos cycle 231 (case 217, I-344 replicate; I-354 relabelling)

Written 2026-11-21 (America/Dawson_Creek, MST) before I ran `bsk230` on any fresh null, before I opened any file under `data/cycle231/R/`, `R_run.log`, `an231.*`, `pool231.*`, `plants231` results, the cycle 231 journal, README/IDEAS of the audited commit, or her check scripts (`an231.py`, `analyze230.py`, `clus230.py`, `pool231.py`).
Audited: kryptos-case-files `36b2871fe2cd6248d056eeb0c8de5da77ab88827` (tree `ac0ccccbae2b415193a0a1f254d41e7e55b103a3`; PREREG231 = `81516e669df0df36aa921d75d34d193e3b936c69`). NOT `a96260d` (no `data/cycle231`).

## Inputs and verification (all before any scan)
- `tools/cycle231/bsk230.c` sha256 `580159e6…`; my build `gcc -O3 -march=native -fopenmp` must give binary sha256 `52c8d591…`.
- `bank.bin` must be `004ffc24…e862`, `all.bin` `8a9e1b32…e857`, `alpha.bin` `2b4ffb69…c84b`, `themed144.bin` `e0c1b627…`, `k4.txt` `2797de14…`, as printed in HASHES231.txt (hash list, read; it carries no results). The big tables are my own copies from my c230 recount (`/workspace/k230-bsk-recount/w`), not hers.
- Fresh nulls: I regenerate seeds 209588+i, i = 0..19 (`random.Random(seed)`, shuffle of the K4 letters) and require byte equality with `data/cycle231/nulls231.txt` (an input).
- Plants: `data/cycle231/plants231.tsv` (her plant list = input, sha `11f93579…`); `plant230.py` needs `k123_eng.txt` which is not in the repo, so I cannot regenerate them: I use her tsv, rebuild each plant's true key independently from ct + (row, dir, X, Y, form) and require consistency with its stated type/size.
- K4 scan: not repeated. I reuse my own published c230 K4 outputs (`/workspace/k230-bsk-recount/out/k4_*.txt`, the same binary 52c8d591 and k4.txt, 0 rederive mismatches there); PREREG231 says she did not re-run K4 either.

## What I run (my own outputs; I do not copy her counts)
Exactly the PREREG231 / `run231.sh` invocations, `maxprint` 100000, `WMAX 10`, `DMAX 6`:
- Fresh nulls i = 0..19: bank `bank.bin themed144.bin 20 i 1 0`, all `all.bin themed144.bin 20 i 1 0` (1/20 scale, ×20); direct for i = 0..7 only: `x alpha.bin 1 0 5 i` (1/5 scale, ×5; X ≡ i mod 5 starting at X = i, so nulls 5, 6, 7 repeat residues 0, 1, 2).
- **My replica (new nulls, "fresh nulls" of the distance rule):** seeds `31231000+i`, same design, same slices. Seeds are mine, chosen before running; they are outside the 209xxx range used by the sister.
- Plants (gate P): `run231.sh` invocations on her tsv.

## Counting (per scope direct / bank / all.bin, per criterion W ≤ 9 and W ≤ 10, D not analysed in c231)
Selected lines = survivor lines with printed `w ≤ W` (W ≤ 10 contains W ≤ 9). Three counts per text:
1. **raw** = number of lines.
2. **cells (house rule, as in c230)** = distinct decrypt profiles over the 97 positions (the set of plaintext letters the covering window of shifts produces from the layer letter at each position).
3. **I-291R (her I-291, my reconstruction)** = single linkage among the selected lines of the same scope/criterion/text; two lines link iff their 24 crib-shift strings agree at ≥ 16 of 24 positions, for k or for the negated key (inverse twins / forms merge). Not from her script (not opened). **Calibrated beforehand on published c230 numbers only**: reproduces K4 direct W ≤ 9 = 2, all W ≤ 9 = 2, direct W ≤ 10 = 22 (the figure in PREREG231), and the c230 null sums (direct W9 2, bank W9 2, bank D6 1, all W9 3), i.e. her published 4 / 4 / 2 / 6 null-equivalents.
Width and pop and the 24 shifts of every line (K4, nulls, replica) are re-derived from (row, dir, X, Y, form) and the tables; every mismatch is listed.

## Null-equivalent and cluster expectation (I-350, my reading)
- **Old claim x20/n:** NE = (sum over nulls of count) × scale / n_nulls, for each of the three counts.
- **Cluster expectation (I-350):** per null text, hit rate = (texts with ≥ 1 selected line)/n with Wilson 95%; expected clusters per text = mean count per text (× scale for the full-scope equivalent) with a bootstrap 95% over texts (20000 resamples, seed 231); clusters per hit text.
- **Pooling:** NE over the 10 old c230 nulls (all three scopes, 1/20 scale; ×20 each) plus the 20 (8 for direct) fresh nulls, plus number of texts with a line; descriptive only.

## Rank rule (PREREG231 decision 2, as I read it)
K4 per-slice mean = K4 full count / scale; n_f = fresh nulls, m_f = nulls with ≥ 1 line; null per-slice max / min over the nulls. Primary precedence: m_f < 3 → INSUFFICIENT-DISCRIMINATION; else K4 mean > max → EXCESS (descriptive, not a lead); else K4 mean in [min, max] → NO-SIGNAL; else BELOW-MIN. I also print the literal order of the text (EXCESS tested first). The label is computed for each of the three counts, on the fresh nulls and on the replica.
Gate P: plants must recover ≥ 19/20 (Wilson printed). Recovery (frozen): strict = a survivor line equal to the plant's (row, dir, X, Y, form) with w ≤ size (type w) or pop ≤ size (type d); loose = a survivor with the same decrypt profile as the true line.

## Distance to the bar (rule agreed 2026-11-21; applied descriptively, retroactively only as relabelling)
These are rank-rule / count verdicts (no p-values in this item, so α/p does not apply).
- **Wilson distance (primary).** Null per-text hit rate h = m/n with Wilson 95% interval [L, U] (z = 1.959964). K4 per-text rate on the same unit: K4's full-scope lines are split into the same slices as the nulls (bank/all.bin: row mod 20, 20 slices; direct: X mod 5, 5 slices); o = occupied slices / slices (floor 0.5/slices when zero). Side: above if o > U (distance o/U); below if o < L (distance L/o); inside otherwise (distance min(U/o, o/L), the second term only when L > 0). Distance ≥ 1 always; 1 = on the bar.
- **Single-text reading (also printed):** K4 as one text, indicator = 1 if it has a line, same formula (slices = 1).
- **Count distance (secondary):** K4 per-slice mean vs null per-slice max: above → mean/max; inside → max/mean (∞ if undefined).
- **Label:** 'robusto' only if Wilson distance ≥ 2 on the fresh nulls AND the same side on my replica (new nulls) AND the rank-rule label is the same on both; otherwise the label gets the suffix `-FRONTEIRA` and I draw no causal reading. Printed for each of raw / house cells / I-291R.

## Comparison (after freezing)
Her `data/cycle231/R/*` vs mine: same sets of `S` lines and same `T` lines (order ignored); then her counts, her NE (bank W≤9 = 2.0 cells = 1 cluster, pooled 10.7 and 3/30), her labels, and her plants.
