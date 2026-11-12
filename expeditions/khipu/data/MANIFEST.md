# Data manifest (khipu expedition)

The database is not copied here (39 MB); fetch it from the source.

| File | Source | Commit | SHA-256 |
|---|---|---|---|
| `khipu.db` | [khipulab/open-khipu-repository `data/khipu.db`](https://github.com/khipulab/open-khipu-repository/blob/master/data/khipu.db) | `4039ca51f4de661d80d0160596309c983a62a9c7` (2026-08-04) | `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db` |

Cite the OKR as https://doi.org/10.5281/zenodo.18025748.

To reproduce: download `khipu.db` into this folder, then from `expeditions/khipu/` run
`python3 tools/k001_sum_cords.py data/khipu.db 5000` (about 4.5 minutes, needs numpy).

## KFG data (from K068 on; primary source for new work)
| Source | Version | Files | Hashes |
|---|---|---|---|
| Khipu Field Guide per-khipu Excel, `https://www.khipufieldguide.com/databook/excel_khipus/<KH>.xlsx` (ids from `/sketchbook/index.html`) | fetched 2026-11-11; Excel write dates 2026-09-08 / 2026-09-10 | 695 of 697 listed (KH0085, KH0109 404: split into lettered parts) | per file in [`analysis/k068_kfg_manifest.tsv`](../analysis/k068_kfg_manifest.tsv) |
| Citable release: [khipufieldguide/data-science-khipu-article](https://github.com/khipufieldguide/data-science-khipu-article) `data/KFG_DB_Excel` | v2.1.0 (2024-01-09) | 651 entries | not used (older) |

KFG data © Ashok Khosla, Manuel Medrano, Karen Thompson and the KFG team (MIT licence in each file). Build the local store with
`python3 tools/k068_kfg_crosswalk.py <xlsx dir> data/khipu.db <out.db>` (about 9 s).
