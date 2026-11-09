# PE015 · Header structure, step 3: does a finer header key predict the number system and the size of the entries?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration** (this file, `tools/pe015_finekey.py`, the label-free `analysis/pe015_inventory.json` and
the rehearsal on destroyed/planted data `analysis/pe015_rehearsal.json` + `pe015_rehearsal_run.log` are pushed before
any observed fine-key–label association is computed). Open line **5b** of the expedition README.

## Not blind — disclosed first
PE012 (`9be8bf6`) published its descriptive tables of the **coarse** header key (first sign, variant dropped) against
SYSTEM and SIZE: e.g. M157 C 94 / I 28 / MIX 7, M327 C 14 / I 10 / MIX 2, M157 sizes 0/1/2/3 = 18/110/97/19, M327
4/24/22/17. I have seen them. They were read *before* this design, and the idea of a finer key came from them. So
PE015 is **not a blind test** of the header line. Two guards:
1. The **W tests** permute the fine key only *inside* its coarse key, so the coarse association I saw is held fixed by
   the null; they ask only what the fine key adds (e.g. M157 vs M157~a, |M327+M342| vs |M327+X| vs M327).
2. Nothing about the fine-key × label cross-table was computed before this push (inventory = marginals only).
How the M157 / M157~a split falls against the labels was never tabulated anywhere (PE012 merged them).

## Data
CDLI `d66b12b` as pinned in `data/MANIFEST.md`; `data/pe.atf` sha256 `5c4860ab…159a6` re-checked this cycle (identical).

## Definitions (fixed before looking)
- **Header line** exactly as PE012: obverse `1.` followed by the editors' `# header`, no numeral.
- **Fine key**: the header text before the first comma; damage marks `# ? ! *` removed; a header with a restored or
  unread token (`[`, `]`, `x`, `X`, `...`) gets **no** key; complex graphemes kept whole (|M327+X| as written);
  **variant suffixes kept** (M157~a ≠ M157); several tokens joined by a space.
- **Coarse key**: PE012's key (first sign, `|A+B|` → A, `~x` dropped).
- **Entries, SYSTEM (C / I / MIX), SIZE (0 fractions / 1 N01 / 2 N14 / 3 higher), statistics** (G for SYSTEM,
  between-key SS for SIZE) and **strata** (H1: entries 1 / 2–3 / 4–7 / ≥ 8; H2: that × SYSTEM): **identical to PE012**.
- **Sets**: fine keys on ≥ 3 tablets of the labelled set. W sets keep only coarse groups that hold ≥ 2 such fine keys.

## Label-free inventory (`analysis/pe015_inventory.json`)
546 PE012-eligible tablets have a fine key (3 lost to restored/unread headers); 146 distinct fine keys.
| Test | Tablets | Fine keys | Coarse groups | Label marginal |
|---|---|---|---|---|
| H1G | 183 | 13 | 8 | C 125 / I 46 / MIX 12 |
| H1W | 166 | 9 | 4 | C 114 / I 41 / MIX 11 |
| H2G | 405 | 25 | 18 | 0: 27, 1: 177, 2: 158, 3: 43 |
| H2W | 325 | 11 | 4 | 0: 22, 1: 137, 2: 126, 3: 40 |
Biggest split: M157 (94 / 173) vs M157~a (28 / 59) in H1 / H2. Dead-on-arrival size gates: all four pass.

## Tests (fixed now)
| Id | Statistic | Null: fine keys permuted within |
|---|---|---|
| **H1G** | G, fine key × SYSTEM | PE012 H1 strata |
| **H1W** | same | PE012 H1 strata × coarse key (refinement only) |
| **H2G** | between-key SS of SIZE | PE012 H2 strata (size beyond system) |
| **H2W** | same | PE012 H2 strata × coarse key |
R = **9 999**, seed **1501** (+ test index × 10 000); p = (1 + #null ≥ obs)/(1 + R). **Holm over the runnable tests.**
Seeds: 1501 null, 1502 FPR, 1503 / 1504 power batches, 1505 audit, 1599 registered shuffle (smoke).

## Gates (re-run identically inside `test`; a failed gate = NOT TESTABLE, test **not run** on the real pairing)
- **Size**: G ≥ 30 tablets in ≥ 3 fine keys; W ≥ 30 informative tablets in ≥ 2 coarse groups.
- **FPR**: 40 destroyed datasets (the test's own null), R 299: rate p ≤ 0.05 must be ≤ 0.10.
- **Power** (Kryptos's two-batch gate, her I-182): **two independent batches** of 100 (seeds 1503, 1504): destroy with
  the test's own null, each fine key gets one target label drawn from the set, each tablet (prob **0.5**, PE012's plant)
  takes its key's target; R 299; rate p ≤ 0.05/k (k = 4 tests passing the size gate → 0.0125) must be ≥ 0.80 on **both**.

## Rehearsal before this push (destroyed and planted data only; 21.8 s; small batch timed first, Kryptos's I-180: 0.016–0.030 s per R 299 null)
| Test | n | FPR | Power 1503 / 1504 | Gate |
|---|---|---|---|---|
| H1G | 183 | 0.10 ✓ | 0.83 / 0.81 ✓ | **runnable** |
| H1W | 166 | 0.05 ✓ | **0.48 / 0.51 ✗** | **NOT TESTABLE (LOW-POWER)** |
| H2G | 405 | **0.125 ✗** | 1.00 / 0.99 | **NOT TESTABLE (FPR gate)** |
| H2W | 325 | 0.00 ✓ | 0.81 / 0.80 ✓ | **runnable** |
Nothing was changed after the rehearsal: gates, plant and k are as first written. H2G's 5/40 is very likely Monte Carlo
noise of a 40-dataset gate (a permutation test's true FPR is ≤ 0.05), though not a comfortable excuse (P(≥ 5/40 | 0.05) ≈ 0.048). The gate is the gate:
H2G stays NOT TESTABLE and is not run. H1G and H2W pass only just (0.81 and 0.80 on the weaker batch).
Smoke on registered shuffle 1599 (R 999, destroyed copy, not observed values): H1G G 30.72 (null mean 26.20, p 0.226);
H2W SSB 13.09 (null mean 12.57, p 0.402).

## Decision rule
NOT TESTABLE if any gate fails (H1W, H2G already). For H1G and H2W: **SUPPORTED** if Holm p ≤ 0.05 (Holm over 2),
**NOT DETECTED** (powered for plant 0.5 only) otherwise. No EXCLUDED verdict (no natural rate bound). A SUPPORTED H1G
alone would not separate the fine key from the coarse key PE012 already tested (H1W, the separating test, is not
testable); it would be reported as such. If both runnable tests come out NOT DETECTED, line 5 is closed within reach of
this corpus and **the camp pauses with its second closing summary** (as planned in `4013328`).

## PE014 audit (this cycle)
PE014 H2 (272 adjacent informative pairs, T 40, p 0.3432 with seed 1401) re-drawn with **seed 1505, R 9 999**: pairs and
T must be identical and p must stay > 0.05.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
