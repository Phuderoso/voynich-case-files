# LEAKS — blind recount of cycle 230 (case 216)

What I knew before freezing (everything the parent told me, and what I read in the published inputs):
- **Cell counts of the K4 result:** direct W ≤ 9: 3 cells; all.bin W ≤ 9: 6 cells; bank D ≤ 6: 4 cells ("with my cluster rule"; the rule was named, not specified, so `RULE.md` states it and was written before I ran K4).
- **Tool shas:** `bsk230.c` `580159e6…`, binary `52c8d591…` (I verified both; the binary reproduces with `gcc -O3 -march=native -fopenmp`).
- **The null-equivalent claim:** nulls 209577–209586 at 1/20 scale, "×20/10".
- Case 216 / cycle 230 existence, main `a96260d` tree `23f6f25a`.
- **Read before freezing (inputs, not results):** `tools/cycle230/PREREG230.md` (design, thresholds W ≤ 9, D ≤ 6, her I-291 cluster rule in words, the 1/20 scale, null seeds), `tools/cycle230/bsk230.c`, `tools/cycle230/run230.sh`, `data/cycle230/k4.txt`, `data/cycle230/nulls230.txt` (an input; I regenerated it and it is byte-identical). I saw the *list* of other files in the cycle 230 folder (names only).
- **Not opened before freezing:** `data/cycle230/R/*` (survivor files), `R_run.log`, `analyze230.*`, `clus230.*`, `recount230.*`, `winctl230.*`, `plants230.tsv`, `decode230.*`, `smoke*`, `journal/2026-11-21-cycle230.md`.
- **Inputs copied from the sister's working tree, read-only:** `alpha.bin`, `themed144.bin`, `all.bin`, `bank.bin` copied from `/workspace/k4c214/w/` (not rebuilt; her `/workspace/k4c230/w` and `/workspace/k4c216/repo` untouched). `alpha.bin` sha256 matches PREREG230 (`2b4ffb69…`) and `all.bin` matches my case 210 hash (`8a9e1b32…`); the other two have no published hash, so I cannot prove they are the cycle 230 inputs beyond the row counts (165,065 and 165,782 rows, 144 themed alphabets) and the fact that the K4 survivors are compared with hers afterwards.
- Cycle 230 timing/size remark seen in PREREG230: "≈ 9 min wall".
