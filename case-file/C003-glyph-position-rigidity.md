# C003 — Expedição 3: The Fixed Stones. How rigidly do Voynich glyphs keep their place in the word?

**Status:** pre-registered 2026-11-04 22:00 PT (before any run). Results appended below.
**Approach family:** glyph-position rigidity against natural-language, vowelless-script and self-citation-generator
controls. New to the coverage table (C001–C002 were vocabulary-vs-page-label tests).

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Question
Many Voynich glyphs seem to live only at the start, middle or end of a word (e.g. `q` initial, `n`/`y` final).
Is this positional rigidity stronger than in natural-language texts written in alphabets of similar size, including
vowelless (abjad-like) writing and a script with real positional letter forms (Hebrew final letters)? And does a
Timm–Schinner-style self-citation generator reproduce it?

## Data
- Voynich: `data/ZL3b-n.txt` (ZL 3b, sha256 `bf5b6d4a…ccafc`), C001 tokenisation (drop words with `?`/`*`, keep
  first reading of `[a:b]`). **V** = split at uncertain spaces (`,`), as in C001. **V'** = uncertain spaces joined.
- Controls (all to appear in `data/MANIFEST.md` with sha256):
  Latin: Caesar *De Bello Gallico* I–IV (Gutenberg #218), Descartes *Meditationes* (#23306);
  Italian: Dante *Divina Commedia* (#1012); Spanish: *Don Quijote* (#2000);
  Hebrew: Genesis, Westminster Leningrad Codex via openscriptures/morphhb `wlc/Gen.xml`, points stripped
  (HE = final letter forms kept, HEm = final forms merged with their base letter);
  vowelless: Caesar and Dante with `a e i o u` removed (LAv, ITv).
  Latin-script texts: Gutenberg header/footer removed, lowercased, diacritics stripped, letters a–z only.

## Glyph units
Voynich EVA tokenised greedily into `cth ckh cph cfh ch sh`, then single characters. Sensitivity: raw EVA characters.

## Metrics
- **M1 (primary) positional rigidity** R = I(G; P) / H(P), where G = glyph unit, P ∈ {initial, medial, final},
  over all glyph tokens in words of ≥ 2 units. 0 = glyphs ignore position, 1 = each glyph type sits in one position.
- **M2 (secondary) rigid mass**: share of glyph tokens whose type has ≥ 90 % of its tokens in one position class.
- Every text is measured on equal samples of **6,000 words**: 300 bootstrap samples built from blocks of 20
  consecutive words; report mean and 99 % interval (0.5–99.5 percentiles).

## Controls (must behave before any verdict)
- **Negative:** Voynich with glyphs shuffled within each word → R must fall near 0 (< 0.05).
- **Planted positive:** Caesar with Hebrew-like final forms planted for `s m t` (word-final s/m/t replaced by new
  symbols) → rule D1 must call it "more rigid than Caesar".
- **False-positive calibration:** for each natural-language control, 40 random splits into two halves
  (alternating 20-word blocks assigned at random); count how often the D1 rule calls one half "outside" the other.
  Rule accepted if this happens in ≤ 5 % of splits overall.

## Generator
Self-citation generator **re-implemented by me from the published description** (Timm & Schinner, Cryptologia 2020),
not their code: each new word copies a word from the previous 1–3 lines, then applies 0–2 changes (glyph swaps within
similarity groups `o/a/y`, `ch/sh`, `k/t`, `p/f`, `l/r`, `d/s`, `e/ee`; add or drop a prefix `q o y ch`; drop or add a
final glyph), occasionally joins two words; ~10 words per line.
- **G1:** seeded with the first 3 lines of f1r (Voynich words); 10 seeds.
- **G2 (diagnostic):** seeded with random glyph strings drawn from Voynich glyph-unit frequencies (no positional
  structure) — tells whether copying *creates* rigidity or only *inherits* it from the seed.

## Decision rules (pre-registered looks: D1 on V, D1 on V', D2 → 3 primary looks; 99 % intervals used throughout)
- **D1:** Voynich is "more rigid than the natural-language envelope" if the lower 99 % bound of its R exceeds the
  upper 99 % bound of **every** control (LA×2, IT, ES, HE, HEm, LAv, ITv). "Inside the envelope" if its interval
  overlaps the controls' range. Robust only if the verdict is the same for V and V'.
- **D2:** G1 "reproduces" Voynich rigidity if Voynich's mean R lies inside [min, max] of the 10 G1 seed means widened by
  the mean G1 interval half-width; otherwise "does not reproduce" (direction stated). The verdict covers my
  re-implementation only.
- If a control fails, no verdict on the affected rule ("not testable this cycle").
- Currier A vs B rigidity: descriptive only, not a verdict.

---
## Results (run 2026-11-04 ~22:05–22:11 PT, `tools/c003_position_rigidity.py`; sensitivity `tools/c003_sensitivity.py`)
Outputs: `analysis/C003_results.json` (sha256 `54f4acfb…37b1efe9`), `analysis/C003_sensitivity.json` (`a6072cfc…c809e1ca`).
Inputs: see `data/MANIFEST.md` (control corpora are not committed; URLs and sha256 are listed so they can be re-fetched).

### Controls first
| Control | Requirement | Result | Pass? |
|---|---|---|---|
| Negative: Voynich, glyphs shuffled within words | R < 0.05 | R = 0.006 [0.004, 0.007] | Yes |
| Planted: Caesar with final forms for s/m/t | D1 calls it more rigid than Caesar | 0.303 [0.294, 0.312] vs 0.139 [0.131, 0.146] | Yes |
| False-positive calibration: 200 half-vs-half splits of 5 natural texts | D1 fires ≤ 5 % | 0 / 200 (0 %) | Yes (the rule is conservative) |

### M1 positional rigidity R (6,000-word samples, mean and 99 % interval; alphabet = distinct symbols)
| Text | R | 99 % interval | M2 rigid mass | Alphabet |
|---|---|---|---|---|
| **Voynich V** (ZL 3b, commas split) | **0.485** | 0.470–0.499 | 0.263 | 31 |
| **Voynich V'** (commas joined) | **0.478** | 0.464–0.492 | 0.313 | 31 |
| Voynich, raw EVA characters | 0.503 | 0.488–0.516 | 0.327 | — |
| Voynich, Currier A only | 0.457 | 0.443–0.473 | 0.299 | 30 |
| Voynich, Currier B only | 0.527 | 0.515–0.541 | 0.332 | 30 |
| Hebrew Genesis, final forms kept (HE) | 0.208 | 0.200–0.216 | 0.067 | 27 |
| Italian, Dante | 0.198 | 0.189–0.208 | 0.009 | 25 |
| Spanish, Quijote | 0.188 | 0.180–0.196 | 0.018 | 25 |
| Latin, Caesar | 0.139 | 0.131–0.146 | 0.082 | 24 |
| Latin, Caesar, vowels removed (LAv) | 0.134 | 0.126–0.142 | 0.000 | 19 |
| Italian, Dante, vowels removed (ITv) | 0.128 | 0.117–0.140 | 0.026 | 20 |
| Latin, Descartes | 0.122 | 0.114–0.128 | 0.079 | 26 |
| Hebrew Genesis, finals merged (HEm) | 0.094 | 0.087–0.099 | 0.000 | 22 |

### Generators
| Generator | R (seed means) | Note |
|---|---|---|
| G1 my re-implementation, Voynich seed (pre-registered), 10 seeds | 0.06–0.26 | drifts into degenerate words (e.g. `ddooeeee`); seen in a smoke test before the formal run |
| G1b amended re-implementation (exploratory, written after that smoke test), 10 seeds | 0.18–0.19 | |
| G2 copying from an unstructured random seed, 10 seeds | 0.08–0.34 | copying alone does not create Voynich-level rigidity |
| **G0 the authors' own published sample** (TorstenTimm/SelfCitationTextgenerator, default config, seed 19, 10,832 words; added mid-cycle, before measuring it) | **0.418** [0.407, 0.430] | one sample only |

### Sensitivity (exploratory)
Merging glyph types with < 0.5 % of tokens into one symbol (alphabets 18–25) changes nothing material: Voynich 0.483,
G0 0.414, HE 0.204, Dante 0.198, Caesar 0.139. Alphabet size does not explain the gap.

### Verdicts (by the pre-registered rules)
- **D1 (V and V'): Voynich is more positionally rigid than every natural-language control**, including vowelless
  Latin/Italian and Hebrew with its genuinely positional final letters. Lower bound 0.464 vs highest control upper
  bound 0.216; same verdict under both comma conventions and raw EVA, so it is **robust** to these transcription choices.
  Voynich glyph identity carries about 2.3× the positional information of the most positional script tested.
- **D2 (G1, my re-implementation): does not reproduce** (Voynich far above the G1 range). This says my
  re-implementation is a poor copy, not that the self-citation idea fails.
- **G0 (the authors' own sample), same D2 rule, flagged as a post-registration addition:** much closer than any natural
  language (0.418, also above every natural-language control) but **still below Voynich** (0.485), and below both
  Currier A (0.457) and B (0.527) taken separately; intervals do not overlap. Only one configuration and one seed were
  tested, so "the self-citation generator cannot reach Voynich rigidity" is **not excluded**; it is open.
- Currier B is more rigid than Currier A (descriptive; intervals disjoint).

### What this does and does not say
- It does not say the text is meaningless or meaningful. It says Voynich glyphs are bound to word positions far more
  tightly than letters in any of eight natural-language and abjad-like controls, so a simple letter-for-letter cipher
  of these languages would have to add positional rules (e.g. positional variants, verbose or syllabic coding) to match.
- It agrees in direction with known qualitative observations (e.g. Currier, Stolfi's word grammar) and with
  Rozanova & Temerev (2026) and Zhang & Sheng (2026) on tight glyph binding; this cycle adds a calibrated, controlled
  number for it and a direct comparison with the published generator sample.
- Not testable this cycle: languages with syllabic scripts or vowel-pointing systems; other generator configurations.

### Next
Run the authors' generator across its configuration space (many seeds; `use_word_final_substitutions` on/off) and ask
whether any setting reaches Voynich R while keeping its other statistics; a verbose-cipher control (Latin through a
positional verbose cipher) as a second planted family.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
