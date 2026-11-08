# C058 — Expedição 58: vizinhos de uma letra (new family F-NEIGH)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Why:** a hallmark of the self-citation account (Timm & Schinner) is that a word is often a lightly changed copy of a word written just before it. Many observers note that Voynich words often differ from a neighbour by one glyph. C055–C057 showed that whole word types clump at the scale of ~115-token chunks; this cycle asks a different, shorter-range question: beyond that chunk-scale clumping, are tokens unusually often *one glyph away* from a token just written? New approach family (rule: one in three cycles; C056–C057 continued F-BURST).

## Step A — plant design (design seed 5858; run and published before any C058 test number)
- **Statistic S:** share of focal tokens (≥ 3 units) with at least one token at edit distance **exactly 1** (one unit substituted, inserted or deleted; identical tokens do not count) among the **10 preceding tokens**. Units: EVA glyph units (`tools/c003_position_rigidity.units`) for Voynich and generator, letters for natural text.
- **Null:** tokens shuffled only inside 115-token chunks, 100 shuffles; **D = S − mean null S**, p by rank (floor 1/101). This keeps chunk-scale clumping (C055–C057) and destroys only short-range order.
- **Plant (copy-with-mutation):** in a shuffled natural half, a share Q of tokens is replaced by a one-unit substitution of a token 1–5 places earlier.
- **Choice rule (in the tool before it ran):** smallest Q with design power ≥ 36/40.

| Q | design power | planted D median |
|---|---|---|
| **0.01 (chosen)** | **39/40** | **0.0079** |
| 0.02 | 40/40 | 0.0158 |
| 0.03 | 40/40 | 0.0222 |
| 0.05 | 40/40 | 0.0379 |

## Step B — pre-registration (pushed before any C058 test number)
- **Data:** ZL 3b and IT2a (`data/ZL3b-n.txt`, `data/IT2a-n.txt`, hashes in `data/MANIFEST.md`), first two disjoint 15,000-token halves in reading order; controls as C055–C057 (9 natural + 3 devowelled, one half for texts under 30k tokens); Timm–Schinner generator default settings, seeds 551–557 (texts under 30,000 tokens dropped; ≥ 6 halves needed).
- **Gates (fresh seed 5859):** 40 replicates. FPR — globally shuffled natural halves, p < 0.05 at most 4/40. Power — plant at Q = 0.01, p < 0.05 at least 32/40. Failing → all NOT TESTABLE.
- **H1:** EXCESS if all four Voynich halves have p < 0.0125; NO EXCESS if none; SPLIT otherwise.
- **H2 / H3:** D of the four Voynich halves against the natural / generator D ranges: ABOVE, BELOW, INSIDE, STRADDLE.
- **Reading rules fixed in advance:** EXCESS means nearby tokens are one glyph apart more often than chunk-level vocabulary explains, consistent with (not proof of) copy-and-modify writing; natural inflection (Latin *-us/-um*, Italian *-o/-a*) can also produce it, which is why H2 is needed. ABOVE natural plus INSIDE/ABOVE generator would favour the self-citation account on this statistic; INSIDE natural would mean the statistic does not separate the accounts. No reading or meaning is implied by any outcome.
- **Tool:** `tools/c058_edit_neighbours.py test` → `analysis/C058_results.json`; `timeout 600`.

## Results
*(to be filled after the run)*

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
