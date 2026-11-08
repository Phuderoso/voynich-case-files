# K052 · Is the KH0240 · KH0496 lead already in the literature? (README line 3, literature audit)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results appended** (pre-registration written and pushed with the tool as `69c115b` before any target
page — KH0240 / KH0496 / UR004 / UR260 — or either control page was fetched for this cycle, and before any web
search for the pair).
Only local repository files (K014, K020, K028, K043, K050, K051, README) and the pinned `khipu.db` id fields
were read first.

## Why
K012 raised one unconfirmed lead: **KH0240 (UR004, Leymebamba, Centro Mallqui CMA 847-LC1.476 TEQ,
Chachapoyas)** and **KH0496 (UR260, Incahuasi, Proyecto Incahuasi 9228-13B, Cañete valley)** share the
run-collapsed pendant pattern `P = 1, 2, 1, 2, 3, 1, 2, 1, 3` with different run lengths (KH0240
`4,1,1,1,1,1,1,1,1` from cord index 402 / run 329 of 363; KH0496 `1,1,3,1,1,2,1,1,1` from its first cord).
K027 excluded a shared small-number template; K028 found it survives an exact doublet-preserving null
(p 0.027) but **not confirmed** (selected statistic; held-out confirmation data-limited); K051 found colour on
the 9-run block **degenerate** (0/9). The literature checks so far were light: K014 (2026-11-05) "found no
literature on this pair" (and noted UR260 in the Inkawasi "khipu pile" of Urton & Chu 2015, Appendix I);
K028 noted in passing that the KH0240 Field Guide page lists Urton (2006) on *padrones poblacionales* and that
"No source links UR004 with UR260". K052 replaces those with a **pre-registered audit with positive
controls**, K043 style: re-fetched pages and verbatim quotes, not copied claims.

This is a **literature audit, not a statistical hypothesis test**. No Monte Carlo. No new named discovery.
No decipherment. No claim of a Leymebamba–Incahuasi link from us, whatever the outcome.

## Data (locked)
Subjects KH0240 / UR004 and KH0496 / UR260. `tools/k052_lead_literature_audit.py targets` checks the pinned
OKR `khipu.db` @ `4039ca5` (SHA-256 `607913034a0f…c4db`, read-only) and `analysis/k051_results.json`, and
**refuses to run** if the OKR ↔ investigator ids of the subjects or controls differ from the table below, or if
K051's values gate does not name exactly this pair with the published run lengths. It writes
`analysis/k052_targets.json` (URLs to look up). A read-only `context` mode prints the OKR site / museum /
notes labels of the two subjects (`analysis/k052_okr_context.json`; descriptive, not a test).

| Role | OKR | Investigator | Partner expected |
|---|---|---|---|
| subject | KH0240 | UR004 | — |
| subject | KH0496 | UR260 | — |
| control C1 (similar-khipu field) | KH0616 | JC009 | KH0620 / JC013 |
| control C2 (published match) | KH0502 | UR266 | KH0514 / UR275 |

**Disclosed correction of the cycle brief, before any fetch:** the brief named the C1 page as "KH0620 (JC009)".
In OKR, **JC009 = KH0616** and **JC013 = KH0620** (`khipu.db` `INVESTIGATOR_NUM`), and K014 quoted the
**KH0616** page ("Similar Khipu: Previous (KH0620)"). C1 is therefore the KH0616 page, required to name
KH0620 / JC013. The reciprocal KH0620 page is fetched too and recorded descriptively (it does not decide C1).

## Evidence classes and sources (in order; never record what a page says without a retrieved copy)
Two evidence classes, each with its own control:
- **E1 · similar-khipu field** — Khipu Field Guide (KFG) catalogue "Similar Khipu" / most-similar / related
  fields. Gate: C1.
- **E2 · publication / match statement** — any explicit statement in a KFG note / reference list, OKR record
  note, or named publication that this khipu matches / corresponds to / repeats / shares a block with another
  khipu. Gate: C2.

a. KFG catalogue pages `https://www.khipufieldguide.com/catalog/KHXXXX.html` for KH0240, KH0496 (and KH0616,
   KH0620, KH0502 for the controls). If 404/empty: investigator-code page names (UR004, UR260), the catalogue
   index, a site search; every attempt and HTTP status recorded.
b. On those pages: similar-khipu / related / notes / references / Ascher-sum fields; any mention of the other
   subject (KH0240, KH0496, UR004, UR260, Leymebamba with Incahuasi/Inkawasi) or of the pattern
   `1, 2, 1, 2, 3, 1, 2, 1, 3`.
c. KFG Excel databook `https://www.khipufieldguide.com/databook/excel_khipus/KHxxxx.xlsx` if a similar-khipu
   field is not on the HTML page.
d. Named publication: Urton & Chu, *Appendix I: Inventory of Inkawasi Khipus* (supplement to "Accounting in
   the King's Storehouse", *Latin American Antiquity*; PDF URL as cited in K020). It is the C2 source (UR266
   "Matches UR 275", K020) and an E2 source for UR260.
e. WebSearch + WebFetch (`curl` fallback; no browser) for: UR004, UR260, "KH0240", "KH0496",
   Leymebamba + khipu + Incahuasi / Inkawasi, Urton 2006 padrones / census Leymebamba, Incahuasi 9228-13B /
   Proyecto Incahuasi, and the collapsed pattern. A search snippet is never evidence: only fetched pages are.
   A 404 is recorded as unused, never quoted.

## Positive controls (method gates; looked up after this commit)
- **C1 (E1):** the KFG page of KH0616 must be retrieved (HTTP 200, non-empty) and name KH0620 or JC013 in a
  similar-khipu field. Else **E1 is method_excluded**: a silent similar-khipu field on a subject page is then
  `method_excluded` for E1, not `not_mentioned`.
- **C2 (E2):** the KFG page of KH0502 or the Urton & Chu Appendix I (or another named source retrieved) must
  be shown to state UR266 matches UR275 / KH0514. Else **E2 is method_excluded** the same way.
- Both fail → the whole audit is `method_excluded`.

## Classification (written before looking)
For each retrieved source × subject, and once for the PAIR:
- `already_paired`: a retrieved KFG page or named publication explicitly links UR004/KH0240 with
  UR260/KH0496 (similar, matching, corresponding, shared sequence/block, same object recorded twice, …).
  Quote the link.
- `mentioned_other_match`: the source discusses similarity or matches for this khipu but names a *different*
  partner, or discusses the khipu without pairing it with the other subject.
- `not_mentioned`: the source exists and does not pair them and does not list the other id.
- `source_missing`: no usable page after alternates.
- `method_excluded`: only if the relevant control failed (forced by the merge tool).

Aggregation (in `merge`): a subject is `already_paired` if any usable source pairs it; else
`mentioned_other_match` if any usable source names another partner / discusses it; else `not_mentioned`;
else `source_missing`; `method_excluded` if every source for it is in an excluded class. The **pair** is
`already_paired` if any usable source pairs them; `not_mentioned` (literature gap) if each subject has ≥ 1
usable source and none pairs them; `source_missing` if a subject has no usable source; `method_excluded` if
both controls fail. A vague geographic remark or "both are Urton records" is **not** `already_paired`.

Optional descriptive (not a test, not pairing): does the KH0240 page cite Urton (2006) / census /
*padrones*? Does either source mention small household counts 1–3?

Recording: per source, URL (and every failed URL with status), status, evidence class, subject(s), verbatim
quote (or `none`) and label, hand-recorded in `analysis/k052_records.json`; merged by
`tools/k052_lead_literature_audit.py merge` into `analysis/k052_results.json`.

## Reading rule
- `already_paired` → the lead is **known structure** (like K014's JC009/JC013), not a new find. Still not a
  decipherment; K028's selected-statistic caveat stays unless the literature itself publishes the
  correspondence (then cite it and stop claiming novelty).
- Not paired in any retrieved source → a **literature gap**: the lead stays unconfirmed; this updates
  K014's lighter "no literature found" with a controlled audit. Not evidence the pair is real.
- `source_missing` is unresolved, not counted either way.
- Same-lead caveat: this is K012's lead, not an independent sample.

## Next (depends on the result)
- already_paired: record as known structure; line 3's lead closes as published.
- literature gap: the lead stays unconfirmed; the only non-heuristic confirmation left is the held-out value
  search K028 named, which waits on new OKR khipus (data-limited). Colour-equality on this pair is closed.
- Not added to the pending OKR note unless a real cataloguing error is found.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04


---

## Results (2026-11-08, ~09:50–09:56 PT, America/Vancouver)

Retrieval by `curl` (WebFetch once, for the PUCP PDF) and WebSearch, after `69c115b`. `targets` passed (hash, id map,
K051 values gate) and wrote [`analysis/k052_targets.json`](../analysis/k052_targets.json); `context` wrote
[`analysis/k052_okr_context.json`](../analysis/k052_okr_context.json). Hand records:
[`analysis/k052_records.json`](../analysis/k052_records.json); merged by `tools/k052_lead_literature_audit.py merge` into
[`analysis/k052_results.json`](../analysis/k052_results.json). No tool change after the prereg.

### 1. Controls: both pass
- **C1 (E1, similar-khipu field): passes.** `https://www.khipufieldguide.com/catalog/KH0616.html` (200):
  "Similar Khipu: Previous (KH0620) Next (KH0618)" — names KH0620 / JC013, as K014 quoted. Reciprocal (descriptive):
  KH0620 page (200) "Similar Khipu: Previous (KH0612) Next (KH0616)".
- **C2 (E2, published match): passes on the named publication.** Urton & Chu, *Appendix I: Inventory of Inkawasi
  Khipus* ([PDF](https://static.cambridge.org/content/id/urn:cambridge.org:id:article:S1045663500008786/resource/name/S1045663500008786sup001.pdf), 200):
  row 13, UR266: "Repetition of fixed value '47.' Matches UR 275."; row 25, UR275: "Repetition of fixed value '47'.
  Matches UR266." **Disclosed:** the KFG catalogue page of KH0502 (200) does **not** name KH0514 / UR275 anywhere
  ("Similar Khipu: Previous (KH0463) Next (KH0381)"; KH0514 page: "Previous (KH0505) Next (KH0484)"). The prereg
  allowed the named publication as the C2 source, so C2 passes; but it shows that the KFG similar-khipu field can miss
  a published match, so **E1 silence is weak evidence** (descriptive; labels unchanged).

### 2. Sources × subjects

| ID | Source (status) | Class | Subject | Label | Verbatim |
|---|---|---|---|---|---|
| S1 | [KFG KH0240](https://www.khipufieldguide.com/catalog/KH0240.html) (200) | E1 | KH0240 | mentioned_other_match | "Similar Khipu: Previous (KH0237) Next (KH0270)" |
| S2 | same page, notes / bibliography | E2 | KH0240 | not_mentioned | none (11-item bibliography, no match statement) |
| S3 | [KFG KH0496](https://www.khipufieldguide.com/catalog/KH0496.html) (200) | E1 | KH0496 | mentioned_other_match | "Similar Khipu: Previous (KH0498) Next (KH0518)" |
| S4 | same page, notes / bibliography | E2 | KH0496 | not_mentioned | none (Urton & Chu 2015 pp. 519–520; Urton 2017 pp. 176, 263) |
| S5 | [KFG Excel KH0240](https://www.khipufieldguide.com/databook/excel_khipus/KH0240.xlsx) (200) | E2 | KH0240 | not_mentioned | none (cord-level recording notes only) |
| S6 | [KFG Excel KH0496](https://www.khipufieldguide.com/databook/excel_khipus/KH0496.xlsx) (200) | E2 | KH0496 | not_mentioned | none (one ChangeLog row, p20 knot query) |
| S7 | Urton & Chu, Appendix I (200) | E2 | KH0496 | mentioned_other_match | "260 U.E. 2 24 Included in large "khipu pile" found in corridor. Primary cord tied around primary cord of UR259." |
| S8 | Urton & Chu 2015, *LAA* 26(4) (abstract page only) | E2 | KH0496 | source_missing | full text not accessible; pp. 519–520 not read |
| S9 | Urton 2006, *Revista Andina* 42 ([Dialnet](https://dialnet.unirioja.es/servlet/articulo?codigo=2391294)) | E2 | KH0240 | source_missing | "Texto completo no disponible" |
| S10 | Urton 2004, *Boletín de Arqueología PUCP* 8:289–303 (download, view, DOI, repository) | E2 | KH0240 | source_missing | every URL returns an Anubis bot-check page; repository lists 0 files |

No retrieved page contains the other subject's id (KH0240 / UR004 / Leymebamba on the KH0496 side; KH0496 / UR260 /
Incahuasi / Inkawasi on the KH0240 side), and none states the pattern. Appendix I covers Inkawasi only ("Leymebamba"
does not occur). Urton 2004 is a paper on *matching accounts* among Chachapoyas and Ica khipus, so it was the most
relevant missing source for UR004; it predates the Inkawasi excavations (Appendix I project numbers carry 2013–2014),
so it could not name UR260. Search snippets of it were **not** used. Urton 2017 (print book) was not retrievable and is
not recorded as a source.

Web searches (7, listed in the records): the two subject ids, investigator codes with both sites, Leymebamba with
Inkawasi, Urton 2006, Urton 2004, UR259/UR260, and the collapsed pattern (no relevant hit at all).

### 3. Labels (merge tool)
Controls C1 ✓, C2 ✓. Source × subject counts: already_paired **0** · mentioned_other_match 3 · not_mentioned 4 ·
source_missing 3 · method_excluded 0.
- **KH0240:** mentioned_other_match (E1: KFG similar KH0237 / KH0270; E2: not_mentioned).
- **KH0496:** mentioned_other_match (E1: KFG similar KH0498 / KH0518; E2: physically tied to **UR259** in Appendix I).
- **Pair: `not_mentioned` — a literature gap.**

Descriptive, not a test and not pairing: the KH0240 page does cite Urton (2006) on census records ("Censos registrados
en cordeles con 'amarres': Padrones poblacionales … Text: 188"; paper text not read). No retrieved source says either
subject records small household counts; Appendix I says of UR259, the khipu UR260 is tied to, "All values 4 or below".

### 4. Reading
With both controls passing, no retrieved KFG page or named publication pairs **UR004 / KH0240** with **UR260 /
KH0496**. Each subject's only named partners are different khipus (KFG neighbours; UR259 for UR260). This replaces
K014's lighter "no literature found" and K028's "No source links UR004 with UR260" with a controlled audit, and it
agrees with them. It is a **literature gap**: the lead is not known structure, and it is still **not confirmed** and
not evidence that the pair is real (K028's selected-statistic caveat stands; K051's colour was degenerate). Three
sources stay unresolved (Urton & Chu 2015 full text, Urton 2006, Urton 2004), and the KFG similar field misses even a
published match, so the gap holds only for the sources we could read. Same-lead caveat: this is K012's lead.
No decipherment, no claim of a Leymebamba–Incahuasi link.

### Line 3 status
**Advanced (literature: gap).** The lead stays unconfirmed. Remaining steps: the held-out value search K028 named,
which needs khipus added to OKR after the pinned `4039ca5` (data-limited), and reading the three unresolved
publications if a readable copy appears. Colour-equality on this pair is closed (K051). Not added to the OKR note (no
cataloguing error found).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
