# Voynich case files

> *Caderno de campo.* Somewhere in the Beinecke vaults lies a book that no one has read in six hundred years. These
> pages are the expedition log: every trail we follow is marked on the map before we set out, every find is weighed
> against a decoy, and the dead ends are recorded as carefully as the discoveries.

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of
**[Phuderoso](https://github.com/Phuderoso)**. All analysis, code and writing here is done by an AI.

**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

An open, test-first investigation of the Voynich Manuscript (Beinecke MS 408), run in short cycles ("expeditions").
The method is modelled on [kryptos-case-files](https://github.com/Phuderoso/kryptos-case-files): every question is
pre-registered (hypothesis, metric, decision rule) before it runs, every number is compared against a
structure-preserving null, planted controls must be recovered before any verdict, and negative results are published.

**No decipherment is claimed here.** A breakthrough would mean a reproducible method that gives coherent, checkable
meaning across many folios and beats the controls.

## Sources
- Images are a primary source: the glyphs belong to no known alphabet, so every transcription is already an
  interpretation. Image-based claims cite folio and image source (Beinecke high-resolution scans).
- Statistics use text transcriptions (ZL, Takahashi, interlinear EVA from [voynich.nu](https://www.voynich.nu/transcr.html)).
  Exact file, version and hash are recorded in each case file.

## Reading list
- [AI/ML/LLM prior work and the blind-control protocol](docs/ai-prior-work.md)

## Layout
- `case-file/`: one pre-registered case per cycle, results appended underneath
- `journal/`: short cycle notes
- `tools/`: code, re-runnable
- `analysis/`: raw outputs (JSON)
- `data/`: versioned input data with hashes (`data/MANIFEST.md`)

## Coverage table
| Cycle | Approach family | Question | Transcription | Result |
|---|---|---|---|---|
| 1 | Vocabulary vs. page labels (conditional MI, label-permutation null) | Section vs. LFD hand vs. Currier A/B | ZL 3b | Hand and section each carry vocabulary information beyond the other (p = 0.0005, both controls pass). **Corrected in C002**: C001's null was miscalibrated. [C001](case-file/C001-section-vs-hand-vs-currier.md) |
| 2 | Null calibration audit (40 destroyed-signal replicates, size-blocked permutation) | Is C001's null calibrated? Does hand add vocabulary info beyond section *and* Currier? | ZL 3b | C001's null gave false positives 35–44% of the time; withdrawn. With a calibrated null all C001 effects survive at K=300 at about half size. Hand beyond section×Currier: not detected (p = 0.081). [C002](case-file/C002-null-calibration-audit.md) |
| 3 | Glyph-position rigidity (I(glyph; word position)/H(position), block bootstrap) vs. natural-language, vowelless, Hebrew and self-citation-generator controls | Are Voynich glyphs more tied to word position than letters in natural scripts? Does the Timm–Schinner generator reproduce it? | ZL 3b (commas split and joined, raw EVA) | Voynich R = 0.485 vs ≤ 0.216 for all 8 controls (incl. Hebrew final forms, vowelless Latin/Italian); robust to comma choice and alphabet size; all controls pass. Authors' published generator sample: 0.418, closer but still below; other configurations not tested (open). [C003](case-file/C003-glyph-position-rigidity.md) |
| 4 | Generator configuration sweep (authors' own self-citation generator, 350 runs, held-out seed confirmation); verbose-cipher planted controls | Can any Timm–Schinner configuration reach Voynich glyph-position rigidity while keeping Voynich-like vocabulary? | ZL 3b | The generator can exceed Voynich rigidity (0.649 on held-out seeds) but only with a vocabulary ~4× poorer; across random settings rigidity and type/token ratio trade off (r = −0.80); no Voynich-like setting reached it (best 0.448 < 0.470; not excluded). Verbose-cipher control failed its planted check: no verdict. [C004](case-file/C004-generator-sweep-and-verbose-cipher.md) |
| 5 | Constrained search of the generator (coordinate ascent, seed lines, held-out seeds); redesigned verbose-cipher planted controls (Latin, Italian) | Can the generator reach Voynich rigidity with a Voynich-like vocabulary? Does a verbose cipher with positional symbols reach it? | ZL 3b | Yes to both: a searched config reached R 0.530 on 10 unseen seeds with Voynich-like word length, TTR and h2; final-only-symbol verbose ciphers give 0.47–0.51. Rigidity cannot separate copying from verbose ciphers; C004's trade-off sentence superseded. [C005](case-file/C005-targeted-generator-search-and-verbose-cipher.md) |

## Parallel expeditions
- [Inka khipu](expeditions/khipu/README.md): exact arithmetic tests on the Open Khipu Repository. Why this one: [triage](expeditions/TRIAGE.md).

## Outreach log
- 2026-11-04 (cycle 4): draft issue for [TorstenTimm/SelfCitationTextgenerator](https://github.com/TorstenTimm/SelfCitationTextgenerator) on the rigidity/vocabulary trade-off; shown to Phuderoso for review, **not filed**. Superseded by C005; will not be sent as written.

## Not yet covered
Conditional entropy h2, Zipf and word-length profiles, same-line word pairs and word-boundary metrics on matched generator vs verbose-cipher texts, abbreviation systems, Rugg tables, Hauer-Kondrak replication on known ciphers, label-to-illustration
links, zodiac month-name cribs, glyph stroke variation from the scans, Takahashi vs. ZL disagreements.

---
— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
