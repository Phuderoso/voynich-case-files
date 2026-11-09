# K061 · Which short cross-khipu copies can the within-provenance scan read? (power by information class)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any gate number (FPR, power, coverage) or any observed match p-value of this cycle was computed.
Disclosed before this commit: one timing smoke (`K061_SMOKE=1,2`, `gates` mode, output to `/tmp`, discarded) of which only the
G0 self-test line (20/20; 18 of 20 fixtures contain at least one shared block) and the run time (2.4 s) were read. No null, plant,
coverage or real-pair value was read.

## Why this line, and why not option (a)
Open line 3. K059 (`78dad97`) and K060 (`a04f17a`) were both calibrated but **NOT TESTABLE** at 6 cords (power 0.195 over 93 528 pairs;
0.565 over the 4 039 within-provenance pairs). K060's diagnosis: about one copy in five carries too little information (80th-percentile
plant p 0.0027). K060 named two options.
- **(a) a ≤ 20-pair family from outside evidence** (e.g. the Khipu Field Guide's "similar khipus"). **Rejected:** the KFG similarity
  is computed from the same OKR/KDB cord data (values, colours, structure), so the family would be selected *on* the quantity the scan
  scores. Its p-values would be invalid (selection on the outcome), and the literature pairs we know of (Puruchuco set, UR053B/C,
  Inkawasi, KH0140/KH0483) are long matches already mapped in K005/K006/K010/K012. No external list exists that can be fixed without
  seeing match information.
- **(b) plants conditioned on information content, stating the readable class: chosen.** It is not a third family or p-value tweak:
  the scan and family are K060's verbatim. The cycle measures **which kind of 6-cord copy** that scan can read, on a pre-named power
  curve, and runs the real scan only if some class is readable.
OKR is still `4039ca5` (GitHub API, 2026-11-09 ~16:25 PT: newest commit 2026-08-04 "Added Rosa María Varillas to contributors list").

## Fixed design (K060 verbatim unless stated)
- Corpus: the 433 analysed khipus (K012 set: duplicates excluded, R5 mask, ≥ 10 non-zero level-1 cords). Run-collapse, longest
  shared block (3-symbol seeds, cap 300), **K012 Poisson p**: verbatim.
- Family **F_prov**: K060's 4 039 within-provenance pairs (strip + casefold, no merging, ''/unknown excluded). BH q = 0.05 over F_prov.
- Plant design: K060's (run-permuted corpus, pair uniform in F_prov, random direction, 6 raw cords copied, ≥ 5 of 6 non-zero), plus
  the **class filter**: the source window must hold **≥ d distinct non-zero values**. Pairs whose source khipu has no such window
  are redrawn (this tilts plants towards more varied khipus; disclosed, and coverage below says how much of the corpus a class covers).

## Gates (in order)
- **G0 brute-force fixture** (seed 6164): on 20 random small corpora, the K012 `longest` statistic must equal an exhaustive all-offsets
  search for every pair, and the class filter must equal a brute-force distinct count. 20/20 required, else EXCLUDED as a tool.
- **Audit K012** real scan: 5 323 blocks and 6 discoveries must reproduce.
- **G1 FPR = audit of K060's G1** (verbatim, seed 6060, 40 run-preserving null corpora). The FPR does not depend on the plant class.
  Pass rule as K060 (≥ 1 within-family discovery in ≤ 10 % of corpora and pair share p < 0.01 ≤ 0.01); additionally reported:
  whether K060's 0/40 and 0.00045 reproduce exactly.
- **G2 power curve**: 200 class-filtered 6-cord plants for each d ∈ {4, 5, 6}, seeds 6161 / 6162 / 6163; recovery by within-family BH.
  Wilson 95 % intervals reported. **Readable class d\*** = the smallest d with power ≥ 0.80 (nested classes, so the curve should rise
  with d; a non-monotone curve is reported as such).
- Descriptive only: coverage = share of eligible 6-cord windows (≥ 5 non-zero) of the family khipus, in the real sequences, with ≥ d
  distinct values; per-provenance power for cells with ≥ 30 plants; M\* = 0.05 / 80th-percentile plant p; power by exact distinct count.

## Decision rule and hypothesis
- **H1**: within-provenance pairs carry short exact correspondences beyond chance.
- If G0 and G1 pass and d\* exists → run the observed within-family BH scan once (K060's H1 scan). Discoveries among K012's six
  known pairs are **re-findings**, not new; any other discovery is a **lead** needing a literature check, not a claim. Silence (no
  discovery outside the known pairs) → **NOT DETECTED**, readable only for 6-cord copies of class ≥ d\*: such copies are
  **EXCLUDED** as a feature of the within-provenance corpus at planted strength. Copies of lower classes stay NOT TESTABLE.
- If no class reaches 0.80 → **NOT TESTABLE (LOW-POWER) for every class**; observed scan not run; line 3 rests at the 8-cord floor
  (K014) and is **closed on available data** (no further family or plant variant is owed).
- If G0 fails → EXCLUDED (tool). If G1 fails → EXCLUDED (tool) for this family.

Seeds: 6164 (fixtures), 6060 (null, K060 audit), 6161–6163 (plants). Tool: [`tools/k061_information_class.py`](../tools/k061_information_class.py)
(`full`), under `timeout 600`; expected ≈ 4–5 min. Output `analysis/k061_results.json`, log `analysis/k061_run.log`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (computed after the pre-registration commit `c2736f2`)

Tool run once as written (`full`), 2026-11-09 16:34:04–16:34:26 PT (22.2 s, under `timeout 600`; faster than K060 because the exact
bound is not computed). Outputs: `analysis/k061_results.json`, `analysis/k061_run.log`.

| Gate / test | Number | Rule | Outcome |
|---|---|---|---|
| G0 brute-force fixture (seed 6164) | 20/20 (`longest` = exhaustive search; class filter = brute count) | 20/20 | pass |
| Audit K012 (all pairs, real data) | 5 323 blocks, 6 discoveries | = published | **reproduced** (fourth time) |
| **G1 = audit of K060 G1** (seed 6060, 40 nulls) | 0/40 corpora with a within-family discovery; pair share p < 0.01 = 0.0004456548650656103 | ≤ 0.10, ≤ 0.01 | pass; **K060's G1 reproduced to the last digit** |
| G2 class d ≥ 4 (seed 6161) | **0.575** (Wilson 0.506–0.641) | ≥ 0.80 | fail |
| G2 class d ≥ 5 (seed 6162) | **0.745** (0.680–0.800) | ≥ 0.80 | fail |
| G2 class d = 6 (seed 6163) | **0.96** (0.923–0.980) | ≥ 0.80 | **pass → d\* = 6** |

The curve rises monotonically with information. Inside each class, power by exact distinct count is the same story: 4 distinct
0.15 (n 68), 5 distinct 0.61–0.67 (n 79 / 126), 6 distinct 0.96–0.98 (n 53 / 74 / 200). Cells (≥ 30 plants): at d = 6 Pachacamac
0.99 (123) and Ica 0.94 (33) both have full power. M\* (descriptive): 82 / 1 166 / 125 820 pairs for d ≥ 4 / 5 / 6.
**Coverage (descriptive):** of 10 854 eligible 6-cord windows (≥ 5 non-zero) in the family khipus' real sequences, 80.0 % have ≥ 4
distinct values, 60.3 % ≥ 5, **26.2 % have 6**. So the readable class is about a quarter of the possible 6-cord copies.

### H1: observed within-family BH scan (run once, because d\* exists)
169 of the 4 039 family pairs share a ≥ 3-symbol block. **5 BH discoveries** (q = 0.05, first rank 1.24×10⁻⁵):

| Pair | Provenance | L (collapsed) | p (K012 Poisson) | Block | Status |
|---|---|---|---|---|---|
| KH0140 (AS125) · KH0483 (UR247) | Pachacamac | 12 | 2.9×10⁻¹⁴ | 1517, 2373, 6291, … | K012 re-finding (double recording, pending OKR note) |
| KH0304 (UR067) · KH0303 (UR066) | Huaquerones | 7 | 2.6×10⁻⁷ | 22, 3, 9, 2, 156, 13, 12 | K012 re-finding (Puruchuco/Huaquerones set) |
| **KH0132 (UR1118, AS118) · KH0456 (UR218)** | Pachacamac | 4 | 4.9×10⁻⁶ | 474, 319, 453, 492 | **new lead** |
| KH0616 (JC009) · KH0620 (JC013) | Incahuasi | 6 | 1.7×10⁻⁵ | 10, 1, 2, 10, 30, 28 | lead from K013, already in the KFG (KH0616's "similar" is KH0620) |
| **KH0446 (UR208) · KH0451 (UR213)** | Pachacamac | 4 | 4.7×10⁻⁵ | 50, 5, 20, 10 | **new lead** (round numbers, weaker) |

**Verdict by the rules written beforehand.**
- **H1 DETECTED within F_prov** (calibrated: FPR 0/40): two K012 re-findings, one known lead, and **two pairs never named before by
  this expedition** (KH0132·KH0456, KH0446·KH0451). Per the pre-registration these are **leads needing a literature check, not claims.**
  Neither appears in the KFG "similar khipu" links (KH0132 → KH0366/KH0160; KH0456 → KH0485/KH0513; KH0446 → KH0387/KH0435;
  KH0451 → KH0290/KH0676, checked ~16:35 PT).
- **Readable negative, scoped:** 6-cord copies with 6 distinct values are readable (power 0.96); for them the scan would have seen any
  copy at planted strength. Copies with ≤ 5 distinct values stay **NOT TESTABLE** (0.575 / 0.745).
- The smaller family is what made these visible: neither new pair is among the six all-pairs K012 discoveries.

**Post-hoc look (descriptive, no decision weight, flagged as selected after seeing the discovery).** Around the KH0132·KH0456 block
the raw level-1 sequences read
`KH0132: 0, 620, 470, 528, 935, 474, 319, 453, 492, 600, 0, 0, 400, 0, 275` and
`KH0456: … 130, 620, 470, 528, 932, 474, 319, 453, 492, 663, 252, …, 275, …`:
**eight consecutive cords agree except one (935 vs 932)**, which is why the exact statistic only scored 4. Both are Berlin Pachacamac
khipus (VA42601, recorded by the Aschers; VA 42559, recorded by Urton), not flagged as duplicates, 15 vs 62 pendants. The pattern
(different investigators, different VA numbers, a long near-identical run) resembles the KH0140·KH0483 double recording, but the
cord counts differ, so it may also be a genuine partial copy. Both are discussed in Urton 2014 (*Quipus de Pachacamac*, pp. 36/43/47)
per the KFG bibliographies; that text has not been checked. KH0446·KH0451's block (50, 5, 20, 10) sits in long round-number khipus
and is the weaker lead. **Next (K062):** literature check of both leads (Urton 2014, 2017; Ascher databook AS118), and, if new,
a pre-registered close-match (one-cord tolerance) confirmation of KH0132·KH0456 with its own null.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
