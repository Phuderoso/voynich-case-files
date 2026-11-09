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

---

## Results (computed after the pre-registration commit `42638a7`)

Tool run once as written (`full`), 2026-11-09 15:50:14–15:52:33 PT (138.3 s, under `timeout 600`). Outputs: `analysis/k060_results.json`, `analysis/k060_run.log`.

| Gate / test | Number | Rule | Outcome |
|---|---|---|---|
| G0 fixture (= audit of K059's G0, seed 5962) | 20/20 exact | 20/20 | pass, **K059 G0 reproduced** |
| Audit K012 (Poisson, all pairs, real data) | 5 323 blocks, 6 BH discoveries | = published | **reproduced exactly** (third time: K012, K059, K060) |
| Family F_prov | 4 039 pairs, 51 provenances (largest 69, 37, 34, 20 khipus) | metadata only | as registered |
| G1 FPR (40 run-preserving nulls, within-family BH) | 0/40 corpora with a discovery (exact bound also 0/40); pair share p < 0.01 = 0.00045 | ≤ 0.10 and ≤ 0.01 | pass |
| **G2 power, 200 within-family 6-cord plants** | **0.565** (exact bound 0.49) | ≥ 0.80 | **fail** |
| Cell scope (≥ 30 plants and ≥ 0.80) | Pachacamac 0.61 (114 plants), Ica 0.56 (41); Incahuasi 0.54 (26, too few) | — | **no full-power cell** |
| secondary: 8-cord plants (100) | 0.69 (exact 0.66) | — | descriptive |

**Verdict by the rules written beforehand.** Short (6-cord) within-provenance matches: **NOT TESTABLE (LOW-POWER)**. G2 failed and no cell
reached full power, so the observed within-family scan (H1) was **not run**. Nothing about the real within-provenance pairs is claimed,
detected or excluded by K060.

**What moved (same plant design, smaller family).** Shrinking the family 23× (93 528 → 4 039) doubled K012-Poisson power at 6 cords
(0.28 in K059 → 0.565) and lifted 8-cord power (0.53 → 0.69). The median plant p (5.5×10⁻⁶) now clears the BH first rank (1.24×10⁻⁵).

**Why it still fails (descriptive, no decision weight).** The plant p distribution has a heavy weak tail: the 80th-percentile plant p is
**0.0027**, so Bonferroni-level power 0.80 would need a family of **M\* ≈ 18 pairs**. About one 6-cord copy in five collapses to so few,
so common symbols that no per-pair chance model can separate it from coincidence at any useful family size. Family size is no longer the
main bottleneck; the **information content of the copy** is. More family shrinking cannot make 6-cord silence readable. Line 3's honest
floor stays **8 cords** (K014), and even within provenance 8-cord power is 0.69.

**Next on line 3 (named, not run).** Either (a) a pre-named family of **≤ 20 pairs** chosen from outside evidence (e.g. the Field Guide's
"most similar" pairs, or museum-number neighbours), or (b) condition the plants on information content (e.g. ≥ 4 distinct collapsed symbols)
and state the readable class explicitly. Otherwise line 3 rests: long matches mapped (K005–K014), short ones unreadable by design.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
