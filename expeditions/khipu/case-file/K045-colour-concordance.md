# K045 · Colour-code concordance: Ascher, Urton and Pereyra/HP codes in OKR (README line 6)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Status: pre-registration** (written and pushed together with `tools/k045_colour_concordance.py`
before any colour documentation beyond K021/K044 was fetched, before the OKR colour dictionary was
dumped, and before any query of which colour codes the named khipus use).

## Why
Line 6's remaining named step (queued by K019 and K021) is a colour-code concordance before colour
names are compared **across** khipus. K021 deliberately used only within-khipu equality "so the test
does not depend on how different investigators named colours (the concordance problem noted in K019)".
The three K018/K019 confirmed pairs all cross recorder systems (metadata already published, cited
here as motivation only, not as a result):

| Khipu | Investigator / origin | Museum | `CREATED_BY` |
|---|---|---|---|
| KH0097 | UR1084, orig AS084 | Quai Branly (Paris) | tania |
| KH0586 | HP055 | MNAAHP (Lima) | julia |
| KH0192 | AS175 / UR1175 | Berlin VA42518 (Pachacamac) | katie |
| KH0470 | UR233 | Berlin VA 63038 b (Huacho) | gurton |
| KH0469 | UR232 | Berlin VA63038(B) (Huacho) | gurton |

So KH0097·KH0586 is Ascher(-Urton) vs Pereyra/HP, and both Berlin pairs are Ascher-recorded KH0192 vs
Urton-recorded KH0469/KH0470. A same-code equality test on them would break the expedition's own rule
unless the codes are first shown to be comparable. **K045 classifies code vocabularies and published
mappings only.** It computes no colour agreement between aligned cords (that would be K046+, and only
on pairs this cycle gates as `co_mappable`). No Monte Carlo, no new named discovery, no decipherment,
and line 2 stays closed.

## Question
Can Ascher, Urton and Pereyra/HP colour codes in OKR be mapped to each other from published sources
and the OKR codebook, tightly enough that a later cycle may compare colours across the K018/K019 pairs?

## Data
OKR `khipu.db` @ `4039ca5` (read-only URI), same file as since K001. Colour tables (schema peek only,
for design): `ascher_cord_color` (`FULL_COLOR`, `COLOR_CD_1..5`, `OPERATOR_1..5`, `RANGE_BEG`,
`PIGMENTATION_CD_*`), `ascher_color_dc` (`AS_COLOR_CD`, `COLOR_DESCR`, `ISCC_NBS_NUM`, RGB),
`color_operator_dc`. `ascher_canuto_color` / `ascher_canutito_color` are secondary and only noted.

- **Cord colour (K021 field):** `FULL_COLOR` of the `ascher_cord_color` row with smallest `RANGE_BEG`
  (ties: smallest `color_id`); its components are that row's non-empty `COLOR_CD_1..5`. Cords with no
  colour row are `no_colour`.
- **Level-1 pendants:** `cord.CORD_LEVEL = 1` (as K019/K021).
- **Token normalisation:** strip whitespace; compare case-sensitively. Case-insensitive near-matches are
  reported descriptively only.
- **Recorder proxy (pre-registered):** leading letters of `khipu_main.orig_inv_num` if non-empty, else of
  `INVESTIGATOR_NUM`, uppercased; `AS`, `UR`, `HP` kept, anything else `other:<prefix>`. `CREATED_BY` is
  reported beside it. Names are table values; nothing is read into them.

## Sources (try in order; record HTTP status; never invent what a page says)
- **Branch A — OKR codebook** (after this push): `tools/k045_colour_concordance.py dump` →
  `analysis/k045_dictionary.json` (`ascher_color_dc`, `color_operator_dc`).
- **Branch B — Khipu Field Guide colour documentation:** start at <https://www.khipufieldguide.com/>
  (guidebook, databook, Excel specification); web searches `khipu field guide color codes`,
  `ascher color code khipu`, Urton colour recording, Pereyra colour. Path guesses allowed if recorded.
- **Branch C — investigator colour lists:** Ascher & Ascher colour abbreviations; Urton (and
  collaborators); Pereyra / HP / Museo Nacional recording notes. Retrieved pages/files only; primary and
  project pages preferred over blogs.
- **Branch D — OKR repo docs** (<https://github.com/khipulab/open-khipu-repository>: README, schema,
  codebook) for how investigator colours were ingested into the `ascher_*` tables.

Everything used is typed into `analysis/k045_published_mappings.json`: a `sources` list (URL, HTTP
status, what was found) and `mappings` rows `{system_a, code_a, system_b, code_b, relation, source,
verbatim}` with `relation ∈ {equivalent, related, not_equivalent}`. The tool has no network access.

## Classification rules (written before looking)
Unit: each distinct component token used by each recorder-proxy system, classified against the shared
reference = OKR `ascher_color_dc` (the single DB-wide codebook); and each mapping row.

- `same_dictionary`: the token is an `AS_COLOR_CD` of `ascher_color_dc` (identical OKR/Ascher token; no mapping needed).
- `exact_published_equivalent`: a retrieved source states the token names the same colour as one
  reference code (explicit equivalent, same ISCC-NBS, or same description), and no source disagrees.
- `related`: a retrieved source says similar / same hue family, not identical.
- `conflicting`: retrieved sources disagree (equivalents to two different codes, or equivalent vs not).
- `unmapped`: a usable colour dictionary/page for that system was retrieved and the token is not equated.
- `source_missing`: no usable colour-code documentation was retrieved for that system.

The classifier applies these in the order above (same_dictionary first). Two codes from different
systems are usable-equal only if both resolve to the **same** reference code.

Secondary system-level note (descriptive, carried as a caveat to K046): whether a retrieved source
documents that the system's colours were recorded in, or translated into, Ascher-style codes when
ingested (`ingest_documented`) or whether only the OKR codebook is available (`okr_codebook_only`).

## Reading rule (written before looking)
- A later cross-khipu colour-equality test may use a pair of codes only if their mapping is
  `exact_published_equivalent` or `same_dictionary`.
- `related`, `conflicting`, `unmapped`, `source_missing` are **not** usable as equal.
- Operators (`-` barber pole, `:` mottled, etc.): two `FULL_COLOR` strings match under the concordance
  only if every component maps as usable **and** the operator sequence is identical (`-` is not `:`).
- If a system is `source_missing` overall, every cross-system comparison involving it is not testable
  until sources appear.

## Coverage census (exact counts; after this push; NOT an agreement test)
1. Corpus: distinct `FULL_COLOR` strings; distinct component tokens; how many are in `ascher_color_dc`.
2. By recorder proxy: distinct codes, colour rows and cords per proxy; tokens outside the dictionary.
3. Five named khipus (six pair-slots): their `FULL_COLOR` strings and tokens, and the fraction of each
   khipu's coloured level-1 pendants whose every component token is usable (`exact_published_equivalent`
   or `same_dictionary`) into the shared reference. Vocabulary coverage, not whether aligned cords share colour.
4. **Pair gate for a future test:** a K019 pair is `co_mappable` if both members have colour data and
   ≥ **50 %** (threshold fixed now) of coloured level-1 pendants on **each** side are fully usable into
   the shared reference; otherwise `not_co_mappable`. Observed fractions reported.
5. Secondary descriptive: number of `FULL_COLOR` values containing an operator.

## Controls
- **Planted fixture (schema):** `tools/k045_colour_concordance.py fixture` — fake rows for an exact
  equivalent, a related code, a conflicting code (two sources), plus same_dictionary, unmapped,
  source_missing, pair-level cases and the operator rule (`-` ≠ `:`). `census` refuses to write results
  if any fixture case fails. (Fixture passes on the committed tool; it touches no data.)
- **Positive control on real data:** `ascher_color_dc` must contain `W` and `AB`; if either is missing,
  label `schema_unexpected` and do not trust coverage numbers.

## Integrity notes
- K019's results JSON contains a descriptive aligned-cord colour field. It is not read for K045, not
  used as an expectation, and K045 computes nothing of the kind.
- Same-data caveat: the pairs are K018/K019's; nothing here re-tests their value correspondence.

## Next after this cycle
If at least one pair is `co_mappable`: K046 = pre-registered cross-khipu colour-agreement test on the
co_mappable pairs only, with the operator rule and a within-khipu shuffle null. If none: more sources.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
