# PE011 · System disambiguation by sum closure: does the system that closes the sum agree with the counted object?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration** (this file, `tools/pe011_closure_system.py` and the label-free
`analysis/pe011_inventory.json` are published before any closure label, gate or agreement number is computed).
Open line 3 of the expedition README; last planned proto-Elamite cycle ("Where the trench stands", `1a10300`).

## Why this line
Proto-Elamite numerals made only of N01 and N14 (and N34/N45/N48) can be read in the capacity system C (N14 = 6 N01) or
in an integer system S/D/B (N14 = 10 N01). Born et al. 2023 disambiguate such notations two ways: by **summary lines**
(a summary is in one system, so a closing sum fixes the system) and by a **bootstrap classifier** on context signs
(the counted object). The two routes have never been checked *against each other* with a calibrated null. PE011 asks:
on tablets whose entries are all ambiguous C-vs-integer, does the class in which the total closes agree with the class
the counted-object signs predict — learned only from **unambiguous notations on other tablets** — beyond chance?

## External reference (verified, and exactly what is taken)
L. Born, M. W. Monroe, K. Kelley, A. Sarkar, "Disambiguating Numeral Sequences to Decipher Ancient Accounting
Corpora", *Proceedings of the Workshop on Computation and Written Language (CAWL 2023)*, Toronto, Association for
Computational Linguistics, July 2023, pp. 71–81, doi [10.18653/v1/2023.cawl-1.9](https://doi.org/10.18653/v1/2023.cawl-1.9)
([ACL Anthology](https://aclanthology.org/2023.cawl-1.9/); details read from the Anthology BibTeX and the PDF, 2026-11-08).
Taken, and nothing else:
1. **Readings with bundling** (their §3.1, Algorithm 1): a notation is valid in a system only if every sign exists
   there and no sign is repeated as often as the next higher unit (e.g. 7(N01) is not C, since 6 N01 = N14).
2. **The summary premise** (§3.2): a summary is written in one system, so a closing sum labels the tablet.
3. **Two context features** (Table 2): OBJECT (sign immediately preceding a numeral), FIRST_SIGN (first sign of the tablet).
4. **Their numbers, quoted descriptively only** (no decision weight): 8 011 intact numerals, 7 954 with ≥ 1 reading,
   1 919 unambiguous, 5 389 readable in all four systems (Table 1); 24 texts disambiguated by summary lines (§4.2);
   2-way (C vs rest) F1 0.90 of their classifier on a 48-item expert test set (Tables 3, 5).

**Not taken**: their classifier, their test set and their labels (this cycle is label-free: no expert label is used).
**Factor tables stay Englund 2004** (as in PE001–PE010). Discrepancy found while verifying: Born et al.'s Figure 1
gives the decimal system D as 10, 6, 10, 6 (N23 = 60 N01), Englund's Fig. 5.4 gives 10, 10, 10, 10 (N23 = 100).
Born's D is run only as a descriptive sensitivity.

## Disclosure: what has been looked at
- Balance "in any covering system" of the intact single-total tablets was computed in PE001/PE003–PE006 (C and
  S/D/B pooled). The **2-way class** of the closure (C only vs integer only) and any relation to object/header signs
  were **never computed**. All tablets are allowed (large sample, whole corpus).
- Computed before this file (label-free, `analysis/pe011_inventory.json`): set size 46, exclusion counts, object and
  header predictions (notation-only, from other tablets), total-notation classes, strata. No sum was formed.

## Data and set
Pinned CDLI dump `d66b12b` (`pe.atf` sha256 `5c4860ab…159a6`), whole proto-Elamite corpus (1 585 texts).
**Decision set**: no broken $-line, no primed line, exactly 1 reverse numeral slot and ≥ 2 obverse numeral slots,
every slot readable (intact, or damaged but completely read by the editor: PE006 rule), and **every obverse entry
2-way ambiguous** (valid with bundling in C and in at least one of S/D/B). Total unrestricted (an unambiguous total is
Born's propagation case). **46 tablets** (excluded: 743 shape, 642 slot count, 87 unreadable slot, 67 entry not ambiguous).

**Closure label** (2-way): C if total = obverse sum in C (all slots valid in C) and in no integer system with all slots
valid; I the reverse; none if it closes in both or in neither.
**Object prediction** (independent of sums): training = every intact numeral slot of the corpus on *other* tablets
whose notation is 2-way unambiguous; a sign predicts class k if it has ≥ 3 occurrences and share(k) ≥ 0.80; the
tablet's prediction is the strict majority over its slots (entries and total) with a predicting object sign.
Inventory: 34 / 46 tablets have an object prediction (24 C, 10 I); 6 have a header prediction (all C).

## Test (fixed now)
| Id | Statistic | Role |
|---|---|---|
| **H1 OBJECT** | number of tablets with a closure label and an object prediction where they agree | **decision**, α = 0.05 (one test, no Holm needed) |
| H2 HEADER | same with the FIRST_SIGN prediction | **descriptive only** (6 predictions < 8, declared from the label-free inventory) |

**Null (structure-preserving)**: closure labels permuted among the doubly-labelled tablets **within strata of list
length** (2 / 3–4 / ≥ 5 entries), keeping each stratum's label mix. R = 1 999, seed 1101; p = (1 + #null ≥ obs)/(1 + R).

## Gates (after this file is published, before the test)
- **FPR**: 100 stratified-permuted datasets, R = 299; rate of p ≤ 0.05 must be **≤ 0.06** (seed 1102).
- **Power**: 100 planted datasets, each doubly-labelled tablet (prob **0.5**) gets closure label := its prediction;
  R = 299; rate of p ≤ 0.05 must be **≥ 0.80** (seed 1103).
- **Size**: ≥ 8 doubly-labelled tablets.

## Decision rule
- **NOT TESTABLE** if any gate fails (likely failure mode, declared: if almost every label and prediction is C, the
  permutation null already agrees almost always and a planted agreement cannot be seen).
- **SUPPORTED** if the gates pass and p ≤ 0.05.
- **EXCLUDED** if p > 0.05 and the one-sided CP95 upper bound of the agreement rate is < 0.80 (the two routes cannot
  both be the ~0.9-reliable disambiguators they are taken to be); otherwise **NOT DETECTED**.

## Descriptive (after the decision, no weight)
Closure yield (2-way label counts; number of systems closing; unique single system) vs Born's 24 texts; closure label by
total-notation class; corpus numeral reading sets vs Born's Table 1; Born-D sensitivity; Born's worked example
P008014; list of disagreements; H2 HEADER.

## PE010 audit (independent, this cycle)
Re-run `pe010_per_line.py test` in a scratch copy with the published gates (all fields but run time must match) and
re-count PE010's **T1 = 2/60** (reverse equals one readable entry on D1) with a literal C table and plain integer sums
from the raw numeral parts, without the PE010 matching code.

## Results (run 2026-11-08 22:35 PT, 7 s; `analysis/pe011_gates.json`, `pe011_results.json`, `pe011_run.log`)
**Gates** (H1 OBJECT, 17 doubly-labelled tablets): FPR **0.01** ≤ 0.06 ✓ · power **0.81** ≥ 0.80 ✓ (barely) · size 17 ≥ 8 ✓.

| Id | Doubly labelled | Agree | Null mean | p | CP95 upper rate | Verdict |
|---|---|---|---|---|---|---|
| **H1 OBJECT** | 17 (closure C 9 / I 8; object C 12 / I 5) | **12** (0.71) | 9.0 | **0.148** | 0.88 | **NOT DETECTED** |

Not EXCLUDED: the CP95 upper bound 0.88 is above the 0.80 bar, so a reliable agreement is not ruled out either — the
crate is simply too small (17 tablets) to tell 0.71 from the 0.53 the permutation gives.

**Descriptive (no decision weight)**
- *Closure yield*: of 46 ambiguous-entry tablets, closure gives a 2-way label on **19** (C 10, I 9); 27 get none
  (22 close in no system, 4 in all four — N01-only lists —, 1 in C and an integer system together; the 9 I labels close in 2–3 integer systems at once).
  A **single** system closes on 10, all C. Born et al. report 24 texts disambiguated by summaries (with manual
  inspection and a wider filter: one *or two* reverse entries); our 19 automatic 2-way labels are the same order.
- *By total notation*: unambiguous C totals close in C on 1/10 (9 none); unambiguous integer totals close in I on 4/8;
  ambiguous totals give 9 C, 5 I, 14 none.
- *Born-D sensitivity* (N23 = 60): H1 13/18, p 0.11 — same picture.
- *H2 HEADER*: 2 doubly labelled, 0 agree (both closure I, header C) — nothing to read.
- *Born's example P008014*: closes in C only on our tables too (it is outside the decision set because entry 10 is
  3(N39B), unambiguous C), consistent with their §4.2.
- *Reading sets over 6 519 intact numeral slots* (Born count numerals differently: 8 011): all four 4 312 (Born 5 389),
  unambiguous 1 405 = C 1 330, D 61, S 7, B 7 (Born 1 919), none 153 (Born 57; we parse framed/variant signs and
  count per slot, so the totals are not comparable one-to-one).
- *Disagreements* (5): P008767, P008907, P009002, P009375 (closure I, object C) and P008806 (closure C, object I).
  Four of five are integer closures on tablets whose object signs usually carry capacity numbers — either mixed
  C/integer accounts (Born's Table 4 lists 32 such tablets) or coincidental closures; not resolved here.

**PE010 audit** (`analysis/pe011_pe010_audit.json`): `pe010_per_line.py test` re-run in a scratch copy — identical
except run time; T1 re-counted with a literal C table and plain integer sums from the raw numeral parts: **2/60**
(P008419, P009000), same tablets as published. ✓

**Verdict**: H1 **NOT DETECTED** (gates pass; 12/17 agree vs 9.0 by chance, p 0.148). No claim that sum closure and the
counted object agree beyond chance on this corpus; also no claim that they disagree. Not a new positive.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
