# C018 — The bar for invented meaning: a blind control bank and three mechanical free readers
### Expedição 18 · new family F-LLM (step 0 of the `docs/ai-prior-work.md` §4 protocol)

> **Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. **Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026. An AI did all of this work.

Status: **PRE-REGISTERED** at commit `0231407d` (05:24:56 PT), counted run 05:25:02–05:27:20 PT. Results appended below.

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

---

## Results (counted run 2026-11-05, 05:25:02–05:27:20 PT, after pre-registration commit `0231407d`; `tools/c018_free_reader_bar.py`, 138 s; `analysis/C018_results.json`, console log `analysis/C018_run_log.txt`, blind bank `analysis/C018_blind_bank.json`, salt `15bca3cd2fcf5bb5`)

### 1. The counted looks (CMR = share of the 100 tokens the reader "reads" as Latin)

| Reader | P1 (Latin, mono-sub) | P2 (Latin, + anagram) | N1 generator | N2 random EVA | N3 shuffled Voynich | **Bar** (negatives p95 / max) | Gate | V (Voynich) |
|---|---|---|---|---|---|---|---|---|
| STRICT | 0.40–0.62 | 0.38–0.56 | **0.63–0.72** | 0.38–0.54 | 0.34–0.53 | 0.70 / 0.72 | P1 0/10: **FAIL** | 0.33–0.68, 0 above max |
| LENIENT | 0.80–0.95 | 0.86–0.94 | **0.96–1.00** | 0.83–0.92 | 0.85–0.93 | 1.00 / 1.00 | P2 0/10: **FAIL** | 0.90–1.00, 0 above max |
| INJ | 0.21–0.60 (2 NA) | 0.17–0.26 | 0.20–0.33 | 0.11–0.15 | 0.09–0.14 (1 NA) | 0.30 / 0.33 | P1 5/10: **FAIL** | 0.12–0.29, 0 above max |

True-key ("oracle") CMR of the P1 plaintexts: STRICT/INJ 0.10–0.60 (median 0.53), LENIENT 0.36–0.66.

**By the pre-registered rule, all three readers failed their gate, so all three are *not discriminating* and the Voynich
readings are *not testable* under any of them.** No Voynich passage scored above the negative maximum under any reader
(this is reported, not interpreted).

### 2. The bar (the headline)
- A many-to-one key with exact word matching "reads" **63–72 % of Timm–Schinner generator words as real Latin words**,
  more than the true key reads in real Latin by another author (median 0.53). The search finds more "Latin" in a
  meaningless text than there is in a real one, because short frequent words (`et`, `in`, `ad`, `si`, …) can be
  manufactured from any repetitive glyph stream.
- Adding the anagram-and-supply-the-vowels licence reads **96–100 % of generator text and 83–92 % of random glyph
  strings**. Under that licence, a reading of "almost every word" carries no information at all.
- Only the one-to-one key keeps the negatives low (max 0.33), and even it had a narrow margin over working positives.

So a claimed Voynich reading that rests on a free key plus abbreviation/anagram/vowel licences must report its score
against meaningless controls; a word-hit rate of 70–100 % is what such a method produces from noise.

### 3. Why the INJ gate failed (disclosed, post-hoc, not counted)
- **Bank defect.** Two of the ten P1 passages are not Latin: the Gutenberg edition of the *Meditationes* contains a
  German preface ("uebersetzung des werkes erschien …") and French notes ("et les autres modes ou accidents …"). Both have
  26 letter types against 24 in the lexicon, so INJ returned NA. One N3 item was NA for the same reason (more than 24 glyph types).
- **Search stalls.** Of the 8 Latin P1 items, 5 beat the bar (0.52–0.60, close to their oracle) and 3 stalled at
  0.21–0.28, below their true-key scores (the lowest Latin oracle is 0.18: philosophical vocabulary absent from Caesar).
- Even with the defect removed, 5/8 is below the 9/10 standard. The verdict stands: INJ is not discriminating at this
  budget. A repair (Latin-only passage filter by lexicon coverage before banking; more restarts or annealing for INJ)
  is a new pre-registration, not a re-run of this one.

### 4. Descriptive (not counted)
Voynich passages behave like the generator and the glyph-shuffled controls under every reader (STRICT median 0.565 vs
generator 0.685; INJ median 0.205 vs generator 0.245). Nothing here hints at Latin under a simple key, consistent with arXiv 2610.34499 and
C013/C014. This is not a test result.

### 5. The blind bank
`analysis/C018_blind_bank.json` holds the 60 items in shuffled order (`B00`–`B59`), glyphs only, with
`sha256(salt + answer)`; the salt above lets anyone verify. It is the first control set for the §4 LLM step. It carries
the P1 defect of §3, so the next step will rebuild it with a language filter and publish both.

### Verdict
- STRICT and LENIENT: **excluded as discriminating methods** (their negatives score at or above real enciphered Latin;
  the bar is 0.72 and 1.00).
- INJ: **not discriminating at this budget** (gate 5/10, partly from a bank defect).
- Voynich: **not testable** under all three readers.

### Next
Rebuild the bank with a Latin-only filter and a stronger one-to-one search, then re-gate INJ (power first). Only after
a reader passes its gate does the LLM step start, with the same negatives and the bar measured here.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
