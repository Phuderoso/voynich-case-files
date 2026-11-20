# Ambiguities in PREREG221 (823ed97) prose, and choices made (blind rebuild of keys221a.bin)

Sources read: tools/cycle221/PREREG221.md, tools/cycle218/PREREG218.md (string list), tools/cycle217/PREREG217.md (window/model
definitions), tools/cycle218/keys218.bin (data input for "drop windows already in keys218.bin"; also used to infer the binary format).
Not opened: keys221.py, keys221.bin, keys221.tsv, split221.py, check221.py, plant*.py, any summary/case file for cycle 221.

A1  Binary format. Not stated. Chosen: 97 raw bytes per window, values 0..25, no header/delimiter (as keys218.bin: 748,743 = 7,719x97).
A2  Window. "97-shift window, cyclic over the encoded string, every offset": k_t = v[(o+t) mod L] mod 26, t=0..96, o=0..L-1.
A3  Strings. 35 of PREREG218 in its listed order (keyed alphabet = KRYPTOSABCDEFGHIJLMNQUVWXZ; the two coordinate strings
    literally incl. spaces and '.'), then the 7 Morse-plate phrases in PREREG221 order. Sum of lengths = 405.
A4  Dedup vs keys217.bin: keys217.bin is NOT committed at 823ed97, so only keys218.bin is used. (No chunk-A window collides with
    keys218.bin, and all family counts match, so 217 overlap is presumably 0.)
A5  Generation order (biggest hash risk). Prose lists families; chosen V1 = string-major (for each string: IT, IG, MC, MV, MB, EB,
    EN), first occurrence kept, IG generated only for dedup, then chunk-A families kept in that order (split preserves order).
    Evidence: ONLY string-major reproduces every published count (MC 394 = 396 - 2 RQ windows equal to BERLIN MB g=8 windows;
    MV 396 = 398 - 2 RQ windows equal to RQ IT reversed-table windows). Family-major (V4) gives MC 396 / MB 3369 (total still 7012).
    keys218.bin is also string-major. BC assumed last (cannot affect chunk A).
A6  ITA2 table: standard ITA2 bit patterns b1..b5; "b1 = LSB" -> A=3, E=1, T=16, FIGS=27, LTRS=31, space=4; reversed = b1 MSB.
    Order: LSB table first, then reversed. Digits and '.' on FIGS row (1=Q..0=P, '.'=M); FIGS/LTRS inserted only on mode change;
    initial mode LTRS; no shift appended at string end; space (4) valid in both modes, no shift. -> IT 826 (matches).
A7  IG bit order inside the stream (b1-first vs b5-first): irrelevant to chunk A (no IG window collides with chunk A); V2 = b5-first
    is byte-identical to V1.
A8  Morse: spaces have no code (skipped); '.' encoded as .-.-.- (6 elements, so MC has one value 6 despite "values 1-5").
    Dropping '.' gives MC 382 / MV 384 / MB 3173 -> rejected by counts.
A9  MV: '1' + dot0/dash1, read MSB-first (A=.- -> 101 = 5), mod 26.
A10 MB: concatenated dot/dash bits, no gaps; window at EVERY BIT offset o: group t = bits[o+g*t .. o+g*t+g-1] cyclic mod M, MSB-first;
    g order 4, 5, 8 (g outer, offset inner). -> 3371 (matches).
A11 EB: cp037 byte mod 26, upper-case block then lower-case block (V1). V3 = 218-style case-outer (EB up, EN, then EB lower).
A12 EN: upper case only; nibbles high-then-low, every nibble offset; then nibble pairs (16a+b) mod 26 at every nibble offset
    0..2L-1; even-offset pairs equal EB upper windows and drop out -> 2L + L = 1215 (matches).
A13 Ordering inside a family: variant (table / case / g) outer, string offset inner.
V5  = V1 windows sorted bytewise (in case the file was sorted).
