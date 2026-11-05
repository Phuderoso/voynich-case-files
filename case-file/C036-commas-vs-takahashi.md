# C036 — A Second Surveyor's Map (F-SEG step 3: ZL's doubtful gaps against Takahashi)

*Expedition 36. Family F-SEG step 3, a bridge to F-TRX (transcription reliability).*

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

Status: pre-registered in commit 3dbc4825 before any run (seed 3636); results added after.

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

## Results (`analysis/C036_results.json`, 155 s)
There are 3,990 common loci, of which 2,465 have identical glyph strings. In those lines: 1,367 commas, 15,932 spaces and 68,510 non-gaps.
Gates pass: FPR A 0/40 and B 0/40, power A 40/40 and B 40/40.

| Where ZL has | Takahashi writes a space |
|---|---|
| a certain space (`.`) | **99.6 %** |
| an uncertain space (`,`) | **65.0 %** |
| no gap | **0.4 %** |

- A (commas minus non-gaps): +0.647, p 0.0005.
- B (spaces minus commas): +0.346, p 0.0005.
- **Verdict: HALF.** A second, independent reader agrees with about two in three of ZL's doubtful gaps. On certain spaces and non-gaps the two readers almost never disagree.
- **Look 2: SCORES SEPARATE.** The C035 glyph-context score is higher at the 889 commas Takahashi spaces than at the 478 he doesn't
  (AUC 0.652, p 0.0005). Two independent kinds of evidence, the glyph stream and a second human eye, point at the same doubtful gaps.

## Audit of C035
C035's mixing-model figure (about 89 % of commas space-like) was model-based and descriptive. The second reader gives 65 %.
The two measure different things: glyph-context similarity vs a reader's decision. But the 89 % should not be read as
"89 % of commas are real spaces". A note has been added to C035.

## Caveats
Only lines where both readers agree on every glyph (62 % of common loci) are used; agreement on glyphs may go with
agreement on gaps. Takahashi's choice is itself a reading. The score is not blind to ZL's commas.

## What this gives
A practical rule: a doubtful gap with a high glyph-context score is more likely a real break. Look 2's AUC of 0.65
means a weak but real resolver, not a classifier. The next step is to check it on the images, whether gap width at commas tracks the
score, using the Beinecke scans as in Rozanova & Temerev.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
