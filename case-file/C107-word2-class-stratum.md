# C107 — Expedição 107: the sh-door at word two
*Does the Currier B line-start length coupling (C106) live in the lines whose second word begins with `sh`?*

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed, ran and wrote this case.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Pre-registration (written and committed before any D_S of this cycle was computed)

**Background.** C106 found that in Currier B the length of word 1 and the length of word 2 of a paragraph line are coupled beyond a
null that keeps paragraph runs and line word-count terciles (D_S +0.108 IT2a, +0.066 ZL 3b, Holm 0.002). Separately, word 2 is
unusually often `sh`-initial: N. Pelling, *Cipher Mysteries*, 8 Nov 2026, "The mysterious Word 2 sh-initial boost" (Quire 20,
Takahashi transcription), replicated by our C070/C073 in Quire 20 and Currier B outside it. **This lead is Pelling's**, so C107 is a
follow-up of a known observation, not a blind discovery. If word 2's class is positionally special, the class could carry the
length coupling.

**Kryptos's review of the C107 plan (12 Nov 2026, 01:06 PT), built in:** (1) the word-2 class is fixed here before any D_S; (2) the
lead is credited to Pelling (above); (3) the C083 generator cells run under the same N1; (4) her C200 errata (kryptos-case-files
case 187 / I-255, tip 9ed6f8c) is linked: <https://github.com/Phuderoso/kryptos-case-files/commit/9ed6f8c>; (5) the exact
binomial false-fail rate of the per-cell gate rules is printed (16/20 at true power 0.95: 0.0026; FPR > 2/20 at true 0.05: 0.075).

**Data.** `data/` interlinear files used by C070 (IT2a, ZL 3b; `tools/c070_word2_sh.py` FILES); lines and runs from
`tools/c104_rhythm_line_breaks.py::parse_runs` (paragraph loci, no `<->`, every word `[a-z]+`, ≥ 6 words); Currier B only
(Currier A was NOT TESTABLE in C106). Lengths in EVA glyph units (`tools/c003_position_rigidity.py::units`).

**Class (fixed now).** *sh-initial*: the EVA string of word 2 starts with `sh`. *other*: every other line.

**H1 (primary; Holm over 4 = {sh, other} × {IT2a, ZL 3b}).** r_S = Pearson(len word 1, len word 2) over the class's lines.
N1c = word 2 permuted among lines of the same class × paragraph run × word-count tercile (tercile cut points from the whole
Currier B subset, as in C106). D_S = r_S − null mean, two-sided p, R = 2,000. Verdict per class: DETECTED-COUPLED/-ANTI (both
transcriptions Holm ≤ 0.05, same sign), PARTIAL (one), NOT DETECTED, NOT TESTABLE (any gate fails).

**Gates (C106 machinery with the Kryptos-amended plant).** Degeneracy: informative lines ≥ 50 %. Calibration (seed 11708, 10 pseudo
replicates per q): q* = smallest q in 0.05…0.60 with mean planted D ≥ +0.15; no q* → NOT TESTABLE; q_half for +0.075 (power
only). Gates (seed 11729, 20 fresh pseudo replicates, RG 300): FPR ≤ 2/20, POS and NEG ≥ 16/20 right sign, broken meter
mean D_NEG < 0 < mean D_POS.

**Reading rule.** both DETECTED → coupling **GENERAL** (not carried by the word-2 class); *other* DETECTED and *sh* not →
**NOT CARRIED BY sh** (quote sh power at q_half); *sh* DETECTED and *other* not → **CARRIED BY sh**; neither →
**DISSOLVED/UNDERPOWERED**.

**H1b (registered secondary family, own Holm over 4, same gate rules, seed 11731).** N2c = word 2 permuted within class ×
word-count tercile over the whole subset (keeps word count, drops runs). Verdicts carry the label *run-free null*; H1 stays
primary. **Disclosed:** a smoke run (1 pseudo replicate per q, no D_S) found no q* ≤ 0.60 for the *sh* class under N1c
(groups are small: IT2a 392 sh lines in 225 groups, 137 singletons; ZL 367 in 227, 146 singletons). So *sh* is likely NOT TESTABLE
under H1 by the registered rule; the grid was not widened; H1b was added before any D_S as the weaker-control fallback.
Smoke sizes: IT2a sh 392 / other 1,621; ZL 3b sh 367 / other 1,621; informative fractions 0.65 / 0.90 / 0.60 / 0.89.

**Generator family (descriptive, Kryptos's request).** C083 cell 0 (all-default) seeds 11709–11718 and cell 33 (C083 winner)
seeds 11719–11728, 2,500 lines each; lines ≥ 6 words, first N lines (N = IT2a Currier B line count); pseudo-runs = consecutive
blocks of 8 lines (Currier B mean run length 7.7–8.3); terciles as above; D_S under N1 (R 500) for all lines and per class; word-2
`sh` share minus mid-line (3..n−2) `sh` share. Call per cell: manuscript full-B D_S ABOVE (above all 10 runs) / BELOW / INSIDE.
Caveat in advance: generator lines have no real paragraphs, so pseudo-runs are a stand-in.

**Seeds.** 11708 calibration, 11709–11728 generator, 11729 gates, 11730 tests (+10⁶ for the full-B re-computation), 11731 H1b.
Next free **11732**.

**Run.** `timeout 600 python tools/c107_word2_class_stratum.py analysis/C107_results.json`

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
