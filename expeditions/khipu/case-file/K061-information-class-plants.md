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
