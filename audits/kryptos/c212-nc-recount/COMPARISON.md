# COMPARISON with Kryptos case 212 (kryptos-case-files @ 137ef5f, cycle 226) — written AFTER FROZEN.txt

Opened only after freezing (FROZEN.txt, 2026-11-20 16:08 MST): `case-file/212-decrypt-bar-calibration-audit.md`,
`data/cycle226/posthoc209.json` (per-null maxima). Fresh clone in `kryptos-main/`; her `analyze223.py` decrypt() read afterwards.

| quantity | frozen (my RULE.md) | hers (c226 / case 212) | match |
|---|---|---|---|
| K4 passes NC >= -6.0 (known >= 49, nq >= 10) | 0 | 0 | yes |
| nulls with a pass | 0 / 168 | 0 / 168 | yes |
| K4 D2 cells p20+p21 | 101 (2 + 99) | 101 (2 + 99) | yes |
| K4 best NC p 21 / p 20 | -7.357 / -8.038 | -7.36 / -8.10 | p 21 yes; p 20 differs by 0.06 |
| null max NC | **-6.431** | **-6.68** (median of maxima -7.38) | **no (0.25 apart)**, both far below -6.0 |

## Discrepancy, explained (post hoc, labelled; the frozen numbers above are NOT changed)
Only difference: tie handling in a residue class with two crib seats that disagree (1 vs 1).
- My RULE.md leaves such a class undetermined ('?'), like my case 209 D3read.
- Her `analyze223.py` decrypt() uses `Counter.most_common(1)`, which on a tie takes the first-voted value in crib order,
  so the class is decrypted with one of the two values.
Re-run with her tie rule (`diag_postcompare.py`, everything else equal, any-hit maximum per text): K4 p21 -7.362, K4 p20 -8.104,
null max **-6.682** (null209379), median of maxima -7.384, and **all 168 per-null maxima equal hers** (|diff| < 0.0015); passes 0; 0/168.
So with her tie rule I reproduce her numbers exactly; with the stricter '?' rule the null max is higher (-6.43) because a '?' drops the
quadgrams around that class and can raise the mean of what is left. Both conventions give K4 0 and nulls 0/168; the conclusion does not depend on it.
Note for the house definition: "known" and NC should say how a tied class is read (her tool: first-voted value; mine: '?').

## Verdict
Independent recount **agrees** on K4 0 and nulls 0/168, K4 best -7.36 (p 21), and (with her tie rule) null max -6.68.
