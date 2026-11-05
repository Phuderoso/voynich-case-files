# K018 · Information-weighted group-leader matches across the whole corpus

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K018 statistic was computed.

## Repairing K017
K017's corpus test failed because a raw LCS lets khipus whose group leaders are all "1" tie with real matches. K018
weights each matched leader by how rare it is. The K017 README line said "per-pair nulls + BH". I'm replacing that
**before running** with a corpus-level maximum-statistic null, which is stricter than BH (it controls the chance of
even one false discovery) and is feasible: per-pair BH over 93 528 pairs would need about 10⁶ permutations per pair.

## Definitions
- The corpus, R5 masking, groups (`CLUSTER_ID`) and leaders (first value of each group with ≥ 5 cords, zeros dropped)
  are exactly as in K017: 433 khipus and 93 528 pairs.
- w(v) = −log₂(share of v among all leaders in the corpus).
- **W(A,B)** is the maximum total weight of a common subsequence of the two leader sequences (weighted LCS).

## Null, threshold and calibration
- **Null corpus:** every khipu's leaders are shuffled independently. This keeps each khipu's multiset of leaders and
  destroys only their order.
- **Threshold T_W** is the 95th percentile of the corpus-wide maximum W over 100 null corpora (family-wise α = 0.05).
- **Calibration:** in 20 held-out null corpora, at most 3 may contain any pair with W > T_W.
- **Planted copies (descriptive power):** in 50 trials, a random pair of khipus that each have ≥ 12 leaders gets 10 of
  A's leaders written, in order, over random positions of B. A trial counts as found if that pair exceeds T_W.

## Decision rule
- A pair is a **discovery** if W > T_W (the test counts only if calibrated).
- The two pairs named in advance are **KH0097 · KH0586** (Paris · Lima) and **KH0192 · KH0470** (Berlin · Berlin).
  Each is **CONFIRMED** as an ordered leader correspondence if it is a discovery, and **NOT CONFIRMED** otherwise.
- All other discoveries are listed as new leads, flagged as known when they are among the K013 exact pairs.

Compute: about 2–4 minutes.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
