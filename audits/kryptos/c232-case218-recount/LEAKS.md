# LEAKS — what I knew or saw before my counts were frozen (case 218 recount)

Times MST (America/Dawson_Creek, UTC−7). Clone of kryptos-case-files at 16:36:17; RULE.md written 16:38:21; RULE + script frozen 16:39:12
(`FROZEN_PRE.txt`); one run 16:39:16; counts frozen 16:39:32 (`FROZEN.txt`); freeze pushed as voynich-case-files `4766f7f` (16:39:49);
`analyze232.log` opened 16:39:57, then the case 218 file. `summary232.json`, `gateT/`, the c232 journal, IDEAS/README of a06bfab and
`analyze232.py` were opened later or not at all (analyze232.py: never opened, only its sha256 computed).

1. **Kryptos's own summary (relayed to me before the job):** slope ≈ 0.079 per e-fold, no curvature (b₂ CI crosses 0), nq term −0.0192,
   bar adopted from cycle 233, K4 NO-SIGNAL robust; seeds 209609–209628 calibration, 209629–209640 holdout, 209641 plants, 209642 bootstrap.
2. **Commit subject of a06bfab** (shown by `git log --oneline` right after cloning, before RULE.md): the full bar
   (−6.8417 + 0.0786 ln N + 0.00027 (ln N)² − 0.0192 nq + 0.879), "curvature not detected", holdout 0/12, plants 23/24 (one-error 11/12),
   decade residuals flat, adopted from c233, K4 0 passes NO-SIGNAL (robust, rank p 0.48 / 0.77), cases 215/216/217 relabelled. So I knew
   every headline number before writing my rule.
3. **`git show --stat`** of 51a9a0f and a06bfab: file names and line counts (e.g. the case file title "nc-bar-search-size-fresh-null-calibration",
   analyze232.log 87 lines, summary232.json 822 lines). No content.
4. **`data/cycle232/MANIFEST.txt`** (read as an input description): run time 15:48:03–15:55:13 MST, 430 s, no resume; analyze232.py
   reproduces analyze232.log byte for byte; unfiltered copies on the box at a Kryptos path (not opened).
5. **`plants232.tsv`** (an input) carries the planting script's predicted known / nq / NC per plant (columns `known_pred`, `n_pred`, `nc_pred`),
   so the plant NCs were visible in advance; my code reads the NC from the plant's own `P` line, not from these columns.
6. **Integrity hashing:** my script sha256-checks every file listed in SHA256SUMS, which includes analyze232.log, summary232.json and gateT/
   (bytes hashed, nothing printed but the OK count). I also computed sha256 of `analyze232.py` (matches HASHES232) without opening it.
7. **`ls /workspace`** at the start printed the names of Kryptos's working dirs (k4c*). Names only; none was entered or listed.
8. **My own prior work cited by PREREG232** (bfa4385 / 3046cd3, b8c71f75 / ca9cbdd6, the case 217 recount): I know those numbers because they are mine.

**What this means.** The recount is blind to her *code and outputs*, not to her *headline numbers*. The fit is deterministic OLS with no
tuning knob; the choices that could move it (consecutive groups, domain N ≥ 10, form match for plants, which K4 unit sets N_ref) were fixed in
RULE.md before the run and are the plain reading of PREREG232. Agreement to four decimals is a reproduction of the arithmetic from the same
inputs; it cannot be read as independent evidence that the numbers were not steered, beyond that the rule/script hashes predate the run.
