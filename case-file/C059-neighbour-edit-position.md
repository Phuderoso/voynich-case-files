# C059 — Expedição 59: onde mora a troca de um glifo? (F-NEIGH step 2)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Why:** [C058](C058-edit-neighbours.md) found that nearby Voynich words are one glyph apart more often than chunk vocabulary explains (EXCESS), at the level of the Timm–Schinner generator (INSIDE) and straddling natural text (only consonantal Hebrew comes near). Two accounts fit: copy-and-modify writing, or one-glyph affixes recurring locally. They predict different *places* for the change. This cycle asks whether the manuscript's excess changes the same word positions as the generator's.

## Pre-registration (pushed before any C059 number)
- **Classification:** for every focal token (≥ 3 units) whose nearest one-glyph neighbour (C058 definition, edit distance exactly 1) is among the 10 preceding tokens, the change is classed by unit position: **INITIAL** (first unit), **FINAL** (last unit), **MEDIAL** (other). For insertions/deletions the position is in the longer word; inside a run of identical units the first mismatching position is used (a fixed convention, same for every text).
- **Excess profile:** share_c = (obs_c − null_c) / (obs_total − null_total), null = mean over 100 shuffles inside 115-token chunks (C058's null). A text is **scored** only if its total excess has z ≥ 3 against the null spread (European texts had no excess in C058 and are expected to be unscored).
- **Gates (position recovery):** natural halves (C058 rotation) with copy-with-mutation planted at Q = 0.03 (fixed before running; C058 showed 1% is detectable, 3% gives a larger excess to apportion), only at the first unit (20 reps) or only at the last unit (20 reps). Recovered if the target share > 0.6; bar ≥ 16/20 for each. Failing either → NOT TESTABLE. (No FPR gate: the question is apportioning an excess already shown in C058, not detecting one.)
- **Data:** ZL 3b and IT2a, first two 15,000-token halves; controls as C058; generator default settings, seeds 551–557 (scored halves ≥ 6 needed).
- **H1:** for each class, the four Voynich shares against the range of the scored generator halves (ABOVE, BELOW, INSIDE, STRADDLE). **MATCH** if all three INSIDE; **DIFFERENT** if any class is ABOVE or BELOW; **PARTIAL** otherwise. Not testable if gates fail, any Voynich half is unscored, or < 6 generator halves are scored.
- **Descriptive (no verdict):** Hebrew and any other scored natural half.
- **Reading rules fixed in advance:** MATCH means the manuscript's local one-glyph changes sit where the generator puts them, so the self-citation account fits this statistic too. DIFFERENT means the generator changes words in other places than the manuscript does; a FINAL- or INITIAL-heavy Voynich profile would point to local affix alternation (as in Hebrew prefixes) rather than the generator's rule. Neither implies meaning.
- **Tool:** `tools/c059_neighbour_edit_position.py` → `analysis/C059_results.json`; seed 5959; `timeout 600`.

## Results
*(to be filled after the run)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
