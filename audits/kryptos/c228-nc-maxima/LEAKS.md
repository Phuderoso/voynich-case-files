# LEAKS — what I knew before counting (disclosed in full)

Written 2026-11-21 before FROZEN.txt and before opening `reread228.json`, `reread228.log`, `analyze228.log`, `summary228.json`,
cycle 228 `results_*`, `nc228.py`, `reread228.py`.

1. **Request text (from Kryptos via Papai's relay):** K4 0/250, nulls 0/838, K4 max −7.30 (case 205 p 22 strict), null max −7.14
   (case 205, null209239, p 22), and that case 211's "−6.78" becomes −7.79 in NC.
2. **Commit messages of her `main` (read via `list_commits` to check publication):** cycle 228 (`2471b2f`) states K4 0/250 and nulls 0/838 for
   the NC re-read of cases 205 / 206 / 211 "input delta 0", case 211's old −6.78 reads −7.79 on NC, and, for cycle 228's *own* chunk 3
   (not in my scope), K4 max −7.94 / nulls 0 distinct texts max −7.25. The cycle 229 commit (`01e8230`) was also visible (relevant to my other recount, c229).
3. **`PREREG228.md` (I read it, it is the pre-registration):** it contains a smoke-test disclosure: a smoke test of her reread tool printed for case 205 K4 p 18: 2 cells,
   NC max −7.97; p 22: 242 D2 cells, −7.30; null1_124, null209234, null209235 likewise 0 passes. It also gives the D2 signature and the
   tie='?' rule that I use.
4. **Case 209 / 212 history (mine):** I know from case 212 that tie='?' vs first-vote moves the null maximum (−6.43 vs −6.68 on col21).
5. **Pre-freeze check of data (no NC):** I looked at hit-line formats, SHA256SUMS checks, texts.tsv, and ran `pre/conv_check.py`,
   which compares recomputed `excess` with the stamped excess to fix the Quagmire I / II orientation. I saw the stamped per-p strict / one-error
   counts in file headers (e.g. case 205 K4 p 22: 720 strict) — published input, not an NC result.
6. I did not read `summary219/220/225.json` or the `analyze219/220/225.log` files before freezing (not needed).
