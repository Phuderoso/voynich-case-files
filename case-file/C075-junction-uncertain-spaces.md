# C075 — The seam or the cut? Word-junction dependence at certain vs uncertain spaces (F-JUNC step 2)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Status: PRE-REGISTERED (pushed before running)

## Why
C074 found strong dependence between a word's last glyph unit and the next word's first unit (Currier B 0.23–0.25 bits, A 0.13–0.14 bits), above every Timm–Schinner setting tried. Some of the strongest cells (`r.a`, `s.a`, `l.k`) look like places where a transcriber's space may cut through one word. If so, part of the C074 signal comes from how word breaks were transcribed, not from the text. The ZL transcription marks uncertain spaces with `,`. This cycle asks two questions. Does the dependence survive on certain-space pairs alone? Is it stronger at uncertain spaces than at certain ones of the same sample size?

## Data
- ZL3b only (`data/ZL3b-n.txt`, sha256 in `data/MANIFEST.md`). IT2a has **no** uncertain-space mark (0 commas in paragraph lines), so it cannot answer this question; it is not used.
- Lines, interior pairs and classes are the same as in C074: paragraph lines with ≥ 5 clean words, adjacent interior words (positions 2..n−1), 8 commonest finals × 10 commonest initials + other per language. The separator between the two words is labelled **uncertain** if it contains `,`, otherwise **certain**.
- Label-free inventory (run before this push; counts only, no MI). Currier A: 103 pages, 4,117 interior pairs, 310 uncertain and 3,807 certain. Currier B: 79 pages, 14,167 pairs, 1,008 uncertain and 13,159 certain. The totals match C074.

## Tests (Holm over the gated tests among 4, α 0.05)
- **H1 (per Currier language):** MI over certain-space pairs only, against a page-shuffle null. Interior words are shuffled among the interior slots of the same page; slots keep their separator label. R = 500, one-sided rank p.
  - Gates (20 reps): FPR ≤ 2/20 on page-shuffled text. Power ≥ 16/20 with C074's planted junction rule (q 0.05, all pairs).
  - Verdict: DETECTED / NOT DETECTED / NOT TESTABLE.
- **H2 (per Currier language):** D = MI(uncertain pairs) − mean MI over 20 random subsamples of certain pairs of the same size. Null: separator labels permuted among the interior pairs of the same page, with the text fixed. R = 500, one-sided (D > 0).
  - Gates (20 reps): the base is page-shuffled text plus the C074 plant (q 0.05 on all pairs), so both kinds of pair carry equal dependence. FPR ≤ 2/20 on the base. Power ≥ 16/20 with an extra plant (q 0.10) on uncertain pairs only.
  - Verdict: UNCERTAIN STRONGER / NO DIFFERENCE SHOWN / NOT TESTABLE.
- **Pre-registered reading:** if H1 is DETECTED in a language, the junction dependence there is not just an uncertain-space artefact. If H2 is UNCERTAIN STRONGER, uncertain spaces carry extra dependence, which fits (but does not prove) the "cut word" hunch.

## Generator (descriptive, pre-registered criterion)
- 20 default runs, fresh seeds 11001–11020, 1,500 lines, pseudo-pages of 29 lines, lines ≥ 5 words.
- Per run: mean MI over 20 subsamples of N pairs, with N = the manuscript's Currier-B certain-pair count (13,159). This is the size-matched comparison that C074's caveat asked for.
- The manuscript's Currier-B certain-pair MI is called ABOVE / INSIDE / BELOW the run range.

## Descriptive
Share of uncertain separators in the C074 seam cells (`y.q`, `r.a`, `n.ch`, `n.o`, `s.a`, `l.k`) compared with all pairs.

Seed 7575. Tool: `tools/c075_junction_spaces.py`. Generator seeds 11001–11020 are spent by this cycle; the next fresh block is 11101+.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
