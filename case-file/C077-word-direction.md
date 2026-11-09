# C077 — Expedição 77: a flecha da palavra (NEW FAMILY F-DIR, direction of predictability)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Question:** is the inside of a Voynich word easier to predict **left-to-right** than **right-to-left** (or the reverse)? Is that asymmetry inside the range of natural languages and of the Timm–Schinner copying generator? Voynich words have a famously rigid slot order (prefix `q`/`o`, gallows, `e`-runs, endings `-dy`, `-aiin`), but no cycle so far has asked which direction that order is "written in". A short-memory model reading forward and one reading backward capture different parts of a word grammar. If one direction is much cheaper, the word was likely built from that side.

**Why a new family:** the last new family was F-JUNC (C074). The rule is at least one new family every three cycles. The README has no row on reading direction.

## Pre-registration (pushed before running the C077 tool)
- **Texts (first N = 15,000 word tokens each):** Voynich ZL 3b and IT2a paragraph text (`data/ZL3b-n.txt`, `data/IT2a-n.txt`, sha256 in `data/MANIFEST.md`; `L.ivtff_paragraphs`, C003 glyph units). There are 9 natural texts, as letters, via the C003/C044 loaders (Project Gutenberg boilerplate after the START marker included as in C044; accents stripped by the loader): Latin Caesar (pg218), Latin Descartes (pg23306), Italian Dante (pg1012), Italian Machiavelli (pg56498), Spanish Cervantes (pg2000), Finnish Kalevala (pg7000), Finnish Kivi (pg11940), Hebrew Genesis and Exodus (consonantal, `Gen.xml`, `Exod.xml`). Corpora are not committed, see `data/MANIFEST.md`. Generator: 10 default Timm–Schinner runs, **fresh seeds 11101–11110**, 2,500 lines each.
- **Model:** each word = `^ u1 … un $`; order-k Markov with add-0.1 smoothing (alphabet + `$` + one unseen symbol); two-fold training on even/odd of 20 contiguous blocks, testing on the other half. Forward = as read; backward = each word reversed. H = test cross-entropy, bits per predicted symbol (units plus `$`).
- **Statistic:** A_k = H_backward − H_forward. A positive value means the word is easier to predict left-to-right. **Primary k = 3**; k = 1, 2 descriptive (with full joint information A would be 0, so A measures which direction a short memory reads better).
- **CI:** block bootstrap of the 20 blocks (B = 1,000), 95% percentile interval.
- **Decision vs natural:** OUTSIDE NATURAL if the manuscript's CI lies entirely outside [min, max] of the 9 natural point values. INSIDE NATURAL if its point value lies inside. Otherwise NOT CALLED. **FPR gate (leave-one-out):** each natural text is judged against the other 8 by the same rule. More than 1/9 called OUTSIDE makes the comparison NOT TESTABLE (a natural spread too wide for its own CIs).
- **Decision vs generator:** ABOVE / BELOW GENERATOR if the manuscript's CI lies entirely above / below all ≥ 8 successful runs. INSIDE GENERATOR RANGE if its point value lies inside. Otherwise NOT CALLED.
- **Sanity (must hold exactly, else the run is void):** reversing every word of a text flips the sign of A.
- **Multiplicity:** one primary statistic (k = 3) in two transcriptions. A verdict counts only if **both** transcriptions agree. k = 1 and 2 carry no verdicts.
- **No power plant** (no agreed way to plant direction): a NOT CALLED or INSIDE is not an exclusion of a direction effect. It means "not distinguishable from natural/generator at this N".
- **Looked at before this push:** only that every text yields 15,000 tokens and the first three tokens parse. No A value was computed.
- **Tool:** `tools/c077_direction.py`, `timeout 600`, 8 processes, seed 7777.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
