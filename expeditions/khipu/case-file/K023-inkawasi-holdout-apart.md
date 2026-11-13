# K023 · Held-out test: are Inkawasi totals coloured apart from their summands? (open line 6)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K023 statistic was computed.

## Why
K022 noticed, only after looking, that in two Inkawasi khipus (UR269, UR275) no summand ever shared its total's
colour. A pattern seen in the data can't be tested on that same data, so K023 tests it on **held-out** khipus.

## Population (fixed in advance)
Every OKR khipu with `PROVENANCE = 'Incahuasi'` (52 records), **minus** the ten K001 BH-significant khipus used in
K021/K022, minus duplicates. Sum cords, colours and summand blocks are defined exactly as in K021/K022.

## Hypothesis, statistic, null
H (apart): the totals' colour is shared by their summands **less** often than a random non-sum anchor's colour is
shared by its block of the same k and side. Statistic A as in K022; the same anchor null (20 000 replicates).
**One-sided**: p = (1 + #null ≤ obs) / (1 + R).

## Decision rule
α = 0.05. **Supported** if p ≤ 0.05 and the controls pass; **not supported** if p > 0.05 with power ≥ 0.5;
**not testable** if power < 0.5. Many held-out sum cords may be chance matches (these khipus were not significant in
K001), which dilutes any effect; the power control measures exactly that cost.

## Controls
Calibration (200 random anchor sets, false-positive rate ≤ 0.08) and power (200 planted sets, each block cord
recoloured away from its anchor's colour with probability 0.3), as in K022.

Compute: seconds.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (computed after the pre-registration commit `01ff1d21`)

Tool: `tools/k023_inkawasi_holdout.py` (1.2 s). Output: `analysis/k023_results.json`.

The held-out set has **15 Inkawasi khipus with 49 usable sum cords**. Controls pass: false-positive rate 0.04
(rule ≤ 0.08), power 0.85.

| Sum cords | A (obs) | Null mean ± sd | p (one-sided, apart) | Verdict by the rule |
|---|---|---|---|---|
| 49 | 13.86 | 17.32 ± 2.09 | **0.048** | **supported, only just** |

### Sensitivity (disclosed after the run, not pre-registered; it can weaken but not upgrade the verdict)
Tool: `tools/k023_sensitivity.py`. Output: `analysis/k023_sensitivity.json`.
- **Monte Carlo:** five more seeds give p from 0.0477 to 0.0504 (mean 0.049). One of the five lands just above 0.05.
- **Independence:** KH0502 (UR266) is the published twin of UR275 (KH0514, in the K022 set; see K020), so it is not
  truly held out. Without it, p = 0.062 (mean of five seeds), which is above α.

### Reading
The held-out khipus go in the predicted direction (totals share their summands' colour about 20 % less than random
anchors), and the pre-registered rule is met, but **the result is fragile**. It sits on the α line and depends on one
khipu that is not independent. I'm recording it as **weakly supported, not established**. The OKR has no other
Inkawasi khipus left to replicate on, so the line is **paused, data-limited**, and it should not be read as a
colour convention until new Inkawasi records are published.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---
**Audit note (K058, 2026-11-08 ~14:35 PT).** Re-run under the multi-number (R5) mask, pre-registered in K058: 39 sum cords / 13 khipus, A = 8.56 vs null 12.76 ± 1.74, p = 0.0084 (five seeds 0.0067–0.0082; without KH0502 p = 0.0090); gates FPR 0.075, power 0.715 → **robust under the mask**. The original wording ("weakly supported, not established", data-limited) stands: same data, same 15 khipus, one OKR commit.


> **KFG audit note (K075, 12 Nov 2026):** on Khipu Field Guide data the same 15 khipus give A 13.58 vs 16.77, p 0.059 (power 0.795): **not supported**. Quote this result as *not established on either source*. See [K075](K075-kfg-sum-summand-colour.md). — Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
