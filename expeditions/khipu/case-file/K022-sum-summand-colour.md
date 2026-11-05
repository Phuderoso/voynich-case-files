# K022 · Are totals the same colour as the cords they add up? (open line 6)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K022 statistic was computed.

## Why
K021 found that sum cords share a colour among themselves but are not colour boundaries. The next question is how
the total relates in colour to its own summands. Neighbouring cords tend to share colour anyway (colour runs), so the
null has to keep that adjacency.

## Definitions (same as K021)
Sum cords, eligible cords, cord colour and the two populations are exactly as in [K021](K021-sum-cord-colour.md).
Each sum cord's **summand block** is its first matching block: the smallest k in 2..12, the right side before the left.

## Statistic
A = Σ over sum cords of (share of the summand block's cords with a known colour equal to the sum cord's colour).
Blocks with no known colour are skipped.

## Null (keeps colour runs and adjacency)
For each sum cord, draw a random **other eligible cord of the same khipu that is not a sum cord**, and take its block
of the same k in the same direction (redraw if it would run off the end). The colour sequence is untouched. 20 000
replicates. **Two-sided** test: p = 2 · min(P(null ≥ obs), P(null ≤ obs)), using (1 + count) / (1 + R).

## Decision rule
Primary population, α = 0.05 two-sided. A > null → **"totals match their summands' colour"**; A < null →
**"totals are coloured apart from their summands"**; otherwise **not supported** if power ≥ 0.5, **not testable** if
below. The secondary population (all khipus with a sum cord) is reported only.

## Controls
- **Calibration:** 200 times, the sum cords are replaced by random non-sum eligible cords with the same k and
  direction; the false-positive rate at α = 0.05 must be ≤ 0.08.
- **Power:** 200 planted sets in which, for those random anchors, each block cord is recoloured to the anchor's colour
  with probability 0.3 (match direction), and separately recoloured away from it with probability 0.3 (apart direction).

Compute: well under a minute.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (computed after the pre-registration commit `d2acdd49`)

Tool: `tools/k022_sum_summand_colour.py` (1.0 s). Output: `analysis/k022_results.json`.

**Controls pass.** False-positive rate 0.03 (rule ≤ 0.08); power 0.99 in the match direction and 1.00 in the apart direction.

| Population | Sum cords | A (obs) | Null mean ± sd | p (two-sided) | Verdict |
|---|---|---|---|---|---|
| **Primary** (K001 BH-significant) | 95 | 50.7 | 46.1 ± 3.1 | 0.13 | **not supported** (real negative, power ≥ 0.99) |
| Secondary (any sum cord) | 712 | 298.1 | 312.6 ± 7.7 | 0.059 | reported only (leans "apart", not significant) |

Taken together, totals are coloured neither like nor unlike their summands beyond what neighbouring cords already
share. Line 6's "colour-matched sums" idea is therefore **closed as not supported** for the pooled primary set.

### Descriptive only (not tested, noticed after looking)
The pooled result may hide two opposite habits. In UR269 (KH0506, 17 sums) and UR275 (KH0514, 10 sums) **no** summand
shares its total's colour (expected 3.6 and 1.8), while in UR267B (KH0504) totals match their summands more than
expected (10.5 vs 6.0). Those are the same khipus whose totals share a colour in K021. Since this pattern was seen in
this data, it can't be tested on it. It becomes a pre-registered hypothesis for **other** Inkawasi khipus (held out).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
