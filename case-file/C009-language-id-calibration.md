# C009 — Expedição 9: The Compass That Points Anywhere. Calibrating unigram-profile language identification on generator noise

**Status:** pre-registered 2026-11-05 01:05 PT, before any run. Results appended below.
**Approach family (new to the coverage table):** calibration of a published decipherment-method stage (Hauer &
Kondrak 2016's idea of identifying the plaintext language of a substitution cipher from its letter-frequency profile,
the stage that pointed them to Hebrew) against planted ciphers and meaningless generator text. My implementation is a
simplified sorted-unigram profile matcher, **not** their code or their full method (no anagram stage, no 380-language
UDHR set). The backlog item "re-run the Hauer–Kondrak method on known ciphers and generator noise" is addressed only
in this simplified form.

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Question
A sorted letter-frequency profile is unchanged by any simple substitution, so it can name the language behind a
substitution cipher. But it is also unchanged by shuffling letters, so it cannot tell language from letter salad with
the same frequencies. **How confidently does it "identify" a language in text that has none (the Timm–Schinner
generator), and is the manuscript's identification more confident than that?**

## Method
- Symbols: glyph units (C003 tokenisation: `cth ckh cph cfh ch sh` then single characters) for Voynich and generator
  text; letters for natural texts.
- Profile: relative frequencies sorted in descending order, padded with zeros to 30 ranks.
- Distance: L1 between profiles. Identification = nearest reference language;
  **margin** m = (d₂ − d₁)/d₁ (second-nearest minus nearest, relative).
- References (first half of each text): Latin (Caesar, pg218), Italian (Dante, pg1012), Spanish (Cervantes, pg2000),
  Hebrew (Genesis, WLC, consonants, final forms kept), vowelless Latin (Caesar with a e i o u removed; C003's abjad
  control).
- Samples: 6,000 consecutive words; 20 per text.

## Controls and decision rules
- **Planted gate:** 20 samples per language from the *second* half of each text (Latin also tested on Descartes,
  pg23306, an unseen author), each passed through a fresh random simple substitution. Overall identification accuracy
  must be ≥ 80 %, or the method is "not testable".
- **Non-language bar B:** 99th percentile of the margins on 20 samples of the default generator (seeds 1–10) and 20 of
  C005's matched generator (seeds 6001–6010), pooled.
- **Look (1):** Voynich (ZL 3b, 20 samples). If the Voynich median margin > B, its identification is "more confident
  than for generator noise". Otherwise it is "no more confident than meaningless text; not evidence for that
  language".
- Descriptive (not looks): the language each text is assigned; Currier A and B separately; raw EVA characters instead
  of glyph units.

## Budget
≈ 1 min; output `analysis/C009_results.json`.

---

## Results (run 2026-11-05, 14 s; `tools/c009_language_id_calibration.py`, output `analysis/C009_results.json`)

- **Planted gate: passed.** 120/120 substitution-cipher samples identified correctly (100 % for every language,
  including the unseen Latin author Descartes and vowelless Latin). Median margin 1.78.
- **Generator noise (40 samples, no language in it):** assigned Latin 13, Spanish 13, vowelless Latin 10, Italian 4.
  Margins: median 0.135, max 0.589. **Bar B (99th percentile) = 0.541.**
- **Voynich (glyph units, 20 samples):** assigned Spanish 10, Latin 5, vowelless Latin 4, Italian 1, Hebrew 0.
  Median margin **0.036**, max 0.283.
- **Verdict (1 look): "no more confident than meaningless text".** The manuscript's best match is weaker than the
  matches generator noise gets, and it changes from sample to sample.

Descriptive (not looks):

| Variant | Assigned | Median margin |
|---|---|---|
| Raw EVA characters | Latin 13, Italian 6, Spanish 1 | 0.061 |
| Currier A | Latin 12, Spanish 8 | 0.128 |
| Currier B | Spanish 12, Italian 4, Latin 4 | 0.030 |

The tokenisation alone changes the "language": glyph units lean Spanish, raw EVA characters lean Latin.

## What this means
- A profile matcher that is perfect on real substitution ciphers (120/120, margins ≈ 1.8) gives the manuscript margins
  about fifty times smaller, and smaller than it gives text from a copying machine that contains no language. On this
  stage, the manuscript looks like **no simple substitution of any of these five languages**. That is consistent with
  long-standing results that Voynichese is not a simple substitution.
- **Calibration lesson:** any unigram-profile "identification" of the manuscript's language must be reported against a
  generator-noise bar. Without that bar, a matcher always names *some* language: here, whatever the reference set and
  the glyph segmentation favour.
- **Limits:** five reference languages only (Hebrew included, Arabic not available locally). This is not Hauer &
  Kondrak's method (they used 380 languages, other features, and a separate anagram stage), so this cycle **does not
  test their Hebrew result**. It tests one idea from their first stage. Next step for this family: add their other
  features and a larger language set, with the same generator bar.

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
