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

## Results
*(to be filled after the run)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
