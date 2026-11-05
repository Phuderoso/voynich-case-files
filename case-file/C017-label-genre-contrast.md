# C017 — Expedição 17: Two Kinds of Name Tags. Do drawing-element labels differ from free-standing labels, page by page?

**Status:** pre-registered. This file, the design outputs and all tools are committed **before** the counted run;
the commit sha and time are recorded in the results section appended below.
**Approach family:** label vocabulary (third cycle; C015, C016). Changed design: the **page**, not the word, is the unit
of the null; **label type contrast** instead of labels vs their own page. The next cycle (C018) must open a new family.

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Question
C016 found that the labels on drawing elements (C015's types `Ln Lt Lz Ls La Lc Lf Lp` and the Rosettes) start with
`o` far more often than their pages' running text, while the free-standing `L0` labels did not. That was a reading of
**two separate tests**, and both used a word-level null in which every label word is an independent draw. Labels on
one page share a scribe, a drawing and a moment of writing, so the word-level null may overstate the evidence, and
the free-standing set is really only a few pages (f67r2 and f69r hold 94 of its 136 tokens).

**Question:** is the label-minus-own-page excess of drawing-element labels different from that of free-standing labels
when the **page** is the unit of chance? If yes for `o`-initial words in both transcriptions, "drawing-element labels
are a genre" becomes a tested claim.

## What I already know (disclosed)
Both label sets were analysed in C015/C016, so this is **not** a fresh sample. From C016 the expected sizes are about
A-excess +0.26 (ZL C015 loci: 0.608 vs 0.349) and B-excess +0.02 (D1: 0.279 vs 0.263) for `o_init`, so a contrast of
about +0.24 is expected. What is new is the inference: a page-level null, and the Takahashi (IT2a) reading of the
free-standing labels, whose features have **never** been computed (C016's D2 covered only the C015 loci).

## Data
| Set | File (version, sha256) | A = drawing-element units (tokens) | B = free-standing units (tokens) |
|---|---|---|---|
| **ZL** | `data/ZL3b-n.txt`, ZL "Version 3b of 13/05/2025", bf5b6d4a…beccafc | 47 (954: BIO 119, ROS 152, AZ 440, PP 243) | 9 (136: f2r 3, f11v 1, f57v 5, f67r2 47, f67v1 16, f68v3 2, f69r 47, f75v 6, f76r 9) |
| **IT** | `data/IT2a-n.txt`, Takahashi "Version 2a of 02/02/2023 modified 25/06/2025", 7f27a8b0…3f536fb5 | 45 (820: BIO 122, AZ 450, PP 248; no fRos in this file) | 7 (127: f57v 5, f67r2 42, f67v1 14, f68v3 2, f69r 49, f75v 6, f76r 9) |

- A **unit** is a (page, label class) block: classes BIO (`Ln Lt`), ROS (`L0` on fRos), AZ (`Lz Ls La`), PP (`Lc Lf Lp`),
  FREE (`L0` elsewhere). f49v and f66r (marginal columns of single glyphs) are excluded a priori, as in C016; `Lx`
  is not used. Three pages carry both A and B units (ZL f2r, f67r2, f75v; IT f67r2, f75v).
- Cleaning, glyph units and features as C016 (`tools/c016_common.py`): first alternative reading, uncertain spaces split,
  `?` words dropped, `ch sh cth ckh cph cfh` one unit. Running text = non-label loci (`P C R`) of the page; a page with
  fewer than 2k running tokens uses the pooled running text of all counted label pages (ZL f65r, f67r2, f68r1;
  IT f65r, f68r1).

## Statistic and null
- Unit excess for feature f: e_u = mean f over the unit's label tokens − mean f over its page's running text.
- **Contrast C = Ē_A − Ē_B**, each a token-weighted mean of unit excesses.
- **Null: size-blocked page-level permutation** (R = 9,999): the A/B labels are permuted among units, but only within
  blocks of similar label count k ∈ [1,3], [4,7], [8,12], [13,19], [20,29], [30,+) (ZL B units per block 3,2,1,1,0,2;
  IT 1,2,1,1,0,2). Two-sided p = min(1, 2·min(p_lo, p_hi)), direction A>B or A<B.
- Features: `o_init`, `len`, `y_fin`, `q_init`, `gallows` (as C016).

## Design step (already run, published with this file; pseudo-labels only)
No feature of any real label word was computed in the design. Pseudo-labels are running-text tokens of each unit's
own page; planted shifts of size Δ are written into them with C016's planter, **plus a unit-level random effect
N(0, τ)** to imitate page-to-page variation (τ = 0.10 for rates, 0.5 units for length; fixed before the design).
"A>B" plant raises the A units by Δ, "A<B" plant raises the B units by Δ. 100 replicates per cell, α = 0.0035.

Three design runs, all published:
1. `tools/c017_power_design_run1.py` → `analysis/C017_power_design_run1_superseded.json`: unblocked permutation; the
   "down" plant lowered A, which a rate near its floor cannot follow (e.g. IT `o_init` 0.74 at Δ 0.4); a heterogeneity
   test among A classes had false-positive rates up to 0.15 at 0.05. Superseded.
2. `analysis/C017_power_design_run2_superseded_partial.json`: "A<B" = raise B; stopped after 4 cells because the
   unblocked permutation's FPR at 0.05 was 0.105 (ZL `o_init`) and 0.115 (ZL `len`).
3. Calibration probe (`tools/c017_calibration_probe.py`, `analysis/C017_calibration_probe.txt`, 400 unplanted draws):
   size-blocked permutation FPR 0.018–0.053 at 0.05 and ≤ 0.005 at α in all 10 cells; studentized contrast did not
   help. **Final design run 3** (`tools/c017_power_design.py` → `analysis/C017_power_design.json`, 148 s):

| Set | Feature | Δ = 0.1 | 0.2 | 0.3 | 0.4 | 0.5 | **Δ\*** | FPR 0.05 / α (200) |
|---|---|---|---|---|---|---|---|---|
| ZL | o_init | 0.03/0.03 | 0.30/0.25 | 0.70/0.66 | 0.97/0.96 | 0.99/1.00 | **0.4** | 0.055 / 0 |
| ZL | y_fin | 0.01/0.04 | 0.32/0.26 | 0.71/0.75 | 0.94/0.91 | 0.98/1.00 | **0.4** | 0.035 / 0 |
| ZL | q_init | 0.05/0.07 | 0.32/0.36 | 0.78/0.80 | 0.99/0.97 | 1.00/1.00 | **0.4** | 0.03 / 0.005 |
| ZL | gallows | 0.02/0.02 | 0.30/0.27 | 0.67/0.77 | 0.94/0.93 | 1.00/0.98 | **0.4** | 0.03 / 0 |
| IT | o_init | 0.07/0.06 | 0.35/0.33 | 0.74/0.75 | 0.95/0.96 | 0.99/0.99 | **0.4** | 0.075 / 0 |
| IT | y_fin | 0.06/0.05 | 0.16/0.30 | 0.71/0.66 | 0.93/0.93 | 0.99/1.00 | **0.4** | 0.035 / 0 |
| IT | q_init | 0.02/0.06 | 0.25/0.32 | 0.81/0.76 | 0.95/0.98 | 0.99/1.00 | **0.4** | 0.045 / 0.005 |
| IT | gallows | 0.04/0.06 | 0.26/0.22 | 0.60/0.70 | 0.89/0.95 | 0.98/1.00 | **0.5** | 0.045 / 0.005 |

| Set | len, Δ (units) = 0.4 | 0.8 | 1.2 | 1.6 | 2.0 | **Δ\*** |
|---|---|---|---|---|---|---|
| ZL | 0.00/0.02 | 0.22/0.16 | 0.57/0.50 | 0.74/0.60 | 0.65/0.70 | **none** |
| IT | 0.04/0.04 | 0.22/0.23 | 0.52/0.56 | 0.79/0.71 | 0.74/0.72 | **none** |

Power is A>B / A<B. **The page is a costly unit**: C016's word-level design reached 0.9 at Δ 0.05–0.20; here the
smallest detectable contrast is 0.4 (0.5 for IT gallows), because B is in effect a handful of pages. The expected
`o_init` contrast (~0.24) has only about 0.3–0.7 power. **`len` is declared not testable up front** (no Δ\* in the grid).

## Decision rule (counted run: `tools/c017_label_genre.py`)
- **8 counted looks** (o_init, y_fin, q_init, gallows × ZL, IT); `len` × 2 reported but not testable. **α = 0.0035**
  (0.05/14, fixed before design run 1; kept, which is conservative for 8 looks).
- **Gate per look** (fresh seeds 17600+): planted contrast Δ\* at τ_design detected (p ≤ α, right direction) in
  **≥ 90 of 100** replicates in both directions. Failed → **not testable**.
- **False-positive check per look** (seeds 17800+): 1,000 unplanted pseudo-label draws at τ_design; limit **≤ 0.08 at
  0.05 and ≤ 0.012 at α**, otherwise the look's verdict is **withdrawn**.
- **Heterogeneity check:** the token-weighted SD of real unit excesses around their group means must not exceed the
  95th percentile of the same quantity in the design's unplanted draws (`resid_sd_tau_p95`, 0.135–0.178 for rates).
  If it does, a non-detection becomes **not testable (heterogeneity above design)**; a detection stands, because the
  permutation does not assume τ.
- Gated, calibrated, p ≤ α → "**drawing-element labels differ from free-standing labels in this feature, beyond
  their pages' text**" (direction, size). p > α → "**no contrast of Δ\* or more detected**". Never "excluded": with
  Δ\* = 0.4, contrasts the size C016 suggests (~0.24) can be missed.
- **Genre claim** ("drawing-element labels are a genre distinct from free-standing labels"): supported only if `o_init`
  shows A>B at p ≤ α in **both** ZL and IT. One of two → "partly supported". Neither → "not established at page level".
- **Breakthrough:** not possible (no meaning is tested).

## Not counted (descriptive, reported)
Per-class excesses (BIO, ROS, AZ, PP, FREE); per-B-unit excesses; leave-one-B-page-out (drop f67r2, drop f69r) with
the same blocked null; heterogeneity among A classes (unblocked permutation, known from design run 1 to be
anti-conservative, so its p is shown only as a pointer).

## Compute and code
sha256: `tools/c017_common.py` bd8ed71e…fa2991fc, `tools/c017_power_design.py` a7c2038c…0a93e669, `tools/c017_label_genre.py` decd668f…e9d730bb, `tools/c017_calibration_probe.py` add4c30f…64a0c3e3, `tools/c017_power_design_run1.py` a311e1a8…aa0f0849;
all committed with this pre-registration. Permutation seeds 17050+ (counted). Checkpoint: `analysis/C017_results.json`
rewritten after each look. Budget ≤ 8 min, `timeout 600`.

## Disclosed before the run
- Design runs 1 and 2 superseded; calibration probes 1 and 2 published. None computes a feature of a real label word;
  the real labels enter only through their count per unit (inventory above).
- Two smoke runs of the counted tool (R = 99, 3 gate replicates, 5 FPR draws): the first crashed on a JSON type
  error (only the last 3 traceback lines, with no data, were read); the second exited 0. Output went to `/dev/null`
  and `/tmp` and was deleted unread.
- The expected sizes from C016 (above) were known when Δ grid and τ were chosen; the grid and τ were fixed in design run 1.

## Limits stated in advance
B is effectively two cosmological pages (f67r2, f69r) plus seven small units; any B result is about those pages.
Labels are typed by Zandbergen's IVTFF conversion in both files, so "what is a label" is shared. τ is an assumption;
the heterogeneity check guards non-detections only partly. Five features only.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
