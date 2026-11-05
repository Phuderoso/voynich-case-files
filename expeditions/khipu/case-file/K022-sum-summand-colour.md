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
