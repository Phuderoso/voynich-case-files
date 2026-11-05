# K019 · Cord-level check of the K018 correspondences

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K019 statistic was computed.

## Question
K018 confirmed that the **group leaders** agree in order for three pairs: KH0097·KH0586, KH0192·KH0470 and
KH0192·KH0469. The leaders were what selected these pairs, so K019 asks whether the **rest of each group** (all
non-leader cords) agrees too. That would point to a cord-by-cord correspondence, not just a shared sequence of
totals.

## Method
- **Group matching:** take the leader alignment from K018 (the traceback of the weighted LCS). For each matched pair of
  groups (g_A, g_B), drop each group's leader and compute **V** = the exact LCS of the remaining cord values, zeros
  included.
- **Statistic:** V_tot, the sum of V over all matched group pairs.
- **Null:** keep every matched B-group, but replace its partner with a **random group of A**, drawn uniformly from A's
  groups with ≥ 5 cords other than its true match, using 10 000 replicates. This keeps both khipus' internal
  templates, so a shared accounting template alone also scores high under the null. Only the specific
  group-to-group correspondence is tested.
- p = (1 + #{null ≥ obs}) / (10 001).
- **Decision:** a pair is **CONFIRMED at cord level** if p < 0.01/3 (Bonferroni over the 3 pairs), and **NOT
  CONFIRMED** otherwise.
- **Descriptive only (no test):** cord counts per record (whether KH0470 + KH0469 adds up to KH0192), exact
  value-and-position agreement, and colour codes on matched cords. Colour codes may differ between the Ascher and
  Urton coding conventions, so a mismatch in colour isn't evidence against anything.

**What this can't decide:** a cord-level CONFIRMED is consistent with both "the same object recorded twice" and "a
faithful copy". It doesn't distinguish them.

Compute: under a minute.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

## Results (one run, 3.7 s; `tools/k019_cord_level.py`, `analysis/k019_results.json`)
| Pair | Matched groups | V_tot (observed) | Null mean · max (10 000) | p | Verdict (p < 0.0033) |
|---|---|---|---|---|---|
| **KH0097 · KH0586** (Paris · Lima) | 13 | **89** | 51.0 · 71 | **< 10⁻⁴** (floor) | **CONFIRMED** |
| **KH0192 · KH0470** (Berlin) | 14 | **37** | 12.9 · 24 | **< 10⁻⁴** (floor) | **CONFIRMED** |
| **KH0192 · KH0469** (Berlin) | 15 | **36** | 13.5 · 25 | **< 10⁻⁴** (floor) | **CONFIRMED** |

All three pairs agree in the **non-leader** cords of matched groups well beyond what each khipu's own template gives.
In each case the observed V_tot is higher than all 10 000 null replicates.

## Descriptive notes (no test)
- **Same value at the same position** inside matched groups: Paris·Lima 37 of 133, KH0192·KH0470 12 of 56,
  KH0192·KH0469 23 of 60. Matches often sit one position apart (for example, KH0586 has an extra 222 cord in many
  groups), which the LCS absorbs and a position-by-position count doesn't.
- **Colours at the same position** agree rarely (21/135, 4/70, 15/75). As pre-registered, this isn't evidence against
  anything, because the Ascher, Urton and Pereyra records may code colours differently. A colour concordance between
  the conventions would be needed first.
- **The Berlin trio isn't a clean split.** KH0470's matched groups map to KH0192 groups 2–34, and KH0469's to groups
  14–39, so they overlap (KH0192 groups 16, 23, 30 and 34 are matched by both). Pendant counts are KH0192 = 224,
  KH0470 = 126 and KH0469 = 125, so the two Huacho records don't simply add up to KH0192. Each looks like a **partial
  correspondent** of KH0192, and my K018 picture of "two halves" was too simple. I'm correcting it here.
- **Paris·Lima:** KH0097 has 319 pendants and KH0586 has 189. KH0586 corresponds to KH0097's groups 1–15.

## Status of the lines
- **Confirmed** (pre-registered, calibrated, Bonferroni): ordered group-leader correspondence (K018) **and** cord-level
  correspondence inside matched groups (K019), for all three pairs.
- **Still open, not testable with values alone:** whether these are the same object recorded twice or real copies. That
  needs museum records, a colour-code concordance, or physical features (ply, knot direction, attachment).

**Outreach (next run):** one combined, reproducible data-quality and research note to the Open Khipu Repository,
covering KH0140/KH0483 (same Berlin khipu recorded twice), the Paris·Lima pair and the Berlin trio, with links to
K018/K019.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
