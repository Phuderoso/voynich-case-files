# LEAKS — case 221 blind recount (cycle 235)

Declared at freeze, 2026-11-23 04:32 PT, before computing anything.

- **PREREG235.md read in full** (it is the rule; that is by design).
- **Her c235 commit message headline was seen** before this audit: 24 nulls, 0 per-text passes, A 0/12, B 0/12, Wilson 0–0.14,
  bar HOLDS; null R_t 0.24 below the case 218 calibration, HL CI 0.16–0.32, MW p 1.1e-6; plants 20/20; K4 343 decrypts, 0 passes, rank p 0.64.
  So this recount is *not blind to her headline numbers*; it is blind to her code and intermediate files.
- **Not opened before freeze + run:** data/cycle235/summary235.json, analyze235.log, nulls235.tsv, gateT.txt, plants235.tsv, MANIFEST.txt,
  tools/cycle235/analyze235.py, check235.py, mknull235.py, plant235.py, case file 221, her c235 journal.
- **Opened (allowed, not results of c235):** data/cycle232/summary232.json (calibration R_t, fit beta, k_text), PREREG232.md (grep for the
  R_t / bar definition), data/cycle235/SHA256SUMS (hash check of R files), data/k4.txt, the 76 files in data/cycle235/R
  (their Y/T lines print per-file n and max — inputs, read by the script).
- The per-file H-line counts of 8 files were printed once by a shell `grep -c` while inspecting the format (K4: 180/74/89 → 343 total, which
  matches the leaked headline before any script ran).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
