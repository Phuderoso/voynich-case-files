# K095 · KFG re-audit of K027 + K028: is the KH0240·KH0496 collapsed-pattern lead a template, and does it survive the doublet null on KFG? (README line 9)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registration only.** Written and pushed **before any KFG statistic was computed** (no KFG pendant sequence of KH0240 or KH0496
was printed, collapsed or compared with the OKR one; I have only listed the metadata of the two khipus in KFG: both names exist).
Tool `tools/k095_kfg_k027_k028.py` is written after this commit.

## What is re-audited
- **K027** (`case-file/K027-small-number-template.md`): the pattern `P = 1,2,1,2,3,1,2,1,3` (run-collapsed level-1 pendants) of KH0240 (UR004)
  and KH0496 (UR260) is **not** a shared small-number template: 0 other khipus contain P, 0 other pairs share a 9-block over {1,2,3}; power 1.00.
- **K028** (`case-file/K028-markov-null-lead.md`): under an exact doublet-preserving shuffle (Wilson's algorithm, Kandel et al. 1996) of every khipu,
  the corpus-wide statistic S (pairs sharing a {1,2,3} 9-block, lead included; OKR S = 1) has p = 0.027: the lead "survives, just". D (longest
  shared block of the lead pair = 9) is descriptive.

## Data and input deltas
- **OKR:** `data/khipu.db` exactly as K027/K028 (level-1 pendants in cord order, `DUPLICATE_FLAG = 1` removed, R5 cords set to 0, ≥ 10 nonzero, 433 khipus).
- **KFG:** `/workspace/kfg/kfg_20261111.db` (sha256 `582e548d…`) through K094's loader (pendants `pN` in name order, K072 `kfg_r5` port,
  ≥ 10 nonzero pendants; KFG has no duplicate flag, so none is dropped; I report the eligible count). Values are the KFG `value` column.
- **Input deltas reported (descriptive, no decision weight):** eligible count KFG vs OKR; for each lead khipu, whether its collapsed sequence is
  identical to OKR's, and whether it still contains P; the lead pair's longest shared all-nonzero block D; the list of pairs/khipus any test counts.
- **Lead missing → NOT TESTABLE (G-LEAD).** If KH0240 or KH0496 is absent from KFG, is merged into another khipu, or has < 10 nonzero pendants,
  every test below is **NOT TESTABLE** and no KFG statistic is read. If both are present but their collapsed sequences no longer share a 9-block
  over {1,2,3}, the tests still run (that is a data change, reported as CHANGED for K028 if S then fails its rule).

## Pre-named tests (same statistics as K027/K028, KFG sequences; P fixed as in K027)
| ID | Statistic | Null | R | Seed |
|---|---|---|---|---|
| T1 | N₁ = #khipus other than the two lead khipus whose collapsed sequence contains P | K012/K027 run-permutation (shuffle runs inside each khipu, re-collapse), upper one-sided p = (1+#{null ≥ obs})/(R+1) | 2 000 | 6499 |
| T2 | N₂ = #pairs, lead pair excluded, sharing ≥ 1 all-{1,2,3} 9-block | same null, same replicates | 2 000 | 6499 |
| S | #pairs, lead pair included, sharing ≥ 1 all-{1,2,3} 9-block | K028 exact doublet-preserving shuffle of every khipu, p = (1+#{null ≥ obs})/(R+1) | 1 000 | 6502 |
| D | longest shared all-nonzero block of the lead pair | doublet shuffle of just the two khipus | 20 000 | 6505 |

D is descriptive only (not corrected for the search, as in K028). Time caps: none in the registered run (compute budget ≈ 8 min; checkpoints per
stage); if a stage cannot finish, the reached R is reported and the gate or test that needed it is NOT TESTABLE.

## Decision rules and multiplicity
- **K027 claim ("template not supported"):** Holm over {T1, T2} at familywise α = 0.05 (the original used Bonferroni ×2 at 0.025; Holm is never more
  conservative, and I report whether Bonferroni would give the same call). **REPLICATED** if neither is significant and G-POW(T1), G-POW(T2) pass;
  **CHANGED** if either is significant (a template or family exists on KFG); **NOT TESTABLE** if a gate fails and nothing is significant.
- **K028 claim ("survives, just"):** S judged at α = 0.05 as registered in K028, *and* the shuffler check passes. **REPLICATED** if p_S < 0.05 with S ≥ 1;
  **CHANGED** if p_S ≥ 0.05 (explained by transition habits on KFG); **NOT TESTABLE** if G-SHUF, G-FPR(S) or G-POW(S) fails.
- **Holm across all three pre-named tests {T1, T2, S}** at familywise α = 0.05 is reported as an additional, stricter column (OKR S p = 0.027 would
  itself not pass Holm-3's first step 0.0167 if it were the smallest p). It does **not** change the label above; a "REPLICATED" for S that fails Holm-3
  is stated as such in the verdict.
- **CORRECTED** is used only if the gate A0 shows that the published OKR numbers were wrong, or if KFG overturns K027 or K028 *and* the cause
  is an error in the original rather than a data change (the label then names which). A change caused only by KFG curation is **CHANGED**, not corrected.
- **TOOL EXCLUDED** if a hash check or A0 fails.

## Gates (all before the verdict can be read; fixed here)
- **G-DATA:** sha256 of OKR db (`607913034a0f…`) and KFG db (`582e548d…`) match MANIFEST/K094.
- **A0 (exact OKR rebuild, run on OKR only, no KFG statistic):** the same tool code path with the original seeds (27027 for K027's run-permutation,
  28028 for K028's `random.Random`) must reproduce **every** field of `analysis/k027_results.json` (obs, null mean, q975, p, power, P holders, pairs)
  and `analysis/k028_results.json` (check, S obs/null_dist/p, D obs/null_dist/p, lead sequences, n_khipus) except `secs`. Any difference → TOOL EXCLUDED.
- **G-LEAD:** as above.
- **G-SHUF (K028 check on KFG):** 20 shuffles of every eligible khipu keep first value, last value and every transition count exactly, and shuffles differ
  from the original for ≥ 90 % of khipus with ≥ 3 distinct transitions.
- **G-FPR (unplanted):** 200 fresh null corpora per null (seeds 6500 T-side, 6503 S-side) are treated as the "observed" data and tested against the
  reference null; the share with p < 0.025 (T1, T2 each) or p < 0.05 (S) must be ≤ 0.05 (T) / ≤ 0.075 (S) (Wilson 95 % interval reported).
- **G-POW (planted copies, ≥ 0.80):** 100 trials each in fresh null corpora: T1 writes P (run length 1) into 3 random non-lead eligible khipus at a
  random position; T2 writes a random 9-block over {1,2,3} with no repeated neighbour into 5 random non-lead pairs; S writes one such block into one
  random non-lead pair (as the lead is one pair). A trial is a detection when the planted statistic exceeds the reference null's 97.5th percentile
  (T1, T2) or reaches the smallest value with null-tail p < 0.05 (S). Seeds 6501 (T) and 6504 (S). Power < 0.80 → that test NOT TESTABLE.
  Wilson 95 % interval reported.

## Seeds
6499 T reference null; 6500 T FPR; 6501 T plants; 6502 S reference null; 6503 S FPR; 6504 S plants; 6505 shuffler check and D. **Next free khipu seed: 6506.**
A0 uses K027/K028's own seeds (27027, 28028), not new ones.

## Reading rules fixed in advance
- A replicated K027 means only: on KFG, as on OKR, no other khipu or pair carries the pattern. It still does not show a link between Leymebamba and Incahuasi.
- A replicated K028 means only: the lead still clears p < 0.05 once, with the selection of 9 and {1,2,3} taken from the lead itself (K028's caveat stands).
- Because the lead came from the same corpus, KFG is not an independent sample of khipus: this is a re-audit of data curation, not a held-out confirmation.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
