# K062 · The two Pachacamac leads of K061: literature audit, then a one-cord-tolerant confirmation of KH0132 · KH0456

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed with both tools before any target page (KFG / databook / publication / search) of this cycle was
fetched and before any reference-null, FPR, power or observed value of the confirmation statistic was computed.

**Disclosed before this commit.**
- K061 (`b7468ad`, `5d8d297`) already read the KFG "similar khipu" links of the four subjects (~16:35 PT): KH0132 → KH0366/KH0160;
  KH0456 → KH0485/KH0513; KH0446 → KH0387/KH0435; KH0451 → KH0290/KH0676. K061 also published the post-hoc look at the raw sequences
  around the KH0132 · KH0456 block (`620, 470, 528, 935|932, 474, 319, 453, 492`). So the one-cord tolerance below was **suggested by the
  data**; that is why the test is labelled post-selection, adjusted over the whole family, and run at α = 0.025.
- One timing smoke of the confirmation tool (`K062_SMOKE=2,2,2`, `gates` mode, output to `/tmp`, discarded; 0.8 s). It printed, and I
  read: G0 fixture 20/20, the K061 audit line (reproduced), the two reference-null family maxima (5, 5) and the two smoke plants'
  T (7, 7). No observed T, no FPR or power from the registered seeds at full size. Nothing in the design was changed after it.
- `targets` mode was run once (ids checked against `khipu.db`, URL list only); `analysis/k062_targets.json` is committed with the results.

## Part 1 · Literature audit (not a statistical test; K043/K052 style)
Subjects: **lead A** KH0132 (UR1118, Ascher AS118, Berlin VA42601) · KH0456 (UR218, VA 42559); **lead B** KH0446 (UR208, 42549) ·
KH0451 (UR213, VA42508(B)), all Pachacamac. `tools/k062_lead_literature_audit.py targets` refuses to run if the khipu.db hash or the
OKR ↔ investigator ids differ, or if K061's results do not name exactly these two new leads.

**Positive controls (method gates, looked up after this commit):**
- **C1 (E1, similar-khipu field):** the KFG page of KH0616 must be retrieved and name KH0620 / JC013 in "Similar Khipu".
- **C2 (E2, published match statement):** Urton & Chu, *Appendix I: Inventory of Inkawasi Khipus* (or the KFG page of KH0502) must be
  retrieved and state that UR266 matches UR275. (Both passed in K052; they are re-fetched, not copied.)
- A control that fails makes its evidence class `method_excluded`; both fail → every lead `method_excluded`.

**Sources, in order (every URL and status recorded; a search snippet is never evidence, only fetched pages):**
a. KFG catalogue pages of the four subjects (similar field, notes, bibliography, any mention of the partner's ids / museum number).
b. KFG Excel databooks of the four subjects (notes / ChangeLog).
c. OKR `khipu_main` NOTES / orig ids of the four (`context` mode, local, read-only).
d. Ascher databook entry for AS118 (KH0132) — whichever copy is retrievable (KFG mirror, Harvard KDB, Cornell eCommons).
e. Urton 2014, *Quipus de Pachacamac* (the pages the KFG bibliographies cite) and Urton 2017, if any readable copy is retrievable
   (publisher page, Google Books preview, repository).
f. WebSearch with every query recorded: the subject ids, UR1118/UR218, AS118, VA 42601/42559, "Quipus de Pachacamac" with UR numbers,
   UR208/UR213, the shared values `474 319 453 492`, and Pachacamac khipu copies / duplicates in Berlin.

**Labels.** Per source: `pairs_them` (explicitly links the two subjects: similar, match, copy, same object recorded twice, shared
sequence — quote it), `other_partner_or_discussed`, `not_mentioned`, `source_missing`. Per lead (forced by `merge`):
**`already_published`** if any usable source pairs them; **`not_found_in_retrieved_sources`** if each subject has ≥ 1 usable source
and none pairs them (a literature gap for the sources read, not evidence the pair is real); **`method_excluded`** if the controls
fail or a subject has no usable source. "Both are Urton's Pachacamac khipus" or "both in Berlin" is not pairing.

## Part 2 · Confirmation of KH0132 · KH0456 (post-selection, family-adjusted)
Tool [`tools/k062_confirm_hamming1.py`](../tools/k062_confirm_hamming1.py) + C kernel [`tools/k062_hamming1.c`](../tools/k062_hamming1.c),
`full` mode under `timeout 600`. Corpus, R5 mask, run-collapse, null and family F_prov (4 039 within-provenance pairs): K061 verbatim.

- **Statistic T** (one-cord tolerance): over all offsets of the two run-collapsed level-1 sequences, the longest aligned segment that
  contains **at most one non-matching position**; T = the number of matching positions in it (match = equal values, > 0).
  K061 selected the pair with T₀ (tolerance 0, the exact block). T is not independent of that selection (it contains the block).
- **Selection adjustment:** single-step **max-T over the whole family**: p_adj = (1 + #{reference nulls whose family max T ≥ T_obs}) /
  (1 + R), R = 1 000 run-permuted corpora (seed 6201). Valid whichever F_prov pair had been picked. Also reported, labelled selected
  and not used for the verdict: the pair-alone null p.
- **α = 0.025** (0.05 / 2: tolerance 0 was already used by K061, tolerance 1 was suggested by its post-hoc look).

**Gates (in order):**
- **G0** brute-force fixture (seed 6204): the C kernel must equal an exhaustive segment search on 20 random small corpora, 20/20.
- **Audit K061:** the within-family exact scan must give the same 5 discoveries and the pair's p = 4.86699140653952×10⁻⁶ (rel. 1e-9).
- **G1 FPR** (seed 6202): 40 fresh run-permuted corpora; each corpus's own family max gets p_adj; share ≤ 0.025 must be ≤ 0.10.
- **G2 power** (seed 6203): 200 plants. Source window of 8 raw level-1 cords, all non-zero and 8 distinct values (the lead's own
  information class, chosen to match it, disclosed), copied into a uniform random F_prov pair at a random position, with one interior
  cord (position 2–7) changed by δ, the first of a random order of {−3, −2, −1, 1, 2, 3} giving a positive value. Recovered iff the
  planted pair's p_adj ≤ 0.025. **Power ≥ 0.80**, else **NOT TESTABLE** (observed T not computed).

**Decision rule.** G0 or G1 fail → EXCLUDED (tool). G2 fails → NOT TESTABLE. All pass → compute T_obs once:
p_adj ≤ 0.025 → **CONFIRMED (post-selection, family-adjusted)**: the near-identical run is beyond what chance, run structure and the
search over 4 039 pairs produce; it says nothing about *why* (double recording vs copy) and is not a decipherment.
p_adj > 0.025 → **NOT CONFIRMED** (the lead stays a lead). Descriptive: the real family's top-10 T (any other pair reaching α is a
new lead, not a claim).

**Reading together.** The lead is a **new finding worth reporting** only if part 1 is `not_found_in_retrieved_sources` *and* part 2
CONFIRMED. If `already_published`, cite the source and stop claiming novelty. If confirmed and unpublished, it is appended
(descriptively) to the pending OKR duplicates draft, still **drafted, not filed**. Lead B gets only the literature audit this cycle.

Seeds: 6201 (reference), 6202 (FPR), 6203 (plants), 6204 (fixture). Outputs: `analysis/k062_confirm_results.json`,
`analysis/k062_confirm_run.log`, `analysis/k062_records.json`, `analysis/k062_literature_results.json`, `analysis/k062_okr_context.json`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
