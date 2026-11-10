# K063 · Rarity-weighted, one-cord-tolerant confirmation of the K061 Pachacamac leads (post-selection, family-adjusted)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed with both tools before any reference-null, FPR, power or observed value of the statistic
below was computed at registered size.

**Why this cycle.** K062 (`949bdb4`, `73320fc`, `0fa4dcf`, `bfc5b02`) found neither lead in any retrieved source (Urton 2014 p. 36 pairs
UR218 = KH0456 with UR1144 = KH0160, not with UR1118 = KH0132), but its count-only confirmation was **NOT TESTABLE** (power 0.01): an
8-cord near-copy scores T = 7 and some pair among the 4 039 reaches T ≥ 7 by chance in 4.3 % of run-permuted corpora. The count
throws away *which* values match. K063 keeps K062's design and changes only the score.

**Disclosed before this commit.**
- Everything K061/K062 published, including K061's post-hoc raw look around lead A (`620, 470, 528, 935|932, 474, 319, 453, 492`) and
  lead B's shared block (`50, 5, 20, 10`). The one-cord tolerance and the rarity weighting were both **suggested by the data and by
  K062's failure**; that is why the test stays post-selection and family-adjusted.
- One smoke of the tool (`K063_SMOKE=2,2,2`, `gates` mode, output `/tmp`, discarded, 0.8 s). I read only: N = 433, family 4 039, lead
  indices A 960 / B 3342, weight source 19 868 tokens / 1 554 distinct values, G0 fixture 20/20, and A0 on 2 corpora (not comparable to
  the 1 000-corpus target). No reference, FPR, power or observed W at registered seeds was looked at. Nothing changed after it except
  deleting an unused K062 helper.

## Design
Tool [`tools/k063_rarity_weighted_confirm.py`](../tools/k063_rarity_weighted_confirm.py) + C kernel [`tools/k063_wham1.c`](../tools/k063_wham1.c),
`full` mode under `timeout 600`. Corpus (433 khipus, K012 rules, R5 mask), run-collapse, null (within-khipu run permutation) and
family F_prov (4 039 within-provenance pairs): K061/K062 verbatim.

- **Weights, fixed in advance.** w(v) = −ln[(n_v + 1)/(n_tot + V + 1)], n_v = count of the non-zero value v in the **run-collapsed real
  level-1 sequences of the corpus with the four lead khipus removed** (KH0132, KH0456, KH0446, KH0451), so the leads' own values do not
  set their own rarity (no leakage). Values absent from that source get the add-one floor −ln[1/(n_tot + V + 1)]. One table for every
  null, plant and the observed corpus. (Disclosed limitation: the table comes from the real corpus, not each null; that is allowed —
  it is a fixed scoring function and the null re-uses it — but it means "rare" is "rare in the real archive".)
- **Statistic W(pair):** over all offsets of the two run-collapsed sequences, the aligned segment with **at most one non-matching
  position** that maximises the **sum of w over its matching positions** (match = equal and > 0). K = number of matches in it.
- **Selection adjustment:** single-step **max-W over the whole family**: p_adj = (1 + #{reference nulls whose family max W ≥ W_obs})/(1 + R),
  R = 1 000 (seed 6301). Single-step max-W controls the family-wise error over all 4 039 pairs at once, so it is valid for lead A
  (picked by K061) and for lead B with **no further correction**. **α = 0.025** (as K062).

**Gates (in order):**
- **G0** brute-force fixture (seed 6304): C kernel = exhaustive weighted segment search on 20 random small corpora with random weights, 20/20.
- **A0 audit of K062:** the new kernel with unit weights on K062's reference seed 6201 must reproduce K062's published family-max T
  counts **exactly** {4: 7, 5: 621, 6: 329, 7: 40, 8: 3}.
- **G1 FPR** (seed 6302): 40 fresh run-permuted corpora; each one's own family max gets p_adj; share ≤ 0.025 must be ≤ 0.10.
- **G2 power** (seed 6303): 200 plants, K062's plant design verbatim (8 raw non-zero cords with 8 distinct values copied into a random
  F_prov pair, one interior cord changed by the first positive of a random order of {−3, −2, −1, 1, 2, 3}). Recovered iff the planted
  pair's p_adj ≤ 0.025. **Power ≥ 0.80**, else **NOT TESTABLE** (observed W not computed).

**Decision rule.** G0, A0 or G1 fail → EXCLUDED (tool/audit). G2 fails → NOT TESTABLE. All pass → compute W once on the real corpus:
lead A p_adj ≤ 0.025 → **CONFIRMED (post-selection, family-adjusted)**; else **NOT CONFIRMED**. Lead B is read with the same p_adj
(valid under max-W); its own information class (four round values) was **not** the plant class, so a non-significant B is "not
confirmed, power for its class not measured", never "absent". Descriptive: real family top-10 W (another pair reaching α is a new
lead, not a claim); the pair-alone null (selected, not used).

**Reading together.** Lead A is a **new finding worth reporting** only if K062's literature verdict stands (`not_found_in_retrieved_sources`)
*and* K063 CONFIRMED. Then it is appended descriptively to the pending OKR duplicates draft — **drafted, not filed**. A confirmation says
the near-identical run is beyond chance, run structure and the 4 039-pair search; it says nothing about *why* (double recording vs copy)
and is not a decipherment.

Seeds: 6301 (reference), 6302 (FPR), 6303 (plants), 6304 (fixture); 6201 re-used only for the A0 audit. Outputs: `analysis/k063_results.json`,
`analysis/k063_run.log`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (computed after the pre-registration commit `8430eef`)

`tools/k063_rarity_weighted_confirm.py data/khipu.db full`, 2026-11-09 18:05:10–18:05:58 PT (47.8 s, under `timeout 600`). Outputs:
[`analysis/k063_results.json`](../analysis/k063_results.json), [`analysis/k063_run.log`](../analysis/k063_run.log). An independent
re-run from a copy of the tools (18:06 PT, `/tmp`) gave a byte-identical results object (all fields except run time).

**Weights.** Source: 19 868 non-zero collapsed values, 1 554 distinct (four lead khipus removed). w ranges 2.45 (value 1) to 9.28 (seen
once); unseen floor 9.97. Examples: 5 → 3.40, 10 → 3.15, 20 → 3.88, 50 → 4.77, 100 → 4.53; 319 → 8.59, 453 → 8.18, 474 → 8.59,
932 → 8.87, 492 and 935 → 9.97 (absent outside the leads).

| Gate | Number | Rule | Outcome |
|---|---|---|---|
| G0 weighted brute-force fixture (seed 6304) | 20/20 | 20/20 | pass |
| **A0 audit of K062** (unit weights, seed 6201) | family-max T counts {4: 7, 5: 621, 6: 329, 7: 40, 8: 3} | = K062 published | **reproduced exactly** |
| Reference null (seed 6301, R = 1 000) | family max W: median 18.36, 90 % 26.33, 97.5 % 26.62 (critical value at α), 99 % 35.21 | — | — |
| G1 FPR (seed 6302, 40 fresh nulls) | 1/40 with p_adj ≤ 0.025 (0.003); next lowest 0.061 | ≤ 0.10 | pass (at nominal) |
| **G2 power** (seed 6303, 200 eight-cord near-copies) | **0.955** (Wilson 0.917–0.976); planted W median 44.5, 5 % quantile 26.96; K = 7 in 189/200 | ≥ 0.80 | **pass** |

All gates passed, so the observed statistic was computed once:

| Lead | W_obs | K | Segment (KH0132 above / KH0456 below; lead B: KH0446 / KH0451) | p_adj (family max-W) | Verdict |
|---|---|---|---|---|---|
| **A** KH0132 · KH0456 | **61.95** | 7 | `620 470 528 935 474 319 453 492` / `620 470 528 932 474 319 453 492` (next cords 600 / 663) | **0.000999 = 1/1 001** (no reference null reached 61.95) | **CONFIRMED (post-selection, family-adjusted)** |
| B KH0446 · KH0451 | 15.20 | 4 | `50 5 20 10` / `50 5 20 10` | 0.995 | NOT CONFIRMED (power for its class not measured) |

p_adj for lead A sits at the resolution floor of R = 1 000; the true family-adjusted p is below about 0.001. Descriptive (selected,
no decision weight): pair-alone null p for A and B both 1/1 001.

**Real family top 10 (descriptive).** 1. KH0140 · KH0483 W 123.4 (K 14; the known same-object pair, p_adj 0.001); 2. **KH0132 · KH0456**
61.9 (K 7, 0.001); 3. KH0304 · KH0303 46.8 (K 9, 0.001; known from K012/K061); 4. KH0616 · KH0620 25.0 (K 7, 0.12; a KFG "similar"
pair); 5. KH0502 · KH0514 23.1 (0.14); the rest ≥ 0.33. No new pair reaches α.

### Reading together
- **Lead A (KH0132 · KH0456): CONFIRMED and not found in any retrieved source (K062).** Eight consecutive collapsed level-1 cords agree,
  seven exactly and one by 3 units (935 vs 932), and the agreeing values are rare in the rest of the archive (474, 319, 453, 492
  occur 3, 3, 5 and 0 times among the 19 868 collapsed values of the other 429 khipus). No run-permuted corpus, in 1 000, produced any within-provenance
  pair scoring this high. It is beyond chance, run structure and the 4 039-pair search; it does **not** say whether this is one object
  recorded twice (as KH0140/KH0483) or a partial copy between two objects — KH0132 (UR1118/AS118, VA42601) and KH0456 (UR218, VA 42559)
  carry different Berlin numbers and different recorders (Ascher; Urton). Urton 2014 p. 36 pairs UR218 with
  UR1144 (KH0160), so this is a *second*, unlisted correspondence of UR218. Appended to the OKR duplicates draft (descriptively, drafted, not filed).
- **Lead B:** not confirmed. Its four shared values are common round numbers (w 3.1–4.8), and this statistic cannot separate that from
  chance at the family level; its class was not the plant class, so this is not evidence of absence.
- **Method lesson:** the same data, the same null, the same family adjustment and the same plants went from power 0.01 (count) to 0.955
  (rarity-weighted). The information was in *which* values match.
- Line 3 next: the camp's cross-khipu exact-match line has now produced its confirmed findings (KH0140/KH0483, KH0304/KH0303 and
  KH0132/KH0456); further steps are physical/archival (museum records), outside the database.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
