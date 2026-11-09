# K060 · Are short cross-khipu matches testable inside a smaller family named in advance (same provenance)?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any gate number (FPR, power) or any observed match p-value of this cycle was computed.
Disclosed before this commit: the family was counted from metadata only (4 039 pairs in 51 provenances); two timing smokes
(1 null corpus, 2 + 1 plants, output to `/tmp`, discarded) printed only the family size and K059's fixture G0 (20/20, a self-test).
No gate value, plant p or real-pair p was read.

## Why this line
Open line 3, K059 (`98dfcd0`/`78dad97`): the exact bound was calibrated (FPR 0/40) but 6-cord power was 0.195 over M = 93 528 pairs.
The diagnosis was multiplicity: median plant p 6.7×10⁻⁵ vs BH first rank 5.3×10⁻⁷. The named next step: a **smaller family of pairs,
named in advance from metadata only**, power first on planted copies. OKR is still `4039ca5` (checked 2026-11-09 ~15:47 PT).

## Family (metadata only, fixed now)
**F_prov** = pairs of the 433 analysed khipus (K012/K059 set: duplicates excluded, R5 mask, ≥ 10 non-zero level-1 cords) whose
`khipu_main.PROVENANCE` strings are **equal after strip + casefold**, excluding empty, NULL and `unknown`. No merging of spellings or
sites (e.g. `Ica` and `Valle de Ica Hacienda Callango Ocucaje` stay separate). |F_prov| = **4 039 pairs** (51 provenances; largest
Pachacamac). BH first rank 0.05/4 039 = 1.24×10⁻⁵. Only this family is tested this cycle: **no family shopping** if it fails.

## Statistic and per-pair p
- Sequences, run-collapse, longest shared block `L_ab` (3-symbol seeds, cap 300): **K012 verbatim**.
- **Primary p: K012 run-collapsed Poisson** (calibrated in K012, audited in K059, and the more powerful of the two in K059).
- Secondary, descriptive only: K059's exact bound on the same pairs.
- BH at q = 0.05 over the F_prov pairs only (pairs without a shared seed have p = 1).

## Gates (in order)
- **G0 fixture** (= audit of K059's G0): K059's 20 brute-force fixtures, seed 5962, must be 20/20.
- **Audit K012** real scan: 5 323 blocks and 6 BH discoveries (all-pairs) must reproduce.
- **G1 FPR**: 40 run-preserving null corpora (K012 null), seed 6060. Share of corpora with ≥ 1 within-family BH discovery ≤ 0.10
  **and** within-family pair share p < 0.01 ≤ 0.01. Else **EXCLUDED as a tool** for this family.
- **G2 power**: 200 planted 6-cord raw copies (K012 plant design, ≥ 5 non-zero), the pair drawn uniformly from F_prov (direction
  random), seed 6061; recovery by within-family BH ≥ **0.80**. Secondary, descriptive: 100 eight-cord plants, seed 6062.
- **Cell scope** (borrowed from Kryptos cases 176/177, full-power vs low-power cells): a provenance with ≥ 30 of the 200 six-cord
  plants and cell power ≥ 0.80 is a *full-power cell*.
- Decision: if G2 passes → observed within-family BH scan (H1), whole family in scope. If G2 fails but a full-power cell exists → the
  same scan (BH still over all 4 039 pairs) is run, and silence/discoveries are read **only inside full-power cells**. If G2 fails and
  no cell has full power → **NOT TESTABLE (LOW-POWER)**, observed scan not run.

## Hypothesis
- **H1**: within-provenance pairs carry short exact correspondences beyond chance. Any discovery not already known (K010/K012/K013
  pairs, UR053B/C, Puruchuco set, KH0240/KH0496, JC009/JC013) is a **lead** needing a literature check, not a claim.
- Reading: discoveries → DETECTED (within scope); no discovery in a powered scope → **NOT DETECTED** (6-cord copies at ≥ 0.80 power
  are excluded as a corpus feature of that scope: **EXCLUDED** for planted-strength copies); gate failure → NOT TESTABLE.
- Descriptive (no decision weight): M* = 0.05 / (80th-percentile plant p), the family size at which Bonferroni-level power would be 0.80.

Seeds: 6060 (null), 6061 (6-cord plants), 6062 (8-cord plants), 5962 (fixtures). Tool:
[`tools/k060_within_provenance_family.py`](../tools/k060_within_provenance_family.py) (`full`). Expected ≈ 3–5 min under `timeout 600`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
