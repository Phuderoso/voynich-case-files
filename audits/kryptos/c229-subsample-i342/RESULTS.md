# RESULTS — I-342 subsample test (c229 Y lines): search size N vs composition, at fixed nq and fixed N

Voynich desk, 2026-11-21 (MST). Prereg commit `b8c71f75` (`PREREG.md` sha256 `78af9769…`, tool `i342_subsample.py` sha256 `5185d776…`, gates ALL PASS). **One real run**, 14:39:31 MST start (about 4 min), tool unchanged since the prereg, `python3 i342_subsample.py real --i-froze-prereg`, log `run_log.txt`. Inputs: 161 R files re-verified against her `SHA256SUMS` (0 bad), 9,693 cells inside the nq 10–40 windows, 16 nulls. Not a decipherment; no bar proposed.

## Confirmatory family (Holm over 4, α = 0.05, cluster bootstrap over the 16 nulls, B = 1000, bootstrap floor p = 0.002)
| Test | θ̂ | 95% CI | threshold | p | Holm step | distance | outcome | replicas (fresh seed / nulls A / nulls B) | label |
|---|---|---|---|---|---|---|---|---|---|
| T1 b_A(STRAT), per unit ln N | **0.1902** | 0.1819–0.1965 | δ_b 0.0217 | 0.0020 | 0.0125 | ≥ 6.3× (p at floor) | **MATERIAL** | 0.1896 / 0.1868 / 0.1904, all above δ_b | robusto |
| T2 −c_B(STRAT), per quadgram | **0.0171** | 0.0154–0.0185 | δ_c 0.0100 | 0.0020 | 0.0167 | ≥ 8.3× (p at floor) | **MATERIAL** | 0.0173 / 0.0158 / 0.0186, all above δ_c | robusto |
| T3 \|b_A(POOL) − b_A(STRAT)\| | 0.0094 | 0.0044–0.0157 | m_b 0.00543 | 0.112 | 0.025 | 4.5× (p/α_step, not rejected) | **INCONCLUSIVE** (not rejected) | 0.0097 / 0.0128 / 0.0101, all above m_b | robusto (of the non-rejection) |
| T4 \|c_B(POOL) − c_B(STRAT)\| | 0.0023 | 0.0014–0.0036 | m_c 0.0025 | 0.883 | 0.05 | 17.7× (not rejected) | **INCONCLUSIVE** (not rejected) | 0.0021 / 0.0021 / 0.0022, all below m_c | robusto (of the non-rejection) |

Reading the labels honestly: `robusto` here means *the call (reject / not reject) is ≥ 2× from its Holm step and every replica has θ̂ on the same side of the threshold*; for T3 and T4 it certifies a stable **non-rejection**, not an equivalence (T3's point estimate is above its margin in all four runs, T4's just below, and both CIs straddle or touch the margin). The replicas are a fresh-seed rerun and two disjoint halves of the same 16 nulls, **not fresh nulls**; the T1/T2 distances are lower bounds because p sits on the bootstrap floor.

## What it says (descriptive reading, no mechanism)
- **Search size matters at fixed nq and fixed family, strongly, inside the covered range** (per-draw N 10–2000): +0.190 NC per e-fold of N = **+0.44 NC per decade**, 8.8× the materiality unit (0.05/decade). **nq matters at fixed N**: −0.0171 NC per quadgram (1.7× the unit 0.01), i.e. −0.086 per five quadgrams. Both survive Holm and all replicas. So the c229 verdict "both terms" holds as a *functional-form* statement: a bar that depends on nq alone would miss a decade-of-N shift ~9× the unit.
- **Composition (family) does not move the coefficients enough to separate**: ignoring family changes b by 0.0094 (5% of b_A) and c by 0.0023 (13% of c_B); neither test rejects (T3 p 0.112, T4 p 0.883). Absence of evidence at this margin, not evidence of equivalence.
- **Descriptive, untested:** per-family (STRAT point values) b_A / c_B: bank_V_a 0.196 / −0.0179, bank_V_b 0.199 / −0.0193, all_V_a 0.189 / −0.0188, all_V_b 0.192 / −0.0179, all_Q_r10 0.191 / −0.0175, **bank_Q_r10 0.164 / −0.0094** (the outlier: about half the length slope; its pools have the smallest N and lowest max). Joint M3 inside STRAT (fixed effect family): ln N +0.191, nq −0.0175, R² 0.591; extreme-value form M4 R² 0.520 (not better in this range).
- **Does not reconcile with c229's pooled partial coefficients** (+0.056 per e-fold, −0.024 per quadgram): different estimand (within-pool nested draws capped at N_d < 2000, versus per-bin maxima over 10 to 4×10^6 decipherments pooled across nulls and files). The subsample b_A is 3.4× larger, c_B 0.7×. **Post hoc** (not preregistered, `posthoc_levels.py`, seed 11857): the per-e-fold slope between successive levels falls slowly, 0.215 (10→30), 0.193 (30→100), 0.199 (100→300), 0.168 (300→1000), so the linear-in-ln N form is only an approximation and nothing here says what happens at 10^5–10^6. Mean draw max at the 1000 level (N_d ≈ 1,160): −6.80 averaged over pools; by window −6.37 (nq 10–12) to −7.07 (nq 31–40) (`posthoc_levels_output.txt`).
- **Per-text pass rates at the bar with Wilson 95%** (`passrates.tsv`): at most 1/16 [0.011, 0.283] per family × window; pooled over families (overlap not de-duplicated) 1/16, 2/16 [0.035, 0.36], 1/16, 0/16, 0/16 for nq windows 10–12, 13–16, 17–22, 23–30, 31–40. The same four null texts as c229 (8 hits at nq 12, 13, 13, 19), nothing new.

## DEVIATIONS / disclosures
1. Replicas are not fresh nulls (stated in the prereg §5).
2. `posthoc_levels.py` is post hoc and descriptive, seed 11857 (reserved, now used). Seeds used: 11850–11856 and 11857; **next free 11860** (11858–11859 reserved, unused, retired).
3. The prereg was written knowing the aggregate c229 outcome (PREREG §0); the window/level grids came from structure counts, not from max values.
4. Before the prereg commit, the synthetic gate set was revised once (flat plant and zero-null composition test replaced; draws per bootstrap level 40 → 200), all on synthetic data; the gates in the repo are from the final tool, run twice with identical output.
5. A smoke of the real code path (synthetic P1 plant, tiny B) ran before the prereg commit; it wrote its two output files (`results.json`, `passrates.tsv`, synthetic content) by mistake into `/tmp/smoke`, a scratch dir that belongs to the concurrent c231 job; I removed those two files afterwards (the other job's scripts do not reference those names, but I cannot rule out that I overwrote same-named files of theirs). No real `max=` was used in it.

I'm Voynich — an AI archaeologist, born 4 November 2026, pimpolha (creation) of Phuderoso (github.com/Phuderoso)
Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026
