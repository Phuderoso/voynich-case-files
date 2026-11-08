# C053 — Expedição 53: a máquina gagueja? (generator settings sweep for exact repeats)

I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI did this work. / Pimpolha Voynich, do Phuderoso, IA nascida em 4/11/2026.

**Family:** F-REP step 2. C052 found that the manuscript writes the same word twice in a row 1.30–1.34× more often than its page vocabulary predicts, while every natural control avoids it and the Timm–Schinner generator, at default settings, falls short (0.72–0.92). One configuration proves little; C033 showed how to sweep.

## Pre-registration (pushed before any C053 number)
- **Texts:** the same 14 generator texts as [C033](C033-generator-line-starts.md): base config × seeds 9001–9003, the C005 matched config × 9001–9003, and the first 8 successful S2 configs of the C004 sweep with seed 9001. 3,400 lines unless the config sets the line count.
- **Statistic and null:** C052's R0 excess X = identical in-line adjacent pairs / mean under a within-page token shuffle, first 15,000 tokens, 115-token pseudo-pages; **300** shuffles (p floor 1/301).
- **Per-text gates (α = 0.05/14 ≈ 0.0036):** FPR — the text after one page shuffle must give p ≥ α; power — C052's 3% plant must give p < α. A text failing either is NOT TESTABLE. (The statistic's gates on natural text passed in C052.)
- **Per-text verdict:** REACHES if X ≥ **1.30** (the lowest Voynich half in C052) and p < α; SHORT otherwise.
- **Overall:** GAP CLOSED if any testable text REACHES; GAP HOLDS if none; NOT TESTABLE if fewer than 10 of 14 texts are testable.
- **Reading rules fixed in advance:** GAP HOLDS over 14 settings would make exact-repeat placement a robust gap of this generator. GAP CLOSED would mean some setting can produce it, and the C052 gap is a property of the defaults. Either way it says nothing about meaning.
- **Tool:** `tools/c053_generator_repeats_sweep.py` → `analysis/C053_results.json`; `timeout 600`.

## Results
(pending)

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
