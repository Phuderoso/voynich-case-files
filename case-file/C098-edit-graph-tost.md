# C098 — F-NET step 5: is the manuscript's link RHO *equivalent* to the generator's best surface-keeping setting? (TOST)

**Status:** PRE-REGISTERED 2026-11-09 ~16:10 PT, before any C098 generator run or manuscript measurement. Results are added below the line after the run.

## Question
C093 and C095 found the manuscript's frequency–neighbour link RHO at K 4,000 types (ZL 0.642, IT 0.635) **higher** than the *default* Timm–Schinner generator (~0.588). C097 searched C083's fixed 65-cell grid. Its best surface-keeping cell (cell 37) produced blind batches averaging 0.652/0.656, which bracket the manuscript. But C097 could only test for *difference*, and its one-direction power gate failed, because the copy-plant **lowers** RHO on that host (−0.035). Not finding a difference is not the same as showing equivalence. C098 asks the equivalence question directly, with a calibration that does not depend on the plant's direction.

## Design (fixed now)
- **Instrument:** C093 verbatim (`tools/c093_edit_graph.py`, K 4,000), applied to the C094 manuscript stream (paragraph loci, whole text), as in C095 W4 and C097.
- **Host (fixed by C097, not re-selected):** cell 37: sourceChooser random, combine_split 30, add_remove 20, word-final substitutions false, canFollow curveline, initial line f103r.1. Each run is 8,000 lines.
- **Fresh blind batches:** N3 uses seeds 11579–11598 and N4 uses 11599–11618, 20 runs each. The next free generator seed is 11619.
- **Test:** a prediction-type TOST (two one-sided tests) of one new text against n runs. Let d = x − batch mean and SE = sd·√(1+1/n), with df n−1. Then p_TOST = max(P(T ≥ (d+δ)/SE), P(T ≤ (d−δ)/SE)). Holm correction runs over the two transcriptions, per batch and per margin.
- **Margins:**
  - δ1 = 0.054 is the manuscript's lead over the default generator (C095). It reads as "as close to cell 37 as the default generator is far".
  - δ2 = 0.027 is half that, the stricter claim.
- **Gates** are computed on generator runs only, before the manuscript is measured, per batch and margin:
  - **G0:** reach ≥ 19/20.
  - **GE1, false equivalence at the boundary:** each held-out run is shifted by +δ and by −δ and tested against the remaining runs. At most 3 of 40 may be called equivalent (nominal 5%).
  - **GE2, equivalence power:** each unshifted held-out run is tested against the remaining runs. At least 19 of 20 must be called equivalent.
  - A margin runs only if every gate passes in **both** batches. Otherwise that margin is **NOT TESTABLE**.
- **Verdict per runnable margin:**
  - **EQUIVALENT** if Holm p_TOST < 0.05 for both transcriptions in both batches.
  - **NOT REPLICATED (no call)** if that holds in one batch only.
  - **NOT SHOWN EQUIVALENT (inconclusive)** otherwise. This does *not* mean "different".
- **Descriptive only, no verdict:**
  - the two-sided difference p (C093 `pt`) and the manuscript's rank within each batch;
  - the copy-plant F 0.20 mean shift and mean |shift| on this host (plant seed 9898);
  - a known-different real-text check: the share of C095's 40 default-generator runs that the δ1 TOST would call equivalent to cell 37.
- **Expected from the C097 batch sd (~0.014), stated in advance:** δ1 should be gate-able, since δ/SE is about 3.8. δ2 will very likely fail GE2 (δ/SE is about 1.9) and come out NOT TESTABLE. We register it anyway, so the stricter claim is not quietly dropped.
- **Reading (registered):**
  - EQUIVALENT at δ1 means a surface-keeping generator setting can reach the C093/C095 RHO departure. RHO then no longer separates the manuscript from the Timm–Schinner hypothesis, and F-NET H3 is closed as a discriminator.
  - EQUIVALENT at δ2 as well would be a strong match.
  - Not shown equivalent means the question stays open at this power.
- **Compute:** 40 generator runs plus plants, about 1–2 minutes, run under `timeout 600`.

Run: `OMP_NUM_THREADS=1 timeout 600 python tools/c098_edit_graph_tost.py run analysis/C098_results.json`

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

---
## Results
(to be filled after the registered run)
