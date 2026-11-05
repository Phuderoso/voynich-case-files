# C024 — Two lamps on the same page: do transcribers stumble more on some scribes?
### Expedição 24 · new family F-TRX (transcription reliability)

> **Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. **Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026. An AI did all of this work.

Status: **PRE-REGISTERED** (before any per-hand rate was computed). Results will be appended below.

## Question
Every transcription is an interpretation. Where two independent transcriptions disagree, the glyphs were hard to
read. **Does the glyph-level disagreement between ZL 3b and Takahashi IT2a depend on the scribe (LFD hand), raw and
within Currier language × illustration type?** A hand with a higher rate would mark pages whose statistics deserve
more caution in every other cycle.

## Data
`data/ZL3b-n.txt` (ZL 3b) and `data/IT2a-n.txt` (Takahashi IT2a, see `data/MANIFEST.md`). Lines matched by locus id.
Seen before pre-registration (no per-hand numbers): 225 pages compared, overall disagreement 4 003 edits / 192 190
glyphs = 2.08 %; mixed-hand strata are herbal B (hands 2, 3, 5), text-only B (2, 5) and cosmological pages without
a Currier label (1, 4).

## Design (`tools/c024_hand_disagreement.py`, helpers `tools/c024_common.py`, seed 24024)
- Rate = Levenshtein edits / max line length, summed over lines present in both files; separators and uncertain
  spaces removed, ZL alternatives → first reading, extended glyph codes → `?`.
- G = Σ strata Σ hands L·(hand rate − stratum rate)² (pooled; L = compared glyphs).
- **Look R (raw):** all pages with hand 1–5, hand labels permuted over all pages.
- **Look W (within):** strata = Currier language × illustration type with ≥ 2 hands; labels permuted within stratum.
- 4000 draws, one-sided p, α = 0.025 per look (Bonferroni, 2 looks).
- Gates: FPR at α ≤ 0.075 on 40 destroyed data sets (page records shuffled within the permutation units); power ≥
  0.8 on 40 planted sets (hand-5 pages get +1 percentage point of edits, about half the overall rate). Failing a gate
  = **not testable**.
- Decision: p ≤ α **detected**; otherwise **not detected** (a +1 pp hand-5 difference excluded for that look).
- Caveat fixed in advance: a raw (R) difference may come from section or language (different layouts, labels,
  damage), not the hand; only W speaks to the hand itself.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
