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
