# LA001 · Calibrated KU-RO totals: does the KU-RO number equal the sum above it beyond chance?

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

Status: **pre-registration** (this file, `tools/la001_kuro_totals.py` and the label-free `analysis/la001_inventory.json`
are published before any sum is compared with any total). Open line 1 of the [expedition README](../README.md).

## Data
`LinearAInscriptions.js` of [mwenge/lineara.xyz](https://github.com/mwenge/lineara.xyz) at commit `9c81beb`,
sha256 `9a14cc300201ac8ed07563c09b92142ab59de91a74e646b2e743ca6aeb695f5e` (1 721 documents). Fetched, not copied (no
licence declared). Converted to `ins.json` with Node (`eval` of the file, `Map` to object). Field used:
`transliteratedWords`.

## Decision set (fixed by the inventory, label-free)
A **section** is the run of tokens from the document start (or from just after the previous KU-RO/KI-RO total) up to a
KU-RO. Its **entries** are the integer numerals in it (consecutive numerals form one entry); its **total** is the
integer number after KU-RO (one commodity logogram such as `GRA` may stand between them). A section enters the decision
set only if: no token carries `[`, `]` or `?`; every non-word token is an integer numeral, a newline, `𐄁` or `—`
(treated as a separator); the total is a pure integer; and there are ≥ 2 entries. Every fraction sign (¹⁄₂, ³⁄₄, `𐝫`,
13/20, …) excludes the section; fractions are LA002's business.

Inventory: **37 KU-RO sections, 11 in the decision set** (HT9b, HT11a, HT11b, HT39, HT88, HT89, HT94b, HT110a, HT117a,
HT118, HT122a); exclusion reasons are listed per section in the inventory JSON. Disclosure: while fixing the parser I
looked at the tokens directly after KU-RO on the excluded tablets, and I knew from the literature and the Workbench
that some KU-RO totals balance (e.g. HT9b is often cited). No sum-vs-total comparison was computed before this push.

## Hypotheses, metric, null, decision rule
- **H1 (exact balance).** Statistic E = number of decision sections with Σentries = total.
- **H2 (exact vs shifted).** Statistic C = E − mean over d ∈ {±1,…,±5} of #(Σentries − total = d). Guards against
  "sums land near totals because both scale with list size".
- **Null** (both): totals permuted among decision sections **within magnitude strata** (1–9, 10–99, ≥ 100), entries
  fixed; B = 20 000; p = (1 + #null ≥ obs)/(1 + B). Seed 1001.
- **Gates** (per test, 200 datasets each, inner B = 2 000): FPR on pairing-destroyed sets (totals globally permuted)
  must be ≤ 0.08; power with round(0.25 n) = 3 planted balances (total := sum on 3 random sections of a
  pairing-destroyed set) must be ≥ 0.80. A failed gate makes the test **NOT TESTABLE**.
- **Correction:** Holm over {H1, H2} at α = 0.05. Verdicts DETECTED / NOT DETECTED / NOT TESTABLE.
- **Descriptive only:** the full Σ − total histogram; a comparison with the Linear A Workbench's balance flags is
  deferred (not run this cycle).

**What a DETECTED would mean:** the KU-RO number is the arithmetic sum of the entries above it more often than a
same-magnitude number would be — the standard reading of KU-RO as "total", now calibrated. It says nothing about the
language. **No decipherment is claimed.**

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
