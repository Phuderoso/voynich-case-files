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

---

## Results (computed after the pre-registration commit `949bdb4`)

### Part 2 · Confirmation run (registered, once)
`tools/k062_confirm_hamming1.py data/khipu.db full`, 2026-11-09 17:27:29–17:27:53 PT (23.4 s, under `timeout 600`). Outputs:
[`analysis/k062_confirm_results.json`](../analysis/k062_confirm_results.json), [`analysis/k062_confirm_run.log`](../analysis/k062_confirm_run.log).

| Gate | Number | Rule | Outcome |
|---|---|---|---|
| G0 brute-force fixture (seed 6204) | 20/20 (C kernel = exhaustive segment search) | 20/20 | pass |
| **Audit K061** | same 5 within-family discoveries; KH0132·KH0456 p = 4.86699140653952×10⁻⁶ | = published (rel. 1e-9) | **reproduced exactly** |
| Reference null (seed 6201, R = 1 000) | family max T: 4 (7), 5 (621), 6 (329), **7 (40)**, 8 (3); survival P(max ≥ 7) = 0.043, P(max ≥ 8) = 0.003 | — | — |
| G1 FPR (seed 6202, 40 fresh nulls) | 0/40 with p_adj ≤ 0.025 (one at 0.044) | ≤ 0.10 | pass |
| **G2 power** (seed 6203, 200 eight-cord near-copies, 8 distinct values) | **0.01** (Wilson 0.003–0.036); planted T = 7 in 195/200, 6 in 3, 8 in 2 | ≥ 0.80 | **fail** |

**Verdict by the rule written beforehand: NOT TESTABLE (power).** The observed T was not computed. The reason is visible in the
numbers: an 8-cord near-copy with one altered cord scores T = 7 (seven matching collapsed cords), and in 4.3 % of run-permuted
corpora *some* pair among the 4 039 already reaches T ≥ 7 by chance, so p_adj = 44/1 001 = 0.044 > α = 0.025. The statistic counts
matching cords equally, so it throws away what made K061's p small: the matched values (474, 319, 453, 492, …) are rare three-digit
numbers, while chance runs of T = 5–7 in the family are mostly made of common small values. Under the max-T adjustment, a count
statistic needs T ≥ 8 (nine-cord near-copies) to be read at α = 0.025.

Descriptive only (not a test, no decision weight): the pair-alone null (selected, not used) gives T ≤ 3 in all 1 000 corpora for
this specific pair (1: 886, 2: 112, 3: 2); K061's already published post-hoc sequences contain a 7-match segment. That contrast is
exactly the selection effect the family adjustment exists for; it is not evidence.

### Part 1 · Literature audit
Retrieval by `curl` and WebSearch, 2026-11-09 ~17:28–17:40 PT, after `949bdb4`. Hand records
[`analysis/k062_records.json`](../analysis/k062_records.json), merged by `tools/k062_lead_literature_audit.py merge` into
[`analysis/k062_literature_results.json`](../analysis/k062_literature_results.json); OKR labels in
[`analysis/k062_okr_context.json`](../analysis/k062_okr_context.json); URL list [`analysis/k062_targets.json`](../analysis/k062_targets.json).

**Controls: both pass.** C1: KFG KH0616 (200) "Similar Khipu: Previous (KH0620) Next (KH0618)". C2: Urton & Chu Appendix I (200),
UR266 "… of fixed value '47.' Matches UR 275." and UR275 "… Matches UR266."

**Key new source: Urton 2014 is openly readable.** *Quipus de Pachacamac* (Ministerio de Cultura, 80 pp.) is posted by the Ministry
([PDF](https://museos.cultura.pe/sites/default/files/publicaciones/pdf/garyurton_quipusdepachacamac%20comprimido.pdf), 200; text
layer plus page image of p. 36 checked). On p. 36 Urton lists the **six "quipus similares" (paired) at Pachacamac**: UR1131–UR1095,
**UR1144–UR218**, UR1151–AS189, UR1096–UR196, HP018–UR243, UR226–UR230. The Spanish edition of Urton 2017 (*La historia inka en
nudos*, archive.org full text, 200), Tabla 6.1 "Khipus correspondientes de Pachacamac", repeats the same six pairs.

| Lead | Sources (usable / total) | Pairs them? | Named partners instead | Verdict (merge) |
|---|---|---|---|---|
| **A** KH0132 (UR1118, AS118) · KH0456 (UR218) | 11 / 12 | none | KH0456's **published partner is UR1144 = KH0160** (Urton 2014 p. 36; Urton 2017 Tabla 6.1); KFG similar: KH0132 → KH0366 / **KH0160**, KH0456 → KH0485 / KH0513; Ascher databook (AS118, via KFG): one of the 1907 Pachacamac acquisitions, values 275–935, multiples of 11 — no partner | **`not_found_in_retrieved_sources`** |
| **B** KH0446 (UR208) · KH0451 (UR213) | 7 / 7 | none | KH0451 carries an attached khipu UR214 (OKR notes); KFG similar KH0387/KH0435 and KH0290/KH0676; both only listed in Urton 2014/2017 appendices | **`not_found_in_retrieved_sources`** |

Unresolved: Urton 2005, "Khipu Archives: Duplicate Accounts and Identity Labels" (academia.edu, login wall, not fetched); the
original Ascher databook pp. 791–793 (read only as the KFG transcription). Five web searches recorded (ids, UR codes, Urton 2014 /
2017, the value block, UR208/UR213); the block `474 319 453 492` has no hit anywhere.

**Descriptive (post hoc, no decision weight).** The literature makes a *triangle*: Urton pairs UR218 (KH0456) with UR1144 (KH0160),
and the KFG lists KH0160 as similar to KH0132. KH0160's level-1 values (500, 40, 52, 73, 350, …) do not contain the K061 block or
the 8-cord near-run, so that link is about structure/colour/cord count (62 cords each), not about these values. Two small record
discrepancies: KH0451's museum number is VA42508(A) on the KFG and VA42508(B) in OKR; Urton 2014 Apéndice I gives UR218 a length
28 and UR1118 71 (units not stated), and 62 vs 15 pendants in OKR.

### Reading together
- **Lead A (KH0132 · KH0456):** literature **gap** (not found in any retrieved source, controls passing; Urton names a different
  partner for UR218) **and** confirmation **NOT TESTABLE** (power 0.01). So it stays a **lead**: not already published as far as
  we can read, but not confirmed beyond chance by a selection-adjusted test either. It is **not** added to the OKR draft.
- **Lead B (KH0446 · KH0451):** literature gap; no confirmation attempted (by design).
- Method lesson: an unweighted run count loses to a selection adjustment over thousands of pairs when the copy is short; the
  information sits in *which* values match. **Next on line 3 (K063):** the same post-selection, family-max design with a
  **rarity-weighted** one-mismatch statistic (sum of −log of the value's corpus frequency over matched cords), new seeds, its own
  fixture / FPR / power gates, pre-registered before any value of it is computed on the real pair.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
