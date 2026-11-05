# K015 · A close-match detector: sorted 3-cord windows, checked against Urton & Chu's published pairs

## Pre-registration (written 2026-11-05 05:50 PT, before any K015 code was run and before looking at the cords of the control pairs)
- **Question (README line 3, opened by the K014 audit).** Urton & Chu (2015) report Inkawasi khipus that "closely
  match": the same values, but triplets reordered (x / 15 / y in one, x / y / 15 in the other). Exact-block tools
  can't see these. Can a detector that tolerates local reordering find them while staying calibrated?
- **Data.** As K009–K014: OKR `khipu.db` @ `4039ca5`, duplicate-flagged khipus removed, R5 masked to 0, khipus with
  at least 10 non-zero pendants (N = 433, m = 93 528). Raw (not run-collapsed) pendant sequences.
- **Symbols.** For each position i, the window (s_i, s_{i+1}, s_{i+2}) is turned into its **sorted** triple if all
  three are non-zero, otherwise into a blank (0). Two khipus agree at aligned windows when their sorted triples are
  equal, so a swap of two neighbouring cords leaves most windows unchanged.
- **Statistic.** The longest aligned run of equal non-blank window symbols per pair, found from shared 3-window
  seeds (pairs without a seed get p = 1). Same Poisson longest-match formula as K011–K014 on the window symbols,
  then BH at FDR 0.05 over all m pairs. Windows overlap, so the formula is **not assumed** valid: it is calibrated
  empirically.
- **Null and calibration rule (unchanged).** 40 run-preserving null corpora (seed 20151105). Acceptable only if at
  most 6 of 40 give any BH discovery and the pooled share of null pairs with p < 0.01 is at most 0.02. Failing
  either means the detector is **excluded as a tool**.
- **Power.** 100 plants each: a copy of 10 cords, and a copy of 16 cords, with neighbouring cords swapped at random
  (each non-overlapping adjacent pair swapped with probability 0.3), planted in a fresh null corpus. Power is the
  share of planted pairs found.
- **Positive controls (published, not used to tune anything).** KH0503 UR267A · KH0491 UR255 and KH0504 UR267B ·
  KH0492 UR256. I report each control's p-value and whether it is a BH discovery. If neither is found, the detector is
  **not shown to see the published kind of close match**, whatever its planted power.
- **Reading.** If calibrated, every real discovery is listed and marked known (K010–K014 or literature) or new.
- **Budget.** One run, `timeout 600`. Any amendment is disclosed below.

## Results (one run, 21.0 s; `analysis/k015_results.json`)
**Amendments, disclosed:** (1) after the run I fixed the tool's docstring, which still named K014; the code itself
did not change. (2) After the verdict I ran a **post-hoc descriptive look** at the control pairs' cords. It is
not a test, and it is reported only to explain why they were missed.

| Check | Rule | Result | Verdict |
|---|---|---|---|
| Null corpora with any BH discovery | ≤ 6 of 40 | **40 of 40** | **fail** |
| Pooled share of null pairs with p < 0.01 | ≤ 0.02 | 0.011 | pass |
| Power, swapped 10-cord plants | descriptive | 0.40 | uninterpretable |
| Power, swapped 16-cord plants | descriptive | 0.60 | uninterpretable |
| Control UR267A · UR255 | descriptive | no shared sorted window (p = 1) | not found |
| Control UR267B · UR256 | descriptive | no shared sorted window (p = 1) | not found |

**Verdict: the sorted-window detector is EXCLUDED as a tool.** Overlapping windows break the independence the
Poisson formula assumes, as runs did in K011, and every null corpus produced false discoveries. Its 227 "discoveries"
on the real data are therefore **not reported as findings**. It also misses both published controls.

## Why the controls are invisible (post-hoc look, not a test)
In OKR, the first cords of UR267A read 106, 15, 91, 112, 15, 0, 161, 15, 140, … and those of UR255 read
106, 0, 15, 0, 100, 0, 15, 0, 160, 0, 15, … Where UR267A has a value, UR255 often has an empty (zero) cord in
between. So no three neighbouring non-zero cords line up, and no window-based or exact-block tool can see the match.
What lines up is the **order of the non-zero values with gaps**: 106, 15, …, 160, 15, …, 206, 15, 238, 15, 85, …
appear in the same order in both. UR267B/UR256 look similar (1054/1055, 10, 63, 138, …, 1411, 10, …, 543, …).
The published close matches look like a **gapped, ordered** relationship, closer to a longest common subsequence (LCS)
than to a local reordering.

**Next line (to be pre-registered separately):** an LCS-type score on the non-zero value sequences, with an empirical
per-pair or max-statistic null (no Poisson formula). The two published pairs are the positive controls and must be
found before anything else is read.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
