# C108 — Expedição 108: the two-class door (Sukhotin's vowels)
*Do the manuscript's glyphs split into two classes that alternate inside words the way vowels and consonants do, and does that alternation look like an alphabet with vowels, an abjad, or the copying generator?*

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed, ran and wrote this case.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Pre-registration (written and committed before any Voynich or generator statistic of this cycle was computed)

**Why now.** C103–C107 were all F-RHYTHM; the one-in-three rule requires a new approach family. **F-VC (vowel/consonant
structure)** is new to this repo. **Prior work credited:** B. V. Sukhotin's algorithm (1962; translated by J. Guy, see
<https://voynich.nu/misc/misc_02.html>); J. B. M. Guy, "Vowel identification: an old (but good) algorithm", *Cryptologia* 15(3),
1991, and "Statistical properties of two folios of the Voynich manuscript", *Cryptologia* 15(3), 207–218, 1991, which ran it on
f79v/f80r and reported `o`, `y`, `a`, `c`, `cc` as the first "vowels" (Bennett transcription; as quoted by Guy on the Voynich
mailing list, 2001). What is new here is a **calibrated** version: a structure-preserving null, planted controls, voweled and
abjad reference ranges, and the Timm–Schinner generator at matched size.

**Data.** `data/ZL3b-n.txt`, `data/IT2a-n.txt` (sha256 in `data/MANIFEST.md`), words in EVA glyph units
(`tools/c003_position_rigidity.py::units`; units `cth ckh cph cfh ch sh`), all pages in file order via
`tools/c047_pair_currier_split.py::ivtff_pages_lang`. Controls (`tools/c051_context_spelling_ab.py::nat_texts`): voweled =
Latin (Caesar, Descartes), Italian (Dante, Machiavelli), Spanish (Cervantes), Finnish (Kalevala, Kivi); abjad = Hebrew
(Genesis, Exodus, unpointed) and devowelled Latin Caesar, Italian Dante, Spanish Cervantes. Generator:
`tools/c004_generator_sweep.py::generate` (Timm–Schinner defaults, 3,400 lines), seeds 11733–11736.

**Statistic.** Each text is cut into 15,000-token halves (two disjoint halves; one when the text has < 30,000 tokens, the C055
rule). Contacts = adjacent units **inside a word**, both orders, identical pairs excluded. Sukhotin's algorithm on the symmetric
contact matrix gives a two-class split V/C. **A** = share of within-word adjacent non-identical pairs whose units are in
different classes. **Null N1**: units shuffled within every word (keeps word length and the unit multiset), Sukhotin
**re-fitted** on each shuffle, NSH = 200. **E = A − mean(A_null)**; p = (1 + #{A_null ≥ A})/(1 + NSH).

**Hypotheses (α = 0.05).**
- **H1** (alternation beyond within-word order): all four Voynich halves (ZL ×2, IT2a ×2) p < α/4 → **EXCESS**; none → **NO
  EXCESS**; else **SPLIT**.
- **H2**: Voynich E vs the voweled range (min–max over voweled halves): INSIDE / ABOVE / BELOW / STRADDLE.
- **H3**: Voynich E vs the abjad range: same labels.
- **H4**: Voynich E vs the generator range (needs ≥ 6 generator halves): same labels.

**Gates.** G1 FPR: 20 within-word-shuffled voweled halves tested against a fresh shuffle null (NSH 100): ≤ 2/20 at α.
G2 power: in a within-word-shuffled voweled half, restore the true spelling of 30 % of words (q fixed now): ≥ 16/20 at α.
G1 or G2 fail → every H **NOT TESTABLE**. G3 tool validity (reported, not a veto): Sukhotin token accuracy vs the true vowel
letters (`aeiou`, plus `y` for Latin and Finnish) ≥ 0.80 in every voweled half. G4 separation: the voweled and abjad E ranges
must not overlap, else H2/H3 are **NOT SEPARABLE** (the scale cannot tell an alphabet from an abjad at this N).

**Reading rule (fixed now).** H2 INSIDE and H3 not INSIDE → "alternation like an alphabet with vowels"; H3 INSIDE and H2 not →
"abjad-like"; H2 BELOW and H3 ABOVE → "between"; anything else is reported as found. H4 says whether the copying generator
reproduces it. **No reading of which glyphs "are vowels" is claimed from this**: the V set is printed descriptively only,
because positional rigidity (e.g. word-final `y`) can create alternation without any sound value. Raw EVA characters (no
units) are a descriptive variant.

**Seeds.** 11732 main (gates, nulls), 11733–11736 generator; next free **11737**.

**Code.** `tools/c108_sukhotin_alternation.py`, committed with this pre-registration. Smoke test before commit: Latin Caesar
half 1 only (A 0.820, E +0.214, V = `aeiouy`, token accuracy 1.00); generator output length checked; no Voynich or generator
statistic computed.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04

## Results (registered run 08:35:59–08:38:30 PT, 151 s; prereg `8d86a2c`; log `analysis/C108_run.log`, numbers `analysis/C108_results.json`)

**Gates.** G1 FPR **0/20**, G2 power **20/20** (30 % restored spellings) → pass. G3 tool validity **pass**: Sukhotin recovers the
true vowels in every voweled half (token accuracy 0.981–1.000; V = `aeiou(y)`, plus a stray `h`, `k` or `f` in four halves).
G4 separation **pass, narrowly**: voweled E 0.137–0.214, abjad E 0.002–0.129 (gap 0.008; devowelled Dante 0.127/0.129 is the
highest abjad: its Sukhotin "vowels" are the sonorants `h l n r s x`).

| Text (15k-token halves) | E = A − null mean | Sukhotin class V |
|---|---|---|
| Latin Caesar / Descartes | 0.214 / 0.193 | aeiouy / aeikouy |
| Italian Dante (2) / Machiavelli | 0.137, 0.138 / 0.152 | aehiou / aeiouy |
| Spanish Cervantes (2) | 0.186, 0.186 | aeiou |
| Finnish Kalevala (2) / Kivi (2) | 0.205, 0.209 / 0.214, 0.211 | aeiouy (Kivi h1 + f) |
| Hebrew Genesis / Exodus (unpointed) | 0.045 / 0.050 | 12–14 letters |
| Devowelled Caesar / Dante (2) / Cervantes (2) | 0.002 (p 0.31) / 0.127, 0.129 / 0.083, 0.082 | sonorants |
| **Voynich ZL 3b (2)** | **0.205, 0.208** | a c e g h n o y / a c e n o u y z |
| **Voynich IT2a (2)** | **0.207, 0.208** | a c e g n o y / a c e n o y |
| Timm–Schinner generator, seeds 11733–11736 (8) | 0.119–0.198 | mostly a e n o y |

All p for H1 are at the floor 1/201 = 0.005 < α/4.

**Verdicts.** **H1 EXCESS** (all four halves). **H2 INSIDE** the voweled range (upper part, beside Finnish and Latin). **H3 ABOVE**
the abjad range. **H4 ABOVE** the generator range (margin small: best seed 0.198 vs Voynich minimum 0.205; four seeds, default
settings only). By the registered reading rule: **the manuscript's within-word glyph order alternates between two classes as
strongly as alphabetic text with written vowels, more than any abjad control, and slightly more than the default copying
generator.**

**What this does not show.** It does not show that any glyph is a vowel. The within-word shuffle null destroys positional slots
as well as phonotactics, and the generator, which has slots but no sounds, reaches 0.12–0.20: most of the alternation can come
from a slot grammar. The Voynich V class (`a c e n o y`, units `ch`/`sh` in C) mixes glyphs that fill fixed positions (`y`
word-final, `n` after `ai(i)`). Guy (1991) found `o y a c cc` first on two folios; our class agrees on `o y a`, while `c`/`cc`
are units `ch`/`e`-runs in a different transcription, so the comparison is approximate. Raw-character variant (descriptive):
ZL 0.140/0.175, IT2a 0.141/0.174, lower because splitting `ch`, `sh` into letters adds artificial contacts.
Seeds used 11732–11736; next free **11737**.

**Next (F-VC step 2, proposed):** separate slots from alternation: (a) a slot-preserving null (shuffle each glyph among words
at the same position-from-end and word length) and (b) the C083 generator grid, to see whether any slot generator reaches
0.205 and whether a residual alternation survives slots.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
