# RULE — how I compute NC vs n (scorable quadgrams) for cycle 227 nulls and Gate P plants

Voynich desk, 2026-11-20 (America/Dawson_Creek, MST). Written and hashed **before** the recount ran
and **before** I opened `summary227.json`, `tools/cycle227/summarize227.py`, `kb227.c`, or any other
cycle 227 analysis script. Not fully blind: see LEAKS.md.

## Inputs (fixed)
- Fresh sparse clone of `Phuderoso/kryptos-case-files` @ `c2af592906d5fb20272ac60d15995e32c5c06b58`
  (origin/main), in `/workspace/k227-nquad-recount/kryptos-main`. Paths used: `tools/cycle227/PREREG227.md`
  and `data/cycle227/` **except** `summary227.json` (not checked out). I do not use `/workspace/k4c216/repo`.
- Quadgram table: `qg.bin` sha256 `4a02ba4eca0b6840a3a5eafe00678e854b25703c36b99e9e26a7697d4ed89f69`
  (the hash declared in PREREG227 / PREREG223; float32, 26^4 entries, index `((a*26+b)*676 + c*26 + d)`,
  A=0..Z=25; values are log10 scores; unseen quadgrams already carry the table's floor, −8.469008,
  393,428 entries). **I use the table value as is, no extra floor, no smoothing.** log base 10.
- Null decrypts: every `B ` and `C ` line with a `pt=` field in `data/cycle227/R/null*.txt`.
  `P ` lines are the same hits already printed as `B`/`C` (plus her `nc` / `nqnc` fields); I do not
  add them as extra rows. I do not use her `qg=`, `nc=`, `nqnc=` or `known=` fields for the official
  counts — only the 97-letter `pt=` string.
- Plants: the 20 rows of `data/cycle227/gateP227.tsv`. The 16 V/Q rows have a 97-letter `pt=`;
  the 4 G rows have `pt=-` and `known=<49` and are not NC-scorable. I recompute `n` and NC from `pt=`.
- Cribs, 1-indexed **22–34** (EASTNORTHEAST) and **64–74** (BERLINCLOCK), i.e. 0-indexed 21–33 and 63–73,
  the same seats in every text.

## NC (same convention as my case 212 RULE, now the house rule)
- Quadgram windows start at 0-indexed i = 0..93 (94 windows). A window is used iff it contains **no '?'**
  AND **none of its four letters sits on a crib position** (windows that merely touch a crib are out).
  That leaves at most 64 windows (starts 0–17, 34–59, 74–93).
- `n` = number of used windows (scorable non-crib quadgrams).
- `NC` = arithmetic mean of `qg[window]` over the used windows. If `n = 0`, NC is NA.
- `known` = 97 minus the number of '?' in `pt` (crib letters count toward known when they are not '?').
- **PASS iff NC ≥ −6.0 AND known ≥ 49 AND n ≥ 10.** If n < 10, the hit cannot pass.

## What is a "null row"
- A **hit** is one unique `B`/`C` line, keyed by (source file, line body with the leading `B`/`C`
  stripped and any `nqnc`/`nc` fields removed). A hit printed as both `B` and `C` counts once.
- The per-`n` table is over these unique null hits with `n ≥ 1` (NC defined). I also print the
  `known ≥ 49` subset, because only those can pass the house bar.
- I do not collapse different `(perm, dir, ix, layout or X/Y/form)` configurations that happen to
  share a plaintext: they are distinct hits. A sensitivity unique-on-`(null, perm, model, p, pt)`
  is reported in the summary, not used as the primary table.

## Per-n summaries (nulls)
For each n = 1..64: number of unique null hits, maximum NC, the 5% upper quantile = the **95th
percentile** of NC among those hits (`numpy.quantile(..., 0.95, method='linear')`, Hyndman–Fan type 7),
and the number of hits that **PASS** the house bar (so 0 automatically when n < 10).
I then say whether the upper tail (max and q95) is monotone in n, and whether a simple
`a + b/sqrt(n)` least-squares fit to q95(n) (for n with at least 5 hits) describes it better than a
flat bar at −6.0.

## Floor 20 on the 16 plants
For each of the 16 V/Q plants: my `n`, my NC, my `known`, whether it passes the published bar
(n ≥ 10), and whether it would be lost under a floor of 20 scorable quadgrams (n < 20, or it
already fails the other clauses).

## Outputs
`counts_by_n.tsv`, `plants_floor20.tsv`, `summary_nquad.txt`, then `FROZEN.txt` with hashes and
the MST timestamp. Comparison with her published numbers is **not** part of the freeze.
