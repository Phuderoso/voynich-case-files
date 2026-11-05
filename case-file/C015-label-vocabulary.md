# C015 — Expedição 15: The Name Tags. Do bath, rosette and zodiac labels use different words or glyphs from plant and pharma labels, beyond what their own pages' running text predicts?

**Status:** pre-registered 2026-11-05 04:06:01 PT (commit a776a40b), before any counted run (the run started 04:06:05 PT). Results appended below. The pre-registration text originally gave 04:07 PT, an estimate written before the commit; corrected here to the commit time.
**Approach family:** **New family: label vocabulary.** C001 used page sections as tags on running text; this is the
first cycle that measures the label words themselves.

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Question
Labels are the short words written next to drawing elements. If they name things (plants, containers, nymphs, tubs,
stars), labels from different kinds of drawings might differ in vocabulary or glyph make-up. But C001/C002 showed that
running text already differs by section and scribe, and the label groups here are almost perfectly confounded with
scribe (inventory below). So the question is relative: **do the labels of group X and the plant/pharma labels differ
in glyph profile or word types more (or less) than random running-text words from the very same pages do?**

## Data and label loci (ZL 3b)
Transcription `data/ZL3b-n.txt`, ZL "Version 3b of 13/05/2025", IVTFF 2.0, sha256 bf5b6d4a…beccafc. Locus types follow
the IVTFF 2.0.1 definition (Table 9). Words are cleaned as in C003 (uncertain spaces `,` split; first alternative
reading; tokens with unreadable `?` dropped; glyph units = C003 units, `ch sh cth ckh cph cfh` as one unit).

| Group | Locus types counted as labels | Loci | Word tokens | Types | Pages | LFD hand / Currier |
|---|---|---|---|---|---|---|
| **BIO** (bath) | `Ln` nymph, `Lt` tub/tube | 110 | 119 | 109 | 11 (f75v–f84r) | hand 2 / B |
| **ROS** (rosettes) | `L0` on the Rosettes foldout `fRos` | 137 | 152 | 138 | 1 | hand 4 / B |
| **AZ** (astro/zodiac) | `Lz` zodiac, `Ls` star, `La` other astronomical | 382 | 440 | 365 | 17 | hand 4 / none |
| **PP** (plant/pharma, reference) | `Lc` container, `Lf` plant fragment, `Lp` herbal plant | 237 | 243 | 229 | 18 | mostly hand 1 / A |

Not counted: other `L0` (not near any drawing element; 160 loci on f2r, f11v, f49v, f57v, f66r, f67r2, f67v1, f68v3,
f69r, f75v, f76r) and `Lx` (marginal). Running text of a page = all its non-label loci (`P`, `C`, `R`), so on zodiac and
rosette pages it is the ring and radial text.

**Where transcription choices matter:** (1) uncertain spaces: 39 of the 866 counted label loci contain `,`; split is
primary, joined is a sensitivity run; (2) alternative readings `[a:b]`: first is primary, second is a sensitivity run;
(3) labels with `?` lose that word (30 counted loci contain `?`); (4) the ZL locus typing itself decides what is a
"label" and which drawing it belongs to; (5) C003 parsing removes `<->` drawing intrusions without a space, which can
join two running-text words around a drawing (kept for consistency with C001–C014).

## Statistics (higher = more separated)
- **S_g (glyph profile):** Jensen–Shannon divergence (bits) between the two groups' distributions of glyph bigrams,
  with word-start `^` and word-end `$` markers (so first and last glyphs are included). Tokens counted with repeats.
- **S_w (words):** 1 − |T_X ∩ T_Y| / min(|T_X|, |T_Y|), where T is the set of distinct word types of a group.

## Tests
- **T2 (decisive, "beyond running text"):** null draw = every label token is replaced by a token drawn without
  replacement from the running text of the same page (for S_w: from the page's distinct types). If a page has fewer
  than 2k running tokens/types (k = its label tokens), it draws from the pooled running text of its group's pages
  (known in advance: f68r1 for tokens and types; f73r, f65r and fRos for types; for fRos the pool is the same page).
  R = 1,999 draws per pair. Two-sided p = min(1, 2·min(p_lo, p_hi)); direction recorded as "more" or "less"
  separated than running text.
- **T1 ("any separation", the shuffled-group-label null):** page-block permutation of group membership among the
  pair's pages, page counts kept, R = 1,999. Pages, not single labels, are shuffled because labels on one page share a
  scribe and a drawing. Only for pairs where both groups have ≥ 5 label pages (BIO–PP, AZ–PP); ROS is one page, so T1
  is **not testable** for ROS by design. T1 is confounded by scribe and dialect and cannot by itself say anything about
  labels as such.
- **Pairs:** BIO–PP (primary, the question the C014 journal set), ROS–PP, AZ–PP.

## Controls and gates
- **Planted separation of known size:** in a fraction f of group-X tokens, glyph units are swapped `k↔t` and
  `ch↔sh` (a "dialect" shift in two common glyph pairs; also creates new word types). For T2, the plant is applied to
  a fresh pseudo-label draw (seeds 15100+, 15200+) and tested against the unplanted null. For T1, pages are randomly
  reassigned to groups (no true difference), the plant is applied, and the permutation test is rerun (seeds 15300+,
  15400+). **Gate:** a (pair, statistic, test) is testable only if the f = 0.5 plant is detected (p ≤ 0.005, "more"
  direction) in **≥ 9 of 10** replicates. f = 0.25 is reported as a power point. Failed gate → **not testable**.
- **False-positive rate:** T2: leave-one-out over the 1,999 null draws (each draw tested against the rest) at 0.05
  and at α. T1: 200 random page reassignments, each tested with its own 1,999 permutations. Acceptable: ≤ 0.08 at
  0.05 and ≤ 0.015 at α; otherwise that test's verdicts are withdrawn.

## Decision rule and comparisons
- Counted looks: T2 × 2 statistics × 3 pairs = 6, plus T1 × 2 statistics × 2 pairs = 4. **10 looks, Bonferroni
  α = 0.005** per look.
- For a gated (pair, statistic): T2 p ≤ 0.005, direction "more" → "**group X labels differ from PP labels more than
  their pages' running text does**" (a label-specific separation). Direction "less" → "**labels are more alike across
  groups than their running text**" (a shared label style). p > 0.005 → "**no label-specific difference detected**"
  at the planted-control power. Not "excluded": the plant sets the smallest effect this test can see.
- T1 p ≤ 0.005 → labels differ between groups (any cause, including scribe). Reported, never called label-specific.
- **Breakthrough:** not possible in this cycle (no meaning is tested).

## Descriptive (not counted)
Most common initial and final glyph units and words, mean word length, for each group's labels and for its pages'
running text. Sensitivity for BIO–PP: commas joined, and second alternative reading (T2 only, 999 draws).

## Compute and code
`tools/c015_label_vocabulary.py` (sha256 72a99fe3…f47e2021), committed with this pre-registration. Seeds fixed in code
(null 1501, T1 1520). Checkpoint: `analysis/C015_results.json` is rewritten after every stage. Budget ≤ 8 min on 8 cores.

## Disclosed before the run
- An inventory pass (locus counts by type, page, hand and Currier language; how many label words fall per group)
  was run to design the groups. It computes no separation statistic.
- A 4-second smoke run (`--smoke`: R = 199, 3 plants, 10 FPR replicates) checked the code paths; it wrote to `/tmp`,
  its separation numbers were not printed or read, and it is discarded. Only its inventory stage was read (same as the
  inventory pass). One crash before it (a JSON type error) was fixed.
- Optional image spot-check of a few labels against the Beinecke MS 408 scans, after the run, if time allows; it
  cannot change any verdict.

## Limits stated in advance
Groups are confounded with scribe, Currier language and page layout, so T1 cannot separate "label" from "scribe"; T2
is the only label-specific test and it assumes that running text of the same page is the right baseline. Labels are a
different genre (isolated words), so a common label style shifts both groups at once; T2's two-sided form reports
it as "less separated". Small groups: ROS is one page; PP has 243 tokens. A planted swap of two glyph pairs is one kind
of difference; a label vocabulary that differs in other ways may need a larger effect to be seen.

## Results (run 2026-11-05, 04:06:05–04:06:48 PT, after the pre-registration commit a776a40b; `tools/c015_label_vocabulary.py`, 44 s on 8 cores; `analysis/C015_results.json`)

One counted run, no reruns. Transcription: ZL 3b (`data/ZL3b-n.txt`, "Version 3b of 13/05/2025", sha256 bf5b6d4a…beccafc).

### 1. Gates (planted separation, f = 0.5, need ≥ 9/10)
| Pair | T2 S_g | T2 S_w | T1 S_g | T1 S_w |
|---|---|---|---|---|
| BIO–PP | 0/10 | 0/10 | 0/10 | 0/10 |
| ROS–PP | 0/10 | 0/10 | not testable (1 page) | not testable (1 page) |
| AZ–PP | 0/10 | 0/10 | 0/10 | 0/10 |

The f = 0.25 power point was also 0/10 everywhere. **Every gate failed, so all 10 counted looks are not testable.**
No verdict on label vocabulary in this cycle.

Why: the groups are small (119–440 label tokens) and a JSD between two samples this small is noisy. The T2 null for
BIO–PP spans S_g 0.150–0.232 (central 99.5 %), while the f = 0.5 swap moved the mean only from 0.188 to 0.198. The
`k↔t`, `ch↔sh` swap also turned out to be a weak plant: those glyph pairs sit in very similar positions and
neighbourhoods, so swapping them barely changes the bigram profile, and swapped words often land on other existing
types. The plant was chosen before the run and is reported as it fell.

### 2. False-positive checks
- T2, leave-one-out over 1,999 null draws: 0.037–0.049 at 0.05 and 0.0015–0.004 at α, for every pair and statistic.
  Calibrated (by construction, so this checks the code rather than the baseline).
- T1, 200 random page reassignments: BIO–PP S_g 0.085 at 0.05 (**above the 0.08 limit, so T1 S_g for BIO–PP would be
  withdrawn even if it had passed its gate**), 0.000 at α; BIO–PP S_w 0.030 / 0.005; AZ–PP S_g 0.060 / 0.010;
  AZ–PP S_w 0.040 / 0.005.

### 3. Descriptive only (not verdicts: gates failed)
| Pair | S_g labels | T2 null median [99.5 % range] | T2 p, direction | S_w labels | T2 null median [range] | T2 p, direction | T1 S_g p | T1 S_w p |
|---|---|---|---|---|---|---|---|---|
| BIO–PP | 0.164 | 0.188 [0.150, 0.232] | 0.107, less | 0.835 | 0.841 [0.752, 0.926] | 0.874, less | 0.001, more | 0.081, less |
| ROS–PP | 0.151 | 0.196 [0.164, 0.239] | 0.001, less | 0.928 | 0.882 [0.822, 0.934] | 0.049, more | — | — |
| AZ–PP | 0.098 | 0.121 [0.098, 0.149] | 0.007, less | 0.860 | 0.776 [0.708, 0.842] | 0.001, more | 0.002, more | 0.621, more |

Two patterns are worth logging as **leads only**:
- **Glyph profile, "less":** in all three pairs the labels of the two groups are *more alike* in glyph bigrams than
  random words from their own pages' running text (ROS p 0.001, AZ 0.007, BIO 0.107). The likely driver is visible in
  the profiles: labels start with `o` far more often than running text does (BIO 61 % vs 17 %, AZ 66 % vs 39 %,
  PP 51 % vs 21 %; ROS 63 % vs 60 %, since its ring text is already `o`-heavy), and they are longer (5.2–5.6 vs
  4.4–4.8 glyph units). Labels look like one shared genre across sections. The gate only tested the "more"
  direction, so this has no planted control yet.
- **Word types, "more" for AZ:** zodiac/star labels share fewer word types with plant/pharma labels than zodiac ring
  text shares with pharma page text (p 0.001; ROS p 0.049). S_w has no working gate, so this is not a result.
- T1 S_g p 0.001–0.002 ("labels differ between groups at all") is expected from scribe and dialect alone (BIO is
  hand 2 / B, PP hand 1 / A, AZ hand 4) and its gate failed too.
- Most common labels: BIO `otedy` (4), `darol`, `daldy`, `otoly`, `otol`; ROS `otedy` (4), `otchdy` (3);
  AZ `otaly` (6), `otar`, `oky`, `otal`, `ar` (5); PP `okol` (4), `otoldy` (3). `otedy` heads both BIO and ROS.

### 4. Transcription-choice sensitivity (BIO–PP, T2, 999 draws, descriptive)
Commas joined: S_g 0.167 (p 0.112, less), S_w 0.868 (p 0.996). Second alternative reading: S_g 0.161 (p 0.074, less),
S_w 0.844 (p 0.886). Same picture as the primary parse.

### 5. Post-hoc power exploration (disclosed, exploratory, not counted)
After all gates failed I ran `tools/c015_power_explore.py` (17 s; `analysis/C015_power_explore.json`) with the same
T2 nulls and seeds to see what size of separation T2 can see at α = 0.005 (hits out of 10, S_g / S_w):

| Plant | BIO–PP | ROS–PP | AZ–PP |
|---|---|---|---|
| swap, f = 0.5 | 0 / 0 | 0 / 0 | 0 / 0 |
| swap, f = 1.0 (every label) | 1 / 0 | 2 / 0 | 0 / 0 |
| `q` prefixed to 10 % of labels | 0 / 0 | 0 / 0 | 0 / 0 |
| `q` prefixed to 25 % | 0 / 0 | 0 / 0 | 0 / 0 |
| `q` prefixed to 50 % | 8 / 3 | 1 / 0 | 4 / 1 |

Even putting `q` (a glyph labels almost never start with) in front of half of a group's labels is caught at most
8 times in 10. **With label groups this small, a two-group JSD against same-page running text cannot see any
separation of a plausible size.** Its first attempt crashed on a JSON type error before printing anything; fixed and
rerun once.

### 6. Image spot-check (does not change any verdict)
Beinecke MS 408, IIIF manifest https://collections.library.yale.edu/manifests/2002046:
- **f77r** (image 1006212, top strip `pct:5,3,85,12`): the labels sit along the pipe and beside the two nymphs, as ZL
  types them (`Ln` by the nymphs, `Lt` under the pipe outlets). `darchdar`, `otedy`, `dchdy`, `dotedy` read as
  transcribed at this resolution; `olkchs`, `otork` and `soral` I could not confirm or refute (cramped strokes).
- **f99r** (image 1006246, full page at 1400 px): one label on the top jar (`Lc`, `okaradag`) and short labels above
  the individual root and leaf fragments (`Lf`), as typed.

### What this does and does not show
- It does **not** show that label vocabulary differs, or does not differ, between bath, rosette, zodiac and
  plant/pharma drawings: every planted gate failed, so all 10 looks are **not testable**.
- It shows that this design (two-group JSD on 119–440 label tokens against same-page running text) is underpowered,
  and by how much (section 5).
- It leaves a lead with a number on it: labels across sections look more like each other than like their own pages'
  text, mostly through `o`-initial words. A power-first test of "labels vs running text" (pooled over all label
  groups, one feature at a time, with a planted control in both directions) is the next step.
- Comparisons: 10 looks registered, 0 judged. 30 exploratory plant settings, not counted.
- Not tested: label-to-drawing links, positional patterns within a label set, Currier-matched subsets, other
  transcriptions (IT, GC, RF).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
