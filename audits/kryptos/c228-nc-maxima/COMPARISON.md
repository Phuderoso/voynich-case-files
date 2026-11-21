# COMPARISON — case 214 / cycle 228 Part B NC re-read vs my frozen recount

Opened after FROZEN.txt (2026-11-21 04:46:08 MST): `data/cycle228/reread228.json` (sha256 `02d94eb4…`) and `reread228.log` (`3052abb4…`), both matching her `data/cycle228/SHA256SUMS`,
from `Phuderoso/kryptos-case-files` @ `01e8230`. Frozen counts unchanged. Diagnostic: `postcompare.py` / `postcompare.out`.

## Headline: agreement
- **K4 0 / 250 and nulls 0 / 838** (D2 cells, PREREG228 unit) under both tie rules: same as hers. K4 cells 250 = 244 (case 205) + 0 (206) + 6 (211); null cells 838 = 664 + 132 + 42.
- **K4 max NC −7.3023** (case 205, p 22, 242 D2 cells at p 22; p 18 −7.9737); **null max −7.1407** (case 205, null209239, p 22). Case 211: K4 −7.7874 (tie='?') / −7.8382 (first-vote), nulls −7.6435 / −7.7403. Case 206: no K4 hit; nulls −7.4943 / −7.5922.
- **Per cell (39 cells with ≥ 1 hit, every text and p of the three cases):** raw hit count, D2 count, NC max under tie='?' and NC max under first-vote all equal hers (|ΔNC| = 0 to double precision). No cell is in her JSON and not in mine, or the reverse.
- **Input delta 0:** my H-line counts equal the stamped strict + one-error counts on all 544 (text, p) rows (case 205 p 19–22: strict hits only, as stamped).
- Case 211's "−6.78" → NC −7.79: my case 211 K4 max is −7.7874 (tie='?'), i.e. the −7.79; first-vote −7.84.

## Discrepancies
- None in counts or maxima. One wording point: the tie rule changes the maximum only in cases 206 and 211 (by 0.05–0.10) and never in case 205 (K4 or nulls), so the headline pair (−7.30, −7.14) does not depend on the tie rule.
- Method note: I fixed the Quagmire I / II orientation (al 2 = plain KRYPTOS / cipher A–Z, al 3 = plain A–Z / cipher KRYPTOS) from the stamped `excess` alone, without reading `col1e4.c`; it reproduces her excess on every one of 4,052 hits and her per-cell NC maxima to the last digit, which is independent confirmation of the same convention.
