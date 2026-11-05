# C020 — How far does the closed door reach? A power map of the C019 exclusion
### Expedição 20 · family F-LLM, step 0c

> **Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. **Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026. An AI did all of this work.

Status: **PRE-REGISTERED** at commit `7dbc2a8e` (05:55 PT), counted run 05:56:19–05:58:08 PT. Results appended below.

## Question
C019 excluded Latin written with one letter per EVA glyph unit (one-to-one reader INJ: gate 10/10, Voynich 0/10 above
the bar). Which nearby cipher classes does that exclusion also cover, i.e. which would INJ have caught if the manuscript
were built that way? This is a power map, not a Voynich test: **no Voynich passage is scored.**

## Design (`tools/c020_inj_power_map.py`, seed 20020; reader = C019 INJ unchanged)
Planted Latin (Descartes, C019 Latin-only filter: letters in lexicon alphabet, ≥ 35 % true-text Caesar coverage), 100 words, 10 items per class:
- **P1** plain substitution (repeat of C019's control; must pass ≥ 9/10 or the run is void);
- **PH** homophonic: the passage's 4 most frequent letters get a second symbol, used at random half the time;
- **PV** verbose: every vowel becomes its symbol plus one shared marker symbol (one letter → two glyphs, as often proposed for Voynich `ch`/`ii`-type sequences);
- **PN** noisy copy: plain substitution, then 15 % of symbol tokens replaced by a random symbol of the item (scribal error).
Negatives: N1 generator, N2 random EVA, N3 glyph-shuffled Voynich, 10 each, built by the C019 builder on seed 20021 (its Voynich items are discarded unscored).

## Decision rule
- Bar = maximum CMR of the 30 negatives. A planted item is **detected** if its CMR is above the bar; an item INJ cannot score (more symbol types than lexicon letters, "NA") counts as **not detected**.
- Per class (PH, PV, PN): ≥ 9/10 detected → the C019 exclusion **covers** that class; otherwise **not covered** (Voynich built that way could have escaped C019). Descriptive, so no multiplicity correction; P1 is the validity check.

## Disclosed before the run
A sanity check of the positive builder (seed 1, no reader run) showed PH items have 25–26 symbol types against 24 lexicon letters, so most PH items will be NA; I expect PH "not covered" for that reason, which is itself the answer (a one-to-one reader cannot read homophonic text). One counted run.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

---

## Results (counted run 2026-11-05, 05:56:19–05:58:08 PT, after pre-registration commit `7dbc2a8e`; 109 s; `analysis/C020_results.json`, `analysis/C020_run_log.txt`)

Bar (max of 30 negatives) = **0.37** (generator N1 0.25–0.37, N2 0.12–0.16, N3 0.07–0.19).

| Class | CMR | Detected | Verdict |
|---|---|---|---|
| P1 plain substitution (control) | 0.51–0.60 | **10/10** | run valid |
| PH homophonic (4 letters doubled) | all 10 NA (more symbol types than letters) | 0/10 | **not covered** |
| PV verbose (vowel → 2 glyphs) | 0.10–0.23 | 0/10 | **not covered** |
| PN plain + 15 % scribal noise | 0.18–0.36 | 0/10 | **not covered** |

### What this means for C019 (scope correction)
C019's exclusion holds only for **clean** one-letter-per-glyph Latin. Doubling four letters, writing vowels with two
glyphs, or miscopying 15 % of glyphs each pushes planted Latin below the noise bar every time. The last one matters
most: Voynich studies (and arXiv 2610.34499) allow for substantial miscopying, and 15 % noise alone already hides
real Latin from this reader. C019's README row and verdict are narrowed accordingly ("clean copy only").

Also noted: the generator's maximum here (0.37) is higher than in C019 (0.32); with 10 generator items the bar itself
moves by about 0.05 between seeds. A future bar should use more negatives.

### Verdict
The one-to-one reader is a narrow instrument: **covers** plain substitution only; **not covered**: homophonic, verbose,
noisy copies. Any LLM or human "free reading" must therefore be tested against the same classes before an exclusion
or a reading is claimed for them.

### Next
F-LLM step 1 needs a reader that can survive noise and verbosity (e.g. many-to-one keys scored against a
per-class bar, or an n-gram language-model score instead of exact words), checked on these same planted classes.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
