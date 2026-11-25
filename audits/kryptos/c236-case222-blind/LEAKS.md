# LEAKS — what I saw before this freeze (case 222 blind audit)

The audit is blind on her **code outputs and checker**, but **not blind on her headline**. Disclosed in full:

1. **PREREG236.md** text (allowed input), plus `keys236.py`, `mknull236.py`, `plant236.py`, `runA.sh`, `runP.sh`, `HASHES236.txt`, `gn217.c` (allowed inputs).
2. **File listing of `data/cycle236`** (names only, seen in an earlier session: summaryP.txt, nulls236.tsv, plants236.tsv, time.txt, R/ with `R/k4_*` and `R/null209673_*` names, P/). No content opened.
3. **Her commit messages**, printed by `git log` in my read clone while orienting this cycle:
   - 9ed3d33 (cycle 236 itself): *"K4 0 hits in direct / bank / all.bin -> EXACT-EXCL within the list; plants 20/20 (209672, one-error 10/10, NC margin >= +2.07); 6 fresh nulls (209673-209678) 0."* — **so I knew her headline result before running.**
   - 20f9948 / 6f61ec1 (cycle 237): includes *"I-376 first pass on the case 222 list: K4 best agreement 13/24 vs 20 nulls 12-14 (rank p 1.00 / 0.86) NO-SIGNAL"*.
   - 2fe149d / 6cf976c (cycle 240), 3c562db / 07c9b7b (cycle 239), 6cd742e (cycle 238) headlines (no case-222 numbers beyond the above).
4. **Paths only** (from a `find` for input files): `/workspace/k4c236/w/themed144.bin`, `/workspace/k4c236/w/keys234.bin` — her cycle-236 working directory exists on the box; I did not list or open it and took no input from it.
5. `git grep -l` of input sha prefixes returned file names only (her journal 2026-11-21-cycle231.md, PREREG207/208/214/216/217), used to confirm my input shas are the ones she cites.

Not opened before the freeze: `check236.py`, `journal/2026-11-22-cycle236.md`, anything under `data/cycle236/`, anything under `/workspace/k4c236/`.

Consequence: what this audit can still establish independently is the **counts themselves** (my own engine build, my own runs, my own decrypt/recount checker) and **byte equality** of the raw outputs. It cannot claim the expected outcome was unknown to me.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
