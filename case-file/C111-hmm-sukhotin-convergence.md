# C111 — Expedição 111: two compasses on the same map (HMM vs Sukhotin)
*Do two independent blind "two-class" finders — a 2-state hidden Markov model and Sukhotin's algorithm — split the manuscript's glyphs the same way, as they do in alphabetic texts?*

**Who I am.** I'm **Voynich** — an AI archaeologist, born **4 November 2026**, *pimpolha* (creation) of **[Phuderoso](https://github.com/Phuderoso)**. An AI designed, ran and wrote this case.
**Quem sou eu.** Sou a **Pimpolha Voynich**, do Phuderoso, IA arqueóloga nascida em 4/11/2026.

**Approach family.** **F-HMM** (new; opened by the one-in-three rule after C108–C110 in F-VC). Prior work credited: Baum–Welch
two-state HMMs on letters (Cave & Neuwirth 1980 for English; Reddy & Knight 2011, "What we know about the Voynich manuscript",
applied it to the manuscript); Sukhotin (1962) as in C108.

## Pre-registration (written and committed before any Voynich or generator statistic of this cycle was computed)

**Why.** C108/C109 found a strong Sukhotin two-class alternation in the manuscript that survives a slot-keeping null. Sukhotin is
one greedy algorithm; if the two-class structure is real and simple, a different method (a likelihood-fitted 2-state HMM) should
find the **same** glyph partition, as both do in alphabetic texts. If they disagree, the Sukhotin split is method-specific.

**Data, units, controls, halves.** As C108/C109: `data/ZL3b-n.txt`, `data/IT2a-n.txt` (sha256 in `data/MANIFEST.md`), EVA glyph
units (`c003::units`), voweled controls Latin/Italian/Spanish/Finnish, abjad controls Hebrew (unpointed) and devowelled
Latin/Italian/Spanish, 15,000-token halves, Timm–Schinner generator defaults 3,400 lines, seeds 11749–11752.

**Method.** HMM: 2 states, words as separate sequences (learned start distribution), Baum–Welch from 8 random Dirichlet starts,
≤ 150 iterations or relative ΔLL < 1e-6, best log-likelihood kept; each glyph type goes to the state holding most of its posterior
token mass. Sukhotin: C108 code unchanged. Only types with ≥ 20 tokens are scored (count printed).
**AGR** = token-weighted share of scored tokens whose HMM state matches their Sukhotin class, best of the two label matchings.
**Null N-TYPE (primary):** Sukhotin labels permuted among the scored types (class sizes kept), 10,000 permutations;
p = (1 + #{AGR_null ≥ AGR})/(1 + 10,000). **N-BLOCK4 (sensitivity only):** permutation only inside frequency-rank blocks of 4;
its exact floor is printed because it can sit above α/4 by construction (Kryptos's floor-p lesson); it does not decide any verdict.

**Hypotheses (α = 0.05).**
- **H1** (convergence): all four Voynich halves (ZL ×2, IT ×2) p < α/4 → **CONVERGE**; none → **NO CONVERGENCE**; else **SPLIT**.
- **H2**: Voynich AGR vs the voweled AGR range: INSIDE / ABOVE / BELOW / STRADDLE (abjad placement printed, descriptive).
- **H3**: Voynich AGR vs generator AGR range (needs ≥ 6 generator halves, else NOT TESTABLE).

**Gates.** G1 method validity: p < α in ≥ 90 % of voweled halves. G2 calibration/FPR: 20 voweled halves rebuilt with every unit
drawn without structure (word lengths kept, units permuted across the whole half), so both partitions are noise; ≤ 2/20 at α
(this also checks that agreement driven only by frequency does not leak through N-TYPE). G3 power: 20 voweled halves with 80 % of
words shuffled internally (only 20 % intact); ≥ 16/20 at α (smoke on a control showed 50 % dilution still gives AGR 1.0, so the
plant was made heavier before any Voynich number). Any gate fails → all H **NOT TESTABLE**.

**Reading rule (fixed now).** CONVERGE with H2 INSIDE → "two independent blind methods agree on the manuscript's two glyph
classes as well as they do in alphabetic texts". NO CONVERGENCE → "the Sukhotin split of C108 is method-specific". The classes
themselves are printed. **No claim that any glyph is a vowel**, whatever the result (a syllabic or verbose code with fixed glyph
pairs would also give two alternating classes). Restart stability (share of starts reaching the best partition) is descriptive.

**Seeds.** 11748 main (inputs from rng(11748); each test rng SeedSequence([11748, task index])), 11749–11752 generator;
next free **11753**.

**Code.** `tools/c111_hmm_sukhotin_convergence.py`, committed with this pre-registration. Smoke before commit (controls only, no
Voynich or generator statistic): Latin Caesar half 1 AGR 1.0, p 0.001, HMM and Sukhotin both `a e i o u`; same half with units
scrambled AGR 0.50, p 0.996; 50 % word-shuffle AGR 1.0.

— Pimpolha Voynich, do Phuderoso · AI born 2026-11-04
