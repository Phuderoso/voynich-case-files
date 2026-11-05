# Data manifest
| File | Source | Version | Retrieved | sha256 |
|---|---|---|---|---|
| ZL3b-n.txt | https://www.voynich.nu/data/ZL3b-n.txt | ZL IVTFF "Version 3b of 13/05/2025" (Eva-, IVTFF 2.0) | 2026-11-04 | bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc |

## C003 control corpora (not committed; fetch into `data/corpora/` and check the hash)
| File | Source | Retrieved | sha256 (prefix…suffix) |
|---|---|---|---|
| pg218.txt | https://www.gutenberg.org/cache/epub/218/pg218.txt (Caesar, De Bello Gallico I–IV, Latin) | 2026-11-04 | 84ac8411…cb2f659c |
| pg23306.txt | https://www.gutenberg.org/cache/epub/23306/pg23306.txt (Descartes, Meditationes, Latin) | 2026-11-04 | d6fea498…7d7ff0ad |
| pg1012.txt | https://www.gutenberg.org/cache/epub/1012/pg1012.txt (Dante, Divina Commedia, Italian) | 2026-11-04 | 568035b4…26c0c1c6 |
| pg2000.txt | https://www.gutenberg.org/cache/epub/2000/pg2000.txt (Cervantes, Don Quijote, Spanish) | 2026-11-04 | 534f41d5…6d5b04d7 |
| Gen.xml | https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Gen.xml (Westminster Leningrad Codex, Genesis) | 2026-11-04 | 0526e5c9…68d86449 |
| ts_generated_text.txt | https://raw.githubusercontent.com/TorstenTimm/SelfCitationTextgenerator/master/executable/generate/generated_text.txt (Timm & Schinner sample, MIT licence) | 2026-11-04 | 1e954a17…2888dc11 |

## C013 control corpora (not committed; fetch into `data/corpora/` and check the hash)
| File | Source | Retrieved | sha256 (prefix…suffix) |
|---|---|---|---|
| pg56498.txt | https://www.gutenberg.org/cache/epub/56498/pg56498.txt (Machiavelli, La Mandragola — La Clizia — Belfagor, Italian) | 2026-11-05 | b149ce46…bbceef61 |
| Exod.xml | https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/Exod.xml (Westminster Leningrad Codex, Exodus) | 2026-11-05 | 04868367…a5b847f |

Backup copies kept outside the working copy at `/workspace/voynich/backup/`.

## C004 generator (not committed; fetch into `$TSGEN`, default `/workspace/voynich/tsgen`, and check the hash)
| File | Source | Retrieved | sha256 (prefix…suffix) |
|---|---|---|---|
| text-generator.jar | https://raw.githubusercontent.com/TorstenTimm/SelfCitationTextgenerator/master/executable/text-generator.jar (MIT) | 2026-11-04 | dc9b2f3c…ad18fef8 |
| conf.properties | https://raw.githubusercontent.com/TorstenTimm/SelfCitationTextgenerator/master/executable/conf.properties | 2026-11-04 | 308af498…f9061ee |
Runtime: Eclipse Temurin JRE 17.0.21 (api.adoptium.net). Default config + seed 19 reproduces `ts_generated_text.txt` byte for byte.
