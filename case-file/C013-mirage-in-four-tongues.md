# C013 — Expedição 13: The Mirage in Four Tongues. Does a free solver find more real words in the manuscript than in meaningless text?

**Status:** pre-registered 2026-11-05 02:56 PT, before any run. Results appended below.
**Approach family:** extends C012 (solver-based decipherment with blind controls) to three new target languages and
moves the decision from a 4-gram score to a **word-level** count, which C012 showed only post hoc.

> I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
> **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. /
> Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Question
C012 found no more Latin in the manuscript than in meaningless text, but it used one language and a 4-gram score that
rewards repetition (`sese sesese`). **Under the same free homophonic solver, does the manuscript yield more distinct
dictionary words than meaningless text with the same glyph inventory, in Italian, consonantal Hebrew, vowelless
Latin (an abjad-style Latin), or Latin?** Italian and Hebrew are the two languages most often proposed in popular
accounts (Hebrew: Hauer & Kondrak 2016); vowelless Latin covers the "abjad" idea from Reddy & Knight.

## Method (identical solver to C012 unless stated)
- **Solver:** each cipher symbol (C003 glyph unit) maps to one letter of the target alphabet; several symbols may share
  a letter (homophonic); word spaces kept; 20 restarts × 15,000 single-symbol hill-climbing moves; objective = joint
  4-gram log10 probability (floor 0.01 counts), as in C012's final run.
- **Languages** (language model trained on corpus T; planted plaintext from a *different* text P; dictionary D = all
  word types of T, used only for scoring):
  | Code | Alphabet | T (model + dictionary) | P (planted, held out) |
  |---|---|---|---|
  | LA | a–z (26) | Caesar, *De Bello Gallico*, pg218, first half (D: whole text) — as C012 | Descartes, pg23306 |
  | LV | Latin with a, e, i, o, u removed (C003 `devowel`) | same Caesar, devowelled | Descartes, devowelled |
  | IT | a–z (accents stripped) | Dante, *Divina Commedia*, pg1012 (whole) | Machiavelli, *La Mandragola — La Clizia — Belfagor*, pg56498 (new) |
  | HE | 22 consonants, final forms merged (C003 `hebrew`) | Genesis, WLC (morphhb Gen.xml) | Exodus, WLC (morphhb Exod.xml, new) |
- **Texts per language (35 runs):** 1,500 words each.
  - **Planted (blind):** 5 samples of P under (P1) random one-to-one substitution and (P2) homophonic substitution with
    the 8 most frequent letters each split into 2 symbols. 10 runs.
  - **Meaningless nulls:** Timm–Schinner generator default config (seeds 11–15), C005 matched config (seeds
    6011–6015), independent glyph text with Voynich unit frequencies and word lengths (seeds 510–514). 15 runs. These
    seeds are fresh (C012 used 1–5, 6001–6005, 500–504).
  - **Manuscript:** 5 samples of 1,500 consecutive words of ZL 3b (random starts, seed 13), C003 units. The same five
    samples and the same 15 nulls are used for all four languages.
- **Primary metric W:** number of distinct decoded tokens of length ≥ 3 that are in dictionary D.
- **Gate (per language):** letter accuracy ≥ 0.80 in at least 9 of 10 planted runs; otherwise that language is
  "not testable".
- **Bar (per language):** the maximum W over the 15 null runs.
- **Decision (per language):** if the manuscript's median W > bar, the result is *provisional*; it is reported as
  "more <language> words than meaningless text" only if a second, fresh set of 5 manuscript samples (seed 113) also has
  median W > bar. Otherwise: "no more <language> words than meaningless text under this solver".
- **Comparisons:** 4 looks (one per language). Under exchangeability, the chance that the manuscript median of 5 beats
  the maximum of 15 nulls is 10/1140 ≈ 0.009 per look, ≈ 0.035 for the family, before the replication step.
- **Descriptive (not decisive):** 4-gram score S per run and C012-style S bar; decoded excerpts; plain-text ceiling.
- **Compute:** ≤ 8 minutes on 8 cores; results checkpointed per run in `analysis/C013_cache.jsonl` (resumable).

## Limits stated in advance
Letter-level substitution with kept word spaces, left-to-right reading, four languages, one dictionary per language.
Not tested here: verbose or syllabic ciphers, anagrams (Hauer & Kondrak), right-to-left reading, nomenclators, ciphers
that move word boundaries, other languages. A dictionary drawn from one text undercounts real words; the bar is built
with the same dictionary, so the comparison stays fair.

## Results (run 2026-11-05, about 02:57–03:04 PT, after the pre-registration commit 6a1c6903; `tools/c013_four_tongues.py`, 7 min 58 s on 8 cores; `analysis/C013_results.json`, per-run cache `analysis/C013_cache.jsonl`)

One run, no reruns. Transcription: ZL 3b (`data/ZL3b-n.txt`, "Version 3b of 13/05/2025", sha256 bf5b6d4a…beccafc).
Manuscript samples (start word, folios): 9644 (f57r–f67r1), 12171 (f68v1–f72v3), 15109 (f76r–f78r), 16974
(f78v–f80v), 19055 (f81v–f84r). All five fell in the astronomical/cosmological/balneological quires; no herbal page
was sampled (a limit of seed 13, stated here, not changed).

| Lang | Planted gate (acc ≥ 0.80) | Planted W | Null W (15 runs) | **Bar W** | Manuscript W (5 samples) | **Median** | Verdict |
|---|---|---|---|---|---|---|---|
| LA Latin | **10/10** (0.92–1.00) | 179–270 | 2–8 (median 4) | **8** | 9, 5, 4, 5, 8 | **5** | no more Latin words than meaningless text |
| LV vowelless Latin | **0/10** (0.14–0.15) | 0 | 0–7 | 7 | 5, 3, 10, 9, 12 | 9 | **not testable** (gate failed) |
| IT Italian | **10/10** (0.99–1.00) | 317–380 | 6–20 (median 14) | **20** | 45, 20, 17, 19, 22 | **20** | no more Italian words than meaningless text (median equals the bar; rule needs >) |
| HE Hebrew | **9/10** (0.77–0.96) | 128–345 | 14–35 (median 28) | **35** | 26, 27, 14, 16, 11 | **16** | no more Hebrew words than meaningless text |

(Manuscript W listed in start-word order 9644, 12171, 15109, 16974, 19055.) No language reached the provisional stage,
so the pre-registered replication set (seed 113) was not run.

**Verdict:** under this solver the manuscript yields **no more Latin, Italian or Hebrew dictionary words than
meaningless text** with the same glyph inventory. **Vowelless Latin is not testable**: the solver failed its planted
gate.

### Why the vowelless-Latin gate failed (disclosed)
With vowels removed, Latin is dominated by `s`, `t`, `n` clusters, and the joint 4-gram score of a string such as
`ss sss ssss` (S ≈ −3.19) is higher than the score of the true devowelled plaintext. The solver therefore collapses
every planted cipher to `s` (letter accuracy 0.14 = the share of `s`), and does the same to the manuscript and the
nulls. This is the same degeneracy C012 saw in one manuscript sample (`sese sesese`), now strong enough to defeat the
planted control. Per the rule, no verdict. A repair (for example a penalty on the decoded letter-frequency profile, or
a properly normalised conditional model with back-off) must be pre-registered and pass the gate in a later cycle.

### Descriptive (not part of the decision)
- **4-gram score S** (C012-style bar = max over nulls): LA manuscript −4.42 to −4.24 vs bar −4.27 (2 of 5 above);
  IT −4.63 to −4.30 vs −4.34 (1 of 5 above); HE −4.57 to −4.18 vs −4.15 (0 of 5 above). Planted ranges: LA −4.43 to
  −4.06, IT −3.82 to −3.77, HE −4.46 to −4.16. S again rewards repetition; W is the better yardstick.
- **The highest single manuscript value** is Italian, sample 9644 (f57r–f67r1): W = 45, above the bar of 20. Its words
  are short and repetitive (`ratto, tira, rai, atto, pera, era, tra, rara`) inside strings such as
  `diira etira riiraerta tira rar perirai`. One sample of five, against a planted range of 317–380; the median rule
  exists for exactly this case. Recorded as a lead of very low weight, not a finding.
- **Hebrew nulls are generous**: meaningless text reaches 14–35 distinct Genesis words, because short consonantal
  Hebrew words (ימ, מימ, הימ, ויהי) are dense in any string of a few letters. Any claimed Hebrew reading that counts
  dictionary hits needs a bar like this one.
- The "plain-text ceiling" S in the JSON is computed on the first 1,500 words of each planted text, which include the
  English Project Gutenberg credit lines; it is unreliable and not used.

### Audit of C012
C012's post-hoc word count (manuscript 4–10 distinct Latin words vs 2–6 for its nulls) hinted at a slight excess. With
the word count now pre-registered, fresh nulls and fresh manuscript samples, the Latin null maximum is 8 and the
manuscript median 5: **no excess**. C012's verdict stands; its post-hoc table should not be read as a weak signal.

### What this does and does not show
- It extends the invented-meaning bar to Italian and Hebrew and makes the word count the decision. A free
  letter-substitution solver finds as many real Latin, Italian and Hebrew words in meaningless generator text as in
  the manuscript.
- Comparisons: 4 looks; none positive, so no correction changes anything.
- Not tested: vowelless Latin (gate failed), verbose/syllabic ciphers, anagrams, right-to-left reading,
  nomenclators, ciphers that move word boundaries, other languages, herbal-section samples.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
