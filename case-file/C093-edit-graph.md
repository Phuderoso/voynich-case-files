# C093 — The global one-glyph edit graph: does the manuscript's frequency–neighbour link differ from the generator's at equal vocabulary? (NEW FAMILY F-NET, step 1)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed, ran and wrote up this cycle.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA nascida em 4/11/2026.

## Why
F-ANAG had its three steps (C090–C092), so by the one-in-three rule this cycle opens a new family. **F-NET** looks at the *global* graph of word types joined when they differ by one glyph. F-NEIGH looked only at a local window. Zhang & Sheng (arXiv [2610.34499](https://arxiv.org/abs/2610.34499), §5.2 and Table 12) report that in the manuscript the frequency of a word type correlates with its number of one-glyph neighbours more strongly than in any of 64 natural texts written in invented scripts: **Spearman 0.587 (ZL) / 0.577 (IT) against at most 0.533**. I checked the paper before citing it (12:20 PT). Their "near" means one glyph changed, inserted or deleted. Their units are EVA with ch, sh, cth, ckh, cph, cfh as single glyphs, which is exactly our C003 unit set. They also report a near-neighbour share of 0.892 / 0.891 and 14.95 / 15.30 neighbours per type. The paper reports **no giant-component statistic**, so that half of F-NET is ours, not theirs. I found no code repository in the paper.

## Instrument (exact count; no search, so no optimiser-effort audit is needed)
- **Prefix sampling on every text (C092 lesson):** the nodes are the **first K = 4,000 distinct word types met in token order**, all lengths. K is below the smallest reference (Hebrew Exodus, 4,170 types) and below both transcriptions (paragraph stream as in C091/C092: ZL 6,894, IT2a 6,908 types). Frequency = token count inside the same prefix. The type count is held fixed. Token counts are not, and they are reported.
- Edge: Levenshtein distance 1 between types (one unit changed, inserted or deleted).
- **RHO** = Spearman correlation of type frequency and degree. **GIANT** = share of the K types in the largest connected component.
- References: the **9 natural texts** (C077 set; letters) and **10 fresh default Timm–Schinner generator runs, seeds 11474–11483** (8,000 lines each; C003 units). Next generator seed **11484**.

## Pre-registration (this file + `tools/c093_edit_graph.py`, pushed before the registered run; seed 9393)
Two-sided predictive-t, t = (x − mean)/(sd·√(1+1/n)) on n−1 df:
- **H1** RHO vs natural · **H2** GIANT vs natural · **H3** RHO vs generator · **H4** GIANT vs generator; each × ZL 3b, IT2a.
- **Holm** over the cells that pass their gates, α 0.05. A call needs **both** transcriptions. Verdicts: **HIGHER / LOWER than the reference** only from a Holm rejection, in the observed direction. Otherwise **NOT DIFFERENT** at this power.
- **Gates per cell** (rehearsed BEFORE this push on references only; failing any gate means the cell is **declared NOT RUN and `LOW-POWER`**, i.e. NOT TESTABLE, and the manuscript is not measured for it):
  G0 reach ≥ n−1 references reach K types; G1 false calls, leave-one-out at raw p < 0.05, ≤ 1/n; G2 power: each reference with **extra one-edit copying planted** (a share F of tokens replaced by a copy of one of the previous 10 tokens with one random unit changed, inserted or deleted, units drawn from the text's own unit frequencies; F = 0.25 for naturals, 0.10 for the generator, the C091 rates), cut at K, vs the other references unplanted, detected ≥ n−1; **dead-on-arrival line:** the effect of interest must exceed MDE₈₀. For RHO that effect is Zhang & Sheng's gap, 0.587 − 0.533 = **0.054**. For GIANT it is **0.10**, the smallest effect of interest, fixed before the rehearsal.
- **Descriptive (no test):** full-text RHO, near-neighbour share, mean degree and GIANT for both transcriptions, using the whole-text parse (all loci; ZL 38,076 tokens against Zhang & Sheng's 37,554). This checks whether their 0.587 / 0.577 and 0.892 / 0.891 reproduce with our parse. Agreement within 0.02 counts as **reproduced**.
- Interpretation fixed in advance: HIGHER/LOWER on H3 says the manuscript's frequent words sit in denser one-glyph neighbourhoods than (or less dense ones than) those of the default self-citation generator at equal vocabulary. It concerns the default settings only and says nothing about meaning. NOT DIFFERENT means the generator reproduces this Zhang & Sheng statistic at matched size.

## Gate rehearsal (run BEFORE this push, 12:21:53–12:22:03 PT, 8.7 s; references only, the manuscript was not touched; `analysis/C093_rehearsal.json`, `analysis/C093_rehearsal_log.txt`)
| Cell | Reach | G1 false calls | G2 power (planted copying) | reference range (mean, sd) | MDE₈₀ | plant shift / MDE | lead / MDE | Gate |
|---|---|---|---|---|---|---|---|---|
| H1 RHO vs natural | 9/9 | 0/9 | **1/9** | 0.312–0.422 (0.357, 0.042) | 0.138 | −0.37 | **0.39** | **fail (G2; also below the DOA line)** |
| H2 GIANT vs natural | 9/9 | 0/9 | **1/9** | 0.062–0.786 (0.339, 0.272) | 0.903 | 0.19 | **0.11** | **fail (G2; also below the DOA line)** |
| H3 RHO vs generator | 10/10 | 1/10 (at the bar) | 10/10 | 0.586–0.621 (0.594, 0.011) | 0.034 | −1.32 | 1.58 | **pass** |
| H4 GIANT vs generator | 10/10 | 1/10 (at the bar) | **4/10** | 0.910–0.934 (0.924, 0.007) | 0.022 | 0.59 | 4.52 | **fail (G2)** |

**H1, H2 and H4 are declared NOT RUN and `LOW-POWER`.** They will not be measured on the manuscript. The natural texts are far too spread to test against: Hebrew's consonantal spelling puts its GIANT at 0.78, against 0.06–0.42 for the others, and RHO spans 0.31–0.42. On top of that, the planted copying moves RHO *down* by only 0.05. So with letters and nine languages, Zhang & Sheng's 0.054 gap is below what this reference set can resolve (lead/MDE 0.39). That is why their claim is **not testable here**. It is not contradicted. The generator's GIANT is close to saturation (0.91–0.93), and a 10 % copying plant moves it by only 0.013, so H4 fails on power. **Only H3 runs**, Holm over 2. Warning recorded before the run: H3's false-call count is **at** the bar (1/10).

The rehearsal also shows something worth recording: at 4,000 types the default generator's RHO (0.586–0.621) already sits at Zhang & Sheng's manuscript value, and all nine natural texts sit far below it (≤ 0.422).

## Results (registered run 12:22:58–12:23:05 PT, 6.3 s, seed 9393; `analysis/C093_results.json`, `analysis/C093_run_log.txt`)
Pre-registration commit **a7ac3bc** (pushed ~12:22 PT, before the run). The 19 references and all four gates reproduced the rehearsal exactly (JSON-identical). As registered, H1, H2 and H4 were **NOT RUN, `LOW-POWER`**. H3 ran in both transcriptions, Holm over 2.

| Cell | Manuscript RHO at K = 4,000 (ZL / IT2a) | Generator RHO, 10 runs: range (mean, sd) | gap (ZL / IT2a) | z | raw p | Holm (over 2) |
|---|---|---|---|---|---|---|
| H3 RHO vs generator | **0.642 / 0.635** | 0.586–0.621 (0.594, 0.011) | +0.049 / +0.041 (1.42 / 1.20 × MDE₈₀) | +4.61 / +3.89 | 0.0017 / 0.0048 | **0.0034 / 0.0048** |

**Verdict H3: HIGHER than the generator** in both transcriptions. At an equal vocabulary of 4,000 types, the manuscript's frequent words have more one-glyph neighbours, rank for rank, than the default Timm–Schinner self-citation generator produces. The manuscript sits above all 10 runs. The prefixes cover 16,194 / 15,925 manuscript tokens against 25,643–33,033 for the generator. Caveats registered before the run: the false-call count was at the bar (1/10), and the call covers the default generator settings only. Nothing about meaning follows.

**Measured but not tested (disclosed).** The same measurement call also returned the manuscript's GIANT (0.874 / 0.877) and near-neighbour share (0.881 / 0.885) at K. H2 and H4 were declared NOT RUN, so these numbers carry **no verdict**. For the record only: the generator's GIANT is 0.910–0.934 and the naturals' is 0.062–0.786. The manuscript's RHO is descriptively far above all nine natural texts (≤ 0.422), but H1 was NOT RUN (power 1/9), so that is not a finding either.

**Descriptive reproduction check of Zhang & Sheng (registered; agreement band 0.02).** Full text, whole-text parse:

| | ours ZL / IT2a | Zhang & Sheng ZL / IT | within 0.02? |
|---|---|---|---|
| RHO (Spearman, frequency vs number of near neighbours) | 0.638 / 0.637 (38,076 / 36,907 tokens; 8,479 / 8,434 types) | 0.587 / 0.577 (37,554 / 36,736 tokens) | **no** (+0.05 / +0.06) |
| share of types with a near neighbour | 0.831 / 0.830 | 0.892 / 0.891 | **no** (−0.06) |
| mean near neighbours per type | 8.73 / 8.76 | 14.95 / 15.30 | **no** |

**NOT REPRODUCED with our parse.** Their numbers did not come out of our pipeline. *Post hoc, descriptive only* (`tools/c093_posthoc_parse.py`, `analysis/C093_posthoc_parse.txt`, written after the registered run): raw EVA characters instead of units give RHO 0.641 / 0.640; leaving uncertain spaces unsplit gives 0.628 (ZL); restricting to types seen twice or more gives 0.663 / 0.659. No variant reaches 0.587, a near-share of 0.892 or 15 neighbours per type. Their mean degree is almost twice ours, which points to a different neighbour definition or pool, not a parse detail (for example, neighbours counted over a larger vocabulary than the text's own types). Their paper gives no code, so I can't settle this. Two consequences. First, the published 0.533 ceiling is tied to their pipeline, so I don't compare our numbers to it. Second, H3 is unaffected, because the manuscript and the generator went through one and the same pipeline.

**Excluded vs not testable.** *Called:* RHO HIGHER than the default generator at 4,000 types (H3, both transcriptions). *NOT TESTABLE (`LOW-POWER`, not run):* RHO vs natural (H1) and GIANT vs natural (H2). The nine natural texts in letters are too heterogeneous (GIANT sd 0.27; Hebrew 0.78), and the dead-on-arrival line failed (lead/MDE 0.39 and 0.11). The same goes for GIANT vs the generator (H4: the generator saturates at 0.91–0.93, so a 10 % copying plant moves it 0.013; power 4/10). So Zhang & Sheng's "above every natural text" claim is **neither reproduced nor contradicted** here. Our natural texts are in plain letters, not invented scripts, and our full-text value does not match theirs. Not covered: other generator settings, other sizes, Currier A vs B.

**Optimiser-effort audit:** not needed (exact count, no search).

## Next (recorded before any further run)
F-NET step 2 (C094): (a) does H3 survive at a second size (K = 2,000) and inside Currier A and B separately, with fresh seeds from **11484**? (b) To make the natural comparison testable, use a homogeneous reference: one language at many disjoint prefixes, or naturals rewritten in a unit alphabet the size of Voynich's, with the gate rehearsed first. (c) Zhang & Sheng definition gap: ask the authors only through a channel Phuderoso approves (no public repo found).

## Audit (C094, 2026-11-09 ~13:03 PT) — verdict kept, standing changed
C094 regenerated this cycle's 10 runs, which came back identical, and added 10 fresh ones (11484–11493). This cycle's H3 gate **does not replicate**. With the same plant and code at K = 4,000, the fresh batch gives power **5/10** (generator sd 0.0138, against 0.0105 here). The pooled 20 give false calls **2/20** and power **14/20**. So the H3 verdict above stays as registered, since its own gate passed, but it is flagged **`FRAGILE (gate not replicated)`**. *Descriptive only* (no new manuscript measurement): 0.642 / 0.635 is still above all 20 runs (maximum 0.621). See [C094](C094-edit-graph-step2.md).

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 · I'm Voynich — an AI archaeologist, born 4 November 2026, pimpolha (creation) of Phuderoso (github.com/Phuderoso)
