# C016 — Expedição 16: The Name Tags, Second Visit. Power first: do label words differ from their own pages' running text in single glyph features?

**Status:** design step published in commit b69a8c5a (04:37:11 PT); pre-registered in commit 897e2b89
(2026-11-05 04:37:19 PT), before the counted run (started 04:37:22 PT). Results appended below.
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

## Results (counted run 2026-11-05, 04:37:22–04:38:35 PT, after pre-registration commit 897e2b89; `tools/c016_label_features.py`, 73 s; `analysis/C016_results.json`)

One counted run, no reruns. Transcriptions: ZL 3b (`data/ZL3b-n.txt`, sha256 bf5b6d4a…beccafc) and Takahashi IT2a
(`data/IT2a-n.txt`, "Version 2a of 02/02/2023 modified 25/06/2025", sha256 7f27a8b0…3f536fb5).

### 1. The 10 counted looks
| Set | Feature | Labels | Same-page null (99.5 % range) | Diff | p | Gate up/down (of 100) | FPR 0.05 / α | **Verdict** |
|---|---|---|---|---|---|---|---|---|
| D1 | o_init | 0.279 | 0.263 (0.176–0.353) | +0.017 | 0.66 | 100/100 | 0.035 / 0.004 | **no difference of 0.20 or more** |
| D1 | len | 3.99 | 4.36 (4.01–4.71) | −0.38 | 0.0024 | 99/98 | 0.056 / 0.006 | **labels shorter** |
| D1 | y_fin | 0.279 | 0.376 (0.287–0.471) | −0.096 | 0.0042 | 98/100 | 0.044 / 0.005 | **labels end in `y` less often** |
| D1 | q_init | 0.007 | 0.070 (0.022–0.125) | −0.062 | 0.0002 | **88**/100 | 0.024 / 0.002 | **not testable** (gate failed) |
| D1 | gallows | 0.471 | 0.424 (0.324–0.522) | +0.047 | 0.21 | 100/100 | 0.040 / 0.007 | **no difference of 0.20 or more** |
| D2 | o_init | 0.594 | 0.303 (0.266–0.340) | +0.291 | 0.0002 | 100/100 | 0.047 / 0.002 | **labels start with `o` more often** |
| D2 | len | 5.26 | 4.73 (4.59–4.88) | +0.53 | 0.0002 | 100/100 | 0.051 / 0.007 | **labels longer** |
| D2 | y_fin | 0.423 | 0.386 (0.345–0.427) | +0.037 | 0.015 | 100/100 | 0.034 / 0.002 | **no difference of 0.10 or more** |
| D2 | q_init | 0.007 | 0.104 (0.078–0.131) | −0.097 | 0.0002 | 100/100 | 0.034 / 0.003 | **labels almost never start with `q`** |
| D2 | gallows | 0.632 | 0.521 (0.479–0.561) | +0.111 | 0.0002 | 100/100 | 0.060 / 0.009 | **labels contain gallows more often** |

p = 0.0002 is the floor for R = 9,999. Every FPR is inside the limits (≤ 0.08 / ≤ 0.015), so no verdict is withdrawn.
**Count: 6 looks show a difference, 3 show no difference of Δ\* or more, 1 is not testable, 0 withdrawn, 0 excluded.**
(D1 q_init: the pre-registered gate failed by 2 hits, 88/100 against 90, although the design step had 0.925. Its
p = 0.0002 is therefore **not** a verdict. It is reported only because it was computed.)

### 2. The C015 lead (label-initial `o`)
- **Not confirmed on the independent sample.** On the 136 held-out ZL labels (D1), 27.9 % start with `o` against
  26.3 % for their pages' running text (p 0.66). The planted control shows this test would catch a shift of 0.20 in
  100/100 replicates; the C015-size excess (about +0.26 to +0.29) is absent here. The first-word-only sensitivity agrees
  (30.6 % vs 26.0 %, p 0.35).
- **Not a ZL typing artefact.** Takahashi's independent reading of the C015 loci (D2) gives 59.4 % against 30.3 %
  (p 0.0002, gate 100/100). Per locus, ZL and IT agree on whether the first word starts with `o` in 690 of 705 shared
  loci (457 both `o`, 233 neither; 8 ZL-only, 7 IT-only, so the disagreements are balanced, e.g. f70v2.22 `otar`/`sar`,
  f73v.10 `okeor`/`ykeor`). Both readers see the same `o`.
- **But D2 is a re-reading of the labels where the lead was seen**, so it is a transcriber replication of a
  re-analysis, not new evidence that labels in general start with `o`.
- So the `o`-initial habit belongs to the **drawing-element label types** of C015 (`Ln Lt Lz Ls La Lc Lf Lp`, Rosettes),
  not to labels as such: the free-standing `L0` labels of f67r2, f69r, f67v1, f57v and others do not show it.
- It is **not** just a line-start habit either: in D2 the labels' 59 % also exceeds the line-initial words of the
  same pages (41 %, p 0.001, descriptive).

### 3. Why D1's two "differences" look weak (post-hoc, not counted; `tools/c016_posthoc_d1.py`, `analysis/C016_posthoc_D1_sensitivity.json`)
D1's shorter length and lower `y`-final rate are pre-registered verdicts and stand as such, but they rest on
one-glyph label words. D1 contains `s` ×9, `l` ×4, `o` ×3, and a run of six single glyphs on f69r (loci 44–49:
`y d o l s ed`, a sequence like the excluded f49v/f66r columns, which I had not known about). Dropping f69r.44–49:
len p 0.057, y_fin p 0.02. Dropping all one-glyph words from labels and null: len 4.59 vs 4.51 (p 0.57), y_fin
0.33 vs 0.36 (p 0.37). Both effects disappear. Read them as "D1 contains single-glyph labels", not as a label style.

### 4. Descriptive (not counted)
- **D0** (ZL reading of the C015 loci; the re-analysis): o_init 0.608 vs 0.349, len 5.37 vs 4.64, y_fin 0.442 vs 0.366,
  q_init 0.007 vs 0.092, gallows 0.652 vs 0.518, all p 0.0002. Same picture as D2.
- **Line-initial / line-final baselines** (same pages): D2 and D0 labels still differ from both on o_init and q_init
  (p ≤ 0.001). In D2, label length (5.26) is close to line-initial words (5.31, p 0.23).
- Most frequent D2 labels: `otal` 10, `am` 7, `daiin` 6, `otol` 6, `oky` 6, `otaly` 6, `dy` 6, `okaly` 5.

### 5. Image spot-check (Beinecke MS 408, IIIF manifest 2002046; cannot change any verdict)
- **f67r2** (image 1006194, region 4350,550,600,900): the red sector label f67r2.5 reads as ZL's `ykeody okchy`: the
  first word opens with the tailed `y` glyph, the second with a round `o`. The two are clearly distinct here, so the
  low `o` rate of these labels is not an `o`/`y` misreading. The top red labels (region 3350,330,1150,330) are faded
  and I did not confirm them.
- **f69r** (image 1006198, region 1450,1330,700,750): the ray labels are small and cramped. One (f69r.9, ZL
  `dcho,char,ar`) is consistent with ZL, including the final `ar` and a non-`o` first glyph. The others are not confirmed.

### 6. Disclosed
- Design run 1 included Lx and was superseded (above). One smoke run was discarded unread (above). There were no
  failed or repeated counted runs.
- The post-hoc sensitivity (section 3) was run after seeing the counted D1 results. It is labelled as exploration.

### Verdict
Under a design with planted power ≥ 0.9 (checked first, then confirmed in the run), **the C015 lead does not carry
over to labels that played no part in forming it**: free-standing `L0` labels start with `o` no more often than their
pages' text. On the C015 loci the `o`-initial excess, the near-absence of `q`, greater length and more gallows are
real in a second, independent transcription and are not a ZL typing choice. That is consistent with what Grove,
Stolfi and Zandbergen described long ago, now with calibrated same-page nulls and planted controls. **No breakthrough**
(no meaning was tested).

### Next
A pre-registered contrast of label *types* (drawing-element labels vs free-standing `L0`) with a page-level permutation
and a power-first design, so that "the drawing-element labels are a genre" becomes a tested claim rather than a reading
of two separate tests. Then go back to comparing sections with pooled power.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
