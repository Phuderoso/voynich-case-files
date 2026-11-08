# K044 · Four KFG top cords stored as 'U' in OKR, and the K026 table for the note (README line 4)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registered** (this file and `tools/k044_tu_attachment_audit.py` are written and will be
pushed before any changelog, about, or updates page is fetched, before any new OKR schema query, and
before the outreach draft is edited).

## Why
K043 found that four of the ten leftover singleton-total pendants are top cords in the Khipu Field
Guide (attachment `T`) but carry `ATTACHMENT_TYPE = 'U'` in OKR `khipu.db` @ `4039ca5`. Line 4 of the
expedition README asked for two note-draft updates: fold K026's per-category E/L table into the
pending OKR data-quality note, and add a descriptive row for those four cords — **only after** checking
KFG's change log (and OKR's own docs) so a known, corrected, or documented encoding difference is not
filed as a new unflagged error.

This is a **literature / schema audit, not a statistical hypothesis test**. It runs no Monte Carlo.
It creates no new named discovery and does not re-open line 2. No decipherment is claimed. The
physical attachment of any cord is the museum's and the original recorder's call, not ours.

## Data (locked to K043)
The four pendants of `analysis/k043_results.json` whose `kfg_attachment` is `T`:

| Khipu | Investigator | Cord ordinal | Value | KFG cord (from K043) |
|---|---|---|---|---|
| KH0323 | UR087 | 7 | 15 | g2p1 |
| KH0424 | UR186 | 24 | 75 | g8p1 |
| KH0424 | UR186 | 58 | 596 | g17p1 |
| KH0482 | UR246 | 25 | 288 | g6p1 |

`tools/k044_tu_attachment_audit.py targets` reads that JSON and **refuses to run** if it does not
find exactly these four `(okr, cord_ordinal, value)` rows with `kfg_attachment == "T"`, or if any
other of K043's ten pendants is also marked `T`. It writes `analysis/k044_targets.json`.

OKR snapshot: `khipu.db` @ `4039ca5` (the same file used since K001). K043's published statements
that these four are `T` in KFG and `U` in OKR are taken as the starting observation to check, not as
a result of this cycle.

## Sources (in order; stop a branch when a usable page is in hand, but finish the list of branches)
**Branch A — KFG change log / updates**, tried in this order and recorded with HTTP status:
1. `https://www.khipufieldguide.com/` (look for a changelog, news, updates, or about link).
2. Obvious path guesses: `/changelog`, `/changelog.html`, `/news`, `/news.html`, `/updates`,
   `/updates.html`, `/about`, `/about.html`, `/notebook/`.
3. A web search for `khipu field guide changelog` / `khipu field guide updates` / `khipu field guide change log`
   (record the query and which URLs were then fetched).
4. Fallback: any KFG GitHub or databook README / HISTORY / CHANGELOG that a search actually returns.
   Commit messages are used only if a named file or release note is retrieved; no inference from a
   search-index snippet alone.

**Branch B — OKR documentation of attachment types**, tried in this order:
1. The Open Khipu Repository README and any data-dictionary / schema / codebook file at
   [khipulab/open-khipu-repository](https://github.com/khipulab/open-khipu-repository) that mentions
   `ATTACHMENT_TYPE`, top cords, or a T/U mapping.
2. Open GitHub issues on that repo that mention attachment type or top cords (search; do not file).

**Branch C — schema context (descriptive, after this prereg is pushed):**
`tools/k044_tu_attachment_audit.py schema` queries `khipu.db` read-only for (i) the distinct
`ATTACHMENT_TYPE` values and their counts among cords, and (ii) the four target rows' OKR
`ATTACHMENT_TYPE`, `CORD_LEVEL` / cluster fields actually present, and `knot_value_type`. This is
context for the reading rule below, not a test.

**Branch D — KFG confirmation of `T`:** re-fetch each khipu's KFG Excel Cords sheet
(`https://www.khipufieldguide.com/databook/excel_khipus/KHxxxx.xlsx`) or the already-used Sum Top
Cords page only as a confirmation that K043's `T` label is still what the live file says. A 404 or
parse failure for a sheet is recorded; it does not by itself change the changelog classification.

Tools: WebFetch and WebSearch (`curl` as fallback if the fetch provider is blocked). Never record
what a page says without a retrieved copy. No browser this cycle.

## Classification per cord (written before looking)
Changelog / docs label, one per cord (the four may share one if the finding is general):

- `changelog_corrected`: a retrieved changelog or OKR note says this cord's (or this khipu's)
  attachment was fixed after our OKR snapshot `4039ca5`, or that KFG later changed `T` to match OKR.
- `changelog_notes_mismatch`: a retrieved changelog or OKR/KFG document explicitly says OKR and KFG
  store attachment differently for this cord, these khipus, or top cords in general (a documented
  encoding difference).
- `no_changelog_mention`: a usable changelog, about/updates page, or OKR schema note was retrieved,
  and it does not mention these cords, these khipus' attachments, or a general T/U (or top-cord)
  mapping difference.
- `source_missing`: no usable changelog, updates/about surrogate, or OKR attachment documentation
  could be retrieved after the branches above.

Optional secondary label (descriptive, not a test): OKR schema shape, from the `schema` query —
`okr_has_T` (OKR stores at least one cord with `ATTACHMENT_TYPE = 'T'`) or `okr_never_T`.

Recording: `analysis/k044_records.json` (hand-recorded after the fetches), then merged by
`tools/k044_tu_attachment_audit.py merge` into `analysis/k044_results.json`. The merge refuses
unknown labels and refuses a set of cords other than the locked four.

## Reading rule (for the note draft)
- If any cord is `changelog_corrected`: do **not** add that cord as a current data-quality fact;
  record it as already addressed.
- If any cord is `changelog_notes_mismatch`, or the documents describe a general T↔U / top-cord
  mapping: add a descriptive row citing that document, as a **known encoding difference**, not as
  an unflagged error.
- If the four are `no_changelog_mention` **and** OKR has some `'T'` values elsewhere: add a
  descriptive row as a **candidate data-quality observation** (four unflagged recording differences).
  Do not call them confirmed physical errors; attachment is not decidable from values alone.
- If the four are `no_changelog_mention` **and** OKR never stores `'T'`: add a descriptive row as a
  **schema-mapping observation**, with the four as examples. Do not call them isolated errors.
- If the four are `source_missing`: report unresolved; **do not** add the T/U row as a confirmed
  data-quality fact. The K026 table may still be folded into the draft (that table is already
  published in [K026](K026-el-knot-audit.md) and does not depend on the changelog).

The K026 fold-in is not a test: copy the noteworthy categories (L-turn0 186, L-turn10+ 155,
L-shift 117, E-type 43, E-zero 22) and the concentration line (AS090/N2 holds 98 of 579) into
[outreach/2026-11-05-okr-duplicates-draft.md](../outreach/2026-11-05-okr-duplicates-draft.md),
clearly marked as flags rather than corrections. That edit happens after this prereg is pushed.

Same-data caveat: these four cords are K043's, which are K042's. Nothing here is an independent
replication of the leftover count.

## Next after this cycle
Whatever the changelog says, line 4's remaining work is to file the pending OKR note when a
connector can do so without stacking an approval form. No further line-2 test.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
