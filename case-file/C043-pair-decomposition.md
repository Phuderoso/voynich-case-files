# C043 — Expedição 43: decomposição por predecessor do déficit h2

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** F-ENT step 3 (continuation of C041/C042). C041 measured the ~0.70-bit h2 deficit; C042 Look 3 (exploratory) named the rigid predecessors. This cycle gates whether that set concentrates the deficit.

## Question
Is the Voynich h2 deficit vs natural language concentrated in a small set of predecessor glyphs (the rigid pairs C042 Look 3 named), or distributed? Does neutralizing that set close ≥ 50% of the deficit? How does concentration compare to vowelless Latin/Italian?

## Pre-registration (written and pushed before any Voynich, generator, or vowelless number is computed)
- **Data (reuse C041/C042 exactly):**
  - **Voynich:** ZL 3b (`data/ZL3b-n.txt`) and Takahashi IT2a (`data/IT2a-n.txt`). Paragraph words from `c030.ivtff_paragraphs`, folio order. Commas as word spaces; lines with unreadable words dropped.
  - **Generator:**
    - `Generator_base` = published base sample `data/corpora/ts_generated_text.txt`.
    - `Generator_C005matched` = jar run with the C005 matched config (2,400 lines, seed 4343 for this cycle's generation call; if the jar is unavailable, skip and disclose).
  - **Natural texts:** the same 7 as C041/C042: Caesar, Descartes (Latin); Dante, Machiavelli (Italian); Cervantes (Spanish); Genesis, Exodus (Hebrew). Parsers `c003.gutenberg` / `c003.hebrew`.
  - **Vowelless controls:** Caesar and Dante with vowels `aeiou` stripped (`c003.devowel`), then the same metrics.
- **Primary tokenization (identical to C041/C042):**
  - Voynich and generator: **EVA glyph units** via `c003.units` (`cth ckh cph cfh ch sh` each one glyph).
  - Natural / vowelless: letters.
  - **One space token `_` after every word.**
  - First **N = 50,000** symbols (spaces included). Short texts disclosed.
- **Fixed set S (from C042 Look 3; exploratory → confirmatory, disclosed):**
  - S = `{y, i, n, a, d, r, ch, l, q}` (EVA units; `ch` is one unit).
  - This set was named in the same repo on the same day; H2 is confirmatory of that exploration, not an independent discovery.
- **Metrics (log2, bits):**
  - For a stream: H(X_t) and H(X_t | X_{t-1}); contributions `c(a) = P(prev=a) · (H(next) − H(next|a))`; `I = Σ c(a)`.
  - **C5** = (sum of top-5 `c(a)`) / I  (concentration).
  - `contrib(S) = Σ_{a∈S} c(a)`; `f_S = contrib(S) / I`.
  - Analytic ablation: `h2_abl(S) = h2 + contrib(S)` (equivalently: for `a ∈ S` use H(next) instead of H(next|a)).
  - Deficit `D = nat_min_h2 − h2_ZL` (nat_min over the 7 natural h2 at N = 50k).
  - `closed = contrib(S) / D` (only defined when D > 0).
  - For natural / vowelless texts: report C5 and `f_top9` (own top 9 by contribution). Using the same EVA labels for `f_S` on natural is N/A (alphabet mismatch); disclosed.
- **H1 PRIMARY — concentration:**
  - Compute C5 for ZL, IT2a, 7 natural, 2 vowelless, 2 generators.
  - **CONCENTRATED** if ZL C5 > max(7 natural C5) **and** ZL C5 > max(2 vowelless C5), and IT2a replicates (same inequalities).
  - **INSIDE** if ZL C5 ≤ max(natural C5).
  - **VOWELLESS-LIKE** if ZL C5 > max(natural) but ZL C5 ≤ max(vowelless).
  - **SPLIT** if ZL and IT2a disagree.
  - Generators do not decide H1.
- **H2 SECONDARY — deficit localization via fixed S:**
  - **GAP-CLOSED** if `h2_ZL + contrib(S) ≥ nat_min_h2` (closed ≥ 1) **and** IT2a same.
  - **HALF-LOCALIZED** if `0.5 ≤ closed < 1` for ZL and IT2a.
  - **DISTRIBUTED** if closed < 0.5.
  - **SPLIT** if ZL/IT2a disagree on bucket.
  - Also report `f_S` for ZL/IT2a and `f_top9` for each natural/vowelless (own top 9) for context; descriptive only.
- **Gates (40 replicates on Latin Caesar windows of 50k, BEFORE any Voynich number):**
  - **FPR (Look concentration):** within-word shuffle; call "false concentrated" if shuffled C5 > C5 of the unshuffled Caesar window itself. Need ≤ 4/40.
  - **Power:** `plant_copy` (c041, p = 0.6) should raise C5 above the unshuffled Caesar C5 in ≥ 32/40.
  - If either gate fails → H1 **NOT TESTABLE**.
  - For H2: no separate gate beyond the C041/C042 FPR/power already established for h2; optional size check: shuffle must not put closed ≥ 0.5 vs nat_min when applied to Caesar vs the 7 naturals' min in ≤ 4/40 if cheap; else disclose skip. Prefer keeping gates focused on C5 so runtime stays under ~8 min.
- **Leave-one-out descriptive:** is any natural C5 above all other six?
- **Seed:** 4343 (new for C043).
- **Caveats fixed in advance:**
  - Low h2 / high concentration = writing-system order, not meaning.
  - S was named in C042 Look 3 (same repo, same day) — confirmatory of that exploration, not independent discovery.
  - Alphabet differences: S glyphs may be rare/absent in natural; `f_S` on natural using same labels is N/A — use `f_top9` instead.
  - Helpers imported from `tools/c041_conditional_entropy.py` and `c003` / `c030`.
- **Code:** `tools/c043_pair_decomposition.py`, seed 4343, run with `timeout 600`. Output: `analysis/C043_results.json`. Budget ~8 min with checkpoints.

**Status:** pre-registered (this commit) before any Voynich / generator / vowelless run; results below after the run.

## Results
*(placeholder — filled after the gated run)*

## What this means
*(placeholder)*

## Next
*(placeholder)*

**Code and numbers.** `tools/c043_pair_decomposition.py`, `analysis/C043_results.json`. Seed 4343.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
