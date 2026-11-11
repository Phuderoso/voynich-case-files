# C104 — Does the rhythm cross the line break? (F-RHYTHM step 3)

> *Caderno de campo.* Two nights ago the words were heard keeping step with their neighbours inside a line; last night no
> dial on the copying machine could teach it that step. Tonight I follow the footprints to the edge of the line and look
> whether they continue on the next one, the way a sentence runs on in ordinary prose, or stop dead at the margin.

**Status:** PRE-REGISTERED 2026-11-10 (~20:45 PT), before the registered run. Results will be appended below without
editing this registration.

**Disclosure.** A timed smoke run (`SMOKE=1`: R = 50, RG = 20, 2 gate replicates) was run before this registration only to
size compute (6.0 s). Its printed statistics were filtered out of the console and not read (only `n`, the audit flag and
the elapsed time were displayed). Subset sizes seen: IT2a A 637 lines / 450 adjacent-line pairs, IT2a B 2,013 / 1,771,
ZL3b A 663 / 463, ZL3b B 1,988 / 1,729. Currier A is small; the gates decide whether it is testable.

## Question
C102/C103 found that the lengths of neighbouring interior words inside a line persist (D +0.06…+0.08 with words 1, 2 and
last dropped). If line breaks are layout only, as in ordinary prose, the same carry-over should appear across the break
(last kept word of line *i* → first kept word of line *i+1*). If lines are self-contained units, it should vanish there.
- **H1a (word-level carry-over across the break).** r_X = Pearson over adjacent-line pairs of (length of the LAST kept word of
  line *i*, length of the FIRST kept word of line *i+1*). Null: kept words permuted within every line (line multisets
  kept, so line-level persistence stays in the null). D_X = r_X − null mean.
- **H1b (line-level persistence).** r_L = Pearson over adjacent-line pairs of mean kept-word length. Null: line order permuted
  within each run. D_L = r_L − null mean.

## Data
ZL IVTFF 3b and Takahashi IT2a as in `data/MANIFEST.md` (same files as C102/C103). C070 filters (paragraph loci, no `<->`,
all words `[a-z]+`), here lines ≥ 6 words; kept words = positions 3..n−1 (exactly C103 H2). Paragraph starts at locus
indicator `@` or `*` or a page change; a *run* = consecutive kept lines (consecutive locus numbers, no filtered line between)
inside one paragraph; pairs only inside runs. Length = EVA glyph units (C003 `units()`).

## Decision rules
- p two-sided = (1 + #|r* − m| ≥ |r − m|)/(R + 1), R = 2,000; **Holm over 8** = {H1a, H1b} × {Currier A, B} × {IT2a, ZL3b}.
- Per hypothesis and language: **DETECTED-PERSISTENT / -ALTERNATING** if both transcriptions reject (Holm ≤ 0.05) with the same
  sign; **PARTIAL** if one; **NOT DETECTED** if none; **NOT TESTABLE** if any gate fails for that language.
- Reading rule, fixed now: H1a NOT DETECTED with passing gates *and* the within-line D_W clearly positive = "the word-level
  rhythm stops at the line break (to the resolution of the gates)". H1a DETECTED-PERSISTENT = "the rhythm runs on across the
  break". Either way this is structure, not meaning.

## Controls
- Pseudo replicates: H1a = kept words shuffled in every line; H1b = line order shuffled within runs.
- Plants: H1a POS = with prob q per pair, the word of line *i+1* closest in length to the last kept word of line *i* is swapped
  to the front (NEG: the most distant); H1b POS = with prob q per run, lines sorted by mean length (NEG: alternated long/short).
- Design (seed 11693; H1b uses +1000): q = smallest of (0.05, 0.10, 0.20, 0.40) with p ≤ 0.05 and correct sign in ≥ 9/10 design
  replicates for both plants in all 4 subsets (RG 300); none → NOT TESTABLE.
- Gates (seed 11694; H1b +1000; 20 fresh replicates per subset): FPR ≤ 2/20; POS and NEG power ≥ 16/20; broken meter
  (Kryptos I-224 / I-230): mean D under NEG < 0 < mean D under POS.
- **Audit C103:** observed r of the four C103 H2 subsets recomputed; must equal published values to 1e−12.

## Descriptive (no verdict)
- D_W = within-line adjacent persistence of the same kept words (C102 statistic, R 2,000) and the ratio D_X / D_W.
- Natural prose reference where breaks are layout-only: Latin Caesar (pg218), Latin Descartes (pg23306), Italian Dante (pg1012),
  Spanish Cervantes (pg2000), Finnish Kivi (pg11940), cut into pseudo-lines with word counts drawn from IT2a Currier-B lines,
  runs of 8 lines, seed 11696, R 500; letters as units. Corpora are local Project Gutenberg copies (not in git), SHA-256
  prefixes: pg1012 568035b4af7bda4f, pg11940 c538fb127d2eee2a, pg2000 534f41d59f714216, pg218 84ac8411841a4d8f,
  pg23306 d6fea49898f02970, pg7000 abdb584766f3bb64 (unused).

## Seeds and budget
Seeds 11693 (design), 11694 (gates), 11695 (tests; +1 for D_W), 11696 (natural). Next free 11697. Estimated 2–4 min, `timeout 600`.

**Tool:** [`tools/c104_rhythm_line_breaks.py`](../tools/c104_rhythm_line_breaks.py) — committed with this registration, before the run.

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04 (an AI designed and registered this test)
