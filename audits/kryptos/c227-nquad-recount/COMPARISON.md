# COMPARISON — cycle 227 n-quad NC recount vs Kryptos's published numbers

Opened after FROZEN.txt (22:01:28 MST). `summary227.json` fetched 22:01:55 MST
from `Phuderoso/kryptos-case-files` @ `c2af592`, sha256 `6262db7a…` (matches her
`data/cycle227/SHA256SUMS`). I also compared the `nqnc` / `nc` fields already
visible on `P` lines and in `gateP227.tsv`, and I re-read the `X` histogram lines.

Frozen counts were not changed.

## Headline agreement
- **The only house-bar pass** is null 209425, Q, all.bin (r10 file), p=24, `perm=78680`,
  n=10, known=77, NC **−5.2916** (she prints **−5.292** / “−5.29”). Same plaintext on
  four `(X,Y,form)` variants (1/6/2, 5/6/2, 16/6/0, 16/6/1).
- Her `summary227.json` cell `(Q, geo=a, scope=all, p=24)` has `null_ncmax=-5.292` and
  `null_ncpass=4`. That matches my **unique-hit** count (4), not the collapse to one
  `(null, perm, model, p, pt)` row. In her request and commit message she also called
  it “one null test / only null pass” (the line / cell). Both descriptions are true
  under the two groupings I froze.
- **K4 NC passes in that JSON: 0.** I did not independently recount K4 (not asked);
  I record her figure only.
- **Gate P, 16 V/Q plants:** my `n`, `known` and NC agree with her printed `nqnc` /
  `known` / `nc` for all 16 (NC within 5×10⁻⁴; she reports 3 decimals). All 16 pass
  the published bar. A floor of 20 scorable quadgrams would **lose only plant 13**
  (Q, p=17, n=11, NC −3.8307; she prints nqnc=11, nc=−3.831). The next-smallest
  plant `n` is 26. The four G plants have no `pt` / known < 49, same as her table.

## No discrepancy in the scoring rule
Re-scoring her published `pt=` strings with my own `qg.bin` (sha 4a02ba4e…) and the
house NC rule (no '?', no crib letter, mean log10, floor already in the table)
reproduces her `nc` / `nqnc`. I did not need to open `summarize227.py` or `kb227.c`.

## What she did not publish (the actual question)
`summary227.json` has no per-`n` table of null max / q95 / pass counts. The `X`
lines in `data/cycle227/R/` are **not** NC-versus-scorable-quadgram histograms:
they are paired `X hit` / `X oracle` records of the form
`X hit model=… p=… kbin=… n=…` followed by `bin:count` (bins such as 0, 77, 80, …),
i.e. the cycle 226-style oracle / k-bin histograms (2,762 `X` lines, half `hit`,
half `oracle`). They do not answer how the null maximum NC depends on n. The
per-n table is therefore new work, from the `B`/`C` decrypts (`P` lines excluded
as duplicates). See `counts_by_n.tsv` and `FROZEN.txt`.

## Should the bar be a function of n?
Empirically, max_NC(n) and q95(n) are **not** monotone, and a fit
`q95(n) ≈ a + b/√n` is weak (R²=0.256). The flat bar NC ≥ −6.0 sits well above
q95 at every n. The **only** breach is the n=10 cluster at −5.2916, and 3 of
those 10 windows are the table floor (−8.469). For every n ≥ 11, the null max
is already below −6.0. Raising the scorable-quadgram floor from 10 to 20 would
remove that one null pass and cost one of the 16 plants (plant 13, n=11). I do
not adopt a new bar here; I report the dependence.

compared_at: 2026-11-20 22:02 MST (America/Dawson_Creek)
