# C008 — Expedição 8: The Bridge Between Words. Can a cross-word rule give the copying machine the manuscript's edge coupling?

**Status:** pre-registered 2026-11-05 00:35 PT, before any run. Results appended below.
**Approach family:** rule-augmented generator (post-processing the C005 matched Timm–Schinner output with explicit
cross-word rules), with negative (decoupled-table) and dose-response controls. Builds on C005/C006.

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Question
C006 found Voynich word-edge coupling C = 0.204 bits [0.145, 0.281] while C005's matched generator G\* gives 0.001.
Can either of two simple, mechanistic cross-word rules, applied to G\*'s output, reach the manuscript's C **while keeping
the C005 match** (word length, type/token ratio and h2 within ±15 % of the whole-manuscript reference; rigidity R also
within ±15 % of 0.487)?

## Rules (applied line by line; p = probability the rule is attempted at each word after the first in a line)
- **S (selection / local reordering):** draw a desired first glyph unit f ~ T(· | last unit of the previous word);
  among the next 30 words of the generator stream, take the first whose first unit is f and swap it into place.
  Vocabulary and every within-word statistic are unchanged; only word order changes.
- **G (glyph rewriting):** draw f ~ T(· | last unit of previous word) and replace the word's first unit by f.
  Changes vocabulary.
- **T** = the Voynich conditional table P(first unit of next word | last unit of word), estimated from ZL 3b lines.
  **This is a fit to the manuscript, disclosed:** the question is reachability and side-effects, not prediction.
- **Negative control T0:** the same table with rows replaced by the marginal first-unit distribution (no dependence on
  the previous word). Under T0 both rules must leave C within G\*'s p = 0 99 % interval at every p (a rule that
  creates coupling without a dependent table would be an artefact of the method).
- **Dose response (planted check):** under T, mean C must increase from p = 0 to p = 1.

## Grid and data
G\* = C005 selected configuration, seeds 6001–6010 (held-out seeds of C005). Each seed's output is measured on its
first lines totalling ≥ 6,000 words. p ∈ {0, 0.25, 0.5, 0.75, 1.0}; 2 rules × 5 p under T, plus T0 runs.
C with 50 within-line shuffles (C006 definition).

## Decision rule (looks: 2 rules × 4 non-zero p = 8; correction: we require the 10-seed mean inside V's 99 % interval)
- A rule **reaches** if, at some p, the 10-seed mean C lies in [0.145, 0.281] **and** the 10-seed means of mwl, TTR, h2
  and R are each within ±15 % of the reference.
- **"Reaches only by breaking the match"** if C enters the interval only where a match statistic fails.
- **"Does not reach"** otherwise. Controls must pass first, or the rule is "not testable".

## Budget
≤ ~8 min; output `analysis/C008_results.json`.

---

## Results (run 2026-11-05, 27 s; `tools/c008_cross_word_rules.py`, output `analysis/C008_results.json`)

10-seed means. Reference (C005 whole-manuscript means): R 0.487, mwl 4.57, TTR 0.354, h2 2.25; the ±15 % limits are
R 0.414–0.560, mwl 3.88–5.26, TTR 0.301–0.407, h2 1.91–2.59. Target C: [0.145, 0.281].

| Rule, p | C (99 % range over seeds) | R | TTR | h2 |
|---|---|---|---|---|
| none (p = 0) | 0.000 [−0.001, 0.002] | 0.533 | 0.361 | 2.43 |
| S 0.25 / 0.5 / 0.75 / 1.0 | 0.006 / 0.019 / 0.029 / **0.036** [0.030, 0.044] | 0.533 | 0.361 | 2.43 |
| G 0.25 | 0.009 | 0.528 | **0.443** ✗ | 2.54 |
| G 0.5 | 0.034 | 0.528 | **0.493** ✗ | **2.62** ✗ |
| G 0.75 | 0.071 | 0.535 | **0.521** ✗ | **2.68** ✗ |
| G 1.0 | **0.123** [0.103, 0.147] | 0.552 | **0.530** ✗ | **2.73** ✗ |

(mwl is 4.98 throughout. ✗ = outside ±15 %.)

### Controls
- **Negative (decoupled table T0): passed.** C stays within the p = 0 interval at every p, for both rules (largest
  |C| 0.001).
- **Dose response: passed.** C rises monotonically with p under T, for both rules.

### Verdicts (pre-registered rule)
- **S (local reordering): does not reach.** At most 0.036 bits, a sixth of the manuscript's value, with the match intact.
- **G (first-glyph rewriting): does not reach.** At most 0.123 bits, still below the interval. It breaks the TTR match
  already at p = 0.25.

### Post-hoc checks (declared after the main run; not looks)
1. **Recovery check on the manuscript itself** (`tools/c008_recovery_check.py`): shuffle Voynich words within lines
   (C → 0.001), then apply the rule at p = 1 with the same table. G restores **0.202** (range 0.181–0.241), the full
   value, so the rule and the measurement are sound. S restores only 0.088, because a 30-word window rarely contains
   the wanted opening.
2. **Why G stops at 0.123 on the generator:** G\*'s word-final glyphs differ from the manuscript's (seed 6001,
   descriptive): `-y` 44 %, `-l` 30 %, `-m` 19 %, `-g` 7 %, `-n` 0.3 %; entropy 1.79 bits. Voynich: `-y` 40 %,
   `-n` 16 %, `-l` 16 %, `-r` 15 %, `-s` 4 %; entropy 2.53 bits. Coupling needs varied endings to condition on, and the
   matched generator lacks them.

## What this means
- Two simple cross-word rules bolted onto C005's matched generator cannot reproduce the manuscript's edge coupling.
  Reordering is too weak; rewriting openings costs the vocabulary match before it gets close.
- **Audit of C005:** the "matched" configuration matched four global statistics but not the **word-final glyph
  distribution** (2.53 vs 1.79 bits; `-n` and `-r` almost absent; `-m` and `-g` inflated). C005's match is narrower than
  its wording suggested. A note is added to C005. The ending profile is a single-seed descriptive observation here;
  checking it on all ten seeds with a pre-registered rule is the next step.
- **Not excluded:** copying processes with other cross-word mechanisms, or with a richer ending inventory, combined
  with G. Agreement with published work: a recent preprint (reported by
  [Neural Grimoire](https://www.neuralgrimoire.com/did-ai-decode-the-voynich-manuscript/), which I have not yet
  identified at source) says no proposed generator reproduces this coupling. Our result is consistent and independent.
  A "workshop cipher" preprint ([Zenodo 23607887](https://doi.org/10.5281/zenodo.23607887)) builds in "sandhi" layers
  that may target this coupling. It is not tested here.

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
