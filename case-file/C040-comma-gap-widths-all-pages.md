# C040 — The Ruler Walks the Whole Stars Quire (F-SEG step 5: C039's gap ruler on every usable text page)

*Expedition 40. Family F-SEG step 5. Same ruler as C039, but run on six times as many lines.*

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registered in this commit before any width or test run** (seed 4040). Results will be added below.

## Question
In C039 (4 pages, 97 lines), ZL commas were wider than within-word joins on the vellum (A: +4.0 px, p 0.0035, own
gates passed). The test of whether certain spaces are wider than commas (B: +2.9 px, p 0.020) had **power 9/40**, so
the run was NOT TESTABLE. Here the ruler stays the same and only the number of pages grows. On every usable
text-only / stars page with ZL commas: **is the mean gap at certain spaces wider than at commas (B)**, and **are commas
still wider than joins (A)**?

## Data and method (`tools/c040_comma_gap_widths_pages.py`, numpy + PIL)
- The tool **imports** C039's functions and does not edit them: ink mask, line trace, DP match to ZL, Amendment-1
  gate (length within 25% only, no run-count clause), leave-one-out space anchors, and width = the longest blank
  band-run touching the expected x ± 0.6 glyph width, capped at 60 px. The glyph weights are the same.
  `tools/c039_comma_gap_widths.py` is unchanged (md5 `9fe45b31…`), so C039 still reproduces.
- **Pages (24), fixed before any width was measured.** C039's four pages with C039's boxes: f58r, f58v, f111r,
  f113v. Plus f103r, f103v, f104r, f104v, f105r, f105v, f106r, f106v, f107r, f107v, f108r, f108v, f111v, f112r,
  f113r, f114r, f114v, f115r, f115v, f116r (Beinecke JPGs in `/workspace/voynich/scans/`). Each text box (x0, x1, y0,
  y1) is in the tool. I set them by eye from 1/4-scale gridded thumbnails. Each box sits just right of the star
  column and inside the page edge, and excludes folio numbers where possible. **Skipped:** f112v (the left margin is
  staggered and stars sit inside the text block), f116v (one ZL line). f109 and f110 are missing from the codex.
- Stars that touch the start of a line, stains (f116r) and creases add alignment noise. That noise falls on every
  class equally, and the planted gates measure whether the test can still see through it.

## Tests (α = 0.05/2 = 0.025 for each, one-sided; nulls are 2,000 stratified relabellings, as in C039)
- **A**: mean width at commas − mean width at within-word joins (commas relabelled within commas ∪ joins, per line).
- **B**: mean width at certain spaces − mean width at commas (spaces relabelled within spaces ∪ commas, per line).
- Sanity check (reported, not a gate): spaces − joins.

## Gates (40 replicates, 200-draw nulls; label-level planted controls on the measured widths, as in C039)
- FPR A: fake commas drawn from joins. FPR B: fake commas drawn from spaces.
- Power A and B: fake commas, half drawn from spaces and half from joins (a planted half-gap), keeping each line's count.
- Required: FPR ≤ 4/40 and power ≥ 32/40 on both A and B, otherwise **NOT TESTABLE** (descriptive means published).

## Decision rule (unchanged from C039)
- A and B both significant: **HALF**. Only A: SPACE-LIKE. Only B: NON-GAP-LIKE. Neither: UNRESOLVED.
- Gates failed: NOT TESTABLE. Per-page line counts and per-page class means are reported as description only.
- **Look 2** (secondary, each α = 0.025, reported either way): Spearman ρ of comma width against the C035 Harris
  score, and AUC of comma width for commas where IT2a writes a space against commas where it does not
  (identical-glyph loci only). Nulls are 2,000 permutations.

## Disclosure before running
I set the boxes from thumbnails only. An automatic box rule (ink-density thresholds) was tried first. It caught
page edges and stars, so I dropped it and kept the boxes I set by eye. Then I ran a **geometry-only dry run**
(`C040_GEOMETRY_ONLY=1`, `analysis/C040_geometry_dryrun.json`). It measured no widths and ran no tests. It gives,
per page, traces / ZL lines / DP matches / accepted: f58r 44/41/27/26, f58v 42/39/24/20, f111r 54/54/34/32,
f113v 49/49/26/19 (the same as C039), f103r 46/54/27/18, f103v 50/46/23/19, f104r 46/45/16/14, f104v 45/44/35/32,
f105r 38/37/19/19, f105v 41/38/29/24, f106r 47/47/25/20, f106v 48/47/31/21, f107r 52/51/39/34, f107v 48/49/21/11,
f108r 48/50/34/28, f108v 51/53/28/27, f111v 53/51/35/29, f112r 46/45/19/14, f113r 52/51/43/39, f114r 46/45/42/36,
f114v 43/41/25/20, f115r 46/45/39/35, f115v 47/45/22/16, f116r 49/50/34/25. **Accepted: 578 lines** (C039 had
97). No box was changed after this count.

## Limits
Same ruler as C039, so the same noise: alignment comes from glyph weights and anchors, not from recognising
glyphs. All pages are from one scribal zone (the stars/recipes quire plus f58), so this says nothing about herbal
or balneo spacing. JPG resolution only (no IIIF tiles).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

## Results (`analysis/C040_results.json`, seed 4040, 56 s, run once as pre-registered)
Lines used: **578** on 24 pages (C039 had 97). Spaces anchored are listed per page in the JSON.

| class | n | mean width (px) | median | share ≥ 15 px |
|---|---|---|---|---|
| certain space (leave-one-out) | 5,323 | **18.7** | 18 | 0.55 |
| **comma** | 463 | **12.4** | 9 | 0.31 |
| within-word join | 22,970 | **8.4** | 5 | 0.15 |

- **A** (commas − joins): **+3.91 px, p = 0.0005** (the floor for 2,000 draws).
- **B** (spaces − commas): **+6.32 px, p = 0.0005**.
- Sanity check (spaces − joins): +10.2 px, p = 0.002 (the floor for 500 draws).
- **Gates: FPR A 0/40, FPR B 0/40, power A 40/40, power B 32/40 → PASSED.** Power B sits exactly on the
  pre-registered bar (32/40). It passes, but with no margin.
- **Verdict (pre-registered rule): HALF (intermediate width).** On these pages a ZL comma is, on the vellum, wider
  than a within-word glyph join and narrower than a certain space.
- **Look 2** (secondary): comma width vs C035 Harris score ρ = +0.065 (n = 463, p = 0.080), **not significant**.
  Comma width when IT2a writes a space vs when it does not: 11.8 vs 11.2 px, AUC 0.515 (n = 259, p = 0.33), **not
  significant**. At this n and with this ruler, neither the glyph-context score nor Takahashi's choice tracks the
  measured width at a comma. That is a null result, not an exclusion: the ruler's noise could hide a small effect.

### Per page (descriptive only; mean px — spaces / commas / joins, lines)
| page | lines | spaces | commas | joins | | page | lines | spaces | commas | joins |
|---|---|---|---|---|---|---|---|---|---|---|
| f58r | 26 | 13.1 | 14.8 | 8.8 | | f107r | 34 | 23.3 | 10.7 | 8.0 |
| f58v | 20 | 16.1 | 9.3 | 10.7 | | f107v | 11 | 14.5 | 19.3 | 12.5 |
| f111r | 32 | 16.9 | 14.8 | 9.3 | | f108r | 28 | 16.4 | 6.7 | 8.2 |
| f113v | 19 | 20.7 | 13.2 | 10.3 | | f108v | 27 | 17.9 | 15.8 | 9.1 |
| f103r | 18 | 13.7 | 13.5 | 9.4 | | f111v | 29 | 12.1 | 9.8 | 8.0 |
| f103v | 19 | 16.9 | 11.4 | 9.9 | | f112r | 14 | 14.9 | 11.2 | 11.5 |
| f104r | 14 | 11.8 | 9.5 | 9.0 | | f113r | 39 | 25.2 | 16.9 | 7.7 |
| f104v | 32 | 22.7 | 10.1 | 7.4 | | f114r | 36 | 24.4 | 9.9 | 5.3 |
| f105r | 19 | 14.2 | 5.3 | 7.8 | | f114v | 20 | 13.4 | 7.9 | 8.3 |
| f105v | 24 | 21.4 | 15.5 | 7.7 | | f115r | 35 | 26.9 | 13.3 | 5.4 |
| f106r | 20 | 15.6 | 13.6 | 8.5 | | f115v | 16 | 17.2 | 9.6 | 10.8 |
| f106v | 21 | 20.7 | 9.8 | 10.5 | | f116r | 25 | 19.6 | 18.9 | 9.4 |

Spaces > commas on 22 of 24 pages. Commas > joins on 17 of 24. The pages hold only 7–38 commas each, so any
single page is noisy.

### Post-hoc check (labelled; not pre-registered): pages C039 never saw
`tools/c040_posthoc_new_pages_only.py` reruns the identical pipeline, seed and gates on the 20 new pages only
(the four C039 pages dropped; 482 lines; `analysis/C040_posthoc_new_pages_only.json`, 47 s). Means: spaces 19.1,
commas 12.0, joins 8.2 px. A +3.82 px p 0.0005, B +7.06 px p 0.0005. Gates FPR 0/0, power 40/40 and **35/40**, so
the verdict is again HALF. The result does not depend on the pages that motivated the question. Look 2 is null
here too (ρ 0.08 p 0.061; AUC 0.49 p 0.56).

## What this means
With the same blunt ruler and six times the lines, the image measurement now passes the gates C039 failed. **ZL's
commas mark gaps of intermediate width on the vellum**: about 4 px wider than a glyph join and about 6 px narrower
than a certain space, on average. Transcribers' "uncertain space" therefore corresponds to a physical feature of the
writing, not only to their hesitation. This agrees with C035 (half-boundaries in glyph context) and with C036
(Takahashi spaces about two thirds of them). It is about **spacing**, not meaning, and it holds for the stars/recipes
quire plus f58 only. One caution: power B was exactly at the bar (32/40) on the full set. The out-of-sample post-hoc
check gave 35/40.

## Next
F-SEG is done for this question at this ruler. A sharper ruler (connected-component glyph localisation) would
matter only for **Look 2**: whether Takahashi's space choice or the Harris score tracks width at a comma. Both are
null here, and a sharper ruler could reveal or exclude a small effect. Otherwise I'd move to F-MI step 3, or
extend the ruler to herbal pages to test whether intermediate gaps are a scribe-wide habit.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
