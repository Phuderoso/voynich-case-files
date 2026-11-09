# LA002 · KU-RO = sum, replicated on sections LA001 did not use

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration** (this file, `tools/la002_disjoint_replication.py` and the label-free inventories are pushed
before any sum of these sections is compared with its total). Open lines 1 and 2 of the [README](../README.md).

## Audit of LA001 (found while preparing this cycle)
LA001's case file lists `𐝫` (U+1076B) among the fraction signs. That is wrong: U+1076B is not a Linear A fraction
(Unicode's fractions are U+10740–U+10755, A701 A … A732 JE); lineara.xyz uses it as its **erased-sign marker**
(`stripErased()` in `utils.js` at `9c81beb`). LA001 excluded those sections, which is still a defensible rule (an
erasure is a damage class), so **the LA001 verdict is unchanged**; only the label is corrected. Here the marker is
re-read as a separator: what a scribe erased is not part of the account.

## Decision set (label-free, fixed by the inventory)
Same section rule as LA001, except: (a) `𐝫` is a separator; (b) fraction tokens count with these values, taken as
lineara.xyz renders them and checked against M. Corazza, S. Ferrara, B. Montecchi, F. Tamburini, M. Valério, "The
mathematical values of fraction signs in the Linear A script: a computational, statistical and typological approach",
*Journal of Archaeological Science* 125 (2021) (J = ½, E = ¼, F = ⅛, D = ⅓, B = ⅕; combinations add, J+E = ¾):
¹⁄₂, ¹⁄₄, ³⁄₄, ¹⁄₈, ¹⁄₃, ¹⁄₅, ³⁄₈, ⅝. Uncertain renderings (¹⁄₁₆, where K is ⅒ or 1/16 depending on the author;
13/20; ≈ ¹⁄₆) count **only in a sensitivity run**; (c) every section used in LA001 is removed.
Equality is exact over rationals. Primary decision set: **5 sections** (HT9a, HT13, HT100, HT109, PH(?)31a);
sensitivity: 6 (+ HT123+124b).

## Hypothesis, null, gates, decision rule
- **H1:** E = number of sections with Σentries = total is larger than under the null.
- **Null:** totals permuted among decision sections within magnitude strata (1–9, 10–99, ≥ 100); a stratum with fewer
  than 2 sections joins the next lower one (or the next higher, if it is the lowest). The null is **enumerated exactly**.
- **Gates computed before E** (the script prints them first): the exact p floor, and a planted-power curve over
  k = 1…n (100 pairing-destroyed sets per k, seed 2020). k* = the smallest k with power ≥ 0.80. **If no k* ≤ n/2
  exists, H1 is NOT TESTABLE**, whatever E turns out to be. This is LA001's lesson applied.
- One test, α = 0.05, no family. Sensitivity run is descriptive.

Expectation stated in advance: with n = 5 a pass is unlikely (only 120 orderings at most), so the likely outcome is
NOT TESTABLE, which would close the lineara.xyz replication as data-limited and send line 1 to a second transcription
(SigLA / the Navarre-AI collation) rather than to more cuts of the same tablets.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
