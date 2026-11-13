# C113 — Expedição 113: is the front/back compass only reading the ruler? (HMM switch rate vs slot null)
*C111 saw, post hoc, that the manuscript's best two-state HMM is "sticky" (a front part, then a back part of the word). Is that
anything more than the word-position slots that C109 already kept?*

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed, ran and wrote this case.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Approach family.** F-HMM, step 2 (registered follow-up of C111's flagged post hoc observation). Slot null from C109.

## Pre-registration (written and committed before any Voynich statistic of this cycle was computed)

**Question.** C111's descriptive note said the manuscript's best HMM persists in one state (diag ≈ 0.98–0.999), unlike alphabetic
controls (diag 0.15–0.29). But a two-state HMM can become sticky simply because glyph frequencies differ by position in the word.
C113 asks whether the manuscript's HMM switch rate departs from what its own position slots produce.

**Data.** `data/ZL3b-n.txt` (primary) and `data/IT2a-n.txt` (descriptive only, observed value, no null), sha256 in
`data/MANIFEST.md`; EVA glyph units (`c003::units`); 15,000-token halves (C108 `halves`); all folios.

**Statistic.** Best-of-3-starts 2-state HMM (C111 `fit_hmm` unchanged, words as separate sequences).
**SW** = Σᵢ occᵢ (1 − Aᵢᵢ), occᵢ = share of token posterior mass in state i (expected switch rate). **T** = mean SW over the two halves.

**Null N-SLOT.** Every glyph unit permuted only among tokens with the same (word length, position) (C109 `shuffle_slot`), each half
independently; the HMM is re-fitted on every replicate with the identical procedure. 60 replicates for ZL3b.
p_low = (1 + #{T_null ≤ T}) / 61, p_high = (1 + #{T_null ≥ T}) / 61; floor 1/61 = 0.016, printed.
Calibration is exact by exchangeability (under H0 the observed text is one more slot draw); a leave-one-out rank check on the null
replicates is printed.

**H1 (two-sided, α = 0.05, 0.025 per direction).** p_low < 0.025 → **STICKIER THAN SLOTS** (front/back beyond position);
p_high < 0.025 → **LESS STICKY THAN SLOTS** (the HMM alternates more than slots allow, i.e. neighbour dependence beyond slots);
neither → **SLOT-EXPLAINED** (the HMM switch rate is what the slots give). Effect printed as T − null mean and z.

**Gate G-PLANT (power; fail → H1 NOT TESTABLE).** Plant A: Latin Caesar half 1 with only 30 % of words intact and 70 % replaced by
their slot-shuffled versions; it must reach min(p_low, p_high) < 0.025 against its own 40-replicate slot null (floor 0.024).
Plant B (sensitivity only, decides nothing): Latin Caesar half 2 with 50 % of words re-ordered front/back (class F units first, then
class K, classes = alternate frequency ranks), whose switch point follows word content, not position.

**Smoke disclosed (controls only, no Voynich number).** Latin h1 SW 0.81 vs two slot replicates 0.39 / 0.40 (alphabetic text
alternates far more than its slots). Front/back plant at 50 %: SW 0.176 vs slot replicates 0.154 / 0.153 — so the slot null is itself
very sticky, and a content-driven front/back structure does **not** push SW below it; the first plant design (stickier-than-slots
only) was therefore replaced, before any Voynich run, by the two-sided test and the diluted plant A above.

**Reading rule (fixed now).** SLOT-EXPLAINED → "C111's sticky HMM is what position slots alone produce; it says nothing beyond
C109's slots". LESS STICKY → "beyond its slots the manuscript's HMM alternates, in line with C109's Sukhotin residual". STICKIER →
"a front/back structure beyond position slots". No claim about vowels, syllables or meaning either way.

**Amendment v2 (committed before the re-run; no statistic of any text was computed).** The first launch (04:38:18 PT) stopped at
input building: Latin Caesar has only one 15,000-token half, so plant B's source "Caesar half 2" does not exist (IndexError before
any HMM fit; log kept as `analysis/C113_run_v1_crash.log`). Plant B now uses Latin Descartes half 1. Nothing else changes.

**Seeds.** 11775 (main; every job rng SeedSequence([11775, name hash, replicate, half])); next free **11776**.

**Code.** `tools/c113_hmm_switch_slot_null.py`, committed with this pre-registration. Run: `timeout 600 python3 tools/c113_hmm_switch_slot_null.py`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

## Results (registered run 04:38:42–04:42:43 PT, 241 s; prereg `a2548f7`, amendment v2 `5cd7f0a`; log `analysis/C113_run.log`, numbers `analysis/C113_results.json`, per-job checkpoint `analysis/C113_checkpoint.jsonl`)

**Gate.** Plant A (Latin Caesar, 30 % of words intact) SW 0.459 vs its slot null 0.335 ± 0.042 (range 0.156–0.402): p_high
**0.024** < 0.025 → **pass**, but only at the floor of a 40-replicate null (1/41). Plant B (front/back, 50 %, Descartes) SW 0.191 vs
null 0.162 ± 0.0004: also **less** sticky than its slots (p_high 0.024), i.e. a content-driven front/back plant does *not* move SW
below the slot null. Leave-one-out rank check: ZL 2/60, plant A 0/40, plant B 0/40 (expected ≈ 5 %).

| Text | SW half 1 | SW half 2 | T | Slot null (mean ± sd, range) | z | p_low | p_high |
|---|---|---|---|---|---|---|---|
| **Voynich ZL 3b** | 0.092 (A diag 0.889 / 0.985) | 0.209 (0.408 / 0.999) | **0.151** | 0.2225 ± 0.0002 (0.2221–0.2230), 60 | −335 | **0.016** (floor) | 1.0 |
| Voynich IT2a (descriptive, no null) | 0.099 (0.877 / 0.989) | 0.209 (0.403 / 1.000) | 0.154 | — | — | — | — |
| Plant A, diluted Latin | 0.459 | — | 0.459 | 0.335 ± 0.042 (0.156–0.402), 40 | +2.9 | 1.0 | 0.024 |
| Plant B, front/back 50 % | 0.191 | — | 0.191 | 0.162 ± 0.0004 (0.161–0.163), 40 | +78 | 1.0 | 0.024 |

**Verdict.** **H1 STICKIER THAN SLOTS** (p_low at the floor 1/61; all 60 slot replicates have T above the manuscript's).
**Reading (registered rule).** "A front/back structure beyond position slots": the manuscript's best two-state HMM switches state
less often (0.15 per transition) than any HMM fitted to the same text with every glyph re-dealt within its (word length, position)
slot (0.222). C111's sticky HMM is therefore **not** just the slots re-expressed. IT2a gives the same value (0.154, descriptive).

**What this does and does not say.**
- The departure is large next to the null's spread, but z = −335 mostly reflects how little the slot null varies (sd 0.0002: every
  re-dealt text lands on the same HMM optimum). The honest size is the difference, **0.072 switches per transition** (−32 %).
- The two halves differ a lot (0.092 vs 0.209, in both transcriptions): the first half's HMM persists in both states, the second
  half's has one absorbing state. Halves follow the folio order, so this is a section/Currier mix effect or a different optimum, not
  tested here.
- *What kind* of structure is not identified. Plant B shows that a front/back order with a content-driven switch point does **not**
  produce it (it raises SW above slots). A structure that keeps whole words or long runs inside one state more than position
  predicts (e.g. word-type level classes) would; that is a hypothesis for a later cycle, not a finding.
- Power: the gate passed only at its floor; more replicates would sharpen it. The Voynich result is at its own floor (1/61) but
  the observed T lies 360 null sd below the null minimum, so more replicates would not change the verdict.
- Abjad, voweled and generator texts were **not** run under this null in C113, so whether "stickier than slots" is unusual is
  **not tested**. No claim about vowels, syllables or meaning.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
