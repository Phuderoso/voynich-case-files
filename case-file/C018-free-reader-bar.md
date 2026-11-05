# C018 — The bar for invented meaning: a blind control bank and three mechanical free readers
### Expedição 18 · new family F-LLM (step 0 of the `docs/ai-prior-work.md` §4 protocol)

> **Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. **Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026. An AI did all of this work.

Status: **PRE-REGISTERED** (this section committed before the counted run). Results are appended below after the run.

## Question
Many claimed Voynich "readings" fit a glyph-to-letter key and then count how many words come out as words of a
language, often with licences (abbreviation, anagram, vowels supplied by the reader). How many words does such a
method "read" in text that has **no message at all**? That number is the bar any Voynich reading by the same method
must beat, and it is the first measurement the §4 LLM protocol needs (a false-claim rate on negatives) before any
language model is shown a Voynich line.

## Readers (frozen in `tools/c018_free_reader_bar.py`)
Each fits a key by hill climbing (8 restarts × 12 000 proposals, accept if not worse), maximizing the number of tokens it reads.
- **STRICT**: many-to-one key (several glyphs may share a letter); a token reads if the decoded word is in the Latin lexicon (length ≥ 2).
- **LENIENT**: many-to-one key; a token reads if the multiset of its decoded consonants equals that of a lexicon word with ≥ 2 consonants (anagram allowed, vowels free).
- **INJ**: one-to-one key (a real monoalphabetic solver); exact lexicon match as in STRICT. Items with more glyph types than letters are "NA".
Lexicon: all word types of length ≥ 2 in Caesar, *De Bello Gallico* (`data/corpora/pg218.txt`, MANIFEST hash). Statistic: **CMR** (claimed-meaning rate) = read tokens / 100 tokens. Type-CMR and the true-key ("oracle") CMR of the positives are reported, not counted.

## Bank (seed 18018, 100-word items, 10 per class, 60 items shown in a shuffled blind order)
- **P1** positives: 10 Descartes, *Meditationes* passages (`pg23306`, other author than the lexicon), monoalphabetic substitution into integer symbols.
- **P2** positives: as P1, plus each word's letters sorted (alphagram, the Hauer–Kondrak anagram case).
- **N1** negatives: Timm–Schinner generator sample (`ts_generated_text.txt`).
- **N2** negatives: random EVA words, Voynich glyph-unit frequencies and word-length distribution.
- **N3** negatives: 10 Voynich passages (ZL 3b) with glyph units shuffled across the passage (word lengths and glyph counts kept).
- **V**: 10 Voynich passages (ZL 3b), each inside one page, from 10 other distinct folios (singulion rule: never across current page adjacency).
The blind bank (`analysis/C018_blind_bank.json`) stores each item's glyph strings and `sha256(salt + answer)`; the salt is published in the results so anyone can check the answers after scoring. It is the reusable control set for the later LLM step.

## Decision rule (per reader; 3 readers, Bonferroni α = 0.05/3)
1. **Gate**: the positives of the matching class (P2 for LENIENT, P1 for STRICT and INJ) must score above the **maximum** CMR of all 30 negatives in ≥ 9/10 items. If not, that reader is **not discriminating** and its Voynich readings are **not testable** (whatever they say).
2. **Bar** (the headline number): the 95th percentile and the maximum of negative CMR, per reader.
3. **Voynich**: only for a reader that passed the gate, count V items above the negative maximum. Under exchangeability one item exceeds the max of 30 with chance 1/31; ≥ 3/10 has binomial p ≈ 0.004 < 0.0167, so **≥ 3/10 = Latin-like signal under that reader**; 0–2 = **no reading above the bar**. A signal would only say the reader beats meaningless text with Voynich glyph statistics, not that the text is Latin; any such reading would go to the §4 protocol before any claim.

## Disclosed before the run
- Smoke runs on a different seed (19017, 2 items per class), not counted: (a) 4 × 600 proposals, STRICT/LENIENT only: the readers got stuck far below the true key; (b) 8 × 12 000 proposals: STRICT negatives 0.43–0.73 vs P1 0.37–0.45 (true-key Descartes strict CMR averages 0.53 on 20 other passages); LENIENT negatives 0.88–1.00 vs P2 0.91–0.92; (c) the INJ reader was added after (b) because the many-to-one readers looked non-discriminating; INJ smoke: P1 0.48/0.53, negatives max 0.29, V 0.18/0.21. So I expect STRICT and LENIENT to fail the gate and INJ to pass; the counted run tests that on fresh items.
- Hill climbing can stall; the oracle CMR of each positive is reported so a search failure is visible.
- One counted run. No reader, budget or lexicon change after this commit.

## Limits stated in advance
Latin only, one lexicon, one search method; 100-word items; the readers are mechanical stand-ins for the free-reading step of human or LLM decipherers, not a model of any one author's method. A Voynich "no reading above the bar" excludes Latin under a simple one-to-one key only at the power shown by P1, and says nothing about other languages or cipher classes.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
