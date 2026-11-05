# C016 — Expedição 16: The Name Tags, Second Visit. Power first: do label words differ from their own pages' running text in single glyph features?

**Status:** design step run and published with this pre-registration (before any counted run); results appended
below after the counted run. Pre-registration commit: see the git history of this file (first commit).
**Approach family:** label vocabulary (second cycle; C015 was the first). Changed design: **power analysis before
the verdict test**, pooled label groups, one feature at a time, planted controls in both directions.

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Why this cycle looks like this
C013–C015 ended partly or fully *not testable*: the planted controls were only checked inside the counted run, and
they failed. Here the planted power is measured **first**, openly, as a design step that never looks at any real
label word, and only (dataset, feature, effect size) combinations with planted power ≥ 0.9 are pre-registered.

C015 left a lead: labels start with `o` far more often than the running text on their pages (51–66 % against
17–39 %). That lead was **seen in C015's data**, so testing it again on the same ZL label words would be
double-dipping. It is also not new: John Grove (cited by Stolfi, *Statistical properties of the VMS*), René Zandbergen
(voynich.nu, *Some special properties of labels*: "ok"/"ot" start 52 % of zodiac labels; labels almost never start
with `qo`) and a 2025 voynich.ninja thread (no. 4929: about 50 % of labels start with `o`, "against their own local
word mix it's only mildly unusual") all describe it. What this cycle can add is a **calibrated, power-checked
same-page test on data that played no part in forming the lead**.

## Data
| Set | Role | File (version, sha256) | Label loci | Tokens | Pages |
|---|---|---|---|---|---|
| **D1 — ZL held-out labels** | counted (independent sample) | `data/ZL3b-n.txt`, ZL "Version 3b of 13/05/2025", bf5b6d4a…beccafc | `L0` loci **not** on fRos, f49v or f66r: never analysed in C001–C015 | 136 (85 loci) | f2r 3, f11v 1, f57v 5, f67r2 47, f67v1 16, f68v3 2, f69r 47, f75v 6, f76r 9 |
| **D2 — Takahashi reading of the C015 loci** | counted (independent *transcriber*, same physical labels) | `data/IT2a-n.txt`, Takahashi transcription in IVTFF, "Version 2a of 02/02/2023 modified 25/06/2025" (voynich.nu/data, retrieved 2026-11-05), 7f27a8b0…3f536fb5 | C015 types `Ln Lt Lz Ls La Lc Lf Lp` (+ `L0` on fRos, absent in this file) | 820 (713 loci) | 45 |
| D0 — ZL reading of the C015 loci | **re-analysis, not counted** | ZL 3b | as C015 | — | — |

- f49v and f66r `L0` loci are excluded *a priori*: they are marginal columns of isolated glyphs, a different genre.
- **Lx** (3 marginal-writing loci) was in D1 in the first design run and was then **dropped**: while locating its
  pages, the grep printed the 7 words of those 3 loci. The first design run is kept as
  `analysis/C016_power_design_run1_with_Lx_superseded.json` (D1 had 145 tokens; Δ* for o_init was 0.15 then, 0.20 now).
- **What D2 does and does not show.** IT2a is an independent *reading* of the glyphs, so it checks that the
  pattern is not a ZL typing choice. It is the same physical ink as C015's labels, so it is **not** an independent
  sample: a D2 result on o_init is a transcriber replication of a re-analysis. D1 is the independent sample.
- Locus types in both files come from Zandbergen's IVTFF conversion, so "what counts as a label" is shared.
- Cleaning as C003/C015 (first alternative reading; uncertain spaces split; `?` words dropped; C003 glyph units,
  `ch sh cth ckh cph cfh` one unit). Running text of a page = its non-label loci (`P`, `C`, `R`).

## Features (one at a time; per word, averaged over label tokens)
`o_init` (first unit is `o`), `len` (glyph units), `y_fin` (last unit `y`), `q_init` (first unit `q`), `gallows`
(contains any of `k t p f cth ckh cph cfh`).

## Test
Statistic: mean feature over a set's label tokens. Null: R = 9,999 draws in which each label token is replaced by a
running-text token of the **same page**, drawn without replacement (page with fewer than 2k running tokens → pooled
running text of the set's label pages; D2: f65r, f68r1). Two-sided p = min(1, 2·min(p_lo, p_hi)), direction recorded.

## Design step (already run; `tools/c016_power_design.py`, 56 s; `analysis/C016_power_design.json`)
Planted shifts on fresh pseudo-labels drawn from running text (seeds 16000+, 16100+): rates moved by ±Δ (absolute)
by rewriting the first glyph to `o` / away from `o` (to a non-`o` initial with running-text frequencies), the last
glyph to `y` / away, prefixing / removing `q`, putting in / taking out one gallows; length moved by ±Δ units by
inserting / deleting one unit. 200 replicates per cell, α = 0.005. Power up/down:

| Set | Feature | Δ = 0.05 | 0.10 | 0.15 | 0.20 | 0.30 | **Δ\*** |
|---|---|---|---|---|---|---|---|
| D1 | o_init | 0.14/0.12 | 0.56/0.65 | 0.85/0.95 | 0.99/1.00 | 1.00/1.00 | **0.20** |
| D1 | y_fin | 0.10/0.09 | 0.50/0.47 | 0.90/0.92 | 0.98/0.98 | 1.00/1.00 | **0.20** |
| D1 | q_init | 0.38/0.53 | 0.93/0.98 | 1.00/1.00 | 1.00/1.00 | 1.00/1.00 | **0.10** |
| D1 | gallows | 0.09/0.04 | 0.47/0.59 | 0.86/0.86 | 0.98/0.99 | 1.00/1.00 | **0.20** |
| D2 | o_init | 0.77/0.83 | 1.00/1.00 | 1.00/1.00 | 1.00/1.00 | 1.00/1.00 | **0.10** |
| D2 | y_fin | 0.70/0.71 | 1.00/0.99 | 1.00/1.00 | 1.00/1.00 | 1.00/1.00 | **0.10** |
| D2 | q_init | 0.98/0.99 | 1.00/1.00 | — | — | — | **0.05** |
| D2 | gallows | 0.69/0.72 | 1.00/1.00 | 1.00/1.00 | 1.00/1.00 | 1.00/1.00 | **0.10** |

| Set | len, Δ (units) = 0.2 | 0.4 | 0.6 | 0.8 | 1.0 | **Δ\*** |
|---|---|---|---|---|---|---|
| D1 | 0.12/0.14 | 0.67/0.69 | 0.97/0.97 | 1.00/1.00 | 1.00/1.00 | **0.6** |
| D2 | 0.83/0.87 | 1.00/1.00 | 1.00/1.00 | 1.00/1.00 | 1.00/1.00 | **0.4** |

Δ\* = smallest grid Δ with power ≥ 0.9 in **both** directions. Every one of the 10 (set, feature) cells reached it,
so all 10 are pre-registered; none is declared untestable up front. Null means (D1 / D2): o_init 0.263 / 0.303,
len 4.36 / 4.73, y_fin 0.375 / 0.386, q_init 0.070 / 0.104, gallows 0.424 / 0.520. Design-step false-positive rate
(200 unplanted draws): 0.025–0.07 at 0.05 and 0–0.02 at α (too few draws to judge; rechecked below with 1,000).

## Decision rule (counted run: `tools/c016_label_features.py`)
- **10 counted looks** (5 features × D1, D2), two-sided, **Bonferroni α = 0.005** (fixed before the design step).
- **Gate per look:** with fresh seeds (16500+), the planted shift of size Δ\* must be detected (p ≤ α, right direction)
  in **≥ 90 of 100** replicates, **up and down**. Failed → **not testable**.
- **False-positive check per look:** 1,000 unplanted pseudo-label draws (seeds 16700+) against the same null;
  limit ≤ 0.08 at 0.05 and ≤ 0.015 at α, otherwise that look's verdict is **withdrawn**.
- Gated and calibrated, p ≤ α → "**labels differ from their own pages' running text in this feature**" (direction,
  size). p > α → "**no difference of Δ\* or more detected**" (not "excluded": smaller effects remain possible).
- **The C015 lead (o_init, labels > running text) counts as confirmed only if D1 shows it** ("more", p ≤ α). D2 alone
  would show only that it is not a ZL typing artefact.
- **Breakthrough:** not possible in this cycle. A feature difference says nothing about meaning, and the o_init
  pattern is already known in the literature.

## Not counted (descriptive, reported)
D0 (same test on ZL's C015 loci, i.e. the re-analysis); first word of each label locus only; an alternative baseline
of **line-initial** and **line-final** running-text words of the same pages (are labels like words that begin
lines?); ZL vs IT per-locus agreement on whether the first word begins with `o` (typing-convention check); optional
Beinecke image spot-check of a few D1 labels after the run (cannot change any verdict).

## Compute and code
`tools/c016_common.py` (sha256 09cb0a87…bf39fc4dcc), `tools/c016_power_design.py` (04e08bc5…74b140a688),
`tools/c016_label_features.py` (3f4ed7a1…293499b), committed with this pre-registration. Seeds fixed in code
(null 1601+). Checkpoint: `analysis/C016_results.json` rewritten after each dataset. Budget ≤ 8 min.

## Disclosed before the run
- Design step, run 1 (with Lx, superseded) and run 2 (final); both published. Neither computes any feature of a real label word.
- 7 words of the 3 Lx loci were seen (see above); Lx dropped.
- A 2-second smoke run of the counted tool (R = 99, 3 plants, 5 FPR draws) checked the code paths; its output went to
  `/dev/null` and `/tmp` and was deleted unread. Exit code 0.
- The literature on label-initial `o` was searched before writing this file (cited above).

## Limits stated in advance
D1 is small (136 tokens) and dominated by two astronomical/cosmological pages (f67r2, f69r: 94 tokens). Labels are
isolated words; running text is in lines, so a positional habit (e.g. words that start lines) could produce a
difference without anything label-specific; the line-initial baseline is there to show how much. Multi-word labels
make tokens within a locus non-independent (first-word-only sensitivity). Only five features; a label "style" could
differ in ways not measured here.
