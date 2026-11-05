# C035 — The Doubtful Gaps (F-SEG step 2: are ZL's uncertain spaces half-boundaries?)

*Expedition 35. Family F-SEG, step 2.*

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

Status: **pre-registered** in this commit, before any run (seed 3535).

## Question
ZL 3b marks gaps the transcriber was unsure of with a comma (`,`), and certain spaces with `.`. Rozanova & Temerev
(arXiv 2608.17096) found that uncertain spaces are physically narrower on the page. On the text-only Harris score of C034 (k = 2,
spaces removed), are commas **between** certain spaces and non-gaps, i.e. half-boundaries? Or do they behave like
full spaces, or like no gap at all?

## Data
`data/ZL3b-n.txt`, paragraph loci, all lines (C030 rules, `<->` as `.`), EVA glyph units. Gap classes: none (inside
a word), space (`.`), comma (`,`). Line-initial positions are excluded. Expected counts: about 118k none, 27.6k spaces, 2.4k commas.

## Tests (α = 0.05 / 2 = 0.025, Bonferroni)
- **A**: AUC of the score for commas vs non-gaps. Null: 1,000 relabellings of the same number of positions within commas plus non-gaps; one-sided.
- **B**: AUC for certain spaces vs commas. Null: same relabelling within spaces plus commas; one-sided.

## Gates (40 replicates each, 200-draw null)
- Size A: fake commas drawn from non-gaps.
- Size B: fake commas drawn from spaces.
- Power A and B: fake commas made of half real spaces and half non-gaps (a planted half-boundary).
- Required: FPR ≤ 4/40 and power ≥ 32/40, else NOT TESTABLE.

## Decision rule
- A and B both significant: **HALF-BOUNDARIES**.
- Only A: **SPACE-LIKE**.
- Only B: **NON-BOUNDARIES**.
- Neither: UNRESOLVED.

AUCs are reported with the certain-space vs non-gap AUC for scale.

## Caveats fixed now
The score is estimated on the whole stream, commas included, so it is not blind to them. It is a property of glyph context only,
not of ink. Commas are one transcriber's judgement.

## Results
*(pending)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
