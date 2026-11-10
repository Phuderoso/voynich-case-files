# K066 · Does the confirmed cross-site segment L1 sit inside a summing structure? (line 3)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed with the tool before any observed value of T or F was computed.

**Why this cycle.** K065 confirmed **L1 KH0143·KH0591** (AS128 Berlin, Nazca · QU03 Dallas): `226 115 124 200|357 161`, W 29.70,
p_adj 0.006 over 89 489 pairs. Its "next" asked whether that segment sits inside an Ascher-style summing structure in either khipu.
If the shared cords are totals or summands, the correspondence is more likely a shared accounting block than a coincidence of rare values;
if not, the lead stays a bare value match.

**Disclosed before this commit.** Everything K064/K065 published. While locating the segment I printed both khipus' raw level-1 values.
I noticed that a `55` sits four cords before `226` in **both** khipus (`150 55 65 98 | 226 …` vs `166 55 196 46 | 226 …`). That is why
H2 below is labelled **exploratory and disclosed-motivated**: its p can never be read as a confirmation. No sum relation was computed on
the observed data. One smoke (`K066_SMOKE=1`, R 200, 20 FPR, 20 plants, output in `/tmp`, no observed value): runs in < 1 s; segment
found once in each khipu (KH0143 position 163 of 269, KH0591 position 31 of 39).

## Design
Tool [`tools/k066_l1_sum_context.py`](../tools/k066_l1_sum_context.py). Data: OKR `khipu.db` @ `4039ca5` (hash checked), K064 level-1
pipeline verbatim (duplicates out, R5 multi-number cords → 0), **uncollapsed** level-1 order (sums need the real neighbours).

- **Segment S:** the 5 aligned positions in each khipu (`226 115 124 200 161` / `226 115 124 357 161`), 10 positions.
- **Sum relation (K001 verbatim):** a cord with value v ≥ 10 such that for some k in 2..12 the k cords immediately to its right or
  left sum to v with ≥ 2 nonzero. A position is **sum-involved** if it is such a total, or a nonzero cord inside such a window.
- **H1 (primary):** T = number of sum-involved positions among the 10. Null N1 (K001): permute each khipu's level-1 values
  independently, R 5 000 (seed 6409). p = (1 + #{T_null ≥ T_obs}) / (1 + R). **SUPPORTED iff p ≤ 0.05** (one primary test).
- **Gates (read before T_obs):** **G1** FPR (seed 6410): 200 null permutations treated as observed, share with p ≤ 0.05 must be ≤ 0.10.
  **G2** power (seed 6411): 200 plants, one per khipu per plant — a segment position (with 3 cords to its right) is made the total of
  the next 3 cords (zeros replaced by draws from the khipu's own nonzero values; total ≥ 10) inside a null permutation; recovered iff
  p ≤ 0.05; **power ≥ 0.80 else NOT TESTABLE**. Plants that leave T unchanged are counted as blind spots (Kryptos's I-228: a plant the
  statistic cannot see must be reported, not hidden).
- **A1 audit of K065:** K065's tool re-run unchanged at registered size (smoke env, output in `/tmp`) must reproduce
  `analysis/k065_results.json` exactly on: reference critical W, G1 share, G2 power, and L1's W and p_adj.
- **Verdicts:** SUPPORTED / NOT SUPPORTED (gates pass, p > 0.05: a readable negative against two planted 3-cord totals) /
  NOT TESTABLE (G2) / EXCLUDED (G1 or A1 fail).
- **H2 (exploratory, disclosed-motivated):** on the L1 diagonal of the **collapsed** sequences, F = sum of K064 full-corpus rarity
  weights of exact nonzero matches outside the segment and its two immediate neighbours (which are mismatches by construction of
  max-W). Null: uniform permutation of KH0591's collapsed tokens outside that block, KH0143 fixed, R 5 000 (seed 6412). Reported
  whatever p is; never a confirmation.

**Reading rule.** A supported H1 makes L1 a candidate *shared accounting block*; it still is not a reading and not proof of a copy.
NOT SUPPORTED says the shared cords are not sum totals/summands of the K001 form in either khipu (other relations — e.g. sums of
non-adjacent cords, or across top cords — are not covered).

Seeds 6409–6412; next free **6413**.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
