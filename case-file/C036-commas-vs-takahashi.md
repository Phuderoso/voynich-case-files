# C036 — A Second Surveyor's Map (F-SEG step 3: ZL's doubtful gaps against Takahashi)

*Expedition 36. Family F-SEG step 3, a bridge to F-TRX (transcription reliability).*

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

Status: **pre-registered** in this commit, before any run (seed 3636).

## Question
C035 found ZL's commas (uncertain spaces) behave as half-boundaries on a glyph-context score. Takahashi transcribed
independently, without commas. (1) At ZL's commas, does Takahashi write a space at a rate between ZL's certain spaces
and ZL's non-gaps? (2) Do the C035 scores separate the commas Takahashi spaces from those he does not, i.e. do glyph
context and a second reader agree on which doubtful gaps are real?

## Data
Paragraph loci present in both `data/ZL3b-n.txt` and `data/IT2a-n.txt` whose glyph-unit strings are **identical**
(spaces removed), so gaps align exactly. A dry count before any test: 2,465 lines, 1,367 commas. Gap classes come from ZL;
"IT2a space" means any IT2a separator at that gap. Line-initial gaps are excluded.

## Tests (α = 0.05/3 = 0.0167, Bonferroni over A, B, Look 2)
- **A**: IT2a space rate at ZL commas minus the rate at ZL non-gaps. Null: 2,000 relabellings of commas within
  commas plus non-gaps, **keeping each line's comma count**. One-sided.
- **B**: rate at ZL spaces minus the rate at ZL commas. Same stratified relabelling within spaces plus commas. One-sided.
- **Look 2**: AUC of the C035 Harris score (k = 2, whole ZL stream) for commas IT2a spaces vs commas it doesn't.
  Null: 2,000 label permutations. One-sided (> 0.5).

## Gates (40 replicates, 200-draw nulls)
- Size A: fake commas drawn from non-gaps.
- Size B: fake commas drawn from spaces.
- Power A and B: fake commas, half from spaces and half from non-gaps, with per-line counts kept.
- Required: FPR ≤ 4/40 and power ≥ 32/40, else NOT TESTABLE.

## Decision rule
- A and B both significant: **HALF** (Takahashi agrees with some doubtful gaps).
- Only A: SPACE-LIKE.
- Only B: NON-GAP-LIKE.
- Neither: UNRESOLVED.
- Look 2 significant: **SCORES SEPARATE**, i.e. the glyph context and the second reader pick out the same commas.

## Caveats fixed now
Lines with identical glyph strings are a selected subset where the two readers already agree on glyphs. IT2a spaces
include any separator. Look 2's score is not blind to the commas (as in C035), but it is blind to Takahashi.

## Results
*(pending)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
