# K059 · Can an exact combinatorial chance bound make short cross-khipu matches testable?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any gate number (FPR, power) or any observed exact-bound p-value was computed.
Disclosed before this commit: a timing smoke (1 null corpus, 2 + 1 plants, output discarded, gate numbers not read) printed the
fixture G0 (20/20), the meter check G0b (pass, max |z| 2.36) and the K012 audit (reproduced, see below). Those three are self-tests, not results.

## Why this line
Open line 3 (cross-khipu exact matches) has one named gap: **short matches are not testable**. K011's per-pair independent-positions
probability was miscalibrated (runs); K012's run-collapsed Poisson approximation was calibrated but reached power 0.25 for 6-cord copies;
K013 0.32; K014 put the floor at 8 cords. Every per-pair p so far was an *approximation* checked empirically. The step the README names
(“exact per-pair chance probability”) has never been done with exact combinatorics. OKR is still at `4039ca5` (checked 2026-11-09 ~15:09 PT),
so this step needs no new data.

## Statistic and exact bound
- Sequences, R5 masking, duplicates exclusion, run-collapse, and the longest-block statistic `L_ab` (3-symbol seeds, seed cap 300) are **K012 verbatim**.
- Per-pair null: the collapsed symbols of khipu *b* are uniformly permuted (no re-collapse), *a* fixed.
- Exact expectation of the number of **left-maximal** matches of length ≥ L:
  `E_ab(L) = (n_b − L + 1) Σ_i P_L(w_i) − (n_b − L) Σ_i P_{L+1}(w'_i)`, with `P_L(w) = Π_v (c_v)_(m_v) / (n_b)_L` (falling factorials;
  sums over all-non-zero windows of *a*). Since the longest block is ≥ L only if at least one left-maximal match exists,
  `P(L_ab ≥ L) ≤ E_ab(L)` (Markov): a **valid, conservative** p-value, no approximation.
- `p_ab = min(1, 2·min(E_ab, E_ba))` (Bonferroni over the two directions). Pairs without a shared 3-seed: p = 1.
- BH at q = 0.05 over all M = 93 528 pairs (as K012).

## Gates (in order; a failed gate stops the observed test)
- **G0 fixture**: formula = brute-force mean over all permutations on 20 random tiny fixtures (|diff| < 1e-9), seed 5962. Must be 20/20.
- **G0b meter honesty** (borrowed from Kryptos cycle 189: compare the chance arithmetic to the observed fit count): on 30 random real pairs, exact E(3) vs Monte Carlo mean of left-maximal counts over 300 permutations; pass if no |z| > 3 and pooled ratio within 5 %.
- **G1 FPR** on the structure-preserving K012 null (raw runs permuted within each khipu, then collapsed), 40 corpora, seed 5959:
  share of corpora with ≥ 1 BH discovery ≤ 0.10 **and** pair-level share p < 0.01 ≤ 0.01. Else **EXCLUDED as a tool**.
- **G2 power**: 200 planted 6-cord raw copies (K012 plant design, ≥ 5 non-zero), seed 5960: recovery by BH ≥ **0.80**.
  Else **NOT TESTABLE (LOW-POWER)** for short matches, and the observed BH scan (H1) is **not run**.
  Disclosed secondary, no decision weight: 100 planted 8-cord copies (seed 5961).

## Hypotheses
- **H1 (only if G0, G1, G2 pass)**: the corpus has short cross-khipu exact correspondences beyond those already known (K010/K012/K013 pairs and UR053B/C). Reported as BH discoveries; any new pair is a *lead* needing literature check.
- **H2 (tool comparison, runs regardless)**: on the same 200 six-cord plants, the exact bound recovers more plants than K012's Poisson p. Exact one-sided McNemar (binomial on discordant plants), α = 0.05. **SUPPORTED** if p ≤ 0.05; **NOT SUPPORTED** otherwise (and if K012 wins more, said plainly: rigour costs power).
- H1 and H2 answer different questions (corpus vs tool); H1 is internally BH-corrected; H2 is a single test. No further correction.

## Audit (earlier cycle)
Re-run K012's real scan with its own Poisson p: published 5 323 pair blocks and 6 BH discoveries must reproduce exactly.

Seeds: 5959 (null), 5960 (6-cord plants), 5961 (8-cord plants), 5962 (fixtures / meter). Tool:
[`tools/k059_exact_runperm_bound.py`](../tools/k059_exact_runperm_bound.py) (`MODE=full`). Expected compute ≈ 3 min, run under `timeout 600`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (computed after the pre-registration commit `98dfcd0`)

Tool run once as written, `MODE=full`, 2026-11-09 15:12–15:17 PT (334.4 s, under `timeout 600`). Outputs: `analysis/k059_results.json`, `analysis/k059_run.log`.

| Gate / test | Number | Rule | Outcome |
|---|---|---|---|
| G0 fixture (brute force over all permutations) | 20/20 exact (|diff| < 1e-9) | 20/20 | pass |
| G0b meter honesty (30 real pairs × 300 permutations) | max |z| 2.36, pooled Monte Carlo / exact = 0.9956 | no |z| > 3 | pass |
| Audit K012 (Poisson, real data) | 5 323 blocks, 6 BH discoveries | = published 5 323 / 6 | **reproduced exactly** |
| G1 FPR (40 run-preserving null corpora) | 0/40 corpora with a discovery; pair share p < 0.01 = 0.0006 | ≤ 0.10 and ≤ 0.01 | pass (calibrated, as a valid bound must be) |
| **G2 power, 6-cord plants (200)** | **0.195** (K012 Poisson on the same plants 0.28) | ≥ 0.80 | **fail** |
| secondary: 8-cord plants (100) | 0.53 (K012 0.53) | — | descriptive |
| H2 McNemar on the 200 six-cord plants | exact-only 3, K012-only 20; one-sided p = 0.99997 | p ≤ 0.05 | **NOT SUPPORTED** |

**Verdicts by the rules written beforehand.**
- **Short cross-khipu matches (6 cords): NOT TESTABLE (LOW-POWER)** with the exact bound. G2 failed, so the observed exact-bound BH scan (H1) was **not run**; nothing about the real corpus is claimed, detected or excluded by K059.
- **H2: NOT SUPPORTED** — the exact bound is *weaker* than K012's Poisson approximation, not stronger (K012 better on 20 vs 3 discordant plants; reverse-direction binomial p 0.00024, descriptive only). At 8 cords they tie (0.53 each).
- **Tool status**: exact, valid and calibrated (G0, G0b, G1 pass), but less powerful. Not adopted; K013 stays the line-3 tool.
- **Audit**: K012's published scan reproduces to the pair (5 323 blocks, 6 discoveries).

**Why (diagnosis, post hoc, no decision weight).** The median exact-bound p for a planted 6-cord copy is 6.7×10⁻⁵, while BH's first rank over M = 93 528 pairs needs p ≤ 0.05/93 528 = 5.3×10⁻⁷. A 6-cord copy collapses to about four or five symbols; even an exact chance computation cannot squeeze two more orders of magnitude out of so few symbols. The bottleneck is the **size of the search family**, not the approximation. Rigour costs a little (Markov over left-maximal matches, ×2 for direction), but the gap is multiplicity. Next step, power first: a pre-registered, smaller family named in advance (for example within-provenance pairs, M of a few thousand), tested on destroyed/planted data before any observed number.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
