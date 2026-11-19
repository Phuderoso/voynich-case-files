# K084 · KFG re-audit of K024: do deeper subsidiaries record the sum of their own subsidiaries? (line 9, step 16)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K084 statistic is computed on KFG data.

## Why
K024 (OKR) asked whether K004's rule (a cord = sum of its own subsidiaries) continues one or more levels down. On the
historical OKR only **109 eligible deeper parents** existed; power with 3 planted parents was 0.22, so the verdict was
**not testable** (2 hits vs 0.89 expected, p 0.22). The Khipu Field Guide (KFG, store built in K068,
`/workspace/kfg/kfg_20261111.db`) names cords by their tree path (`p12s3s1` ...) and carries 1 830 level-3, 300
level-4, 31 level-5 and 3 level-6 cords, so the question may become testable. This is the next verdict-reaching row of
the coverage table owed under line 9 (KFG re-audit).

## Data and definitions (K024's rules, KFG hierarchy as in K070)
- KFG cords whose name matches `p<n>(s<n>)*`; depth = number of path segments (p = 1, s = 2, ss = 3 ...). Cords with
  other forms (e.g. `p5m1`, 23 cords) are left out, as in K070. Value = KFG `value` (integer; blank = 0).
- **Gate G0:** every KFG xlsx hashes to the sha256 recorded in the store (as K070); a mismatching khipu is dropped and
  the gate is reported failed.
- **Eligible parent:** a cord at depth L ≥ 2 with value ≥ 10 and ≥ 2 children (cords at depth L+1 whose path extends
  the parent's).
- **Hit:** parent value = sum of its children's values with ≥ 2 children nonzero (K024 verbatim).
- One KFG record per khipu (the KFG has merged KH0140/KH0483, K068), so no duplicate flag is needed.

## Null and tests (K024 verbatim)
- **N_a (primary):** within each khipu, permute values among all cords at the **same depth** as the children (each depth
  ≥ 3 separately); parent values and tree shape fixed. K = 10 000. One-sided p = (1 + #null ≥ obs)/(1 + K).
- **Secondary:** the same test without KH0349 (UR113), reported; descriptive held-out view on KFG-only khipus (not in
  the OKR), no decision attached.

## Gates and controls
- **A0 (OKR anchor):** the K024 eligible set on the OKR is rebuilt inside the tool: must give 109 eligible parents and 2
  hits (exact). If not, the run is reported as **GATES FAIL**.
- **Calibration:** 200 corpora, each khipu's child values shuffled once and treated as observed (K 1 000 each);
  FPR at 0.01 must be ≤ 0.03.
- **Power:** 200 shuffled corpora with **3** eligible parents planted (K024 verbatim); disclosed secondary power at
  **5** planted (K024's add-on value), 200 corpora.

## Decision rule (fixed now)
- Gates fail (G0, A0 or calibration) → **GATES FAIL**, no verdict.
- p ≤ 0.01 → **evidence** that deeper subsidiaries record sums → KFG status **CHANGED** (OKR: not testable).
- p > 0.01 and power(3) ≥ 0.5 → **not supported (powered negative)** → KFG status **CHANGED** (now testable, negative).
- p > 0.01 and power(3) < 0.5 → **not testable** → KFG status **REPLICATED** (same verdict).
- One test, α 0.01; the KH0349-free test is a secondary report at Bonferroni ×2 (α 0.005) as in K024.

Seeds: 6463 (main), next free **6464**. Tool: `tools/k084_kfg_k024_deeper_sums.py`. Compute: under a minute, one
call under `timeout 600`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
