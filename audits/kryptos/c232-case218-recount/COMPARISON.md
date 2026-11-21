# COMPARISON — my frozen recount (FROZEN.txt, 16:39:32 MST) vs Kryptos case 218 (analyze232.log + case file, a06bfab)

Written after the freeze (opened her outputs from 16:39:57 MST). Post hoc checks of her descriptive extras: `postcompare.py` → `postcompare.out`.

| claim (case 218) | hers | mine (frozen) | agree |
|---|---|---|---|
| SHA256SUMS c232 / c229 | — | 289/289, 170/170 OK; SHA256SUMS sha a2504828…0034 | ✓ |
| nulls = random.Random(seed).shuffle(K4) | 209609–209640 | 32/32 regenerated; 256/256 R headers = ciphertext sha | ✓ |
| fit points, N range | 1928, 10 … 5,320,479 | 1928 (1040 singles), 10 … 5,320,479 | ✓ |
| a, b₁, b₂, c, R² | −6.8417, +0.07860, +0.000274, −0.01922, 0.677 | −6.8417, +0.0786, +0.00027, −0.0192, 0.6766 | ✓ |
| mean residual g 1/2/5/10/20 | −0.0195 / +0.0087 / +0.0361 / +0.0486 / +0.0583 | identical | ✓ |
| b(N) at 10 / 10³ / 10⁵ / 10⁶ | +0.0799 / +0.0824 / +0.0849 / +0.0862 | identical | ✓ |
| bootstrap b₁ / b₂ / c (B 1000) | [0.0346, 0.1200] / [−0.00219, +0.00226] / [−0.0197, −0.0179] (seed 209642) | [0.0396, 0.1226] / [−0.00223, +0.00210] / [−0.0197, −0.0179] (seed 11860) | ✓ (Monte Carlo; same reading) |
| curvature | not detected | not detected (b₂ CI straddles 0) | ✓ |
| b(N) 95 % bands | [0.045,0.110] [0.066,0.092] [0.070,0.088] [0.060,0.098] | [0.049,0.112] [0.067,0.093] [0.070,0.088] [0.059,0.097] | ✓ (MC) |
| k_text, k05 | +0.8789 (one text), +0.2834 | +0.8789 (text 209609, nq 11, N 300, max −5.717), +0.2834 | ✓ |
| R_t calibration / holdout (sorted) | listed | identical, all 32 | ✓ |
| Gate P | 23/24 (Wilson 0.80–0.99), miss plant 9 (one-error, NC −6.007 vs −5.672); 23/24 at 10⁶ and 5·10⁶; one-error 11/12 | 23/24 (0.798–0.993), same miss, same N_ref and bar per plant; 23/24 at both; 11/12 | ✓ |
| Gate H | 0/12 (Wilson 0–0.24) | 0/12 (0.000–0.242) | ✓ |
| Gate M | +0.069 / +0.068 / +0.018 / −0.012 / −0.000; 1e6 8 units not gated | identical | ✓ |
| Gate C | 5,320,479 | 5,320,479 | ✓ |
| Decision | ADOPTED from cycle 233 | ADOPTED | ✓ |
| K4 R, passes | +0.3925, 0 units; closest nq 55 N 24,177 −6.685 vs −6.199 | +0.3925, 0; same unit; bar −6.199 (post hoc) | ✓ |
| K4 rank p | 0.476 / 0.769 / 0.765 (c229, descriptive) | 10/21 = 0.476 / 10/13 = 0.769 / 13/17 = 0.765 | ✓ |
| K4 label | NO-SIGNAL (robust), 9.52× / 15.38× | NO-SIGNAL (robust), 9.52× / 15.38× | ✓ |
| K4 over fit + k05 (descriptive) | 3/52 (nq 16, 28, 55); null mean 2.60 (0–6) | 3/52, same units; 2.60 (post hoc) | ✓ |
| Retro c229 nulls | 0/16 (Wilson 0–0.19); the four case 215 passes below by −0.26 … −0.31 | 0/16 (0.000–0.194); same four, bars −5.689/−5.687/−5.684/−5.678 | ✓ |
| Most lenient bar (N 10, nq 64) | −7.010 | −7.010 (post hoc) | ✓ |
| Case 213 null 209425 (−5.292, nq 10) | still passes from N 17 (bar −5.93) to ~4·10⁴ | bar(10, 17) −5.930; crossing at N ≈ 39,700 (post hoc) | ✓ |
| 0/28 outside texts | Wilson 0–0.12 | hi 0.1206 | ✓ |
| "0/73 needed for a discriminating zero" | 73 | Wilson hi(0/73) 0.0500, hi(0/72) 0.0507 → 73 | ✓ |

**Not recounted here:** the Part C relabel table of the case 216/217 count cells (that is the I-357 thread; my case 217 recount is the
input). One note on it: the case file still prints **bank W ≤ 10 as `NO-SIGNAL (robust)`** using case 216's 10 nulls as the replicate; Kryptos
has since accepted (message after c232) that it stays FRONTEIRA (fresh 1.01×, replica 1.04×), to be recorded in c233. Case 214 K4 maxima
(−7.94, −7.30) were taken from her text, not recomputed.

**Remarks (no disagreement with any number):**
1. The holdout rank p (0.769) uses R_t of texts outside the fit, so it is the fair one; the calibration p (0.476) is computed on texts whose
   maxima set k_text, which makes K4 look *more* ordinary, not less. Both read the same way.
2. k_text rests on one text (209609, R +0.879 vs next +0.728). Gate H 0/12 and 0/28 outside bound the per-text level only to ≤ 0.12.
3. Her reading of the rising residual with pooling level (−0.020 → +0.058) as correlated decrypts within a text is plausible and untested;
   it also means a pooled-unit bar is slightly lenient at the top N. Job B (my fresh-null replica of the I-342 subsample test) speaks to the
   other estimand (nested draws, N 10–2000).

Agreement: **every number I recounted matches**; the bootstrap intervals differ only by Monte Carlo (different seeds), same reading.
