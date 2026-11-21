# RULE — case 214 / cycle 228 Part B question: max NC per case (205, 206, 211), K4 and nulls, tie='?' and first-vote

Voynich desk, 2026-11-21 (America/Dawson_Creek, MST). Written and hashed **before** any NC was computed on these
hits and before opening `data/cycle228/reread228.json`, `reread228.log`, `analyze228.log`, `summary228.json`,
`results_*` of cycle 228, `tools/cycle228/{nc228,reread228}.py`. Not fully blind: see LEAKS.md.

## Inputs (fixed)
- Fresh sparse clone of `Phuderoso/kryptos-case-files` @ `01e823035e4b581fafd599534b08fcac6c910084` (origin/main) in
  `/workspace/k228-nc-maxima/kryptos-main`. Paths: `data/cycle219/` (case 205), `data/cycle220/` (case 206),
  `data/cycle225/` (case 211), `tools/cycle228/PREREG228.md`. No `data/cycle228/`. `/workspace/k4c216/repo` untouched.
  Each cycle's `SHA256SUMS` verified (all OK) before use.
- Hit lines (`H ...`) of K4 and of every published null, texts from each cycle's `texts.tsv`:
  case 205 (`K4.txt`, `null1_124`, `null209234–209241`; w 9–10, excess ≤ 1 at p ≤ 18, strict at every p printed),
  case 206 (`results_k4.txt`, `results_null209243–209250`; w 11, π[0] ∈ {0,1}, p 1–18, excess ≤ 1),
  case 211 (`results_k4.txt`, `results_null209538–209545`; w 11, π[0] ∈ {2,3}, p 1–18, excess ≤ 1).
  Plants and gate files are not used.
- `qg.bin` sha256 4a02ba4e… (index ((a·26+b)·26+c)·26+d, A=0, floor −8.469008 already in the table, no extra floor).

## Decrypt (my own code; geometry from my case 209 recount `perm_maps`, key-value logic as `recount209.py`)
- Hit fields: `w mode dir al be model p excess bad π…`. Positions S[i] from `perm_maps(w, π)` (σ if dir 0, σ⁻¹ if dir 1).
  Residue of plaintext index i = (S[i] if model = 1 else i) mod p. Key value of crib seat t = (c − k) form for Vigenère
  (be 0), (c + k) form for Beaufort (be 1), with alphabets (plain-side alphabet for the crib letter, cipher-side alphabet
  for the ciphertext letter): al 0 = (A–Z, A–Z); al 1 = (KRYPTOS-keyed, KRYPTOS-keyed); **al 2 = (KRYPTOS, A–Z) (Quagmire I)**;
  **al 3 = (A–Z, KRYPTOS) (Quagmire II)**. This orientation was chosen by testing which of the four (plain, cipher) pairings
  reproduces the stamped `excess` on a sample of every al value (conv_check.py, run before this file; it computes **no NC**);
  only one pairing matched for each al. The full script re-asserts excess == stamped value on **every** hit and aborts otherwise.
- Residue class of crib seats (24 seats: 0-indexed 21–33 EASTNORTHEAST, 63–73 BERLINCLOCK); class key is:
  - **tie='?' (house rule):** the unique top-multiplicity key value; a tie for the top reads **'?'**;
  - **first-vote (old rule, `Counter.most_common` first inserted, seats taken in order 0…23):** the first-inserted of the top-multiplicity values.
  A class with no crib seat is '?' in both rules. Determined classes decrypt every position of the class (97 letters).
- known = 97 − (number of '?'). NC windows start at i = 0..93: used iff no '?' and no letter on a crib position (0-indexed 21–33, 63–73);
  n = number of used windows; NC = mean `qg` over them (NA if n = 0). **PASS iff NC ≥ −6.0, known ≥ 49, n ≥ 10.**

## Units and counts (each reported under both tie rules)
- **U1 raw hit lines.**
- **U2 D2 as PREREG228 (primary):** first hit (file order) of each signature (w, mode, dir, al, be, model, p, 24 carved positions j under the crib seats).
- **U3 D2 as my case 209 recount:** first hit of each (al, be, model, p, j) (no w / mode / dir) — sensitivity.
- **U4 distinct decrypt texts** (97-letter strings, '?' included), used for null pass counts "per distinct text".
- Per case (205, 206, 211) and per class (K4 / nulls pooled), plus per null text and per (case, p): number of hits / cells,
  **maxNC-elig** (max NC over hits with known ≥ 49 and n ≥ 10, the pass-eligible hits; **headline**), **maxNC-n10** (n ≥ 10, any known),
  **maxNC-any** (n ≥ 1), passes (U1, U2, U3), distinct texts passing, count of eligible hits. Max is over all hits of the unit
  (for U2/U3 over the first-hit representatives; the all-hits max is U1).
- Totals over the three cases: K4 cells and null cells (U2), K4 passes / null passes.
- Outputs: `counts_case.tsv`, `counts_case_p.tsv`, `counts_text.tsv`, `summary_nc_maxima.txt`, then `FROZEN.txt` and `SHA256SUMS`.
- The comparison with her published numbers is **not** part of the freeze.
