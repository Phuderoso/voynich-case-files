# K091 · K019 cord-level check with a shift-aware exact null and an exhaustive calibration corpus (README line 9)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registered** (this file and the tool are pushed before the real run; results will be appended below).

## Why this one
K090 left two things open (both named in its Reading as "the K091 candidate"):
1. **The KFG calibration was data-limited.** Only 92 random unrelated KFG pairs reached ≥ 5 leader-matched groups in
   20 000 draws, below the registered 100, so all three KFG pairs went NOT TESTABLE (pipeline) although the rate
   (1/92 = 0.011) was under the bar. Sampling was the bottleneck, not the data: here **every ordered pair** of the 312
   candidate khipus is enumerated.
2. **Paris·Lima failed the shift gate.** Pairing each KH0586 group with the KH0097 partner of its neighbouring group
   (offsets ±1) already gave p 0.0032 / 0.00059 under K019's null: KH0097's groups resemble their neighbours (a slowly
   drifting template). K019's null lets the true partner's *neighbours* act as "wrong partners", so it cannot separate
   "template drift" from "group-to-group copy" — and conversely the true partner's own neighbours inflate nothing in
   the null, they deflate it. A **shift-aware null** asks the sharper question: does the true partner beat groups that
   are *not* its immediate neighbours, and do the ±1 neighbours still beat that same null?

## Disclosed before writing this
- **Everything observed on these pairs under K019's null is public** (K019, K090): V_tot 89 / 37 / 36, exact p
  10⁻¹⁵–10⁻¹⁸, and the K090 post-hoc diagnostic that only offsets ±1 reject for Paris·Lima. The radius W = 1 was chosen
  *after* seeing that diagnostic; W = 2 and 3 are printed descriptively to show whether the verdict depends on it.
  The p under W ≥ 1 has **not** been computed by anyone before this push.
- **Plumbing smoke** (`run --smoke`, non-leader values shuffled within each khipu, calibration on the first 40
  candidates only, OKR arm skipped): G0, fixture 42/42, A0 (K019 rebuilt exactly on the OKR) passed; shuffled-data
  p 0.71 / 0.36 / 0.51, MC and exact agreed. Smoke statistics are noise and were deleted.

## Design (changes from K090 only; everything else verbatim)
- **Tool** [`tools/k091_shift_aware_k019.py`](../tools/k091_shift_aware_k019.py), produced from
  `tools/k090_kfg_k019_cord_level.py` (fde05b9) by a scripted patch; every changed line is marked `K091`.
  SHA-256 `036048fa1d3f0c9c591f5f86c640c8670e1ea7eab723d75b4f3777c934c32b8c`.
- **Data** unchanged: KFG `kfg_20261111.db` (SHA-256 `582e548d…742994d`) + 695 hash-checked xlsx, R5 masked;
  OKR `khipu.db` (SHA-256 `607913…c1c4db`).
- **Statistic** unchanged: V_tot = Σ LCS(non-leaders of A_i, non-leaders of B_j) over leader-matched (i, j).
- **Null (new, primary W = 1).** Each matched B_j receives a uniformly random leader group i₂ of A with
  **|i₂ − i| > W**: the true partner and its two neighbours in A's leader-group order are excluded. Exact p by integer
  convolution (K090 engine). Descriptive only: W = 0 (= K090), 2, 3. MC cross-check R 10 000, seed **6487**.
- **Shift gate** unchanged in form (cyclic offsets k = 1…m−1, share with p < 0.01/3 > 0.10 → TOOL EXCLUDED), each
  pseudo-observation scored under the **same W = 1 null** around its own pseudo-partner.
- **G-FPR (exhaustive).** All ordered pairs (a, b), a ≠ b, of the 312 candidate KFG khipus (eligible, ≥ 2 leader
  groups, none of the five named khipus) are aligned; kept if ≥ 8 matched groups, fallback ≥ 5 if fewer than 100;
  **no cap, no sampling, no seed**. Pairs where some matched group has no admissible alternative under W = 1 are
  dropped and counted. **Gate: ≥ 100 pairs and FPR ≤ 0.02** at 0.01/3. Note: ordered pairs (a, b) and (b, a) are both
  in the corpus; they are not independent, and the count is reported as is.
- **G-POW** unchanged (planted copy f = 0.25 on the same pairs, seed **6488**; curve f = 0.10/0.15/0.25/0.40, seed
  **6489**; bar 0.5; gates only the reading of silence).
- **Holm** at family α 0.01 over the 3 pairs.

## Decision rules (written before the run)
- G0, fixture or A0 fail → cycle EXCLUDED. G-EX or G-FPR fail → every KFG pair **NOT TESTABLE (pipeline gate)**.
- Missing khipu / < 2 matched groups / a matched group without admissible alternatives → **NOT TESTABLE (data)**;
  shift gate fails → **TOOL EXCLUDED**; Holm-rejected → **CONFIRMED**; not rejected → **NOT CONFIRMED** if G-POW
  passes, else **NOT TESTABLE (power)**.
- **OKR arm** (same rules; G-FPR is KFG-only, as in K090). Against K019 as corrected by K090 (Paris·Lima TOOL
  EXCLUDED, Berlin CONFIRMED): if Paris·Lima becomes CONFIRMED under W = 1, the K090 correction is **superseded** —
  K019's Paris·Lima cord-level agreement is restored *as a shift-aware result* (true partner beats non-neighbour
  groups and the neighbour template does not pass the same test). If it stays TOOL EXCLUDED, the K090 correction
  stands. A Berlin pair that is not CONFIRMED under W = 1 is a **new correction** of K019.
- **KFG mapping** (line 9 table): KFG label equal to the OKR label under the same K091 rules → **REPLICATED**;
  different readable label → **CHANGED**; any KFG NOT TESTABLE → **NOT TESTABLE**.

## What this cannot decide
A CONFIRMED is a value correspondence (copy, or the same object recorded twice), not a reading. KFG and OKR share
recorders for these khipus: a re-audit on re-curated data, not an independent replication. W = 1 was fixed after the
K090 diagnostic (disclosed above).

## Seeds and compute
MC **6487**, power **6488**, curve **6489**; next free **6490**. From `expeditions/khipu/`:
`timeout 600 python3 tools/k091_shift_aware_k019.py run` → `analysis/k091_results.json`, log
`analysis/k091_run.log`. Smoke 5 s; full run expected ≈ 1–2 min (≈ 97 000 alignments).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
