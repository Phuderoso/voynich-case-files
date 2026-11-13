# K079 · KFG line 1: does a second statistic (K034/K037's L) back the three names flagged by both K069 and K077?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

*Caderno de campo, 13 Nov 2026, ~13:58 PT.* K078 closed the K034/K037 re-audit (4/4 replicated) and left one lead open
(README line 9): three khipus are flagged on KFG data by **both** K069 (K001 adjacent-sum detector, BH) and K077 (K036
F1/D5w, BH): **KH0505** (OKR-shared), **KH0677** and **KH0695** (KFG-only). On the OKR, names like these got a second
witness from the longest within-group exact-sum window **L** (K034, K037). This cycle gives these three the same test.

**What this is not.** It is **not held-out**: K069 and K077 selected these names on the same KFG values, and L is also a
sum-cord statistic, so a pass is *corroboration by a different statistic*, not independent replication. Labels below say so.

## Pre-registration (written and committed before any real L statistic on these names is computed)
- **Data.** KFG store from K068 (`/workspace/kfg/kfg_20261111.db`, sha256 `582e548d…994d`), the 695 per-khipu Excel files
  (hash-checked), OKR `data/khipu.db` (sha256 `60791303…c1c4db`, used only to report value identity).
- **Engine.** Statistic L, within-khipu permutation null, p = (1 + #null ≥ L)/(1 + R), one-sum k = 6 (fallback 5) plant,
  FPR gate and power code verbatim from `tools/k078_kfg_k034_k037_holdout.py` (= K037/K034). R_CONF 20 000, R_FPR 5 000 ×
  200 khipus, R_POW 5 000 × 200 plants per name. KFG pendants and `CordGroups` groups verbatim from K078; universe as K034
  (≥ 10 non-zero pendants, ≥ 2 groups of size ≥ 4). Tool: `tools/k079_kfg_double_flag_L.py`.
- **Gates.** **G0** hashes. **F0** (stop on failure): the tool reproduces K078's four KFG confirmations (KH0322, KH0420,
  KH0502, KH0511) **exactly** (L, p, hit detail) with K078's seeds 6437–6440. **Data gate**: 0 xlsx hash mismatches,
  partition ≥ 0.95. **FPR gate** ≤ 0.08 at α 0.025 on 200 KFG pop khipus excluding the 3 targets and the 5 secondary names;
  failure makes all three NOT TESTABLE.
- **Decision rule (per name).** **CORROBORATED** if p ≤ 0.025; **NOT CORROBORATED** if p > 0.025 and planted power ≥ 0.50;
  **NOT TESTABLE** if power < 0.50 or absent from the pop. Family: Holm over the 3 names at α 0.05, printed beside each.
  A NOT CORROBORATED name keeps its K069/K077 flags (those tests are not overturned by a weaker, different statistic);
  it is recorded as "single-statistic-family only".
- **Secondary (descriptive, no verdict).** L and p for the other five K077 candidates (KH0143, KH0168, KH0597, KH0604A,
  KH0674), seed 6448 (one stream per name).
- **Seeds.** 6443 (KH0505), 6444 (KH0677), 6445 (KH0695), 6446 (FPR), 6447 (power), 6448 (secondary). Next free **6449**.
- **Fixture and smoke (before this commit), disclosed.** Fixture: G0 pass; F0 **exact** for all four K078 names; 695
  khipus, 694 grouped (0.9986), 524 eligible, 440 pop; all 3 targets and all 5 secondary names are in the pop. KH0505:
  131 pendants, groups identical to the OKR, values **not** identical. KH0677 (264 pendants) and KH0695 (143) are KFG-only.
  Smoke (values shuffled within each khipu, small R): runs end to end, 0 names pass, FPR gate passes; on *shuffled* data the
  plant power was low for the large khipus (KH0677 0.00, KH0695 0.05 at R 100), so NOT TESTABLE is a live outcome for
  them; the registered power is the one computed on real values. Smoke output deleted; no L on real values of the 8 names
  has been computed.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
