# C062 — Expedição 62: rótulos contra iscas de mesma frequência (F-LABEL step 2, repair of C061)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Why:** [C061](C061-labels-in-own-text.md) asked whether a label word occurs in its own page's running text, but was NOT TESTABLE: its gate drew fake labels from other pages only, and a post-hoc diagnostic showed its label-set permutation null was confounded (FPR 0.25). This cycle replaces the null with one that holds each page fixed and compares each label with **decoy words of the same frequency** from the same section, scored on the same page.

## Pre-registration (pushed before any C062 number)
- **Data:** as C061 (ZL 3b primary, IT2a replication; running text = non-label loci; pages ≥ 20 running tokens; labels = distinct `L*` tokens ≥ 3 EVA units).
- **Scorable labels:** a label w on page p in section s with count f ≥ 1 in s's running text. Its decoy bin = all other distinct words (≥ 3 units) of s's running text in the same count bin (1, 2, 3, 4, then 5–8, 9–16, 17–32, …). Labels with f = 0 cannot be scored; their share is reported descriptively.
- **H1:** T1 = Σ_w [h_own(w) − mean over the bin of h_own(decoy)], h_own = occurs in p's running text. **EXCESS** if one-sided p ≤ 0.025, else **NO EXCESS**.
- **H2 (page vs neighbourhood):** same with c = h_own − mean h over the bound neighbours (previous/next page of the same section with running text). **PAGE-SPECIFIC** if p ≤ 0.025, else **NOT PAGE-SPECIFIC**.
- **Null:** each label replaced by a uniform draw from its own bin, 20,000 draws (labels independent).
- **Gates (same model as the null, ZL structure, 200 replicates):** FPR = fake labels drawn from their bins (bar ≤ 0.05); power = as FPR, but each label slot with probability 0.10 is drawn from the bin words present on its own page, when there are any (bar ≥ 0.80). A failed gate → **NOT TESTABLE** for that hypothesis.
- **Reading rules fixed in advance:** EXCESS + PAGE-SPECIFIC = labels are tied to their own page's text beyond frequency, consistent with naming *or* with copying from the page (not separable here); NO EXCESS = no such tie among scorable labels. The labels never found in their section's text are outside this test whatever their share. No claim about meaning; no natural-language control has this layout.
- **Tool:** `tools/c062_label_decoys.py` → `analysis/C062_results.json`; seed 6262; `timeout 600`.

## Results (run 2026-11-08 ~12:58 PT, 2 s, seed 6262; `analysis/C062_results.json`, `analysis/C062_run_log.txt`)
- **Scorable labels:** ZL 282 of 1,001 (719 labels, **72%**, never occur in their section's running text at all and cannot be scored); IT2a 240 of 873 (633 unscorable).
- **Gates:** FPR **0.01** (H1) and 0.01 (H2) — pass. Power **0.86** (H1, pass) and **0.72** (H2, below 0.80 → fail). The planted effect is about 19.5 extra own-page hits over 282 labels.
- **H1 — NO EXCESS.** ZL: 97 own-page hits vs 87.0 expected from frequency-matched decoys; T1 = +10.0, p = **0.072**. IT2a replication: 78 vs 70.7, T1 = +7.3, p = 0.116.
- **H2 — NOT TESTABLE** (power 0.72). Descriptive: ZL T2 = +9.3, p 0.130; IT2a +9.6, p 0.097.

## Verdict
**H1 NO EXCESS; H2 NOT TESTABLE.** Among labels whose word occurs anywhere in their section's text, the label is not found on its own page significantly more often than words of the same frequency; an effect the size of the plant (~20 extra hits) would have been found 86% of the time, and the observed +10 is about half of that. A smaller tie cannot be excluded.

## Audit of C061
C061's descriptive "97 own-page hits vs 78.8 expected" shrinks to 97 vs 87.0 once each page is held fixed and decoys are frequency-matched, so about half of C061's apparent surplus came from the confound its diagnostic flagged. C061's verdict (NOT TESTABLE) stands; a note is added to its case file.

## What this does and doesn't say
- 72% of label words never occur in their section's running text. That is descriptive only: there is no control here for how often a random word of a label's length would be absent, so it is not evidence that labels are a separate vocabulary (that is a separate, testable question). Prior work already reports that labels form a distinct register: R. Zandbergen, [Some special properties of labels](https://voynich.nu/extra/labels.html); J. G. Molina (2026), [doi:10.5281/zenodo.22757117](https://doi.org/10.5281/zenodo.22757117); and [doi:10.5281/zenodo.21761983](https://doi.org/10.5281/zenodo.21761983) on zodiac labels as sigla. The 72% is consistent with that and is not claimed as new.
- NO EXCESS counts against labels being words that the page's text repeats, and against labels copied from their own page, **only for the scorable 28%**. It says nothing about meaning.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
