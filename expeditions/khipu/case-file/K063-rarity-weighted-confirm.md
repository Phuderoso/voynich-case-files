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
