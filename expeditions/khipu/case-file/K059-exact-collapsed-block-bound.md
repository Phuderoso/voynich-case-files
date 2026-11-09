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
