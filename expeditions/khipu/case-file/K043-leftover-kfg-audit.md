# K043 · Are the 10 leftover singleton-total pendants already counted? (README line 2, literature audit)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: results appended** (pre-registration written and pushed first as `c759929`, before any of the nine
target Khipu Field Guide pages or the KH0359 control page was fetched for this cycle).

## Why
K042 located the leftover whole-group-sum count excess in singleton-total pairs: G_s = 10 against a
null mean of 1.7338 (p = 0.00009999, Monte Carlo floor; FPR 0.005; power 1.00), while G_ns = 13 sat on
its chance mean (p = 0.4608). K025 had already noted that UR119/KH0359's whole-group totals are counted
by the Khipu Field Guide ("Ascher sums"), so they were known structure, not a new find. K043 asks the
same question of the leftover ten: are any of them already counted as whole-group / adjacent-group
totals in the Field Guide or a named publication, or are they unpublished observations of the same form?

This is a **literature audit, not a statistical hypothesis test**. It runs no Monte Carlo. It creates no
new named discovery and does not replicate K040/K042 statistically (same data: these are K042's ten).
No decipherment is claimed.

## Data (locked to K042)
The 10 pendants of `analysis/k042_results.json` → `observed.catalogue_Gs` (nine khipus; KH0424/UR186
holds two). `tools/k043_leftover_kfg_audit.py targets` reads that JSON and **refuses to run** if the
catalogue is not length 10, if any entry is not singleton-total, or if the set of OKR ids differs from
{KH0082, KH0113, KH0235, KH0246, KH0323, KH0424, KH0460, KH0482, KH0583}. It writes
`analysis/k043_targets.json`.

| Khipu | Investigator | Cord ordinal | Value | Side | Group length |
|---|---|---|---|---|---|
| KH0082 | AS069 | 286 | 18 | L | 7 |
| KH0113 | UR1100 | 1 | 259 | L | 6 |
| KH0235 | AS215 | 12 | 14 | L | 4 |
| KH0246 | UR010 | 91 | 112 | L | 7 |
| KH0323 | UR087 | 7 | 15 | R | 6 |
| KH0424 | UR186 | 24 | 75 | R | 6 |
| KH0424 | UR186 | 58 | 596 | R | 6 |
| KH0460 | UR222 | 1 | 17 | L | 6 |
| KH0482 | UR246 | 25 | 288 | R | 8 |
| KH0583 | HP052 | 7 | 40 | L | 2 |

(Side L = the pendant sums the group to its left in K025's convention as recorded in K042's JSON;
cord ordinals are OKR ordinals, which may not equal the Field Guide's cord labels — a mismatch of
naming is recorded, not silently resolved.)

## Sources (in order)
a. Khipu Field Guide catalogue page, URL pattern used in K014/K025:
   `https://www.khipufieldguide.com/catalog/KHXXXX.html` (OKR id). If 404/empty, try the obvious
   alternates (investigator-code page name, the catalogue index, a site search result) and record each
   attempt and its status.
b. On that page: any Ascher-sum, sum-relationship, notes, or similar-khipu fields.
c. If the page is thin or missing: a web search for the investigator code (AS069, UR1100, AS215,
   UR010, UR087, UR186, UR222, UR246, HP052) plus "sum" / "total" / "Ascher".
Tools: WebFetch and WebSearch (no browser this cycle; `curl` as fallback if the fetch provider is
blocked). Never record what a page says without a retrieved copy.

## Positive control (method gate)
KH0359 / UR119. K025 and the coverage table say the Field Guide lists it with 65 "Ascher sums"
(`https://www.khipufieldguide.com/catalog/KH0359.html`). Looked up **after** this prereg commit, before
or with the targets. If that page cannot be retrieved, or does not mention Ascher sums / whole-group
totals, the method is **excluded** and every leftover pendant is reported `method_excluded`
(not `not_mentioned`).

## Classification per pendant (written before looking)
- `already_counted`: the KFG page or a named publication explicitly describes **this** pendant
  (matching cord/position and/or the exact value as the total of the adjacent group, or an
  Ascher / Field Guide sum that is clearly this cord) as a whole-group / adjacent-group total.
- `mentioned_other_sum`: the page discusses sums on this khipu but does not identify this pendant as
  such a total. A generic "Ascher sums" count or list that cannot be matched to this cord/value is
  this label, **not** `already_counted`.
- `not_mentioned`: the page (or equivalent source) exists and does not mention this total.
- `source_missing`: no usable KFG page or equivalent could be retrieved after trying alternates.
- `method_excluded`: only if the KH0359 control fails.

Optional secondary label (descriptive, not a test): whether the khipu page mentions any sums at all.

Recording: for each pendant, the URL that worked (or each failed URL with status), retrieval status,
and a short verbatim quote (or `none`). Hand-recorded in `analysis/k043_records.json`, then merged by
`tools/k043_leftover_kfg_audit.py merge` into `analysis/k043_results.json` (the merge enforces
`method_excluded` for all ten if the control failed).

## Reading rule
Count how many of the 10 are `already_counted` vs not.
- If some are already counted: say so and treat them as known structure (like UR119).
- If none are: the leftover singleton-totals are not yet recorded as Ascher/KFG whole-group totals —
  a **literature gap**, not a decipherment.
- `source_missing` pendants are reported as unresolved and are not counted on either side.
Same-data caveat: these are K042's ten, not an independent sample.

---

## Results (2026-11-08, ~03:55–04:10 PT)

Retrieval by `curl` and WebFetch (WebSearch for source c). Hand records:
`analysis/k043_records.json`; merged by `tools/k043_leftover_kfg_audit.py merge` into
`analysis/k043_results.json`. **Disclosed addition after the prereg:** a `context` mode in the same tool
(read-only `khipu.db` read) prints each target's OKR value and the OKR values of the group it sums
(`analysis/k043_okr_context.json`), so the cord-by-cord comparison is reproducible. Cord mapping: OKR
`CORD_ORDINAL` n = KFG pendant `pn`, checked against the KFG Excel files
(`https://www.khipufieldguide.com/databook/excel_khipus/KHxxxx.xlsx`, CordGroups and Cords sheets); KFG
`gXpY` labels mapped through the CordGroups ranges. For every target, KFG's own cord values for the
summed group equal the OKR values.

### 1. Control (KH0359 / UR119): passes
- `https://www.khipufieldguide.com/catalog/KH0359.html` (200): "# Ascher Sums (pps, ips, cps, sps,...): 65 (38, 11, 16, 0,...)" — matches K025's 65.
- `…/notebook/fieldmarks/colored_pendant_sum/html/KH0359.html` (200) lists all four K025 whole-group totals
  at cord level, e.g. "g15p1 : 416 W 416 6 g16p1: 19 W + g16p2: 74 W + g16p3: 44 W + g16p4: 221 W + g16p5: 30 W + g16p6: 28 W"
  (also g17p1 = 390, g19p1 = 406, g21p1 = 481, each the six cords of the next group).
- So the method is not excluded, and it can match a pendant at cord level.

### 2. Per-pendant classification

| Khipu | Inv. | OKR cord | Value | KFG cord | KFG attach. | Label | Source (status 200) | Verbatim |
|---|---|---|---|---|---|---|---|---|
| KH0082 | AS069 | 286 | 18 | g75p1 | U | **already_counted** (span) | [pendant_pendant_sum/KH0082](https://www.khipufieldguide.com/notebook/fieldmarks/pendant_pendant_sum/html/KH0082.html) | "g75p1 : 18 W 18 4 g76p2: 10 W + g76p3: 0 W + g76p4: 0 W + g76p5: 8 W" |
| KH0113 | UR1100 | 1 | 259 | g1p1 | U | **already_counted** | [pendant_pendant_sum/KH0113](https://www.khipufieldguide.com/notebook/fieldmarks/pendant_pendant_sum/html/KH0113.html) | "g1p1 : 259 W 259 6 ❽ g2p1: 81 W + g2p2: 38 W + g2p3: 31 B + g2p4: 42 W + g2p5: 31 DB + ∞ g2p6: 36 B" |
| KH0235 | AS215 | 12 | 14 | g7p1 | U | **already_counted** | [pendant_pendant_sum/KH0235](https://www.khipufieldguide.com/notebook/fieldmarks/pendant_pendant_sum/html/KH0235.html) | "g7p1 : 14 W:DB 14 4 ❽ g8p1: 1 W:DB + g8p2: 11 W:DB + g8p3: 1 W:DB + g8p4: 1 W:DB ❽" |
| KH0246 | UR010 | 91 | 112 | g16p1 | R | **already_counted** | [pendant_pendant_sum/KH0246](https://www.khipufieldguide.com/notebook/fieldmarks/pendant_pendant_sum/html/KH0246.html) | "g16p1 : 112 W 112 7 g17p1: 2 KB + g17p2: 40 W + … + g17p7: 5 AB:GG" |
| KH0323 | UR087 | 7 | 15 | g2p1 | **T** | **already_counted** (summary row) | [analyses/sum_top_cords](https://www.khipufieldguide.com/notebook/analyses/sum_top_cords.html) | "KH0323 2 15 15 16" |
| KH0424 | UR186 | 24 | 75 | g8p1 | **T** | **already_counted** (summary row) | [analyses/sum_top_cords](https://www.khipufieldguide.com/notebook/analyses/sum_top_cords.html) | "KH0424 3 250 75 596" |
| KH0424 | UR186 | 58 | 596 | g17p1 | **T** | **already_counted** (summary row) | [analyses/sum_top_cords](https://www.khipufieldguide.com/notebook/analyses/sum_top_cords.html) | "KH0424 3 250 75 596" |
| KH0460 | UR222 | 1 | 17 | g1p1 | V | **already_counted** | [pendant_pendant_sum/KH0460](https://www.khipufieldguide.com/notebook/fieldmarks/pendant_pendant_sum/html/KH0460.html) | "g1p1 : 17 HB 17 6 g2p1: 6 W + g2p2: 4 W + g2p3: 1 W + g2p4: 2 W + g2p5: 1 W + g2p6: 3 W ❽" |
| KH0482 | UR246 | 25 | 288 | g6p1 | **T** | **already_counted** | [colored_pendant_sum/KH0482](https://www.khipufieldguide.com/notebook/fieldmarks/colored_pendant_sum/html/KH0482.html) | "g6p1 : 288 AB 288 8 g5p1: 8 AB ∞ + g5p2: 91 AB + … + ∞ g5p8: 9 AB"; also "KH0482 2 302 288 316" |
| KH0583 | HP052 | 7 | 40 | g5p1 | R | **already_counted** | [pendant_pendant_sum/KH0583](https://www.khipufieldguide.com/notebook/fieldmarks/pendant_pendant_sum/html/KH0583.html) | "g5p1 : 40 W:RM 40 2 g6p1: 20 W:RM + g6p2: 20 W:RM" |

(Quoted rows are the KFG sum-detail tables flattened to text: sum cord : value colour, value, number of summands, summands. The Sum Top Cords row columns are: khipu, number of sum top cords, mean, min, max top-cord value, …)

Qualifications, disclosed:
- **KH0082:** KFG lists the sum over g76p2–p5, the nonzero span of the adjacent 7-cord group (g76p1, p6, p7 = 0 in KFG's Cords sheet). Same cord, same value, same group total; KFG names the span, not the full group.
- **KH0323, KH0424 (×2):** not in those khipus' pendant-pendant / group-group sum tables. They are matched through KFG's **Sum Top Cords** analysis, whose summary row gives count, mean, min and max. KH0424's top cords are 89, 110, 75, 79, 50, 71, 596 (KFG Cords sheet), so min 75 and max 596 identify p24 and p58 uniquely (3 × 250 − 75 − 596 = 79 = p32). KH0323's only top cord valued 15 is p7 (its group p1–p6 = 1+1+10+1+1+1). That page defines the search ("top cord values matching the sum of their adjacent group cords"; the code excerpt tags a one-cord group next to a group whose sum matches). Evidence grade: summary-row value match, not a cord-level listing.
- A WebSearch index snippet of `…/group_group_sum/html/UR186.html` showed 75 and 596 as group sums, but that URL (and the KH0424 variant) returned **404** on direct fetch; it is not used as evidence.
- Named publications (e.g. Medrano & Urton 2018 on the Santa Valley set including KH0323; Locke 1923/1928 in KH0424's bibliography) were not read for these cords; the KFG pages were enough to decide.

### 3. Counts
already_counted **10** · mentioned_other_sum 0 · not_mentioned 0 · source_missing 0 · method_excluded 0.
(6 cord-level listings of the full group, 1 cord-level listing of the nonzero span, 3 summary-row value matches; KH0482 has both.)

Secondary descriptive (not a test): every one of the nine khipu pages states a nonzero Ascher-sum count
(KH0082 682, KH0113 26, KH0235 11, KH0246 172, KH0323 101, KH0424 16, KH0460 17, KH0482 3, KH0583 26).
Four of the ten pendants are **top cords** in KFG (attachment `T`: KH0323 p7, KH0424 p24 and p58, KH0482 p25)
but carry `ATTACHMENT_TYPE = 'U'` in OKR `khipu.db` @ `4039ca5` (where they sit as level-1 cords). KFG's Sum Top
Cords page: "A total of 86 sum top cords exist over 22 khipus with sum top cords".

### 4. Reading
All ten leftover singleton-total pendants are **already counted** by the Khipu Field Guide — seven in its
pendant-pendant / colored-pendant sum tables at cord level, three (plus KH0482 again) as Locke-style sum top cords.
So the leftover count excess that K040–K042 located is **known structure, like UR119**, not a literature gap and
not a new find. Part of it is Locke's classic top-cord sum (a top cord that totals its group; the KFG page dates the
discovery to 1926). Our level-1 detector picks those up because in OKR they are level-1 cords with
attachment `U`, while KFG marks them `T`. Same-data caveat stands;
nothing deciphered. Line 2's leftover question is closed as answered by the literature.

### Next
Proposed K044 (light, non-testing): line 4 — put the K026 per-category table into the OKR data-quality note
draft, and add, as a disclosed descriptive row, the KFG-`T` / OKR-`U` attachment mismatch for these four cords
(check first whether KFG's change log or OKR documents the mismatch before calling it a data-quality fact).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
