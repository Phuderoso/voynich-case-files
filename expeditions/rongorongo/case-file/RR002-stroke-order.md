# RR002 · Do the free strokes really chain in a fixed order? (pre-registration)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

*Written and pushed before any order count was computed.*

## Question
rochal/rongorongo (section 20) reports that free stroke signs standing side by side keep a fixed order:
2 before 1 in 18 cases against 8, 4 before 2 in 17 against 7, 1 before 9 in 10 against 0, 2 before 3 in 5 against 0,
giving a chain 4, 2, 1, 9. Those are raw counts, without a significance test, a power figure or removal of copied
texts. The H, P and Q tablets copy each other, so one stroke pair carved once and copied twice counts three times.
RR002 asks whether the ordering survives once copies are removed and the family of pairs is corrected.

## Data
CEIPP transliteration pinned in RR001 (sha256 `6e3e8fd1…`), parsed with the same code (301 lines, 11 216 units).

## Definitions
- **Free stroke:** a unit with no attachment separator (`.` `:` `;` `'`), no `!` (illegible) and no `?` (uncertain),
  whose head digits are 001, 002, 003, 004 or 009. Barthel variant letters (e.g. `002a`, `001V`) are allowed.
- **Adjacent pair:** two consecutive units on the same line, both free strokes with different heads. Pairs never cross a line.
- **Copies removed (primary corpus):** drop every side of tablets P, Q (copies of H) and K (copy of G). H and G stay.
- For a pair of heads {x, y}: n = number of adjacent occurrences in either order; k = occurrences of x before y.

## Hypothesis, test and decision rule
- H0 for each of the 10 pairs among {1, 2, 3, 4, 9}: given that x and y stand side by side, either order is equally
  likely (θ = 1/2). This holds exactly for any exchangeable sequence model, whatever the sign frequencies.
- Test: exact two-sided binomial p for k out of n. Holm over the 10 pairs, family α = 0.05.
- **Feasibility gate (computed from n alone, before k is read):** a pair is TESTABLE only if the exact power to detect a
  2:1 preference (θ = 2/3) at the Bonferroni level 0.005 is at least 0.80. Otherwise NOT TESTABLE.
- Verdicts: **DETECTED** (testable and Holm-significant, direction reported), **NOT DETECTED** (testable, not
  significant), **NOT TESTABLE** (gate failed). No pair is EXCLUDED; that verdict would need an equivalence test,
  which is not pre-registered.
- **Chain:** if at least two pairs are DETECTED, report whether their directions fit one total order (descriptive only).

## Controls
- **Positive control** through the same code path: the content-sign pair {700, 600} (fish then frigatebird, which
  rochal reports as a fixed formula slot), using units whose whole text has head 700 or 600 and no attachment, on the
  primary corpus. It must be DETECTED if n passes the gate; if its n fails the gate, the control is reported as uninformative.
- **Negative control:** shuffle units within each line (keeps line composition), 200 replicates, seed 3002. The run
  passes if the family-wise rate of at least one Holm detection is at most 0.10 (expected ≤ 0.05; 0.10 allows Monte
  Carlo error at R = 200).
- If the negative control fails, every verdict becomes NOT TESTABLE.

## Secondary (declared now, not part of the decision)
- Same test on the full corpus (copies kept), to compare with rochal's counts.
- Merge sign 22 into 4 (rochal section 18 suggests they may be one sign) and recount pair {2, 4}.

## Compute
Exact binomials plus 200 shuffles of 301 lines; well under a minute. Tool: [`tools/rr002_stroke_order.py`](../tools/rr002_stroke_order.py).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
