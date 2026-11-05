# C004 — Expedição 4: The Copyist's Workshop. Can the real self-citation generator reach Voynich glyph-position rigidity?

**Status:** pre-registered 2026-11-04 22:35 PT, after one instrument smoke test (below) and before any measurement.
Results appended below.
**Approach family:** generator configuration sweep with held-out confirmation, plus verbose-cipher planted controls.
Continues C003 (same metric); the verbose-cipher family is new to the coverage table.

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Question
C003 found Voynich positional rigidity R = 0.485 [99 %: 0.470, 0.499] (ZL 3b, commas split), far above eight
natural-language controls, and above the one published sample of the Timm–Schinner self-citation generator (0.418).
(a) Does **any** configuration of the authors' own generator reach Voynich R, and does it do so while keeping other
basic Voynich statistics? (b) How much rigidity does a **verbose cipher** of Latin produce, with and without positional
code variants?

## Instrument
- Generator: the authors' own executable `text-generator.jar` from
  [TorstenTimm/SelfCitationTextgenerator](https://github.com/TorstenTimm/SelfCitationTextgenerator) (MIT), sha256
  `dc9b2f3c…ad18fef8`, run on Temurin JRE 17.0.21. Not re-implemented.
- Smoke test (done before this registration; no R measured): default `conf.properties`, seed 19, reproduces the
  published `generated_text.txt` **byte for byte** (sha256 `1e954a17…2888dc11`). The instrument is the authors' own.
- Metric: R = I(glyph; position)/H(position), position ∈ {initial, medial, final}, words of ≥ 2 glyph units, glyph units
  as in C003 (`cth ckh cph cfh ch sh` then single characters). Code reused from `tools/c003_position_rigidity.py`.
- Sweep screening uses the **point R on the first 6,000 words** of each generated text (no bootstrap). Bootstrap 99 %
  intervals (C003 method, 300 × 6,000 words in 20-word blocks) only for the confirmation step.

## Secondary "Voynich-likeness" statistics (screening, 6,000 words)
mean word length in glyph units; type/token ratio; within-word glyph conditional entropy h2 = H(g_i | g_{i-1}).
A configuration is "Voynich-like" if all three are within ±15 % of the Voynich V value.

## Sweep (all runs: 1,200 lines, other settings default unless varied)
- **S0:** default configuration, seeds 1–50.
- **S1 (one switch at a time, seeds 1–10 each):** `use_word_final_substitutions=false`; `canFollow` ∈ {statistic,
  voynich, none}; `sourceChooser` ∈ {position, random}; `suggestions` ∈ {none, daiin, random};
  `replace.probability` ∈ {20, 100}; `add_remove.probability` ∈ {0, 80}; `combine_split.probability` ∈ {0, 80};
  `same_position_probability` ∈ {0, 100}; `canFollow.error_rate` = 10. (19 settings, 190 runs.)
- **S2 (random search):** 120 configurations, every documented switch and probability drawn uniformly from its
  documented range (PROPERTIES.md), one seed each (seeds 1001–1120, Python RNG seed 404).

## Decision rules (looks counted: D1, D2, D3 → 3 primary looks)
- **Selection then held-out confirmation** (handles best-of-~360 selection bias): the screening config with the highest
  point R (for D1) and the highest point R among Voynich-like configs (for D2) are each re-run on **10 fresh seeds
  (5001–5010)** and bootstrapped.
- **D1 reach:** the generator "reaches Voynich rigidity" if the confirmed config's 10-seed mean R ≥ 0.470 (Voynich V
  lower 99 % bound). "Does not reach in the explored space" otherwise; this is *not* "excluded" for unexplored settings
  or for a differently seeded `initial_line`.
- **D2 reach while Voynich-like:** same rule for the best Voynich-like config; if no screened config is Voynich-like,
  D2 is "not testable".
- **D3 is G0 typical?** report where 0.418 (seed 19) falls in the S0 seed distribution (descriptive percentile; a
  "lucky/unlucky seed" call only if outside the S0 min–max).
- If any confirmed config exceeds 0.499, that is reported as "more rigid than Voynich" (direction stated).

## Verbose-cipher planted controls (Caesar *De Bello Gallico* I–IV, same file as C003)
Alphabet of 12 abstract symbols; each Latin letter replaced by a 2-symbol code (Python RNG seed 4004).
- **VC-N:** one fixed code per letter (no positional variants).
- **VC-P:** three codes per letter, one each for word-initial, medial and final position, all drawn from the same 12
  symbols.
- **VC-D:** like VC-P but initial, medial and final codes drawn from three disjoint 4-symbol pools (upper bound).
- Glyph unit = one symbol. Bootstrap R as in C003.
- **Planted rule (must pass for the verbose-cipher part to count):** VC-P lower 99 % bound > VC-N upper bound, and
  VC-D > VC-P likewise. Descriptive question: where do they sit relative to Voynich 0.485?

## Controls for the sweep
- **Negative:** the D1-confirmed generator output with glyphs shuffled within words → R < 0.05.
- **Re-measure:** the published sample re-measured with this tool must give 0.418 ± 0.005 (agreement with C003).
If a control fails: no verdict on the affected rule ("not testable this cycle").

## Budget
Heavy compute ≤ ~8 min, resumable (each run's result cached in `analysis/C004_sweep.jsonl`).

---
## Results (run 2026-11-04 ~22:40–22:47 PT, `tools/c004_generator_sweep.py`)
Outputs: `analysis/C004_sweep.jsonl` (sha256 `cb316f72…96086b88`, one line per run), `analysis/C004_confirm.json`
(`978b3dbd…0fce858e`), `analysis/C004_verbose_cipher.json` (`30171f4a…9618a783`). Generator jar and
`conf.properties` are listed in `data/MANIFEST.md` (not committed; fetch and check the hash).

### Corrections to the registration (no effect on the rules)
- **S1 has 18 settings, not 19** (the list above is authoritative; I miscounted). Screening total: 50 + 180 + 120 =
  **350 runs**, all completed, none failed.
- **`replace.probability` is not a free setting.** The generator source (`AbstractBaseGroupMorpher.java`, line 56)
  sets replace = 100 − add_remove − combine_split and prints a warning otherwise. My S1 settings `replace` = 20 and
  100 therefore produced output identical to the default (checked: identical R on all 10 seeds), and the value drawn
  for it in S2 was ignored. Documented behaviour, not a generator bug; the sweep simply has two fewer effective settings.

### Controls
| Control | Requirement | Result | Pass? |
|---|---|---|---|
| Instrument: default config, seed 19, reproduces the published sample | byte-identical | identical sha256 `1e954a17…2888dc11` | Yes |
| Re-measure the published sample with this tool | 0.418 ± 0.005 | 0.418 [0.405, 0.429] | Yes |
| Negative: D1-confirmed output, glyph units shuffled within words | R < 0.05 | 0.009 | Yes |
| Verbose-cipher planted rule: VC-P > VC-N and VC-D > VC-P (99 % intervals) | both | VC-N 0.164 [0.160, 0.167], **VC-P 0.115 [0.111, 0.119]**, VC-D 0.654 [0.649, 0.659] | **No** (VC-P < VC-N) |

The verbose-cipher control failed, so by the registered rule **the verbose-cipher part gives no verdict this cycle**.
Why it failed (diagnosis after the fact): with a fixed code per letter (VC-N), each code's first symbol inherits the
positional habits of Latin letters; with independent random codes per position drawn from one shared pool (VC-P), the
symbols that open, fill and close words are all near-uniform over the same 12 symbols, so position is *less* visible
per symbol, not more. My planted design assumed the opposite. VC-D (disjoint pools) does show that a verbose cipher
with position-specific symbol sets can be very rigid (0.654); that number is reported, not counted.

### Screening (point R on the first 6,000 words; Voynich V on its first 6,000 words: R 0.450, word length 4.26 units, TTR 0.365, h2 2.34 bits)
| Set | Runs | R min / median / max | Note |
|---|---|---|---|
| S0 default, seeds 1–50 | 50 | 0.372 / 0.423 / 0.478 | |
| S1 `use_word_final_substitutions=false` | 10 | 0.459 / 0.493 / 0.520 | TTR 0.17 |
| S1 `canFollow=voynich` | 10 | 0.480 / 0.502 / 0.550 | TTR 0.10 |
| S1 `canFollow=none` | 10 | 0.154 / 0.173 / 0.210 | Voynich-like vocabulary, no rigidity |
| S1 `sourceChooser=random` | 10 | 0.422 / 0.445 / 0.474 | the only S1 setting that is Voynich-like |
| S1 `add_remove=80` | 10 | 0.558 / 0.600 / 0.622 | TTR 0.10 |
| S1 `combine_split=0` | 10 | 0.535 / 0.566 / 0.598 | TTR 0.12 |
| other S1 settings | 120 | 0.350 – 0.549 | all medians 0.39–0.44 |
| S2 random configurations | 120 | 0.134 / 0.475 / 0.703 | |

26 of 350 screened runs are "Voynich-like" (word length, TTR and h2 all within ±15 % of Voynich): all 10
`canFollow=none` runs, all 10 `sourceChooser=random` runs and 6 S2 configurations. Their R ranges 0.134–0.474.
**Across the 120 random configurations, R and type/token ratio are strongly anti-correlated (Pearson r = −0.80):**
the generator becomes more positionally rigid mainly by shrinking its vocabulary.

### Confirmation on held-out seeds 5001–5010 (bootstrap, 300 × 6,000 words)
| Rule | Selected config | 10-seed mean R | Per-seed R range | TTR range | Verdict |
|---|---|---|---|---|---|
| **D1** highest screened R | S2.112 (seed 1113): `sourceChooser=position`, add_remove 2, combine_split 1, `max_repeat_count=1`, … (full config in JSON) | **0.649** | 0.613–0.671 | 0.066–0.095 | **reaches** (and exceeds Voynich 0.485) |
| **D2** highest R among Voynich-like | S1 `sourceChooser=random` (seed 10) | **0.448** | 0.425–0.463 | 0.29–0.35 | **does not reach** (< 0.470) |

**D3:** the published sample's 0.418 (seed 19) sits at the 34th percentile of the 50 default seeds (range
0.372–0.478): a typical seed, not an unlucky one.

### Verdicts
- **D1: the authors' generator can reach and exceed Voynich glyph-position rigidity**, but the configurations that do
  so produce a vocabulary about four times poorer than the manuscript's (TTR ≈ 0.08 vs 0.36 at 6,000 words). So C003's
  "still below Voynich" for the default sample was a property of one configuration, not of the generator family.
- **D2: no configuration in the explored space reaches Voynich rigidity while keeping Voynich-like word length,
  vocabulary richness and glyph-transition entropy**; the best confirmed is 0.448 vs the required 0.470. This is
  "not reached in 350 screened runs", **not excluded**: the space is large, `initial_line` was never varied, and a
  targeted optimiser could do better than random search.
- The useful new fact is the trade-off: in this generator, rigidity is bought with vocabulary. The manuscript has
  both, so a self-citation account must explain how it keeps a rich vocabulary *and* rigid glyph positions.
- Verbose cipher: **not testable this cycle** (planted control failed; design error diagnosed above).

### What this does not say
It does not say the manuscript is or is not meaningful, nor that the self-citation hypothesis is wrong. It compares one
statistic pair (R, TTR) plus two side statistics; Timm & Schinner tuned the generator for other properties. The
Voynich screening reference uses the first 6,000 words (mostly Currier A herbal), whose TTR may differ from other
sections; a section-matched comparison is open.

### Next
Targeted search (e.g. coordinate ascent on R subject to TTR ≥ 0.31) to make D2 sharper; a redesigned verbose-cipher
planted control (codes built with a stated positional rule, e.g. Hebrew-like final variants inside a verbose code);
section-matched Voynich references.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
