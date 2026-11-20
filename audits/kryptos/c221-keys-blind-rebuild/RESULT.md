# Result (after freeze at 2026-11-19 23:53:10 PT)
MATCH: keys221a_V1.bin sha256 aef84534c6a53c9d0dd4415c8bd0f5a76d67635cf364e481cd75f47d022d4cfe
= sha256 of origin/main:tools/cycle221/keys221a.bin (her file, hashed from git blob; data/cycle221/SHA256SUMS lists only keys221a.tsv).
Leaks disclosed: (1) `git show --stat 823ed97` listed file names/sizes (keys221.bin 1,239,078 B) and the commit message;
(2) `git log origin/main -3` showed commit subjects of cycles 221/222 (K4 0 hits, plants 20/20, null 0; 222 IG "both bit orders");
(3) `git grep aef84534` printed one line of case-file/207 (the hash line only). None seen before the freeze except (1).
