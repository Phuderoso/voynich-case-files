# C015 — Expedição 15: The Name Tags. Do bath, rosette and zodiac labels use different words or glyphs from plant and pharma labels, beyond what their own pages' running text predicts?

**Status:** pre-registered 2026-11-05 04:07 PT, before any counted run. Results appended below.
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
