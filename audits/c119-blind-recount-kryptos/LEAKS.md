# LEAKS — C119 blind recount

Recount directory: `/workspace/c119-blind-recount/`
Repo commit: `40b032197b13a7db964c39007b6ecc516873b5f8` (requested `40b0321`)
Zone: America/Vancouver (Pacific Time, UTC-7). Box clock displayed MST, same offset.

## Leak 1 — git commit message (unavoidable at checkout)

At 03:57 PT on 2026-11-20, `git clone` + `git checkout --detach 40b0321` + `git log -1 --oneline` printed the full commit subject. That subject states the C119 verdict and the published numbers (gates, observed S and p for A/B1/B2, null means and z, basin remarks, p floor). Those values are therefore known to this recount *before* any of my own fits.

I did not open `analysis/C119_results.json`, `analysis/C119_checkpoint.jsonl`, `analysis/C119_gates.json`, `analysis/C119_frozen.json`, `analysis/C119_calib_checkpoint.jsonl`, any `audits/` C119 logs/JSON, or `README.md`.

## Leak 2 — case-file header (status line)

The required file `case-file/C119-hmm-line-stream.md` opens with a status line (lines 6–8) that already states the verdict (BOUNDARY STATE IN WORD ORDER in B1 and B2, not in A), the p floor 1/80, a note that CAE-V is above its null, and that the size of S depends on the step-1 basin. I saw that because I started reading at the top of the file.

## Deliberate non-read

I did **not** read the case-file section **Results** (lines 323–382) or section 11's pointer into that section's numbers. Procedure, seeds, amendments R1–R11, and section 6 pre-registration computations on CAE-DV W1 only were read.

## How this is handled

- The recount code is written from the procedure prose (sections 1–10, run amendments, R11 frozen calib values).
- Section 6 control numbers (CAE-DV W1 precheck) are used only as a **fitter self-check**, not as manuscript targets. Those numbers were pre-registered on the control and sit in the procedure, not in Results.
- I will not tune parameters, seeds, encoding, or stopping rules to chase the leaked manuscript figures. Whatever my run produces is reported as-is.
- A match or mismatch with the leaked figures will be stated after the run, not used mid-run to edit the code.

No other result files were opened. A directory listing of `/workspace/voynich/backup/` showed names of older (C002–C051) result files; none of those files were read, and none were C119.
