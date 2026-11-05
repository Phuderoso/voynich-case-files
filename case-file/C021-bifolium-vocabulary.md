# C021 — Do the two halves of a sheet remember each other? Bifolium vocabulary beyond scribe and language
### Expedição 21 · new family F-COD (codicology)

> **Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. **Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026. An AI did all of this work.

Status: **PRE-REGISTERED** (written before any similarity was computed on the real leaves). Results will be appended below.

## Question
A bifolium is one folded sheet: its two leaves (conjugates) sit far apart in a quire but were one physical object.
If the sheet, not the bound order, was the working unit, conjugate leaves should share vocabulary. But conjugates also
tend to share scribe (LFD hand), Currier language and illustration type, so a raw similarity says little. Question:
**do conjugate leaves share vocabulary beyond what hand × language × illustration type already explain?**

## Data
ZL 3b (`data/ZL3b-n.txt`). Leaf = all pages of one folio number (recto, verso, foldout panels); metadata from the
first page header of the leaf: `$Q` quire, `$B` bifolio within quire, `$H` hand, `$L` language, `$I` illustration.
Leaves with < 20 words dropped. Structure check (done before pre-registration, no similarities): 102 leaves, 50
complete conjugate pairs; 44 of them share hand, language and illustration type.

## Design (`tools/c021_bifolium_vocab.py`, seed 21021)
- Similarity: cosine of word-count vectors over word types with ≥ 5 tokens.
- **Look A (raw):** S = mean similarity of conjugate pairs − mean similarity of all other leaf pairs in the same quire.
- **Look B (controlled):** same, using only pairs whose two leaves share hand, language and illustration type.
- Null: random re-pairing of each quire's leaves into the same number of bifolia, 4000 draws; one-sided p.
- α = 0.025 per look (Bonferroni over 2 looks).
- **Calibration gate:** 40 destroyed-signal corpora per look (A: every leaf's words redrawn from its quire's pool;
  B: from its hand × language × illustration pool), 500 null draws each. FPR at α must be ≤ 0.075.
- **Power gate:** 40 planted corpora (B-destroyed corpus; one leaf of each conjugate pair gets 20 % of its words
  redrawn from its partner). Detection ≥ 0.8 at α required.
- Decision: a look failing either gate is **not testable**. Otherwise p ≤ α is **detected**, p > α is
  **not detected** (a bifolium effect of the planted size, 20 % shared words, is then excluded for that look).
- Expected reading: A detected and B not detected would mean the raw conjugate similarity is explained by scribe,
  language and section; B detected would be a bifolium-level signal beyond them.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
