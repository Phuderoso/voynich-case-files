# C054 — Expedição 54: a máquina na medida certa? (matched fit for exact repeats)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** F-REP step 3. [C053](C053-generator-repeats-sweep.md) closed C052's exact-repeat gap across generator settings, but the three settings that reached it overshot: X 3.1–3.9 at 4–8% raw repeats, against the manuscript's X 1.30–1.34 at 0.89–1.16%. All three used `method.canFollow = statistic`. The open question is whether any setting lands on both numbers at once.

## Pre-registration (pushed before any C054 number)
- **Search space, fixed now:** every successful S2 config of the C004 sweep with `method.canFollow = statistic` — **27 configs** (three of them are C053's S2_4/S2_6/S2_7). No new tuning.
- **Screen:** seed 9001, 3,400 lines unless set, first 15,000 tokens, 115-token pseudo-pages; C052's R0 statistic with a 300-shuffle within-page null. Also record R1 X (descriptive).
- **Window (from C052's Voynich halves, widened):** X ∈ [1.20, 1.50] **and** raw R0 rate ∈ [0.80%, 1.30%].
- **Confirm:** the screen hits closest to (X 1.32, rate 1.0%) — at most 3 — on held-out seeds 9002–9004, with per-text gates at α = 0.05/9 (page-shuffled FPR p ≥ α; 3% plant p < α). A seed is IN WINDOW if both numbers are in the window and its own excess p < α.
- **Verdict:** MATCH FOUND if a config is IN WINDOW on all three held-out seeds; PARTIAL if there are screen hits but none confirms; NO MATCH if no screen hit among the 27; NOT TESTABLE if fewer than 20 configs give text.
- **Reading rules fixed in advance:** MATCH FOUND means the copying account can reproduce this feature at the manuscript's level in this slice of settings (it does not show the manuscript was made that way, and C052's other placements must then be checked on that config). NO MATCH says only that this slice of 27 settings does not; it does not exclude the generator.
- **Tool:** `tools/c054_matched_repeat_fit.py` → `analysis/C054_results.json`; `timeout 600`.

## Results
(pending)

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
