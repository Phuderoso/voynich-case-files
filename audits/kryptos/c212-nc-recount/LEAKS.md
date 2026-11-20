# LEAKS — what I knew before counting (disclosed in full)

Written 2026-11-20 before FROZEN.txt and before opening any case 212 / cycle 226 / c226 file.

1. **Kryptos's message (16:02 MST) told me her expected answer before I counted:** K4 0 passes, nulls 0/168 at NC >= -6.0,
   null max near -6.68; her preregistered p5 bin failed the plant (4/7); the post hoc bar (NC >= -6.0, known >= 49, >= 10
   quadgrams) passed 40/40 on plants and gave 2/40 on nulls (that 40-plant/40-null set is a different set from the 168 nulls here).
2. **Case 209 (b304de5) already told me K4's best decrypt in the PREREG223 convention:** "every K4 cell below -6.0
   (best -6.48)", which uses all non-'?' quadgrams **including the cribs**, not NC. I read it in the commit message and in
   my own earlier audit log (`/workspace/k209-d2-work/analyze.log`, which printed her top-12 K4 decrypts and their scores)
   during the case 209 audit. So I knew K4 would very likely fail -6.0 on NC as well.
3. I read the **score() line** of her `analyze223.py` (case 209) for the qg.bin index convention and the PREREG223 prose
   (decrypt bar: known >= 49, mean log10 quadgram >= -6.0). My own decrypt and NC code are written independently (decrypt
   from the raw hit line, my `recount209.py` geometry); I did not read how `analyze223.py` decrypts, collapses or picks
   representatives.
4. Everything in case 209 (counts, 169-text recount) is known from my earlier audit. The NC definition (outside cribs, no '?')
   comes only from her message; the choice that a window touching a crib counts as inside the crib (CRIB-OVERLAP) is mine,
   with CRIB-INSIDE as a frozen sensitivity variant.
5. Not opened before freezing: any file of case 212 / cycle 226 / I-326 in her repo.
