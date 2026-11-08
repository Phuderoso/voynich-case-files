# K043 · Are the 10 leftover singleton-total pendants already counted? (README line 2, literature audit)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registration only, no results yet.** Written and pushed before any of the nine target
Khipu Field Guide pages (or the KH0359 control page) was fetched for this cycle.

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

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
