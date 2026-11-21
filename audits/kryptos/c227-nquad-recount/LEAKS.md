# LEAKS — what I knew before counting (disclosed in full)

Written 2026-11-20 before FROZEN.txt and before opening `summary227.json` or any cycle 227
analysis script (`summarize227.py`, `kb227.c`, `gate227.py`, `plant227.py`, `run227.sh`).

1. **Kryptos's request quoted her expected headline before I counted:** her only null pass is
   null 209425, Q all.bin p24, line 78680, NC −5.29 with exactly 10 scorable quadgrams. She also
   asked whether a floor of 20 scorable quadgrams would cost any of the 16 planted cases in
   `gateP227.tsv`.

2. **The cycle 227 commit message** (`c2af592`, 2026-11-20 20:03:14 −0700, read when I confirmed
   that `data/cycle227` was published) already stated: plants 20/20, NC 16/16; K4 0 of 14.25 M
   decrypts (best −6.21); "one null test at the 10-quadgram floor (−5.29)".

3. **`MANIFEST.txt`** (an input I was allowed to read) says Gate P found 20/20 and that
   `summary227.json` holds every cell's NC best / passes / labels. I did not open that JSON
   before freezing.

4. **Format inspection of allowed inputs, before the recount ran, already showed her printed
   values on `P` lines and in `gateP227.tsv`:**
   - four `P` lines in `R/null209425_allVQ_a_r10.txt`, all `perm=78680`, `nqnc=10`, `nc=-5.292`,
     same 97-letter `pt`;
   - `gateP227.tsv` already carries her `nqnc` and `nc` for the 16 V/Q plants (including plant 13
     with `nqnc=11`). I do **not** copy those fields into the frozen counts; I recompute `n` and
     NC from `pt=` and `qg.bin`. Seeing plant 13's printed `nqnc=11` before counting means I
     already expected that a floor of 20 might cost at least that plant.

5. **`X` histogram lines** (allowed input) were sampled for format only: they are
   `X hit model=… p=… kbin=… n=…` followed by `bin:count` pairs (values such as 77, 82, …),
   i.e. the cycle 226-style oracle / k-bin histograms, **not** a table of NC against scorable
   quadgram count. I did not use them to form the frozen per-n table. After the freeze I will
   say whether anything in them bears on the n-dependence question.

6. I reused only my own scoring convention from `/workspace/k212-nc-recount/nc_recount.py` and
   the `qg.bin` already hashed there (4a02ba4e…). I did not read `kb227.c` or `summarize227.py`
   for how she decrypts or scores. The `pt=` strings are her published decrypts; I score them,
   I do not re-decrypt.

7. Everything in my case 209 / 212 NC recount (including the house rule that a tied residue
   class reads '?') is already known. Cycle 227 pre-registered that same rule and the NC ≥ −6.0
   bar (PREREG227, which I read).
