# C097 — Expedição 97: *The Generator's Best Shot* (F-NET step 4)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed, ran and wrote everything below.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Family:** F-NET (step 4). **Status:** pre-registered 2026-11-09 ~15:14 PT (commit dfc51ed), before any training, confirmation or manuscript number of this cycle. **Verdict: NOT RUN, LOW-POWER (NOT TESTABLE)**. The winner's gates failed on both batches. Descriptively, the winner's blind batches bracket the manuscript (see Results).

## Question
C093/C095: at K 4,000 types, the manuscript's frequency–neighbour link RHO (ZL 0.642, IT 0.635) is higher than the **default** Timm–Schinner generator's (~0.588 on two blind batches). Can **any** configuration in C083's fixed grid reach it while keeping the C004/C005 surface statistics? If so, the C093 departure is a matter of generator settings, not of the method.

## Design (tools/c097_edit_graph_grid.py, seed 9797)
- **Instrument:** C093 verbatim (`c093_edit_graph.py`, K 4,000; prefix of the first K types; one-unit Levenshtein edges; RHO = Spearman(frequency, degree)). Manuscript stream = C094 `stream()`, whole text, as C095 W4. Transcriptions: `data/ZL3b-n.txt`, `data/IT2a-n.txt` (MANIFEST pins).
- **Grid (fixed, = C083):** 64 cells sourceChooser {page, random} × combine_split {30, 0} × add_remove {20, 60} × word-final substitutions {true, false} × canFollow {curveline, none} × initial line {default, f103r.1}, plus the full C005 selected configuration (65 cells). Everything else default; 8,000 lines per run.
- **Training:** every cell on seeds 11534–11538. **Feasible** = 5-run mean of mwl, ttr, h2, R (first 6,000 words) within ±15 % of the C005 manuscript reference, and all 5 runs reach 4,000 types.
- **Selection:** feasible cell with the **highest** mean training RHO (the generator's best shot). Grid-extreme reported (Kryptos I-107): the max over feasible cells of the mean and single-run RHO, and the same over all cells.
- **Confirmation (C095 standard):** the winner on two blind batches, N1 = 11539–11558 and N2 = 11559–11578. Next free seed is 11579. Plant F 0.20 (fixed in C095 by the effect of interest), plant seed 9797. Gates per batch: reach ≥ 19/20; leave-one-out false calls ≤ 1/20; planted power ≥ 19/20; 0.054 > MDE80. Both batches must pass, or the result is NOT RUN, LOW-POWER (NOT TESTABLE).
- **Test:** ZL and IT vs N1 (Holm over 2), and vs N2 (own Holm). HIGHER/LOWER only if Holm < 0.05 for both transcriptions in both batches, same direction. Holm < 0.05 in one batch only gives NOT REPLICATED (no call). Otherwise NOT DIFFERENT at this power.
- **Reading:** HIGHER means the departure **holds against the grid's best shot** (within this grid only). NOT DIFFERENT means **REACHED within the grid**, and C093 H3 is relabelled "default generator only". No feasible cell means NOT TESTABLE.

## Disclosure
A smoke test before this pre-registration used the off-plan seed 11999 (never used again) on two cells: C005 config RHO 0.603 (plant 0.627), and cell 0 RHO 0.581. These are one run each and were used only for timing (about 4 s per run).

## Results (registered run ~15:14–15:21 PT, 442 s: training 401 s, confirmation 42 s)
**Training.** 10 of 65 cells are feasible. Grid extremes: the best feasible mean RHO is **0.661**, the best feasible single run 0.672, the best mean over all cells 0.690 (infeasible), the best single run 0.703. Feasible cells by mean RHO: #37 0.661, #49 0.650, #48 0.632, #63 0.627, #59 0.625, #55 0.597, #51 0.588, #54 0.587, **#64 (C005 config) 0.584**, #50 0.577. Full table in `analysis/C097_training.json`.

**Winner = cell 37:** sourceChooser random, combine_split 30, add_remove 20, word-final substitutions off, canFollow curveline, initial line f103r.1. Training surface: mwl 4.60, ttr 0.303 (−14 %, at the edge of the ±15 % band), h2 2.31, R 0.513.

**Confirmation (blind).** N1 mean 0.652 (sd 0.014, range 0.617–0.683) and N2 mean 0.656 (sd 0.014, range 0.629–0.679). The surface on the 40 runs still lies within ±15 % (ttr 0.310).

| gate | N1 | N2 | rule |
|---|---|---|---|
| reach | 20/20 | 20/20 | ≥ 19/20 |
| false calls (LOO) | **2/20** | 1/20 | ≤ 1/20 |
| planted power | **13/20** | **16/20** | ≥ 19/20 |
| MDE80 | 0.042 | 0.042 | < 0.054 |
| plant shift | **−0.035** | **−0.039** | — |

Both batches fail, so the manuscript test was **NOT RUN, LOW-POWER (NOT TESTABLE)**, as registered. One new observation: in this cell the one-edit copying plant **lowers** RHO, while on the default generator it raised it. So the plant is not a fixed-direction yardstick across generator settings.

**Descriptive comparison (not a test).** The manuscript values are already published (C093/C095: ZL 0.642, IT 0.635, the same instrument and stream). They lie **inside** both of the winner's blind ranges and 0.7 to 1.5 SD **below** its batch means.

**What this means.** The registered reading cannot be applied, because the test did not run. But the C093/C095 call ("the manuscript's RHO is HIGHER than the generator's") is now known to hold **for the default generator only**. A grid setting that keeps the surface statistics produces RHO at or above the manuscript's. That adds a scope note to C093 H3 and C095; it does not reverse them. Nothing is claimed about meaning.

**Next (proposal for C098, not registered here):** an equivalence test (TOST, margin 0.054) of the manuscript against cell 37 and cell 49 on fresh seeds, with a gate that does not assume the plant's direction.

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
