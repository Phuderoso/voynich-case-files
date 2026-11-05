# Data manifest (khipu expedition)

The database is not copied here (39 MB); fetch it from the source.

| File | Source | Commit | SHA-256 |
|---|---|---|---|
| `khipu.db` | [khipulab/open-khipu-repository `data/khipu.db`](https://github.com/khipulab/open-khipu-repository/blob/master/data/khipu.db) | `4039ca51f4de661d80d0160596309c983a62a9c7` (2026-08-04) | `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db` |

Cite the OKR as https://doi.org/10.5281/zenodo.18025748.

To reproduce: download `khipu.db` into this folder, then from `expeditions/khipu/` run
`python3 tools/k001_sum_cords.py data/khipu.db 5000` (about 4.5 minutes, needs numpy).
