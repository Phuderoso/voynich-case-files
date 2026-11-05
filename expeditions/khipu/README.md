# Expedition 2 · Inka khipu

A parallel dig to the Voynich trench: exact, test-first analysis of Inka khipus from the
[Open Khipu Repository](https://github.com/khipulab/open-khipu-repository) (OKR). Why khipu: see [TRIAGE.md](../TRIAGE.md).

Method is the same as the main repo: pre-register hypothesis, metric and decision rule; calibrate every null;
plant controls; correct for multiple comparisons; say "not testable" when power is low; publish negatives.
**No decipherment is claimed.**

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Layout
`case-file/` pre-registered cases with results · `journal/` field notes · `tools/` re-runnable code ·
`analysis/` raw JSON · `data/` manifest with source commit and hash.

## Coverage table
| Cycle | Approach family | Question | Data | Result |
|---|---|---|---|---|
| K001 | Exact arithmetic (adjacent sum cords), within-khipu permutation and group-order nulls, BH-FDR | Do sum cords beat a calibrated null? | OKR `khipu.db` @ `4039ca5` | Null calibrated (FPR 0.022). 10 of 457 khipus significant at K = 5000 (amendment after a p-floor problem at K = 500); none across group boundaries. Replication of known structure; detector power only 38%. [K001](case-file/K001-adjacent-sum-cords.md) |
| K002 | Detector design: log-weighted exact sums, blind dev/eval split on planted controls, two-stage Monte Carlo, BH-FDR | Can a sharper detector reach 80% planted recovery? | OKR `khipu.db` @ `4039ca5` | **Target missed**: recovery 0.37 to 0.63 (FPR 0.026), no gain on long sums. Corpus: 16 of 457 significant (all 10 of K001 + 6 new, first non-UR: AS026A). UR excess confounded by size. [K002](case-file/K002-sharper-sum-detector.md) |
| K003 | Min-p combination of per-k calibrated scores; blind dev/eval on short and long plants; size-stratified permutation | Can combining windows reach the power target? Is the UR excess size? | OKR `khipu.db` @ `4039ca5` | **Target missed** (spec A 0.66, spec B 0.59, FPR 0.046), best detector so far on long sums. Corpus: 20 of 457 significant; K001's 10 flagged by all three detectors. UR excess **not supported** after size matching (p = 0.175). K002's size argument corrected. [K003](case-file/K003-combined-window-detector.md) |
| K004 | Hierarchy arithmetic (pendant = sum of its own subsidiaries); two within-khipu permutation nulls; calibration + planted controls; BH-FDR | Do pendants record their subsidiaries' sum? | OKR `khipu.db` @ `4039ca5` | **Yes, corpus-wide** (25 hits vs 7.1 expected, p ≤ 0.0001, both nulls), but concentrated in **KH0349/UR113** (13 hits, BH-significant). Power 0.99, so the other 99 testable khipus are a real negative. Without UR113: p = 0.019 (suggestive). No overlap with adjacent-sum khipus. [K004](case-file/K004-subsidiary-sums.md) |
| K005 | Cross-khipu shared value runs; within-khipu permutation null; max-statistic FWER over 104 196 pairs; calibration + planted copies | Do different khipus share long identical value runs? | OKR `khipu.db` @ `4039ca5` | 5 pairs significant, all explained: an unflagged double recording (KH0140/KH0483), a catalogued similar pair (KH0362/KH0049), a Puruchuco pair, a related Berlin pair, and one null artefact (runs of 10s). Power for 6-cord copies only 0.11, so short matches are not testable yet. [K005](case-file/K005-cross-khipu-matches.md) |
| K006 | Cross-khipu runs with a run-preserving null and a composition-aware score; FWER; calibration + planted copies | Does K005 survive a fairer null, and can short matches be tested? | OKR `khipu.db` @ `4039ca5` | K005's UR047/UR211 flag confirmed as a null artefact; other four pairs survive, plus one more Puruchuco pair (UR067/UR066). Power for 6-cord copies 0.23 (target 0.5 missed), so short matches stay not testable. [K006](case-file/K006-run-preserving-cross-khipu.md) |
| K007 | Exact decoding audit of `knot_value_type` against seven decimal rules; planted violations | Do the knot values follow the decimal rules, and is our cord value safe? | OKR `khipu.db` @ `4039ca5` | S knots and cluster places consistent (under 0.1%); E/L knots slightly inconsistent (1.1%, 2.2%). **9.7% of our pendants (224 khipus) carry multi-number patterns** that our plain sum flattens: a caveat for K001–K006, with sensitivity reruns opened as line 8. [K007](case-file/K007-decoding-audit.md) |
| K008 | Sensitivity rerun: multi-number (R5) cords masked in place; structure-preserving masked nulls; BH-FDR; calibration + planted | Do K001 and K004 survive without cords that carry two numbers? | OKR `khipu.db` @ `4039ca5` | **K001: 8 of 10 survive**; KH0491 (UR255) and KH0507 (UR270) drop below the BH bar (not established, not excluded); 24 khipus not testable. **K004 robust** (24 hits vs 5.7, p ≤ 0.0001); UR113 untouched; without UR113 p = 0.006, meeting the rule but a re-analysis of the same hits, not a replication. [K008](case-file/K008-multinumber-sensitivity.md) |

## Open investigative lines
1. **Sharper sum detector** (advanced in K002 and K003, not closed): best is D5, min-p over per-k scores (spec A 0.66, spec B 0.59). Short-sum power is the gap; large khipus have the lowest power. Possible next step: exact chance probability per hit instead of log-weights.
2. **Cross-group sums on KH0359 and KH0405**: nominal under the group-order null; test with a targeted pre-registered rule.
3. **Cross-khipu exact matches**: identical or summing value sequences between different khipus (e.g. UR267A vs. UR267B), with a calibrated null for chance matches. **Advanced in K005:** long shared runs found and explained; **K006:** a run-preserving null removed K005's one artefact; long matches are mapped (all known or within the Puruchuco set); short matches not testable (power 0.23). Next: exact per-pair probabilities with BH.
4. **Decoding audit**: compare `knot_value_type` against knot type, count and position to find likely recording or place-value errors (could become an OKR data-quality issue). **Advanced in K007:** S knots and places consistent; E/L knots 1.1% and 2.2% inconsistent (examples in `analysis/k007_results.json`); possible OKR note after manual checks.
5. ~~Why mostly UR-series?~~ **Closed in K003, not supported**: size-matched permutation p = 0.175 (not excluded as a convention; the corpus can't separate it from size).
6. **Colour and value**: does cord colour predict which cords are sums? Needs a structure-preserving null.
7. **Subsidiary-to-parent sums**: **answered in K004** (yes corpus-wide, concentrated in UR113; real negative elsewhere). Follow-up: deeper levels (subsidiaries of subsidiaries) and a pre-registered replication of the non-UR113 signal on a held-out set. **K008:** robust to masking multi-number cords; non-UR113 p 0.019 → 0.006 (same data, so replication still owed).
8. **Multi-number cords (from K007)**: rerun K001–K006 with the 2 437 pendants that have more than one units cluster or out-of-order places excluded (or split into separate numbers), and report whether any result changes. **Advanced in K008:** K001 (8 of 10 survive) and K004 (robust) done; K002, K003, K005 and K006 still to rerun.

## Outreach log
None submitted yet (K001 to K004: no result new enough to share with OKR; UR113 is already well studied). K005: a data-quality issue for [khipulab/open-khipu-repository](https://github.com/khipulab/open-khipu-repository) about the unflagged double recording KH0140/KH0483 is drafted and awaiting submission. K008: the issue was prepared and raised for submission on the connector; it still needs to be confirmed before it appears on GitHub.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
