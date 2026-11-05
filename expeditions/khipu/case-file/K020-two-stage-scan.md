# K020 · Two-stage scan for further correspondences (groups of ≥ 3 cords)

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration**, committed before any K020 statistic was computed.

## Why
K018 only used groups of at least 5 cords, so khipus built from smaller groups had few or no leaders and couldn't be
tested. K020 lowers the bar to **groups of at least 3 cords** and runs the full K018 → K019 chain as one
pre-registered pipeline over the whole corpus.

## Pipeline
1. **Stage 1 (K018 method).** Leaders are the first value of each group with ≥ 3 cords, zeros dropped. W is the
   information-weighted LCS of the leader sequences. The null shuffles each khipu's leaders (100 corpora) and the
   threshold is the 95th percentile of the null maximum. Calibration needs ≤ 3 of 20 held-out corpora with any pair
   above it. Power is measured with 50 planted ordered copies of 10 leaders.
2. **Stage 2 (K019 method), for every stage-1 discovery.** Using the leader-aligned groups, take the LCS of the
   non-leader cords and compare against a null that gives each group a random partner group (10 000 replicates).
   Bonferroni over the number of stage-1 discoveries, at α = 0.01.
3. **A pair is a confirmed correspondence** if it passes both stages and stage 1 is calibrated.

## Positive controls
The three K018/K019 pairs (KH0097·KH0586, KH0192·KH0470, KH0192·KH0469) must be found again. If any of them is
missed, the K020 pipeline counts as **failed**: its new discoveries are only reported, and I'll investigate why.

## Reporting
New confirmed pairs are listed with museum, number, provenance and investigator, and checked against the Khipu Field
Guide afterwards. The K013 known exact pairs are flagged as known.

Compute: a few seconds for stage 1, under a minute for stage 2.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (computed after the pre-registration commit `aedfa3e4`)

Tool: `tools/k020_two_stage.py`. Output: `analysis/k020_results.json`. Run time: 6.9 s.

Lowering the group size to 3 cords gives 2,763 leaders (606 distinct values), up from K018's 1,914.

**Stage 1 is calibrated.** The threshold is T_W = 74.8. Two of the 20 held-out null corpora had a pair above it, and
the rule allows three. Planted copies were found 23 times out of 50.

**The pipeline passes.** All three positive controls were found again in both stages.

Stage 1 found five pairs. Stage 2 used a Bonferroni level of 0.01/5, and each p-value comes from 10,000 replicates:

| Pair | Records | W | Matched groups | V | p₂ | Verdict |
|---|---|---|---|---|---|---|
| KH0491 · KH0503 | UR255 / UR267A, Inkawasi | 138.5 | 15 | 15 | 0.36 | stage 1 only |
| KH0097 · KH0586 | Paris / Lima (control) | 131.9 | 13 | 89 | < 1e-4 | confirmed |
| **KH0502 · KH0514** | **UR266 (Inkawasi 13829) / UR275 (Inkawasi 13836-2014)** | **123.4** | **12** | **13** | **< 1e-4** | **new, confirmed** |
| KH0192 · KH0470 | Berlin (control) | 94.7 | 14 | 37 | < 1e-4 | confirmed |
| KH0192 · KH0469 | Berlin (control) | 80.8 | 15 | 36 | < 1e-4 | confirmed |

### Reading the results
- **KH0491 · KH0503 is the Urton & Chu Inkawasi control pair** that K012–K016 never detected. Stage 1 finds it now:
  this is the first time one of my tools has recovered a published Inkawasi match. It fails stage 2 because the
  leaders correspond but the cords inside each group do not, more than chance would allow. That fits the published
  description of these as *close matches*, not copies. This reading is a disclosed post-hoc interpretation.
- **KH0502 · KH0514 (UR266 · UR275) is new to this expedition.** Both are Inkawasi records. The run of leaders
  2089, 1842, 1876, 2229, 3320, 4273, 2633, 2950, 2275 appears in the same order in both, and the cords inside those
  groups also match beyond the null. I have only checked it against the K013 list of known pairs. **I have not checked
  whether Urton & Chu already published it.** Until someone checks the Inkawasi literature, read it as
  "rediscovered or new", not as "new to science".
- **Caveat.** The null maximum is concentrated at 74.5, which is the median and the minimum across the 100 null
  corpora. One pair seems to reach that value under any shuffle, probably because of a shared rare multiset of
  leaders. So the threshold is driven by that one pair. Calibration still holds on held-out corpora.

**Next:** check UR266/UR275 against Urton & Chu's Inkawasi publications, then run the cord-level comparison of the
KH0491/KH0503 close match with an order-free statistic.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Addendum · literature audit (07:31 PT, after the results were committed)

**UR266 · UR275 is already published.** Urton & Chu's *Appendix I: Inventory of Inkawasi Khipus* (supplement to
"Accounting in the King's Storehouse", *Latin American Antiquity*;
[PDF](https://static.cambridge.org/content/id/urn:cambridge.org:id:article:S1045663500008786/resource/name/S1045663500008786sup001.pdf))
describes UR266 as "Repetition of fixed value '47.' Matches UR 275". Both khipus come from the group of 14 khipus
covered with peanuts in kallanka U.A.4. Urton (2017, *Inka History in Knots*, pp. 164–170) and Urton & Chu (2019)
also discuss them.

**Revised verdict.** KH0502 · KH0514 is a **blind rediscovery of a published match**, not a new correspondence. That
is still a useful result. Without being told about it, the pipeline found a second published Inkawasi match and
placed it in the same class (confirmed at cord level) as the Paris/Lima and Berlin pairs. It also recovered the
UR255 · UR267A "close match" at the leader level only, and the inventory itself uses the word "close" for that pair.
The leader 47 that appears twice in KH0502 is the "fixed value 47" the inventory mentions.

**What the K020 pipeline reports that is new:** nothing beyond K018/K019. Every pair it found is now either a
published match or one of my earlier confirmations. This is a **negative for new discoveries** at groups of ≥ 3
cords, published as such.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
