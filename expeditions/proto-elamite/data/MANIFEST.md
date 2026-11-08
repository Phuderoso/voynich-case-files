# Data manifest (proto-Elamite expedition)

Nothing from CDLI is copied here; `tools/pe001_totals.py fetch` downloads the pinned files and verifies them.

| File | Source | Commit | SHA-256 |
|---|---|---|---|
| `cdliatf_unblocked.atf` | [cdli-gh/data](https://github.com/cdli-gh/data) (Git LFS; daily dump, last update Aug 2022) | `d66b12b065af39a57d640576b4c7e098db5dac7f` (2023-10-11) | `2896ec253767fa07fcaa5424af6fc25d6a047dc30b99c95f99d57ce75384d836` |
| `cdli_cat.csv` | same | same | `2e3232f75325b61c4d1e788d4d8c074c6230a947aed422110f9f35a6e353d09c` |
| `pe.atf` (derived) | catalogue `period` contains "Proto-Elamite": 1 729 ids, 1 585 with ATF | built by `fetch` | `5c4860abe9d04ee4677875248c52e768d4b9fd026fa30878ce8e0425888159a6` |

Source: Cuneiform Digital Library Initiative, https://cdli.mpiwg-berlin.mpg.de/ . Cite CDLI and the primary
publications (MDP 6, 17, 26, 26S, etc.) listed in the catalogue.

Reproduce: from `expeditions/proto-elamite/` run `python3 tools/pe001_totals.py fetch` then `python3 tools/pe001_totals.py run`.
