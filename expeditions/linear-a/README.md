# Expedition 4 · Linear A accounts (Minoan Crete, c. 1800–1450 BCE) — skeleton

> *Caderno de campo.* A few hundred clay tablets from Minoan Crete. We can sound out most of the signs, because Linear B
> borrowed them, but the language behind them is unknown. Some tablets end in **KU-RO**, a word that sits where a total
> sits. Totals either add up or they do not.

**Status: skeleton only (2026-11-08).** No data fetched, no number computed. The proto-Elamite expedition was paused
after PE011 ([closing summary](../proto-elamite/README.md#closing-summary-expedition-paused-after-pe011-2026-11-08)),
and Linear A is next in [TRIAGE.md](../TRIAGE.md) (score 6). The first cycle, LA001, is planned below and will be
pre-registered in its own commit before any data is touched.

Method is the same as the main repo and the proto-Elamite dig: pre-register hypothesis, metric and decision rule;
calibrate every null under a structure-preserving shuffle; plant controls (power ≥ 0.80); fixed seeds; Holm across a
family; verdicts SUPPORTED / NOT DETECTED / EXCLUDED / NOT TESTABLE; publish negatives. **No decipherment is claimed.**

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

## Layout (to be created by LA001)
`case-file/` pre-registered cases with results · `journal/` field notes · `tools/` re-runnable code ·
`analysis/` raw JSON · `data/` manifest with source commit and hashes (corpus files are fetched, not copied).

## Data (checked 2026-11-08, not yet fetched)
- **lineara.xyz** ([mwenge/lineara.xyz](https://github.com/mwenge/lineara.xyz), `LinearAInscriptions.js`): per-document
  JSON with transliterated words and numerals, after GORILA and G. Douros's tabulation. Candidate pin: commit
  `9c81beb` (2026-09-28 11:14 PT). The repository declares **no licence**, so LA001 fetches it by commit and hash and
  does not copy it here.
- **SigLA** (E. Salgarella, S. Castellan, [sigla.phis.me](https://sigla.phis.me/), CC BY-NC-SA): sign-level records,
  for cross-checking readings of numerals and fractions.
- Source edition behind both: L. Godart, J.-P. Olivier, *Recueil des inscriptions en linéaire A* (GORILA), Études
  Crétoises 21, vols. 1–5, 1976–1985.

## Prior work we must build on, not echo
- **Linear A Workbench** ([ryanpavlicek/linearaworkbench](https://github.com/ryanpavlicek/linearaworkbench), Apache-2.0)
  already publishes *machine-verified KU-RO arithmetic on every accounting tablet*. LA001 therefore cannot claim "the
  totals add up" as new; what it can add is the **calibration**: how often a KU-RO line equals the sum of the lines above
  it beyond a structure-preserving null (total shuffled among tablets of similar magnitude), with a planted-power gate
  and an exact-vs-shifted contrast (the PE003 instrument), and an audit of the Workbench's balance flags.
- **Navarre-AI/linear-a** ([repo](https://github.com/Navarre-AI/linear-a)): collated dataset with field-level provenance
  (GORILA, RILA Suppl. 1, SigLA, Younger, lineara.xyz) — a candidate cross-check for readings.
- J. G. Younger, *Linear A Texts and Inscriptions in Phonetic Transcription* (online commentary).

## Planned cycles (not run)
| Cycle | Family | Question | Notes |
|---|---|---|---|
| LA001 | Data setup + exact totals (F-SUM) | Does the KU-RO line equal the sum of the preceding integer numerals beyond a magnitude-stratified total-shuffle null, and more than its ±1 neighbours (exact-vs-shifted)? | Label-free inventory first (KU-RO tablets, intact lines, fraction signs present or not); fractions excluded from the decision set and declared; audit of the Workbench's balance flags as descriptive. |
| LA002 | Fractions (F-FRAC) | Which fraction values (J, E, F, K, …) close otherwise-failing KU-RO sums? | Candidate value sets fixed from the literature before looking; held-out tablets. |
| LA003 | KI-RO vs KU-RO | Do KI-RO lines behave like deficits (total − paid) rather than sums? | Only if LA001 is testable. |

## Open investigative lines
1. **Calibrated KU-RO totals** (LA001).
2. **Fraction values by closure** (LA002), with the PE004 lesson: closure solves only on tablets that balance.
3. **KI-RO arithmetic** (LA003).

## Outreach log
- 2026-11-08 (skeleton): none.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
