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
