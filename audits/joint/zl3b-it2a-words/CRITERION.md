# Alignment criterion v2 — ZL3b vs IT2a word division (frozen with the code; no real count existed when this was written)

Status: **v2, amended with Kryptos's amendments a–h (her message of 2026-11-21 09:09 MST, `C124/KRYPTOS_REVIEW2_2026-11-21.md`, sha256 `3437572d…`)**. v1 was commit `94cb5d1` (`CRITERION.md` sha256 `7259ace5d71c5c50821dd70f31820447ad5ed1da860f5463c809be28f63a43ad`). v2 was written 2026-11-21 (America/Dawson_Creek, MST) after the planted control (§9) and before any real count; `FROZEN.txt` carries the time and hashes. Inputs: `HASHES.txt`. Code: `tools/joint_words_zl3b_it2a.py`.

## 0. Why it matters
Every statistic in C120–C124 uses unit streams in which the word end `_` is a symbol, so the word division of a transcription is part of the instrument. ZL3b and IT2a are two independent readings of the same pages; how often they divide the same glyph string differently, and how often they read different glyphs, is a measurement-reliability quantity for the whole F-MID chain. This audit measures it; it does not say which reading is right. **Descriptive only: no hypothesis test, no label, no ranking of the transcriptions.**

## 1. Line normalisation (C070 / C123 retention kept as a separate flag)
1. Locus line regex `^<(f\w+)\.(\d+),([@+=*&~/!-])(\w+)>\s*(.*)$` (v1 lacked `/` and `!`: two loci, `<fRos.110,/L0>` in ZL3b and `<f89v2.26,!Lf>` in IT2a, did not parse; now they do and they stay unpaired unless key or fallback pairs them). Key = (folio, line number, first letter of the locus code: `P`, `L`, `R`, `C`). No duplicate keys exist in either file. Lines that do not match are listed.
2. Text layer: `<->` → **definite separator** in both files (amendment c; sensitivity: removed, glued); other `<…>` markup removed; `@NNN;` removed; `[a:b]` → `a` (sensitivity: `b`); `{`, `}`, `'` removed. **No lowercasing (amendment a):** the only upper-case glyph in either file's locus lines is one `I` in ZL3b, kept as its own glyph. `.` = definite space, `,` = uncertain space (amendment d; sensitivity: `,` removed, no separator), whitespace = `.`; a run of separators collapses to `.` unless it is only commas. `?` is an ordinary glyph (equal only to `?`; sensitivity a2: `?` matches any single glyph, substitution cost 0).
3. Line glyph string G = concatenation of the tokens. Empty lines are kept (both empty → identical).
4. **Retention flag** (C070 rule on the first reading, independent of the sensitivities): no `<->`, ≥ 5 tokens, every token `[a-z]+`. Reported per transcription.

## 1b. Alphabets (amendment a)
ZL3b is `Eva-`, IT2a is `EvaT`. No documented glyph-by-glyph map between them is available to me, so I do not invent one. What the files show, before any alignment: glyphs present in the locus lines of ZL3b and absent from IT2a: `b` (15), `j` (14), `u` (9), `I` (1); present in both with different counts: `g` (154 vs 96), `x` (41 vs 35), `v` (15 vs 9), `z` (9 vs 2), `?` (209 vs 254). **Base: no map (identity).** Sensitivity **a (rare-glyph collapse)**: every glyph outside the 18 core letters `acdefhiklmnopqrsty` and `?` is mapped to `#` in both files. Sensitivity **a2**: `?` is a wildcard. Both are reported next to the base.

## 2. Level A — pairing of loci (amendment b)
1. Stage 1: pair by key. **Key match rate** = (key pairs)/(loci of each file), reported before and after the release in step 2.
2. A key pair whose lines fail the line threshold of §3 (Lev > ⅓ max length; a line-number shift shows up exactly like this) is **released** to the pool (sensitivity: no release, no fallback).
3. Fallback: inside each folio, the unpaired lines of ZL3b and of IT2a (those never key-paired plus the released ones) are aligned by an order-preserving DP over the two lists: a pair is allowed only if the locus letters are equal and the line passes the §3 line threshold; maximise the number of pairs, then minimise the sum of Levenshtein distances, ties: pair first, then skip a ZL3b line, then skip an IT2a line.
4. Whatever remains is **only in ZL3b** / **only in IT2a** (unalignable at line level). Reported for: all loci; `P`; P retained in both; P retained in exactly one; Currier A / B (header `$L` of each file, `pages_of` rule); the CB stratum of ZL3b (retained lines of Currier-B pages of ZL3b) and the CB stratum of IT2a.

## 3. Level B — paired lines
With Lev = Levenshtein distance on G strings (unit costs) and line threshold τ_L = ⅓ (sensitivities ¼, ½):
- **identical**: token lists equal;
- **division_only** (split/merge-only): G_a = G_b, token lists differ;
- **glyph_different**: G_a ≠ G_b and Lev ≤ τ_L·max(|G_a|, |G_b|);
- **unalignable_line**: Lev > τ_L·max(|G_a|, |G_b|) (reported, not dropped; excluded from level C).

## 4. Level C — tokens in identical, division-only and glyph-different lines
Groups: moves (i tokens of ZL3b : j tokens of IT2a), (i, j) in the order **(1,1), (1,2), (2,1), (1,3), (3,1), (2,2), (1,0), (0,1)**. Cost of a group = Lev(concatenations); a gap move costs the token length. Minimise total cost. **Tie-break (amendment f):** among optimal alignments, more (1,1) moves, then fewer gap moves, then the **lexicographically smallest move sequence** with the list above as the alphabet order (implemented as a suffix-optimal DP and a forward pass that always takes the lowest-index optimal move). Groups are classed with token threshold τ_T = ½ (sensitivities ⅓, ⅔):
- **identical**: (1,1), equal strings;
- **split_merge**: cost 0 but not (1,1)-equal: concatenations equal, the only difference is a space or comma. Direction: ZL3b token divided in IT2a (i < j), ZL3b tokens merged in IT2a (i > j), or shift (2,2). Recorded: separator type on the dividing side, boundary glyph pair (last | first);
- **glyph_different**: cost > 0 and ≤ τ_T·max(length of the two concatenations); equal-length substitution pairs are tallied;
- **unalignable**: gap moves, or cost > τ_T·max. (A one-glyph token against a different one-glyph token has cost 1 > ½: unalignable. v1's toy `x` vs `y` was wrong on this; corrected in §10.)

## 5. (h) `_` symbols of the unit stream (amendment h)
For C120–C124 every word ends with a symbol `_`. For each transcription T separately, take its CB stratum as C123/C124 build it (retained lines, Currier-B pages, 4-line blocks from offset 0, remainder tail) and count the `_` symbols (one per token, incl. the line-final one). A `_` is **same** if its line is paired (not unalignable) and the other transcription has a token end at the same column of the glyph alignment of the two lines (identity alignment when G is equal; otherwise Levenshtein traceback preferring diagonal, then a gap in ZL3b, then a gap in IT2a), and **differ** if the line is paired and it has not. `_` in lines without a counterpart (unpaired or unalignable) are counted separately and never added to *differ*. The headline is **differ / (same + differ)** with a Wilson 95 % interval, for (i) all `_`, (ii) non-final `_` only, (iii) only lines with G equal in both (pure division), and split by position class of the line in its own CB geometry: **first line of a block**, **last line of a block**, **interior** (lines 2–3 of a block), **tail**. "First/last vs interior" is the comparison asked for; there is no test.

## 6. What is reported
Counts and shares, every share with its denominator and Wilson 95 % interval: Level A key and fallback rates; Level B by stratum; Level C by stratum with split vs merge direction, `.` vs `,` share on dividing sides, top glyph substitutions and top boundary pairs; separator-type cross-table at group boundaries; retention disagreement and words-per-line differences; the (h) table. Sensitivities are one at a time against the base: a, a2, b (no release / no fallback), c, d, e (line ¼, ½; token ⅓, ⅔), `[a:b]` second reading.

## 7. Order of work (as done)
1. v1 proposal; Kryptos amendments a–h (this v2).
2. Code `tools/joint_words_zl3b_it2a.py` written; toy lines of §10 checked by hand.
3. **Planted control (g), seed 11848, run before any real count:** a copy of ZL3b is damaged at registered rates, aligned against the original, and the recovery is compared with the truth (§9). Result in `control/`.
4. Freeze (`FROZEN.txt`: criterion sha, code sha, seed, control result sha, input hashes, MST time, SHA256SUMS).
5. Real count with all sensitivities; publication; Kryptos may blind-recount from this text with her own code.

## 8. Not done / limits
No claim about which transcription is right; no claim that a split/merge is an error of either; the rare-glyph collapse is not an Eva–EvaT conversion; the alignment is one deterministic choice among ties (rule §4).

## 9. Planted control (g)
Source: the ZL3b text layer of every locus line. Per original token, left to right, at registered rates: merge with the next token 0.04, split at a random interior point 0.04 (token length ≥ 2), replace one glyph by another glyph of {acdefhiklmnopqrsty, g, x, v, z} 0.03 (token length ≥ 3); per line: damage 70 % of the glyphs with probability 0.02 (**expected to be unpaired**), delete the line and renumber the later lines of its folio with probability 0.02; all separators written as `.`. Events sit on disjoint tokens. Seed 11848. Passed if (1) among non-garbled, non-deleted lines the share paired with the correct partner is ≥ 0.99, (2) for merges, splits and one-glyph swaps the planted rate lies inside the Wilson 95 % interval of the recovered rate, (3) the (h) differ counts on the ZL3b side (= planted merges) and the IT2a side (= planted splits) have the planted rate inside their Wilson interval. The first run of the code printed FAIL because the metric (1) counted the deliberately garbled lines as pairs to find; I fixed the metric (garbled lines are listed separately, expected unpaired) and re-ran with the same seed; both outputs are described in `control/CONTROL_LOG.md`.

## 10. Toy examples (hand-made, not from the files; run by hand with the code)
- `daiin.ol` vs `daiin.ol` → identical. `qokeedy.chedy` vs `qokeedy,chedy` → identical (separator type differs: tallied in the cross-table, not a class).
- `ol.chedy` vs `olchedy` → division_only, one split_merge group (2:1). `ol.chedy.x` vs `olchedy.y` → one split_merge group and one **unalignable** group (single-glyph tokens `x`, `y`; v1 wrongly said glyph-different).
- `sheedy` vs `cheedy` → glyph_different (1:1, cost 1 ≤ 3).

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
