# LA003 · Can KI-RO arithmetic, or a second reading of the failing totals, be tested at all?

**Status: pre-registered 2026-11-09 ~00:55 PT (commit `b0b6118`), results ~01:05 PT. Both lines NOT TESTABLE.**

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

LA001 and LA002 taught one thing: compute the attainable p floor and the power **before** the count. LA003 is
therefore a feasibility cycle for the two remaining open lines. It decides *whether* a test can exist; it does not
claim a reading.

## Line A · KI-RO as a deficit (open line 3)
- **Hypothesis (to be tested only if the gate passes).** A number written after KI-RO equals an expected amount minus
  what was delivered, within the same document that carries a KU-RO total.
- **Usable case (fixed now).** A document side in lineara.xyz `9c81beb` where (i) KI-RO is followed by at least one
  numeral (integer or a fraction sign, values after Corazza et al. 2021 as in LA002), (ii) the same side carries a
  KU-RO total, (iii) neither the KI-RO line nor the KU-RO line carries damage (`[`, `]`, `?`) or an unreadable
  token (anything that is not a word, separator, integer or a known fraction sign).
- **Gate.** Any permutation null over n usable cases has at most n! orderings, so the floor is ≥ 1/n!. The test is
  run only if n ≥ 4 (24 orderings, floor ≤ 0.042 < 0.05) **and** a planted-power curve on the usable cases reaches
  0.80. Otherwise **NOT TESTABLE**, and any arithmetic is printed as descriptive only.
- **Disclosure.** Before writing this file I listed the 12 lineara.xyz sides that contain KI-RO (positions and tokens,
  no balance computed by the tool). Reading that list, I saw by eye that HT123+124a's OLIV column adds to its KU-RO
  (31 + 31½ + 16 + 15 = 93½). That side is therefore **descriptive only** whatever the gate says.

## Line B · Second reading of HT39 and HT122a (rest of open line 1)
- **Question.** Does a source independent of lineara.xyz give different *numerals* for the two KU-RO sections that
  fail and that the Bologna literature does not explain (HT39, HT122a)?
- **Source.** Navarre-AI/linear-a `corpus.json` at commit `e4cb48b` (sha256 `1fc20814…24a8`, CC BY 4.0 with SigLA-derived
  records CC BY-NC-SA 4.0; fetched by commit, not copied here).
- **Rule.** For each record, list which sources it cites and whether any sign-level entry carries a numeral role. If
  the numerals reach the record only through lineara.xyz's Unicode text, the cross-check is **NOT TESTABLE** with
  this source (it would compare lineara.xyz with itself). If an independent numeral reading exists, report whether it
  makes the section balance (descriptive; n = 2, no p-value).

## Results (2026-11-09 ~01:05 PT; `python3 tools/la003_feasibility.py ins.json corpus.json analysis/la003_results.json`, 0.1 s)
**Line A · NOT TESTABLE.** 12 lineara.xyz sides contain KI-RO. Only **2** are usable cases (HT123+124a, HT123+124b),
so the best possible floor is 1/2! = 0.5 and the n ≥ 4 gate fails before any power curve. No test was run.

| Side | KI-RO use | KU-RO on side | Note |
|---|---|---|---|
| HT1, HT15, HT30 | followed by a number | no | nothing to subtract from on the same side |
| HT34 | followed by a number | no | damaged (`[[7]]`) |
| HT37, HT55a, HT93b | heading, no number | no | |
| **HT88, HT94b, HT117a** | **heading, no number** | **yes** | the KU-RO closes the list KI-RO heads |
| HT123+124a | four per-person KI-RO amounts + KI-RO 6 after the KU-RO | yes | two amounts carry an unreadable `.3` |
| HT123+124b | KI-RO 5 after KU-RO 20 | yes | |

*Descriptive only (not a test).*
- Three of the six sections that balanced in LA001 (HT88, HT94b, HT117a) are lists **headed** by KI-RO, each a column
  of 1s closed by KU-RO. In these three, KI-RO is a heading and carries no number of its own.
- HT123+124a: the OLIV column adds exactly (93½, seen by eye before the pre-registration, see the disclosure). The *308
  column is 8¼ + 8¾ + 4≈⅙ + 4¼ = 25 5⁄12 against KU-RO 25≈⅙, a ¼ gap if ≈⅙ is read as ⅙. The per-person KI-RO amounts
  that can be read are ¾ and ¾. Two are unreadable (`1 .3`, `.3`), so whether they add up to the final KI-RO 6 cannot
  be checked on this transcription.

**Line B · NOT TESTABLE with this source.** Navarre-AI's records for HT39 and HT122a cite `lineara` and `sigla`. In the
whole corpus.json, the sign-level entries have the roles erasure, fraction, logogram, syllabogram and transaction.
None of them is a numeral. The numerals (5 in HT39, 21 in HT122a) appear only in `unicode_text`, which is
lineara.xyz's text, so this cross-check would compare lineara.xyz with itself. The SigLA word readings differ
from lineara.xyz in one word of HT122a (`pa-ri-ne` vs `PA-TA-NE`), which does not touch a number.
Descriptive: in HT39 the KU-RO carries a different commodity (*414+A 100) from the entries (AROM 10, 8, 10). So it is
probably not a sum of the lines above, and LA001's parser counts it as a failure only because it has no commodity check.

## What this closes
- Open line 1 (KU-RO totals): closed on every machine-readable source we can reach. A numeral check needs the GORILA
  photographs or the SigLA sign drawings, which have no numeral layer in machine-readable form.
- Open line 3 (KI-RO): closed as NOT TESTABLE on lineara.xyz (n = 2).
- Audit of LA001: the parser has no commodity check, so HT39 counts as a failure of a sum it probably never claimed.
  This doesn't change LA001's verdict (NOT TESTABLE) or its 6/11 count: removing HT39 would make it 6/10. Declared here.

## Tool
`tools/la003_feasibility.py` (no randomness; exact counts only). Output `analysis/la003_results.json`.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
