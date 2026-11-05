# K028 · Does the KH0240/KH0496 lead survive a null that keeps each khipu's step-to-step habits? (README line 3)

## Why
K027 found that no other pair of the 433 khipus shares a 9-step block of 1s, 2s and 3s. With the lead pair included,
no null corpus produced any such pair (p 0.0005). But that null shuffles runs freely, which destroys habits like
"1 is usually followed by 2". This cycle uses the fairest null available for short sequences: an **exact
doublet-preserving shuffle**. Every khipu's collapsed sequence is replaced by a uniformly random sequence with exactly
the same first value, last value and count of every value-to-value transition (Altschul & Erickson 1985; sampled with
Wilson's algorithm as in Kandel et al. 1996).

## Pre-registration (written before the analysis code was run)
Data and collapsing: exactly as K027 (level-1 pendants, R5 cords set to 0, ≥ 10 nonzero, runs collapsed; 0 is a
symbol, but blocks must be all nonzero). The lead pair is named in advance: **KH0240 (UR004) and KH0496 (UR260)**.

- **S (confirmatory, corpus-wide).** The K027 post-hoc statistic: the number of khipu pairs, lead included, sharing at
  least one 9-block whose values are all in {1, 2, 3}. Observed 1. Null: doublet-preserving shuffle of every khipu,
  R = 1 000 corpus replicates (time cap 420 s; the number reached is reported). p = (1 + #{null ≥ 1}) / (R + 1).
- **Decision.** The lead **survives** if p_S < 0.05: no khipu's own transition habits explain it, even allowing for
  the search over all pairs. Otherwise it is **explained by transition habits** and dropped as evidence of a link.
  Either way, the length 9 and the {1, 2, 3} alphabet came from the lead itself; that selection is stated with the
  result.
- **D (descriptive).** For the lead pair alone: the longest shared all-nonzero collapsed block, against shuffling just
  those two khipus 20 000 times. This is not corrected for the search, so it isn't a decision.
- **Shuffler check (must pass, or the cycle is *not testable*).** On every eligible khipu, 20 shuffles each must keep
  the first value, the last value and every transition count exactly. Shuffles must also differ from the original
  for at least 90% of khipus with ≥ 2 possible orders.

## Results
(Written after the run, below this line.)

Run: `python3 tools/k028_markov_null_lead.py ../khipu.db` (37.6 s). Output: `analysis/k028_results.json`, log
`k028_run1.log`.

**Shuffler check: passed.** 0 violations in 20 shuffles of each of the 433 khipus; shuffles differ from the original
for 91.4% of the 431 khipus with more than one possible order.

| Test | Observed | Null | p | Verdict |
|---|---|---|---|---|
| **S** · any pair sharing a {1,2,3} 9-block (corpus-wide) | 1 pair | 0 pairs in 974 of 1 000, 1 pair in 25, 2 in 1 | **0.027** | **survives** (p < 0.05) |
| D · longest shared block, lead pair only | 9 | most often 4; ≥ 9 in 1 of 20 000 | 1·10⁻⁴ | descriptive (not corrected for search) |

**Reading.** Keeping each khipu's exact transition habits makes the lead look 50 times less rare than under K027's
run null (0.027 against 0.0005). So part of what looked striking was khipu habit. It still clears the pre-registered
bar, so it **survives**, but only just. Two cautions:
1. The 9 and the {1,2,3} alphabet came from the lead. A different length or alphabet would give a different p, and
   no correction covers that choice.
2. K013's test that keeps run lengths gave 0.18 for this pair.

So it stays a **lead, now harder to explain away**, not a link between sites.

**Literature.** The Khipu Field Guide page for KH0240 (UR004) lists Urton (2006) on census records (*padrones
poblacionales*). Small household counts (1–3) are what a census would record, which fits the shared alphabet but not
the shared order. No source links UR004 with UR260.

### Line 3 status
**Advanced:** the lead survives the exact doublet null (p 0.027) after the K027 template exclusion. It's not
confirmed, because the statistic was selected. Remaining test: a held-out confirmation fixed in advance, such as
the same 9-block search on khipus newly added to the OKR after this commit. That is **data-limited** for now.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
