# COMPARISON (written after freezing; her files opened 2026-11-21 ~04:53 MST)

Opened only after `FROZEN.txt` and `SHA256SUMS` existed: `data/cycle229/summary229.json` (sha256 `3fb84701…`) and `analyze229.log` (`6c49bed8…`), both at her commit `01e8230`, both verified against her `data/cycle229/SHA256SUMS`. Not opened at all: `plants229.tsv`, `gateT/`, `kb229.c`, `analyze229.py`.

## Counts: exact agreement
- `postcompare.py` / `postcompare.out`: her `null_by_nq` (63 bins) and `k4_by_nq` (60 bins) vs my `counts_by_nq.tsv`: **0 differences** in (decrypts, passes, max NC to 3 decimals). My table has one more bin (nq 63, tiny N) that hers omits. nq > 40: 20,406,218 decrypts, 0 passes, max −6.355 in both.
- Bar-eligible nulls (floor nq ≥ 10): her 8 hits / 4 distinct texts / 4 of 16 nulls (209560, 209563, 209568, 209573), best −5.945 (null209573, all_V_b, p24, nq 13) vs my 8 hits / 4 Y cells / 4 nulls at nq 12, 13, 13, 19, best −5.945. Same. None at nq 10–11. (Y lines carry no texts, so I counted nulls, not texts; her 8 hits over 4 texts = my 8 hits over 4 cells, one direction pair each.) K4: 0 passes, K4 best −6.095 at nq 9, −6.210 at nq ≥ 10; null best at nq ≥ 10 is −5.945.
- The 10 extra pass cells at nq 4–8 (20 hits, N from 6 to 1,615) are in her table too (pass columns 6, 4, 4, 2, 4 at nq 4–8). They sit under the floor n ≥ 10, so they are not bar passes; do not mix them into "passes".

## Model question (hers: "null max near −6.0 tracks search size"): where I land
Her log contains no regression of max NC on log N; the model comparison below is mine only.
- Marginal: max NC vs nq is strong (ρ −0.83, R² 0.647); vs ln N_bin alone it is weak and *negative* (ρ −0.54, R² 0.098) because N_bin grows with nq (corr 0.66). So "the max grows with log N" is not true marginally.
- Partial: at fixed nq, ln N adds a small positive effect (+0.056 per e-fold of N, t 4.3; Freedman–Lane p 0.0001–0.0004); at fixed N, nq is far stronger (−0.024 per quadgram, t −11.7). M3 (both) has the lowest AICc (−183.4 vs −168.8 for nq only, −111.5 for ln N only). RULE verdict, primary: **BOTH**.
- Robustness: restricted to bins with N ≥ 100 or ≥ 1000 the ln N term disappears (partial p 0.97 / 0.15) and the extreme-value form sqrt(2 ln N)/sqrt(nq) fits best (R² 0.86 / 0.83): **NQ-DOMINATES**. Restricted to nq ≥ 10 (added after the first run, labelled so) the primary pattern returns: M3 R² 0.883, ln N +0.0625 (t 6.9), nq −0.0224 (t −19.4), partial Spearman for ln N p 0.10.
- Why the max looks flat near −6.0 for nq 10–25: along the observed ridge N grows ~27× (3.7k → 98.5k, +3.3 in ln N) while nq grows 2.5×; the nq term (−0.34) and the ln N term (+0.21) nearly cancel, so the bin max drifts only −5.95 … −6.34. A flat bar is not "tracking" either variable cleanly; it sits where two opposing effects balance.
- Reading for I-342 / cycle 232: the null max is a function of nq first and N second, and the nulls that cross −6.0 live at nq 12–19 only (none at nq 20–40, whose bin maxima are −6.05 … −6.67, and none at nq > 40, max −6.355). A bar that depends on nq (and optionally log N) is supported; "bigger search ⇒ higher null max" alone is not. I do not propose a bar. Caveat: a bin max is a noisy single draw from 16 nulls (e.g. −5.945 at nq 13 vs −6.335 at nq 24), and the pass cells at nq 12–19 are 4 draws.
- Not a decipherment; K4 has no pass.
