# K095 · KFG re-audit of K027 + K028: is the KH0240·KH0496 collapsed-pattern lead a template, and does it survive the doublet null on KFG? (README line 9)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results appended** (pre-registration `5df8589`; artefacts `7d3e961`). Pre-registration was written and pushed **before any KFG statistic was computed** (no KFG pendant sequence of KH0240 or KH0496
was printed, collapsed or compared with the OKR one; I have only listed the metadata of the two khipus in KFG: both names exist).
Tool `tools/k095_kfg_k027_k028.py` (sha256 `ef328c83…`) was written after that commit.

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

## Results
(Written after the run; the pre-registration above is unchanged.)

**Gates.** All passed, 73 s of KFG compute (A0 55 s).
- **G-DATA** hashes match. **A0 passed:** this tool on OKR with K027's seed 27027 and K028's seed 28028, no time cap, reproduces **every** field of `analysis/k027_results.json` and `analysis/k028_results.json` (differing fields: none; `analysis/k095_a0.json`).
- **G-LEAD** passed: KH0240 and KH0496 are separate, eligible khipus in KFG (482 and 24 pendants).
- **G-SHUF** passed: 0 violations in 20 shuffles of each of 496 khipus; shuffles differ for 91.5 % of the 491 with ≥ 3 distinct transitions.
- **G-FPR** (200 fresh null corpora each): T1 0.010 (Wilson 0.003–0.036), T2 0.000 (0–0.019), S 0.040 (0.020–0.077). All within bound.
- **G-POW** (100 plants each): T1 **1.00** (0.963–1.00), T2 **1.00**, S **1.00** (detection threshold s* = 1). All ≥ 0.80.

**Input deltas (descriptive).** KFG has 496 eligible khipus against OKR's 433 (65 KFG-only names, 3 OKR-only: KH0109 split into A/B, KH0431 and KH0483 merged away).
- **KH0496** collapsed sequence: identical to OKR (20 values; P is its first 9).
- **KH0240**: not identical; 374 collapsed values against 363. Three pure **insertions** (91 after position 199; `0,13,30,1,73,3,9,10` at 200; `19,1` at 330), no value changed, none inside P.
  P is still present, now at position 340 (329 in OKR). The lead pair's longest shared block D is still 9.

| Test | KFG observed | Null | p | Verdict |
|---|---|---|---|---|
| T1 · P in other khipus | **0** | mean 0.0025, q97.5 = 0 | 1.0 | not significant |
| T2 · other pairs sharing a {1,2,3} 9-block | **0** | mean 0.000, q97.5 = 0 | 1.0 | not significant |
| S · any pair sharing a {1,2,3} 9-block (lead included) | **1** (KH0240·KH0496 only) | 0 pairs in 972 of 1 000, 1 pair in 28 | **0.029** | survives (p < 0.05) |
| D · longest shared block, lead pair (descriptive) | 9 | 3: 4 165, 4: 11 799, 5: 3 387, 6: 570, 7: 70, 8: 9 of 20 000 | 5·10⁻⁵ | descriptive |

**Multiplicity.** Holm over {T1, T2} (α 0.05): neither rejected (Bonferroni: same). Holm over all three {T1, T2, S}: S is not rejected (0.029 > 0.0167); that
was announced in advance as an extra, stricter column that does not change the label.

**Verdicts.**
- **K027: REPLICATED.** On KFG, as on OKR, only KH0240 and KH0496 contain P and no other pair of the 496 khipus shares any 9-block over 1–3; power 1.00.
- **K028: REPLICATED ("survives, just"), and it fails the stricter Holm-3 column.** p = 0.029 against 0.027 on OKR (28 against 25 in 1 000 null corpora with one pair; a difference of that size is Monte-Carlo noise).
  Everything K028 said about the selection of 9 and {1,2,3} still holds; the survival is a statement under the original rule, not strong evidence.
- **Nothing published is overturned or corrected.** The changes between OKR and KFG (65 new khipus, 3 insertions in KH0240) add no pair, no holder of P and no new transition habit that explains the lead.

**What this does and does not say.** KFG is the same lead corpus recurated, not an independent sample, so this is a **data-curation re-audit, not a held-out confirmation**.
The remaining test K028 named (new khipus added after that commit) is still data-limited: the 65 KFG-only khipus are the closest thing, and **none** of them
carries P or shares a 9-block over {1,2,3} with any other khipu (T1 and T2 counted them). It is a lead without a replicate, and a link between Leymebamba and Incahuasi remains unshown.

### Line 9 status
KFG re-audit of K027 and K028 **done: replicated, no correction**. Next free khipu seed: **6506**.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
