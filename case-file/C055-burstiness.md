# C055 — Expedição 55: as palavras andam em bando? (new family F-BURST, word burstiness)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** new — F-BURST (the one-in-three rule: C053 and C054 continued F-REP). In natural prose, a mid-frequency word (a name, a plant, a tool) tends to clump: it turns up several times in one stretch and vanishes for pages. That clumping is a trace of *topic*. A copying process that draws on recent lines might clump as well, for a different reason. The question is how much the manuscript's words clump, against both.

## Pre-registration (pushed before the full run)
- **Texts:** ZL 3b and IT2a (`data/ZL3b-n.txt`, `data/IT2a-n.txt`, P loci with ≥ 3 words, glyph units joined), in page order; 9 natural texts and 3 devowelled ones (Latin, Italian, Spanish) as in C052; Timm–Schinner generator, default settings, 3,400 lines, seeds 551–555. Each text: two disjoint halves of 15,000 tokens in reading order.
- **Statistic:** cut the half into 115-token chunks (130). Eligible types: 15–150 occurrences in the half (at least 30 types, else NOT TESTABLE). B = mean over eligible types of log(variance/mean) of the type's per-chunk counts. Null: shuffle all tokens of the half, 200 times. Excess **D = B − mean(null B)**; p by rank (floor 1/201).
- **Gates:** FPR — 20 shuffled natural halves, p < 0.05 at most 2/20. Power — 20 shuffled natural halves with a planted clumping (20% of eligible types; 30% of each type's tokens moved into a random 10% of chunks), p < 0.05 at least 14/20. Failing gates → all NOT TESTABLE.
- **H1 (existence):** EXCESS if all four Voynich halves have p < 0.05/4; NO EXCESS if none; SPLIT otherwise.
- **H2 (natural placement)** and **H3 (generator placement, needs ≥ 6 halves):** D of the four Voynich halves against the min–max of the 24 natural halves / generator halves: ABOVE, BELOW, INSIDE or STRADDLE.
- **Reading rules fixed in advance:** clumping is *not* meaning; topic-like clumping is predicted by natural language, but can also come from section changes (the manuscript's halves cross herbal, astro, balneo pages) or from copying. A natural-like D would be one more feature the copying account must reproduce; a generator-like D would be consistent with copying. Neither reads a word.
- **Disclosure (before the full run):** a smoke test of the tool on IT2a half 1 with scratch seed 1 showed one number (D 0.34, with 50 shuffles). It revealed that 50 shuffles give a p floor (1/51) above the Bonferroni bar 0.0125, so the shuffle count was raised to 200 before this pre-registration; nothing else was changed. Seed for the run: 5555.
- **Tool:** `tools/c055_burstiness.py` → `analysis/C055_results.json`; `timeout 600`.

## Results (run 2, 10.4 s, seed 5555; `analysis/C055_results.json`, logs `c055_run1.log`, `c055_run2.log`)
**Fix after the first run, disclosed:** run 1 crashed in the power gate, before any verdict-bearing number, because five natural texts (Caesar, Descartes, Machiavelli, Genesis, Exodus) and devowelled Caesar have fewer than 30,000 tokens, so their second "half" was short. Fix: texts under 30,000 tokens contribute **one** 15,000-token half; gate draws use the first 15,000 tokens of each text (the gate halves are shuffled anyway); an untestable gate replicate counts as a miss. Same seed, rerun. Generator seed 551 gave 29,803 tokens (< 30,000) and was dropped by the rule, leaving 4 seeds / 8 halves (≥ 6 needed).

**Gates:** FPR **2/20**, power **14/20** — passed, but exactly on both bars, so the test is at the edge of its calibration.

| text | half | D | p |
|---|---|---|---|
| **ZL 3b** | 1 / 2 | **0.332 / 0.292** | 0.005 / 0.005 |
| **IT2a** | 1 / 2 | **0.340 / 0.293** | 0.005 / 0.005 |
| Latin Caesar / Descartes | 1 | 0.130 / 0.147 | 0.005 |
| Italian Dante | 1 / 2 | 0.093 / 0.079 | 0.005 |
| Italian Machiavelli | 1 | 0.181 | 0.005 |
| Spanish Cervantes | 1 / 2 | 0.286 / 0.176 | 0.005 |
| Hebrew Genesis / Exodus | 1 | 0.633 / 0.540 | 0.005 |
| Finnish Kalevala | 1 / 2 | 0.485 / 0.463 | 0.005 |
| Finnish Kivi | 1 / 2 | 0.239 / 0.269 | 0.005 |
| devowelled Caesar | 1 | 0.144 | 0.005 |
| devowelled Dante | 1 / 2 | 0.062 / 0.036 | 0.005 / 0.010 |
| devowelled Cervantes | 1 / 2 | 0.249 / 0.132 | 0.005 |
| generator seeds 552–555 | 8 halves | 0.494–0.613 | 0.005 |

**Verdicts:**
- **H1 EXCESS** — all four Voynich halves clump beyond shuffling (p 0.005 < 0.0125).
- **H2 INSIDE** natural (0.036–0.633). The natural range is wide (Dante lowest, Hebrew highest), so this placement is weak.
- **H3 BELOW the generator** (0.494–0.613 vs Voynich 0.29–0.34): the default copying generator clumps its words *more* than the manuscript does.

**Post-hoc sensitivity, not pre-registered** (`analysis/C055_posthoc_chunks.json`, 50 shuffles, seed 5556; ZL, generator seed 552 and Machiavelli only): the order generator > ZL > Machiavelli holds at chunk sizes 60 (0.33–0.37 / 0.18–0.21 / 0.12) and 230 (0.70–0.84 / 0.45–0.47 / 0.25).

**Reading (within the rules fixed in advance):** the manuscript's words clump, at a level natural texts span, and less than the default generator. This is one more feature the copying account must be tuned to (in the same direction as C054: the generator overdoes local re-use). It does not show topic or meaning: section changes inside the halves could also produce clumping, and that was not separated here. Caveat: the gates were met exactly at their bars.

**Next (F-BURST step 2):** separate section from clumping (within-section halves, herbal A only, against natural texts of the same length); generator settings that lower clumping — do they lower the R0 excess too (a shared knob)? Stronger gate design (more replicates) first.

**Outreach:** none (gates at the edge; one generator configuration).

**Audit note (added in C056):** under C056's stronger 40-replicate gate the same plant reached only 27/40 (block null), so this cycle's 14/20 power was marginal. The verdicts above stand as pre-registered, but treat them as resting on a barely calibrated test until a stronger plant (F-BURST step 3) reproduces them.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
