# Voynich case files

An open, test-first investigation of the Voynich Manuscript (Beinecke MS 408), run in short cycles by **Voynich**,
a research agent working for Phuderoso. The method is modelled on
[kryptos-case-files](https://github.com/Phuderoso/kryptos-case-files): every question is pre-registered (hypothesis,
metric, decision rule) before it runs, every number is compared against a structure-preserving null, planted controls
must be recovered before any verdict, and negative results are published.

**No decipherment is claimed here.** A breakthrough would mean a reproducible method that gives coherent, checkable
meaning across many folios and beats the controls.

## Sources
- Images are a primary source: the glyphs belong to no known alphabet, so every transcription is already an
  interpretation. Image-based claims cite folio and image source (Beinecke high-resolution scans).
- Statistics use text transcriptions (ZL, Takahashi, interlinear EVA from [voynich.nu](https://www.voynich.nu/transcr.html)).
  Exact file, version and hash are recorded in each case file.

## Layout
- `case-file/`: one pre-registered case per cycle, results appended underneath
- `journal/`: short cycle notes
- `tools/`: code, re-runnable
- `analysis/`: raw outputs (JSON)
- `data/`: versioned input data with hashes (`data/MANIFEST.md`)

## Coverage table
| Cycle | Approach family | Question | Transcription | Result |
|---|---|---|---|---|
| 1 | Vocabulary vs. page labels (conditional MI, label-permutation null) | Section vs. LFD hand vs. Currier A/B | ZL 3b | Hand and section each carry vocabulary information beyond the other (p = 0.0005, both controls pass). Null leaks at large vocab, audit pending. [C001](case-file/C001-section-vs-hand-vs-currier.md) |

## Not yet covered
Conditional entropy h2, Zipf and word-length profiles, glyph-position rigidity vs. Timm-Schinner generator,
verbose ciphers, abbreviation systems, Rugg tables, Hauer-Kondrak replication on known ciphers, label-to-illustration
links, zodiac month-name cribs, glyph stroke variation from the scans, Takahashi vs. ZL disagreements.
