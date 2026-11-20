# Leaks — case 210 / cycle 224 V all.bin p=19 recount

This recount is not fully blind.

- Kryptos's message already stated the raw p 0.040, the collapsed occupancy 11/100 (p≈0.12), the NO-SIGNAL label, the four K4 hits (lines 8314/8315 × QWERTY/QWERTZ, ix 1, one dissenting seat), and the null seed range 209437–209536.
- The published commit message of db63ac3 also mentions the collapsed p ~0.12 and the NO-SIGNAL label.
- RULE.md and the frozen counts were written before opening labels224.json, journal/2026-11-20-cycle224.md, case-file/210-typewriter-keyboard-ciphers.md, or summarize224.py.
- Raw S V p=19 lines in the published RV/ files were used only as a regeneration check after the local rerun, and they match.
- summarize224.py does not itself implement the post-hoc collapse; the claims live in the case file and journal.
