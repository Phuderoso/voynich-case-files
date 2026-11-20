# Collapse rule for case 210 / cycle 224, cell V, all.bin, p=19

Voynich desk, 2026-11-20, America/Vancouver.
Defined and hashed before opening Kryptos's summary, label, journal, or verdict files
for cycle 224, and before opening summarize224.py. Not fully blind: Kryptos's message
already stated raw p 0.040 and a collapsed occupancy of 11/100 (see LEAKS, written later).

## Cell
Model V (vector offset on a 3x10 torus keyboard), column A, wordlist all.bin, period p=19.
A raw hit is one H-line: (perm, dir, ix, lay, p, err).

## Unit: distinct crib test
Two hits are the same test if and only if they produce the identical decrypt/crib
alignment. The identity of a test is the pair

    (crib string used, plaintext / alignment that the crib induces)

and not the raw (perm, dir, ix, lay) tuple. Layout, wordlist line number, and
direction are only instruments; they collapse when they do not change that pair.

Operationally, after decrypting each hit with its crib-derived key:

1. Layouts (QWERTY vs QWERTZ, and any other pair). Collapse two hits that share
   the same crib and the same plaintext. This is expected when the hit does not
   touch a key that differs between the layouts (for QWERTY/QWERTZ, the Y/Z
   keys). If the plaintexts differ, they are distinct tests.

2. Wordlist lines. Collapse two hits whose cribs are the same string, or one of
   which is derived from the other (the same letters in the same order, including
   a mere direction flip, a duplicate line, or an adjacent-line copy of the same
   crib). Adjacent wordlist lines that are different crib strings and that yield
   different alignments stay distinct.

3. Direction (dir=0/1). Collapse when the resulting crib string and plaintext
   are the same (a reversed scan of the same crib is not a new test).

4. The seat / phase index (ix) is part of the alignment: a different ix that
   seats the crib at a different residue, or that yields a different plaintext,
   is a different test. A dissenting seat that is only an equivalent coding of
   the same alignment is not.

## Counts
- For each corpus (K4 and each of the 100 nulls 209437-209536), count the number
  of distinct tests under this rule, at this cell only (V, all.bin, p=19).
- Occupancy: number of nulls with at least one distinct test.
- p_raw = (1 + #{nulls with raw hit count >= K4 raw hit count}) / (1 + 100),
  with K4's raw count taken from the H-lines (expected 4).
- p_collapsed = (1 + #{nulls with >= 1 distinct test}) / (1 + 100)
  if K4 itself has >= 1 distinct test; this is the occupancy p, which is the
  quantity asked about. Also report the stricter rank
  p_up = (1 + #{nulls with distinct-test count >= K4's distinct-test count}) / (1 + 100).

Hits at other periods, other models, or other wordlists are out of scope.
