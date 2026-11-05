# C035 — The Doubtful Gaps (F-SEG step 2: are ZL's uncertain spaces half-boundaries?)

*Expedition 35. Family F-SEG, step 2.*

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

Status: pre-registered in commit 4e56395e before any run (seed 3535); results added after.

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

## Results (`analysis/C035_results.json`, 13 s)
**Run note:** run 1 crashed before computing anything (a boolean index of the wrong length in `auc_groups`). The fix
changes no analysis choice (marked in the code). Run 2 is the result.

Gaps: 118,045 none, 27,647 spaces and 2,386 commas (line-initial positions excluded).
Gates pass: FPR A 2/40, FPR B 0/40, power A 40/40, power B 40/40.

| Comparison | AUC | p (1,000 relabellings) |
|---|---|---|
| A: commas vs non-gaps | **0.831** | 0.001 |
| B: certain spaces vs commas | **0.560** | 0.001 |
| (scale) certain spaces vs non-gaps | 0.873 | — |

**Verdict (pre-registered rule): HALF-BOUNDARIES.** Both tests are significant at α 0.025. But the commas sit much
closer to full spaces than to non-gaps. As a rough descriptive reading (assuming commas are a mix of fraction f
true-space-like gaps and 1 − f word-internal gaps, which is a model, not a test), f ≈ (0.831 − 0.5)/(0.873 − 0.5) ≈ 0.89.
In glyph context, most of the transcriber's doubtful gaps look like real word breaks. A minority, or all of them to a lesser degree, do
not, which the text alone cannot tell apart.

This fits Rozanova & Temerev's physical finding: uncertain spaces are narrower on the page. Here they are also somewhat
weaker breaks in the glyph stream, and a half-planted mixture would have been seen (power 40/40).

## Audit note (added after C036)
In the lines both transcriptions agree on, Takahashi writes a space at **65 %** of ZL commas (C036). The 89 % figure above is a
glyph-context mixing model, not a count of real spaces; read it as "commas look mostly like spaces in glyph context", not
as "89 % are spaces".

## Caveats
The score is estimated on the whole stream, commas included. Commas are one transcriber's judgement. The f ≈ 0.89 is
model-based and descriptive. ZL only, since IT2a has no commas (0 in paragraph text).

## Next
Check commas against Takahashi at the same loci: where ZL doubts a gap, does IT2a write a space? That needs a locus
alignment, and is a candidate F-TRX/F-SEG bridge.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
