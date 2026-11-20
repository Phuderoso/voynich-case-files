# RULE — how I compute NC for the case 209 col21 raw hits (case 212 / I-326 question)

Voynich desk, 2026-11-20 (America/Dawson_Creek, MST). Written and hashed **before** any NC was computed
and before opening any case 212 / cycle 226 file. Not fully blind: see LEAKS.md.

## Inputs (fixed)
- Raw hit files: `/workspace/k209-d2-work/out/<text>/*.raw` (my regeneration of `run223.sh`, verified 170/170 against
  `SHA256SUMS_all_results.txt` in the case 209 audit), the lines starting `H `. Texts: K4 + 168 nulls from
  `/workspace/k209-d2-work/texts.tsv` (sha256 8c0d56d2…, byte-identical to `data/cycle223/texts.tsv` @ b304de5).
- Quadgram table: `qg.bin` sha256 4a02ba4e… (the hash declared in PREREG223; float32, 26^4 entries,
  index ((a*26+b)*676 + c*26 + d), letters A=0..Z=25; values are log10 scores; unseen quadgrams already carry the table's
  floor, -8.469008 (393,428 entries). **I use the table value as is, no extra floor, no smoothing.** log base 10.
- Scope (primary): every `H ` line at period p = 20 and p = 21. Variants frozen in advance: p 21 only; p 20 only.

## Decrypt of a hit (my own code, nothing imported from analyze223.py)
For hit (w, mode, dir, alph, beau, model, p, perm): positions S[i] in the ciphertext as in my case 209 recount
(`perm_maps`, `inv` if dir else `sig`); residue of plaintext index i is (S[i] if model else i) mod p; key value of each of
the 24 crib seats = (c - k) for Vigenere form (beau 0), (c + p) for Beaufort form (beau 1), in the hit's alphabet
(alph 0 = A-Z, 1 = KRYPTOS-keyed); a residue class's key = its **unique majority** value; a one-against-one class and
every class with no crib seat is **undetermined** -> plaintext letter '?'. Determined classes decrypt every position:
P = C - k (Vigenere) or P = k - C (Beaufort), back through the alphabet. Plaintext has 97 letters.

## NC
- Crib positions, K4 known plaintext, **1-indexed 22-34 EASTNORTHEAST and 64-74 BERLINCLOCK** (0-indexed 21-33, 63-73),
  the same positions in every text (the crib seats are the same plaintext indexes).
- Quadgram windows start at 0-indexed i = 0..93 (94 windows). **Primary (CRIB-OVERLAP): a window is used iff it contains
  no '?' AND none of its four letters sits on a crib position** (so windows that merely touch a crib are out).
  That leaves at most 64 windows (starts 0-17, 34-59, 74-93).
- NC = arithmetic mean of qg[window] over the used windows. nq = number of used windows.
- **known** = 97 minus the number of '?' in the decrypt (crib letters count).
- **PASS iff NC >= -6.0 AND known >= 49 AND nq >= 10.** If nq < 10, NC is reported as NA and the hit cannot pass.
- Sensitivity (frozen too, not primary): **CRIB-INSIDE**: window excluded only if all four letters lie inside one crib
  (partial overlap kept).

## Collapse and counts
- D2 key of a hit = (alph, beau, model, p, the 24 positions j[0..23] of the crib seats), as PREREG223.
- A D2 class **passes iff any hit in it passes** (the hits of one D2 class can differ outside the crib seats, because
  the column order is free there). So a corpus has a pass iff any raw hit passes; I also print the number of passing D2
  classes, and a variant where the class is represented only by its first hit (files sorted by name, then line order).
- Per corpus (K4 and each null): raw hits, D2 classes, passing hits, passing D2 classes, max NC over hits with nq >= 10
  (**maxNC**), and max NC over hits with nq >= 10 and known >= 49 (**maxNC49**).
- Summary: K4 passes; nulls with >= 1 pass out of 168; null max (maxNC and maxNC49); K4 max (both).
- Outputs: `counts_nc.tsv` (per corpus), `summary_nc.txt`, then `FROZEN.txt` with hashes and timestamp.
