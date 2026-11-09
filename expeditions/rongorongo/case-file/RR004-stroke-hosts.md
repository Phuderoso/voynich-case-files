# RR004 · Do fused strokes choose their hosts?

> *Caderno de campo.* The free strokes have told us nothing (RR002, RR003). But most strokes are not free: about a
> thousand of them are carved *onto* another sign, like a tick on a bird's wing. If they were affixes with grammar or
> counting meaning, a 1-stroke and a 3-stroke should not sit on the same signs in the same proportions. That is the
> trench for today.

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. All analysis and writing here is done by an AI.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results below.** Open line 4 of the [expedition README](../README.md). Pre-registered 2026-11-09 before any test statistic was computed
(only the sizes below were looked at to fix the host threshold).

## Data
CEIPP transliteration as pinned in RR001 (parsed `corpus.json`, sha256 `ce1782aa…e460`), copy tablets P, Q, K removed
(as in RR002/RR003). **Code normalisation:** every component's leading digit run is padded to three digits
(`4.120a` → `004.120a`); some lines (mostly Aa01–Aa02) are written unpadded in the source.

## Definitions
- Unit components: split on `.` and `:`.
- **Bound stroke:** a component whose base is 001, 002, 003, 004 or 009 (the strokes of RR002/RR003; no `!`/`?`), in a
  unit that also holds at least one non-stroke component. Its **host** is the nearest non-stroke component to its left
  in the same unit (side R = stroke after host), otherwise the nearest to its right (side L). Host = three-digit base.
- Hosts with ≥ 5 bound strokes are kept (43); the rest are pooled as `other`.
- Sizes: 943 bound strokes (001: 313, 003: 269, 004: 166, 009: 107, 002: 88); R 554, L 389; 16 tablets.

## Hypotheses (Holm over 2, α = 0.05)
- **H1 (host selectivity):** stroke type depends on host. Statistic: plug-in MI(stroke type; host), bits.
- **H2 (side):** stroke type depends on side. Statistic: MI(stroke type; side).

**Null (both):** stroke-type labels permuted among bound slots *within each tablet*, R = 999. This keeps each host's
number of bound strokes, each tablet's stroke mix and every side, so a tablet-wide habit (e.g. Mamari's lists) cannot
produce H1 by itself. p = (1 + #{null ≥ obs}) / (R + 1).

## Gates (before any verdict)
- **Power:** on null replicates, m slots of the most frequent kept host (and separately the second) are re-set to the
  stroke type that host uses least; m* = smallest m in {2, 4, 6, 8, 10, 15, 20, 30, 40, 60} with power ≥ 0.80 at
  α 0.025 (and m slots actually available). For H2 the same with side-L slots. No m* → NOT TESTABLE.
- **Negative control:** 20 fresh null replicates scored as if observed; family-wise rejections ≤ 2/20, else NOT TESTABLE.

## Decision rule
DETECTED if Holm-rejected and gates pass; NOT DETECTED if not rejected and gates pass (the claim is then: no
host-specific substitution larger than ~m* slots of one host); NOT TESTABLE otherwise. Descriptive table of stroke ×
host published either way. **A DETECTED H1 does not mean the strokes are affixes**: carving or copying habits of
particular compounds (e.g. 380.001 in lists) would also do it; it would only open the next test.

## Audit A (RR002/RR003)
RR002/RR003 matched strokes with the regex `00[12349]` on raw codes, so unpadded strokes in Aa01–Aa02 were missed.
Pre-check: free strokes 732 → 738, adjacent pairs 107 → 109. RR003 is re-run unchanged except for padding
(descriptive; verdicts change only if a Holm decision flips).

Tool: [`tools/rr004_stroke_hosts.py`](../tools/rr004_stroke_hosts.py), seed 4004.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (run 2026-11-09 ~03:55 PT, seed 4004, 2.4 s; raw output [`analysis/rr004_results.json`](../analysis/rr004_results.json), log [`analysis/rr004_run.log`](../analysis/rr004_run.log))

**Gates.** Negative control 0/20 family-wise (pass). Power: H1 m* = 60 slots on the commonest host (380, which already
carries 83/115 of stroke 1) and m* = 30 on the second host (064); H2 m* = 40 side-L slots. All defined: both tests
testable.

| Test | Observed MI (bits) | Null mean | Null max | p | m* | Verdict |
|---|---|---|---|---|---|---|
| H1 stroke type × host | 0.878 | 0.180 | 0.225 | 0.001 (floor) | 60 / 30 | **DETECTED** |
| H2 stroke type × side | 0.181 | 0.005 | 0.020 | 0.001 (floor) | 40 | **DETECTED** |

Both Holm-rejected. The observed values sit far beyond every null replicate (H1 about 4× the null max, H2 about 9×).

**Descriptive table (hosts with ≥ 24 bound strokes).** 064: stroke 4 on 52 of 53. 065: 3 on 20 of 24. 380: 1 on 83, 3 on
30 of 115. 010: 2 on 24 and 1 on 20 of 49. 062: 1 on 24 of 30. 600: 4 on 18 of 30. 005: 9 on 13 and 1 on 11 of 26.
Sides: 3 follows its host 238 to 31 and 9 follows 78 to 29, while 4 precedes 126 to 40 and 2 precedes 60 to 28;
1 is split (170 after, 143 before).

**Post hoc (labelled; seed 4005, [`analysis/rr004_posthoc.log`](../analysis/rr004_posthoc.log)).** (a) Type level, with
each distinct normalised compound counted once (501 slots, hosts with ≥ 3 kept, global permutation): H1 0.724 vs null
max 0.477, H2 0.133 vs 0.026, p 0.001 both. So the effect does not come only from repeated list formulae.
(b) Without host 380: H1 0.889, H2 0.209, p 0.001 both. (c) The highest-lift cells are 025+9 (8.8×), 430+4 (5.7×),
064+4 (5.6×) and 010+2 (5.3×).

**Reading.** Bound strokes are **host- and side-specialised**: each stroke type lives on its own set of signs and on
its own side. This is the null-calibrated version of a pattern rochal/rongorongo counted without a null. It does
**not** show that the strokes are affixes. A carving habit, a fixed ligature or a Barthel/CEIPP coding convention for
how a compound is split and ordered would produce the same numbers, and the side result is the most exposed to coding
order. The next test that could separate these needs a property the coding cannot make. One candidate: do
host+stroke compounds alternate with the bare host in parallel passages (H/P/Q), the way an affix would?

## Audit A (RR002/RR003, padded codes; [`analysis/rr004_auditA_rr003.json`](../analysis/rr004_auditA_rr003.json))
RR003 re-run unchanged except for padding: 738 free strokes (was 732). H1 109 vs null 96.3, p 0.070 (was 107, p 0.098);
H2 11 vs 9.4, p 0.311; H3 5 vs 9.5, p 0.986; m* 30 / 8 / 10; negative control 1/20. **All three verdicts unchanged
(NOT DETECTED).** RR002 was not re-run. Padding adds at most 6 strokes to any pair, and its largest pair is 23 against a
gate of n ≥ 120, so NOT TESTABLE stands by arithmetic. An audit note is added to RR003.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
